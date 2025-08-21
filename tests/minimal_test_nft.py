"""
Minimal test for NFT endpoints
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from portfolio.main import app

# Create a test client
client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is running"}

def test_list_nfts():
    """Test listing NFTs in a portfolio"""
    portfolio_id = "test-portfolio-1"
    response = client.get(
        f"/api/v1/portfolios/{portfolio_id}/nfts",
        headers={"X-User-ID": "test-user-1"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_nft():
    """Test getting a specific NFT"""
    portfolio_id = "test-portfolio-1"
    nft_id = "test-nft-1"
    response = client.get(
        f"/api/v1/portfolios/{portfolio_id}/nfts/{nft_id}",
        headers={"X-User-ID": "test-user-1"}
    )
    # Should return 200 if found, 404 if not
    assert response.status_code in [200, 404]

if __name__ == "__main__":
    # Run the tests
    pytest.main(["-v", __file__])
