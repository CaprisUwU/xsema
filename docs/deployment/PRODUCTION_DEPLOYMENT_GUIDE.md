# 🚀 NFT Analytics Engine - Production Deployment Guide

**Version**: 3.0.0  
**Last Updated**: January 31, 2025  
**Deployment Time**: ~30 minutes

---

## 📋 **Prerequisites**

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Docker-compatible Linux
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Disk**: 100GB+ SSD storage
- **Network**: Stable internet connection, ports 80, 443, 8001 available

### Required Software
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### External Services Setup
1. **Blockchain RPC Endpoints**:
   - Ethereum: Alchemy, Infura, or QuickNode
   - Polygon: Alchemy or QuickNode
   - BSC: Official RPC or third-party

2. **API Keys Required**:
   - Alchemy API key
   - OpenSea API key (optional)
   - Moralis API key (optional)

---

## ⚡ **Quick Production Deployment**

### 1. Clone and Setup
```bash
# Clone repository
git clone https://github.com/yourusername/nft-analytics-engine.git
cd nft-analytics-engine

# Create environment file
cp config/production.env .env
```

### 2. Configure Environment
Edit `.env` with your production values:
```bash
# Required: Set secure secret key
export SECRET_KEY=$(openssl rand -hex 32)

# Required: Set database password
export POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Required: Add your blockchain RPC URLs
export ETHEREUM_RPC_URL="https://eth-mainnet.alchemyapi.io/v2/YOUR_KEY"
export ALCHEMY_API_KEY="your_alchemy_key_here"

# Optional: External API keys
export OPENSEA_API_KEY="your_opensea_key"
export MORALIS_API_KEY="your_moralis_key"
```

### 3. Deploy with One Command
```bash
# Make deployment script executable
chmod +x scripts/deploy/production_deploy.sh

# Deploy!
./scripts/deploy/production_deploy.sh
```

### 4. Verify Deployment
```bash
# Check all services are running
docker-compose ps

# Test API health
curl http://localhost:8001/health

# View logs
docker-compose logs -f nft-engine
```

---

## 🔧 **Detailed Setup Guide**

### Step 1: Environment Configuration

Create production environment file:
```bash
# Copy template
cp config/production.env .env

# Generate secure secrets
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env
```

**Critical Environment Variables:**
```bash
# Security (REQUIRED)
SECRET_KEY=your-super-secure-secret-key
POSTGRES_PASSWORD=your-postgres-password

# Blockchain RPC URLs (REQUIRED)
ETHEREUM_RPC_URL=https://eth-mainnet.alchemyapi.io/v2/YOUR_KEY
POLYGON_RPC_URL=https://polygon-mainnet.alchemyapi.io/v2/YOUR_KEY
BSC_RPC_URL=https://bsc-dataseed1.binance.org/

# API Keys (REQUIRED for full functionality)
ALCHEMY_API_KEY=your_alchemy_key
OPENSEA_API_KEY=your_opensea_key
MORALIS_API_KEY=your_moralis_key

# Application Settings
ENVIRONMENT=production
DEBUG=false
WORKERS=4
```

### Step 2: SSL/TLS Setup (Production)

#### Option A: Let's Encrypt (Recommended)
```bash
# Install certbot
sudo apt install certbot

# Generate SSL certificate
sudo certbot certonly --standalone -d api.yourdomain.com

# Update nginx configuration
cp nginx/nginx.conf.ssl nginx/nginx.conf
```

#### Option B: Custom SSL Certificate
```bash
# Place your SSL files
mkdir -p nginx/ssl
cp your-certificate.crt nginx/ssl/
cp your-private-key.key nginx/ssl/
```

### Step 3: Database Initialization
```bash
# Create init script
cat > scripts/init.sql << EOF
-- Create database and user
CREATE DATABASE nft_analytics;
CREATE USER nft_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nft_analytics TO nft_user;

-- Create extensions
\c nft_analytics;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
EOF
```

### Step 4: Deploy Services
```bash
# Build and start all services
docker-compose --env-file .env up -d

# Check service status
docker-compose ps

# Expected output:
# nft-engine    Up (healthy)
# postgres      Up (healthy)
# redis         Up (healthy)
# nginx         Up
```

### Step 5: Health Verification
```bash
# Run comprehensive health check
./scripts/monitoring/health_check.sh

# Test API endpoints
curl -f http://localhost:8001/health
curl -f http://localhost:8001/api/v1/nfts
curl -f http://localhost:8001/docs  # API documentation
```

---

## 🔍 **Monitoring & Maintenance**

