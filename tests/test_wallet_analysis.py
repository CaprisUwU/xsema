"""
Tests for wallet analysis functionality.

These tests verify the wallet analysis endpoints and blockchain service integration.
"""
import pytest
import os
import json
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone, timedelta

# Import the FastAPI app
from main import app

# Test client
client = TestClient(app)

# Test data
TEST_WALLET = "0x1234567890123456789012345678901234567890"
TEST_CONTRACT = "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d"  # BAYC contract

# Mock responses
MOCK_NFT_RESPONSE = {
    "ownedNfts": [
        {
            "contract": {"address": TEST_CONTRACT, "symbol": "BAYC"},
            "id": {"tokenId": "1234", "tokenMetadata": {"tokenType": "ERC721"}},
            "title": "BoredApeYachtClub #1234",
            "timeLastUpdated": datetime.now(timezone.utc).isoformat() + "Z"
        }
    ],
    "totalCount": 1,
    "pageKey": "next-page-key"
}

MOCK_METADATA_RESPONSE = {
    "title": "BoredApeYachtClub #1234",
    "description": "A Bored Ape Yacht Club NFT",
    "image": "ipfs://Qm...",
    "attributes": [
        {"trait_type": "Background", "value": "Blue"},
        {"trait_type": "Fur", "value": "Brown"}
    ]
}

MOCK_TOKEN_BALANCES = {
    "address": TEST_WALLET,
    "tokenBalances": [
        {"contractAddress": "0x123...", "tokenBalance": "1000000000000000000"},
        {"contractAddress": "0x456...", "tokenBalance": "5000000000000000000"}
    ]
}

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set up environment variables for testing."""
    monkeypatch.setenv("ALCHEMY_API_KEY", "test-api-key")
    monkeypatch.setenv("ETHEREUM_RPC_URL", "https://eth-mainnet.alchemyapi.io/v2/test-api-key")

@pytest.mark.asyncio
async def test_get_wallet_analysis():
    """Test getting wallet analysis."""
    with (
        patch('services.blockchain.BlockchainService.get_wallet_nfts', 
             new_callable=AsyncMock, 
             return_value=MOCK_NFT_RESPONSE) as mock_nfts,
        patch('services.blockchain.BlockchainService.get_wallet_token_balances',
             new_callable=AsyncMock,
             return_value=MOCK_TOKEN_BALANCES) as mock_balances
    ):
        
        # Call the endpoint
        response = client.get(f"/api/v1/wallets/analysis/{TEST_WALLET}")
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify the response structure
        assert data["wallet_address"] == TEST_WALLET.lower()
        assert data["total_tokens"] == 1
        assert data["unique_collections"] == 1
        assert data["token_balance_count"] == 2
        assert len(data["tokens"]) == 1
        
        # Verify the token data
        token = data["tokens"][0]
        assert token["contract_address"] == TEST_CONTRACT.lower()
        assert token["token_id"] == "1234"
        assert token["name"] == "BoredApeYachtClub #1234"
        assert token["symbol"] == "BAYC"
        
        # Verify the mocks were called
        mock_nfts.assert_called_once()
        mock_balances.assert_called_once()

@pytest.mark.asyncio
async def test_get_wallet_tokens():
    """Test getting wallet tokens with pagination."""
    with patch('services.blockchain.BlockchainService.get_wallet_nfts', 
              new_callable=AsyncMock, 
              return_value=MOCK_NFT_RESPONSE):
        
        # Call the endpoint with pagination
        response = client.get(
            f"/api/v1/wallets/tokens/{TEST_WALLET}",
            params={"limit": 10, "offset": 0}
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify the response structure
        assert data["wallet_address"] == TEST_WALLET.lower()
        assert data["total"] == 1
        assert data["limit"] == 10
        assert data["offset"] == 0
        assert data["page_key"] == "next-page-key"
        assert len(data["tokens"]) == 1
        
        # Verify the token data
        token = data["tokens"][0]
        assert token["contract_address"] == TEST_CONTRACT.lower()
        assert token["token_id"] == "1234"
        assert token["name"] == "BoredApeYachtClub #1234"
        assert token["symbol"] == "BAYC"

@pytest.mark.asyncio
async def test_get_wallet_tokens_with_metadata():
    """Test getting wallet tokens with metadata."""
    with (
        patch('services.blockchain.BlockchainService.get_wallet_nfts', 
             new_callable=AsyncMock, 
             return_value=MOCK_NFT_RESPONSE),
        patch('services.blockchain.BlockchainService.get_token_metadata',
             new_callable=AsyncMock,
             return_value=MOCK_METADATA_RESPONSE)
    ):
        
        # Call the endpoint with metadata flag
        response = client.get(
            f"/api/v1/wallets/tokens/{TEST_WALLET}",
            params={"include_metadata": "true"}
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify metadata is included
        token = data["tokens"][0]
        assert "metadata" in token
        assert token["metadata"]["title"] == "BoredApeYachtClub #1234"
        assert "attributes" in token["metadata"]

@pytest.mark.asyncio
async def test_invalid_wallet_address():
    """Test with an invalid wallet address."""
    response = client.get("/api/v1/wallets/analysis/not-a-valid-address")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid wallet address" in response.text

@pytest.mark.asyncio
async def test_blockchain_service_error():
    """Test handling of blockchain service errors."""
    with patch('services.blockchain.BlockchainService.get_wallet_nfts', 
              new_callable=AsyncMock, 
              side_effect=Exception("Blockchain service error")):
        
        response = client.get(f"/api/v1/wallets/analysis/{TEST_WALLET}")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to analyze wallet" in response.text
