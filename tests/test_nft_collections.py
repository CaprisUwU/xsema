"""
Tests for NFT Collection endpoints
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, APIRouter
from unittest.mock import Mock, patch

# Import the router directly for testing
from portfolio.api.v1.endpoints.nfts_flat import router as nfts_router

# Create a test app with the API v1 router
app = FastAPI()

# Create an API v1 router with the correct prefix
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(nfts_router)
app.include_router(api_router)

# Create test client
client = TestClient(app)

# Add test data
from portfolio.api.v1.endpoints.nfts_flat import collections_store
collections_store["test-portfolio-1"] = {
    "test-collection-1": {
        "collection_id": "test-collection-1",
        "name": "Test Collection",
        "symbol": "TST",
        "contract_address": "0xabcdef1234567890abcdef1234567890abcdef12",
        "blockchain": "ethereum",
        "nft_count": 5,
        "owners": 3,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }
}

# Print detailed route information for debugging
print("\n=== Registered Routes ===")
for route in app.routes:
    if hasattr(route, 'methods'):
        methods = ', '.join(route.methods or [])
        path = getattr(route, 'path', '')
        if hasattr(route, 'endpoint'):
            endpoint = getattr(route.endpoint, '__name__', str(route.endpoint))
            print(f"{methods:10} {path:60} -> {endpoint}")
        else:
            print(f"{methods:10} {path}")

# Print test data for debugging
print("\n=== Test Data ===")
print(f"collections_store keys: {list(collections_store.keys())}")
if collections_store.get("test-portfolio-1"):
    print(f"Collections in test-portfolio-1: {list(collections_store['test-portfolio-1'].keys())}")
print()

# Print the router's prefix
print(f"Router prefix: {nfts_router.prefix}")
print()

def test_list_nft_collections():
    """Test listing NFT collections in a portfolio"""
    portfolio_id = "test-portfolio-1"
    
    # Mock the current user dependency
    with patch('portfolio.api.v1.endpoints.nfts_flat.get_current_user') as mock_user:
        mock_user.return_value = {"id": "test-user-1"}
        
        # The full path includes /api/v1/portfolios/{portfolio_id}/nfts/collections
        url = f"/api/v1/portfolios/{portfolio_id}/nfts/collections"
        print(f"\nTesting URL: {url}")
        response = client.get(url, headers={"Authorization": "Bearer test-token"})
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}: {response.text}"
    collections = response.json()
    assert isinstance(collections, list)
    
    if collections:  # If there are collections in the test data
        collection = collections[0]
        assert "collection_id" in collection
        assert "name" in collection
        assert "symbol" in collection
        assert "contract_address" in collection

def test_get_nft_collection():
    """Test getting details of a specific NFT collection"""
    portfolio_id = "test-portfolio-1"
    collection_id = "test-collection-1"
    
    # Mock the current user dependency
    with patch('portfolio.api.v1.endpoints.nfts_flat.get_current_user') as mock_user:
        mock_user.return_value = {"id": "test-user-1"}
        
        response = client.get(
            f"/api/v1/portfolios/{portfolio_id}/nfts/collections/{collection_id}",
            headers={"Authorization": "Bearer test-token"}
        )
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}: {response.text}"
    collection = response.json()
    
    assert collection["collection_id"] == collection_id
    assert collection["name"] == "Test Collection"
    assert collection["symbol"] == "TST"
    assert collection["contract_address"] == "0xabcdef1234567890abcdef1234567890abcdef12"

def test_get_nonexistent_collection():
    """Test getting a non-existent NFT collection returns 404"""
    portfolio_id = "test-portfolio-1"
    collection_id = "nonexistent-collection"
    
    # Mock the current user dependency
    with patch('portfolio.api.v1.endpoints.nfts_flat.get_current_user') as mock_user:
        mock_user.return_value = {"id": "test-user-1"}
        
        response = client.get(
            f"/api/v1/portfolios/{portfolio_id}/nfts/collections/{collection_id}",
            headers={"Authorization": "Bearer test-token"}
        )
    
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
    assert response.json()["detail"] == "NFT collection not found"
