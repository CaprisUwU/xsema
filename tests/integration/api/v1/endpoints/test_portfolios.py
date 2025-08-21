"""
Integration tests for Portfolio endpoints.
"""
import os
import sys
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from fastapi import status
from fastapi.testclient import TestClient

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import the application and models
from portfolio.main import app
from portfolio.models.portfolio import Portfolio, PortfolioInsights, Wallet, Asset, AssetType

# Test data
TEST_USER_ID = "test-user-1"
TEST_PORTFOLIO_ID = "test-portfolio-1"

# Create a test client
@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.mark.asyncio
async def test_create_portfolio(test_client, mock_portfolio_service):
    """Test creating a new portfolio."""
    # Setup
    portfolio_data = {
        "name": "Test Portfolio",
        "description": "A test portfolio"
    }
    
    created_portfolio = {
        "id": TEST_PORTFOLIO_ID,
        "user_id": TEST_USER_ID,
        "name": portfolio_data["name"],
        "description": portfolio_data["description"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    mock_portfolio_service.create_portfolio.return_value = Portfolio(**created_portfolio)
    
    # Execute
    response = test_client.post(
        "/api/v1/portfolio/portfolios/",
        json=portfolio_data,
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    # Verify
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == TEST_PORTFOLIO_ID
    assert data["name"] == portfolio_data["name"]
    assert data["description"] == portfolio_data["description"]
    mock_portfolio_service.create_portfolio.assert_called_once()

@pytest.mark.asyncio
async def test_get_portfolio(test_client, mock_portfolio_service, sample_portfolio):
    """Test getting a portfolio by ID."""
    # Setup
    mock_portfolio_service.get_portfolio.return_value = sample_portfolio
    
    # Execute
    response = test_client.get(
        f"/api/v1/portfolio/portfolios/{sample_portfolio['id']}",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    # Verify
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_portfolio["id"]
    assert data["name"] == sample_portfolio["name"]
    mock_portfolio_service.get_portfolio.assert_called_once_with(
        user_id=TEST_USER_ID,
        portfolio_id=sample_portfolio['id']
    )

@pytest.mark.asyncio
async def test_list_portfolios(test_client, mock_portfolio_service, sample_portfolio):
    """Test listing portfolios for a user."""
    # Setup
    mock_portfolio_service.list_portfolios.return_value = [Portfolio(**sample_portfolio)]
    
    # Execute
    response = test_client.get(
        "/api/v1/portfolio/portfolios/",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    # Verify
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == sample_portfolio["id"]
    mock_portfolio_service.list_portfolios.assert_called_once_with(
        user_id=TEST_USER_ID,
        skip=0,
        limit=100
    )

@pytest.mark.asyncio
async def test_update_portfolio(test_client, mock_portfolio_service, sample_portfolio):
    """Test updating a portfolio."""
    # Setup
    update_data = {
        "name": "Updated Portfolio Name",
        "description": "Updated description"
    }
    
    updated_portfolio = {**sample_portfolio, **update_data}
    mock_portfolio_service.update_portfolio.return_value = Portfolio(**updated_portfolio)
    
    # Execute
    response = test_client.put(
        f"/api/v1/portfolio/portfolios/{sample_portfolio['id']}",
        json=update_data,
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    # Verify
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    mock_portfolio_service.update_portfolio.assert_called_once()

@pytest.mark.asyncio
async def test_delete_portfolio(test_client, mock_portfolio_service, sample_portfolio):
    """Test deleting a portfolio."""
    # Setup
    mock_portfolio_service.delete_portfolio.return_value = True
    
    # Execute
    response = test_client.delete(
        f"/api/v1/portfolio/portfolios/{sample_portfolio['id']}",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    # Verify
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_portfolio_service.delete_portfolio.assert_called_once_with(
        user_id=TEST_USER_ID,
        portfolio_id=sample_portfolio['id']
    )

@pytest.mark.asyncio
async def test_get_portfolio_insights(test_client, mock_portfolio_service, mock_analytics_service, sample_portfolio):
    """Test getting portfolio insights."""
    # Setup
    mock_portfolio_service.get_portfolio.return_value = Portfolio(**sample_portfolio)
    
    insights_data = {
        "portfolio_id": sample_portfolio['id'],
        "performance": {
            "total_return_percent": 15.5,
            "volatility": 0.25,
            "sharpe_ratio": 1.8
        },
        "risk_assessment": {
            "concentration_risk": 65,
            "liquidity_risk": 30,
            "market_risk": 45
        },
        "opportunities": [],
        "warnings": [],
        "market_conditions": {
            "market_sentiment": "bullish",
            "market_volatility": "medium"
        },
        "generated_at": datetime.utcnow().isoformat()
    }
    
    mock_analytics_service.get_portfolio_insights.return_value = PortfolioInsights(**insights_data)
    
    # Execute
    response = test_client.get(
        f"/api/v1/portfolio/portfolios/{sample_portfolio['id']}/insights",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    # Verify
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["portfolio_id"] == sample_portfolio['id']
    assert "performance" in data
    assert "risk_assessment" in data
    assert "opportunities" in data
    assert "warnings" in data
    assert "market_conditions" in data
    
    mock_portfolio_service.get_portfolio.assert_called_once_with(
        user_id=TEST_USER_ID,
        portfolio_id=sample_portfolio['id']
    )
    mock_analytics_service.get_portfolio_insights.assert_called_once()

@pytest.mark.asyncio
async def test_get_portfolio_performance(test_client, mock_portfolio_service, mock_analytics_service, sample_portfolio):
    """Test getting portfolio performance."""
    # Setup
    mock_portfolio_service.get_portfolio.return_value = Portfolio(**sample_portfolio)
    
    performance_data = {
        "time_series": [
            {"timestamp": 1672444800, "value": 10000},
            {"timestamp": 1672531200, "value": 10200}
        ],
        "metrics": {
            "total_return_percent": 2.0,
            "volatility": 0.15,
            "sharpe_ratio": 1.5,
            "start_value": 10000,
            "end_value": 10200,
            "time_range": "7d"
        }
    }
    
    mock_analytics_service.get_portfolio_performance.return_value = performance_data
    
    # Execute
    response = test_client.get(
        f"/api/v1/portfolio/portfolios/{sample_portfolio['id']}/performance?time_range=7d",
        headers={"X-User-ID": TEST_USER_ID}
    )
    
    # Verify
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "time_series" in data
    assert "metrics" in data
    assert data["metrics"]["total_return_percent"] == 2.0
    
    mock_portfolio_service.get_portfolio.assert_called_once_with(
        user_id=TEST_USER_ID,
        portfolio_id=sample_portfolio['id']
    )
    mock_analytics_service.get_portfolio_performance.assert_called_once()
