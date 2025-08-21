"""
Test Asset Endpoints

This script tests the asset-related API endpoints.
Created: 2025-08-01
"""
import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
from main import app

# Test configuration
TEST_PORTFOLIO_ID = "test_portfolio_1"
TEST_WALLET_ID = "test_wallet_1"
TEST_ASSET = {
    "asset_id": "test_asset_1",
    "symbol": "TST",
    "name": "Test Asset",
    "type": "token",
    "balance": 100.0,
    "avg_buy_price": 10.5
}

# API prefix for portfolio routes
API_PREFIX = "/api/v1/portfolio"

# Test client fixture
@pytest.fixture
def client():
    return TestClient(app)

# Test create asset
def test_create_asset(client):
    """Test creating a new asset."""
    # First, ensure the portfolio and wallet exist
    portfolio_data = {
        "user_id": "demo-user",  # Required field
        "name": "Test Portfolio",
        "description": "Test portfolio for asset testing",
        "risk_tolerance": 0.5
    }
    wallet_data = {
        "address": "0x1234567890123456789012345678901234567890",  # Valid Ethereum address format
        "chain": "ethereum",
        "name": "Test Wallet",
        "is_primary": False
    }

    # Create test portfolio and get the created portfolio ID
    portfolio_response = client.post(f"{API_PREFIX}/portfolios", json=portfolio_data)
    if portfolio_response.status_code == 201:
        created_portfolio = portfolio_response.json()
        portfolio_id = created_portfolio["id"]
    else:
        # If portfolio creation failed, use the test ID
        portfolio_id = TEST_PORTFOLIO_ID
        
    # Create test wallet in the created portfolio
    try:
        wallet_response = client.post(f"{API_PREFIX}/portfolios/{portfolio_id}/wallets", json=wallet_data)
        if wallet_response.status_code == 201:
            created_wallet = wallet_response.json()
            wallet_id = created_wallet["id"]
            print(f"Created wallet with ID: {wallet_id}")
        else:
            wallet_id = TEST_WALLET_ID
            print(f"Wallet creation failed with status {wallet_response.status_code}, using test ID: {wallet_id}")
    except Exception as e:
        wallet_id = TEST_WALLET_ID
        print(f"Wallet creation exception: {e}, using test ID: {wallet_id}")
    
    # Test asset creation
    response = client.post(
        f"{API_PREFIX}/portfolios/{portfolio_id}/wallets/{wallet_id}/assets/",
        json=TEST_ASSET
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["asset_id"] == TEST_ASSET["asset_id"]
    assert data["balance"] == TEST_ASSET["balance"]
    return data

# Test get asset
def test_get_asset(client):
    """Test retrieving an asset."""
    # First create the necessary test data
    portfolio_data = {
        "user_id": "demo-user",
        "name": "Test Portfolio for Get",
        "description": "Test portfolio for asset retrieval testing",
        "risk_tolerance": 0.5
    }
    wallet_data = {
        "address": "0x1234567890123456789012345678901234567890",
        "chain": "ethereum",
        "name": "Test Wallet for Get",
        "is_primary": False
    }
    
    # Create portfolio and wallet
    portfolio_response = client.post(f"{API_PREFIX}/portfolios", json=portfolio_data)
    assert portfolio_response.status_code == 201
    portfolio_id = portfolio_response.json()["id"]
    
    wallet_response = client.post(f"{API_PREFIX}/portfolios/{portfolio_id}/wallets", json=wallet_data)
    assert wallet_response.status_code == 201
    wallet_id = wallet_response.json()["id"]
    
    # Create an asset
    asset_response = client.post(
        f"{API_PREFIX}/portfolios/{portfolio_id}/wallets/{wallet_id}/assets/",
        json=TEST_ASSET
    )
    assert asset_response.status_code == 201
    
    # Now test retrieving the asset
    response = client.get(
        f"{API_PREFIX}/portfolios/{portfolio_id}/wallets/{wallet_id}/assets/{TEST_ASSET['asset_id']}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == TEST_ASSET["asset_id"]

# Test list assets
def test_list_assets(client):
    """Test listing all assets in a wallet."""
    # First create the necessary test data
    portfolio_data = {
        "user_id": "demo-user",
        "name": "Test Portfolio for List",
        "description": "Test portfolio for asset listing testing",
        "risk_tolerance": 0.5
    }
    wallet_data = {
        "address": "0x1234567890123456789012345678901234567890",
        "chain": "ethereum",
        "name": "Test Wallet for List",
        "is_primary": False
    }
    
    # Create portfolio and wallet
    portfolio_response = client.post(f"{API_PREFIX}/portfolios", json=portfolio_data)
    assert portfolio_response.status_code == 201
    portfolio_id = portfolio_response.json()["id"]
    
    wallet_response = client.post(f"{API_PREFIX}/portfolios/{portfolio_id}/wallets", json=wallet_data)
    assert wallet_response.status_code == 201
    wallet_id = wallet_response.json()["id"]
    
    # Create an asset
    asset_response = client.post(
        f"{API_PREFIX}/portfolios/{portfolio_id}/wallets/{wallet_id}/assets/",
        json=TEST_ASSET
    )
    assert asset_response.status_code == 201
    
    # Now test listing assets
    response = client.get(
        f"{API_PREFIX}/portfolios/{portfolio_id}/wallets/{wallet_id}/assets/"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(asset["asset_id"] == TEST_ASSET["asset_id"] for asset in data)

# Test update asset
def test_update_asset(client):
    """Test updating an asset."""
    # First create the necessary test data
    portfolio_data = {
        "user_id": "demo-user",
        "name": "Test Portfolio for Update",
        "description": "Test portfolio for asset update testing",
        "risk_tolerance": 0.5
    }
    wallet_data = {
        "address": "0x1234567890123456789012345678901234567890",
        "chain": "ethereum",
        "name": "Test Wallet for Update",
        "is_primary": False
    }
    
    # Create portfolio and wallet
    portfolio_response = client.post(f"{API_PREFIX}/portfolios", json=portfolio_data)
    assert portfolio_response.status_code == 201
    portfolio_id = portfolio_response.json()["id"]
    
    wallet_response = client.post(f"{API_PREFIX}/portfolios/{portfolio_id}/wallets", json=wallet_data)
    assert wallet_response.status_code == 201
    wallet_id = wallet_response.json()["id"]
    
    # Create an asset
    asset_response = client.post(
        f"{API_PREFIX}/portfolios/{portfolio_id}/wallets/{wallet_id}/assets/",
        json=TEST_ASSET
    )
    assert asset_response.status_code == 201
    
    # Now test updating the asset
    update_data = {"balance": 150.0, "avg_buy_price": 12.0}
    
    response = client.put(
        f"{API_PREFIX}/portfolios/{portfolio_id}/wallets/{wallet_id}/assets/{TEST_ASSET['asset_id']}",
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 150.0
    assert data["avg_buy_price"] == 12.0

# Test delete asset
def test_delete_asset(client):
    """Test deleting an asset."""
    # First create the necessary test data
    portfolio_data = {
        "user_id": "demo-user",
        "name": "Test Portfolio for Delete",
        "description": "Test portfolio for asset deletion testing",
        "risk_tolerance": 0.5
    }
    wallet_data = {
        "address": "0x1234567890123456789012345678901234567890",
        "chain": "ethereum",
        "name": "Test Wallet for Delete",
        "is_primary": False
    }
    
    # Create portfolio and wallet
    portfolio_response = client.post(f"{API_PREFIX}/portfolios", json=portfolio_data)
    assert portfolio_response.status_code == 201
    portfolio_id = portfolio_response.json()["id"]
    
    wallet_response = client.post(f"{API_PREFIX}/portfolios/{portfolio_id}/wallets", json=wallet_data)
    assert wallet_response.status_code == 201
    wallet_id = wallet_response.json()["id"]
    
    # Create an asset
    asset_response = client.post(
        f"{API_PREFIX}/portfolios/{portfolio_id}/wallets/{wallet_id}/assets/",
        json=TEST_ASSET
    )
    assert asset_response.status_code == 201
    
    # Now test deleting the asset
    response = client.delete(
        f"{API_PREFIX}/portfolios/{portfolio_id}/wallets/{wallet_id}/assets/{TEST_ASSET['asset_id']}"
    )
    
    assert response.status_code == 204  # 204 No Content is correct for DELETE
    
    # Verify deletion
    response = client.get(
        f"{API_PREFIX}/portfolios/{portfolio_id}/wallets/{wallet_id}/assets/{TEST_ASSET['asset_id']}"
    )
    assert response.status_code == 404

# Asset endpoint tests are now pytest-compatible
# Run with: python -m pytest tests/test_asset_endpoints.py -v
