#!/usr/bin/env python3
"""
Domain Configuration Checker for XSEMA
This script helps verify domain configuration and DNS resolution
"""

import socket
import requests
import dns.resolver
import time

def check_dns_resolution(domain):
    """Check DNS resolution for a domain."""
    print(f"🔍 Checking DNS resolution for: {domain}")
    
    try:
        # Get IP address
        ip = socket.gethostbyname(domain)
        print(f"  ✅ IP Address: {ip}")
        
        # Get all IP addresses (in case of multiple)
        try:
            answers = dns.resolver.resolve(domain, 'A')
            ips = [str(rdata) for rdata in answers]
            if len(ips) > 1:
                print(f"  📍 All IPs: {', '.join(ips)}")
        except:
            pass
            
        return ip
    except socket.gaierror as e:
        print(f"  ❌ DNS resolution failed: {e}")
        return None

def check_railway_connection(domain):
    """Check if domain can connect to Railway."""
    print(f"🔍 Checking Railway connection for: {domain}")
    
    try:
        # Try to connect to the domain
        response = requests.get(f"https://{domain}/health", timeout=10)
        print(f"  ✅ Connection successful: HTTP {response.status_code}")
        print(f"  📊 Response: {response.text[:200]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Connection failed: {e}")
        return False

def check_railway_app():
    """Check Railway app directly."""
    print("🔍 Checking Railway app directly...")
    
    try:
        response = requests.get("https://xsema-production.up.railway.app/health", timeout=10)
        print(f"  ✅ Railway app responding: HTTP {response.status_code}")
        print(f"  📊 Response: {response.text[:200]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Railway app not responding: {e}")
        return False

def main():
    """Main domain check function."""
    print("=" * 60)
    print("🌐 XSEMA DOMAIN CONFIGURATION CHECKER")
    print("=" * 60)
    
    # Check Railway app first
    railway_working = check_railway_app()
    print()
    
    # Check domain resolution
    xsema_ip = check_dns_resolution("xsema.co.uk")
    railway_ip = check_dns_resolution("xsema-production.up.railway.app")
    print()
    
    # Check domain connection
    if xsema_ip:
        domain_working = check_railway_connection("xsema.co.uk")
    else:
        domain_working = False
    print()
    
    # Summary
    print("=" * 60)
    print("📋 CONFIGURATION SUMMARY")
    print("=" * 60)
    
    if railway_working:
        print("✅ Railway app is working")
    else:
        print("❌ Railway app is not responding")
        print("   → Fix Railway deployment first")
        return
    
    if xsema_ip and railway_ip:
        if xsema_ip == railway_ip:
            print("✅ Domain pointing to correct Railway IP")
        else:
            print("❌ Domain pointing to wrong IP")
            print(f"   → xsema.co.uk: {xsema_ip}")
            print(f"   → Railway app: {railway_ip}")
            print("   → Update DNS records to point to Railway")
    
    if domain_working:
        print("✅ Domain is working and connected to Railway")
    else:
        print("❌ Domain is not working")
        if xsema_ip != railway_ip:
            print("   → Fix DNS records first")
        else:
            print("   → Check Railway domain configuration")
    
    print()
    print("🔧 NEXT STEPS:")
    if not railway_working:
        print("1. Fix Railway deployment issues")
    elif xsema_ip != railway_ip:
        print("1. Update Cloudflare DNS records")
        print("2. Point xsema.co.uk to Railway IP")
    elif not domain_working:
        print("1. Add xsema.co.uk as custom domain in Railway")
        print("2. Wait for SSL certificate provisioning")
    else:
        print("🎉 Domain is fully configured and working!")

if __name__ == "__main__":
    main()
