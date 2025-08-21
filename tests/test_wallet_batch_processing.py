"""
Tests for wallet batch processing functionality.

These tests verify that the batch processing endpoints work correctly,
including job creation, status checking, and WebSocket updates.
"""
import os
import sys
import pytest
import json
import asyncio
import websockets
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FastAPI app
from main import app

# Test client
client = TestClient(app)

# Sample test data
SAMPLE_WALLETS = [
    "0x1111111111111111111111111111111111111111",
    "0x2222222222222222222222222222222222222222",
    "0x3333333333333333333333333333333333333333",
]

class TestWalletBatchProcessing:
    """Test cases for wallet batch processing endpoints."""
    
    @patch('api.v1.endpoints.wallets.WALLET_CLUSTERING')
    def test_batch_cluster_creation(self, mock_clustering):
        """Test creating a new batch clustering job."""
        # Mock the clustering response
        mock_cluster = MagicMock()
        mock_cluster.addresses = ["0x1111111111111111111111111111111111111111"]
        mock_clustering.cluster_wallets.return_value = [mock_cluster]
        
        # Make the request
        response = client.post(
            "/api/v1/wallets/batch/cluster",
            json={
                "wallet_addresses": SAMPLE_WALLETS,
                "depth": "shallow",
                "include_risk": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert data["total_addresses"] == len(SAMPLE_WALLETS)
        
        # Verify the job was created
        job_id = data["job_id"]
        response = client.get(f"/api/v1/wallets/batch/status/{job_id}")
        assert response.status_code == 200
        job_data = response.json()
        assert job_data["job_id"] == job_id
        assert job_data["status"] in ["pending", "processing", "completed"]
    
    @pytest.mark.asyncio
    async def test_websocket_updates(self):
        """Test WebSocket updates for batch processing."""
        # Start a WebSocket connection
        uri = "ws://testserver/ws/wallets/batch/test-job-123"
        
        async with websockets.connect(uri) as websocket:
            # Send a test message (server expects to receive something)
            await websocket.send("ping")
            
            # Simulate receiving a progress update
            test_message = {
                "type": "progress",
                "job_id": "test-job-123",
                "progress": 50,
                "processed": 1,
                "total": 2
            }
            await websocket.send(json.dumps(test_message))
            
            # Verify we can receive the message back
            response = await websocket.recv()
            assert json.loads(response) == test_message
    
    def test_invalid_wallet_addresses(self):
        """Test batch processing with invalid wallet addresses."""
        response = client.post(
            "/api/v1/wallets/batch/cluster",
            json={
                "wallet_addresses": ["invalid-address"],
                "depth": "shallow",
                "include_risk": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["valid_addresses"] == []
        assert data["invalid_addresses"] == ["invalid-address"]
    
    def test_nonexistent_job_status(self):
        """Test checking status of a non-existent job."""
        response = client.get("/api/v1/wallets/batch/status/nonexistent-job")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch('api.v1.endpoints.wallets.WALLET_CLUSTERING')
    def test_large_batch_processing(self, mock_clustering):
        """Test processing a large batch of wallets."""
        # Create a large list of test wallets
        large_wallet_list = [f"0x{i:040x}" for i in range(100)]
        
        # Mock the clustering response
        mock_cluster = MagicMock()
        mock_cluster.addresses = large_wallet_list[:50]  # Simulate one large cluster
        mock_clustering.cluster_wallets.return_value = [mock_cluster]
        
        # Make the request
        response = client.post(
            "/api/v1/wallets/batch/cluster",
            json={
                "wallet_addresses": large_wallet_list,
                "depth": "deep",
                "include_risk": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_addresses"] == len(large_wallet_list)
        assert len(data["valid_addresses"]) == len(large_wallet_list)
        assert data["invalid_addresses"] == []

if __name__ == "__main__":
    pytest.main(["-v", "test_wallet_batch_processing.py"])
