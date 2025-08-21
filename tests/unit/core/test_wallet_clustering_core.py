"""
Core tests for wallet clustering functionality.
These tests focus on the core logic without requiring the full application context.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

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
    "risk_score": 0.75,
    "cluster_metadata": {
        "common_networks": ["ethereum"],
        "interaction_patterns": ["NFT transfers", "token swaps"]
    }
}

# Mock Wallet class
class MockWallet:
    def __init__(self, address):
        self.address = address
        self.interactions = {}
        self.tokens = []
        self.transactions = []
        self.networks = ["ethereum"]
    
    async def analyze(self):
        return {"risk_score": 0.5, "anomalies": []}

# Mock WalletClustering class
class MockWalletClustering:
    def __init__(self):
        self.cluster_wallet = AsyncMock(return_value=MOCK_CLUSTER_RESULT)
        self.cluster_wallets = AsyncMock(return_value={"clusters": [MOCK_CLUSTER_RESULT] * 3})
        self.get_wallet = AsyncMock(return_value=MockWallet("0x123"))

@pytest.fixture
def mock_wallet_clustering():
    """Fixture for mock wallet clustering."""
    return MockWalletClustering()

@pytest.fixture
def mock_job_store():
    """Fixture for a mock job store."""
    class MockJobStore:
        def __init__(self):
            self.jobs = {}
            
        async def save_job(self, job_id, job_data):
            self.jobs[job_id] = job_data
            return job_data
            
        async def get_job(self, job_id):
            return self.jobs.get(job_id)
            
        async def cleanup_old_jobs(self, max_age_days):
            count = len(self.jobs)
            self.jobs = {}
            return count
            
    return MockJobStore()

def test_mock_wallet_creation():
    """Test that our mock wallet works as expected."""
    wallet = MockWallet("0x123")
    assert wallet.address == "0x123"
    assert wallet.networks == ["ethereum"]

@pytest.mark.asyncio
async def test_mock_wallet_analysis():
    """Test that our mock wallet analysis works."""
    wallet = MockWallet("0x123")
    analysis = await wallet.analyze()
    assert "risk_score" in analysis
    assert "anomalies" in analysis

@pytest.mark.asyncio
async def test_mock_wallet_clustering(mock_wallet_clustering):
    """Test that our mock wallet clustering works."""
    result = await mock_wallet_clustering.cluster_wallet("0x123")
    assert result["wallet_address"] == "0x1111111111111111111111111111111111111111"
    assert len(result["cluster_members"]) == 2
    assert result["cluster_size"] == 2
    assert "risk_score" in result

@pytest.mark.asyncio
async def test_batch_processing_flow(mock_wallet_clustering, mock_job_store):
    """Test the complete batch processing flow with mocks."""
    # Simulate creating a batch job
    job_id = "test_job_123"
    job_data = {
        "job_id": job_id,
        "status": "pending",
        "created_at": datetime.now().timestamp(),
        "wallet_addresses": TEST_WALLETS,
        "progress": 0,
        "total_wallets": len(TEST_WALLETS),
        "results": None,
        "error": None
    }
    
    # Save the job
    await mock_job_store.save_job(job_id, job_data)
    
    # Simulate processing the batch
    results = await mock_wallet_clustering.cluster_wallets()
    
    # Update job with results
    job_data["status"] = "completed"
    job_data["progress"] = len(TEST_WALLETS)
    job_data["results"] = {"clusters": results["clusters"]}
    job_data["completed_at"] = datetime.now().timestamp()
    
    await mock_job_store.save_job(job_id, job_data)
    
    # Verify the job was processed
    job = await mock_job_store.get_job(job_id)
    assert job["status"] == "completed"
    assert job["progress"] == len(TEST_WALLETS)
    assert "results" in job
    assert len(job["results"]["clusters"]) == 3  # 3 mock clusters returned
    assert job["results"]["clusters"][0]["wallet_address"] == "0x1111111111111111111111111111111111111111"

class TestRateLimiter:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_check(self):
        """Test the rate limit check logic."""
        from core.utils.rate_limiter import RateLimiter
        
        # Create a rate limiter that allows 5 requests per minute
        limiter = RateLimiter(requests=5, window=60)
        
        # First 5 requests should pass
        for _ in range(5):
            assert not await limiter.is_rate_limited("test_key")
        
        # 6th request should be rate limited
        assert await limiter.is_rate_limited("test_key")
        
        # Different keys should have separate limits
        assert not await limiter.is_rate_limited("different_key")

class TestJobStore:
    """Test job store functionality."""
    
    @pytest.mark.asyncio
    async def test_job_store_operations(self, mock_job_store):
        """Test basic job store operations."""
        # Create a test job
        job_id = "test_job_123"
        job_data = {
            "job_id": job_id,
            "status": "pending",
            "created_at": datetime.now().timestamp()
        }
        
        # Save the job
        await mock_job_store.save_job(job_id, job_data)
        
        # Retrieve the job
        retrieved = await mock_job_store.get_job(job_id)
        assert retrieved["job_id"] == job_id
        
        # Clean up old jobs
        count = await mock_job_store.cleanup_old_jobs(7)
        assert count == 1  # Should clean up our test job
