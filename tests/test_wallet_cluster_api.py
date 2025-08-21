"""
API tests for wallet clustering functionality.
These tests verify the HTTP API endpoints for wallet clustering.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

# Create a test client
client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}

def test_wallet_cluster_endpoint():
    """Test the wallet cluster endpoint with a mock wallet address."""
    # Mock the wallet clustering functionality
    mock_cluster = {
        "cluster_id": "cluster_123",
        "wallet_address": "0x1234...",
        "cluster_members": ["0x1234...", "0x5678..."],
        "cluster_size": 2,
        "cluster_metadata": {"similarity_score": 0.85}
    }
    
    with patch('api.v1.endpoints.wallets.WalletClustering') as mock_wallet_clustering:
        # Set up the mock
        mock_instance = MagicMock()
        mock_instance.analyze_wallet.return_value = mock_cluster
        mock_wallet_clustering.return_value = mock_instance
        
        # Make the request
        response = client.get(
            "/api/v1/wallets/0x1234.../cluster",
            params={"depth": 1, "include_risk": True}
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert "cluster_id" in data
        assert data["wallet_address"] == "0x1234..."
        assert len(data["cluster_members"]) > 0

def test_wallet_cluster_invalid_address():
    """Test the wallet cluster endpoint with an invalid wallet address."""
    response = client.get("/api/v1/wallets/invalid_address/cluster")
    assert response.status_code == 400
    assert "Invalid wallet address" in response.json()["detail"]

# Add more test cases as needed