### Health Monitoring
```bash
# Set up automated health checks (cron)
echo "*/5 * * * * /path/to/nft-engine/scripts/monitoring/health_check.sh" | crontab -

# View real-time logs
docker-compose logs -f nft-engine

# Monitor resource usage
docker stats
```

### Backup Strategy
```bash
# Database backup (daily)
docker-compose exec postgres pg_dump -U nft_user nft_analytics > backup_$(date +%Y%m%d).sql

# Volume backup
docker run --rm -v nft-analytics-engine_postgres_data:/source -v $(pwd)/backups:/backup alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz -C /source .
```

### Log Management
```bash
# Rotate logs
docker-compose exec nft-engine logrotate /etc/logrotate.conf

# View application logs
docker-compose logs nft-engine --tail=100 -f

# Monitor error logs
docker-compose logs nft-engine | grep ERROR
```

---

## 🔒 **Security Hardening**

### Firewall Configuration
```bash
# UFW setup
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8001/tcp  # Block direct API access
sudo ufw enable
```

### Docker Security
```bash
# Run containers as non-root user (already configured in Dockerfile)
# Limit container resources
docker-compose up -d --scale nft-engine=2 --memory=2g --cpus=2
```

### API Security
```bash
# Enable rate limiting (configured in .env)
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=10

# Enable CORS protection
CORS_ORIGINS=["https://yourdomain.com"]
```

---

## 🚀 **Scaling & Performance**

### Horizontal Scaling
```bash
# Scale API instances
docker-compose up -d --scale nft-engine=3

# Load balancing with nginx
# (nginx configuration automatically handles multiple instances)
```

### Database Optimization
```bash
# PostgreSQL tuning
docker-compose exec postgres psql -U nft_user -d nft_analytics

-- Optimize for NFT data
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
```

### Redis Optimization
```bash
# Redis configuration for caching
echo "maxmemory 512mb" >> redis.conf
echo "maxmemory-policy allkeys-lru" >> redis.conf
```

---

## 🔧 **Troubleshooting**

### Common Issues

#### Issue: Container fails to start
```bash
# Check logs
docker-compose logs nft-engine

# Common solutions:
1. Check environment variables are set
2. Verify ports are not in use: netstat -tulpn | grep 8001
3. Check disk space: df -h
```

#### Issue: Database connection failed
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U nft_user -d nft_analytics -c "SELECT 1;"
```

#### Issue: API returns 500 errors
```bash
# Check application logs
docker-compose logs nft-engine --tail=50

# Verify all required environment variables
docker-compose exec nft-engine printenv | grep -E "(SECRET_KEY|DATABASE_URL|REDIS_URL)"
```

### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check API response times
curl -w "@curl-format.txt" -o /dev/null http://localhost:8001/health

# Database query analysis
docker-compose exec postgres psql -U nft_user -d nft_analytics -c "SELECT * FROM pg_stat_activity;"
```

---

## 📋 **Deployment Checklist**

### Pre-Deployment ✓
- [ ] Server meets minimum requirements
- [ ] Docker and Docker Compose installed
- [ ] Domain name configured (for SSL)
- [ ] Blockchain RPC endpoints ready
- [ ] API keys obtained
- [ ] Environment variables configured
- [ ] SSL certificates ready

### Deployment ✓
- [ ] Code deployed from latest release
- [ ] Environment file configured
- [ ] Database initialized
- [ ] All services started successfully
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] WebSocket connections working

### Post-Deployment ✓
- [ ] SSL/TLS working
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Security hardening applied
- [ ] Performance baseline established
- [ ] Documentation updated

---

## 🆘 **Support & Emergency Contacts**

### Emergency Procedures
```bash
# Immediate rollback
docker-compose down
docker-compose up -d --scale nft-engine=1

# Emergency stop
docker-compose down --remove-orphans

# Restore from backup
./scripts/restore_backup.sh backup_20250131.sql
```

### Getting Help
- **Documentation**: [docs.yourproject.com](https://docs.yourproject.com)
- **Discord**: [discord.gg/yourproject](https://discord.gg/yourproject)
- **Emergency Email**: emergency@yourproject.com
- **Status Page**: [status.yourproject.com](https://status.yourproject.com)

---

## 🎯 **Success Metrics**

After successful deployment, you should see:
- ✅ **Uptime**: 99.9%+
- ✅ **Response Time**: <200ms average
- ✅ **Memory Usage**: <70% of allocated
- ✅ **CPU Usage**: <50% under normal load
- ✅ **Error Rate**: <1%

---

*Deployment Guide v3.0.0 - Production Ready* 🚀

*Your NFT Analytics Engine is now ready to analyze the blockchain!*
