# 🚀 NFT Analytics Engine - Complete API Reference

**Version**: 3.0.0  
**Base URL**: `https://api.yourproject.com`  
**Documentation**: Live at `/docs`  
**Last Updated**: January 31, 2025

---

## 📋 **Table of Contents**

1. [Authentication](#authentication)
2. [Core Endpoints](#core-endpoints)
3. [NFT Analytics](#nft-analytics)
4. [Wallet Analysis](#wallet-analysis)
5. [Market Intelligence](#market-intelligence)
6. [Portfolio Management](#portfolio-management)
7. [Security Features](#security-features)
8. [Real-time WebSocket](#real-time-websocket)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

---

## 🔐 **Authentication**

### API Key Authentication
All API requests require authentication via API key in the header:

```http
Authorization: Bearer YOUR_API_KEY
```

### Getting an API Key
```bash
# Request API key (development)
curl -X POST "https://api.yourproject.com/auth/api-key" \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "purpose": "development"}'
```

---

## 🏥 **Health & Status**

### System Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "timestamp": "2025-01-31T12:00:00Z",
  "uptime_seconds": 86400,
  "environment": "production"
}
```

---

## 🎨 **Core Endpoints**

### NFT Analytics

#### Get NFT Details
```http
GET /api/v1/nfts/{contract_address}/{token_id}
```

**Parameters:**
- `contract_address` (string): Ethereum contract address
- `token_id` (string): Token ID

**Example:**
```bash
curl "https://api.yourproject.com/api/v1/nfts/0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D/1" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
  "token_id": "1",
  "name": "BoredApeYachtClub #1",
  "description": "The Bored Ape Yacht Club...",
  "image": "https://ipfs.io/ipfs/...",
  "attributes": [
    {"trait_type": "Background", "value": "Blue"},
    {"trait_type": "Fur", "value": "Brown"}
  ],
  "rarity_score": 342.5,
  "rarity_rank": 156,
  "last_sale": {
    "price": "50.5",
    "currency": "ETH",
    "timestamp": "2025-01-30T10:00:00Z"
  },
  "price_history": [
    {"price": "45.0", "currency": "ETH", "timestamp": "2025-01-29T10:00:00Z"},
    {"price": "50.5", "currency": "ETH", "timestamp": "2025-01-30T10:00:00Z"}
  ]
}
```

#### Get NFT Rarity Analysis
```http
GET /api/v1/nfts/{contract_address}/{token_id}/rarity
```

**Response:**
```json
{
  "rarity_score": 342.5,
  "rarity_rank": 156,
  "total_supply": 10000,
  "percentile": 98.44,
  "trait_analysis": {
    "Background": {"rarity": 0.12, "score": 8.33},
    "Fur": {"rarity": 0.25, "score": 4.0}
  }
}
```

#### Get Similar NFTs
```http
GET /api/v1/nfts/{contract_address}/{token_id}/similar
```

**Query Parameters:**
- `limit` (int, default: 10): Number of similar NFTs to return
- `threshold` (float, default: 0.8): Similarity threshold

**Response:**
```json
{
  "similar_nfts": [
    {
      "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
      "token_id": "2543",
      "similarity_score": 0.92,
      "matching_traits": ["Background", "Fur"],
      "price": "48.2"
    }
  ]
}
```

### Wallet Analysis

#### Get Wallet Overview
```http
GET /api/v1/wallets/{wallet_address}
```

**Example:**
```bash
curl "https://api.yourproject.com/api/v1/wallets/0x1234...abcd" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "ens_name": "vitalik.eth",
  "total_nfts": 1247,
  "total_value_eth": "2847.5",
  "collections": [
    {
      "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
      "name": "Bored Ape Yacht Club",
      "count": 12,
      "floor_price": "45.0"
    }
  ],
  "risk_score": {
    "overall": 3.2,
    "wash_trading": 1.8,
    "suspicious_activity": 0.5
  },
  "cluster_id": "cluster_vip_001",
  "last_activity": "2025-01-31T08:30:00Z"
}
```

#### Get Wallet Activity
```http
GET /api/v1/wallets/{wallet_address}/activity
```

**Query Parameters:**
- `limit` (int, default: 50): Number of activities to return
- `days` (int, default: 30): Days of history

**Response:**
```json
{
  "activities": [
    {
      "type": "purchase",
      "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
      "token_id": "1234",
      "price": "45.5",
      "currency": "ETH",
      "from": "0xabcd...",
      "to": "0x1234...",
      "timestamp": "2025-01-31T08:00:00Z",
      "tx_hash": "0x789..."
    }
  ]
}
```

#### Wallet Clustering Analysis
```http
GET /api/v1/wallets/{wallet_address}/cluster
```

**Response:**
```json
{
  "cluster_id": "cluster_vip_001",
  "cluster_type": "vip_collector",
  "confidence": 0.94,
  "related_wallets": [
    "0xabcd1234...",
    "0xefgh5678..."
  ],
  "cluster_metrics": {
    "total_wallets": 15,
    "total_volume": "12847.5",
    "avg_hold_time": 45.2
  }
}
```

### Market Intelligence

#### Market Summary
```http
GET /api/v1/markets
```

**Query Parameters:**
- `timeframe` (string, default: "24h"): Options: "1h", "24h", "7d", "30d"

**Response:**
```json
{
  "timeframe": "24h",
  "total_volume": "15247.8",
  "total_sales": 2847,
  "avg_price": "5.36",
  "top_collections": [
    {
      "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
      "name": "Bored Ape Yacht Club",
      "volume_24h": "2847.5",
      "sales_count": 45,
      "floor_price": "45.0",
      "change_24h": "+12.5%"
    }
  ]
}
```

#### Collection Details
```http
GET /api/v1/collections/{contract_address}
```

**Response:**
```json
{
  "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
  "name": "Bored Ape Yacht Club",
  "symbol": "BAYC",
  "total_supply": 10000,
  "floor_price": "45.0",
  "volume_24h": "2847.5",
  "volume_7d": "18245.2",
  "volume_total": "847523.8",
  "owners": 6247,
  "social_links": {
    "website": "https://boredapeyachtclub.com",
    "twitter": "@BoredApeYC",
    "discord": "https://discord.gg/3P5K3dzgdB"
  }
}
```

### Security Features

#### Wash Trading Detection
```http
POST /api/v1/security/wash-trading
```

**Body:**
```json
{
  "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
  "token_id": "1234",
  "analysis_days": 30
}
```

**Response:**
```json
{
  "wash_trading_score": 0.12,
  "risk_level": "low",
  "suspicious_transactions": [],
  "analysis": {
    "total_transactions": 15,
    "unique_traders": 12,
    "price_manipulation_score": 0.05
  }
}
```

#### Provenance Verification
```http
GET /api/v1/security/provenance/{contract_address}/{token_id}
```

**Response:**
```json
{
  "verified": true,
  "provenance_score": 0.94,
  "ownership_history": [
    {
      "owner": "0x1234...",
      "from": "2024-01-15T00:00:00Z",
      "to": "2025-01-31T00:00:00Z",
      "verification_method": "blockchain_verified"
    }
  ],
  "authenticity_checks": {
    "contract_verified": true,
    "metadata_consistent": true,
    "image_authentic": true
  }
}
```

---

## 🔌 **Real-time WebSocket**

### Connection
```javascript
const ws = new WebSocket('wss://api.yourproject.com/ws');

ws.onopen = function() {
    console.log('Connected to NFT Analytics Engine');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### Event Types

#### NFT Sale Event
```json
{
  "type": "nft_sale",
  "data": {
    "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
    "token_id": "1234",
    "price": "45.5",
    "currency": "ETH",
    "from": "0xabcd...",
    "to": "0x1234...",
    "timestamp": "2025-01-31T12:00:00Z"
  }
}
```

#### Market Alert
```json
{
  "type": "market_alert",
  "data": {
    "alert_type": "floor_price_change",
    "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
    "old_floor": "40.0",
    "new_floor": "45.0",
    "change_percent": 12.5
  }
}
```

---

## ⚠️ **Error Handling**

### Standard Error Response
```json
{
  "error": "NotFound",
  "message": "NFT not found",
  "code": 404,
  "timestamp": "2025-01-31T12:00:00Z",
  "path": "/api/v1/nfts/0x123.../999999"
}
```

### Error Codes
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `429` - Rate Limited (too many requests)
- `500` - Internal Server Error

---

## ⏱️ **Rate Limiting**

### Limits
- **Free Tier**: 100 requests/minute
- **Pro Tier**: 1000 requests/minute
- **Enterprise**: Custom limits

### Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1643723400
```

---

## 📚 **SDKs & Libraries**

### Python
```python
from nft_analytics import NFTAnalyticsClient

client = NFTAnalyticsClient(api_key="your_api_key")
nft = client.get_nft("0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D", "1")
print(f"Rarity Score: {nft.rarity_score}")
```

### JavaScript
```javascript
import { NFTAnalytics } from 'nft-analytics-sdk';

const client = new NFTAnalytics({ apiKey: 'your_api_key' });
const nft = await client.getNFT('0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D', '1');
console.log(`Rarity Score: ${nft.rarityScore}`);
```

---

## 🔧 **Advanced Features**

### Batch Processing
```http
POST /api/v1/batch/analyze
```

**Body:**
```json
{
  "requests": [
    {
      "type": "nft_analysis",
      "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
      "token_id": "1"
    },
    {
      "type": "wallet_analysis",
      "address": "0x1234567890abcdef1234567890abcdef12345678"
    }
  ]
}
```

### Custom Webhooks
```http
POST /api/v1/webhooks
```

**Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["nft_sale", "market_alert"],
  "filters": {
    "contract_addresses": ["0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"],
    "min_price": "10.0"
  }
}
```

---

## 📞 **Support**

- **Documentation**: https://docs.yourproject.com
- **Discord**: https://discord.gg/yourproject
- **Email**: support@yourproject.com
- **Status Page**: https://status.yourproject.com

---

*API Reference v3.0.0 - Last updated: January 31, 2025*
