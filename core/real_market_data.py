"""
Real Market Data Service for XSEMA
Fetches live data from OpenSea and other marketplaces
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import json

logger = logging.getLogger(__name__)

class RealMarketDataService:
    """Service for fetching real market data from OpenSea and other sources"""
    
    def __init__(self):
        self.opensea_api_key = os.getenv("OPENSEA_API_KEY")
        self.opensea_base_url = "https://api.opensea.io/api/v2"  # Use v2 API
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, datetime] = {}
        self.cache_duration = timedelta(minutes=2)  # Market data changes quickly
        
        # No hardcoded collections - everything is dynamic
        logger.info("🚀 Real Market Data Service initialized - Dynamic collection discovery enabled")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "XSEMA/1.0",
                "Accept": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache or key not in self.cache_ttl:
            return False
        return datetime.now() < self.cache_ttl[key]
    
    def _set_cache(self, key: str, data: Any):
        """Set data in cache with TTL"""
        self.cache[key] = data
        self.cache_ttl[key] = datetime.now() + self.cache_duration
    
    async def get_collection_stats(self, contract_address: str) -> Optional[Dict[str, Any]]:
        """Get real collection statistics from OpenSea"""
        cache_key = f"collection_stats_{contract_address}"
        
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached collection stats for {contract_address}")
            return self.cache[cache_key]
        
        if not self.session:
            logger.error("Session not initialized")
            return None
        
        try:
            # First, we need to find the collection slug from the collections list
            # OpenSea API v2 doesn't support direct contract address lookup
            # We'll search through collections to find the matching one
            collections_url = f"{self.opensea_base_url}/collections?offset=0&limit=50"
            
            headers = {}
            if self.opensea_api_key:
                headers["X-API-KEY"] = self.opensea_api_key
            
            logger.info(f"Searching for collection with contract {contract_address}")
            
            async with self.session.get(collections_url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    collections = data.get("collections", [])
                    
                    # Find collection with matching contract address
                    target_collection = None
                    for collection in collections:
                        contracts = collection.get("contracts", [])
                        for contract in contracts:
                            if contract.get("address", "").lower() == contract_address.lower():
                                target_collection = collection
                                break
                        if target_collection:
                            break
                    
                    if not target_collection:
                        logger.warning(f"Collection with contract {contract_address} not found in OpenSea collections")
                        return None
                    
                    # Now get stats using the collection slug
                    collection_slug = target_collection.get("collection")
                    if not collection_slug:
                        logger.warning(f"No slug found for collection {contract_address}")
                        return None
                    
                    # Use the collection slug for stats
                    stats_url = f"{self.opensea_base_url}/collections/{collection_slug}/stats"
                    
                    logger.info(f"Fetching collection stats from OpenSea: {stats_url}")
                    
                    async with self.session.get(stats_url, headers=headers, timeout=30) as response:
                        if response.status == 200:
                            data = await response.json()
                            stats = data.get("stats", {})
                            
                            # Extract key statistics
                            collection_data = {
                                "floor_price": stats.get("floor_price"),
                                "floor_price_currency": "ETH",
                                "total_volume": stats.get("total_volume"),
                                "volume_24h": stats.get("one_day_volume"),
                                "volume_7d": stats.get("seven_day_volume"),
                                "total_supply": stats.get("total_supply"),
                                "owners_count": stats.get("num_owners"),
                                "sales_24h": stats.get("one_day_sales"),
                                "sales_7d": stats.get("seven_day_sales"),
                                "last_updated": datetime.now().isoformat(),
                                "data_source": "opensea"
                            }
                            
                            # Cache the data
                            self._set_cache(cache_key, collection_data)
                            
                            logger.info(f"✅ Successfully fetched stats for {contract_address}")
                            return collection_data
                            
                        else:
                            logger.warning(f"OpenSea API returned {response.status} for collection {contract_address}")
                            if response.status == 404:
                                logger.warning("Collection not found - check contract address")
                            elif response.status == 429:
                                logger.warning("Rate limited - consider adding API key")
                            
                            return None
                    
        except Exception as e:
            logger.error(f"Error fetching collection stats: {e}")
            return None
    
    async def get_collection_info(self, contract_address: str) -> Optional[Dict[str, Any]]:
        """Get collection information from OpenSea"""
        cache_key = f"collection_info_{contract_address}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        if not self.session:
            return None
        
        try:
            # First, we need to find the collection slug from the collections list
            collections_url = f"{self.opensea_base_url}/collections?offset=0&limit=50"
            
            headers = {}
            if self.opensea_api_key:
                headers["X-API-KEY"] = self.opensea_api_key
            
            async with self.session.get(collections_url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    collections = data.get("collections", [])
                    
                    # Find collection with matching contract address
                    target_collection = None
                    for collection in collections:
                        contracts = collection.get("contracts", [])
                        for contract in contracts:
                            if contract.get("address", "").lower() == contract_address.lower():
                                target_collection = collection
                                break
                        if target_collection:
                            break
                    
                    if not target_collection:
                        logger.warning(f"Collection with contract {contract_address} not found in OpenSea collections")
                        return None
                    
                    # Return the collection info directly from the search results
                    collection_info = {
                        "name": target_collection.get("name"),
                        "description": target_collection.get("description"),
                        "image_url": target_collection.get("image_url"),
                        "external_url": target_collection.get("opensea_url"),
                        "verified": False,  # OpenSea API v2 doesn't provide verification status
                        "slug": target_collection.get("collection"),
                        "contract_address": contract_address,
                        "last_updated": datetime.now().isoformat(),
                        "data_source": "opensea"
                    }
                    
                    self._set_cache(cache_key, collection_info)
                    return collection_info
                    
                else:
                    logger.warning(f"OpenSea API returned {response.status} for collections search")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching collection info: {e}")
            return None
            
            headers = {}
            if self.opensea_api_key:
                headers["X-API-KEY"] = self.opensea_api_key
            
            async with self.session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    collection = data.get("collection", {})
                    
                    collection_info = {
                        "name": collection.get("name"),
                        "description": collection.get("description"),
                        "image_url": collection.get("image_url"),
                        "external_url": collection.get("external_url"),
                        "verified": collection.get("verified", False),
                        "slug": collection.get("slug"),
                        "contract_address": contract_address,
                        "last_updated": datetime.now().isoformat(),
                        "data_source": "opensea"
                    }
                    
                    self._set_cache(cache_key, collection_info)
                    return collection_info
                    
                else:
                    logger.warning(f"OpenSea API returned {response.status} for collection info {contract_address}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching collection info: {e}")
            return None
    
    async def get_nft_data(self, contract_address: str, token_id: str) -> Optional[Dict[str, Any]]:
        """Get individual NFT data from OpenSea"""
        cache_key = f"nft_data_{contract_address}_{token_id}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        if not self.session:
            return None
        
        try:
            url = f"{self.opensea_base_url}/assets/{contract_address}/{token_id}"
            
            headers = {}
            if self.opensea_api_key:
                headers["X-API-KEY"] = self.opensea_api_key
            
            async with self.session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract NFT data
                    name = data.get("name", f"#{token_id}")
                    if not name or name == "None":
                        name = f"#{token_id}"
                    
                    # Get listing data
                    listing = data.get("seaport_sell_orders", [{}])[0] if data.get("seaport_sell_orders") else {}
                    current_price = None
                    if listing:
                        try:
                            current_price = float(listing.get("current_price", 0)) / (10 ** 18)  # Convert from wei to ETH
                        except (ValueError, TypeError):
                            current_price = None
                    
                    # Get collection data
                    collection = data.get("collection", {})
                    
                    nft_data = {
                        "token_id": token_id,
                        "contract_address": contract_address,
                        "name": name,
                        "description": data.get("description", ""),
                        "image_url": data.get("image_url"),
                        "external_url": data.get("external_url"),
                        "current_price": current_price,
                        "current_price_currency": "ETH" if current_price else None,
                        "is_listed": bool(current_price),
                        "collection_name": collection.get("name"),
                        "collection_slug": collection.get("slug"),
                        "collection_verified": collection.get("verified", False),
                        "attributes": data.get("traits", []),
                        "last_updated": datetime.now().isoformat(),
                        "data_source": "opensea"
                    }
                    
                    self._set_cache(cache_key, nft_data)
                    return nft_data
                    
                else:
                    logger.warning(f"OpenSea API returned {response.status} for NFT {contract_address}/{token_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching NFT data: {e}")
            return None
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get real market overview from OpenSea"""
        cache_key = "market_overview"
        
        if self._is_cache_valid(cache_key):
            logger.info("Using cached market overview")
            return self.cache[cache_key]
        
        if not self.session:
            logger.error("Session not initialized")
            return None
        
        try:
            # Get available collections from OpenSea
            collections_url = f"{self.opensea_base_url}/collections?offset=0&limit=10"
            
            headers = {}
            if self.opensea_api_key:
                headers["X-API-KEY"] = self.opensea_api_key
            
            logger.info("Fetching available collections from OpenSea")
            
            async with self.session.get(collections_url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    collections = data.get("collections", [])
                    
                    if not collections:
                        logger.warning("No collections found in OpenSea API response")
                        return None
                    
                    logger.info(f"Found {len(collections)} collections in OpenSea")
                    
                    # Process the first few collections
                    processed_collections = []
                    total_volume_24h = 0
                    
                    for collection in collections[:5]:  # Use first 5 collections
                        collection_slug = collection.get("collection")
                        collection_name = collection.get("name", "Unknown")
                        contract_address = collection.get("contracts", [{}])[0].get("address", "Unknown")
                        
                        if collection_slug:
                            # Get stats for this collection
                            stats = await self.get_collection_stats(contract_address)
                            
                            if stats:
                                processed_collections.append({
                                    "name": collection_name,
                                    "slug": collection_slug,
                                    "contract_address": contract_address,
                                    "floor_price": stats.get("total", {}).get("floor_price"),
                                    "floor_price_currency": "ETH",
                                    "volume_24h": stats.get("intervals", [{}])[0].get("volume"),
                                    "volume_7d": stats.get("intervals", [{}])[1].get("volume") if len(stats.get("intervals", [])) > 1 else None,
                                    "total_volume": stats.get("total", {}).get("volume"),
                                    "total_supply": None,  # Not available in this API
                                    "owners_count": stats.get("total", {}).get("num_owners"),
                                    "verified": False,  # Not available in this API
                                    "image_url": collection.get("image_url")
                                })
                                
                                # Add to total volume
                                volume_24h = stats.get("intervals", [{}])[0].get("volume", 0)
                                total_volume_24h += volume_24h
                    
                    market_data = {
                        "collections": processed_collections,
                        "total_volume_24h": total_volume_24h,
                        "active_collections": len(processed_collections),
                        "market_status": "active",
                        "last_updated": datetime.now().isoformat()
                    }
                    
                    logger.info(f"📊 Market overview: {market_data['active_collections']} active collections")
                    
                    # Cache the result
                    self._set_cache(cache_key, market_data)
                    
                    return market_data
                else:
                    logger.error(f"Failed to fetch collections: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return None
    
    async def get_live_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get live market activity (recent sales, listings, etc.)"""
        logger.info("Fetching live market activity...")
        
        # Get market overview to generate activity from real collections
        overview = await self.get_market_overview()
        if not overview or not overview.get("collections"):
            return []
        
        activity = []
        
        # Generate activity from the first few collections
        for collection in overview["collections"][:3]:
            if collection.get("floor_price"):
                activity.append({
                    "collection_name": collection["name"],
                    "contract_address": collection["contract_address"],
                    "event_type": "floor_price_update",
                    "price": collection["floor_price"],
                    "currency": "ETH",
                    "timestamp": datetime.now().isoformat(),
                    "source": "opensea"
                })
        
        return activity[:limit]

# Global instance
real_market_service = RealMarketDataService()

async def test_real_market_data():
    """Test the real market data service"""
    print("\n🚀 Testing Real Market Data Service...")
    print("=" * 50)
    
    try:
        async with real_market_service as service:
            # Test market overview (this will discover collections dynamically)
            print("📈 Testing market overview...")
            overview = await service.get_market_overview()
            
            if overview:
                print(f"✅ Market Overview:")
                print(f"   Active Collections: {overview['active_collections']}")
                print(f"   24h Total Volume: {overview['total_volume_24h']:.2f} ETH")
                print(f"   Collections: {len(overview['collections'])}")
                
                # Show discovered collections
                if overview['collections']:
                    print(f"\n📋 Discovered Collections:")
                    for i, collection in enumerate(overview['collections'][:3], 1):
                        print(f"   {i}. {collection['name']} ({collection['contract_address'][:8]}...)")
                        print(f"      Floor: {collection['floor_price'] or 'N/A'} ETH")
                        print(f"      Volume 24h: {collection['volume_24h'] or 'N/A'} ETH")
            else:
                print("❌ Could not fetch market overview")
            
            return True
            
    except Exception as e:
        print(f"❌ Real market data test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_real_market_data())
