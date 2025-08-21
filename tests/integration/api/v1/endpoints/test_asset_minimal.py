"""
Minimal test for the asset endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from portfolio.main import app

# Create a test client
client = TestClient(app)

def test_create_asset_minimal():
    """Test creating an asset with minimal required fields."""
    # Minimal request body with only required fields
    request_body = {
        "portfolio_id": "test-portfolio-1",
        "wallet_id": "test-wallet-1",
        "asset": {
            "asset_id": "test-asset-1",
            "name": "Test Asset",
            "symbol": "TST",
            "type": "token",
            "balance": 100.0,
            "avg_buy_price": 100.0
        }
    }
    
    # Print the request for debugging
    print("\n=== TEST REQUEST ===")
    print(f"URL: POST /api/v1/assets/")
    print(f"Request body: {request_body}")
    
    # Make the request
    response = client.post(
        "/api/v1/assets/",
        json=request_body,
        headers={"Content-Type": "application/json"}
    )
    
    # Print response for debugging
    print("\n=== TEST RESPONSE ===")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Basic assertions
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    assert "asset_id" in response.json(), "Response should include asset_id"

if __name__ == "__main__":
    test_create_asset_minimal()
