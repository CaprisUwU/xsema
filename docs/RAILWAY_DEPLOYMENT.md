# Railway Deployment Guide for XSEMA

**Complete guide to deploy XSEMA on Railway.app**

## 🚀 **Quick Deploy**

### **1. Automatic Deployment**
- Push to `main` branch
- Railway automatically detects changes
- Builds and deploys automatically

### **2. Manual Deployment**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link project
railway link

# Deploy
railway up
```

## 📋 **Prerequisites**

### **Required Environment Variables**
```bash
# Core settings
PORT=8080  # Railway will override this
SECRET_KEY=your-secret-key-here

# Optional: Custom domain
CUSTOM_DOMAIN=xsema.co.uk
```

### **Required Files**
- ✅ `railway.json` - Railway configuration
- ✅ `railway_start.py` - Startup script
- ✅ `requirements.txt` - Python dependencies
- ✅ `app.py` - Main FastAPI application

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. ModuleNotFoundError: No module named 'pydantic_settings'**
**Solution**: Ensure `requirements.txt` includes:
```txt
pydantic==2.5.0
pydantic-settings==2.1.0
```

#### **2. Import Errors in core/__init__.py**
**Solution**: Check that all imported modules exist:
```python
# Only import from existing files
from .cache import cache
from .config import settings
# from .security.authentication import validate_api_key  # Comment out if file doesn't exist
```

#### **3. Port Configuration Issues**
**Solution**: Railway automatically sets `PORT` environment variable:
```python
# In railway_start.py
port = int(os.environ.get("PORT", "8000"))
```

### **Debugging Steps**

1. **Check Railway Logs**
   - Go to Railway dashboard
   - Click on your service
   - View deployment logs

2. **Verify Dependencies**
   - Ensure `requirements.txt` is up to date
   - Check for version conflicts

3. **Test Locally First**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

## 📊 **Deployment Status**

### **Current Status**: ✅ **Working**
- **Last Deployment**: August 24, 2025
- **Status**: Successfully deployed
- **Port**: 8080 (Railway assigned)
- **Domain**: xsema.co.uk

### **Recent Fixes Applied**
- ✅ Added missing `pydantic-settings` dependency
- ✅ Fixed import errors in `core/__init__.py`
- ✅ Updated requirements files
- ✅ Standardized port configuration

## 🔄 **Continuous Deployment**

### **Automatic Triggers**
- **Push to main**: Triggers automatic deployment
- **Pull Request**: Can be configured for staging deployment

### **Manual Triggers**
- Railway dashboard: Manual deploy button
- Railway CLI: `railway up` command

## 📝 **Best Practices**

1. **Always test locally** before pushing
2. **Keep requirements.txt updated** with exact versions
3. **Use environment variables** for configuration
4. **Monitor deployment logs** for errors
5. **Have a rollback plan** ready

## 🆘 **Support**

If deployment fails:
1. Check Railway logs
2. Verify all dependencies are in `requirements.txt`
3. Test locally with same Python version
4. Check for import errors in core modules
