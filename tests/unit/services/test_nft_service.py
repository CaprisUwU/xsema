"""
Unit tests for the NFT Service.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from portfolio.models.portfolio import NFTCollection, NFTMetadata, NFTAttribute
from portfolio.services.nft_service import NFTService, nft_service

@pytest.mark.asyncio
async def test_get_nft_collections():
    """Test getting NFT collections for an owner."""
    # Setup
    owner = "0x1234567890abcdef1234567890abcdef12345678"
    chain = "ethereum"
    
    mock_response = {
        "ownedNfts": [
            {
                "contract": {
                    "address": "0x123...",
                    "name": "Test Collection",
                    "symbol": "TST"
                },
                "id": {
                    "tokenId": "1"
                },
                "metadata": {
                    "name": "Test NFT #1",
                    "description": "A test NFT",
                    "image": "https://example.com/nft1.jpg"
                }
            }
        ]
    }
    
    # Mock the HTTP client
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        # Execute
        collections = await nft_service.get_nft_collections(owner, chain)
        
        # Verify
        assert len(collections) > 0
        assert isinstance(collections[0], NFTCollection)
        assert len(collections[0].nfts) == 1
        assert collections[0].nfts[0].token_id == "1"

@pytest.mark.asyncio
async def test_get_nfts_for_collection():
    """Test getting NFTs for a collection."""
    # Setup
    contract_address = "0x1234567890abcdef1234567890abcdef12345678"
    chain = "ethereum"
    
    mock_response = {
        "nfts": [
            {
                "id": {
                    "tokenId": "1"
                },
                "metadata": {
                    "name": "Test NFT #1",
                    "description": "A test NFT",
                    "image": "https://example.com/nft1.jpg"
                }
            }
        ]
    }
    
    # Mock the HTTP client
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        # Execute
        nfts = await nft_service.get_nfts_for_collection(contract_address, chain)
        
        # Verify
        assert len(nfts) == 1
        assert isinstance(nfts[0], NFTMetadata)
        assert nfts[0].token_id == "1"
        assert "Test NFT #1" in nfts[0].name

@pytest.mark.asyncio
async def test_get_contract_metadata():
    """Test getting contract metadata."""
    # Setup
    contract_address = "0x1234567890abcdef1234567890abcdef12345678"
    chain = "ethereum"
    
    mock_response = {
        "contractMetadata": {
            "name": "Test Collection",
            "symbol": "TST",
            "totalSupply": "10000",
            "tokenType": "ERC721"
        }
    }
    
    # Mock the HTTP client
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        # Execute
        metadata = await nft_service.get_contract_metadata(contract_address, chain)
        
        # Verify
        assert metadata["name"] == "Test Collection"
        assert metadata["symbol"] == "TST"
        assert metadata["totalSupply"] == "10000"

@pytest.mark.asyncio
async def test_get_nft_metadata():
    """Test getting NFT metadata."""
    # Setup
    contract_address = "0x1234567890abcdef1234567890abcdef12345678"
    token_id = "1"
    chain = "ethereum"
    
    mock_response = {
        "contract": {
            "address": contract_address,
            "name": "Test Collection",
            "symbol": "TST"
        },
        "id": {
            "tokenId": token_id
        },
        "metadata": {
            "name": "Test NFT #1",
            "description": "A test NFT",
            "image": "https://example.com/nft1.jpg",
            "attributes": [
                {"trait_type": "Color", "value": "Blue"},
                {"trait_type": "Rarity", "value": "Rare"}
            ]
        }
    }
    
    # Mock the HTTP client
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200
        
        # Execute
        nft = await nft_service.get_nft_metadata(contract_address, token_id, chain)
        
        # Verify
        assert nft.token_id == token_id
        assert nft.contract_address == contract_address
        assert nft.name == "Test NFT #1"
        assert len(nft.attributes) == 2
        assert isinstance(nft.attributes[0], NFTAttribute)
        assert nft.attributes[0].trait_type == "Color"
        assert nft.attributes[0].value == "Blue"

@pytest.mark.asyncio
async def test_parse_nft_metadata():
    """Test parsing NFT metadata."""
    # Setup
    nft_data = {
        "contract": {
            "address": "0x123..."
        },
        "id": {
            "tokenId": "1"
        },
        "metadata": {
            "name": "Test NFT #1",
            "description": "A test NFT",
            "image": "https://example.com/nft1.jpg",
            "attributes": [
                {"trait_type": "Color", "value": "Blue"},
                {"trait_type": "Rarity", "value": "Rare"}
            ]
        }
    }
    
    # Execute
    nft = nft_service._parse_nft_metadata(nft_data)
    
    # Verify
    assert nft.token_id == "1"
    assert nft.name == "Test NFT #1"
    assert len(nft.attributes) == 2
    assert nft.attributes[0].trait_type == "Color"
    assert nft.attributes[0].value == "Blue"
