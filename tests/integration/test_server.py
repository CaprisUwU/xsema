import requests
import time

def test_server():
    url = "http://localhost:8001/health"
    print(f"Testing server at {url}")
    
    try:
        print("Sending request...")
        start_time = time.time()
        response = requests.get(url, timeout=5)
        end_time = time.time()
        
        print(f"Response received in {end_time - start_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        print("Response content:", response.text)
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_server()
