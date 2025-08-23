#!/usr/bin/env python3
"""
Railway start script for XSEMA
This script handles the PORT environment variable and starts the FastAPI application
"""

import os
import sys
import uvicorn
from app import app

if __name__ == "__main__":
    try:
        # Get port from Railway environment variable, default to 8000
        port_str = os.environ.get("PORT", "8000")
        
        # Ensure port is a valid integer
        try:
            port = int(port_str)
        except ValueError:
            print(f"❌ Invalid PORT value: {port_str}. Using default port 8000.")
            port = 8000
        
        print(f"🚀 Starting XSEMA on port {port}")
        print(f"🌐 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'development')}")
        
        # Start the FastAPI application
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Failed to start XSEMA: {e}")
        sys.exit(1)
