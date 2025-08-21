"""
Integration test script for Portfolio Management API endpoints.
"""
import requests
import json
import time

def test_endpoint(method, url, data=None, headers=None):
    """Test an API endpoint and print the response."""
    try:
        print(f"\n{'='*80}")
        print(f"Testing {method.upper()} {url}")
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
            
        response = requests.request(
            method=method.upper(),
            url=url,
            json=data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print("Response:")
            print(json.dumps(response_data, indent=2))
            return response_data
        except ValueError:
            print(f"Response (raw): {response.text}")
            return response.text
            
    except Exception as e:
        print(f"Error testing {url}: {str(e)}")
        return None

def test_assets_endpoints(base_url):
    """Test assets endpoints."""
    print("\n" + "="*50)
    print("TESTING ASSETS ENDPOINTS")
    print("="*50)
    
    # Get all assets
    test_endpoint('GET', f"{base_url}/api/v1/assets/")
    
    # Get asset by ID (replace with a valid asset ID if available)
    test_endpoint('GET', f"{base_url}/api/v1/assets/ethereum")

def test_nfts_endpoints(base_url):
    """Test NFTs endpoints."""
    print("\n" + "="*50)
    print("TESTING NFTS ENDPOINTS")
    print("="*50)
    
    # Get all NFTs for a wallet (replace with a valid wallet address)
    wallet_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik's wallet
    test_endpoint('GET', f"{base_url}/api/v1/nfts/wallet/{wallet_address}")
    
    # Get NFT details (replace with a valid contract address and token ID)
    test_endpoint('GET', f"{base_url}/api/v1/nfts/0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D/1")  # Bored Ape Yacht Club #1

def test_wallets_endpoints(base_url):
    """Test wallets endpoints."""
    print("\n" + "="*50)
    print("TESTING WALLETS ENDPOINTS")
    print("="*50)
    
    # Get wallet balance (replace with a valid wallet address)
    wallet_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik's wallet
    test_endpoint('GET', f"{base_url}/api/v1/wallets/{wallet_address}/balance")

def test_health_endpoints(base_url):
    """Test health and root endpoints."""
    print("\n" + "="*50)
    print("TESTING HEALTH AND ROOT ENDPOINTS")
    print("="*50)
    
    # Test root endpoint
    test_endpoint('GET', f"{base_url}/")
    
    # Test health check endpoint
    test_endpoint('GET', f"{base_url}/health")

def main():
    base_url = "http://localhost:8000"  # Default FastAPI port
    
    print("Portfolio Management API Integration Tests")
    print("="*80)
    
    # Test all endpoints
    test_health_endpoints(base_url)
    test_assets_endpoints(base_url)
    test_nfts_endpoints(base_url)
    test_wallets_endpoints(base_url)
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()
