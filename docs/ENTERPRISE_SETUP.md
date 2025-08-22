# XSEMA Enterprise Setup Guide

## 🏢 **Enterprise Authentication & Management**

This guide covers setting up XSEMA for enterprise customers with advanced authentication, user management, and compliance features.

---

## 📋 **Table of Contents**

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [User Management](#user-management)
6. [Authentication Setup](#authentication-setup)
7. [Security & Compliance](#security--compliance)
8. [Troubleshooting](#troubleshooting)

---

## 🌟 **Overview**

XSEMA Enterprise provides:
- **Single Sign-On (SSO)** with SAML 2.0 and OAuth 2.0
- **LDAP/Active Directory** integration
- **Multi-Factor Authentication (MFA)**
- **Role-Based Access Control (RBAC)**
- **Audit logging** for compliance
- **Portfolio management** with enterprise features

---

## ✅ **Prerequisites**

### **System Requirements**
- Python 3.8+
- PostgreSQL 12+ (recommended) or SQLite
- Redis (for caching and sessions)
- 4GB+ RAM
- 10GB+ storage

### **Dependencies**
```bash
pip install sqlalchemy bcrypt PyJWT python-multipart
```

---

## 🚀 **Installation**

### **1. Clone Repository**
```bash
git clone https://github.com/your-org/xsema.git
cd xsema
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Environment Configuration**
Create `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/xsema
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Security
SECRET_KEY=your-super-secret-key-here
API_KEY_REQUIRED=true

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your-redis-password

# Enterprise Features
ENABLE_SAML=true
ENABLE_OAUTH=true
ENABLE_LDAP=true
ENABLE_MFA=true
```

---

## ⚙️ **Configuration**

### **Database Setup**

#### **PostgreSQL (Recommended)**
```sql
CREATE DATABASE xsema;
CREATE USER xsema_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE xsema TO xsema_user;
```

#### **SQLite (Development)**
```bash
# Database will be created automatically
# File: ./xsema.db
```

### **Redis Configuration**
```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf

# Set password
requirepass your-redis-password

# Restart Redis
sudo systemctl restart redis
```

---

## 👥 **User Management**

### **User Roles & Permissions**

| Role | Permissions | Description |
|------|-------------|-------------|
| **Viewer** | `read_portfolio`, `read_market_data` | Read-only access |
| **User** | `read_portfolio`, `write_portfolio`, `read_market_data` | Basic portfolio management |
| **Analyst** | User + `read_reports`, `write_reports` | Analysis and reporting |
| **Manager** | Analyst + `manage_users` | Team management |
| **Admin** | Manager + `admin_settings` | System administration |
| **Super Admin** | `*` | Full access |

### **Creating Users**

#### **Via API**
```bash
curl -X POST "http://localhost:8001/api/v1/enterprise/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "username": "john.doe",
    "email": "john.doe@company.com",
    "full_name": "John Doe",
    "role": "analyst",
    "organization_id": "org_123"
  }'
```

#### **Via Python Script**
```python
from core.storage.enterprise_service import enterprise_service
from core.enterprise_auth import UserRole, AuthProvider

# Create user
user = enterprise_service.create_user(
    username="john.doe",
    email="john.doe@company.com",
    full_name="John Doe",
    role=UserRole.ANALYST,
    auth_provider=AuthProvider.SAML
)
```

---

## 🔐 **Authentication Setup**

### **SAML 2.0 Configuration**

#### **1. Identity Provider Setup**
Configure your IdP (Okta, Azure AD, etc.):

**Service Provider (XSEMA) Details:**
- Entity ID: `https://your-domain.com/saml/metadata`
- ACS URL: `https://your-domain.com/saml/acs`
- Single Logout URL: `https://your-domain.com/saml/logout`

#### **2. XSEMA SAML Configuration**
```bash
curl -X POST "http://localhost:8001/api/v1/saml/configure" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "idp_entity_id": "https://your-idp.com",
    "idp_sso_url": "https://your-idp.com/sso",
    "idp_slo_url": "https://your-idp.com/slo",
    "idp_x509_cert": "-----BEGIN CERTIFICATE-----...",
    "sp_entity_id": "https://your-domain.com/saml/metadata",
    "acs_url": "https://your-domain.com/saml/acs",
    "slo_url": "https://your-domain.com/saml/logout"
  }'
```

### **OAuth 2.0 Configuration**

#### **1. OAuth Provider Setup**
Configure your OAuth provider (Google, Microsoft, etc.):

**Redirect URIs:**
- `https://your-domain.com/oauth/callback`

#### **2. XSEMA OAuth Configuration**
```bash
curl -X POST "http://localhost:8001/api/v1/oauth/clients" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "client_name": "Company OAuth Client",
    "redirect_uris": ["https://your-domain.com/oauth/callback"],
    "scopes": ["openid", "profile", "email"],
    "grant_types": ["authorization_code", "refresh_token"]
  }'
```

### **LDAP/Active Directory Integration**

#### **1. LDAP Configuration**
```bash
curl -X POST "http://localhost:8001/api/v1/enterprise/ldap/configure" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "ldap_server": "ldap://your-ldap-server.com:389",
    "ldap_base_dn": "DC=company,DC=com",
    "ldap_bind_dn": "CN=service_account,OU=ServiceAccounts,DC=company,DC=com",
    "ldap_bind_password": "secure_password",
    "user_search_base": "OU=Users,DC=company,DC=com",
    "user_search_filter": "(sAMAccountName={username})",
    "group_search_base": "OU=Groups,DC=company,DC=com",
    "group_search_filter": "(member={user_dn})"
  }'
```

#### **2. LDAP User Mapping**
```python
# LDAP attributes to XSEMA user mapping
ldap_mapping = {
    "username": "sAMAccountName",
    "email": "mail",
    "full_name": "displayName",
    "department": "department",
    "manager": "manager"
}
```

---

## 🔒 **Security & Compliance**

### **Multi-Factor Authentication (MFA)**

#### **Enable MFA for User**
```python
from core.storage.enterprise_service import enterprise_service

# Enable MFA
user = enterprise_service.enable_mfa(user_id, mfa_secret)

# Verify MFA token
is_valid = enterprise_service.verify_mfa_token(user_id, token)
```

#### **MFA Setup Flow**
1. User requests MFA setup
2. System generates TOTP secret
3. User scans QR code with authenticator app
4. User verifies setup with generated token
5. MFA is enabled for the account

### **Audit Logging**

#### **View Audit Logs**
```bash
# Get user audit logs
curl "http://localhost:8001/api/v1/enterprise/audit/logs?user_id=user_123" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Get system audit logs
curl "http://localhost:8001/api/v1/enterprise/audit/logs?action=user_created" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### **Audit Events Tracked**
- User creation, modification, deletion
- Login/logout events
- Portfolio changes
- Security alerts
- Administrative actions
- API access

### **Rate Limiting**

#### **Configure Rate Limits**
```env
# Rate limiting settings
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100  # requests per minute
RATE_LIMIT_BATCH=10     # batch operations per minute
RATE_LIMIT_AUTH=5       # authentication attempts per minute
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Errors**
```bash
# Check database status
python -c "from core.storage.database import engine; print(engine.execute('SELECT 1').scalar())"

# Verify environment variables
echo $DATABASE_URL
```

#### **2. SAML Configuration Issues**
```bash
# Test SAML metadata
curl "http://localhost:8001/saml/metadata"

# Check SAML status
curl "http://localhost:8001/api/v1/saml/status"
```

#### **3. OAuth Issues**
```bash
# Test OAuth discovery
curl "http://localhost:8001/.well-known/oauth-authorization-server"

# Check OAuth client status
curl "http://localhost:8001/api/v1/oauth/clients"
```

#### **4. LDAP Connection Issues**
```bash
# Test LDAP connection
python -c "from core.enterprise_auth import test_ldap_connection; test_ldap_connection()"

# Check LDAP logs
tail -f logs/xsema.log | grep LDAP
```

### **Log Files**

#### **Application Logs**
```bash
# Main application log
tail -f logs/xsema.log

# Database log
tail -f logs/database.log

# Authentication log
tail -f logs/auth.log
```

#### **System Logs**
```bash
# System service logs
sudo journalctl -u xsema -f

# Database service logs
sudo journalctl -u postgresql -f
```

---

## 📞 **Support**

### **Getting Help**
- **Documentation**: [docs.xsema.com](https://docs.xsema.com)
- **API Reference**: [api.xsema.com](https://api.xsema.com)
- **Support Email**: enterprise-support@xsema.com
- **Emergency**: +44 (0) 800 123 4567

### **Enterprise Support Tiers**

| Tier | Response Time | Features |
|------|---------------|----------|
| **Basic** | 24 hours | Email support, documentation |
| **Professional** | 8 hours | Phone support, priority tickets |
| **Enterprise** | 2 hours | Dedicated support engineer, SLA |

---

## 🎯 **Next Steps**

1. **Complete Setup**: Follow this guide to configure all components
2. **User Onboarding**: Create initial users and test authentication
3. **Security Review**: Conduct security assessment and penetration testing
4. **Go Live**: Launch XSEMA for your enterprise users
5. **Monitoring**: Set up monitoring and alerting for production

---

**XSEMA Enterprise - Secure, Scalable, Compliant** 🚀
