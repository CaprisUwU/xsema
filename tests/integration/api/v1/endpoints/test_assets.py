"""
Integration tests for Asset endpoints.
"""
import logging
import os
import sys
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch, call
from fastapi import status
from fastapi.testclient import TestClient

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up logging to capture test output
log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "test_assets.log")

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import application code after setting up logging
from portfolio.main import app
from portfolio.models.portfolio import Asset, AssetType, Portfolio, Wallet

# Test data
TEST_USER_ID = "demo-user"  # Must match the user ID in the test client
TEST_PORTFOLIO_ID = "test-portfolio-1"
TEST_ASSET_ID = "test-asset-1"
TEST_WALLET_ID = "test-wallet-1"

# Create a test client
@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_asset():
    return {
        "asset_id": TEST_ASSET_ID,
        "portfolio_id": TEST_PORTFOLIO_ID,
        "wallet_id": TEST_WALLET_ID,
        "name": "Ethereum",
        "symbol": "ETH",
        "type": AssetType.TOKEN,
        "balance": 1.5,
        "avg_buy_price": 2500.00,
        "value_usd": 4500.00,  # 1.5 * 3000
        "pnl": 0.2,  # (4500 - 3750) / 3750
        "allocation": 100.0,  # 100% of portfolio
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "metadata": {}
    }

