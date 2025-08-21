"""
Cache module for temporary data storage
"""
from datetime import datetime, timedelta
from typing import Any, Optional

class Cache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self._store = {}
        
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if exists and not expired"""
        if key not in self._store:
            return None
            
        value, expiration = self._store[key]
        if expiration and datetime.now() > expiration:
            del self._store[key]
            return None
            
        return value
        
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store value with time-to-live in seconds"""
        expiration = datetime.now() + timedelta(seconds=ttl) if ttl else None
        self._store[key] = (value, expiration)
        
    def delete(self, key: str) -> None:
        """Remove a key from cache"""
        if key in self._store:
            del self._store[key]
            
    def clear(self) -> None:
        """Clear all cached values"""
        self._store.clear()

# Singleton cache instance
cache = Cache()


def initialize_cache():
    """
    Initialize the cache system.
    This function can be extended to set up different cache backends
    or configure cache settings.
    """
    global cache
    # Reset cache to ensure clean state
    cache.clear()
    
    # Initialize with default settings
    cache.set("cache_initialized", True, ttl=3600)  # 1 hour TTL
    
    return cache


def get_cache():
    """
    Get the global cache instance.
    """
    return cache
