"""
Isolated tests for batch processing functionality.
"""
import os
import json
import time
import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

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

@pytest.fixture
def mock_job_store():
    """Fixture for a mock job store."""
    class MockJobStore:
        def __init__(self):
            self.jobs = {}
            
        async def save_job(self, job_id, job_data):
            self.jobs[job_id] = job_data
            
        async def get_job(self, job_id):
            return self.jobs.get(job_id)
            
        async def cleanup_old_jobs(self, max_age_days):
            # Simple implementation that doesn't actually check age
            count = len(self.jobs)
            self.jobs = {}
            return count
            
    return MockJobStore()

@pytest.fixture
def mock_rate_limiter():
    """Fixture for a mock rate limiter."""
    class MockRateLimiter:
        async def is_rate_limited(self, key):
            return False
            
        async def __call__(self, request, limiter):
            pass
            
    return MockRateLimiter()

@pytest.fixture
def mock_wallet_clustering():
    """Fixture for mock wallet clustering."""
    class MockWalletClustering:
        def __init__(self):
            self.cluster_wallet = AsyncMock(return_value=MOCK_CLUSTER_RESULT)
            
    return MockWalletClustering()

@pytest.mark.asyncio
async def test_batch_job_lifecycle(mock_job_store, mock_rate_limiter, mock_wallet_clustering):
    """Test the complete lifecycle of a batch job."""
    # Mock the dependencies
    with patch('api.v1.endpoints.wallets.job_store', mock_job_store), \
         patch('api.v1.endpoints.wallets.BATCH_PROCESSING_LIMITER', mock_rate_limiter), \
         patch('api.v1.endpoints.wallets.WalletClustering', return_value=mock_wallet_clustering):
        
        # Import the functions we want to test
        from api.v1.endpoints.wallets import batch_cluster_wallets, get_batch_job_status, process_wallet_batch
        
        # Create a background tasks object
        class BackgroundTasks:
            def add_task(self, func, *args, **kwargs):
                self.func = func
                self.args = args
                self.kwargs = kwargs
                
        # Create a mock request
        class MockRequest:
            def __init__(self):
                self.client = type('Client', (), {'host': 'test'})()
                
        # Start a batch job
        background_tasks = BackgroundTasks()
        request_data = {
            "wallet_addresses": TEST_WALLETS,
            "depth": "medium",
            "include_risk": True
        }
        
        # Call the endpoint
        response = await batch_cluster_wallets(
            request=type('Request', (), {"json": lambda _: request_data})(),
            background_tasks=background_tasks,
            http_request=MockRequest()
        )
        
        # Verify the response
        assert "job_id" in response
        assert response["status"] == "pending"
        assert response["total_wallets"] == len(TEST_WALLETS)
        
        # Get the job ID
        job_id = response["job_id"]
        
        # Verify the job was saved
        job = await mock_job_store.get_job(job_id)
        assert job is not None
        assert job["status"] == "pending"
        
        # Process the batch
        await process_wallet_batch(
            job_id=job_id,
            wallet_addresses=TEST_WALLETS,
            depth="medium",
            include_risk=True
        )
        
        # Verify the job was updated
        job = await mock_job_store.get_job(job_id)
        assert job["status"] == "completed"
        assert job["progress"] == len(TEST_WALLETS)
        assert "results" in job
        assert len(job["results"]["clusters"]) == len(TEST_WALLETS)
        
        # Get the job status
        status_response = await get_batch_job_status(job_id)
        assert status_response["status"] == "completed"
        assert status_response["progress"] == len(TEST_WALLETS)
        assert "results" in status_response

@pytest.mark.asyncio
async def test_rate_limiting(mock_job_store, mock_wallet_clustering):
    """Test that rate limiting is enforced."""
    # Mock rate limiter that fails after first request
    class FailingRateLimiter:
        def __init__(self):
            self.count = 0
            
        async def __call__(self, request, limiter):
            self.count += 1
            if self.count > 5:  # Allow first 5 requests
                from fastapi import HTTPException
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    rate_limiter = FailingRateLimiter()
    
    with patch('api.v1.endpoints.wallets.job_store', mock_job_store), \
         patch('api.v1.endpoints.wallets.BATCH_PROCESSING_LIMITER', rate_limiter), \
         patch('api.v1.endpoints.wallets.WalletClustering', return_value=mock_wallet_clustering):
        
        from api.v1.endpoints.wallets import batch_cluster_wallets
        from fastapi import HTTPException
        
        # First 5 requests should succeed
        for _ in range(5):
            response = await batch_cluster_wallets(
                request=type('Request', (), {"json": lambda _: {"wallet_addresses": ["0x123"], "depth": "shallow"}})(),
                background_tasks=type('BackgroundTasks', (), {"add_task": lambda *_, **__: None})(),
                http_request=type('Request', (), {'client': type('Client', (), {'host': 'test'})()})()
            )
            assert "job_id" in response
        
        # 6th request should fail
        with pytest.raises(HTTPException) as exc_info:
            await batch_cluster_wallets(
                request=type('Request', (), {"json": lambda _: {"wallet_addresses": ["0x123"], "depth": "shallow"}})(),
                background_tasks=type('BackgroundTasks', (), {"add_task": lambda *_, **__: None})(),
                http_request=type('Request', (), {'client': type('Client', (), {'host': 'test'})()})()
            )
            
        assert exc_info.value.status_code == 429
