"""
Portfolio API package.

This package contains the API endpoints and related functionality for the Portfolio Management system.
"""

# Import key components to make them available at the package level
from .endpoints import router as api_router

__all__ = ['api_router']
