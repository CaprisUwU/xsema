"""
Portfolio Services package.

This package contains the service layer for the Portfolio Management system.
"""

# Import services to make them available at the package level
try:
    from .portfolio_service import PortfolioService, portfolio_service
    portfolio_service = portfolio_service  # Already instantiated in the module
except ImportError as e:
    print(f"Warning: Could not import portfolio_service: {e}")
    portfolio_service = None
    PortfolioService = None

# Re-enable services now that dependencies are fixed
try:
    from .analytics_service import AnalyticsService
    analytics_service = AnalyticsService()
except ImportError as e:
    print(f"Warning: Could not import analytics_service: {e}")
    analytics_service = None

try:
    from .balance_service import BalanceService
    balance_service = BalanceService()
except ImportError as e:
    print(f"Warning: Could not import balance_service: {e}")
    balance_service = None
    
try:
    from .nft_service import NFTService, nft_service
    # nft_service already instantiated in module
except ImportError as e:
    print(f"Warning: Could not import nft_service: {e}")
    nft_service = None
    
try:
    from .price_service import PriceService
    price_service = PriceService()
except ImportError as e:
    print(f"Warning: Could not import price_service: {e}")
    price_service = None
    
try:
    from .recommendation_service import RecommendationService
    recommendation_service = RecommendationService()
except ImportError as e:
    print(f"Warning: Could not import recommendation_service: {e}")
    recommendation_service = None

__all__ = [
    'analytics_service',
    'balance_service',
    'nft_service',
    'price_service',
    'recommendation_service',
    'portfolio_service',
    'AnalyticsService',
    'BalanceService',
    'NFTService',
    'PriceService',
    'PortfolioService',
    'RecommendationService'
]
