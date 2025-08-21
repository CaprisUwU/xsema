"""
Integration tests for NFT endpoints.
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
from portfolio.models.portfolio import NFT, Portfolio, Wallet, NFTMetadata, NFTTrait, NFTCreate, NFTUpdate, NFTResponse

# Test data
TEST_USER_ID = "test-user-1"
TEST_PORTFOLIO_ID = "test-portfolio-1"
TEST_WALLET_ID = "test-wallet-1"
TEST_NFT_ID = "test-nft-1"
TEST_COLLECTION_ID = "test-collection-1"

# Create a test client with overridden dependencies
@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_portfolio_service():
    # Create a mock portfolio service
    mock_service = MagicMock()

    # Import the nfts module to patch the service
    from portfolio.api.v1.endpoints import nfts
    from portfolio.services.portfolio_service import PortfolioService

    # Save the original service
    original_service = nfts.portfolio_service

    # Apply the mock
    nfts.portfolio_service = mock_service

    yield mock_service

    # Restore the original service
    nfts.portfolio_service = original_service

@pytest.fixture
def mock_analytics_service():
    # Create a mock analytics service
    mock_service = MagicMock()

    # Import the nfts module to patch the service
    from portfolio.api.v1.endpoints import nfts
    from portfolio.services.analytics_service import AnalyticsService

    # Save the original service
    original_service = nfts.analytics_service

    # Apply the mock
    nfts.analytics_service = mock_service

    yield mock_service

    # Restore the original service
    nfts.analytics_service = original_service

@pytest.fixture
def sample_nft_metadata():
    return {
        "name": "Test NFT #1",
        "description": "A test NFT",
        "image_url": "https://example.com/nft.jpg",
        "external_url": "https://example.com/nft/1",
        "traits": [
            {"trait_type": "Background", "value": "Blue"},
            {"trait_type": "Rarity", "value": "Legendary"}
        ]
    }

@pytest.fixture
def sample_nft_create_data():
    return {
        "token_id": "1",
        "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
        "name": "Test NFT #1",
        "description": "A test NFT",
        "image_url": "https://example.com/nft.jpg",
        "external_url": "https://example.com/nft/1",
        "standard": "erc721",
        "metadata": {
            "attributes": [
                {"trait_type": "Background", "value": "Blue"},
                {"trait_type": "Rarity", "value": "Legendary"}
            ]
        },
        "owner_address": "0x1234567890abcdef1234567890abcdef12345678",
        "collection_id": TEST_COLLECTION_ID
    }

@pytest.fixture
def sample_nft(sample_nft_metadata):
    now = datetime.now(timezone.utc)
    return {
        "id": TEST_NFT_ID,
        "token_id": "1",
        "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
        "name": "Test NFT #1",
        "description": "A test NFT",
        "image_url": "https://example.com/nft.jpg",
        "external_url": "https://example.com/nft/1",
        "standard": "erc721",
        "metadata": sample_nft_metadata,
        "owner": "0x1234567890abcdef1234567890abcdef12345678",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "is_verified": False,
        "is_listed": False
    }

@pytest.mark.asyncio
async def test_list_nfts(test_client, mock_portfolio_service, sample_nft):
    """Test listing NFTs in a portfolio."""
    # Setup mock
    from portfolio.models.portfolio import NFTResponse
    mock_portfolio_service.list_nfts.return_value = [NFTResponse(**sample_nft)]
    
    # Make request
    response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/nfts",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == TEST_NFT_ID
    
    # Verify service was called correctly
    mock_portfolio_service.list_nfts.assert_called_once_with(
        portfolio_id=TEST_PORTFOLIO_ID,
        user_id=TEST_USER_ID
    )

@pytest.mark.asyncio
async def test_get_nft(test_client, mock_portfolio_service, sample_nft):
    """Test getting an NFT by ID."""
    mock_portfolio_service.get_nft.return_value = NFT(**sample_nft)
    
    response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/nfts/{TEST_NFT_ID}",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == TEST_NFT_ID
    assert response.json()["portfolio_id"] == TEST_PORTFOLIO_ID

@pytest.mark.asyncio
async def test_refresh_nft_metadata(test_client, mock_portfolio_service, sample_nft):
    """Test refreshing NFT metadata."""
    updated_nft = {
        **sample_nft,
        "name": "Updated Test NFT #1",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    mock_portfolio_service.refresh_nft_metadata.return_value = NFT(**updated_nft)
    
    response = test_client.post(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/nfts/{TEST_NFT_ID}/refresh",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == updated_nft["name"]
    assert response.json()["id"] == TEST_NFT_ID

@pytest.mark.asyncio
async def test_get_nft_collections(test_client, mock_portfolio_service):
    """Test listing NFT collections in a portfolio."""
    collection_data = {
        "collection_id": TEST_COLLECTION_ID,
        "name": "Test Collection",
        "symbol": "TST",
        "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
        "blockchain": "ethereum",
        "nft_count": 5,
        "floor_price": "0.5",
        "total_volume": "10.0",
        "owners": 100,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    mock_portfolio_service.get_nft_collections.return_value = [collection_data]
    
    response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/nfts/collections",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["collection_id"] == TEST_COLLECTION_ID

@pytest.mark.asyncio
async def test_get_nft_collection(test_client, mock_portfolio_service, sample_nft):
    """Test getting details of an NFT collection."""
    collection_data = {
        "collection_id": TEST_COLLECTION_ID,
        "name": "Test Collection",
        "description": "A test NFT collection",
        "symbol": "TST",
        "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
        "blockchain": "ethereum",
        "nft_count": 5,
        "floor_price": "0.5",
        "total_volume": "10.0",
        "owners": 100,
        "website": "https://test-collection.com",
        "twitter_username": "testcollection",
        "discord_url": "https://discord.gg/test",
        "created_at": (datetime.now(timezone.utc) - timedelta(days=365)).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    mock_portfolio_service.get_nft_collection.return_value = collection_data
    
    response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/nfts/collections/{TEST_COLLECTION_ID}",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["collection_id"] == TEST_COLLECTION_ID
    assert "floor_price" in response.json()
    assert "nft_count" in response.json()

@pytest.mark.asyncio
async def test_get_nft_rarity(test_client, mock_analytics_service, sample_nft):
    """Test getting NFT rarity information."""
    mock_analytics_service.get_nft_rarity.return_value = {
        "score": 0.95,
        "rank": 10,
        "total": 1000,
        "traits": [
            {"trait_type": "Background", "value": "Blue", "rarity": 0.05},
            {"trait_type": "Rarity", "value": "Legendary", "rarity": 0.01}
        ]
    }
    
    response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/nfts/{TEST_NFT_ID}/rarity",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "score" in data
    assert "rank" in data
    assert "total" in data
    assert "traits" in data
    assert len(data["traits"]) == 2

# New tests for NFT CRUD operations
@pytest.mark.asyncio
async def test_create_nft(test_client, sample_nft_create_data):
    """Test creating a new NFT."""
    response = test_client.post(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/nfts",
        json=sample_nft_create_data,
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["token_id"] == sample_nft_create_data["token_id"]
    assert data["contract_address"] == sample_nft_create_data["contract_address"]
    assert data["name"] == sample_nft_create_data["name"]
    assert data["is_verified"] is False
    assert data["is_listed"] is False

@pytest.mark.asyncio
async def test_create_nft_invalid_contract(test_client, sample_nft_create_data):
    """Test creating an NFT with an invalid contract address."""
    invalid_data = sample_nft_create_data.copy()
    invalid_data["contract_address"] = "invalid-address"
    
    response = test_client.post(
        "/api/v1/nfts",
        json=invalid_data,
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_update_nft(test_client, sample_nft):
    """Test updating an existing NFT."""
    # First create the NFT
    create_response = test_client.post(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/nfts",
        json={
            "token_id": "1",
            "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
            "name": "Original Name"
        },
        headers={"X-User-ID": TEST_USER_ID}
    )
    nft_id = create_response.json()["id"]
    
    # Update the NFT
    update_data = {
        "name": "Updated Name",
        "description": "Updated description",
        "is_listed": True
    }
    
    response = test_client.put(
        f"/api/v1/nfts/{nft_id}",
        json=update_data,
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated description"
    assert data["is_listed"] is True

@pytest.mark.asyncio
async def test_update_nonexistent_nft(test_client):
    """Test updating a non-existent NFT."""
    response = test_client.put(
        "/api/v1/nfts/nonexistent-id",
        json={"name": "Updated Name"},
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_nft(test_client):
    """Test deleting an NFT."""
    # First create an NFT to delete
    create_response = test_client.post(
        "/api/v1/nfts",
        json={
            "token_id": "1",
            "contract_address": "0x1234567890abcdef1234567890abcdef12345678"
        },
        headers={"X-User-ID": TEST_USER_ID}
    )
    nft_id = create_response.json()["id"]
    
    # Delete the NFT
    response = test_client.delete(
        f"/api/v1/nfts/{nft_id}",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify the NFT no longer exists
    get_response = test_client.get(
        f"/api/v1/portfolios/{TEST_PORTFOLIO_ID}/nfts/{nft_id}",
        headers={"X-User-ID": TEST_USER_ID}
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_nonexistent_nft(test_client):
    """Test deleting a non-existent NFT."""
    response = test_client.delete(
        "/api/v1/nfts/nonexistent-id",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
