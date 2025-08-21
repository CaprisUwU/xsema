"""
Unit tests for wallet clustering functionality.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException
import time

# Test data
TEST_WALLETS = [
    "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "0x1234567890123456789012345678901234567890",
    "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
]

# Mock data for wallet clustering
MOCK_CLUSTER_RESULT = {
    "cluster_id": "test_cluster_1",
    "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "cluster_members": ["0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"],
    "cluster_size": 1,
    "cluster_metadata": {"risk_score": 0.1},
    "risk_analysis": {"overall_risk": "low"}
}

@pytest.fixture
def mock_wallet_clustering():
    """Mock WalletClustering class."""
    mock = MagicMock()
    mock.cluster_wallets.return_value = [MOCK_CLUSTER_RESULT] * len(TEST_WALLETS)
    return mock

@pytest.fixture
def mock_job_store():
    """Mock job store for testing."""
    class MockJobStore:
        def __init__(self):
            self.jobs = {}
            
        async def save_job(self, job_id, job_data):
            self.jobs[job_id] = job_data
            
        async def get_job(self, job_id):
            return self.jobs.get(job_id)
            
        async def cleanup_old_jobs(self, max_age_days):
            return 0
    
    return MockJobStore()

@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter that allows requests."""
    mock = MagicMock()
    mock.is_rate_limited = AsyncMock(return_value=False)
    mock.window = 60
    return mock

@pytest.mark.asyncio
async def test_process_wallet_batch(mock_wallet_clustering, mock_job_store):
    """Test the process_wallet_batch function."""
    # Import the function we want to test
    from api.v1.endpoints.wallets import process_wallet_batch, BatchJob, JobStatus

    # Create a test job first
    job_id = "test_job_123"
    test_job_data = {
        "job_id": job_id,
        "status": JobStatus.PENDING.value,
        "created_at": time.time(),
        "total_wallets": len(TEST_WALLETS),
        "wallet_addresses": TEST_WALLETS,
        "progress": 0,
        "results": None,
        "error": None
    }
    
    # Save the test job to the mock store
    await mock_job_store.save_job(job_id, test_job_data)

    # Mock the WalletClustering class
    with patch('api.v1.endpoints.wallets.WalletClustering', return_value=mock_wallet_clustering), \
         patch('api.v1.endpoints.wallets.batch_job_store', mock_job_store), \
         patch('api.v1.endpoints.wallets.ws_manager') as mock_ws_manager, \
         patch('api.v1.endpoints.wallets.get_wallet_cluster') as mock_get_cluster:
        
        # Mock the get_wallet_cluster function
        mock_get_cluster.return_value = MOCK_CLUSTER_RESULT
        
        # Mock the WebSocket manager
        mock_ws_manager.broadcast_job_update = AsyncMock()

        # Call the function
        await process_wallet_batch(
            job_id=job_id,
            wallet_addresses=TEST_WALLETS,
            depth="medium",
            include_risk=True
        )

        # Verify the job was processed
        job = await mock_job_store.get_job(job_id)
        assert job is not None
        assert job["status"] == "completed"
        assert job["progress"] == len(TEST_WALLETS)
        assert "results" in job
        assert len(job["results"]["clusters"]) == len(TEST_WALLETS)

@pytest.mark.asyncio
async def test_batch_cluster_wallets(mock_wallet_clustering, mock_job_store, mock_rate_limiter):
    """Test the batch_cluster_wallets endpoint."""
    # Import the function we want to test
    from api.v1.endpoints.wallets import batch_cluster_wallets, WalletClusterRequest
    
    # Mock dependencies
    with patch('api.v1.endpoints.wallets.WalletClustering', return_value=mock_wallet_clustering), \
         patch('api.v1.endpoints.wallets.batch_job_store', mock_job_store), \
         patch('api.v1.endpoints.wallets.BATCH_PROCESSING_LIMITER', mock_rate_limiter):
        
        # Create a proper WalletClusterRequest object
        request = WalletClusterRequest(
            wallet_addresses=TEST_WALLETS,
            depth="medium",
            include_risk=True
        )
        
        # Create a mock background tasks object
        background_tasks = MagicMock()
        http_request = MagicMock()
        http_request.client.host = "127.0.0.1"
        
        # Call the endpoint
        response = await batch_cluster_wallets(
            request=request,
            background_tasks=background_tasks,
            http_request=http_request
        )
        
        # Debug output
        print(f"Response: {response}")
        print(f"Expected total_wallets: {len(TEST_WALLETS)}")
        print(f"Actual total_wallets: {response.get('total_wallets')}")
        
        # Verify the response
        assert "job_id" in response
        assert response["status"] == "pending"
        assert response["total_wallets"] == len(TEST_WALLETS)
        
        # Verify background task was added
        background_tasks.add_task.assert_called_once()
        
        # Verify the job was created in memory
        from api.v1.endpoints.wallets import batch_jobs
        job_id = response["job_id"]
        assert job_id in batch_jobs
        job = batch_jobs[job_id]
        assert job.total == len(TEST_WALLETS)

@pytest.mark.asyncio
async def test_get_batch_job_status(mock_job_store):
    """Test the get_batch_job_status endpoint."""
    # Import the function we want to test
    from api.v1.endpoints.wallets import get_batch_job_status, BatchJob, JobStatus
    
    # Create a test job
    job_id = "test_job_123"
    test_job = {
        "job_id": job_id,
        "status": JobStatus.COMPLETED.value,
        "created_at": datetime.now().timestamp(),
        "total_wallets": 3,  # This field is required for the total calculation
        "progress": 3,
        "results": {"clusters": [MOCK_CLUSTER_RESULT] * 3},
        "error": None
    }
    
    # Save the test job
    await mock_job_store.save_job(job_id, test_job)
    
    # Mock the job store
    with patch('api.v1.endpoints.wallets.batch_job_store', mock_job_store):
        # Call the endpoint
        response = await get_batch_job_status(job_id)
        
        # Verify the response
        assert response["job_id"] == job_id
        assert response["status"] == "completed"
        assert response["progress"] == 3
        assert response["total"] == 3
        assert "results" in response
        assert len(response["results"]["clusters"]) == 3

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test that rate limiting is enforced."""
    from api.v1.endpoints.wallets import BATCH_PROCESSING_LIMITER
    from core.utils.rate_limiter import rate_limit_check
    
    # Mock the rate limiter to fail after first request
    mock_limiter = MagicMock()
    mock_limiter.is_rate_limited.return_value = True
    mock_limiter.window = 60
    
    # Mock request
    request = MagicMock()
    request.client.host = "127.0.0.1"
    
    # Test rate limited
    with patch('core.utils.rate_limiter.RateLimiter.is_rate_limited', return_value=True):
        with pytest.raises(HTTPException) as exc_info:
            await rate_limit_check(request, BATCH_PROCESSING_LIMITER)
        
        assert exc_info.value.status_code == 429
        assert "Too many requests" in str(exc_info.value.detail)
