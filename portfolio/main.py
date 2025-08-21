"""
Portfolio Management API

This module serves as the main entry point for the Portfolio Management API.
It initializes the FastAPI application and includes all API routers.
"""
import os
import logging
import sys
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import traceback

from core.security.authentication import validate_api_key
from core.exceptions import standard_error_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Portfolio Management API",
    description="API for managing and analyzing cryptocurrency and NFT portfolios",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom error handling middleware
@app.middleware("http")
async def exception_middleware(request: Request, call_next):
    return await standard_error_handler(request, call_next)

# Simple health check endpoint - defined BEFORE any router imports
@app.get("/api/v1/health", tags=["health"])
async def health_check():
    """Health check endpoint to verify the API is running."""
    try:
        return {"status": "ok", "message": "API is running"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": "Health check failed"}

# Include the API v1 router with the base prefix
from .api.v1.endpoints import router as api_v1_router
app.include_router(api_v1_router, prefix="/api/v1", dependencies=[Depends(validate_api_key)])

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Portfolio Management API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Add startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Portfolio Management API...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Portfolio Management API...")

# This allows running the app directly with: python -m portfolio
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("portfolio.main:app", host="0.0.0.0", port=8000, reload=True)
