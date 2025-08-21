"""
Test if port 8001 is available and start a simple HTTP server.
"""
import socket
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

def is_port_available(port):
    """Check if a port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            return True
        except OSError:
            return False

def start_temp_server(port):
    """Start a temporary HTTP server on the specified port."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Temporary HTTP server started on port {port}")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()

if __name__ == "__main__":
    port = 8001
    print(f"Testing port {port}...")
    
    if is_port_available(port):
        print(f"[OK] Port {port} is available")
        
        # Start a temporary HTTP server
        print(f"Starting a temporary HTTP server on port {port}...")
        try:
            start_temp_server(port)
        except KeyboardInterrupt:
            print("\nServer stopped by user")
        except Exception as e:
            print(f"Error starting server: {e}")
    else:
        print(f"[ERROR] Port {port} is not available")
        print("Please close any applications using this port and try again.")
