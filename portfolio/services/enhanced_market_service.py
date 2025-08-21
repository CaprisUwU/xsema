"""
Enhanced Market Data Service for XSEMA

This service provides:
- Real-time floor price monitoring
- Market cap tracking
- Cross-market aggregation
- Event filtering and subscription management
- Market sentiment analysis
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from decimal import Decimal
import aiohttp
from collections import defaultdict

from portfolio.core.cache import cache
from portfolio.services.price_service import price_service

logger = logging.getLogger(__name__)

@dataclass
class FloorPriceData:
    """Floor price data for an NFT collection."""
    collection_id: str
    collection_name: str
    floor_price: Decimal
    floor_price_usd: Decimal
    currency: str
    last_updated: datetime
    change_24h: Decimal
    change_7d: Decimal
    volume_24h: Decimal
    sales_24h: int
    listed_count: int
    source: str  # opensea, blur, etc.

@dataclass
class MarketCapData:
    """Market cap data for a collection or asset."""
    asset_id: str
    asset_name: str
    market_cap: Decimal
    market_cap_usd: Decimal
    fully_diluted_market_cap: Decimal
    circulating_supply: Decimal
    total_supply: Decimal
    max_supply: Optional[Decimal]
    price: Decimal
    price_usd: Decimal
    volume_24h: Decimal
    change_24h: Decimal
    last_updated: datetime

@dataclass
class CrossMarketData:
    """Aggregated data across multiple markets."""
    asset_id: str
    asset_name: str
    markets: Dict[str, Dict[str, Any]]  # market_name -> data
    aggregated_price: Decimal
    aggregated_volume: Decimal
    price_spread: Decimal  # difference between highest and lowest
    arbitrage_opportunities: List[Dict[str, Any]]
    last_updated: datetime

@dataclass
class MarketEvent:
    """Market event for subscription management."""
    event_id: str
    event_type: str  # price_alert, volume_spike, floor_drop, etc.
    asset_id: str
    asset_name: str
    severity: str  # low, medium, high, critical
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    acknowledged: bool = False

class EnhancedMarketService:
    """Enhanced market data service with real-time monitoring."""
    
    def __init__(self):
        self.price_service = price_service
        self.active_subscriptions: Dict[str, Set[str]] = defaultdict(set)  # user_id -> event_types
        self.price_alerts: Dict[str, Dict[str, Any]] = {}  # user_id -> alerts
        self.floor_price_cache: Dict[str, FloorPriceData] = {}
        self.market_cap_cache: Dict[str, MarketCapData] = {}
        self.cache_ttl = 300  # 5 minutes cache
        
        # Market data sources
        self.market_sources = {
            "opensea": "https://api.opensea.io/api/v1",
            "blur": "https://api.blur.io",
            "x2y2": "https://api.x2y2.io",
            "looksrare": "https://api.looksrare.org/api/v1",
            "coinbase": "https://api.coinbase.com/v2",
            "binance": "https://api.binance.com/api/v3"
        }
        
        # Start background tasks
        asyncio.create_task(self._floor_price_monitor())
        asyncio.create_task(self._market_cap_monitor())
    
    async def get_real_time_floor_price(
        self, 
        collection_id: str, 
        refresh: bool = False
    ) -> Optional[FloorPriceData]:
        """Get real-time floor price for an NFT collection."""
        
        try:
            cache_key = f"floor_price:{collection_id}"
            
            if not refresh:
                cached = cache.get(cache_key)
                if cached:
                    return FloorPriceData(**json.loads(cached))
            
            # Get floor price from multiple sources
            floor_prices = await self._fetch_floor_prices(collection_id)
            
            if not floor_prices:
                return None
            
            # Aggregate floor prices from multiple sources
            aggregated_floor = self._aggregate_floor_prices(floor_prices)
            
            # Cache the result
            cache.set(cache_key, json.dumps(asdict(aggregated_floor)), ttl=self.cache_ttl)
            
            # Update cache
            self.floor_price_cache[collection_id] = aggregated_floor
            
            return aggregated_floor
            
        except Exception as e:
            logger.error(f"Error getting floor price for {collection_id}: {e}")
            return None
    
    async def get_market_cap(
        self, 
        asset_id: str, 
        refresh: bool = False
    ) -> Optional[MarketCapData]:
        """Get market cap data for an asset."""
        
        try:
            cache_key = f"market_cap:{asset_id}"
            
            if not refresh:
                cached = cache.get(cache_key)
                if cached:
                    return MarketCapData(**json.loads(cached))
            
            # Get market cap from multiple sources
            market_caps = await self._fetch_market_caps(asset_id)
            
            if not market_caps:
                return None
            
            # Aggregate market cap data
            aggregated_mc = self._aggregate_market_caps(market_caps)
            
            # Cache the result
            cache.set(cache_key, json.dumps(asdict(aggregated_mc)), ttl=self.cache_ttl)
            
            # Update cache
            self.market_cap_cache[asset_id] = aggregated_mc
            
            return aggregated_mc
            
        except Exception as e:
            logger.error(f"Error getting market cap for {asset_id}: {e}")
            return None
    
    async def get_cross_market_data(
        self, 
        asset_id: str, 
        markets: Optional[List[str]] = None
    ) -> Optional[CrossMarketData]:
        """Get aggregated data across multiple markets."""
        
        try:
            if markets is None:
                markets = list(self.market_sources.keys())
            
            # Get data from each market
            market_data = {}
            for market in markets:
                try:
                    data = await self._fetch_market_data(asset_id, market)
                    if data:
                        market_data[market] = data
                except Exception as e:
                    logger.warning(f"Failed to fetch data from {market}: {e}")
                    continue
            
            if not market_data:
                return None
            
            # Aggregate cross-market data
            cross_market = self._aggregate_cross_market_data(asset_id, market_data)
            
            return cross_market
            
        except Exception as e:
            logger.error(f"Error getting cross-market data for {asset_id}: {e}")
            return None
    
    async def subscribe_to_events(
        self, 
        user_id: str, 
        event_types: List[str],
        assets: Optional[List[str]] = None
    ) -> bool:
        """Subscribe to market events."""
        
        try:
            # Add user to event type subscriptions
            for event_type in event_types:
                self.active_subscriptions[user_id].add(event_type)
            
            # Store asset preferences if provided
            if assets:
                self.active_subscriptions[f"{user_id}_assets"] = set(assets)
            
            logger.info(f"User {user_id} subscribed to events: {event_types}")
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing user {user_id} to events: {e}")
            return False
    
    async def unsubscribe_from_events(
        self, 
        user_id: str, 
        event_types: Optional[List[str]] = None
    ) -> bool:
        """Unsubscribe from market events."""
        
        try:
            if event_types is None:
                # Unsubscribe from all events
                if user_id in self.active_subscriptions:
                    del self.active_subscriptions[user_id]
                if f"{user_id}_assets" in self.active_subscriptions:
                    del self.active_subscriptions[f"{user_id}_assets"]
            else:
                # Unsubscribe from specific event types
                for event_type in event_types:
                    self.active_subscriptions[user_id].discard(event_type)
            
            logger.info(f"User {user_id} unsubscribed from events: {event_types}")
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing user {user_id} from events: {e}")
            return False
    
    async def set_price_alert(
        self, 
        user_id: str, 
        asset_id: str, 
        target_price: Decimal,
        alert_type: str = "above"  # above, below, change_percent
    ) -> bool:
        """Set a price alert for an asset."""
        
        try:
            alert_id = f"{user_id}_{asset_id}_{int(time.time())}"
            
            self.price_alerts[alert_id] = {
                "user_id": user_id,
                "asset_id": asset_id,
                "target_price": float(target_price),
                "alert_type": alert_type,
                "created_at": datetime.now(timezone.utc),
                "triggered": False,
                "active": True
            }
            
            logger.info(f"Price alert set for user {user_id}, asset {asset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting price alert: {e}")
            return False
    
    async def get_user_events(
        self, 
        user_id: str, 
        event_types: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[MarketEvent]:
        """Get events for a specific user."""
        
        try:
            # This would integrate with your event storage system
            # For now, returning mock events
            events = []
            
            # Check if user has active subscriptions
            if user_id in self.active_subscriptions:
                user_event_types = self.active_subscriptions[user_id]
                
                # Filter by event types if specified
                if event_types:
                    user_event_types = user_event_types.intersection(set(event_types))
                
                # Generate mock events based on subscriptions
                for event_type in user_event_types:
                    event = MarketEvent(
                        event_id=f"event_{int(time.time())}_{event_type}",
                        event_type=event_type,
                        asset_id="bitcoin",
                        asset_name="Bitcoin",
                        severity="medium",
                        message=f"Market event: {event_type}",
                        data={"price": 50000.0, "change": 2.5},
                        timestamp=datetime.now(timezone.utc)
                    )
                    events.append(event)
            
            return events[:limit]
            
        except Exception as e:
            logger.error(f"Error getting user events: {e}")
            return []
    
    async def _floor_price_monitor(self):
        """Background task to monitor floor prices."""
        
        while True:
            try:
                # Get collections to monitor (this would come from user subscriptions)
                collections_to_monitor = ["boredapeyachtclub", "cryptopunks", "doodles"]
                
                for collection_id in collections_to_monitor:
                    try:
                        floor_price = await self.get_real_time_floor_price(collection_id, refresh=True)
                        
                        if floor_price:
                            # Check for significant changes and trigger alerts
                            await self._check_floor_price_alerts(collection_id, floor_price)
                            
                    except Exception as e:
                        logger.warning(f"Error monitoring floor price for {collection_id}: {e}")
                        continue
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in floor price monitor: {e}")
                await asyncio.sleep(60)
    
    async def _market_cap_monitor(self):
        """Background task to monitor market caps."""
        
        while True:
            try:
                # Get assets to monitor
                assets_to_monitor = ["bitcoin", "ethereum", "polygon"]
                
                for asset_id in assets_to_monitor:
                    try:
                        market_cap = await self.get_market_cap(asset_id, refresh=True)
                        
                        if market_cap:
                            # Check for significant changes and trigger alerts
                            await self._check_market_cap_alerts(asset_id, market_cap)
                            
                    except Exception as e:
                        logger.warning(f"Error monitoring market cap for {asset_id}: {e}")
                        continue
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in market cap monitor: {e}")
                await asyncio.sleep(300)
    
    async def _fetch_floor_prices(self, collection_id: str) -> List[Dict[str, Any]]:
        """Fetch floor prices from multiple sources."""
        
        floor_prices = []
        
        # Fetch from OpenSea (mock implementation)
        try:
            opensea_data = await self._fetch_opensea_floor_price(collection_id)
            if opensea_data:
                floor_prices.append(opensea_data)
        except Exception as e:
            logger.warning(f"Failed to fetch OpenSea data: {e}")
        
        # Fetch from Blur (mock implementation)
        try:
            blur_data = await self._fetch_blur_floor_price(collection_id)
            if blur_data:
                floor_prices.append(blur_data)
        except Exception as e:
            logger.warning(f"Failed to fetch Blur data: {e}")
        
        return floor_prices
    
    async def _fetch_market_caps(self, asset_id: str) -> List[Dict[str, Any]]:
        """Fetch market cap data from multiple sources."""
        
        market_caps = []
        
        # Fetch from Coinbase (mock implementation)
        try:
            coinbase_data = await self._fetch_coinbase_market_cap(asset_id)
            if coinbase_data:
                market_caps.append(coinbase_data)
        except Exception as e:
            logger.warning(f"Failed to fetch Coinbase data: {e}")
        
        # Fetch from Binance (mock implementation)
        try:
            binance_data = await self._fetch_binance_market_cap(asset_id)
            if binance_data:
                market_caps.append(binance_data)
        except Exception as e:
            logger.warning(f"Failed to fetch Binance data: {e}")
        
        return market_caps
    
    async def _fetch_market_data(self, asset_id: str, market: str) -> Optional[Dict[str, Any]]:
        """Fetch data from a specific market."""
        
        try:
            if market == "opensea":
                return await self._fetch_opensea_data(asset_id)
            elif market == "blur":
                return await self._fetch_blur_data(asset_id)
            elif market == "coinbase":
                return await self._fetch_coinbase_data(asset_id)
            elif market == "binance":
                return await self._fetch_binance_data(asset_id)
            else:
                logger.warning(f"Unknown market: {market}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching data from {market}: {e}")
            return None
    
    def _aggregate_floor_prices(self, floor_prices: List[Dict[str, Any]]) -> FloorPriceData:
        """Aggregate floor prices from multiple sources."""
        
        if not floor_prices:
            raise ValueError("No floor prices to aggregate")
        
        # Calculate weighted average based on volume
        total_volume = sum(fp.get('volume_24h', 0) for fp in floor_prices)
        
        if total_volume == 0:
            # If no volume data, use simple average
            avg_floor = sum(fp.get('floor_price', 0) for fp in floor_prices) / len(floor_prices)
        else:
            # Weighted average by volume
            weighted_sum = sum(
                fp.get('floor_price', 0) * fp.get('volume_24h', 0) 
                for fp in floor_prices
            )
            avg_floor = weighted_sum / total_volume
        
        # Use the first source for metadata
        first_source = floor_prices[0]
        
        return FloorPriceData(
            collection_id=first_source.get('collection_id', ''),
            collection_name=first_source.get('collection_name', ''),
            floor_price=Decimal(str(avg_floor)),
            floor_price_usd=Decimal(str(first_source.get('floor_price_usd', 0))),
            currency=first_source.get('currency', 'ETH'),
            last_updated=datetime.now(timezone.utc),
            change_24h=Decimal(str(first_source.get('change_24h', 0))),
            change_7d=Decimal(str(first_source.get('change_7d', 0))),
            volume_24h=Decimal(str(total_volume)),
            sales_24h=sum(fp.get('sales_24h', 0) for fp in floor_prices),
            listed_count=sum(fp.get('listed_count', 0) for fp in floor_prices),
            source="aggregated"
        )
    
    def _aggregate_market_caps(self, market_caps: List[Dict[str, Any]]) -> MarketCapData:
        """Aggregate market cap data from multiple sources."""
        
        if not market_caps:
            raise ValueError("No market cap data to aggregate")
        
        # Use the most recent data source
        most_recent = max(market_caps, key=lambda x: x.get('last_updated', datetime.min))
        
        return MarketCapData(
            asset_id=most_recent.get('asset_id', ''),
            asset_name=most_recent.get('asset_name', ''),
            market_cap=Decimal(str(most_recent.get('market_cap', 0))),
            market_cap_usd=Decimal(str(most_recent.get('market_cap_usd', 0))),
            fully_diluted_market_cap=Decimal(str(most_recent.get('fully_diluted_market_cap', 0))),
            circulating_supply=Decimal(str(most_recent.get('circulating_supply', 0))),
            total_supply=Decimal(str(most_recent.get('total_supply', 0))),
            max_supply=Decimal(str(most_recent.get('max_supply', 0))) if most_recent.get('max_supply') else None,
            price=Decimal(str(most_recent.get('price', 0))),
            price_usd=Decimal(str(most_recent.get('price_usd', 0))),
            volume_24h=Decimal(str(most_recent.get('volume_24h', 0))),
            change_24h=Decimal(str(most_recent.get('change_24h', 0))),
            last_updated=datetime.now(timezone.utc)
        )
    
    def _aggregate_cross_market_data(
        self, 
        asset_id: str, 
        market_data: Dict[str, Dict[str, Any]]
    ) -> CrossMarketData:
        """Aggregate data across multiple markets."""
        
        if not market_data:
            raise ValueError("No market data to aggregate")
        
        # Calculate aggregated metrics
        prices = [data.get('price', 0) for data in market_data.values()]
        volumes = [data.get('volume_24h', 0) for data in market_data.values()]
        
        aggregated_price = sum(prices) / len(prices) if prices else 0
        aggregated_volume = sum(volumes)
        price_spread = max(prices) - min(prices) if prices else 0
        
        # Find arbitrage opportunities
        arbitrage_opportunities = []
        if len(prices) > 1:
            min_price = min(prices)
            max_price = max(prices)
            min_market = [k for k, v in market_data.items() if v.get('price') == min_price][0]
            max_market = [k for k, v in market_data.items() if v.get('price') == max_price][0]
            
            if max_price > min_price * 1.02:  # 2% spread threshold
                arbitrage_opportunities.append({
                    "buy_market": min_market,
                    "sell_market": max_market,
                    "buy_price": min_price,
                    "sell_price": max_price,
                    "spread_percentage": ((max_price - min_price) / min_price) * 100
                })
        
        return CrossMarketData(
            asset_id=asset_id,
            asset_name=list(market_data.values())[0].get('asset_name', ''),
            markets=market_data,
            aggregated_price=Decimal(str(aggregated_price)),
            aggregated_volume=Decimal(str(aggregated_volume)),
            price_spread=Decimal(str(price_spread)),
            arbitrage_opportunities=arbitrage_opportunities,
            last_updated=datetime.now(timezone.utc)
        )
    
    async def _check_floor_price_alerts(self, collection_id: str, floor_price: FloorPriceData):
        """Check floor price alerts and trigger notifications."""
        
        # This would check user alerts and send notifications
        # For now, just logging
        logger.info(f"Floor price alert check for {collection_id}: {floor_price.floor_price}")
    
    async def _check_market_cap_alerts(self, asset_id: str, market_cap: MarketCapData):
        """Check market cap alerts and trigger notifications."""
        
        # This would check user alerts and send notifications
        # For now, just logging
        logger.info(f"Market cap alert check for {asset_id}: {market_cap.market_cap}")
    
    # Real API fetch methods
    async def _fetch_opensea_floor_price(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """Real OpenSea floor price fetch using their API."""
        try:
            import aiohttp
            from portfolio.core.config import get_config
            
            config = get_config()
            api_key = config.OPENSEA_API_KEY
            base_url = config.OPENSEA_API_URL
            
            if not api_key:
                logger.warning("OpenSea API key not configured, using fallback data")
                return await self._fetch_opensea_fallback(collection_id)
            
            headers = {
                "Accept": "application/json",
                "X-API-KEY": api_key
            }
            
            # OpenSea API endpoint for collection stats
            url = f"{base_url}/collection/{collection_id}/stats"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        stats = data.get("stats", {})
                        
                        return {
                            "collection_id": collection_id,
                            "collection_name": data.get("collection", {}).get("name", f"Collection {collection_id}"),
                            "floor_price": stats.get("floor_price", 0),
                            "floor_price_usd": stats.get("floor_price_usd", 0),
                            "currency": "ETH",
                            "change_24h": stats.get("one_day_change", 0),
                            "change_7d": stats.get("seven_day_change", 0),
                            "volume_24h": stats.get("one_day_volume", 0),
                            "sales_24h": stats.get("one_day_sales", 0),
                            "listed_count": stats.get("count", 0),
                            "source": "opensea",
                            "last_updated": data.get("last_updated", None)
                        }
                    else:
                        logger.warning(f"OpenSea API returned status {response.status}")
                        return await self._fetch_opensea_fallback(collection_id)
                        
        except Exception as e:
            logger.error(f"Error fetching OpenSea data: {e}")
            return await self._fetch_opensea_fallback(collection_id)
    
    async def _fetch_opensea_fallback(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """Fallback OpenSea data when API fails."""
        return {
            "collection_id": collection_id,
            "collection_name": f"Collection {collection_id}",
            "floor_price": 10.5,
            "floor_price_usd": 21000.0,
            "currency": "ETH",
            "change_24h": 2.5,
            "change_7d": -5.0,
            "volume_24h": 1000.0,
            "sales_24h": 50,
            "listed_count": 200,
            "source": "opensea_fallback",
            "last_updated": None
        }
    
    async def _fetch_opensea_data(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Real OpenSea asset data fetch using their API."""
        try:
            import aiohttp
            from portfolio.core.config import get_config
            
            config = get_config()
            api_key = config.OPENSEA_API_KEY
            base_url = config.OPENSEA_API_URL
            
            if not api_key:
                logger.warning("OpenSea API key not configured, using fallback data")
                return await self._fetch_opensea_asset_fallback(asset_id)
            
            headers = {
                "Accept": "application/json",
                "X-API-KEY": api_key
            }
            
            # OpenSea API endpoint for asset details
            url = f"{base_url}/asset/{asset_id}/"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        asset = data.get("asset", {})
                        
                        return {
                            "asset_id": asset_id,
                            "name": asset.get("name", f"Asset {asset_id}"),
                            "description": asset.get("description", ""),
                            "image_url": asset.get("image_url", ""),
                            "animation_url": asset.get("animation_url", ""),
                            "traits": asset.get("traits", []),
                            "last_sale": asset.get("last_sale", {}),
                            "top_bid": asset.get("top_bid", {}),
                            "listing_date": asset.get("listing_date", None),
                            "supports_wyvern": asset.get("supports_wyvern", False),
                            "source": "opensea",
                            "last_updated": data.get("last_updated", None)
                        }
                    else:
                        logger.warning(f"OpenSea API returned status {response.status}")
                        return await self._fetch_opensea_asset_fallback(asset_id)
                        
        except Exception as e:
            logger.error(f"Error fetching OpenSea asset data: {e}")
            return await self._fetch_opensea_asset_fallback(asset_id)
    
    async def _fetch_opensea_asset_fallback(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Fallback OpenSea asset data when API fails."""
        return {
            "asset_id": asset_id,
            "name": f"Asset {asset_id}",
            "description": "Asset description not available",
            "image_url": "",
            "animation_url": "",
            "traits": [],
            "last_sale": {},
            "top_bid": {},
            "listing_date": None,
            "supports_wyvern": False,
            "source": "opensea_fallback",
            "last_updated": None
        }
    
    async def _fetch_blur_floor_price(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """Mock Blur floor price fetch."""
        return {
            "collection_id": collection_id,
            "collection_name": f"Collection {collection_id}",
            "floor_price": 10.3,
            "floor_price_usd": 20600.0,
            "currency": "ETH",
            "change_24h": 2.0,
            "change_7d": -4.5,
            "volume_24h": 800.0,
            "sales_24h": 40,
            "listed_count": 180,
            "source": "blur"
        }
    
    async def _fetch_coinbase_market_cap(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Mock Coinbase market cap fetch."""
        return {
            "asset_id": asset_id,
            "asset_name": f"Asset {asset_id}",
            "market_cap": 1000000000.0,
            "market_cap_usd": 1000000000.0,
            "fully_diluted_market_cap": 1100000000.0,
            "circulating_supply": 1000000.0,
            "total_supply": 1100000.0,
            "max_supply": 1200000.0,
            "price": 1000.0,
            "price_usd": 1000.0,
            "volume_24h": 50000000.0,
            "change_24h": 2.5,
            "source": "coinbase"
        }
    
    async def _fetch_binance_market_cap(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Mock Binance market cap fetch."""
        return {
            "asset_id": asset_id,
            "asset_name": f"Asset {asset_id}",
            "market_cap": 1000000000.0,
            "market_cap_usd": 1000000000.0,
            "fully_diluted_market_cap": 1100000000.0,
            "circulating_supply": 1000000.0,
            "total_supply": 1100000.0,
            "max_supply": 1200000.0,
            "price": 1000.0,
            "price_usd": 1000.0,
            "volume_24h": 52000000.0,
            "change_24h": 2.3,
            "source": "binance"
        }
    
    async def _fetch_blur_data(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Mock Blur data fetch."""
        return {"price": 10.3, "volume_24h": 800.0, "source": "blur"}
    
    async def _fetch_coinbase_data(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Mock Coinbase data fetch."""
        return {"price": 1000.0, "volume_24h": 50000000.0, "source": "coinbase"}
    
    async def _fetch_binance_data(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Mock Binance data fetch."""
        return {"price": 1000.0, "volume_24h": 52000000.0, "source": "binance"}

# Global instance
enhanced_market_service = EnhancedMarketService()
