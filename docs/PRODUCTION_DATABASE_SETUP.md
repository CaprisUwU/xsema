# 🗄️ Production Database Setup Guide

**XSEMA Production Database Configuration**

## 📋 **Overview**

This guide covers setting up PostgreSQL and Redis instances for production deployment of XSEMA.

## 🐘 **PostgreSQL Setup**

### **Option 1: Railway PostgreSQL (Recommended)**

1. **Create PostgreSQL Service**
   ```bash
   # In Railway dashboard
   New Service → Database → PostgreSQL
   ```

2. **Configure Environment Variables**
   ```env
   POSTGRES_HOST=your-railway-postgres-host
   POSTGRES_PORT=5432
   POSTGRES_DB=xsema_production
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_POOL_SIZE=20
   POSTGRES_MAX_OVERFLOW=30
   ```

3. **Database Initialization**
   ```sql
   -- Connect to your PostgreSQL instance
   psql -h your-host -U your-username -d xsema_production
   
   -- Create extensions
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   CREATE EXTENSION IF NOT EXISTS "pgcrypto";
   
   -- Verify connection
   SELECT version();
   ```

### **Option 2: AWS RDS PostgreSQL**

1. **Create RDS Instance**
   - Engine: PostgreSQL 15+
   - Instance: db.t3.micro (dev) / db.t3.small (prod)
   - Storage: 20GB+ with auto-scaling
   - Multi-AZ: Enabled for production

2. **Security Group Configuration**
   ```bash
   # Allow connections from your application
   Type: PostgreSQL
   Protocol: TCP
   Port: 5432
   Source: Your application security group
   ```

3. **Environment Variables**
   ```env
   POSTGRES_HOST=your-rds-endpoint.region.rds.amazonaws.com
   POSTGRES_PORT=5432
   POSTGRES_DB=xsema_production
   POSTGRES_USER=admin
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_SSL=true
   ```

### **Option 3: DigitalOcean Managed Database**

1. **Create Database Cluster**
   - Engine: PostgreSQL 15+
   - Node Count: 1 (dev) / 3 (prod)
   - Size: Basic (dev) / Professional (prod)

2. **Configure Firewall**
   ```bash
   # Allow connections from your droplets
   ufw allow from your-app-ip to any port 5432
   ```

3. **Environment Variables**
   ```env
   POSTGRES_HOST=your-do-db-host
   POSTGRES_PORT=25060
   POSTGRES_DB=xsema_production
   POSTGRES_USER=doadmin
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_SSL=true
   ```

## 🔴 **Redis Setup**

### **Option 1: Railway Redis (Recommended)**

1. **Create Redis Service**
   ```bash
   # In Railway dashboard
   New Service → Database → Redis
   ```

2. **Configure Environment Variables**
   ```env
   REDIS_HOST=your-railway-redis-host
   REDIS_PORT=6379
   REDIS_DB=0
   REDIS_PASSWORD=your_redis_password
   REDIS_SSL=false
   ```

### **Option 2: AWS ElastiCache Redis**

1. **Create ElastiCache Cluster**
   - Engine: Redis 7.0+
   - Node Type: cache.t3.micro (dev) / cache.t3.small (prod)
   - Multi-AZ: Enabled for production

2. **Security Group Configuration**
   ```bash
   # Allow connections from your application
   Type: Redis
   Protocol: TCP
   Port: 6379
   Source: Your application security group
   ```

3. **Environment Variables**
   ```env
   REDIS_HOST=your-elasticache-endpoint.region.cache.amazonaws.com
   REDIS_PORT=6379
   REDIS_DB=0
   REDIS_PASSWORD=your_auth_token
   REDIS_SSL=true
   ```

### **Option 3: DigitalOcean Managed Redis**

1. **Create Redis Database**
   - Engine: Redis 7.0+
   - Size: Basic (dev) / Professional (prod)

2. **Environment Variables**
   ```env
   REDIS_HOST=your-do-redis-host
   REDIS_PORT=25061
   REDIS_DB=0
   REDIS_PASSWORD=your_redis_password
   REDIS_SSL=true
   ```

## 🔧 **Database Schema Setup**

### **Automatic Migration (Recommended)**

1. **Enable Auto-Migration**
   ```env
   AUTO_MIGRATE=true
   SQL_ECHO=false
   ```

2. **Manual Migration (if needed)**
   ```bash
   # Run migrations
   python -c "
   from core.database import db_manager
   from core.models import create_tables
   import asyncio
   
   async def setup_db():
       await db_manager.initialize()
       # Tables will be created automatically
   
   asyncio.run(setup_db())
   "
   ```

