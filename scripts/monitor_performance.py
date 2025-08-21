"""
Performance monitoring for the NFT API.

This script monitors:
1. API response times
2. Cache hit/miss ratios
3. Rate limiting metrics
4. Redis memory usage
"""
import asyncio
import time
import logging
import psutil
import redis
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the blockchain service
from services.blockchain import BlockchainService
from portfolio.core.config import settings

class PerformanceMonitor:
    """Monitor performance metrics for the API and Redis."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.redis_client = redis.Redis.from_url(
            settings.redis_url,
            password=settings.redis_password or None,
            decode_responses=True
        )
        self.metrics = {
            'api_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'rate_limited_requests': 0,
            'total_response_time': 0.0,
            'errors': 0
        }
        self.start_time = time.time()
    
    async def collect_metrics(self):
        """Collect and log performance metrics."""
        try:
            # Get Redis info
            redis_info = self.redis_client.info()
            
            # Calculate cache hit rate
            total_cache = self.metrics['cache_hits'] + self.metrics['cache_misses']
            cache_hit_rate = (self.metrics['cache_hits'] / total_cache * 100) if total_cache > 0 else 0
            
            # Calculate average response time
            avg_response_time = (
                self.metrics['total_response_time'] / self.metrics['api_calls']
                if self.metrics['api_calls'] > 0 else 0
            )
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            
            # Log metrics
            logger.info("\n=== Performance Metrics ===")
            logger.info(f"Uptime: {time.time() - self.start_time:.1f}s")
            logger.info(f"API Calls: {self.metrics['api_calls']}")
            logger.info(f"Cache Hits: {self.metrics['cache_hits']}")
            logger.info(f"Cache Misses: {self.metrics['cache_misses']}")
            logger.info(f"Cache Hit Rate: {cache_hit_rate:.1f}%")
            logger.info(f"Rate Limited Requests: {self.metrics['rate_limited_requests']}")
            logger.info(f"Average Response Time: {avg_response_time*1000:.2f}ms")
            logger.info(f"Errors: {self.metrics['errors']}")
            logger.info(f"CPU Usage: {cpu_percent}%")
            logger.info(f"Memory Usage: {memory_info.percent}%")
            logger.info(f"Redis Memory Usage: {int(redis_info.get('used_memory', 0) / 1024 / 1024)}MB")
            logger.info("=" * 30)
            
            return True
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            return False
    
    def increment_metric(self, metric_name: str, value: float = 1):
        """Increment a metric counter."""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
    
    async def monitor_loop(self, interval: int = 60):
        """Run the monitoring loop."""
        logger.info("Starting performance monitoring...")
        
        try:
            while True:
                await self.collect_metrics()
                await asyncio.sleep(interval)
                
        except asyncio.CancelledError:
            logger.info("Stopping performance monitoring...")
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")

# Global monitor instance
monitor = PerformanceMonitor()

def track_performance(func):
    """Decorator to track API performance metrics."""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        monitor.increment_metric('api_calls')
        
        try:
            result = await func(*args, **kwargs)
            monitor.increment_metric('cache_hits' if getattr(func, '_cache_hit', False) else 'cache_misses')
            return result
            
        except Exception as e:
            monitor.increment_metric('errors')
            if isinstance(e, RateLimitExceeded):
                monitor.increment_metric('rate_limited_requests')
            raise
            
        finally:
            monitor.increment_metric('total_response_time', time.time() - start_time)
    
    return wrapper

async def main():
    """Run the performance monitor."""
    # Start the monitoring loop
    monitor_task = asyncio.create_task(monitor.monitor_loop(interval=60))
    
    try:
        # Keep the script running
        while True:
            await asyncio.sleep(3600)  # Run until interrupted
            
    except (KeyboardInterrupt, SystemExit):
        # Clean up
        monitor_task.cancel()
        await monitor_task
        logger.info("Performance monitoring stopped.")

if __name__ == "__main__":
    # Apply the performance tracking decorator to relevant methods
    from functools import update_wrapper
    
    # Patch the blockchain service methods
    original_get_nfts = BlockchainService.get_wallet_nfts
    original_get_metadata = BlockchainService.get_token_metadata
    
    async def patched_get_nfts(self, *args, **kwargs):
        return await track_performance(original_get_nfts)(self, *args, **kwargs)
        
    async def patched_get_metadata(self, *args, **kwargs):
        return await track_performance(original_get_metadata)(self, *args, **kwargs)
    
    # Apply the patches
    BlockchainService.get_wallet_nfts = patched_get_nfts
    BlockchainService.get_token_metadata = patched_get_metadata
    
    # Run the monitor
    asyncio.run(main())
