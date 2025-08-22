# 🚀 Railway Deployment Guide - Fix Domain & Static Files

## 🚨 **CURRENT ISSUES IDENTIFIED:**
1. **Domain `xsema.co.uk` not working** - DNS not configured
2. **Static files serving with wrong MIME types** - JavaScript served as HTML
3. **Manifest syntax errors** - Missing favicon files

## ✅ **FIXES IMPLEMENTED:**
1. **Enhanced static file handler** - Better MIME type detection for Railway
2. **Fixed manifest file** - Only references existing files
3. **Added CORS headers** - Better Railway compatibility

---

## 🔧 **STEP 1: DEPLOY THE FIXES TO RAILWAY**

### **Option A: Git Push (Recommended)**
```bash
# Commit the fixes
git add .
git commit -m "Fix Railway static file serving and MIME types"
git push origin main
```

### **Option B: Manual Deploy via Railway Dashboard**
1. Go to [railway.app](https://railway.app)
2. Select your XSEMA project
3. Go to **Deployments** tab
4. Click **Deploy** to trigger a new build

---

## 🌐 **STEP 2: CONFIGURE DOMAIN ON RAILWAY**

### **In Railway Dashboard:**
1. Go to your XSEMA project
2. Click **Settings** → **Domains**
3. Click **Add Domain**
4. Enter: `xsema.co.uk`
5. Railway will provide DNS instructions

### **DNS Configuration (at your domain registrar):**
```
Type: CNAME
Name: @ (or leave blank)
Value: [Your Railway app URL from dashboard]
TTL: 300
```

**Example:**
```
Type: CNAME
Name: @
Value: xsema-production.up.railway.app
TTL: 300
```

---

## 🧪 **STEP 3: TEST THE FIXES**

### **Test Static Files:**
```bash
# Test JavaScript MIME type
curl -I "https://xsema-production.up.railway.app/static/assets/index-*.js"

# Test CSS MIME type  
curl -I "https://xsema-production.up.railway.app/static/assets/index-*.css"

# Test manifest
curl -I "https://xsema-production.up.railway.app/static/site.webmanifest"
```

### **Expected Results:**
- **JavaScript**: `Content-Type: application/javascript`
- **CSS**: `Content-Type: text/css`
- **Manifest**: `Content-Type: application/manifest+json`

---

## 🚀 **STEP 4: VERIFY DOMAIN WORKS**

### **After DNS Propagation (5-10 minutes):**
1. Visit: `https://xsema.co.uk`
2. Should load without MIME type errors
3. Static files should load correctly
4. No more manifest syntax errors

---

## 🔍 **TROUBLESHOOTING**

### **If Static Files Still Don't Work:**
1. **Check Railway logs** for errors
2. **Verify file paths** in static directory
3. **Test individual files** with curl
4. **Check Railway environment** variables

### **If Domain Still Doesn't Work:**
1. **Verify DNS records** are correct
2. **Wait for propagation** (can take up to 24 hours)
3. **Check Railway domain status**
4. **Verify SSL certificate** is issued

---

## 📱 **STEP 5: TEST MOBILE COMPATIBILITY**

### **Test on Mobile Devices:**
1. **iOS Safari** - Check responsive design
2. **Android Chrome** - Verify touch interactions
3. **Mobile network** - Test loading speed
4. **PWA features** - Check manifest loading

---

## 🎯 **EXPECTED OUTCOME**

After completing these steps:
- ✅ **Domain working**: `https://xsema.co.uk` loads correctly
- ✅ **Static files**: JavaScript, CSS, images load with correct MIME types
- ✅ **No errors**: No more MIME type or manifest syntax errors
- ✅ **Mobile ready**: Responsive design works on all devices
- ✅ **PWA ready**: Manifest loads without errors

---

## 🚨 **IMMEDIATE ACTION REQUIRED**

**To fix the domain and static file issues:**

1. **Deploy the fixes** (git push or manual deploy)
2. **Configure domain** on Railway dashboard
3. **Update DNS records** at your registrar
4. **Wait for propagation** and SSL certificate
5. **Test the domain** at `https://xsema.co.uk`

**This should resolve both the domain access and the MIME type errors!** 🎯
