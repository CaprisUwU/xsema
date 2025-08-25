"""
XSEMA Market Data Integration Module - Phase 4
Real NFT marketplace data from OpenSea, Magic Eden, etc.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import os
import json
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class Marketplace(Enum):
    """Supported NFT marketplaces"""
    OPENSEA = "opensea"
    MAGIC_EDEN = "magic_eden"
    BLUR = "blur"
    LOOKSRARE = "looksrare"
    X2Y2 = "x2y2"
    RARIBLE = "rarible"
    FOUNDATION = "foundation"
    SUPERRARE = "superrare"
    MANIFOLD = "manifold"

@dataclass
class MarketplaceConfig:
    """Configuration for NFT marketplaces"""
    marketplace: Marketplace
    api_url: str
    api_key: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    enabled: bool = True
    supported_networks: List[str] = None

@dataclass
class NFTMarketData:
    """Real NFT market data structure"""
    token_id: str
    contract_address: str
    network: str
    marketplace: Marketplace
    name: str
    description: str
    image_url: str
    external_url: Optional[str] = None
    
    # Market data
    current_price: Optional[float] = None
    current_price_currency: Optional[str] = None
    floor_price: Optional[float] = None
    floor_price_currency: Optional[str] = None
    last_sale_price: Optional[float] = None
    last_sale_currency: Optional[str] = None
    last_sale_date: Optional[datetime] = None
    
    # Collection data
    collection_name: Optional[str] = None
    collection_slug: Optional[str] = None
    collection_verified: Optional[bool] = None
    
    # Trading data
    volume_24h: Optional[float] = None
    volume_7d: Optional[float] = None
    volume_total: Optional[float] = None
    sales_24h: Optional[int] = None
    sales_7d: Optional[int] = None
    sales_total: Optional[int] = None
    
    # Listing data
    is_listed: bool = False
    listing_price: Optional[float] = None
    listing_currency: Optional[str] = None
    listing_expires: Optional[datetime] = None
    
    # Metadata
    attributes: List[Dict[str, Any]] = None
    rarity_score: Optional[float] = None
    rarity_rank: Optional[int] = None
    
    # Timestamps
    last_updated: datetime = None
    data_source: str = "unknown"

class MarketDataManager:
    """Manages real NFT marketplace data integration"""
    
    def __init__(self):
        self.configs: Dict[Marketplace, MarketplaceConfig] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, datetime] = {}
        self.cache_duration = timedelta(minutes=2)  # Market data changes quickly
        self.rate_limiters: Dict[Marketplace, Dict[str, datetime]] = {}
        
        # Initialize configurations
        self._load_configurations()
    
    def _load_configurations(self):
        """Load marketplace configurations from environment"""
        # OpenSea configuration
        self.configs[Marketplace.OPENSEA] = MarketplaceConfig(
            marketplace=Marketplace.OPENSEA,
            api_url="https://api.opensea.io/api/v2",
            api_key=os.getenv("OPENSEA_API_KEY"),
            rate_limit=100,
            enabled=bool(os.getenv("OPENSEA_ENABLED", "true").lower() == "true"),
            supported_networks=["ethereum", "polygon", "arbitrum", "optimism", "base"]
        )
        
        # Magic Eden configuration
        self.configs[Marketplace.MAGIC_EDEN] = MarketplaceConfig(
            marketplace=Marketplace.MAGIC_EDEN,
            api_url="https://api-mainnet.magiceden.dev/v2",
            api_key=os.getenv("MAGIC_EDEN_API_KEY"),
            rate_limit=200,
            enabled=bool(os.getenv("MAGIC_EDEN_ENABLED", "true").lower() == "true"),
            supported_networks=["solana"]
        )
        
        # Blur configuration
        self.configs[Marketplace.BLUR] = MarketplaceConfig(
            marketplace=Marketplace.BLUR,
            api_url="https://api.blur.io/v1",
            api_key=os.getenv("BLUR_API_KEY"),
            rate_limit=150,
            enabled=bool(os.getenv("BLUR_ENABLED", "true").lower() == "true"),
            supported_networks=["ethereum"]
        )
        
        # LooksRare configuration
        self.configs[Marketplace.LOOKSRARE] = MarketplaceConfig(
            marketplace=Marketplace.LOOKSRARE,
            api_url="https://api.looksrare.org/v2",
            api_key=os.getenv("LOOKSRARE_API_KEY"),
            rate_limit=100,
            enabled=bool(os.getenv("LOOKSRARE_ENABLED", "true").lower() == "true"),
            supported_networks=["ethereum"]
        )
        
        # X2Y2 configuration
        self.configs[Marketplace.X2Y2] = MarketplaceConfig(
            marketplace=Marketplace.X2Y2,
            api_url="https://api.x2y2.io/v1",
            api_key=os.getenv("X2Y2_API_KEY"),
            rate_limit=100,
            enabled=bool(os.getenv("X2Y2_ENABLED", "true").lower() == "true"),
            supported_networks=["ethereum"]
        )
        
        logger.info(f"Loaded {len([c for c in self.configs.values() if c.enabled])} enabled marketplace configurations")
    
    async def __aenter__(self):
        """Async context manager entry"""
        headers = {
            "User-Agent": "XSEMA-Market-Data/2.0.0",
            "Accept": "application/json"
        }
        
        # Add OpenSea API key if available
        if self.configs[Marketplace.OPENSEA].api_key:
            headers["X-API-KEY"] = self.configs[Marketplace.OPENSEA].api_key
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _check_rate_limit(self, marketplace: Marketplace) -> bool:
        """Check if we can make a request to a marketplace"""
        if marketplace not in self.rate_limiters:
            self.rate_limiters[marketplace] = {}
        
        now = datetime.now()
        requests = self.rate_limiters[marketplace]
        
        # Clean old requests
        cutoff = now - timedelta(minutes=1)
        requests = {k: v for k, v in requests.items() if v > cutoff}
        self.rate_limiters[marketplace] = requests
        
        config = self.configs[marketplace]
        if len(requests) >= config.rate_limit:
            return False
        
        # Add current request
        requests[f"req_{len(requests)}"] = now
        return True
    
    async def get_nft_data(self, contract_address: str, token_id: str, network: str = "ethereum") -> Optional[NFTMarketData]:
        """Get real NFT data from marketplaces"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        # Try OpenSea first (most comprehensive)
        if self.configs[Marketplace.OPENSEA].enabled and network in self.configs[Marketplace.OPENSEA].supported_networks:
            if self._check_rate_limit(Marketplace.OPENSEA):
                try:
                    data = await self._get_opensea_nft_data(contract_address, token_id, network)
                    if data:
                        return data
                except Exception as e:
                    logger.warning(f"OpenSea data fetch failed: {e}")
        
        # Try other marketplaces based on network
        if network == "solana" and self.configs[Marketplace.MAGIC_EDEN].enabled:
            if self._check_rate_limit(Marketplace.MAGIC_EDEN):
                try:
                    data = await self._get_magic_eden_nft_data(contract_address, token_id)
                    if data:
                        return data
                except Exception as e:
                    logger.warning(f"Magic Eden data fetch failed: {e}")
        
        # Try Blur for Ethereum
        if network == "ethereum" and self.configs[Marketplace.BLUR].enabled:
            if self._check_rate_limit(Marketplace.BLUR):
                try:
                    data = await self._get_blur_nft_data(contract_address, token_id)
                    if data:
                        return data
                except Exception as e:
                    logger.warning(f"Blur data fetch failed: {e}")
        
        logger.warning(f"No marketplace data available for {contract_address}:{token_id} on {network}")
        return None
    
    async def _get_opensea_nft_data(self, contract_address: str, token_id: str, network: str) -> Optional[NFTMarketData]:
        """Get NFT data from OpenSea API v2"""
        try:
            # OpenSea API v2 endpoint
            url = f"{self.configs[Marketplace.OPENSEA].api_url}/chain/{network}/contract/{contract_address}/nfts/{token_id}"
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Debug: Log the response structure
                    logger.debug(f"OpenSea API response: {data}")
                    
                    # Handle different response formats
                    if isinstance(data, dict):
                        # Extract NFT data
                        nft_data = data.get("nft", {})
                        market_data = data.get("market_data", {})
                        
                        # Parse attributes
                        attributes = []
                        if "traits" in nft_data and isinstance(nft_data["traits"], list):
                            for trait in nft_data["traits"]:
                                if isinstance(trait, dict):
                                    attributes.append({
                                        "trait_type": trait.get("trait_type"),
                                        "value": trait.get("value"),
                                        "display_type": trait.get("display_type")
                                    })
                        
                        # Parse market data safely
                        current_price = None
                        current_price_currency = None
                        floor_price = None
                        floor_price_currency = None
                        
                        if "floor_price" in market_data and isinstance(market_data["floor_price"], dict):
                            try:
                                floor_price = float(market_data["floor_price"].get("amount", 0))
                                floor_price_currency = market_data["floor_price"].get("currency", "ETH")
                                current_price = floor_price
                                current_price_currency = floor_price_currency
                            except (ValueError, TypeError):
                                logger.warning("Invalid floor price data from OpenSea")
                        
                        return NFTMarketData(
                            token_id=token_id,
                            contract_address=contract_address,
                            network=network,
                            marketplace=Marketplace.OPENSEA,
                            name=nft_data.get("name", f"#{token_id}"),
                            description=nft_data.get("description", ""),
                            image_url=nft_data.get("image_url", ""),
                            external_url=nft_data.get("external_url"),
                            current_price=current_price,
                            current_price_currency=current_price_currency,
                            floor_price=floor_price,
                            floor_price_currency=floor_price_currency,
                            collection_name=nft_data.get("collection", {}).get("name") if isinstance(nft_data.get("collection"), dict) else None,
                            collection_slug=nft_data.get("collection", {}).get("slug") if isinstance(nft_data.get("collection"), dict) else None,
                            collection_verified=nft_data.get("collection", {}).get("verified", False) if isinstance(nft_data.get("collection"), dict) else False,
                            attributes=attributes,
                            last_updated=datetime.now(),
                            data_source="opensea"
                        )
                    else:
                        logger.warning(f"Unexpected OpenSea API response format: {type(data)}")
                        return None
                else:
                    logger.warning(f"OpenSea API returned {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching OpenSea data: {e}")
            return None
    
    async def _get_magic_eden_nft_data(self, contract_address: str, token_id: str) -> Optional[NFTMarketData]:
        """Get NFT data from Magic Eden API"""
        try:
            # Magic Eden API endpoint - use mint address directly
            url = f"{self.configs[Marketplace.MAGIC_EDEN].api_url}/tokens/{contract_address}"
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract data
                    attributes = []
                    if "attributes" in data:
                        for attr in data["attributes"]:
                            attributes.append({
                                "trait_type": attr.get("trait_type"),
                                "value": attr.get("value")
                            })
                    
                    return NFTMarketData(
                        token_id=token_id,
                        contract_address=contract_address,
                        network="solana",
                        marketplace=Marketplace.MAGIC_EDEN,
                        name=data.get("name", f"#{token_id}"),
                        description=data.get("description", ""),
                        image_url=data.get("image", ""),
                        attributes=attributes,
                        last_updated=datetime.now(),
                        data_source="magic_eden"
                    )
                else:
                    logger.warning(f"Magic Eden API returned {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Magic Eden data: {e}")
            return None
    
    async def _get_blur_nft_data(self, contract_address: str, token_id: str) -> Optional[NFTMarketData]:
        """Get NFT data from Blur API"""
        try:
            # Blur API endpoint
            url = f"{self.configs[Marketplace.BLUR].api_url}/nft/{contract_address}/{token_id}"
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract data
                    attributes = []
                    if "attributes" in data:
                        for attr in data["attributes"]:
                            attributes.append({
                                "trait_type": attr.get("trait_type"),
                                "value": attr.get("value")
                            })
                    
                    return NFTMarketData(
                        token_id=token_id,
                        contract_address=contract_address,
                        network="ethereum",
                        marketplace=Marketplace.BLUR,
                        name=data.get("name", f"#{token_id}"),
                        description=data.get("description", ""),
                        image_url=data.get("image", ""),
                        attributes=attributes,
                        last_updated=datetime.now(),
                        data_source="blur"
                    )
                else:
                    logger.warning(f"Blur API returned {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Blur data: {e}")
            return None
    
    async def get_collection_data(self, contract_address: str, network: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get collection-level data from marketplaces"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        # Try OpenSea first
        if self.configs[Marketplace.OPENSEA].enabled and network in self.configs[Marketplace.OPENSEA].supported_networks:
            if self._check_rate_limit(Marketplace.OPENSEA):
                try:
                    # Use the correct OpenSea API endpoint for collections
                    url = f"{self.configs[Marketplace.OPENSEA].api_url}/collection/{contract_address}"
                    
                    headers = {}
                    if self.configs[Marketplace.OPENSEA].api_key:
                        headers["X-API-KEY"] = self.configs[Marketplace.OPENSEA].api_key
                    
                    async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                        if response.status == 200:
                            data = await response.json()
                            collection = data.get("collection", {})
                            stats = collection.get("stats", {})
                            
                            return {
                                "name": collection.get("name"),
                                "description": collection.get("description"),
                                "image_url": collection.get("image_url"),
                                "external_url": collection.get("external_url"),
                                "verified": collection.get("verified", False),
                                "floor_price": stats.get("floor_price"),
                                "total_supply": stats.get("total_supply"),
                                "owners_count": stats.get("num_owners"),
                                "data_source": "opensea"
                            }
                        else:
                            logger.warning(f"OpenSea API returned {response.status} for collection {contract_address}")
                except Exception as e:
                    logger.warning(f"OpenSea collection fetch failed: {e}")
        
        return None
    
    def get_marketplace_status(self) -> Dict[str, Any]:
        """Get status of all marketplaces"""
        status = {}
        
        for marketplace, config in self.configs.items():
            status[marketplace.value] = {
                "enabled": config.enabled,
                "api_url": config.api_url,
                "rate_limit": config.rate_limit,
                "supported_networks": config.supported_networks,
                "has_api_key": bool(config.api_key)
            }
        
        return status

# Global instance
market_data_manager = MarketDataManager()

async def test_market_data_integration():
    """Test market data integration"""
    async with market_data_manager as manager:
        print("\n📊 Market Data Integration Test:")
        print("=" * 50)
        
        # Test OpenSea (if API key available)
        if manager.configs[Marketplace.OPENSEA].api_key:
            print("Testing OpenSea integration...")
            # Test with a known NFT (Bored Ape #1)
            nft_data = await manager.get_nft_data(
                "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",  # BAYC contract
                "1",  # Token ID
                "ethereum"
            )
            if nft_data:
                print(f"✅ OpenSea: Fetched {nft_data.name}")
                print(f"   Floor Price: {nft_data.floor_price} {nft_data.floor_price_currency}")
            else:
                print("❌ OpenSea: Failed to fetch data")
        else:
            print("⚠️ OpenSea: No API key configured")
            print("   To test OpenSea, set OPENSEA_API_KEY environment variable")
            print("   Example: $env:OPENSEA_API_KEY='920418bd75db4fa2a05780bff97a0f32'")
        
        # Test Magic Eden
        print("\nTesting Magic Eden integration...")
        # Test with a known Solana NFT
        nft_data = await manager.get_nft_data(
            "SoLNFGRD5bzKprM5WLqyVwfWqHVeVxQA12e5Q4L7PMQ",  # Solana NFT
            "1",
            "solana"
        )
        if nft_data:
            print(f"✅ Magic Eden: Fetched {nft_data.name}")
        else:
            print("❌ Magic Eden: Failed to fetch data")
        
        print(f"\n📊 Summary: Market data integration ready")
        return True

if __name__ == "__main__":
    # Test the market data integration
    asyncio.run(test_market_data_integration())
