"""
Logging utilities for the NFT Analytics API.

This module provides a configured logger instance that can be used throughout the application.
"""
import logging
import sys
from typing import Optional

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Create and configure a logger with the given name.
    
    Args:
        name: The name of the logger. If None, uses the root logger.
    
    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name or "nft_analytics")
    return logger

def setup_logger(name: Optional[str] = None, log_level: Optional[str] = None) -> logging.Logger:
    """
    Create and configure a logger with the given name and log level.
    
    Args:
        name: The name of the logger. If None, uses the root logger.
        log_level: The log level to set. If None, uses INFO level.
    
    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name or "nft_analytics")
    if log_level:
        logger.setLevel(getattr(logging, log_level, logging.INFO))
    return logger

# Default logger instance
default_logger = get_logger()
