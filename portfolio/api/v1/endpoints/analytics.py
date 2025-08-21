"""
Portfolio Analytics API Endpoints

Provides portfolio analytics, performance metrics, and insights.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from ....models.portfolio import (
    Portfolio, PortfolioInsights, AssetPerformance, Recommendation
)
from ....services.portfolio_service import portfolio_service
from ....services.analytics_service import analytics_service
from ....services.price_service import price_service
from .deps import get_current_user

router = APIRouter(tags=["portfolio-analytics"])

@router.get(
    "/portfolios/{portfolio_id}/insights",
    response_model=PortfolioInsights,
    summary="Get portfolio insights and analytics"
)
async def get_portfolio_insights(
    portfolio_id: str,
    time_range: str = Query("30d", description="Time range for analysis (e.g., 7d, 30d, 1y, all)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive insights and analytics for a portfolio
    """
    try:
        # Get the portfolio
        portfolio = await portfolio_service.get_portfolio(portfolio_id, current_user["id"])
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        # Generate insights
        insights = await analytics_service.get_portfolio_insights(portfolio, time_range)
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating portfolio insights: {str(e)}"
        )

@router.get(
    "/portfolios/{portfolio_id}/performance",
    response_model=Dict[str, Any],
    summary="Get portfolio performance metrics"
)
async def get_portfolio_performance(
    portfolio_id: str,
    time_range: str = Query("30d", description="Time range for analysis"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get performance metrics for a portfolio including:
    - Total return
    - Daily/weekly/monthly returns
    - Volatility
    - Sharpe ratio
    - Drawdowns
    - Benchmark comparison
    """
    try:
        portfolio = await portfolio_service.get_portfolio(portfolio_id, current_user["id"])
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
            
        performance = await analytics_service.get_portfolio_performance(portfolio, time_range)
        return performance
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating performance metrics: {str(e)}"
        )

@router.get(
    "/portfolios/{portfolio_id}/risk",
    response_model=Dict[str, Any],
    summary="Get portfolio risk metrics"
)
async def get_portfolio_risk(
    portfolio_id: str,
    time_range: str = Query("30d", description="Time range for analysis"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get risk assessment for a portfolio including:
    - Volatility
    - Value at Risk (VaR)
    - Conditional Value at Risk (CVaR)
    - Maximum drawdown
    - Beta and correlation with market
    """
    try:
        portfolio = await portfolio_service.get_portfolio(portfolio_id, current_user["id"])
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
            
        risk_metrics = await analytics_service.get_portfolio_risk(portfolio, time_range)
        return risk_metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating risk metrics: {str(e)}"
        )

@router.get(
    "/portfolios/{portfolio_id}/diversification",
    response_model=Dict[str, Any],
    summary="Get portfolio diversification metrics"
)
async def get_portfolio_diversification(
    portfolio_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get diversification metrics for a portfolio including:
    - Asset class distribution
    - Collection concentration
    - Chain/token distribution
    - Herfindahl-Hirschman Index (HHI)
    - Sector/industry exposure
    """
    try:
        portfolio = await portfolio_service.get_portfolio(portfolio_id, current_user["id"])
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
            
        diversification = await analytics_service.get_portfolio_diversification(portfolio)
        return diversification
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating diversification metrics: {str(e)}"
        )

@router.get(
    "/portfolios/{portfolio_id}/recommendations",
    response_model=List[Recommendation],
    summary="Get portfolio recommendations"
)
async def get_portfolio_recommendations(
    portfolio_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-generated recommendations for portfolio optimization
    """
    try:
        portfolio = await portfolio_service.get_portfolio(portfolio_id, current_user["id"])
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
            
        recommendations = await analytics_service.generate_recommendations(portfolio)
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )
