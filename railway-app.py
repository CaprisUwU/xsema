#!/usr/bin/env python3
"""
Ultra-minimal XSEMA app for Railway deployment
No external dependencies, no complex imports
"""

import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class XSEMAHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response = """
            <html>
                <head><title>XSEMA Platform</title></head>
                <body>
                    <h1>🚀 XSEMA Successfully Deployed on Railway!</h1>
                    <p>Advanced NFT Security & Analytics Platform</p>
                    <p>Status: ✅ Production Ready</p>
                    <p>Build: ✅ Ultra-Minimal</p>
                </body>
            </html>
            """
            self.wfile.write(response.encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "XSEMA is running",
                "build": "ultra-minimal"
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), XSEMAHandler)
    print(f"Starting XSEMA server on port {port}")
    server.serve_forever()
