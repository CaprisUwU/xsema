# 🚀 XSEMA Heroku Deployment Guide

## 📋 **Overview**
This guide will help you deploy XSEMA to Heroku and connect it to your `xsema.co.uk` domain.

## 🎯 **What You'll Get**
- **Live XSEMA API** on Heroku
- **Professional hosting** with SSL
- **Custom domain** support
- **Automatic scaling** when needed
- **Cost**: £5/month for basic dyno

---

## 📅 **Step 1: Heroku Account Setup (Today)**

### **🆔 Create Heroku Account**
1. **Go to**: [heroku.com](https://heroku.com)
2. **Click** "Sign up"
3. **Enter** your email and create password
4. **Verify** your email address

### **💳 Add Payment Method**
- **Required** for custom domains
- **Cost**: £5/month for basic dyno
- **Free tier**: No longer available

---

## 📅 **Step 2: Install Heroku CLI (Today)**

### **🖥️ Windows Installation**
```powershell
# Option 1: Using winget
winget install --id=Heroku.HerokuCLI

# Option 2: Manual download
# Visit: https://devcenter.heroku.com/articles/heroku-cli
```

### **🔐 Login to Heroku**
```powershell
heroku login
# This will open your browser to login
```

---

## 📅 **Step 3: Deploy XSEMA to Heroku (Today)**

### **🚀 Quick Deployment (Recommended)**
```powershell
# Run the deployment script
.\deploy-heroku.ps1
```

### **🔧 Manual Deployment**
```powershell
# Create Heroku app
heroku create xsema-nft-api

# Add Python buildpack
heroku buildpacks:add heroku/python

# Deploy
git add .
git commit -m "Deploy XSEMA to Heroku"
git push heroku main
```

---

## 📅 **Step 4: Configure Custom Domain (Next Week)**

### **🌐 Add Domain to Heroku**
```powershell
# Add your domain
heroku domains:add xsema.co.uk
heroku domains:add www.xsema.co.uk
```

### **🔧 Configure DNS in 123-REG**
```
Type: CNAME Record
Name: @ (or leave blank)
Value: [YOUR_HEROKU_APP].herokuapp.com
TTL: 300

Type: CNAME Record
Name: www
Value: xsema.co.uk
TTL: 300
```

---

## 📅 **Step 5: SSL Certificate (Automatic)**

### **🔒 Heroku SSL**
- **Automatic**: SSL certificates included
- **HTTPS**: Your site will be secure
- **No configuration**: Required for custom domains

---

## 🎯 **Expected Results**

### **✅ After Deployment**
- **XSEMA API**: Live on Heroku
- **URL**: https://xsema-nft-api.herokuapp.com
- **Status**: Professional hosting with SSL

### **✅ After Domain Setup**
- **Custom Domain**: https://xsema.co.uk
- **Professional**: Business-grade hosting
- **Scalable**: Easy to upgrade when needed

---

## 🔧 **Troubleshooting**

### **❌ Common Issues**

#### **1. Heroku CLI Not Found**
```powershell
# Reinstall Heroku CLI
winget install --id=Heroku.HerokuCLI
```

#### **2. Login Failed**
```powershell
# Clear and re-login
heroku logout
heroku login
```

#### **3. Build Failed**
```powershell
# Check logs
heroku logs --tail

# Check buildpacks
heroku buildpacks
```

---

## 📊 **Cost Breakdown**

### **💰 Monthly Costs**
```
Heroku Basic Dyno: £5/month
Domain (xsema.co.uk): £8/year (£0.67/month)
Total: £5.67/month
```

### **💡 Cost Optimization**
- **Start with Basic**: £5/month
- **Scale up**: When you have traffic
- **Enterprise**: When you have customers

---

## 🚀 **Next Steps After Deployment**

### **📋 Week 1**
1. **Test API** on Heroku
2. **Verify functionality**
3. **Check performance**

### **📋 Week 2**
1. **Configure domain**
2. **Set up email**
3. **Test live site**

### **📋 Week 3**
1. **Monitor performance**
2. **Optimize if needed**
3. **Plan scaling**

---

## 🎯 **Ready to Deploy?**

**Run this command to deploy XSEMA:**
```powershell
.\deploy-heroku.ps1
```

**This will:**
1. ✅ Check Heroku CLI installation
2. ✅ Verify login status
3. ✅ Create Heroku app
4. ✅ Deploy XSEMA
5. ✅ Open your live app

**Your XSEMA will be live on Heroku in minutes!** 🚀🇬🇧
