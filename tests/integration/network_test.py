import socket
import sys
import os
import platform
import requests
from datetime import datetime

def print_banner():
    print("\n=== Network and Server Diagnostics ===")
    print(f"Python Version: {platform.python_version()}")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Current Directory: {os.getcwd()}")
    print(f"Python Path: {sys.executable}")
    print("-" * 40)

def test_port(port):
    print(f"\nTesting port {port}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                print(f"Port {port} is in use by another process")
                return False
            else:
                print(f"Port {port} is available")
                return True
    except Exception as e:
        print(f"Error testing port {port}: {e}")
        return False

def test_http_server(port):
    print(f"\nTesting HTTP server on port {port}...")
    try:
        response = requests.get(f"http://localhost:{port}", timeout=5)
        print(f"HTTP Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return True
    except requests.exceptions.ConnectionError:
        print("Connection refused - server may not be running")
    except requests.exceptions.Timeout:
        print("Request timed out")
    except Exception as e:
        print(f"Error: {e}")
    return False

def test_python_http_server():
    print("\n=== Testing Python HTTP Server ===")
    port = 8080
    if test_port(port):
        try:
            import http.server
            import socketserver
            import threading
            import time
            
            print(f"Starting HTTP server on port {port}...")
            handler = http.server.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer(("", port), handler)
            
            def run_server():
                httpd.serve_forever()
                
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # Give it a moment to start
            time.sleep(2)
            
            # Test the server
            if test_http_server(port):
                print("Python HTTP server is working correctly!")
            else:
                print("Python HTTP server is not responding")
                
        except Exception as e:
            print(f"Error starting HTTP server: {e}")
        finally:
            httpd.shutdown()
            httpd.server_close()
            print(f"HTTP server on port {port} has been stopped")

if __name__ == "__main__":
    print_banner()
    
    # Test common ports
    for port in [8000, 8001, 8003, 8005, 8080]:
        test_port(port)
    
    # Test Python's built-in HTTP server
    test_python_http_server()
    
    print("\n=== Diagnostics Complete ===")
    print("If you see any errors or unexpected results, please share them.")
