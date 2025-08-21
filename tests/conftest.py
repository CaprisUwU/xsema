"""
Test configuration and fixtures for the Portfolio Management API.
"""
import asyncio
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

# Import the FastAPI app
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from portfolio.main import app

# Create a test client
@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

# Mock services
@pytest.fixture
def mock_portfolio_service():
    """Mock the portfolio service."""
    with patch('portfolio.services.portfolio_service.portfolio_service') as mock:
        yield mock

@pytest.fixture
def mock_balance_service():
    """Mock the balance service."""
    with patch('portfolio.services.balance_service.balance_service') as mock:
        yield mock

@pytest.fixture
def mock_nft_service():
    """Mock the NFT service."""
    with patch('portfolio.services.nft_service.nft_service') as mock:
        yield mock

@pytest.fixture
def mock_price_service():
    """Mock the price service."""
    with patch('portfolio.services.price_service.price_service') as mock:
        yield mock

@pytest.fixture
def mock_analytics_service():
    """Mock the analytics service."""
    with patch('portfolio.services.analytics_service.analytics_service') as mock:
        yield mock

# Test data fixtures
@pytest.fixture
def sample_portfolio():
    """Sample portfolio data for testing."""
    return {
        "id": "test-portfolio-1",
        "name": "Test Portfolio",
        "description": "A test portfolio",
        "owner_id": "test-user-1",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_wallet():
    """Sample wallet data for testing."""
    return {
        "id": "test-wallet-1",
        "address": "0x1234567890abcdef1234567890abcdef12345678",
        "name": "Test Wallet",
        "description": "A test wallet",
        "owner_id": "test-user-1",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_asset():
    """Sample asset data for testing."""
    return {
        "id": "test-asset-1",
        "symbol": "TEST",
        "name": "Test Token",
        "decimals": 18,
        "contract_address": "0xabcdef1234567890abcdef1234567890abcdef12",
        "type": "ERC20",
        "logo_url": "https://example.com/logo.png"
    }

@pytest.fixture
def sample_nft():
    """Sample NFT data for testing."""
    return {
        "id": "test-asset-1",
        "wallet_id": "test-wallet-1",
        "asset_id": "ethereum",
        "symbol": "ETH",
        "balance": 1.5,
        "type": "crypto",
        "metadata": {"decimals": 18},
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_nft_collection():
    """Sample NFT collection data for testing."""
    return {
        "id": "test-collection-1",
        "name": "Test Collection",
        "symbol": "TST",
        "contract_address": "0xabcdef1234567890abcdef1234567890abcdef12",
        "type": "ERC721",
        "name": "Test NFT Collection",
        "symbol": "TNFT",
        "description": "A test NFT collection",
        "image_url": "https://example.com/image.jpg",
        "chain": "ethereum",
        "total_supply": 10000
    }
