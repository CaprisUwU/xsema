"""
Market API v1 Endpoints

Market intelligence API endpoints.
"""
from fastapi import APIRouter

# Create main market router
router = APIRouter()

# Import and include all market endpoint modules
try:
    from .markets import router as markets_router
    from .collections import router as collections_router  
    from .ranking import router as ranking_router
    
    # Include market routers
    router.include_router(markets_router, prefix="/markets", tags=["markets"])
    router.include_router(collections_router, prefix="/collections", tags=["collections"])
    router.include_router(ranking_router, prefix="/ranking", tags=["ranking"])
    
except ImportError as e:
    print(f"Warning: Could not import some market endpoints: {e}")

__all__ = ["router"]