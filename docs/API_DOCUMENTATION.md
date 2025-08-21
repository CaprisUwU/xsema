# XSEMA API Documentation
*Updated: 21 August 2025 - Test Coverage: 31% → Target: 85%+*

## Overview

XSEMA (Advanced NFT Security & Analytics Platform) provides a comprehensive API for NFT analytics, security analysis, and portfolio management across multiple blockchain networks.

**Base URL**: `http://localhost:8001` (Development)  
**Production URL**: TBD  
**API Version**: v2.0.0  
**Authentication**: API Key required for most endpoints

## Quick Start

### 1. Health Check
```bash
curl http://localhost:8001/health
```

### 2. API Information
```bash
curl http://localhost:8001/
```

### 3. API Documentation (Swagger UI)
```
http://localhost:8001/docs
```

## Authentication

Most endpoints require an API key. Include it in the header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8001/api/v1/portfolio/portfolios
```

## Core Endpoints

### Root & Health
- `GET /` - API information and welcome message
- `GET /health` - Health check and system status

### Multi-Chain Support
- `GET /api/v1/multi-chain/networks` - List supported networks
- `GET /api/v1/multi-chain/networks/status` - Network connectivity status
- `GET /api/v1/multi-chain/networks/{chain_type}/info` - Network information

### Portfolio Management
- `GET /api/v1/portfolio/portfolios` - List portfolios
- `POST /api/v1/portfolio/portfolios` - Create portfolio
- `GET /api/v1/portfolio/portfolios/{portfolio_id}` - Get portfolio details
- `PUT /api/v1/portfolio/portfolios/{portfolio_id}` - Update portfolio
- `DELETE /api/v1/portfolio/portfolios/{portfolio_id}` - Delete portfolio

### Wallet Analysis
- `GET /api/v1/wallet-analysis/cluster/{wallet_address}` - Analyze wallet
- `POST /api/v1/wallet-analysis/batch` - Batch wallet analysis
- `GET /api/v1/wallet-analysis/batch/{job_id}` - Get batch job status

### NFT Management
- `GET /api/v1/nfts` - List NFTs
- `POST /api/v1/nfts` - Create NFT record
- `GET /api/v1/nfts/{nft_id}` - Get NFT details
- `PUT /api/v1/nfts/{nft_id}` - Update NFT
- `DELETE /api/v1/nfts/{nft_id}` - Delete NFT

### Market Data
- `GET /api/v1/markets` - Market overview
- `GET /api/v1/markets/collections` - Collections data
- `GET /api/v1/markets/ranking` - Market rankings

### Trait Analysis
- `GET /api/v1/traits/rarity/{collection_id}` - Trait rarity analysis
- `POST /api/v1/traits/analyze` - Analyze NFT traits

### WebSocket Endpoints
- `WS /ws` - Real-time event streaming

## Detailed Endpoint Reference

### Multi-Chain Networks

#### Get Supported Networks
```bash
GET /api/v1/multi-chain/networks
```

**Response**:
```json
[
  "ethereum",
  "polygon", 
  "bsc",
  "arbitrum",
  "optimism",
  "base",
  "avalanche",
  "fantom",
  "solana"
]
```

#### Get Network Status
```bash
GET /api/v1/multi-chain/networks/status
```

**Response**:
```json
{
  "ethereum": {
    "connected": true,
    "chain_id": 1,
    "block_number": 12345678,
    "rpc_url": "https://ethereum.publicnode.com"
  },
  "polygon": {
    "connected": false,
    "error": "Connection failed"
  }
}
```

### Portfolio Management

#### Create Portfolio
```bash
POST /api/v1/portfolio/portfolios
Content-Type: application/json

{
  "name": "My NFT Portfolio",
  "description": "Personal NFT collection",
  "wallet_addresses": ["0x1234..."],
  "tags": ["personal", "art"]
}
```

**Response**:
```json
{
  "portfolio_id": "uuid-here",
  "name": "My NFT Portfolio",
  "description": "Personal NFT collection",
  "wallet_addresses": ["0x1234..."],
  "tags": ["personal", "art"],
  "created_at": "2025-08-11T06:30:00Z",
  "total_value": 0,
  "nft_count": 0
}
```

#### Get Portfolio Details
```bash
GET /api/v1/portfolio/portfolios/{portfolio_id}
```

**Response**:
```json
{
  "portfolio_id": "uuid-here",
  "name": "My NFT Portfolio",
  "description": "Personal NFT collection",
  "wallet_addresses": ["0x1234..."],
  "tags": ["personal", "art"],
  "created_at": "2025-08-11T06:30:00Z",
  "total_value": 1500.50,
  "nft_count": 25,
  "assets": [
    {
      "nft_id": "uuid-here",
      "name": "Cool NFT #123",
      "collection": "Cool Collection",
      "value": 150.50,
      "chain": "ethereum"
    }
  ]
}
```

### Wallet Analysis

#### Analyze Single Wallet
```bash
GET /api/v1/wallet-analysis/cluster/{wallet_address}
```

**Response**:
```json
{
  "wallet_address": "0x1234...",
  "risk_score": 0.15,
  "cluster_id": "cluster-123",
  "cluster_members": ["0x1234...", "0x5678..."],
  "anomalies": [
    {
      "type": "wash_trading",
      "confidence": 0.85,
      "description": "Suspicious trading patterns detected"
    }
  ],
  "security_recommendations": [
    "Monitor for unusual activity",
    "Consider wallet isolation"
  ]
}
```

#### Batch Wallet Analysis
```bash
POST /api/v1/wallet-analysis/batch
Content-Type: application/json

{
  "wallet_addresses": ["0x1234...", "0x5678..."],
  "depth": "medium",
  "user_id": "user-123"
}
```

**Response**:
```json
{
  "job_id": "job-uuid-here",
  "status": "pending",
  "total_wallets": 2,
  "message": "Analysis job created successfully"
}
```

#### Get Batch Job Status
```bash
GET /api/v1/wallet-analysis/batch/{job_id}
```

**Response**:
```json
{
  "job_id": "job-uuid-here",
  "status": "completed",
  "total_wallets": 2,
  "progress": 100,
  "results": [
    {
      "wallet_address": "0x1234...",
      "risk_score": 0.15,
      "cluster_id": "cluster-123"
    }
  ]
}
```

### NFT Management

#### Create NFT Record
```bash
POST /api/v1/nfts
Content-Type: application/json

{
  "name": "Cool NFT #123",
  "collection": "Cool Collection",
  "token_id": "123",
  "contract_address": "0xabcd...",
  "chain": "ethereum",
  "metadata": {
    "image": "https://example.com/image.png",
    "description": "A really cool NFT"
  },
  "traits": [
    {
      "trait_type": "Background",
      "value": "Blue",
      "rarity": 0.25
    }
  ]
}
```

**Response**:
```json
{
  "nft_id": "uuid-here",
  "name": "Cool NFT #123",
  "collection": "Cool Collection",
  "token_id": "123",
  "contract_address": "0xabcd...",
  "chain": "ethereum",
  "created_at": "2025-08-11T06:30:00Z",
  "value": 150.50
}
```

### Market Data

#### Get Market Overview
```bash
GET /api/v1/markets
```

**Response**:
```json
{
  "total_volume_24h": 1500000,
  "total_sales_24h": 2500,
  "top_collections": [
    {
      "name": "Cool Collection",
      "volume_24h": 150000,
      "floor_price": 2.5,
      "sales_count": 150
    }
  ],
  "market_trends": {
    "volume_change_24h": 0.15,
    "floor_price_change_24h": -0.05
  }
}
```

### Trait Analysis

#### Get Trait Rarity
```bash
GET /api/v1/traits/rarity/{collection_id}
```

**Response**:
```json
{
  "collection_id": "uuid-here",
  "collection_name": "Cool Collection",
  "total_nfts": 10000,
  "traits": {
    "Background": {
      "Blue": {"count": 2500, "rarity": 0.25},
      "Red": {"count": 1000, "rarity": 0.10},
      "Green": {"count": 6500, "rarity": 0.65}
    },
    "Eyes": {
      "Normal": {"count": 8000, "rarity": 0.80},
      "Laser": {"count": 2000, "rarity": 0.20}
    }
  }
}
```

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8001/ws');
```

### Subscribe to Events
```json
{
  "type": "subscribe",
  "channels": ["nft_events", "sales", "market_updates"]
}
```

### Event Types
- `nft_events`: New NFT listings, sales, transfers
- `sales`: Real-time sales data
- `market_updates`: Price changes, volume updates

### Example Event
```json
{
  "type": "nft_sale",
  "data": {
    "nft_id": "uuid-here",
    "collection": "Cool Collection",
    "price": 150.50,
    "buyer": "0x1234...",
    "seller": "0x5678...",
    "timestamp": "2025-08-11T06:30:00Z"
  }
}
```

## Error Handling

### Standard Error Response
```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "request_id": "uuid-here",
  "timestamp": "2025-08-11T06:30:00Z"
}
```

### Common HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing/invalid API key)
- `404` - Not Found
- `429` - Rate Limited
- `500` - Internal Server Error

### Rate Limiting
- **Standard endpoints**: 100 requests per minute
- **Batch operations**: 10 requests per minute
- **WebSocket connections**: 5 concurrent connections per IP

## SDKs and Libraries

### Python
```python
import requests

api_key = "your-api-key"
headers = {"X-API-Key": api_key}

# Get portfolio
response = requests.get(
    "http://localhost:8001/api/v1/portfolio/portfolios",
    headers=headers
)
portfolios = response.json()
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'http://localhost:8001',
  headers: {
    'X-API-Key': 'your-api-key'
  }
});

// Get portfolio
const portfolios = await api.get('/api/v1/portfolio/portfolios');
```

### cURL Examples
```bash
# Get all portfolios
curl -H "X-API-Key: your-api-key" \
  http://localhost:8001/api/v1/portfolio/portfolios

# Create portfolio
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Portfolio"}' \
  http://localhost:8001/api/v1/portfolio/portfolios

# Analyze wallet
curl -H "X-API-Key: your-api-key" \
  http://localhost:8001/api/v1/wallet-analysis/cluster/0x1234...
```

## Best Practices

### 1. Error Handling
- Always check HTTP status codes
- Implement exponential backoff for retries
- Log request IDs for debugging

### 2. Rate Limiting
- Implement client-side rate limiting
- Use batch endpoints for multiple operations
- Cache responses when possible

### 3. Security
- Never expose API keys in client-side code
- Use HTTPS in production
- Validate all input data

### 4. Performance
- Use pagination for large datasets
- Implement caching strategies
- Use WebSocket for real-time updates

## Support

- **Documentation**: `/docs` (Swagger UI)
- **Health Check**: `/health`
- **API Status**: Check network status endpoint
- **Issues**: Check server logs for detailed error information

---

*Last Updated: August 11, 2025*  
*Version: 2.0.0*  
*XSEMA API Documentation*
