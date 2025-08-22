#!/usr/bin/env python3
"""
Test script to verify static file serving with correct MIME types.
This helps diagnose Railway deployment issues.
"""

import os
import mimetypes
import requests
from pathlib import Path

def test_local_static_files():
    """Test static files locally to ensure they exist and have correct extensions."""
    print("🔍 Testing local static files...")
    
    static_dir = Path("static")
    if not static_dir.exists():
        print("❌ Static directory not found!")
        return False
    
    # Test key files
    test_files = [
        "site.webmanifest",
        "assets/index-58eed827.js",
        "assets/index-4f13db28.css",
        "xsema-icon.svg",
        "index.html"
    ]
    
    for file_path in test_files:
        full_path = static_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} - NOT FOUND")
    
    return True

def test_railway_static_files():
    """Test static files on Railway to check MIME types."""
    print("\n🌐 Testing Railway static files...")
    
    base_url = "https://xsema-production.up.railway.app"
    test_files = [
        "/static/site.webmanifest",
        "/static/assets/index-58eed827.js",
        "/static/assets/index-4f13db28.css",
        "/static/xsema-icon.svg"
    ]
    
    for file_path in test_files:
        url = base_url + file_path
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', 'Unknown')
                print(f"✅ {file_path}")
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {content_type}")
                
                # Check if MIME type is correct
                if file_path.endswith('.js'):
                    if 'javascript' in content_type:
                        print("   ✅ JavaScript MIME type correct")
                    else:
                        print(f"   ❌ JavaScript MIME type wrong: {content_type}")
                elif file_path.endswith('.css'):
                    if 'css' in content_type:
                        print("   ✅ CSS MIME type correct")
                    else:
                        print(f"   ❌ CSS MIME type wrong: {content_type}")
                elif file_path.endswith('.webmanifest'):
                    if 'manifest' in content_type:
                        print("   ✅ Manifest MIME type correct")
                    else:
                        print(f"   ❌ Manifest MIME type wrong: {content_type}")
                elif file_path.endswith('.svg'):
                    if 'svg' in content_type:
                        print("   ✅ SVG MIME type correct")
                    else:
                        print(f"   ❌ SVG MIME type wrong: {content_type}")
            else:
                print(f"❌ {file_path} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {file_path} - Error: {e}")
    
    return True

def test_railway_main_page():
    """Test the main page on Railway."""
    print("\n🏠 Testing Railway main page...")
    
    url = "https://xsema-production.up.railway.app/"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Main page loads - Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            
            # Check if it's HTML
            if 'html' in response.headers.get('Content-Type', '').lower():
                print("   ✅ Main page served as HTML")
            else:
                print("   ❌ Main page not served as HTML")
        else:
            print(f"❌ Main page error - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Main page error: {e}")

def main():
    """Main test function."""
    print("🚀 XSEMA Static File Test Suite")
    print("=" * 50)
    
    # Test local files
    test_local_static_files()
    
    # Test Railway deployment
    test_railway_static_files()
    
    # Test main page
    test_railway_main_page()
    
    print("\n" + "=" * 50)
    print("✅ Testing complete!")

if __name__ == "__main__":
    main()
