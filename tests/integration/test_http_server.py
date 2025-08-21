import http.server
import socketserver
import threading
import time
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hello, this is a test server!')

def start_test_server(port=8002):
    if is_port_in__use(port):
        print(f"Port {port} is already in use")
        return None
    
    handler = SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    
    def run_server():
        print(f"Starting test HTTP server on port {port}")
        httpd.serve_forever()
    
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server a moment to start
    time.sleep(1)
    return httpd, server_thread

if __name__ == "__main__":
    # Start a test server on port 8002
    httpd, server_thread = start_test_server(8002)
    
    if httpd:
        try:
            print("Test server is running. Press Ctrl+C to stop.")
            server_thread.join()
        except KeyboardInterrupt:
            print("\nShutting down test server...")
            httpd.shutdown()
            httpd.server_close()
            server_thread.join(timeout=1)
            print("Test server stopped.")
