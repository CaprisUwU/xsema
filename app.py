from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI application
app = FastAPI(title="XSEMA", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    port = os.environ.get("PORT", "8000")
    logger.info(f"🚀 XSEMA starting on port {port}")
    logger.info(f"🌐 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'development')}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"📋 Available files: {os.listdir('.')}")
    logger.info(f"📁 Static directory: {os.listdir('static') if os.path.exists('static') else 'Not found'}")

@app.get("/health")
async def health_check():
    try:
        port = os.environ.get("PORT", "8000")
        return {
            "status": "healthy", 
            "message": "XSEMA is running",
            "port": port,
            "environment": os.environ.get("RAILWAY_ENVIRONMENT", "development")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main XSEMA React application"""
    try:
        index_path = os.path.join("static", "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        else:
            logger.error(f"index.html not found at {index_path}")
            raise HTTPException(status_code=404, detail="Frontend not found")
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        return HTMLResponse(content=f"""
        <html>
        <head><title>XSEMA - Loading</title></head>
        <body>
            <h1>🚀 XSEMA is starting up...</h1>
            <p>Please wait a moment while the application loads.</p>
            <p>Error: {str(e)}</p>
        </body>
        </html>
        """)

@app.get("/test")
async def test():
    return {"message": "Test successful", "timestamp": "now"}

# Catch-all route for SPA routing
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Handle SPA routing by serving index.html for non-API routes"""
    if full_path.startswith("api/") or full_path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    try:
        index_path = os.path.join("static", "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")
    except Exception as e:
        logger.error(f"Error in catch-all route: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
