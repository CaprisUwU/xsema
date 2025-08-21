"""
Portfolio Configuration

Portfolio-specific configuration settings and environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class PortfolioSettings(BaseSettings):
    """Portfolio-specific configuration settings."""
    
    # Database settings
    portfolio_db_url: str = "sqlite:///./portfolio.db"
    portfolio_db_echo: bool = False
    
    # Cache settings
    portfolio_cache_ttl: int = 3600  # 1 hour
    portfolio_cache_maxsize: int = 1000
    
    # API settings
    portfolio_api_prefix: str = "/api/v1"
    portfolio_pagination_limit: int = 100
    
    # External services
    price_service_url: Optional[str] = None
    nft_metadata_service_url: Optional[str] = None
    
    # Blockchain RPC URLs
    ethereum_rpc_url: str = "https://mainnet.infura.io/v3/your-project-id"
    polygon_rpc_url: str = "https://polygon-mainnet.infura.io/v3/your-project-id"
    bsc_rpc_url: str = "https://bsc-dataseed1.binance.org/"
    
    # Alchemy API URLs (required by portfolio services)
    alchemy_eth_http_url: str = "https://eth-mainnet.alchemyapi.io/v2/your-key"
    alchemy_polygon_http_url: str = "https://polygon-mainnet.alchemyapi.io/v2/your-key"
    alchemy_arbitrum_http_url: str = "https://arb-mainnet.alchemyapi.io/v2/your-key"
    alchemy_optimism_http_url: str = "https://opt-mainnet.alchemyapi.io/v2/your-key"
    
    # External API endpoints
    opensea_api_url: str = "https://api.opensea.io/api/v1"
    moralis_api_url: str = "https://deep-index.moralis.io/api/v2"
    
    # API Keys (environment variables)
    alchemy_api_key: Optional[str] = None
    opensea_api_key: Optional[str] = None
    moralis_api_key: Optional[str] = None
    
    # Make attribute access case-insensitive for backward compatibility
    @property
    def ETHEREUM_RPC_URL(self) -> str:
        return self.ethereum_rpc_url
    
    @property 
    def POLYGON_RPC_URL(self) -> str:
        return self.polygon_rpc_url
        
    @property
    def BSC_RPC_URL(self) -> str:
        return self.bsc_rpc_url
    
    @property
    def ALCHEMY_ETH_HTTP_URL(self) -> str:
        return self.alchemy_eth_http_url
        
    @property
    def ALCHEMY_POLYGON_HTTP_URL(self) -> str:
        return self.alchemy_polygon_http_url
        
    @property
    def OPENSEA_API_URL(self) -> str:
        return self.opensea_api_url
        
    @property
    def MORALIS_API_URL(self) -> str:
        return self.moralis_api_url
        
    @property
    def ALCHEMY_ARBITRUM_HTTP_URL(self) -> str:
        return self.alchemy_arbitrum_http_url
        
    @property
    def ALCHEMY_OPTIMISM_HTTP_URL(self) -> str:
        return self.alchemy_optimism_http_url
    
    # Portfolio-specific features
    enable_profit_loss_tracking: bool = True
    enable_tax_reporting: bool = False
    enable_portfolio_recommendations: bool = True
    
    model_config = {
        "env_file": ".env",
        "env_prefix": "PORTFOLIO_",
        "extra": "ignore"  # Ignore extra environment variables
    }


# Global settings instance
settings = PortfolioSettings()
