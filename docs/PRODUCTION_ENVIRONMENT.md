# 🔐 Production Environment Variables Guide

**XSEMA Production Environment Configuration**

## 📋 **Essential Environment Variables**

### **Application Configuration**
```env
APP_ENV=production
APP_DEBUG=false
SECRET_KEY=your_very_long_and_secure_secret_key_here
LOG_LEVEL=INFO
```

### **Database Configuration**
```env
# PostgreSQL
POSTGRES_HOST=your-postgres-host
POSTGRES_PORT=5432
POSTGRES_DB=xsema_production
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_secure_postgres_password
POSTGRES_POOL_SIZE=20
POSTGRES_SSL=true

# Redis
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_redis_password
REDIS_SSL=true
```

### **Security Configuration**
```env
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
RATE_LIMIT_MAX_REQUESTS=100
```

### **External APIs**
```env
OPENSEA_API_KEY=your_opensea_api_key
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your_project_id
```

## 🔧 **Setup Commands**

### **Railway Environment Variables**
```bash
# Set production variables
railway variables set APP_ENV=production
railway variables set SECRET_KEY=your_secret_key
railway variables set POSTGRES_HOST=your_postgres_host
railway variables set POSTGRES_PASSWORD=your_postgres_password
railway variables set REDIS_HOST=your_redis_host
railway variables set OPENSEA_API_KEY=your_opensea_key

# Set as secrets
railway variables set SECRET_KEY=your_secret_key --secret
railway variables set POSTGRES_PASSWORD=your_password --secret
```

### **Generate Secure Keys**
```bash
# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate database password
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

## 🚨 **Security Best Practices**

1. **Never commit .env files**
   ```bash
   echo ".env*" >> .gitignore
   ```

2. **Use different files for environments**
   - `.env.local` - Local development
   - `.env.staging` - Staging
   - `.env.production` - Production

3. **Restrict file permissions**
   ```bash
   chmod 600 .env.production
   ```

## 📊 **Validation Endpoint**

```python
@app.get("/env/health")
async def environment_health():
    """Check environment variable health."""
    required_vars = [
        "SECRET_KEY", "POSTGRES_HOST", "POSTGRES_PASSWORD",
        "REDIS_HOST", "OPENSEA_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    return {
        "status": "healthy" if not missing_vars else "unhealthy",
        "missing_variables": missing_vars,
        "total_required": len(required_vars),
        "total_missing": len(missing_vars)
    }
```

---

*Complete environment setup guide available in the main project docs.*
