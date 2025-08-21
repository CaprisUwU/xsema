"""
Simple HTTP test script to verify server is responding.
"""
import requests
import sys

def test_http():
    url = "http://localhost:8001/health"
    print(f"Testing HTTP connection to {url}...")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting HTTP test...")
    success = test_http()
    print("\nTest", "succeeded!" if success else "failed!")
    sys.exit(0 if success else 1)
