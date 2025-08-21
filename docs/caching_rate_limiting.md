# Caching and Rate Limiting

This document describes the caching and rate limiting implementation in the NFT Analytics API.

## Table of Contents
- [Overview](#overview)
- [Caching](#caching)
  - [How It Works](#how-it-works)
  - [Configuration](#configuration)
  - [Cache Keys](#cache-keys)
  - [Cache Invalidation](#cache-invalidation)
- [Rate Limiting](#rate-limiting)
  - [How It Works](#how-it-works-1)
  - [Configuration](#configuration-1)
  - [Handling Rate Limits](#handling-rate-limits)
- [Monitoring](#monitoring)
- [Best Practices](#best-practices)

## Overview

The API implements both client-side caching and rate limiting to:
- Improve performance by reducing redundant API calls
- Protect against abuse and ensure fair usage
- Maintain high availability for all users

## Caching

### How It Works

Caching is implemented using Redis with the following characteristics:
- **Time-to-Live (TTL)**: Each cached item has a configurable TTL
- **Automatic Invalidation**: Items are automatically removed after their TTL expires
- **Conditional Requests**: Supports ETag and Last-Modified headers when available

### Configuration

Caching can be configured using the following environment variables:

```ini
# Enable/disable caching (default: true)
CACHE_ENABLED=true

# Default TTL in seconds (default: 300)
CACHE_DEFAULT_TTL=300

# Redis connection URL (default: redis://localhost:6379/0)
REDIS_URL=redis://username:password@host:port/db

# Optional Redis password
REDIS_PASSWORD=your_redis_password
```

### Cache Keys

Cache keys are automatically generated based on the function name and its arguments. For example:

```python
@cached(ttl=300, key_prefix="alchemy:nfts:{wallet_address}")
async def get_wallet_nfts(wallet_address: str):
    # Function implementation
    pass
```

This would generate cache keys like: `alchemy:nfts:0x1234...`

### Cache Invalidation

Cache entries are automatically invalidated when:
1. The TTL expires
2. The Redis cache is cleared
3. The application is restarted (for in-memory caches)

To manually invalidate a cache entry, you can use the `invalidate_cache` function:

```python
from utils.cache import invalidate_cache

# Invalidate cache for a specific key
await invalidate_cache("alchemy:nfts:0x1234...")

# Invalidate all cache keys with a prefix
await invalidate_cache("alchemy:nfts:*")
```

## Rate Limiting

### How It Works

Rate limiting is implemented using Redis to track request counts per client. Each client is identified by their IP address or API key.

### Configuration

Rate limiting can be configured using the following environment variables:

```ini
# Enable/disable rate limiting (default: true)
RATE_LIMIT_ENABLED=true

# Number of requests allowed per minute (default: 100)
RATE_LIMIT_PER_MINUTE=100

# Redis connection URL (default: redis://localhost:6379/0)
REDIS_URL=redis://username:password@host:port/db
```

### Handling Rate Limits

When a client exceeds the rate limit, the API will respond with:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
Content-Type: application/json

{
    "detail": "Rate limit exceeded. Please try again in 60 seconds."
}
```

Clients should:
1. Check for the 429 status code
2. Read the `Retry-After` header to determine how long to wait
3. Implement exponential backoff when retrying

## Monitoring

Performance metrics are available via the monitoring script:

```bash
python scripts/monitor_performance.py
```

This will display real-time metrics including:
- API call counts
- Cache hit/miss ratios
- Rate limiting statistics
- System resource usage
- Redis memory usage

## Best Practices

### For API Consumers
- Always check for `429` responses and implement proper backoff
- Cache responses locally when possible
- Use conditional requests with `ETag` and `If-None-Match` headers
- Minimize the number of API calls by batching requests when possible

### For API Developers
- Set appropriate TTLs based on data volatility
- Use descriptive cache key prefixes
- Monitor cache hit/miss ratios and adjust TTLs as needed
- Test rate limiting with different thresholds to find the right balance
- Document rate limits and caching behavior for API consumers
