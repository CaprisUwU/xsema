#!/usr/bin/env python3
"""
OpenSea API Integration Test Script
Tests the connection and data fetching from OpenSea API
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_opensea_api_connection():
    """Test basic OpenSea API connection without API key"""
    print("🔍 Testing OpenSea API Connection...")
    print("=" * 50)
    
    try:
        import aiohttp
        
        # Test basic connection (no API key required for basic endpoints)
        async with aiohttp.ClientSession() as session:
            # Test collections endpoint (limited without API key)
            url = "https://api.opensea.io/api/v2/collections?offset=0&limit=5"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            print(f"📡 Testing endpoint: {url}")
            
            async with session.get(url, headers=headers, timeout=30) as response:
                print(f"📊 Response Status: {response.status}")
                print(f"📊 Response Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success! Retrieved {len(data.get('collections', []))} collections")
                    
                    # Show first collection details
                    if data.get('collections'):
                        first_collection = data['collections'][0]
                        print(f"📋 Sample Collection: {first_collection.get('name', 'Unknown')}")
                        print(f"   Slug: {first_collection.get('slug', 'Unknown')}")
                        print(f"   Floor Price: {first_collection.get('stats', {}).get('floor_price', 'Unknown')}")
                    
                    return True
                else:
                    print(f"❌ Failed with status: {response.status}")
                    error_text = await response.text()
                    print(f"❌ Error: {error_text[:200]}...")
                    return False
                    
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def test_opensea_with_api_key():
    """Test OpenSea API with API key for full access"""
    print("\n🔑 Testing OpenSea API with API Key...")
    print("=" * 50)
    
    api_key = os.getenv("OPENSEA_API_KEY")
    
    if not api_key:
        print("⚠️ No OPENSEA_API_KEY environment variable found")
        print("   Set it with: $env:OPENSEA_API_KEY='your_api_key'")
        print("   Or add it to your .env file")
        return False
    
    if api_key == "your_opensea_api_key" or api_key == "demo":
        print("⚠️ API key appears to be placeholder/demo value")
        print("   Please set a real OpenSea API key")
        return False
    
    print(f"🔑 API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Test with API key for full access
            url = "https://api.opensea.io/api/v2/collections?offset=0&limit=10"
            headers = {
                "X-API-KEY": api_key,
                "User-Agent": "XSEMA/1.0"
            }
            
            print(f"📡 Testing authenticated endpoint: {url}")
            
            async with session.get(url, headers=headers, timeout=30) as response:
                print(f"📊 Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    collections = data.get('collections', [])
                    print(f"✅ Success! Retrieved {len(collections)} collections")
                    
                    # Show detailed collection information
                    for i, collection in enumerate(collections[:3]):
                        print(f"\n📋 Collection {i+1}: {collection.get('name', 'Unknown')}")
                        print(f"   Slug: {collection.get('slug', 'Unknown')}")
                        print(f"   Contract: {collection.get('primary_asset_contracts', [{}])[0].get('address', 'Unknown')}")
                        
                        stats = collection.get('stats', {})
                        print(f"   Floor Price: {stats.get('floor_price', 'Unknown')} ETH")
                        print(f"   24h Volume: {stats.get('one_day_volume', 'Unknown')} ETH")
                        print(f"   Total Supply: {stats.get('total_supply', 'Unknown')}")
                    
                    return True
                else:
                    print(f"❌ Failed with status: {response.status}")
                    error_text = await response.text()
                    print(f"❌ Error: {error_text[:200]}...")
                    return False
                    
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

async def test_specific_collection():
    """Test fetching data for a specific collection (BAYC)"""
    print("\n🎯 Testing Specific Collection (BAYC)...")
    print("=" * 50)
    
    api_key = os.getenv("OPENSEA_API_KEY")
    
    if not api_key or api_key in ["your_opensea_api_key", "demo"]:
        print("⚠️ Skipping specific collection test - no valid API key")
        return False
    
    try:
        import aiohttp
        
        # BAYC contract address
        contract_address = "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d"
        
        async with aiohttp.ClientSession() as session:
            # Test collection stats
            stats_url = f"https://api.opensea.io/api/v2/collections/{contract_address}/stats"
            headers = {
                "X-API-KEY": api_key,
                "User-Agent": "XSEMA/1.0"
            }
            
            print(f"📡 Testing collection stats: {stats_url}")
            
            async with session.get(stats_url, headers=headers, timeout=30) as response:
                print(f"📊 Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('stats', {})
                    
                    print(f"✅ BAYC Collection Stats:")
                    print(f"   Floor Price: {stats.get('floor_price', 'Unknown')} ETH")
                    print(f"   24h Volume: {stats.get('one_day_volume', 'Unknown')} ETH")
                    print(f"   7d Volume: {stats.get('seven_day_volume', 'Unknown')} ETH")
                    print(f"   Total Volume: {stats.get('total_volume', 'Unknown')} ETH")
                    print(f"   Total Supply: {stats.get('total_supply', 'Unknown')}")
                    print(f"   Owners: {stats.get('num_owners', 'Unknown')}")
                    
                    return True
                else:
                    print(f"❌ Failed with status: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Specific collection test failed: {e}")
        return False

async def test_market_data_integration():
    """Test the XSEMA market data integration module"""
    print("\n🚀 Testing XSEMA Market Data Integration...")
    print("=" * 50)
    
    try:
        from core.market_data_integration import test_market_data_integration
        
        print("📊 Running XSEMA market data integration test...")
        result = await test_market_data_integration()
        
        if result:
            print("✅ XSEMA market data integration test completed")
            return True
        else:
            print("❌ XSEMA market data integration test failed")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import market data integration: {e}")
        return False
    except Exception as e:
        print(f"❌ Market data integration test failed: {e}")
        return False

async def main():
    """Run all OpenSea integration tests"""
    print("🚀 XSEMA OpenSea Integration Test Suite")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Environment: {os.getenv('APP_ENV', 'development')}")
    print(f"🔑 API Key Status: {'Set' if os.getenv('OPENSEA_API_KEY') else 'Not Set'}")
    
    results = []
    
    # Test 1: Basic API connection
    print("\n" + "="*60)
    result1 = await test_opensea_api_connection()
    results.append(("Basic API Connection", result1))
    
    # Test 2: API with key
    print("\n" + "="*60)
    result2 = await test_opensea_with_api_key()
    results.append(("API with Key", result2))
    
    # Test 3: Specific collection
    print("\n" + "="*60)
    result3 = await test_specific_collection()
    results.append(("Specific Collection", result3))
    
    # Test 4: XSEMA integration
    print("\n" + "="*60)
    result4 = await test_market_data_integration()
    results.append(("XSEMA Integration", result4))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OpenSea integration is working correctly.")
    elif passed >= total - 1:
        print("⚠️ Most tests passed. Check the failed test for details.")
    else:
        print("❌ Multiple tests failed. Review the errors above.")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if not os.getenv("OPENSEA_API_KEY"):
        print("1. Set OPENSEA_API_KEY environment variable for full API access")
    if not result1:
        print("2. Check internet connection and OpenSea API availability")
    if not result4:
        print("3. Review XSEMA market data integration configuration")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
