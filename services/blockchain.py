"""
Blockchain API Service

This module provides services for interacting with blockchain APIs like Alchemy and Infura.
It handles wallet analysis, token fetching, and other blockchain-related operations.
"""
import os
import logging
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import aiohttp
import json
import backoff
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# Import caching and rate limiting utilities
from utils.cache import cached, rate_limited, CacheConfig, cache_config
from portfolio.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class BlockchainServiceError(Exception):
    """Custom exception for blockchain service errors."""
    def __init__(self, message: str, status_code: int = 500, retry_after: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(message)

class RateLimitExceeded(BlockchainServiceError):
    """Raised when rate limit is exceeded."""
    def __init__(self, retry_after: int):
        super().__init__(
            "Rate limit exceeded. Please try again later.",
            status_code=429,
            retry_after=retry_after
        )

class APITimeoutError(BlockchainServiceError):
    """Raised when an API request times out."""
    def __init__(self, message: str = "API request timed out"):
        super().__init__(message, status_code=504)

class BlockchainService:
    """Service for interacting with blockchain APIs."""
    
    def __init__(self, rpc_url: Optional[str] = None, api_key: Optional[str] = None):
        self._web3 = None
        self._initialized = False
        """
        Initialize the blockchain service.
        
        Args:
            rpc_url: Optional RPC URL (defaults to environment variable)
            api_key: Optional API key (defaults to environment variable)
        """
        self.rpc_url = rpc_url or settings.ethereum_rpc_url
        self.api_key = api_key or settings.alchemy_api_key
        self.web3 = None
        self._session = None
        self._rate_limits = {}  # Track rate limits per endpoint
        
        # Configure cache
        cache_config.enabled = settings.cache_enabled
        cache_config.default_ttl = settings.cache_default_ttl
        
        if not self.rpc_url and settings.ethereum_rpc_url:
            self.rpc_url = settings.ethereum_rpc_url
            
        if not self.api_key and settings.alchemy_api_key:
            self.api_key = settings.alchemy_api_key
            
        if not self.rpc_url:
            logger.warning("No RPC URL provided. Some functionality may be limited.")
        else:
            self._init_web3()
    
    def _init_web3(self):
        """Initialize the Web3 instance."""
        try:
            self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            # Inject POA middleware for networks like Polygon
            self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            
            if not self.web3.is_connected():
                logger.warning("Web3 connection test failed. Some functionality may be limited.")
            else:
                logger.info(f"Connected to Ethereum network (chain_id: {self.web3.eth.chain_id})")
                
        except Exception as e:
            logger.error(f"Failed to initialize Web3: {str(e)}")
            self.web3 = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp client session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None
    
    @cached(ttl=300, key_prefix="alchemy:nfts:{wallet_address}:{contract_address}")
    @rate_limited("alchemy:nfts:{request.client.host}", rate=30, period=60)  # 30 req/min per IP
    async def get_wallet_nfts(
        self, 
        wallet_address: str, 
        contract_address: Optional[str] = None,
        chain: str = "eth-mainnet",
        page_key: Optional[str] = None,
        page_size: int = 100,
        request: Any = None  # For rate limiting
    ) -> Dict[str, Any]:
        """
        Get NFTs owned by a wallet using Alchemy's NFT API.
        
        Args:
            wallet_address: The wallet address to query
            contract_address: Optional contract address to filter by
            chain: Blockchain network (default: eth-mainnet)
            page_key: Pagination key for the next page of results
            page_size: Number of results per page (max 100)
            request: FastAPI Request object for rate limiting (injected by decorator)
            
        Returns:
            Dictionary containing NFTs and pagination info
            
        Raises:
            BlockchainServiceError: If there's an error fetching NFTs
            RateLimitExceeded: If rate limit is exceeded
        """
        if not self.api_key:
            raise BlockchainServiceError("Alchemy API key is required for this operation")
        
        base_url = f"https://{chain}.g.alchemy.com/nft/v2/{self.api_key}"
        params = {
            "owner": Web3.to_checksum_address(wallet_address),
            "withMetadata": "true",
            "pageSize": min(page_size, 100),
        }
        
        if contract_address:
            params["contractAddresses"] = [Web3.to_checksum_address(contract_address)]
        if page_key:
            params["pageKey"] = page_key
        
        try:
            session = await self.get_session()
            
            # Add timeout to prevent hanging requests
            timeout = aiohttp.ClientTimeout(total=30)  # 30 seconds timeout
            
            async with session.get(
                f"{base_url}/getNFTs",
                params=params,
                timeout=timeout
            ) as response:
                # Handle rate limiting
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitExceeded(retry_after)
                    
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Alchemy API error: {response.status} - {error_text}")
                    raise BlockchainServiceError(
                        f"Alchemy API error: {response.status} - {error_text}",
                        status_code=response.status
                    )
                
                data = await response.json()
                
                # Add cache control headers if available
                cache_control = response.headers.get('Cache-Control', '')
                if 'max-age=' in cache_control:
                    max_age = int(cache_control.split('max-age=')[1].split(',')[0])
                    # Update cache TTL based on API response
                    if hasattr(self, '_cache_ttl'):
                        self._cache_ttl = min(self._cache_ttl or float('inf'), max_age)
                
                return data
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout while fetching NFTs for wallet {wallet_address}")
            raise APITimeoutError("Request to Alchemy API timed out")
            
        except aiohttp.ClientError as e:
            logger.error(f"Network error while fetching NFTs: {str(e)}")
            raise BlockchainServiceError(f"Network error: {str(e)}", status_code=503)
            
        except Exception as e:
            if not isinstance(e, BlockchainServiceError):
                logger.error(f"Error fetching NFTs for wallet {wallet_address}: {str(e)}")
                raise BlockchainServiceError(f"Failed to fetch NFTs: {str(e)}")
            raise
    
    async def get_wallet_token_balances(
        self,
        wallet_address: str,
        chain: str = "eth-mainnet"
    ) -> Dict[str, Any]:
        """
        Get token balances for a wallet.
        
        Args:
            wallet_address: The wallet address to query
            chain: Blockchain network (default: eth-mainnet)
            
        Returns:
            Dictionary containing token balances
        """
        if not self.api_key:
            raise BlockchainServiceError("Alchemy API key is required for this operation")
        
        base_url = f"https://{chain}.g.alchemy.com/v2/{self.api_key}"
        
        # Get token balances
        payload = {
            "jsonrpc": "2.0",
            "method": "alchemy_getTokenBalances",
            "params": [wallet_address, "erc20"],
            "id": 1
        }
        
        try:
            session = await self.get_session()
            async with session.post(base_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise BlockchainServiceError(
                        f"Alchemy RPC error: {response.status} - {error_text}"
                    )
                
                result = await response.json()
                if "error" in result:
                    raise BlockchainServiceError(f"Alchemy error: {result['error']['message']}")
                
                return result.get("result", {})
                
        except Exception as e:
            logger.error(f"Error fetching token balances for {wallet_address}: {str(e)}")
            raise BlockchainServiceError(f"Failed to fetch token balances: {str(e)}")
    
    @cached(ttl=3600, key_prefix="alchemy:metadata:{contract_address}:{token_id}")
    @rate_limited("alchemy:metadata:{request.client.host}", rate=50, period=60)  # 50 req/min per IP
    async def get_token_metadata(
        self,
        contract_address: str,
        token_id: str,
        chain: str = "eth-mainnet",
        request: Any = None  # For rate limiting
    ) -> Dict[str, Any]:
        """
        Get metadata for a specific token.
        
        Args:
            contract_address: The token contract address
            token_id: The token ID
            chain: Blockchain network (default: eth-mainnet)
            request: FastAPI Request object for rate limiting (injected by decorator)
            
        Returns:
            Dictionary containing token metadata
            
        Raises:
            BlockchainServiceError: If there's an error fetching metadata
            RateLimitExceeded: If rate limit is exceeded
        """
        if not self.api_key:
            raise BlockchainServiceError("Alchemy API key is required for this operation")
        
        base_url = f"https://{chain}.g.alchemy.com/nft/v2/{self.api_key}"
        
        try:
            session = await self.get_session()
            
            # Add timeout to prevent hanging requests
            timeout = aiohttp.ClientTimeout(total=15)  # 15 seconds timeout
            
            async with session.get(
                f"{base_url}/getNFTMetadata",
                params={
                    "contractAddress": Web3.to_checksum_address(contract_address),
                    "tokenId": str(token_id),
                    "tokenType": "erc721"  # or "erc1155" as needed
                },
                timeout=timeout
            ) as response:
                # Handle rate limiting
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitExceeded(retry_after)
                    
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"Error fetching metadata for token {contract_address}/{token_id}: "
                        f"{response.status} - {error_text}"
                    )
                    raise BlockchainServiceError(
                        f"Alchemy API error: {response.status} - {error_text}",
                        status_code=response.status
                    )
                
                data = await response.json()
                
                # Add cache control headers if available
                cache_control = response.headers.get('Cache-Control', '')
                if 'max-age=' in cache_control:
                    max_age = int(cache_control.split('max-age=')[1].split(',')[0])
                    # Update cache TTL based on API response
                    if hasattr(self, '_cache_ttl'):
                        self._cache_ttl = min(self._cache_ttl or float('inf'), max_age)
                
                return data
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout while fetching metadata for token {contract_address}/{token_id}")
            raise APITimeoutError("Request to Alchemy API timed out")
            
        except aiohttp.ClientError as e:
            logger.error(f"Network error while fetching token metadata: {str(e)}")
            raise BlockchainServiceError(f"Network error: {str(e)}", status_code=503)
            
        except Exception as e:
            if not isinstance(e, BlockchainServiceError):
                logger.error(
                    f"Error fetching metadata for token {contract_address}/{token_id}: {str(e)}"
                )
                raise BlockchainServiceError(f"Failed to fetch token metadata: {str(e)}")
            raise

# Global instance that will be initialized on first use
blockchain_service = None

async def get_blockchain_service():
    """Get or initialize the global blockchain service instance."""
    global blockchain_service
    if blockchain_service is None:
        blockchain_service = BlockchainService()
    if not blockchain_service._initialized:
        await blockchain_service.initialize()
    return blockchain_service

# Async context manager support
class BlockchainServiceContext:
    """Context manager for BlockchainService."""
    
    def __init__(self, rpc_url: Optional[str] = None, api_key: Optional[str] = None):
        self.service = BlockchainService(rpc_url, api_key)
    
    async def __aenter__(self):
        return self.service
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.service.close()

# Example usage:
# async with BlockchainServiceContext() as blockchain:
#     nfts = await blockchain.get_wallet_nfts("0x...")
