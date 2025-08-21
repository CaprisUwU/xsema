"""Simplified Web3 connection test script."""
import time
from web3 import Web3

def test_connection(rpc_url, chain_name):
    """Test connection to a Web3 provider."""
    print(f"\nTesting {chain_name}...")
    print(f"URL: {rpc_url}")
    
    try:
        # Initialize Web3
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))
        
        # Test connection
        start_time = time.time()
        is_connected = w3.is_connected()
        connection_time = time.time() - start_time
        
        print(f"Connected: {'✅' if is_connected else '❌'}")
        print(f"Time: {connection_time:.2f}s")
        
        if is_connected:
            # Get block number
            try:
                block = w3.eth.block_number
                print(f"Latest block: {block:,}")
                return True
            except Exception as e:
                print(f"Error getting block: {e}")
        
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function to test multiple RPC endpoints."""
    print("Simple Web3 Connection Tester")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ("https://polygon-rpc.com", "Polygon"),
        ("https://bsc-dataseed.binance.org/", "BSC"),
        ("https://api.avax.network/ext/bc/C/rpc", "Avalanche"),
    ]
    
    results = []
    for url, name in endpoints:
        success = test_connection(url, name)
        results.append((name, success))
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    for name, success in results:
        print(f"{name}: {'✅' if success else '❌'}")
    
    print("\nTests completed!")

if __name__ == "__main__":
    main()
