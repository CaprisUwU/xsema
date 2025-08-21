"""
Test Configuration

This module provides test configuration for the WebSocket client tests.
"""
from pydantic import BaseModel

class TestSettings(BaseModel):
    """Test settings for the WebSocket client."""
    NFT_WS_URL: str = "ws://localhost:8001/ws"  # Using port 8001 for testing
    DEBUG: bool = True

# Create test settings instance
test_settings = TestSettings()
