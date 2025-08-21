"""
Logging configuration for the Portfolio Management API.

This module provides a configured logger instance that can be used throughout the application.
"""
import logging
import sys
from typing import Optional

from core.config import settings

# Configure the root logger
logging.basicConfig(
    level=logging.getLevelName(settings.LOG_LEVEL) if settings.LOG_LEVEL else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create a logger instance
logger = logging.getLogger("portfolio")

def setup_logger(name: Optional[str] = None, log_level: Optional[str] = None) -> logging.Logger:
    """
    Create and configure a logger with the given name and log level.
    
    Args:
        name: The name of the logger. If None, uses the root logger.
        log_level: The log level to set. If None, uses the level from settings.
    
    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name or "portfolio")
    if log_level:
        logger.setLevel(getattr(logging, log_level, logging.INFO))
    return logger

# Set default logger level based on settings
logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
