# 🚀 Phase 4 API Endpoints Documentation

**XSEMA NFT Analytics Platform - Phase 4 API Reference**

## 🔐 **Authentication Endpoints**

### **User Registration**
```http
POST /auth/register
{
  "username": "string",
  "email": "string", 
  "password": "string"
}
```

### **User Login**
```http
POST /auth/login
{
  "username": "string",
  "password": "string"
}
```

### **Token Refresh**
```http
POST /auth/refresh
Authorization: Bearer {refresh_token}
```

### **User Profile**
```http
GET /auth/profile
Authorization: Bearer {access_token}
```

## 🗄️ **Database Endpoints**

### **Database Health Check**
```http
GET /db/health
```

### **Database Statistics**
```http
GET /db/stats
Authorization: Bearer {access_token}
```

## 📊 **Portfolio Management**

### **Create Portfolio**
```http
POST /portfolios
{
  "name": "string",
  "description": "string",
  "is_public": "boolean"
}
```

### **Get Portfolios**
```http
GET /portfolios
Authorization: Bearer {access_token}
```

### **Add NFT to Portfolio**
```http
POST /portfolios/{portfolio_id}/nfts
{
  "token_id": "string",
  "contract_address": "string",
  "purchase_price": "float"
}
```

## 🖼️ **NFT Management**

### **Get NFT Details**
```http
GET /nfts/{nft_id}
```

### **Search NFTs**
```http
GET /search/nfts?q={query}&collection={address}
```

## 🏪 **Collection Management**

### **Get Collection Info**
```http
GET /collections/{contract_address}
```

### **Get Collection Stats**
```http
GET /collections/{contract_address}/stats
```

## 📈 **Live Market Data**

### **WebSocket Connection**
```websocket
ws://{host}:8001/ws
```

**Subscribe to collection:**
```json
{
  "type": "subscribe",
  "contract_address": "string"
}
```

### **Real-time Floor Price**
```http
GET /market/floor-price/{contract_address}
```

## 🛡️ **Security Endpoints**

### **Security Status**
```http
GET /security/status
Authorization: Bearer {access_token}
```

### **Security Events**
```http
GET /security/events?severity={level}
Authorization: Bearer {access_token}
```

## 📊 **Analytics**

### **Portfolio Analytics**
```http
GET /analytics/portfolio/{portfolio_id}?period={7d|30d|90d}
Authorization: Bearer {access_token}
```

### **Market Overview**
```http
GET /analytics/market/overview
```

## ⚠️ **Error Responses**

```json
{
  "error": "string",
  "message": "string",
  "timestamp": "datetime"
}
```

## 🔧 **Rate Limiting**

- **Auth endpoints**: 5 requests/minute
- **Data endpoints**: 100 requests/minute
- **Analytics**: 50 requests/minute

## 📝 **Example Usage**

```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "email": "user@example.com", "password": "pass"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Create portfolio
curl -X POST http://localhost:8000/portfolios \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"name": "My NFTs", "is_public": false}'
```

---

*Complete API documentation available in the main project docs.*
