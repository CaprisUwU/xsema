"""
Configuration management for XSEMA application.

This module handles environment variables, configuration validation,
and provides a centralized settings interface.
"""

import os
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    APP_NAME: str = "XSEMA"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment (development/production)")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of worker processes")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator('PORT')
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate and override port with environment variable if set."""
        env_port = os.environ.get("PORT")
        if env_port:
            try:
                return int(env_port)
            except ValueError:
                pass
        return v
    
    # Database settings
    DATABASE_URL: Optional[str] = Field(default=None, description="Database connection URL")
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow")
    
    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    
    # Security settings
    SECRET_KEY: str = Field(default="your-secret-key-here", description="Secret key for JWT")
    API_KEY_HEADER: str = Field(default="X-API-Key", description="API key header name")
    API_KEY_REQUIRED: bool = Field(default=True, description="Require API key for endpoints")
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_DEFAULT: int = Field(default=100, description="Default rate limit per minute")
    RATE_LIMIT_BATCH: int = Field(default=10, description="Batch operation rate limit per minute")
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow CORS credentials")
    
    # Blockchain settings
    ETHEREUM_RPC_URL: Optional[str] = Field(default=None, description="Ethereum RPC URL")
    POLYGON_RPC_URL: Optional[str] = Field(default=None, description="Polygon RPC URL")
    BSC_RPC_URL: Optional[str] = Field(default=None, description="BSC RPC URL")
    ARBITRUM_RPC_URL: Optional[str] = Field(default=None, description="Arbitrum RPC URL")
    OPTIMISM_RPC_URL: Optional[str] = Field(default=None, description="Optimism RPC URL")
    BASE_RPC_URL: Optional[str] = Field(default=None, description="Base RPC URL")
    AVALANCHE_RPC_URL: Optional[str] = Field(default=None, description="Avalanche RPC URL")
    FANTOM_RPC_URL: Optional[str] = Field(default=None, description="Fantom RPC URL")
    SOLANA_RPC_URL: Optional[str] = Field(default=None, description="Solana RPC URL")
    
    # ML Model settings
    MODEL_PATH: str = Field(default="models", description="Path to ML models")
    MODEL_VERSION: str = Field(default="latest", description="Active model version")
    MODEL_RETRAINING_ENABLED: bool = Field(default=True, description="Enable automatic model retraining")
    MODEL_RETRAINING_SCHEDULE: str = Field(default="weekly", description="Model retraining schedule")
    
    # Feature flags
    ENABLE_WEBHOOKS: bool = Field(default=False, description="Enable webhook notifications")
    ENABLE_ANALYTICS: bool = Field(default=True, description="Enable analytics collection")
    ENABLE_MONITORING: bool = Field(default=True, description="Enable system monitoring")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

# Global settings instance
settings = Settings()

# Convenience functions
def get_setting(key: str, default=None):
    """Get a setting value."""
    return getattr(settings, key, default)

def is_production() -> bool:
    """Check if running in production."""
    return settings.ENVIRONMENT.lower() == "production"

def is_development() -> bool:
    """Check if running in development."""
    return settings.ENVIRONMENT.lower() == "development"

def is_debug() -> bool:
    """Check if debug mode is enabled."""
    return settings.DEBUG or is_development()

# Environment-specific overrides
if is_production():
    # Production overrides
    settings.DEBUG = False
    settings.LOG_LEVEL = "INFO"
    settings.CORS_ORIGINS = []  # Restrict in production
    
elif is_development():
    # Development overrides
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"
    settings.CORS_ORIGINS = ["*"]  # Allow all in development

# Validate critical settings
if is_production():
    if settings.SECRET_KEY == "your-secret-key-here":
        raise ValueError("SECRET_KEY must be set in production")
    
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL must be set in production")

# Export settings
__all__ = ["settings", "get_setting", "is_production", "is_development", "is_debug"]
