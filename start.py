#!/usr/bin/env python3
"""
Railway start script for XSEMA
This script handles the PORT environment variable and starts the FastAPI application
"""

import os
import uvicorn
from main import app

if __name__ == "__main__":
    # Get port from Railway environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting XSEMA on port {port}")
    
    # Start the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
