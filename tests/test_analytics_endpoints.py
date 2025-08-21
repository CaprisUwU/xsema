"""
Tests for Portfolio Analytics API endpoints
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from main import app
from portfolio.models.portfolio import Portfolio, PortfolioInsights, Asset, AssetPerformance, Recommendation, RecommendationType

# Helper function to get current UTC time with timezone info
def utc_now():
    return datetime.now(timezone.utc)

client = TestClient(app)

# Test data
TEST_PORTFOLIO = Portfolio(
    id="test-portfolio-1",
    name="Test Portfolio",
    description="Test portfolio for unit testing",
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
    user_id="test-user-1"
)

def create_test_insights():
    now = utc_now()
    return PortfolioInsights(
        portfolio_id="test-portfolio-1",
        risk_assessment={
            "score": 0.65,
            "level": "Moderate",
            "factors": ["Diversified assets", "Balanced risk profile"],
            "concentration_risk": 0.7,
            "liquidity_risk": 0.3,
            "market_risk": 0.5,
            "metrics": {
                "value_at_risk_95": -0.05,
                "expected_shortfall_95": -0.07,
                "max_drawdown": -0.1,
                "beta": 1.1
            }
        },
        opportunities=[
            Recommendation(
                type=RecommendationType.BUY,
                asset_id="asset-1",
                current_value=100.0,
                suggested_value=150.0,
                confidence=0.85,
                reasons=["Undervalued based on recent market trends"],
                priority=1,
                expires_at=now + timedelta(days=7)
            )
        ],
        warnings=[
            Recommendation(
                type=RecommendationType.RISK,
                asset_id="asset-2",
                current_value=5000.0,
                suggested_value=4000.0,
                confidence=0.9,
                reasons=["High concentration in single asset"],
                priority=1,
                expires_at=now + timedelta(days=1)
            )
        ],
        market_conditions={
            "sentiment": "bullish",
            "trend": "slightly_bullish",
            "volatility": "medium",
            "market_trend": "up",
            "fear_greed_index": 65,
            "dominance": {
                "btc": 42.5,
                "eth": 18.3,
                "stablecoins": 12.1,
                "other": 27.1
            }
        },
        generated_at=now
    )

TEST_INSIGHTS = create_test_insights()

# Mock authentication
@pytest.fixture
def mock_auth():
    with patch("portfolio.api.v1.endpoints.analytics.get_current_user") as mock_auth:
        mock_auth.return_value = {"id": "test-user-1", "email": "test@example.com"}
        yield mock_auth

# Mock portfolio service
@pytest.fixture
def mock_portfolio_service():
    with patch("portfolio.api.v1.endpoints.analytics.portfolio_service") as mock_svc:
        mock_svc.get_portfolio.return_value = TEST_PORTFOLIO
        yield mock_svc

# Mock analytics service
@pytest.fixture
def mock_analytics_service():
    with patch("portfolio.api.v1.endpoints.analytics.analytics_service") as mock_svc:
        mock_svc.get_portfolio_insights.return_value = TEST_INSIGHTS
        mock_svc.get_portfolio_performance.return_value = {
            "total_return": 1234.56,
            "daily_returns": [0.01, -0.02, 0.03],
            "volatility": 0.0567,
            "sharpe_ratio": 1.23
        }
        mock_svc.get_portfolio_risk.return_value = {
            "var_95": -0.123,
            "cvar_95": -0.156,
            "max_drawdown": -0.234,
            "beta": 1.05
        }
        mock_svc.get_portfolio_diversification.return_value = {
            "hhi": 0.45,
            "asset_distribution": {"ETH": 60.0, "NFTs": 40.0},
            "category_distribution": {"Art": 30.0, "Collectibles": 70.0}
        }
        mock_svc.generate_recommendations.return_value = [
            Recommendation(
                type="rebalance",
                asset_id="portfolio-rebalance",
                confidence=0.85,
                priority=1,
                reasons=["Consider diversifying your portfolio", "Add more asset classes"]
            )
        ]
        yield mock_svc

def test_get_portfolio_insights(mock_auth, mock_portfolio_service, mock_analytics_service):
    """Test getting portfolio insights"""
    # Setup mock return value
    test_insights = create_test_insights()
    mock_analytics_service.get_portfolio_insights.return_value = test_insights
    
    response = client.get(
        "/api/v1/portfolio/analytics/portfolios/test-portfolio-1/insights?time_range=30d",
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check top-level fields
    assert data["portfolio_id"] == "test-portfolio-1"
    assert "risk_assessment" in data
    assert "opportunities" in data
    assert "warnings" in data
    assert "market_conditions" in data
    assert "generated_at" in data
    
    # Check risk assessment
    risk_assessment = data["risk_assessment"]
    assert "score" in risk_assessment
    assert "level" in risk_assessment
    assert "factors" in risk_assessment
    assert "metrics" in risk_assessment
    assert "concentration_risk" in risk_assessment
    assert "liquidity_risk" in risk_assessment
    assert "market_risk" in risk_assessment
    
    # Check metrics in risk assessment
    metrics = risk_assessment["metrics"]
    assert "value_at_risk_95" in metrics
    assert "expected_shortfall_95" in metrics
    assert "max_drawdown" in metrics
    assert "beta" in metrics
    
    # Check opportunities
    assert isinstance(data["opportunities"], list)
    if data["opportunities"]:
        opp = data["opportunities"][0]
        assert opp["type"] == "buy"
        assert opp["asset_id"] == "asset-1"
        assert opp["current_value"] == 100.0
        assert opp["suggested_value"] == 150.0
        assert opp["confidence"] == 0.85
        assert "Undervalued" in "".join(opp["reasons"])
        assert opp["priority"] == 1
        assert "expires_at" in opp
    
    # Check warnings
    assert isinstance(data["warnings"], list)
    if data["warnings"]:
        warning = data["warnings"][0]
        assert warning["type"] == "risk"
        assert warning["asset_id"] == "asset-2"
    
    # Check market conditions
    market_conditions = data["market_conditions"]
    assert "sentiment" in market_conditions
    assert "trend" in market_conditions
    assert "volatility" in market_conditions
    assert "market_trend" in market_conditions
    assert "fear_greed_index" in market_conditions
    assert "dominance" in market_conditions
    
    # Check dominance in market conditions
    dominance = market_conditions["dominance"]
    assert "btc" in dominance
    assert "eth" in dominance
    assert "stablecoins" in dominance
    assert "other" in dominance
    
    # Verify the service was called with correct parameters
    mock_portfolio_service.get_portfolio.assert_called_once_with("test-portfolio-1", "test-user-1")
    mock_analytics_service.get_portfolio_insights.assert_called_once()

def test_get_portfolio_performance(mock_auth, mock_portfolio_service, mock_analytics_service):
    """Test getting portfolio performance metrics"""
    # Setup mock return value
    mock_analytics_service.get_portfolio_performance.return_value = {
        'time_series': [
            {'timestamp': 1234567890, 'value': 10000.0},
            {'timestamp': 1234567891, 'value': 10100.0}
        ],
        'metrics': {
            'total_return_percent': 1.0,
            'volatility': 0.1,
            'sharpe_ratio': 1.2,
            'start_value': 10000.0,
            'end_value': 10100.0,
            'time_range': '30d'
        }
    }
    
    response = client.get(
        "/api/v1/portfolio/analytics/portfolios/test-portfolio-1/performance?time_range=30d",
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check the response structure
    assert "time_series" in data
    assert "metrics" in data
    assert isinstance(data["time_series"], list)
    assert isinstance(data["metrics"], dict)
    assert "total_return_percent" in data["metrics"]
    assert "volatility" in data["metrics"]
    assert "sharpe_ratio" in data["metrics"]
    
    # Verify the service was called with correct parameters
    mock_portfolio_service.get_portfolio.assert_called_once_with("test-portfolio-1", "test-user-1")
    mock_analytics_service.get_portfolio_performance.assert_called_once_with(TEST_PORTFOLIO, "30d")

def test_get_portfolio_risk(mock_auth, mock_portfolio_service, mock_analytics_service):
    """Test getting portfolio risk metrics"""
    # Setup mock return value
    mock_analytics_service.get_portfolio_risk.return_value = {
        'concentration_risk': 0.7,
        'liquidity_risk': 0.3,
        'market_risk': 0.5,
        'overall_risk': 0.5,
        'metrics': {
            'value_at_risk_95': -0.05,
            'expected_shortfall_95': -0.07,
            'max_drawdown': -0.1,
            'beta': 1.1
        }
    }
    
    response = client.get(
        "/api/v1/portfolio/analytics/portfolios/test-portfolio-1/risk?time_range=30d",
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check the response structure
    assert "overall_risk" in data
    assert "metrics" in data
    assert "value_at_risk_95" in data["metrics"]
    assert "expected_shortfall_95" in data["metrics"]
    assert "max_drawdown" in data["metrics"]
    assert "beta" in data["metrics"]
    
    # Verify the service was called with correct parameters
    mock_portfolio_service.get_portfolio.assert_called_once_with("test-portfolio-1", "test-user-1")
    mock_analytics_service.get_portfolio_risk.assert_called_once_with(TEST_PORTFOLIO, "30d")

def test_get_portfolio_diversification(mock_auth, mock_portfolio_service, mock_analytics_service):
    """Test getting portfolio diversification metrics"""
    # Setup mock return value
    mock_analytics_service.get_portfolio_diversification.return_value = {
        'hhi': 0.35,
        'asset_distribution': {
            'crypto': 60.0,
            'nfts': 30.0,
            'stablecoins': 10.0
        },
        'category_distribution': {
            'art': 40.0,
            'collectibles': 35.0,
            'gaming': 25.0
        },
        'metrics': {
            'effective_num_assets': 8.2,
            'concentration_risk': 'moderate',
            'diversification_score': 72.5
        }
    }
    
    response = client.get(
        "/api/v1/portfolio/analytics/portfolios/test-portfolio-1/diversification",
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check the response structure
    assert "hhi" in data
    assert "asset_distribution" in data
    assert "category_distribution" in data
    assert "metrics" in data
    assert isinstance(data["asset_distribution"], dict)
    assert isinstance(data["category_distribution"], dict)
    
    # Verify the service was called with correct parameters
    mock_portfolio_service.get_portfolio.assert_called_once_with("test-portfolio-1", "test-user-1")
    mock_analytics_service.get_portfolio_diversification.assert_called_once_with(TEST_PORTFOLIO)

def test_get_portfolio_recommendations(mock_auth, mock_portfolio_service, mock_analytics_service):
    """Test getting portfolio recommendations"""
    # Setup mock return value
    now = utc_now()
    mock_analytics_service.generate_recommendations.return_value = [
        {
            'type': 'diversification',
            'asset_id': 'asset-1',
            'current_value': 5000.0,
            'suggested_value': 3000.0,
            'confidence': 0.85,
            'reasons': ['High concentration in single asset'],
            'priority': 1,
            'expires_at': now + timedelta(days=7)
        },
        {
            'type': 'buy',
            'asset_id': 'asset-2',
            'current_value': 1000.0,
            'suggested_value': 2000.0,
            'confidence': 0.75,
            'reasons': ['Undervalued based on metrics'],
            'priority': 2,
            'expires_at': now + timedelta(days=14)
        }
    ]
    
    response = client.get(
        "/api/v1/portfolio/analytics/portfolios/test-portfolio-1/recommendations",
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check the response structure
    assert isinstance(data, list)
    if data:  # If there are recommendations
        for rec in data:
            assert "type" in rec
            assert "asset_id" in rec
            assert "current_value" in rec
            assert "suggested_value" in rec
            assert "confidence" in rec
            assert "reasons" in rec
            assert "priority" in rec
            assert "expires_at" in rec
    
    # Verify the service was called with correct parameters
    mock_portfolio_service.get_portfolio.assert_called_once_with("test-portfolio-1", "test-user-1")
    mock_analytics_service.generate_recommendations.assert_called_once_with(TEST_PORTFOLIO)

def test_unauthorized_access():
    """Test unauthorized access to analytics endpoints"""
    import traceback
    import sys
    
    # Create a test client that doesn't include auth headers
    test_client = TestClient(app, raise_server_exceptions=False)
    url = "/api/v1/portfolio/analytics/portfolios/test-portfolio-1/insights"
    print(f"\n=== Testing URL: {url} ===")
    
    try:
        # Make the request
        print("\nSending request...")
        response = test_client.get(url)
        
        # Print detailed response information
        print(f"\n=== Response Information ===")
        print(f"Status code: {response.status_code}")
        print("\nHeaders:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
            
        print("\nResponse content:")
        print(response.text)
        
        try:
            print("\nResponse JSON:")
            print(response.json())
        except Exception as json_err:
            print(f"Could not parse response as JSON: {json_err}")
        
        # Check if we're getting a 401 or 500 status code
        if response.status_code == 500:
            print("\n=== 500 Error Details ===")
            print("A 500 error occurred. This might be due to an unhandled exception in the endpoint.")
            if hasattr(response, 'raw') and hasattr(response.raw, '_original_content'):
                print("\nOriginal error content:")
                print(response.raw._original_content)
            
        # The test expects a 401 for unauthorized access
        assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"
        
    except Exception as e:
        print("\n=== EXCEPTION OCCURRED ===")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc(file=sys.stdout)
        raise  # Re-raise the exception to fail the test
