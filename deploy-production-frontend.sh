#!/bin/bash

# XSEMA Frontend Production Deployment Script
# This script deploys the React frontend to production

echo "🚀 XSEMA Frontend Production Deployment"
echo "======================================"

# 1. Build the frontend
echo "📦 Building frontend..."
cd frontend
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi
echo "✅ Frontend built successfully"

# 2. Copy built files to backend static directory
echo "📁 Copying built files to backend..."
cd ..
mkdir -p static
cp -r frontend/dist/* static/
echo "✅ Static files copied to backend"

# 3. Update backend configuration for production
echo "⚙️  Updating backend configuration..."
cat > config/production.env << EOF
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8001
WORKERS=4

# Database Configuration
DATABASE_URL=your_production_database_url
REDIS_URL=your_production_redis_url

# API Keys (Configure these in production)
OPENSEA_API_KEY=your_opensea_api_key
OPENSEA_API_URL=https://api.opensea.io/api/v1

# Security
SECRET_KEY=your_production_secret_key
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
EOF

echo "✅ Production configuration created"

# 4. Create production startup script
echo "📝 Creating production startup script..."
cat > start-production.py << EOF
#!/usr/bin/env python3
"""
XSEMA Production Server Startup Script
"""

import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        workers=4,
        log_level="info",
        access_log=True
    )
EOF

echo "✅ Production startup script created"

# 5. Create systemd service file
echo "🔧 Creating systemd service file..."
cat > xsema.service << EOF
[Unit]
Description=XSEMA NFT Analytics Platform
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python start-production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service file created"

# 6. Create nginx configuration
echo "🌐 Creating nginx configuration..."
cat > nginx-xsema.conf << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Frontend static files
    location / {
        root /var/www/xsema/static;
        try_files \$uri \$uri/ /index.html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
    }
    
    # OpenAPI docs
    location /docs {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
    }
}
EOF

echo "✅ Nginx configuration created"

# 7. Create deployment instructions
echo "📋 Creating deployment instructions..."
cat > PRODUCTION_DEPLOYMENT_INSTRUCTIONS.md << EOF
# XSEMA Production Deployment Instructions

## 🚀 Deployment Steps

### 1. Server Setup
- Ubuntu 20.04+ or CentOS 8+
- 4GB RAM minimum, 8GB recommended
- 50GB storage minimum

### 2. Install Dependencies
\`\`\`bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Node.js, Nginx
sudo apt install python3.9 python3.9-venv python3.9-dev nginx nodejs npm -y

# Install Redis (optional, for caching)
sudo apt install redis-server -y
\`\`\`

### 3. Deploy Application
\`\`\`bash
# Clone repository
git clone https://github.com/yourusername/xsema.git
cd xsema

# Run deployment script
chmod +x deploy-production-frontend.sh
./deploy-production-frontend.sh

# Set up virtual environment
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

### 4. Configure Domain & SSL
\`\`\`bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test SSL renewal
sudo certbot renew --dry-run
\`\`\`

### 5. Start Services
\`\`\`bash
# Copy nginx config
sudo cp nginx-xsema.conf /etc/nginx/sites-available/xsema
sudo ln -s /etc/nginx/sites-available/xsema /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Start XSEMA service
sudo cp xsema.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable xsema
sudo systemctl start xsema

# Check status
sudo systemctl status xsema
\`\`\`

### 6. Verify Deployment
- Frontend: https://yourdomain.com
- API: https://yourdomain.com/api/v1
- Docs: https://yourdomain.com/docs
- Health: https://yourdomain.com/health

## 🔧 Configuration

### Environment Variables
Update \`config/production.env\` with your production values:
- Database URLs
- API keys
- Secret keys
- Domain names

### Nginx Configuration
Update \`nginx-xsema.conf\` with your domain name.

## 📊 Monitoring

### Logs
\`\`\`bash
# Application logs
sudo journalctl -u xsema -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
\`\`\`

### Health Checks
- Application: \`curl https://yourdomain.com/health\`
- API: \`curl https://yourdomain.com/api/v1/portfolio/health\`

## 🚨 Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure port 8001 is free
2. **Permission errors**: Check file ownership and permissions
3. **SSL issues**: Verify domain DNS and certificate validity
4. **Database connection**: Check database URL and credentials

### Support
- Check logs: \`sudo journalctl -u xsema -f\`
- Restart service: \`sudo systemctl restart xsema\`
- Check nginx: \`sudo nginx -t\`
EOF

echo "✅ Deployment instructions created"

echo ""
echo "🎉 XSEMA Frontend Production Deployment Complete!"
echo ""
echo "📁 Files created:"
echo "  - static/ (frontend build files)"
echo "  - config/production.env (production config)"
echo "  - start-production.py (production server)"
echo "  - xsema.service (systemd service)"
echo "  - nginx-xsema.conf (nginx config)"
echo "  - PRODUCTION_DEPLOYMENT_INSTRUCTIONS.md (deployment guide)"
echo ""
echo "🚀 Next steps:"
echo "  1. Update domain names in nginx-xsema.conf"
echo "  2. Configure production environment variables"
echo "  3. Deploy to your production server"
echo "  4. Set up SSL certificates with Let's Encrypt"
echo "  5. Start the production services"
echo ""
echo "📖 See PRODUCTION_DEPLOYMENT_INSTRUCTIONS.md for detailed steps"