### **Manual Schema Creation**

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    role VARCHAR(20) DEFAULT 'user',
    status VARCHAR(20) DEFAULT 'active',
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Portfolios table
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NFTs table
CREATE TABLE nfts (
    id SERIAL PRIMARY KEY,
    token_id VARCHAR(100) NOT NULL,
    contract_address VARCHAR(42) NOT NULL,
    chain_id INTEGER DEFAULT 1,
    name VARCHAR(255),
    description TEXT,
    image_url VARCHAR(500),
    external_url VARCHAR(500),
    attributes JSONB,
    nft_data JSONB,
    rarity_score FLOAT,
    floor_price FLOAT,
    last_floor_price FLOAT,
    volume_24h FLOAT,
    holders_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_nfts_contract_address ON nfts(contract_address);
CREATE INDEX idx_nfts_token_id ON nfts(token_id);
CREATE INDEX idx_nfts_floor_price ON nfts(floor_price);
```

## 🔒 **Security Configuration**

### **PostgreSQL Security**

1. **Enable SSL**
   ```env
   POSTGRES_SSL=true
   ```

2. **Connection Pooling**
   ```env
   POSTGRES_POOL_SIZE=20
   POSTGRES_MAX_OVERFLOW=30
   ```

3. **Network Security**
   ```bash
   # Only allow connections from your application
   # Configure firewall rules accordingly
   ```

### **Redis Security**

1. **Authentication**
   ```env
   REDIS_PASSWORD=your_secure_password
   ```

2. **Network Security**
   ```bash
   # Bind to localhost only if on same machine
   # Use VPN/private network for remote connections
   ```

## 📊 **Performance Optimization**

### **PostgreSQL Optimization**

1. **Connection Pooling**
   ```env
   POSTGRES_POOL_SIZE=20
   POSTGRES_MAX_OVERFLOW=30
   ```

2. **Query Optimization**
   ```sql
   -- Enable query logging for optimization
   SET log_statement = 'all';
   SET log_min_duration_statement = 1000;
   ```

3. **Indexing Strategy**
   ```sql
   -- Add indexes for frequently queried fields
   CREATE INDEX idx_nfts_floor_price_chain ON nfts(floor_price, chain_id);
   CREATE INDEX idx_portfolios_user_public ON portfolios(user_id, is_public);
   ```

### **Redis Optimization**

1. **Memory Configuration**
   ```env
   REDIS_MAX_MEMORY=256mb
   REDIS_MAX_MEMORY_POLICY=allkeys-lru
   ```

2. **Persistence**
   ```env
   REDIS_SAVE_INTERVAL=900
   REDIS_SAVE_CHANGES=1
   ```

## 🔍 **Monitoring and Health Checks**

### **Database Health Endpoint**

```python
@app.get("/db/health")
async def database_health():
    """Check database health status."""
    try:
        health_status = await db_manager.health_check()
        return {
            "status": "healthy",
            "databases": health_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

### **Connection Pool Monitoring**

```python
@app.get("/db/stats")
async def database_stats():
    """Get database statistics."""
    try:
        # Get connection pool stats
        pool_stats = {
            "postgresql": {
                "pool_size": db_manager.postgres_engine.pool.size(),
                "checked_in": db_manager.postgres_engine.pool.checkedin(),
                "checked_out": db_manager.postgres_engine.pool.checkedout(),
                "overflow": db_manager.postgres_engine.pool.overflow()
            }
        }
        
        return {
            "status": "success",
            "stats": pool_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Connection Refused**
   ```bash
   # Check if database is running
   # Verify firewall rules
   # Check connection string
   ```

2. **Authentication Failed**
   ```bash
   # Verify username/password
   # Check database permissions
   # Verify SSL configuration
   ```

3. **Connection Pool Exhausted**
   ```bash
   # Increase pool size
   # Check for connection leaks
   # Monitor connection usage
   ```

### **Debug Commands**

```bash
# Test PostgreSQL connection
psql -h your-host -U your-username -d your-database

# Test Redis connection
redis-cli -h your-host -p your-port -a your-password ping

# Check database logs
tail -f /var/log/postgresql/postgresql-*.log
```

## 📚 **Additional Resources**

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Railway Database Docs](https://docs.railway.app/databases)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)

---

*This guide ensures your XSEMA deployment has a robust, scalable database foundation.*
