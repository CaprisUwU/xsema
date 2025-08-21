"""
Tests for the batch processing functionality including rate limiting and persistence.
"""
import os
import json
import time
import asyncio
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch, MagicMock

# Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from core.storage.batch_job_store import BatchJobStore, job_store
from core.utils.rate_limiter import RateLimiter

# Test client
client = TestClient(app)

# Test data
TEST_WALLETS = [
    "0x1111111111111111111111111111111111111111",
    "0x2222222222222222222222222222222222222222",
    "0x3333333333333333333333333333333333333333"
]

# Mock data for wallet clustering
MOCK_CLUSTER_RESULT = {
    "wallet_address": "0x1111111111111111111111111111111111111111",
    "cluster_members": [
        "0x1111111111111111111111111111111111111111",
        "0x2222222222222222222222222222222222222222"
    ],
    "cluster_size": 2,
    "risk_score": 0.75
}

@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test."""
    # Clear the job store before each test
    if os.path.exists("data/batch_jobs"):
        for file in os.listdir("data/batch_jobs"):
            os.remove(os.path.join("data/batch_jobs", file))
    
    # Reset rate limiter
    RateLimiter._instance = None
    
    yield
    
    # Cleanup after test
    if os.path.exists("data/batch_jobs"):
        for file in os.listdir("data/batch_jobs"):
            os.remove(os.path.join("data/batch_jobs", file))

def test_batch_job_creation():
    """Test creating a new batch job."""
    response = client.post(
        "/api/v1/wallets/batch/cluster",
        json={
            "wallet_addresses": TEST_WALLETS,
            "depth": "medium",
            "include_risk": True
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    assert data["total_wallets"] == len(TEST_WALLETS)
    assert "websocket_url" in data
    assert "status_url" in data

def test_rate_limiting():
    """Test that rate limiting is enforced."""
    # First 5 requests should succeed
    for _ in range(5):
        response = client.post(
            "/api/v1/wallets/batch/cluster",
            json={"wallet_addresses": ["0x123"], "depth": "shallow"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    # 6th request should be rate limited
    response = client.post(
        "/api/v1/wallets/batch/cluster",
        json={"wallet_addresses": ["0x123"], "depth": "shallow"}
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Retry-After" in response.headers

@pytest.mark.asyncio
async def test_job_persistence():
    """Test that jobs are persisted to storage."""
    # Create a job
    job_id = "test_job_123"
    job_data = {
        "job_id": job_id,
        "status": "pending",
        "created_at": time.time(),
        "wallet_addresses": TEST_WALLETS,
        "progress": 0,
        "total_wallets": len(TEST_WALLETS),
        "results": None,
        "error": None
    }
    
    # Save the job
    await job_store.save_job(job_id, job_data)
    
    # Retrieve the job
    retrieved = await job_store.get_job(job_id)
    
    # Verify the data
    assert retrieved is not None
    assert retrieved["job_id"] == job_id
    assert retrieved["status"] == "pending"
    assert len(retrieved["wallet_addresses"]) == len(TEST_WALLETS)

def test_get_job_status():
    """Test retrieving job status."""
    # First create a job
    create_response = client.post(
        "/api/v1/wallets/batch/cluster",
        json={"wallet_addresses": TEST_WALLETS, "depth": "shallow"}
    )
    job_id = create_response.json()["job_id"]
    
    # Get job status
    status_response = client.get(f"/api/v1/wallets/batch/{job_id}/status")
    
    assert status_response.status_code == status.HTTP_200_OK
    data = status_response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "pending"
    assert data["total"] == len(TEST_WALLETS)

@pytest.mark.asyncio
async def test_cleanup_old_jobs():
    """Test that old jobs are cleaned up."""
    # Create an old job (older than 7 days)
    old_job_id = "old_job_123"
    old_timestamp = time.time() - (8 * 24 * 60 * 60)  # 8 days ago
    
    old_job_data = {
        "job_id": old_job_id,
        "status": "completed",
        "created_at": old_timestamp,
        "completed_at": old_timestamp + 60,  # 1 minute later
        "wallet_addresses": ["0x123"],
        "progress": 1,
        "total_wallets": 1,
        "results": {"clusters": []},
        "error": None
    }
    
    # Create a recent job
    recent_job_id = "recent_job_123"
    recent_job_data = {
        "job_id": recent_job_id,
        "status": "completed",
        "created_at": time.time(),
        "completed_at": time.time() + 60,  # 1 minute later
        "wallet_addresses": ["0x456"],
        "progress": 1,
        "total_wallets": 1,
        "results": {"clusters": []},
        "error": None
    }
    
    # Save both jobs
    await job_store.save_job(old_job_id, old_job_data)
    await job_store.save_job(recent_job_id, recent_job_data)
    
    # Run cleanup
    deleted = await job_store.cleanup_old_jobs(max_age_days=7)
    
    # Only the old job should be deleted
    assert deleted == 1
    
    # Verify old job is gone
    assert await job_store.get_job(old_job_id) is None
    
    # Verify recent job still exists
    assert await job_store.get_job(recent_job_id) is not None

# Mock the actual clustering to speed up tests
@patch("api.v1.endpoints.wallets.get_wallet_cluster")
def test_batch_processing_complete(mock_cluster):
    """Test the complete batch processing flow with mocks."""
    # Setup mock
    mock_cluster.return_value = MOCK_CLUSTER_RESULT
    
    # Start batch job
    response = client.post(
        "/api/v1/wallets/batch/cluster",
        json={"wallet_addresses": TEST_WALLETS, "depth": "medium"}
    )
    assert response.status_code == status.HTTP_200_OK
    job_id = response.json()["job_id"]
    
    # Simulate processing time
    time.sleep(0.5)
    
    # Check job status
    status_response = client.get(f"/api/v1/wallets/batch/{job_id}/status")
    assert status_response.status_code == status.HTTP_200_OK
    
    data = status_response.json()
    assert data["status"] in ["processing", "completed"]
    
    # If completed, verify results
    if data["status"] == "completed":
        assert "results" in data
        assert len(data["results"]["clusters"]) == len(TEST_WALLETS)
        assert data["progress"] == len(TEST_WALLETS)
        assert data["total"] == len(TEST_WALLETS)

def test_invalid_batch_request():
    """Test validation of batch request parameters."""
    # Empty wallet list
    response = client.post(
        "/api/v1/wallets/batch/cluster",
        json={"wallet_addresses": [], "depth": "shallow"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Invalid depth
    response = client.post(
        "/api/v1/wallets/batch/cluster",
        json={"wallet_addresses": TEST_WALLETS, "depth": "invalid"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Batch size too large
    large_batch = [f"0x{i:040x}" for i in range(1001)]
    response = client.post(
        "/api/v1/wallets/batch/cluster",
        json={"wallet_addresses": large_batch, "depth": "shallow"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
