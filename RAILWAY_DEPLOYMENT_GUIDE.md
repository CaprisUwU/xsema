# 🚀 XSEMA Railway Deployment Guide

## 📋 **Overview**
This guide will help you deploy XSEMA to Railway and connect it to your `xsema.co.uk` domain.

## 🎯 **What You'll Get**
- **Live XSEMA API** on Railway
- **Professional hosting** with SSL
- **Custom domain** support
- **Automatic scaling** when needed
- **Cost**: $5/month (30 days free)

---

## 📅 **Step 1: GitHub Repository Setup (Completed)**

✅ **Repository created** with Python .gitignore
✅ **Public visibility** enabled
✅ **README and license** added

---

## 📅 **Step 2: Connect Local XSEMA to GitHub**

### **🔍 Check Git Status**
```bash
# In your XSEMA folder
git status
```

### **🔗 Add GitHub Remote**
Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual details:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
```

---

## 📅 **Step 3: Deploy to Railway**

### **🚀 Run Deployment Script**
```bash
# Use the automated script
.\deploy-railway.ps1
```

### **📤 Manual Deployment (Alternative)**
```bash
# Add Railway configuration files
git add railway.json railway.toml

# Commit and push
git commit -m "Add Railway deployment configuration"
git push origin main
```

---

## 📅 **Step 4: Railway Dashboard Setup**

### **🌐 Access Railway**
1. **Go to**: [railway.app](https://railway.app)
2. **Login** with your account
3. **Click** "New Project"

### **🔗 Connect GitHub Repository**
1. **Select** "Deploy from GitHub repo"
2. **Search** for your XSEMA repository
3. **Click** on your repository
4. **Deploy** XSEMA

---

## 📅 **Step 5: Railway Configuration**

### **⚙️ Automatic Configuration**
Railway will automatically detect:
- **Python application**
- **Start command** from `railway.json`
- **Health check** endpoint
- **Port configuration**

### **🔧 Manual Override (if needed)**
- **Build Command**: Leave empty (auto-detected)
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`

---

## 📅 **Step 6: Verify Deployment**

### **✅ Check Deployment Status**
1. **Monitor** build logs in Railway
2. **Wait** for deployment to complete (2-5 minutes)
3. **Copy** the generated URL

### **🧪 Test Your Deployment**
1. **Visit** the Railway URL
2. **Test** `/health` endpoint
3. **Verify** API documentation at `/docs`

---

## 📅 **Step 7: Connect Custom Domain**

### **🌐 Domain Configuration**
1. **Go to** Railway project settings
2. **Click** "Domains"
3. **Add** `xsema.co.uk`
4. **Configure** DNS records

### **🔧 DNS Records (123-REG)**
```
Type: CNAME
Name: @
Value: [YOUR_RAILWAY_URL].up.railway.app
TTL: 300

Type: CNAME
Name: www
Value: xsema.co.uk
TTL: 300
```

---

## 🚨 **Troubleshooting**

### **Build Errors**
- **Check** Python version compatibility
- **Verify** `requirements.txt` exists
- **Ensure** `main.py` is in root directory

### **Deployment Issues**
- **Check** Railway build logs
- **Verify** GitHub repository access
- **Ensure** repository is public

### **Domain Issues**
- **Wait** 24-48 hours for DNS propagation
- **Verify** CNAME records are correct
- **Check** Railway domain settings

---

## 🎯 **Next Steps After Deployment**

### **✅ Week 1**
1. **Test** all API endpoints
2. **Monitor** performance metrics
3. **Set up** monitoring and alerts

### **✅ Week 2**
1. **Connect** `xsema.co.uk` domain
2. **Configure** SSL certificate
3. **Set up** business email

### **✅ Week 3**
1. **Launch** marketing campaign
2. **Onboard** first customers
3. **Collect** user feedback

---

## 📞 **Support**

### **🚨 Emergency Issues**
- **Railway Status**: [status.railway.app](https://status.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)

### **📚 Documentation**
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **XSEMA Docs**: `/docs` endpoint on your deployment

---

## 🎉 **Congratulations!**

You now have XSEMA running on Railway with:
- ✅ **Professional hosting**
- ✅ **Automatic scaling**
- ✅ **SSL certificates**
- ✅ **Custom domain support**
- ✅ **Production-ready infrastructure**

**XSEMA is now live and ready for customers!** 🚀
