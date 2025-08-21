"""
Unit tests for the Portfolio Service.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from portfolio.models.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate
from portfolio.services.portfolio_service import PortfolioService, portfolio_service

@pytest.mark.asyncio
async def test_create_portfolio():
    """Test creating a new portfolio."""
    # Setup
    user_id = "test-user-1"
    portfolio_data = PortfolioCreate(
        user_id=user_id,
        name="Test Portfolio",
        description="A test portfolio"
    )
    
    expected_portfolio = Portfolio(
        id="test-portfolio-1",
        user_id=user_id,
        name=portfolio_data.name,
        description=portfolio_data.description,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Execute
    result = await portfolio_service.create_portfolio(user_id, portfolio_data)
    
    # Verify
    assert result.id is not None
    assert result.name == portfolio_data.name
    assert result.description == portfolio_data.description

@pytest.mark.asyncio
async def test_get_portfolio():
    """Test getting a portfolio by ID."""
    # Setup
    user_id = "test-user-1"
    
    # First create a portfolio to test with
    portfolio_data = PortfolioCreate(
        user_id=user_id,
        name="Test Portfolio",
        description="A test portfolio",
        risk_tolerance=0.5
    )
    
    created_portfolio = await portfolio_service.create_portfolio(user_id, portfolio_data)
    portfolio_id = created_portfolio.id
    
    # Execute
    result = await portfolio_service.get_portfolio(portfolio_id, user_id)
    
    # Verify
    assert result is not None
    assert result.id == portfolio_id
    assert result.user_id == user_id
    
    # Clean up
    await portfolio_service.delete_portfolio(portfolio_id, user_id)

@pytest.mark.asyncio
async def test_list_portfolios():
    """Test listing portfolios for a user."""
    # Setup
    user_id = "test-user-1"
    
    # Create some test portfolios
    portfolio_data_1 = PortfolioCreate(
        user_id=user_id,
        name="Portfolio 1",
        description="First test portfolio",
        risk_tolerance=0.5
    )
    
    portfolio_data_2 = PortfolioCreate(
        user_id=user_id,
        name="Portfolio 2",
        description="Second test portfolio",
        risk_tolerance=0.7
    )
    
    portfolio1 = await portfolio_service.create_portfolio(user_id, portfolio_data_1)
    portfolio2 = await portfolio_service.create_portfolio(user_id, portfolio_data_2)
    
    # Execute
    result = await portfolio_service.list_portfolios(user_id)
    
    # Verify
    assert result is not None
    assert isinstance(result, list)
    assert len(result) >= 2
    
    # Clean up
    await portfolio_service.delete_portfolio(portfolio1.id, user_id)
    await portfolio_service.delete_portfolio(portfolio2.id, user_id)

@pytest.mark.asyncio
async def test_update_portfolio():
    """Test updating a portfolio."""
    # Setup
    user_id = "test-user-1"
    
    # First create a portfolio to test with
    portfolio_data = PortfolioCreate(
        user_id=user_id,
        name="Original Portfolio Name",
        description="Original Description",
        risk_tolerance=0.5
    )
    
    created_portfolio = await portfolio_service.create_portfolio(user_id, portfolio_data)
    portfolio_id = created_portfolio.id
    
    update_data = PortfolioUpdate(
        name="Updated Portfolio Name",
        description="Updated description"
    )
    
    # Execute
    result = await portfolio_service.update_portfolio(
        portfolio_id=portfolio_id,
        user_id=user_id,
        portfolio_update=update_data
    )
    
    # Verify
    assert result is not None
    assert result.name == update_data.name
    assert result.description == update_data.description
    
    # Clean up
    await portfolio_service.delete_portfolio(portfolio_id, user_id)

@pytest.mark.asyncio
async def test_delete_portfolio():
    """Test deleting a portfolio."""
    # Setup
    user_id = "test-user-1"
    
    # First create a portfolio to test with
    portfolio_data = PortfolioCreate(
        user_id=user_id,
        name="Portfolio to Delete",
        description="A portfolio that will be deleted",
        risk_tolerance=0.5
    )
    
    created_portfolio = await portfolio_service.create_portfolio(user_id, portfolio_data)
    portfolio_id = created_portfolio.id
    
    # Execute
    result = await portfolio_service.delete_portfolio(portfolio_id, user_id)
    
    # Verify
    assert result is True
    
    # Verify it's gone
    deleted_portfolio = await portfolio_service.get_portfolio(portfolio_id, user_id)
    assert deleted_portfolio is None
