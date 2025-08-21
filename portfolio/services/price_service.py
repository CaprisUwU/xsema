"""
Price Service - Handles real-time and historical price data for cryptocurrencies and NFTs.
"""
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from core.config import settings
from core.cache import cache
from portfolio.utils.logger import logger

class PriceService:
    """Service for fetching and managing price data"""
    
    def __init__(self):
        self.sessions = {}
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self.cmc_url = "https://pro-api.coinmarketcap.com/v2"
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session"""
        loop = asyncio.get_event_loop()
        if loop not in self.sessions or self.sessions[loop].closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.sessions[loop] = aiohttp.ClientSession(timeout=timeout)
        return self.sessions[loop]
    
    # Removed invalid cache decorator
    async def get_prices(
        self, 
        asset_ids: List[str], 
        vs_currencies: List[str] = ['usd']
    ) -> Dict:
        """Get current prices for multiple assets"""
        cache_key = f"prices_{'_'.join(sorted(asset_ids))}_{'_'.join(sorted(vs_currencies))}"
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        try:
            url = f"{self.coingecko_url}/simple/price"
            params = {
                'ids': ','.join(asset_ids),
                'vs_currencies': ','.join(vs_currencies),
                'include_24hr_change': 'true'
            }
            
            session = await self.get_session()
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                result = await response.json()
                cache.set(cache_key, result, ttl=300)
                return result
                
        except Exception as e:
            logger.error(f"Error getting prices: {str(e)}")
            return {}
    
    # Removed invalid cache decorator
    async def get_price_history(
        self,
        asset_id: str,
        days: int = 30,
        vs_currency: str = 'usd'
    ) -> Dict:
        """Get historical price data for an asset"""
        cache_key = f"history_{asset_id}_{days}_{vs_currency}"
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        try:
            url = f"{self.coingecko_url}/coins/{asset_id}/market_chart"
            params = {
                'vs_currency': vs_currency,
                'days': days
            }
            
            session = await self.get_session()
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                result = {
                    'prices': [{'timestamp': t, 'price': p} 
                             for t, p in data.get('prices', [])],
                    'market_caps': [{'timestamp': t, 'market_cap': m} 
                                  for t, m in data.get('market_caps', [])],
                    'volumes': [{'timestamp': t, 'volume': v} 
                              for t, v in data.get('total_volumes', [])]
                }
                
        except Exception as e:
            logger.error(f"Error getting price history: {str(e)}")
            result = {'prices': [], 'market_caps': [], 'volumes': []}
            cache.set(cache_key, result, ttl=3600)
            return result
    
    async def close(self):
        """Close all open sessions"""
        for session in self.sessions.values():
            if not session.closed:
                await session.close()
        self.sessions.clear()

# Singleton instance
price_service = PriceService()
