"""
Integration tests for Wallet endpoints.
"""
import os
import sys
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from portfolio.main import app
from portfolio.models.portfolio import Wallet, Portfolio, Asset

# Test data
TEST_USER_ID = "test-user-1"
TEST_PORTFOLIO_ID = "test-portfolio-1"
TEST_WALLET_ID = "test-wallet-1"

# Create a test client
@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_wallet():
    return {
        "id": TEST_WALLET_ID,
        "portfolio_id": TEST_PORTFOLIO_ID,
        "name": "Test Wallet",
        "address": "0x1234567890abcdef1234567890abcdef12345678",
        "blockchain": "ethereum",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

@pytest.mark.asyncio
async def test_create_wallet(test_client, mock_portfolio_service):
    """Test creating a new wallet."""
    wallet_data = {
        "name": "Test Wallet",
        "address": "0x1234567890abcdef1234567890abcdef12345678",
        "blockchain": "ethereum"
    }
    
    created_wallet = {
        "id": TEST_WALLET_ID,
        "portfolio_id": TEST_PORTFOLIO_ID,
        **wallet_data,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    mock_portfolio_service.create_wallet.return_value = Wallet(**created_wallet)
    
    response = test_client.post(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets",
        json=wallet_data,
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == TEST_WALLET_ID
    assert response.json()["name"] == wallet_data["name"]
    assert response.json()["address"] == wallet_data["address"]

@pytest.mark.asyncio
async def test_list_wallets(test_client, mock_portfolio_service, sample_wallet):
    """Test listing wallets in a portfolio."""
    mock_portfolio_service.list_wallets.return_value = [Wallet(**sample_wallet)]
    
    response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == TEST_WALLET_ID

@pytest.mark.asyncio
async def test_get_wallet(test_client, mock_portfolio_service, sample_wallet):
    """Test getting a wallet by ID."""
    mock_portfolio_service.get_wallet.return_value = Wallet(**sample_wallet)
    
    response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets/{TEST_WALLET_ID}",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == TEST_WALLET_ID
    assert response.json()["portfolio_id"] == TEST_PORTFOLIO_ID

@pytest.mark.asyncio
async def test_update_wallet(test_client, mock_portfolio_service, sample_wallet):
    """Test updating a wallet."""
    update_data = {"name": "Updated Wallet Name"}
    updated_wallet = {**sample_wallet, **update_data, "updated_at": datetime.now(timezone.utc).isoformat()}
    
    mock_portfolio_service.update_wallet.return_value = Wallet(**updated_wallet)
    
    response = test_client.patch(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets/{TEST_WALLET_ID}",
        json=update_data,
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == update_data["name"]
    assert response.json()["id"] == TEST_WALLET_ID

@pytest.mark.asyncio
async def test_delete_wallet(test_client, mock_portfolio_service, sample_wallet):
    """Test deleting a wallet."""
    response = test_client.delete(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets/{TEST_WALLET_ID}",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.asyncio
async def test_get_wallet_balance(test_client, mock_balance_service, sample_wallet):
    """Test getting wallet balance."""
    balance_data = {
        "wallet_id": TEST_WALLET_ID,
        "native_balance": "1.5",
        "native_currency": "ETH",
        "usd_value": "3000.00",
        "tokens": [
            {"symbol": "USDC", "balance": "100.00", "usd_value": "100.00"}
        ],
        "nft_count": 5,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    mock_balance_service.get_wallet_balance.return_value = balance_data
    
    response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets/{TEST_WALLET_ID}/balance",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["wallet_id"] == TEST_WALLET_ID
    assert "native_balance" in response.json()
    assert "tokens" in response.json()
