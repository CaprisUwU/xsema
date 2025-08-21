"""
Test Socket Connection

A simple script to test basic socket connectivity to a port.
"""
import socket
import sys
from datetime import datetime

def test_connection(host='localhost', port=8001):
    print(f"[{datetime.now().isoformat()}] Testing connection to {host}:{port}...")
    
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # 5 second timeout
        
        # Try to connect
        print(f"[{datetime.now().isoformat()}] Attempting to connect...")
        s.connect((host, port))
        print(f"[{datetime.now().isoformat()}] Successfully connected to {host}:{port}")
        
        # Try to send some data (HTTP GET request)
        request = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
        print(f"[{datetime.now().isoformat()}] Sending test data...")
        s.sendall(request)
        
        # Try to receive some data
        print(f"[{datetime.now().isoformat()}] Waiting for response...")
        response = s.recv(1024)
        print(f"[{datetime.now().isoformat()}] Received: {response.decode('utf-8', 'ignore')}")
        
        s.close()
        return True
        
    except socket.timeout:
        print(f"[{datetime.now().isoformat()}] Connection attempt timed out")
    except ConnectionRefusedError:
        print(f"[{datetime.now().isoformat()}] Connection refused - is the server running?")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Error: {e}")
    
    return False

if __name__ == "__main__":
    print(f"Socket Connection Test - {datetime.now().isoformat()}")
    print("-" * 50)
    
    # Test both localhost and 127.0.0.1
    for host in ['localhost', '127.0.0.1']:
        print(f"\nTesting connection to {host}:8001")
        print("=" * 50)
        success = test_connection(host, 8001)
        if success:
            print(f"\n✅ Successfully connected to {host}:8001")
            break
    else:
        print("\n❌ Failed to connect to any host on port 8001")
    
    print("\nTest complete")
