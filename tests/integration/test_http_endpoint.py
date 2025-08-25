"""
Test HTTP endpoint to verify server is responding.
"""
import requests
import sys

def test_http_endpoint():
    url = "http://localhost:8000/health"
    print(f"Testing HTTP endpoint: {url}")
    print("-" * 60)
    
    try:
        # Test 1: Basic GET request
        print("1. Sending GET request...")
        response = requests.get(url, timeout=5)
        print(f"✅ Status code: {response.status_code}")
        print(f"✅ Response: {response.text}")
        print(f"✅ Headers: {response.headers}")
        
        # Test 2: Check response content
        print("\n2. Verifying response content...")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Valid JSON response: {data}")
                return True
            except ValueError:
                print(f"⚠️  Response is not valid JSON: {response.text}")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("Starting HTTP endpoint test...")
    print("=" * 60)
    success = test_http_endpoint()
    print("\n" + "=" * 60)
    print("Test", "PASSED!" if success else "FAILED!")
    sys.exit(0 if success else 1)
