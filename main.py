"""
XSEMA - Main Application Entry Point

This is the main FastAPI application for XSEMA.
It provides real-time NFT analytics, security analysis, and portfolio management.
"""
import logging
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import json
import uuid
import traceback
from typing import Optional
import os
import mimetypes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("server.log")
    ]
)
logger = logging.getLogger(__name__)

# Application metadata
APP_TITLE = "XSEMA"
APP_DESCRIPTION = """
# XSEMA - Advanced NFT Security & Analytics Platform

A comprehensive platform for NFT analytics, security analysis, and portfolio management.

## Key Features

- **🔒 Security Analysis**: Advanced wallet clustering, wash trading detection, and anomaly detection
- **📊 Portfolio Management**: Track and analyze NFT portfolios across multiple wallets
- **🔍 Market Analytics**: Real-time market data, trends, and insights
- **🎯 Trait Analysis**: Comprehensive rarity scoring and trait statistics
- **⚡ Real-time Updates**: WebSocket-based live event streaming
- **🔗 Multi-Chain Support**: Ethereum mainnet with more chains coming soon

## API Sections

- **Portfolio**: Manage and track NFT portfolios
- **Security**: Advanced security analysis and threat detection
- **Market**: Market data and analytics
- **Traits**: NFT trait analysis and rarity scoring
- **WebSocket**: Real-time event streaming
"""

APP_VERSION = "2.0.0"

# Track application start time
app_start_time = time.time()

# Global WebSocket manager
websocket_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application lifecycle events.
    """
    # Startup
    logger.info(f"Starting {APP_TITLE} v{APP_VERSION}")
    
    try:
        # Initialize WebSocket manager
        global websocket_manager
        from live.ws_manager import ConnectionManager
        websocket_manager = ConnectionManager()
        logger.info("WebSocket manager initialized")
        
        # Initialize services
        await initialize_services()
        
        # Log successful startup
        logger.info(f"{APP_TITLE} started successfully")
        logger.info(f"API documentation available at: http://localhost:{os.environ.get('PORT', '8001')}/docs")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        logger.error(traceback.format_exc())
        raise
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {APP_TITLE}")
    await cleanup_services()
    logger.info("Shutdown complete")

# Create the main FastAPI application
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "health", "description": "Health check endpoints"},
        {"name": "portfolio", "description": "Portfolio management endpoints"},
        {"name": "security", "description": "Security analysis endpoints"},
        {"name": "market", "description": "Market data and analytics"},
        {"name": "traits", "description": "NFT trait analysis"},
        {"name": "wallets", "description": "Wallet analysis and tracking"},
        {"name": "websocket", "description": "Real-time WebSocket endpoints"},
    ]
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:5173",  # Vite development server
        "http://localhost:8001",  # API development server
        # Add production domains here
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Static files are handled by custom handler below
# Note: If custom handler fails on Railway, uncomment the line below:
# from fastapi.staticfiles import StaticFiles

async def initialize_services():
    """
    Initialize all required services during startup.
    """
    logger.info("Initializing services...")
    
    # Initialize cache
    try:
        from core.cache import initialize_cache
        await initialize_cache()
        logger.info("Cache service initialized")
    except Exception as e:
        logger.warning(f"Could not initialize cache: {e}")
    
    # Initialize database connections
    try:
        from core.config import settings
        # Add database initialization here
        logger.info("Database connections initialized")
    except Exception as e:
        logger.warning(f"Could not initialize database: {e}")

async def cleanup_services():
    """
    Cleanup services during shutdown.
    """
    logger.info("Cleaning up services...")
    
    # Cleanup WebSocket connections
    if websocket_manager:
        # Disconnect all active connections
        for client_id in list(websocket_manager.connections.keys()):
            await websocket_manager.disconnect(client_id)
    
    # Add other cleanup tasks here

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: Health status information
    """
    uptime = time.time() - app_start_time
    
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(uptime, 2),
        "environment": "development",  # TODO: Get from config
    }

