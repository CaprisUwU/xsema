from fastapi import FastAPI, HTTPException, Request, Depends, status, Query
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any

# Import authentication modules
from core.authentication import (
    auth_manager, 
    authenticate_user, 
    register_user,
    UserRegistration, 
    UserLogin,
    UserProfile,
    TokenData
)

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xsema.log'),
        logging.StreamHandler()
    ]
)
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

# Global disclaimer and safety information
DEMO_DISCLAIMER = """
⚠️ **DEMO VERSION - NOT FOR REAL INVESTMENT USE** ⚠️

This is a demonstration prototype of XSEMA. 
- All data shown is MOCK/SIMULATED data
- Do NOT make investment decisions based on this information
- This is NOT a financial advisory tool
- Use at your own risk

For real investment advice, consult qualified financial professionals.
"""

@app.on_event("startup")
async def startup_event():
    port = os.environ.get("PORT", "8000")
    logger.info(f"🚀 XSEMA starting on port {port}")
    logger.info(f"🌐 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'development')}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"📋 Available files: {os.listdir('.')}")
    logger.info(f"📁 Static directory: {os.listdir('static') if os.path.exists('static') else 'Not found'}")
    logger.info("⚠️ IMPORTANT: This is a DEMO VERSION - NOT FOR REAL INVESTMENT USE")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests for security and monitoring"""
    start_time = datetime.now()
    
    # Log request details
    logger.info(f"📥 REQUEST: {request.method} {request.url}")
    logger.info(f"👤 User-Agent: {request.headers.get('user-agent', 'Unknown')}")
    logger.info(f"🌐 Client IP: {request.client.host if request.client else 'Unknown'}")
    
    # Process request
    response = await call_next(request)
    
    # Log response details
    process_time = datetime.now() - start_time
    logger.info(f"📤 RESPONSE: {response.status_code} - Processed in {process_time.total_seconds():.3f}s")
    
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint with disclaimer"""
    try:
        port = os.environ.get("PORT", "8000")
        logger.info("🏥 Health check requested")
        return {
            "status": "healthy", 
            "message": "XSEMA is running",
            "port": port,
            "environment": os.environ.get("RAILWAY_ENVIRONMENT", "development"),
            "warning": "DEMO VERSION - NOT FOR REAL INVESTMENT USE",
            "timestamp": datetime.now().isoformat(),
            "access": "Public demo - No authentication required"
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/terms")
async def terms_of_service():
    """Serve the terms of service"""
    logger.info("📜 Terms of service requested")
    try:
        terms_path = "TERMS_OF_SERVICE.md"
        if os.path.exists(terms_path):
            with open(terms_path, "r", encoding="utf-8") as f:
                terms_content = f.read()
            
            # Simple HTML conversion without complex markdown parsing
            html_content = """
            <html>
            <head>
                <title>Terms of Service - XSEMA Demo</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; line-height: 1.6; }
                    .container { max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .warning { background: #ff6b6b; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }
                    h1, h2, h3 { color: #2c3e50; }
                    h1 { border-bottom: 3px solid #3498db; padding-bottom: 10px; }
                    h2 { border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; margin-top: 30px; }
                    ul, ol { margin: 20px 0; }
                    li { margin: 10px 0; }
                    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1; text-align: center; color: #7f8c8d; }
                    pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
                    code { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="warning">
                        <h2>⚠️ DEMO VERSION - NOT FOR REAL INVESTMENT USE ⚠️</h2>
                        <p><strong>This is a demonstration prototype of XSEMA.</strong></p>
                    </div>
                    
                    <div class="terms-content">
                        """ + terms_content.replace('# ', '<h1>').replace('## ', '<h2>').replace('### ', '<h3>').replace('#### ', '<h4>').replace('\n\n', '</p><p>').replace('\n- ', '</p><p>• ').replace('\n', '<br>') + """
                    </div>
                    
                    <div class="footer">
                        <p><a href="/">← Return to XSEMA Demo</a></p>
                        <p><em>XSEMA Demo Version - For demonstration purposes only</em></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            logger.info("✅ Terms of service served successfully")
            return HTMLResponse(content=html_content)
        else:
            logger.error(f"❌ Terms of service file not found at {terms_path}")
            raise HTTPException(status_code=404, detail="Terms of service not found")
    except Exception as e:
        logger.error(f"❌ Error serving terms of service: {e}")
        # Return a simple error page instead of raising an exception
        return HTMLResponse(content="""
        <html>
        <head>
            <title>Error - XSEMA Demo</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .error { background: #ff6b6b; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ Error Loading Terms of Service</h1>
                <div class="error">
                    <p><strong>Sorry, there was an error loading the terms of service.</strong></p>
                    <p>Error: """ + str(e) + """</p>
                </div>
                <p><a href="/">← Return to XSEMA Demo</a></p>
                <p><em>XSEMA Demo Version - For demonstration purposes only</em></p>
            </div>
        </body>
        </html>
        """, status_code=500)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main XSEMA React application with disclaimer"""
    try:
        logger.info("🏠 Root page requested - serving XSEMA frontend")
        index_path = os.path.join("static", "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Add disclaimer banner to the HTML
            disclaimer_banner = """
            <div style="
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white;
                padding: 15px;
                text-align: center;
                font-family: Arial, sans-serif;
                font-weight: bold;
                font-size: 16px;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 10000;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            ">
                ⚠️ DEMO VERSION - NOT FOR REAL INVESTMENT USE ⚠️
                <br>
                <span style="font-size: 14px; font-weight: normal;">
                    This is a demonstration prototype. All data is simulated. Do not make investment decisions based on this information.
                    <a href="/terms" style="color: white; text-decoration: underline; margin-left: 10px;">View Terms of Service</a>
                </span>
            </div>
            <div style="margin-top: 80px;"></div>
            """
            
            # Insert disclaimer after <body> tag
            html_content = html_content.replace('<body>', '<body>' + disclaimer_banner)
            
            logger.info("✅ Frontend served successfully with disclaimer")
            return HTMLResponse(content=html_content)
        else:
            logger.error(f"❌ index.html not found at {index_path}")
            raise HTTPException(status_code=404, detail="Frontend not found")
    except Exception as e:
        logger.error(f"❌ Error serving frontend: {e}")
        return HTMLResponse(content="""
        <html>
        <head>
            <title>XSEMA - Demo Version</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .warning { background: #ff6b6b; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }
                .info { background: #4ecdc4; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 XSEMA - NFT Analytics Platform</h1>
                
                <div class="warning">
                    <h2>⚠️ DEMO VERSION - NOT FOR REAL INVESTMENT USE ⚠️</h2>
                    <p><strong>This is a demonstration prototype of XSEMA.</strong></p>
                    <ul style="text-align: left; display: inline-block;">
                        <li>All data shown is MOCK/SIMULATED data</li>
                        <li>Do NOT make investment decisions based on this information</li>
                        <li>This is NOT a financial advisory tool</li>
                        <li>Use at your own risk</li>
                    </ul>
                </div>
                
                <div class="info">
                    <h3>ℹ️ Important Information</h3>
                    <p>For real investment advice, consult qualified financial professionals.</p>
                    <p>This demo shows the user interface and features of XSEMA, but all data is simulated.</p>
                    <p><a href="/terms">View Terms of Service</a></p>
                </div>
                
                <h3>🔧 Technical Status</h3>
                <p>Error: """ + str(e) + """</p>
                <p>Please contact support if this issue persists.</p>
                
                <hr>
                <p><em>XSEMA Demo Version - For demonstration purposes only</em></p>
            </div>
        </body>
        </html>
        """)

@app.get("/test")
async def test():
    """Test endpoint with disclaimer"""
    logger.info("🧪 Test endpoint requested")
    return {
        "message": "Test successful", 
        "timestamp": datetime.now().isoformat(),
        "warning": "DEMO VERSION - NOT FOR REAL INVESTMENT USE",
        "disclaimer": "This is a demonstration prototype. All data is simulated.",
        "access": "Public demo - No authentication required"
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint with comprehensive information"""
    logger.info("📊 API status requested")
    return {
        "status": "operational",
        "version": "2.0.0",
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "development"),
        "timestamp": datetime.now().isoformat(),
        "disclaimer": "DEMO VERSION - NOT FOR REAL INVESTMENT USE",
        "access": "Public demo - No authentication required",
        "phase": "Phase 4 - Real Data Integration",
        "features": {
            "portfolio_tracking": "demo_mode",
            "market_data": "simulated",
            "security_analysis": "prototype",
            "analytics": "mock_data",
            "blockchain_integration": "ready",
            "market_data_integration": "ready"
        },
        "warnings": [
            "This is a demonstration prototype",
            "All data is simulated/mock data",
            "Do not make investment decisions based on this information",
            "For real investment advice, consult qualified professionals"
        ]
    }

@app.get("/api/v1/blockchain/status")
async def blockchain_status():
    """Get blockchain network status"""
    logger.info("🔗 Blockchain status requested")
    try:
        from core.blockchain_integration import blockchain_manager
        status = blockchain_manager.get_network_status()
        return {
            "status": "success",
            "data": status,
            "timestamp": datetime.now().isoformat(),
            "message": "Blockchain network status retrieved successfully"
        }
    except Exception as e:
        logger.error(f"❌ Error getting blockchain status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "message": "Failed to retrieve blockchain status"
        }

@app.get("/api/v1/blockchain/test")
async def test_blockchain_connections():
    """Test blockchain connections"""
    logger.info("🧪 Blockchain connection test requested")
    try:
        from core.blockchain_integration import test_blockchain_connections
        results = await test_blockchain_connections()
        return {
            "status": "success",
            "data": results,
            "timestamp": datetime.now().isoformat(),
            "message": "Blockchain connection test completed"
        }
    except Exception as e:
        logger.error(f"❌ Error testing blockchain connections: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "message": "Failed to test blockchain connections"
        }

@app.get("/api/v1/marketplace/status")
async def marketplace_status():
    """Get marketplace integration status"""
    logger.info("📊 Marketplace status requested")
    try:
        from core.market_data_integration import market_data_manager
        status = market_data_manager.get_marketplace_status()
        return {
            "status": "success",
            "data": status,
            "timestamp": datetime.now().isoformat(),
            "message": "Marketplace status retrieved successfully"
        }
    except Exception as e:
        logger.error(f"❌ Error getting marketplace status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "message": "Failed to retrieve marketplace status"
        }

@app.get("/api/v1/market/real-data")
async def get_real_market_data():
    """Get real market data from OpenSea (if API key available)"""
    logger.info("📊 Real market data requested")
    
    try:
        from core.real_market_data import real_market_service
        
        async with real_market_service as service:
            # Check if we have a valid API key
            if not os.getenv("OPENSEA_API_KEY") or os.getenv("OPENSEA_API_KEY") in ["test_key_for_now", "your_opensea_api_key", "demo"]:
                return {
                    "status": "warning",
                    "message": "No valid OpenSea API key configured",
                    "data": {
                        "market_status": "mock_data",
                        "collections": [],
                        "total_volume_24h": 0,
                        "active_collections": 0,
                        "last_updated": datetime.now().isoformat()
                    },
                    "recommendation": "Set OPENSEA_API_KEY environment variable for real data"
                }
            
            # Try to get real data
            market_overview = await service.get_market_overview()
            
            if market_overview and market_overview.get("active_collections", 0) > 0:
                return {
                    "status": "success",
                    "message": "Real market data retrieved successfully",
                    "data": market_overview,
                    "data_source": "opensea"
                }
            else:
                return {
                    "status": "warning",
                    "message": "Could not fetch real data, falling back to mock data",
                    "data": {
                        "market_status": "mock_data",
                        "collections": [],
                        "total_volume_24h": 0,
                        "active_collections": 0,
                        "last_updated": datetime.now().isoformat()
                    },
                    "recommendation": "Check OpenSea API key and network connectivity"
                }
                
    except Exception as e:
        logger.error(f"❌ Error getting real market data: {e}")
        return {
            "status": "error",
            "message": "Failed to retrieve market data",
            "error": str(e)
        }

@app.get("/api/v1/nft/{contract_address}/{token_id}")
async def get_nft_data(contract_address: str, token_id: str, network: str = "ethereum"):
    """Get real NFT data from marketplaces"""
    logger.info(f"🖼️ NFT data requested: {contract_address}:{token_id} on {network}")
    try:
        from core.market_data_integration import market_data_manager
        
        async with market_data_manager as manager:
            nft_data = await manager.get_nft_data(contract_address, token_id, network)
            
            if nft_data:
                return {
                    "status": "success",
                    "data": {
                        "token_id": nft_data.token_id,
                        "contract_address": nft_data.contract_address,
                        "network": nft_data.network,
                        "marketplace": nft_data.marketplace.value,
                        "name": nft_data.name,
                        "description": nft_data.description,
                        "image_url": nft_data.image_url,
                        "current_price": nft_data.current_price,
                        "current_price_currency": nft_data.current_price_currency,
                        "floor_price": nft_data.floor_price,
                        "floor_price_currency": nft_data.floor_price_currency,
                        "collection_name": nft_data.collection_name,
                        "collection_verified": nft_data.collection_verified,
                        "attributes": nft_data.attributes,
                        "last_updated": nft_data.last_updated.isoformat() if nft_data.last_updated else None,
                        "data_source": nft_data.data_source
                    },
                    "timestamp": datetime.now().isoformat(),
                    "message": "NFT data retrieved successfully"
                }
            else:
                return {
                    "status": "not_found",
                    "data": None,
                    "timestamp": datetime.now().isoformat(),
                    "message": "NFT data not available"
                }
                
    except Exception as e:
        logger.error(f"❌ Error getting NFT data: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "message": "Failed to retrieve NFT data"
        }

@app.get("/api/v1/collection/{contract_address}")
async def get_collection_data(contract_address: str, network: str = "ethereum"):
    """Get collection data from marketplaces"""
    logger.info(f"🏛️ Collection data requested: {contract_address} on {network}")
    try:
        from core.market_data_integration import market_data_manager
        
        async with market_data_manager as manager:
            collection_data = await manager.get_collection_data(contract_address, network)
            
            if collection_data:
                return {
                    "status": "success",
                    "data": collection_data,
                    "timestamp": datetime.now().isoformat(),
                    "message": "Collection data retrieved successfully"
                }
            else:
                return {
                    "status": "not_found",
                    "data": None,
                    "timestamp": datetime.now().isoformat(),
                    "message": "Collection data not available"
                }
                
    except Exception as e:
        logger.error(f"❌ Error getting collection data: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "message": "Failed to retrieve collection data"
        }

@app.get("/api/v1/phase4/status")
async def phase4_status():
    """Get Phase 4 implementation status"""
    logger.info("🚀 Phase 4 status requested")
    return {
        "status": "success",
        "data": {
            "phase": "Phase 4 - Real Data Integration",
            "completion": "45%",
            "components": {
                "blockchain_integration": {
                    "status": "ready",
                    "description": "Blockchain API connections ready",
                    "networks": ["ethereum", "polygon", "bsc", "arbitrum", "optimism", "base", "avalanche", "fantom", "solana"]
                },
                "market_data_integration": {
                    "status": "ready",
                    "description": "NFT marketplace data integration ready",
                    "marketplaces": ["opensea", "magic_eden", "blur", "looksrare", "x2y2"]
                },
                "real_time_data": {
                    "status": "in_progress",
                    "description": "WebSocket connections for live updates",
                    "progress": "10%"
                },
                "user_authentication": {
                    "status": "implemented",
                    "description": "Secure user accounts and JWT tokens",
                    "progress": "100%",
                    "features": ["JWT tokens", "bcrypt hashing", "user roles", "mock database"],
                    "endpoints": ["/api/v1/auth/register", "/api/v1/auth/login", "/api/v1/auth/profile", "/api/v1/auth/status"]
                }
            },
            "next_steps": [
                "Test authentication endpoints",
                "Set up PostgreSQL database",
                "Migrate from mock to real database",
                "Implement WebSocket connections",
                "Add portfolio management features"
            ]
        },
        "timestamp": datetime.now().isoformat(),
        "message": "Phase 4 status retrieved successfully"
    }

# =============================================================================
# AUTHENTICATION ENDPOINTS - Phase 4
# =============================================================================

# Security scheme for JWT tokens
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Dependency to get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        user_data = auth_manager.verify_token(token)
        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_data
    except Exception as e:
        logger.error(f"❌ Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/api/v1/auth/register", response_model=Dict[str, Any])
async def user_registration(user_data: UserRegistration):
    """User registration endpoint"""
    try:
        logger.info(f"📝 User registration requested for {user_data.username}")
        
        # Register new user
        new_user = await register_user(user_data)
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed - username or email already exists"
            )
        
        # Convert enums to strings for JSON serialization
        new_user_response = {
            "id": new_user["id"],
            "username": new_user["username"],
            "email": new_user["email"],
            "first_name": new_user["first_name"],
            "last_name": new_user["last_name"],
            "role": new_user["role"].value if hasattr(new_user["role"], 'value') else str(new_user["role"]),
            "status": new_user["status"].value if hasattr(new_user["status"], 'value') else str(new_user["status"]),
            "created_at": new_user["created_at"].isoformat(),
            "is_verified": new_user["is_verified"]
        }
        
        # Create tokens
        access_token = auth_manager.create_access_token(new_user_response)
        refresh_token = auth_manager.create_refresh_token(new_user_response)
        
        logger.info(f"✅ User {user_data.username} registered successfully")
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "data": {
                "user": new_user_response,
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@app.post("/api/v1/auth/login", response_model=Dict[str, Any])
async def user_login(login_data: UserLogin):
    """User login endpoint"""
    try:
        logger.info(f"🔐 User login requested for {login_data.username}")
        
        # Authenticate user
        user = await authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convert enums to strings for JSON serialization
        user_response = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "role": user["role"].value if hasattr(user["role"], 'value') else str(user["role"]),
            "status": user["status"].value if hasattr(user["status"], 'value') else str(user["status"]),
            "last_login": user["last_login"].isoformat() if user["last_login"] else None,
            "is_verified": user["is_verified"]
        }
        
        # Create tokens
        access_token = auth_manager.create_access_token(user_response)
        refresh_token = auth_manager.create_refresh_token(user_response)
        
        logger.info(f"✅ User {login_data.username} logged in successfully")
        
        return {
            "status": "success",
            "message": "Login successful",
            "data": {
                "user": user_response,
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ User login failed: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        logger.error(f"❌ Error details: {str(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during login: {str(e)}"
        )

@app.post("/api/v1/auth/refresh", response_model=Dict[str, Any])
async def refresh_token(refresh_token: str = Query(..., description="Refresh token")):
    """Refresh access token endpoint"""
    try:
        logger.info("🔄 Token refresh requested")
        
        # Refresh access token
        new_access_token = auth_manager.refresh_access_token(refresh_token)
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("✅ Access token refreshed successfully")
        
        return {
            "status": "success",
            "message": "Token refreshed successfully",
            "data": {
                "access_token": new_access_token,
                "token_type": "bearer"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )

@app.get("/api/v1/auth/profile", response_model=Dict[str, Any])
async def get_user_profile(current_user: TokenData = Depends(get_current_user)):
    """Get current user profile"""
    try:
        logger.info(f"👤 Profile requested for user {current_user.username}")
        
        # Get user data from mock database
        from core.authentication import mock_db
        user = mock_db.get_user_by_username(current_user.username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "status": "success",
            "message": "Profile retrieved successfully",
            "data": {
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "role": user["role"].value if hasattr(user["role"], 'value') else str(user["role"]),
                    "status": user["status"].value if hasattr(user["status"], 'value') else str(user["status"]),
                    "created_at": user["created_at"].isoformat(),
                    "last_login": user["last_login"].isoformat() if user["last_login"] else None,
                    "is_verified": user["is_verified"]
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Profile retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during profile retrieval"
        )

@app.get("/api/v1/auth/status", response_model=Dict[str, Any])
async def get_auth_status():
    """Get authentication system status"""
    try:
        logger.info("🔐 Authentication status requested")
        
        return {
            "status": "success",
            "message": "Authentication system status",
            "data": {
                "system": "active",
                "jwt_algorithm": auth_manager.algorithm,
                "access_token_expire_minutes": auth_manager.access_token_expire_minutes,
                "refresh_token_expire_days": auth_manager.refresh_token_expire_days,
                "bcrypt_rounds": auth_manager.bcrypt_rounds,
                "demo_user_available": True,
                "demo_credentials": {
                    "username": "demo",
                    "password": "xsema2025"
                },
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Auth status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during status check"
        )

# Catch-all route for SPA routing
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Handle SPA routing by serving index.html for non-API routes"""
    if full_path.startswith("api/") or full_path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    logger.info(f"🔄 SPA route requested: {full_path}")
    
    try:
        index_path = os.path.join("static", "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Add disclaimer banner (same as root route)
            disclaimer_banner = """
            <div style="
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white;
                padding: 15px;
                text-align: center;
                font-family: Arial, sans-serif;
                font-weight: bold;
                font-size: 16px;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 10000;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            ">
                ⚠️ DEMO VERSION - NOT FOR REAL INVESTMENT USE ⚠️
                <br>
                <span style="font-size: 14px; font-weight: normal;">
                    This is a demonstration prototype. All data is simulated. Do not make investment decisions based on this information.
                    <a href="/terms" style="color: white; text-decoration: underline; margin-left: 10px;">View Terms of Service</a>
                </span>
            </div>
            <div style="margin-top: 80px;"></div>
            """
            
            html_content = html_content.replace('<body>', '<body>' + disclaimer_banner)
            
            logger.info(f"✅ SPA route {full_path} served successfully with disclaimer")
            return HTMLResponse(content=html_content)
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")
    except Exception as e:
        logger.error(f"❌ Error in catch-all route: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Error handlers with logging
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    logger.warning(f"❌ 404 Not Found: {request.url}")
    return HTMLResponse(content="""
    <html>
    <head><title>Page Not Found - XSEMA Demo</title></head>
    <body style="font-family: Arial, sans-serif; text-align: center; margin: 50px;">
        <h1>❌ Page Not Found</h1>
        <p>The requested page could not be found.</p>
        <div style="background: #ff6b6b; color: white; padding: 20px; margin: 20px; border-radius: 8px;">
            <strong>⚠️ DEMO VERSION - NOT FOR REAL INVESTMENT USE ⚠️</strong>
        </div>
        <p><a href="/">Return to Home</a></p>
        <p><a href="/terms">View Terms of Service</a></p>
    </body>
    </html>
    """, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    logger.error(f"❌ 500 Internal Server Error: {request.url} - {exc}")
    return HTMLResponse(content="""
    <html>
    <head><title>Server Error - XSEMA Demo</title></head>
    <body style="font-family: Arial, sans-serif; text-align: center; margin: 50px;">
        <h1>❌ Server Error</h1>
        <p>Something went wrong on our end. Please try again later.</p>
        <div style="background: #ff6b6b; color: white; padding: 20px; margin: 20px; border-radius: 8px;">
            <strong>⚠️ DEMO VERSION - NOT FOR REAL INVESTMENT USE ⚠️</strong>
        </div>
        <p><a href="/">Return to Home</a></p>
        <p><a href="/terms">View Terms of Service</a></p>
    </body>
    </html>
    """, status_code=500)

# Main execution block for local development
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting XSEMA server locally...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
