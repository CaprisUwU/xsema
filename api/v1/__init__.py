"""
XSema API v1

This module provides the main FastAPI router for XSema API.
"""
import sys
from pathlib import Path
from fastapi import APIRouter

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import endpoint routers
from .endpoints import nfts, collections, wallets, markets, security, network_health

# Import portfolio endpoints
from portfolio.api.v1.endpoints import router as portfolio_router

api_router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
api_router.include_router(nfts.router, prefix="/nfts", tags=["NFTs"])
api_router.include_router(collections.router, prefix="/collections", tags=["Collections"])
api_router.include_router(wallets.router, prefix="/wallets", tags=["Wallets"])
api_router.include_router(markets.router, prefix="/markets", tags=["Markets"])
api_router.include_router(security.router, prefix="/security", tags=["Security"])
api_router.include_router(network_health.router, tags=["Network Health"])

# Include portfolio router with the correct prefix
api_router.include_router(portfolio_router, prefix="/portfolios", tags=["Portfolios"])
