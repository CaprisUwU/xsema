"""
Portfolio API Endpoints

This module contains all API endpoints for the Portfolio Management module.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

# Create main router without any prefix (prefix will be added in main.py)
router = APIRouter()

# Import all endpoint modules to register their routes
from .portfolios import router as portfolios_router
from .wallets import router as wallets_router
from .assets import router as assets_router
from .nfts_flat import router as nfts_router
from .analytics import router as analytics_router

# Include all routers under the main router with appropriate prefixes
router.include_router(portfolios_router, prefix="/portfolios", tags=["portfolios"])

# Update wallet router to be included under portfolios
router.include_router(wallets_router, prefix="/portfolios/{portfolio_id}/wallets", tags=["wallets"])

# Update assets router to be included under portfolios/wallets
router.include_router(assets_router, prefix="/portfolios/{portfolio_id}/wallets/{wallet_id}/assets", tags=["assets"])

# Include the NFT router with the portfolio prefix
# The router's own prefix will be appended to the router's prefix
router.include_router(nfts_router)

# Include analytics router
router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

# Health check endpoint
@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint"
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify the API is running
    """
    return {"status": "ok", "message": "API is running"}
