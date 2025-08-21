"""
Portfolio Cache Management

Portfolio-specific caching functionality for performance optimization.
"""
from cachetools import TTLCache, LRUCache, cached
from typing import Any, Optional, Dict, Callable
import json
import hashlib
import functools
from .config import settings


class PortfolioCache:
    """Portfolio-specific cache implementation."""
    
    def __init__(self):
        self.ttl_cache = TTLCache(
            maxsize=settings.portfolio_cache_maxsize,
            ttl=settings.portfolio_cache_ttl
        )
        self.lru_cache = LRUCache(maxsize=settings.portfolio_cache_maxsize)
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Create a cache key from arguments."""
        key_data = {
            'prefix': prefix,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self.ttl_cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self.ttl_cache[key] = value
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self.ttl_cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache."""
        self.ttl_cache.clear()
        self.lru_cache.clear()
    
    def cache_portfolio(self, portfolio_id: str, data: Dict[str, Any]) -> None:
        """Cache portfolio data."""
        key = self._make_key("portfolio", portfolio_id)
        self.set(key, data)
    
    def get_portfolio(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        """Get cached portfolio data."""
        key = self._make_key("portfolio", portfolio_id)
        return self.get(key)
    
    def cache_asset_price(self, asset_id: str, price_data: Dict[str, Any]) -> None:
        """Cache asset price data."""
        key = self._make_key("asset_price", asset_id)
        self.set(key, price_data)
    
    def get_asset_price(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get cached asset price data."""
        key = self._make_key("asset_price", asset_id)
        return self.get(key)


    def __call__(self, ttl: int = None):
        """Make the cache instance callable as a decorator."""
        def decorator(func: Callable) -> Callable:
            cache_instance = TTLCache(maxsize=1000, ttl=ttl or settings.portfolio_cache_ttl)
            return cached(cache_instance)(func)
        return decorator


# Global cache instance
cache = PortfolioCache()
