#!/usr/bin/env python3
"""
Railway start script for XSEMA
This script handles the PORT environment variable and starts the FastAPI application
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# Configure logging to stdout (Railway requirement)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Get port from Railway environment variable
        port_str = os.environ.get("PORT")
        if not port_str:
            logger.error("❌ PORT environment variable not set!")
            logger.error("Available environment variables:")
            for key, value in os.environ.items():
                logger.error(f"  {key}: {value}")
            sys.exit(1)
        
        # Ensure port is a valid integer
        try:
            port = int(port_str)
            logger.info(f"✅ PORT environment variable: {port}")
        except ValueError:
            logger.error(f"❌ Invalid PORT value: {port_str}")
            sys.exit(1)
        
        # Log environment information
        logger.info("=" * 50)
        logger.info("🚀 XSEMA RAILWAY STARTUP")
        logger.info("=" * 50)
        logger.info(f"📡 Port: {port}")
        logger.info(f"🌐 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')}")
        logger.info(f"📁 Working Directory: {os.getcwd()}")
        logger.info(f"🐍 Python Version: {sys.version}")
        logger.info(f"📦 Python Path: {sys.executable}")
        
        # Check if app.py exists
        app_file = Path("app.py")
        if not app_file.exists():
            logger.error(f"❌ app.py not found at {app_file.absolute()}")
            logger.error(f"Available files: {list(Path('.').iterdir())}")
            sys.exit(1)
        
        logger.info(f"✅ app.py found at {app_file.absolute()}")
        logger.info("=" * 50)
        
        # Start the FastAPI application
        logger.info(f"🚀 Starting uvicorn on port {port}")
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start XSEMA: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
