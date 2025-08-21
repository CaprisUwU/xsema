"""
Rate limiting utilities for API endpoints.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException, Request, status
import time

class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    For production, consider using Redis or another distributed store.
    """
    def __init__(self, requests: int, window: int):
        """
        Initialize rate limiter.
        
        Args:
            requests: Number of requests allowed per window
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.access_records: Dict[str, list] = {}
        
    async def is_rate_limited(self, key: str) -> bool:
        """
        Check if a request should be rate limited.
        
        Args:
            key: Rate limiting key (e.g., IP address or API key)
            
        Returns:
            bool: True if rate limited, False otherwise
        """
        current_time = time.time()
        
        # Remove old entries outside the current window
        if key in self.access_records:
            self.access_records[key] = [
                timestamp for timestamp in self.access_records[key]
                if current_time - timestamp < self.window
            ]
            
            # Check if we've exceeded the rate limit
            if len(self.access_records[key]) >= self.requests:
                return True
            
            self.access_records[key].append(current_time)
        else:
            self.access_records[key] = [current_time]
            
        return False

# Global rate limiter instance
BATCH_PROCESSING_LIMITER = RateLimiter(
    requests=5,  # 5 requests
    window=60    # per minute
)

def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Client IP address
    """
    if request.client and request.client.host:
        return request.client.host
    return "unknown"

async def rate_limit_check(request: Request, limiter: RateLimiter) -> None:
    """
    Check if a request should be rate limited.
    
    Args:
        request: FastAPI request object
        limiter: RateLimiter instance
        
    Raises:
        HTTPException: 429 if rate limited
    """
    client_ip = get_client_ip(request)
    if await limiter.is_rate_limited(f"batch_process:{client_ip}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": limiter.window
            },
            headers={"Retry-After": str(limiter.window)}
        )
