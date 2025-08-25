#!/usr/bin/env python3
"""
Test OpenSea Collections
"""

import asyncio
import aiohttp
import os
import json

async def test_collections():
    """Test what collections are available from OpenSea"""
    api_key = os.getenv("OPENSEA_API_KEY")
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:] if api_key else 'None'}")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    async with aiohttp.ClientSession() as session:
        headers = {"X-API-KEY": api_key}
        
        # Test collections endpoint
        url = "https://api.opensea.io/api/v2/collections?offset=0&limit=3"
        print(f"📡 Testing: {url}")
        
        try:
            async with session.get(url, headers=headers) as response:
                print(f"📊 Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    collections = data.get('collections', [])
                    print(f"✅ Found {len(collections)} collections")
                    
                    # Show first collection in detail
                    if collections:
                        first = collections[0]
                        print(f"\n📋 First Collection Structure:")
                        print(json.dumps(first, indent=2))
                        
                        # Try to get stats for this collection
                        if 'collection' in first and first['collection']:
                            print(f"\n📊 Testing stats for: {first['collection']}")
                            stats_url = f"https://api.opensea.io/api/v2/collections/{first['collection']}/stats"
                            async with session.get(stats_url, headers=headers) as stats_resp:
                                print(f"Stats Status: {stats_resp.status}")
                                if stats_resp.status == 200:
                                    stats_data = await stats_resp.json()
                                    print("Stats:", json.dumps(stats_data, indent=2))
                                else:
                                    print("Stats Error:", await stats_resp.text())
                        
                else:
                    print(f"❌ Error: {response.status}")
                    text = await response.text()
                    print(f"Response: {text[:200]}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_collections())
