"""
Portfolio Management Module

This module provides comprehensive tools for tracking, analyzing, and managing
NFT and token assets across multiple blockchains, powered by AI-driven insights.
"""
__version__ = "0.1.0"

# Import core components to make them available at package level
from .models.portfolio import (
    Asset,
    Wallet,
    Portfolio,
    Recommendation,
    PortfolioInsights,
    AssetType,
    RecommendationType
)

# Import services from the services package to avoid circular imports
from .services import (
    recommendation_service,
    analytics_service,
    balance_service,
    nft_service,
    price_service
)

# Import API router
from .api.endpoints import router as portfolio_router

__all__ = [
    # Models
    'Asset',
    'Wallet',
    'Portfolio',
    'Recommendation',
    'PortfolioInsights',
    'AssetType',
    'RecommendationType',
    
    # Services
    'recommendation_service',
    'analytics_service',
    'balance_service',
    'nft_service',
    'price_service',
    
    # API
    'portfolio_router'
]
