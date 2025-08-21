#!/usr/bin/env python3
"""
XSEMA HTTP Server for Railway - Actually responds to HTTP requests
"""
import os
import socket
import threading
import time

def create_http_response(status_code, content_type, body):
    response = f"""HTTP/1.1 {status_code}
Content-Type: {content_type}
Content-Length: {len(body)}
Connection: close

{body}"""
    return response.encode()

def handle_request(client_socket, addr):
    try:
        request = client_socket.recv(1024).decode()
        if not request:
            return
        
        lines = request.split('\n')
        if not lines:
            return
            
        request_line = lines[0]
        path = request_line.split(' ')[1] if len(request_line.split(' ')) > 1 else '/'
        
        if path == '/':
            body = """
            <html>
                <head><title>XSEMA Platform</title></head>
                <body>
                    <h1>🚀 XSEMA Successfully Deployed on Railway!</h1>
                    <p>Advanced NFT Security & Analytics Platform</p>
                    <p>Status: ✅ Production Ready</p>
                    <p>Server: HTTP Server Running</p>
                </body>
            </html>
            """
            response = create_http_response(200, 'text/html', body)
        elif path == '/health':
            body = '{"status": "healthy", "message": "XSEMA HTTP server is running"}'
            response = create_http_response(200, 'application/json', body)
        else:
            body = 'Not Found'
            response = create_http_response(404, 'text/plain', body)
            
        client_socket.send(response)
        
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        client_socket.close()

def main():
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"🚀 XSEMA HTTP Server running on {host}:{port}")
        print(f"✅ Health check: http://localhost:{port}/health")
        print(f"✅ Root page: http://localhost:{port}/")
        
        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_request, args=(client_socket, addr))
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\nShutting down XSEMA server...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
