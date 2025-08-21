"""
Configuration settings for the application.

This module provides a single source of truth for application settings.
It re-exports the Settings class from portfolio.core.config to maintain
backward compatibility with existing code.
"""
from portfolio.core.config import Settings, settings as app_settings

# Re-export the settings instance for backward compatibility
settings = app_settings

# Lazy load the app to avoid circular imports
def get_app():
    """Get the FastAPI application instance."""
    import main
    return main.app
