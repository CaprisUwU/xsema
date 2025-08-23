"""
XSEMA - Minimal Application Entry Point

This is a minimal FastAPI application for XSEMA to ensure it starts successfully on Railway.
"""
import os
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the main FastAPI application
app = FastAPI(
    title="XSEMA",
    description="Advanced NFT Security & Analytics Platform",
    version="2.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check for Railway"""
    return {"status": "healthy", "message": "XSEMA is running"}

# Root endpoint - serves the frontend
@app.get("/")
async def root():
    """Root endpoint serving the XSEMA frontend"""
    try:
        # Check if frontend files exist
        current_dir = os.getcwd()
        index_path = os.path.join(current_dir, "static", "index.html")
        
        if os.path.exists(index_path):
            return FileResponse(index_path, media_type="text/html")
        else:
            # Fallback response
            return {
                "message": "Welcome to XSEMA",
                "version": "2.0.0",
                "status": "operational",
                "note": "Frontend files not found"
            }
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        return {"error": "Internal error", "message": str(e)}

# Static file handler
@app.get("/static/{file_path:path}")
async def serve_static_files(file_path: str):
    """Serve static files"""
    try:
        file_path_full = os.path.join(os.getcwd(), "static", file_path)
        
        if not os.path.exists(file_path_full):
            return JSONResponse(
                status_code=404,
                content={"error": "File not found", "path": file_path}
            )
        
        # Basic MIME type detection
        if file_path.endswith('.html'):
            media_type = "text/html"
        elif file_path.endswith('.js'):
            media_type = "application/javascript"
        elif file_path.endswith('.css'):
            media_type = "text/css"
        elif file_path.endswith('.png'):
            media_type = "image/png"
        elif file_path.endswith('.svg'):
            media_type = "image/svg+xml"
        else:
            media_type = "application/octet-stream"
        
        return FileResponse(file_path_full, media_type=media_type)
        
    except Exception as e:
        logger.error(f"Error serving static file: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal error", "message": str(e)}
        )

# Basic API info endpoint
@app.get("/api/info")
async def api_info():
    """Basic API information"""
    return {
        "name": "XSEMA",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": ["/", "/health", "/static/*", "/api/info"]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)