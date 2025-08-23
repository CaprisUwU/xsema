from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI application
app = FastAPI(title="XSEMA", version="2.0.0")

@app.on_event("startup")
async def startup_event():
    port = os.environ.get("PORT", "8000")
    logger.info(f"🚀 XSEMA starting on port {port}")
    logger.info(f"🌐 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'development')}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"📋 Available files: {os.listdir('.')}")

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

@app.get("/")
async def root():
    return {"message": "Welcome to XSEMA", "status": "running"}

@app.get("/test")
async def test():
    return {"message": "Test successful", "timestamp": "now"}

@app.get("/static/{file_path:path}")
async def static_files(file_path: str):
    return {"message": "Static file requested", "path": file_path}
