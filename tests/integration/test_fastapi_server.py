import sys
import os
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Create a minimal FastAPI app
app = FastAPI(title="Test FastAPI Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add a simple endpoint
@app.get("/")
async def root():
    return {
        "message": "Test FastAPI server is running!",
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "python_path": sys.path
    }

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-07-31T17:40:00Z"}

# Add a test endpoint that returns request information
@app.get("/test-request")
async def test_request(request: Request):
    return {
        "client_host": request.client.host if request.client else None,
        "headers": dict(request.headers),
        "method": request.method,
        "url": str(request.url)
    }

if __name__ == "__main__":
    port = 8001
    print(f"Starting test FastAPI server on port {port}...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("\nEndpoints:")
    print(f"  - http://localhost:{port}/")
    print(f"  - http://localhost:{port}/health")
    print(f"  - http://localhost:{port}/test-request")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Configure and run the server
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=True
    )
    
    server = uvicorn.Server(config)
    
    try:
        # Run the server
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nError starting server: {e}")
        raise
