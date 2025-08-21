#!/usr/bin/env python3
import os
import sys

def main():
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting XSEMA on port {port}")
    
    # Simple HTTP response
    response = f"""HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<html><body><h1>XSEMA Running on Port {port}</h1></body></html>"""
    
    print("XSEMA is ready!")
    print(f"Health check endpoint: http://localhost:{port}/health")
    
    # Keep process alive
    while True:
        try:
            import time
            time.sleep(1)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