@pytest.mark.asyncio
async def test_create_asset(test_client, mock_portfolio_service):
    """Test creating a new asset."""
    # Setup test data
    asset_data = {
        "name": "Test Asset",
        "symbol": "TST",
        "type": "token",
        "balance": 100.0,
        "avg_buy_price": 100.0,
        "metadata": {}
    }
    
    # Import the models
    from portfolio.models.portfolio import Portfolio, Wallet
    
    # Create proper model instances for the mocks with all required fields
    mock_portfolio = Portfolio(
        id=TEST_PORTFOLIO_ID,
        user_id=TEST_USER_ID,  # From PortfolioCreate
        name="Test Portfolio",  # From PortfolioCreate
        description="Test portfolio description",  # Optional in PortfolioCreate
        risk_tolerance=0.5,  # Default in PortfolioCreate
        # Portfolio fields
        wallets=[],  # Will be added below
        total_value=0.0,  # Default in Portfolio
        risk_score=None,  # Optional in Portfolio
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Create a wallet with all required fields
    mock_wallet = Wallet(
        id=TEST_WALLET_ID,
        address="0x1234567890abcdef",  # From WalletCreate
        chain="ethereum",  # From WalletCreate
        name="Test Wallet",  # Optional in WalletCreate
        is_primary=False,  # Default in WalletCreate
        # Wallet fields
        assets=[],  # Will be added by the service
        is_connected=False,  # Default in Wallet
        last_synced=None,  # Optional in Wallet
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Add the wallet to the portfolio
    mock_portfolio.wallets.append(mock_wallet)
    
    mock_asset = {
        "asset_id": TEST_ASSET_ID,
        "name": "Test Asset",
        "symbol": "TST",
        "type": "token",
        "balance": 100.0,
        "wallet_id": TEST_WALLET_ID,
        "portfolio_id": TEST_PORTFOLIO_ID,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
    
    # Import the module where portfolio_service is used in the endpoint
    from portfolio.api.v1.endpoints import assets as assets_module
    
    # Define the mock function
    async def mock_get_portfolio(user_id: str, portfolio_id: str):
        print(f"\n=== MOCK GET_PORTFOLIO CALLED ===")
        print(f"user_id: {user_id}, portfolio_id: {portfolio_id}")
        if user_id == TEST_USER_ID and portfolio_id == TEST_PORTFOLIO_ID:
            print("Returning mock portfolio")
            return mock_portfolio
        print("Portfolio not found")
        return None
    
    # Patch the portfolio_service in the assets module
    with patch('portfolio.api.v1.endpoints.assets.portfolio_service.get_portfolio', new_callable=AsyncMock) as mock_get_portfolio_func, \
         patch('portfolio.api.v1.endpoints.assets.portfolio_service.get_wallet', new_callable=AsyncMock) as mock_get_wallet_func, \
         patch('portfolio.api.v1.endpoints.assets.portfolio_service.create_asset', new_callable=AsyncMock) as mock_create_asset_func:
        
        # Configure the mocks
        mock_get_portfolio_func.side_effect = mock_get_portfolio
        mock_get_wallet_func.return_value = mock_wallet
        mock_create_asset_func.return_value = mock_asset
        
        # Prepare the request data with correct structure and types
        # The endpoint expects the asset data directly, not nested under an 'asset' key
        request_data = {
            "asset_id": TEST_ASSET_ID,  # Required by AssetCreate model
            "name": "Test Asset",
            "symbol": "TST",
            "type": "token",  # Use string value that matches AssetType enum
            "balance": 100.0,
            "avg_buy_price": 100.0,
            "metadata": {}
        }
        
        # Make the request inside the patch context
        response = test_client.post(
            f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets/{TEST_WALLET_ID}/assets/",
            json=request_data,
            headers={"Authorization": "Bearer test-token", "X-User-ID": TEST_USER_ID, "Content-Type": "application/json"}
        )
        
        # Verify the mocks were called as expected
        mock_get_portfolio_func.assert_called_once_with(
            user_id=TEST_USER_ID,
            portfolio_id=TEST_PORTFOLIO_ID 
        )
        mock_get_wallet_func.assert_called_once_with(
            portfolio_id=TEST_PORTFOLIO_ID,
            wallet_id=TEST_WALLET_ID
        )     
        mock_create_asset_func.assert_called_once()
        
    # Print response details
    print("\n=== RESPONSE DETAILS ===")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    # Check if the response is successful
    if response.status_code == status.HTTP_201_CREATED:
        print("\n" + "="*80)
        print("ASSET CREATED SUCCESSFULLY")
        print("="*80)
        response_data = response.json()
        print("Created Asset:", response_data)
        
        # Verify the response contains the expected fields
        assert "asset_id" in response_data, "Response missing 'asset_id' field"
        assert response_data["name"] == "Test Asset", "Incorrect asset name"
        assert response_data["symbol"] == "TST", "Incorrect asset symbol"
        # Note: wallet_id and portfolio_id are not included in the API response
    else:
        print("\n" + "!"*80)
        print("ASSET CREATION FAILED")
        print("!"*80)
        assert False, f"Expected status code 201, got {response.status_code}"
    
    # Assert the response
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["asset_id"] == TEST_ASSET_ID
    assert response_data["name"] == asset_data["name"]
    assert response_data["symbol"] == asset_data["symbol"]

@pytest.mark.asyncio
async def test_list_assets(test_client, mock_portfolio_service, sample_asset):
    """Test listing assets in a portfolio."""
    mock_portfolio_service.list_assets.return_value = [Asset(**sample_asset)]
    
    response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets/{TEST_WALLET_ID}/assets",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 1
    assert response_data[0]["asset_id"] == TEST_ASSET_ID

@pytest.mark.asyncio
async def test_get_asset(test_client, mock_portfolio_service, sample_asset):
    """Test getting an asset by ID."""
    mock_portfolio_service.get_asset.return_value = Asset(**sample_asset)
    
    response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets/{TEST_WALLET_ID}/assets/{TEST_ASSET_ID}",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["asset_id"] == TEST_ASSET_ID
    assert response.json()["portfolio_id"] == TEST_PORTFOLIO_ID

@pytest.mark.asyncio
async def test_update_asset(test_client, mock_portfolio_service, sample_asset):
    """Test updating an asset."""
    update_data = {"balance": 2.0, "avg_buy_price": 2600.00}
    updated_asset = {
        **sample_asset,
        **update_data,
        "value_usd": 6000.00,  # 2.0 * 3000
        "pnl": 0.15,  # (6000 - 5200) / 5200
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
    
    mock_portfolio_service.update_asset.return_value = Asset(**updated_asset)
    
    response = test_client.put(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets/{TEST_WALLET_ID}/assets/{TEST_ASSET_ID}",
        json=update_data,
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["balance"] == update_data["balance"]
    assert response_data["asset_id"] == TEST_ASSET_ID

@pytest.mark.asyncio
async def test_delete_asset(test_client, mock_portfolio_service, sample_asset):
    """Test deleting an asset."""
    mock_portfolio_service.delete_asset.return_value = True
    
    response = test_client.delete(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets/{TEST_WALLET_ID}/assets/{TEST_ASSET_ID}",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.asyncio
async def test_get_asset_performance(test_client, mock_analytics_service, sample_asset):
    """Test getting asset performance metrics."""
    performance_data = {
        "asset_id": TEST_ASSET_ID,
        "time_period": "30d",
        "start_price": 3000.00,
        "end_price": 4500.00,
        "high_price": 4800.00,
        "low_price": 1200.00,
        "price_change": 1500.00,
        "price_change_pct": 0.5,
        "volume": 10000.00,
        "start_timestamp": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
        "end_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    mock_analytics_service.get_asset_performance.return_value = performance_data
    
    response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/wallets/{TEST_WALLET_ID}/assets/{TEST_ASSET_ID}/performance",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["asset_id"] == TEST_ASSET_ID
    assert response_data["time_period"] == "30d"
    assert response_data["start_price"] == 3000.00
    assert response_data["end_price"] == 4500.00
    assert response_data["price_change_pct"] == 0.5
