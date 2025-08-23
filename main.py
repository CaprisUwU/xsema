"""
XSEMA - Ultra-Minimal Application Entry Point

This is the most minimal FastAPI application possible to ensure it starts and stays running on Railway.
"""
import os
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the most minimal FastAPI application possible
app = FastAPI(
    title="XSEMA",
    description="Advanced NFT Security & Analytics Platform",
    version="2.0.0"
)

# Ultra-simple health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check for Railway"""
    return {"status": "healthy", "message": "XSEMA is running"}

# Ultra-simple root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to XSEMA", "status": "running"}

# Test endpoint
@app.get("/test")
async def test():
    """Test endpoint"""
    return {"message": "Test successful", "timestamp": "now"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)