#!/usr/bin/env python3
"""
Test environment variables
"""

import os

def test_env():
    """Test environment variables"""
    print("🔍 Environment Variables Test")
    print("=" * 40)
    
    # Check OpenSea API key
    opensea_key = os.getenv("OPENSEA_API_KEY")
    print(f"OPENSEA_API_KEY: {opensea_key[:8] if opensea_key else 'None'}...{opensea_key[-4:] if opensea_key else ''}")
    
    # Check other relevant vars
    print(f"APP_ENV: {os.getenv('APP_ENV', 'Not Set')}")
    print(f"PORT: {os.getenv('PORT', 'Not Set')}")
    
    # Test the exact condition from app.py
    if not opensea_key or opensea_key in ["test_key_for_now", "your_opensea_api_key", "demo"]:
        print("❌ API key check FAILED - would return mock data")
    else:
        print("✅ API key check PASSED - would return real data")
    
    # Show all environment variables
    print("\n📋 All Environment Variables:")
    for key, value in os.environ.items():
        if "OPENSEA" in key or "API" in key or "KEY" in key:
            print(f"  {key}: {value[:8]}...{value[-4:] if value else ''}")

if __name__ == "__main__":
    test_env()