# Root endpoint - serves the frontend
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint serving the XSEMA frontend application.
    
    Returns:
        FileResponse: The frontend index.html file
    """
    from fastapi.responses import FileResponse
    import os
    
    # Debug: Check working directory and file paths
    current_dir = os.getcwd()
    index_path = os.path.join("static", "index.html")
    static_dir = os.path.join(current_dir, "static")
    
    logger.info(f"Root route accessed - Current directory: {current_dir}")
    logger.info(f"Static directory path: {static_dir}")
    logger.info(f"Index file path: {index_path}")
    logger.info(f"Static directory exists: {os.path.exists(static_dir)}")
    logger.info(f"Index file exists: {os.path.exists(index_path)}")
    
    # List contents of static directory
    if os.path.exists(static_dir):
        try:
            static_contents = os.listdir(static_dir)
            logger.info(f"Static directory contents: {static_contents}")
        except Exception as e:
            logger.error(f"Error listing static directory: {e}")
    
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    else:
        # Fallback to API info if frontend not built
        return {
            "message": "Welcome to XSEMA",
            "version": APP_VERSION,
            "description": "Advanced NFT Security & Analytics Platform",
            "status": "operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "documentation": "/docs",
            "health_check": "/health",
                               "api_endpoints": {
                       "portfolio": "/api/v1/portfolio",
                       "market": "/api/v1",
                       "traits": "/api/v1/traits",
                       "security": "/api/v1/wallet-analysis",
                       "multi_chain": "/api/v1/multi-chain",
                       "enterprise_auth": "/api/v1/enterprise",
                       "saml_auth": "/api/v1/saml",
                       "oauth_auth": "/api/v1/oauth",
                       "websocket": "/ws"
                   },
            "features": [
                "🔒 Advanced Security Analysis",
                "📊 Portfolio Management", 
                "🔍 Market Analytics",
                "🎯 Trait Analysis",
                "⚡ Real-time Updates",
                "🔗 Multi-Chain Support"
            ],
            "note": "Frontend not built. Run 'npm run build' in frontend/ directory."
        }



# Include API routers
def include_routers():
    """
    Include all API routers in the application.
    """
    try:
        # Portfolio API routes (using main router from __init__.py)
        from portfolio.api.v1.endpoints import router as portfolio_router
        app.include_router(portfolio_router, prefix="/api/v1/portfolio", tags=["portfolio"])
        logger.info("Portfolio API routes included successfully")
    except Exception as e:
        logger.error(f"Error including portfolio routes: {e}")
        logger.info("Portfolio routes disabled due to import issues")
    
    try:
        # Market module routes (consolidated)
        try:
            from market.api.v1.endpoints import router as market_router
            app.include_router(market_router, prefix="/api/v1", tags=["market"])
            logger.info("Market module routes included successfully")
        except Exception as e:
            logger.error(f"Error including market routes: {e}")
            
        # Core API routes
        try:
            from api.v1.endpoints import traits, wallet_analysis
            app.include_router(traits.router, prefix="/api/v1", tags=["traits"])
            app.include_router(wallet_analysis.router, prefix="/api/v1", tags=["security"])
            logger.info("Core API routes enabled successfully")
        except Exception as e:
            logger.error(f"Error enabling some core routes: {e}")
            logger.info("Continuing with available routes")
        
        # Multi-chain API routes
        try:
            from api.v1.endpoints import multi_chain
            app.include_router(multi_chain.router, prefix="/api/v1/multi-chain", tags=["multi-chain"])
            logger.info("Multi-chain API routes included successfully")
        except Exception as e:
            logger.error(f"Error including multi-chain routes: {e}")
            logger.info("Multi-chain routes disabled due to import issues")
            
        # Enterprise Authentication API routes
        try:
            from api.v1.endpoints import enterprise_auth
            app.include_router(enterprise_auth.router, prefix="/api/v1/enterprise", tags=["enterprise-auth"])
            logger.info("Enterprise Authentication API routes included successfully")
        except Exception as e:
            logger.error(f"Error including enterprise auth routes: {e}")
            logger.info("Enterprise auth routes disabled due to import issues")
        
        # SAML Authentication API routes
        try:
            from api.v1.endpoints import saml_auth
            app.include_router(saml_auth.router, prefix="/api/v1/saml", tags=["saml-auth"])
            logger.info("SAML Authentication API routes included successfully")
        except Exception as e:
            logger.error(f"Error including SAML auth routes: {e}")
            logger.info("SAML auth routes disabled due to import issues")
        
        # SAML Configuration API routes
        try:
            from api.v1.endpoints import saml_config
            app.include_router(saml_config.router, prefix="/api/v1/saml", tags=["saml-config"])
            logger.info("SAML Configuration API routes included successfully")
        except Exception as e:
            logger.error(f"Error including SAML config routes: {e}")
            logger.info("SAML config routes disabled due to import issues")
        
        # OAuth 2.0 Authentication API routes
        try:
            from api.v1.endpoints import oauth_auth
            app.include_router(oauth_auth.router, prefix="/api/v1/oauth", tags=["oauth-auth"])
            logger.info("OAuth 2.0 Authentication API routes included successfully")
        except Exception as e:
            logger.error(f"Error including OAuth auth routes: {e}")
            logger.info("OAuth auth routes disabled due to import issues")
    except Exception as e:
        logger.error(f"Error including core routes: {e}")
    
    # Note: Legacy routes removed as they were deprecated
    logger.info("Legacy routes skipped (deprecated modules removed)")

# Include routers after app creation
include_routers()

# FALLBACK OPTION: If custom static handler fails on Railway, uncomment these lines:
# from fastapi.staticfiles import StaticFiles
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Enhanced static file handler optimized for Railway - MUST be BEFORE catch-all
@app.get("/static/{file_path:path}")
async def serve_static_files(file_path: str):
    """
    Enhanced static file handler with proper MIME type detection.
    Optimized for Railway deployment with fallback handling.
    """
    # Debug logging for Railway troubleshooting
    logger.info(f"Static file request: {file_path}")
    
    # Handle root /static/ path
    if not file_path or file_path == "":
        return {
            "message": "Static files directory",
            "note": "Access specific files like /static/index.html, /static/assets/script.js, etc."
        }
    
    file_path_full = os.path.join("static", file_path)
    logger.info(f"Full file path: {file_path_full}")
    logger.info(f"File exists: {os.path.exists(file_path_full)}")
    
    if not os.path.exists(file_path_full):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    # Comprehensive MIME type mapping for Railway
    mime_types = {
        # JavaScript
        '.js': 'application/javascript',
        '.mjs': 'application/javascript',
        '.jsx': 'application/javascript',
        
        # CSS
        '.css': 'text/css',
        '.scss': 'text/x-scss',
        '.sass': 'text/x-sass',
        
        # Images
        '.svg': 'image/svg+xml',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.ico': 'image/x-icon',
        '.bmp': 'image/bmp',
        
        # Fonts
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
        '.ttf': 'font/ttf',
        '.otf': 'font/otf',
        '.eot': 'application/vnd.ms-fontobject',
        
        # Documents
        '.html': 'text/html',
        '.htm': 'text/html',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        
        # Archives
        '.zip': 'application/zip',
        '.tar': 'application/x-tar',
        '.gz': 'application/gzip',
        
        # Web specific
        '.webmanifest': 'application/manifest+json',
        '.webp': 'image/webp',
        '.webm': 'video/webm',
    }
    
    # Get file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Determine MIME type
    mime_type = mime_types.get(file_ext, 'application/octet-stream')
    
    # Special handling for specific files
    if file_path.endswith('site.webmanifest'):
        mime_type = 'application/manifest+json'
    elif file_path.endswith('.js') and 'assets' in file_path:
        mime_type = 'application/javascript'
    elif file_path.endswith('.css') and 'assets' in file_path:
        mime_type = 'text/css'
    
    # Create response with proper headers
    try:
        response = FileResponse(
            file_path_full, 
            media_type=mime_type,
            headers={
                "Cache-Control": "public, max-age=31536000",  # 1 year cache
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block"
            }
        )
        
        # Add specific headers for JavaScript files
        if mime_type == 'application/javascript':
            response.headers["Content-Type"] = "application/javascript; charset=utf-8"
        elif mime_type == 'text/css':
            response.headers["Content-Type"] = "text/css; charset=utf-8"
        elif mime_type == 'application/manifest+json':
            response.headers["Content-Type"] = "application/manifest+json; charset=utf-8"
        
        return response
        
    except Exception as e:
        logger.error(f"Error serving static file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error serving file: {e}")

# Frontend routing catch-all - serves index.html for all non-API routes
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """
    Catch-all route for frontend routing.
    Serves index.html for all non-API routes to support React Router.
    """
    from fastapi.responses import FileResponse
    import os
    
    # Skip API routes and static files
    if full_path.startswith(("api/", "static/", "docs", "openapi.json", "health")):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve frontend index.html for all other routes
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Frontend not built")

# WebSocket endpoint for real-time events
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time NFT event streaming.
    
    Protocol:
    - Subscribe: {"type": "subscribe", "channels": ["nft_events", "sales"]}
    - Unsubscribe: {"type": "unsubscribe", "channels": ["sales"]}
    - Ping: {"type": "ping"}
    """
    if not websocket_manager:
        await websocket.close(code=1011, reason="WebSocket service unavailable")
        return
    
    client_id = f"client-{uuid.uuid4().hex[:8]}"
    await websocket_manager.connect(websocket, client_id)
    logger.info(f"WebSocket client connected: {client_id}")
    
    try:
        while True:
            try:
                # Receive and process client messages
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    await websocket_manager.handle_message(client_id, message)
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON format"
                    })
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected: {client_id}")
                await websocket_manager.disconnect(client_id)
                break
                
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        logger.error(traceback.format_exc())
        await websocket_manager.disconnect(client_id)

# Custom error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": str(uuid.uuid4())
        }
    )

if __name__ == "__main__":
    # Run the application
    import os
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info",
        access_log=True,
    )