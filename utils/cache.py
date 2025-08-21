"""
Cache utility module for handling Redis caching.

This module provides decorators and utilities for caching function results
and managing cache keys with TTL (Time To Live) support.
"""

import asyncio
import functools
import json
import logging
from typing import Any, Callable, Optional, TypeVar, Union
from datetime import timedelta

import redis.asyncio as redis
from fastapi import Request, HTTPException, status

# Configure logging
logger = logging.getLogger(__name__)

# Type variable for generic function typing
T = TypeVar('T')

class CacheConfig:
    """Configuration for cache settings."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: int = 300,  # 5 minutes
        enabled: bool = True
    ) -> None:
        """Initialize cache configuration.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            default_ttl: Default time-to-live in seconds
            enabled: Whether caching is enabled
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.default_ttl = default_ttl
        self.enabled = enabled
        self._redis: Optional[redis.Redis] = None
    
    @property
    def redis(self) -> redis.Redis:
        """Lazy-load Redis client."""
        if self._redis is None:
            self._redis = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )
        return self._redis
    
    async def close(self) -> None:
        """Close the Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

# Default configuration (can be overridden)
cache_config = CacheConfig()

def get_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """Generate a cache key from function arguments.
    
    Args:
        prefix: Key prefix
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
        
    Returns:
        str: Generated cache key
    """
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
    
    # Add keyword arguments
    for k, v in sorted(kwargs.items()):
        if v is not None:
            key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)

def cached(
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None,
    ignore_kwargs: Optional[list[str]] = None
) -> Callable[..., Callable[..., Any]]:
    """Decorator to cache function results in Redis.
    
    Args:
        ttl: Time to live in seconds (default: cache_config.default_ttl)
        key_prefix: Custom cache key prefix (default: function name)
        ignore_kwargs: List of kwargs to exclude from cache key generation
        
    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        prefix = key_prefix or f"cache:{func.__module__}:{func.__name__}"
        
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Skip caching if disabled
            if not cache_config.enabled:
                return await func(*args, **kwargs)
            
            # Filter out ignored kwargs
            cache_kwargs = kwargs.copy()
            if ignore_kwargs:
                for k in ignore_kwargs:
                    cache_kwargs.pop(k, None)
            
            # Generate cache key
            cache_key = get_cache_key(prefix, *args, **cache_kwargs)
            
            try:
                # Try to get from cache
                cached_value = await cache_config.redis.get(cache_key)
                if cached_value is not None:
                    logger.debug("Cache hit for key: %s", cache_key)
                    return json.loads(cached_value)
                
                # Call the function if not in cache
                logger.debug("Cache miss for key: %s", cache_key)
                result = await func(*args, **kwargs)
                
                # Cache the result
                if result is not None:
                    ttl_actual = ttl if ttl is not None else cache_config.default_ttl
                    await cache_config.redis.set(
                        cache_key,
                        json.dumps(result),
                        ex=ttl_actual
                    )
                
                return result
                
            except Exception as e:
                logger.error("Cache error for key %s: %s", cache_key, str(e))
                # If there's a cache error, still try to call the function
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

class RateLimiter:
    """Rate limiting using Redis."""
    
    def __init__(self, redis_client: redis.Redis, rate: int, period: int) -> None:
        """Initialize rate limiter.
        
        Args:
            redis_client: Redis client instance
            rate: Number of allowed requests per period
            period: Time period in seconds
        """
        self.redis = redis_client
        self.rate = rate
        self.period = period
    
    async def is_rate_limited(self, key: str) -> tuple[bool, int]:
        """Check if the request should be rate limited.
        
        Args:
            key: Rate limit key
            
        Returns:
            tuple: (is_limited, remaining_seconds)
        """
        current = await self.redis.get(key)
        if current is None:
            # First request in this period
            await self.redis.setex(key, self.period, 1)
            return False, self.period
        
        current = int(current)
        if current >= self.rate:
            # Rate limit exceeded
            ttl = await self.redis.ttl(key)
            return True, ttl
        
        # Increment the counter
        await self.redis.incr(key)
        return False, self.period - (await self.redis.ttl(key))

def rate_limited(
    key: str,
    rate: int = 100,
    period: int = 60,
    request: Optional[Request] = None
) -> Callable[..., Callable[..., Any]]:
    """Decorator to rate limit a function.
    
    Args:
        key: Rate limit key (can include {request} for request attributes)
        rate: Number of allowed requests per period
        period: Time period in seconds
        request: Optional FastAPI Request object for dynamic keys
        
    Returns:
        Decorated function with rate limiting
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Skip rate limiting if disabled
            if not cache_config.enabled:
                return await func(*args, **kwargs)
            
            # Format the key with request attributes if available
            formatted_key = key
            if request and '{request.' in key:
                try:
                    # Get request from kwargs if not provided
                    req = kwargs.get('request') or request
                    # Replace placeholders like {request.client.host}
                    formatted_key = key.format(request=req)
                except Exception as e:
                    logger.warning("Error formatting rate limit key: %s", str(e))
                    formatted_key = key
            
            # Create rate limiter instance
            limiter = RateLimiter(cache_config.redis, rate, period)
            
            # Check rate limit
            is_limited, retry_after = await limiter.is_rate_limited(formatted_key)
            if is_limited:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": "Rate limit exceeded",
                        "retry_after": retry_after,
                        "rate_limit": rate,
                        "period": period
                    },
                    headers={"Retry-After": str(retry_after)}
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
