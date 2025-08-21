# API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require authentication using a Bearer token.

```http
GET /endpoint
Authorization: Bearer your_jwt_token_here
```

## Portfolios

### Create Portfolio
```http
POST /portfolios/
```
**Request Body:**
```json
{
  "name": "My NFT Portfolio",
  "description": "Collection of high-value NFTs",
  "risk_tolerance": "medium"
}
```

**Response:**
```json
{
  "id": "portfolio_123",
  "user_id": "user_456",
  "name": "My NFT Portfolio",
  "description": "Collection of high-value NFTs",
  "risk_tolerance": "medium",
  "created_at": "2025-08-01T12:00:00Z",
  "updated_at": "2025-08-01T12:00:00Z"
}
```

### List Portfolios
```http
GET /portfolios/?skip=0&limit=100
```

### Get Portfolio
```http
GET /portfolios/{portfolio_id}
```

### Update Portfolio
```http
PATCH /portfolios/{portfolio_id}
```

### Delete Portfolio
```http
DELETE /portfolios/{portfolio_id}
```

### Get Portfolio Insights
```http
GET /portfolios/{portfolio_id}/insights?time_range=30d
```

### Get Portfolio Performance
```http
GET /portfolios/{portfolio_id}/performance?time_range=30d
```

## Wallets

### Add Wallet to Portfolio
```http
POST /portfolios/{portfolio_id}/wallets/
```
**Request Body:**
```json
{
  "address": "0x1234...",
  "name": "My Main Wallet",
  "type": "ethereum"
}
```

### List Wallets in Portfolio
```http
GET /portfolios/{portfolio_id}/wallets/
```

### Get Wallet Details
```http
GET /portfolios/{portfolio_id}/wallets/{wallet_id}
```

### Update Wallet
```http
PATCH /portfolios/{portfolio_id}/wallets/{wallet_id}
```

### Delete Wallet
```http
DELETE /portfolios/{portfolio_id}/wallets/{wallet_id}
```

### Get Wallet Balance
```http
GET /portfolios/{portfolio_id}/wallets/{wallet_id}/balance
```
**Response:**
```json
{
  "wallet_id": "wallet_789",
  "address": "0x1234...",
  "native_balance": {
    "amount": "1.5",
    "currency": "ETH",
    "value_usd": "3000.00"
  },
  "tokens": [
    {
      "token_address": "0x...",
      "name": "Example Token",
      "symbol": "EXMPL",
      "balance": "100.0",
      "value_usd": "150.00"
    }
  ],
  "nfts": {
    "count": 5,
    "value_usd": "2500.00"
  },
  "total_value_usd": "5650.00",
  "last_updated": "2025-08-01T12:00:00Z"
}
```

## Assets

### List Assets in Portfolio
```http
GET /portfolios/{portfolio_id}/assets/
```

### Get Asset Details
```http
GET /portfolios/{portfolio_id}/assets/{asset_id}
```

## NFTs

### List NFTs in Portfolio
```http
GET /portfolios/{portfolio_id}/nfts/
```

### Get NFT Details
```http
GET /portfolios/{portfolio_id}/nfts/{nft_id}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting
- 100 requests per minute per IP address
- 1000 requests per day per user

*Last Updated: August 1, 2025*
*Version: 2.0.0*
