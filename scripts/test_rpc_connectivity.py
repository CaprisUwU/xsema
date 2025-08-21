#!/usr/bin/env python3
"""
Test RPC Connectivity for Multi-Chain Networks
This script tests the connection to all configured blockchain networks
"""

import asyncio
import sys
import os
import aiohttp
import time
from typing import Dict, List, Tuple

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_rpc_endpoint(session: aiohttp.ClientSession, name: str, url: str, method: str = "POST", params: dict = None) -> Tuple[str, bool, float, str]:
    """
    Test an RPC endpoint and return the result
    """
    start_time = time.time()
    try:
        if method == "POST":
            # Standard EVM RPC call
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_blockNumber",
                "params": []
            }
            if params:
                payload.update(params)
            
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data:
                        response_time = time.time() - start_time
                        return name, True, response_time, f"Block: {data['result']}"
                    else:
                        return name, False, time.time() - start_time, f"Invalid response: {data}"
                else:
                    return name, False, time.time() - start_time, f"HTTP {response.status}"
        
        elif method == "GET":
            # Simple GET request for some endpoints
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    response_time = time.time() - start_time
                    return name, True, response_time, f"Status: {response.status}"
                else:
                    return name, False, time.time() - start_time, f"HTTP {response.status}"
                    
    except asyncio.TimeoutError:
        return name, False, time.time() - start_time, "Timeout"
    except Exception as e:
        return name, False, time.time() - start_time, f"Error: {str(e)[:50]}"

async def test_all_networks():
    """
    Test all configured blockchain networks
    """
    print("🧪 Testing Multi-Chain RPC Connectivity")
    print("=" * 60)
    
    # Network configurations
    networks = [
        ("Ethereum", "https://eth.llamarpc.com", "POST"),
        ("Polygon", "https://polygon-rpc.com", "POST"),
        ("BSC", "https://bsc-dataseed1.binance.org", "POST"),
        ("Arbitrum", "https://arb1.arbitrum.io/rpc", "POST"),
        ("Optimism", "https://mainnet.optimism.io", "POST"),
        ("Base", "https://mainnet.base.org", "POST"),
        ("Avalanche", "https://api.avax.network/ext/bc/C/rpc", "POST"),
        ("Fantom", "https://rpc.ftm.tools", "POST"),
        ("Solana", "https://api.mainnet-beta.solana.com", "POST", {"method": "getSlot", "params": []}),
    ]
    
    results = []
    async with aiohttp.ClientSession() as session:
        # Test all networks concurrently
        tasks = []
        for name, url, method, *extra in networks:
            params = extra[0] if extra else None
            task = test_rpc_endpoint(session, name, url, method, params)
            tasks.append(task)
        
        # Wait for all tests to complete
        network_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in network_results:
            if isinstance(result, Exception):
                results.append(("Unknown", False, 0, f"Exception: {result}"))
            else:
                results.append(result)
    
    # Display results
    print("\n📊 Network Connectivity Results:")
    print("-" * 60)
    
    successful = 0
    total_time = 0
    
    for name, success, response_time, details in results:
        status = "✅" if success else "❌"
        time_str = f"{response_time:.2f}s" if success else "N/A"
        
        if success:
            successful += 1
            total_time += response_time
        
        print(f"{status} {name:<12} | {time_str:<8} | {details}")
    
    print("-" * 60)
    print(f"📈 Summary: {successful}/{len(networks)} networks connected successfully")
    
    if successful > 0:
        avg_time = total_time / successful
        print(f"⏱️  Average response time: {avg_time:.2f} seconds")
    
    # Test multi-chain service integration
    print("\n🔗 Testing Multi-Chain Service Integration:")
    print("-" * 60)
    
    try:
        from services.multi_chain_service import MultiChainService
        from core.multi_chain_config import MultiChainConfig, ChainType
        
        print("✅ Multi-chain modules imported successfully")
        
        # Test configuration
        config = MultiChainConfig()
        supported_networks = config.get_supported_networks()
        print(f"✅ Found {len(supported_networks)} supported networks in config")
        
        # Test service
        service = MultiChainService()
        print("✅ MultiChainService created successfully")
        
        # Test connection status
        print("🔄 Testing connection status...")
        status = await service.get_connection_status()
        
        connected_count = sum(1 for is_connected in status.values() if is_connected)
        print(f"✅ {connected_count}/{len(status)} networks connected via service")
        
        return successful == len(networks)
        
    except Exception as e:
        print(f"❌ Multi-chain service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_all_networks())
        if success:
            print("\n🎉 All networks connected successfully!")
        else:
            print("\n⚠️  Some networks failed to connect. Check RPC URLs and network status.")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
