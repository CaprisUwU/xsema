"""
Portfolio API Endpoints

Handles portfolio-related operations including CRUD and analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ....models.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioInsights
from ....services.portfolio_service import portfolio_service
from .deps import get_current_user

# Create a router for portfolio endpoints
router = APIRouter(tags=["portfolios"])

# Portfolio endpoints
@router.post(
    "/",
    response_model=Portfolio,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new portfolio"
)
async def create_portfolio(
    portfolio: PortfolioCreate,
    current_user: dict = Depends(get_current_user)
) -> Portfolio:
    """
    Create a new portfolio for the current user
    """
    try:
        return await portfolio_service.create_portfolio(
            user_id=current_user["user_id"],
            portfolio=portfolio
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/",
    response_model=List[Portfolio],
    summary="List all portfolios for the current user"
)
async def list_portfolios(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
) -> List[Portfolio]:
    """
    List all portfolios for the current user
    """
    try:
        return await portfolio_service.list_portfolios(
            user_id=current_user["user_id"],
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{portfolio_id}",
    response_model=Portfolio,
    summary="Get a specific portfolio by ID"
)
async def get_portfolio(
    portfolio_id: str,
    current_user: dict = Depends(get_current_user)
) -> Portfolio:
    """
    Get a specific portfolio by ID
    """
    try:
        portfolio = await portfolio_service.get_portfolio(
            user_id=current_user["user_id"],
            portfolio_id=portfolio_id
        )
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        return portfolio
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/{portfolio_id}",
    response_model=Portfolio,
    summary="Update a portfolio"
)
async def update_portfolio(
    portfolio_id: str,
    portfolio_update: PortfolioUpdate,
    current_user: dict = Depends(get_current_user)
) -> Portfolio:
    """
    Update a portfolio
    """
    try:
        portfolio = await portfolio_service.update_portfolio(
            user_id=current_user["user_id"],
            portfolio_id=portfolio_id,
            portfolio_update=portfolio_update
        )
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        return portfolio
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete(
    "/{portfolio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a portfolio"
)
async def delete_portfolio(
    portfolio_id: str,
    current_user: dict = Depends(get_current_user)
) -> None:
    """
    Delete a portfolio
    """
    try:
        success = await portfolio_service.delete_portfolio(
            user_id=current_user["user_id"],
            portfolio_id=portfolio_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{portfolio_id}/insights",
    response_model=PortfolioInsights,
    summary="Get portfolio insights and analytics"
)
async def get_portfolio_insights(
    portfolio_id: str,
    time_range: str = "30d",
    current_user: dict = Depends(get_current_user)
) -> PortfolioInsights:
    """
    Get insights and analytics for a portfolio
    """
    try:
        # Verify portfolio exists and belongs to user
        portfolio = await portfolio_service.get_portfolio(
            user_id=current_user["user_id"],
            portfolio_id=portfolio_id
        )
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
            
        # Get portfolio with all related data
        portfolio = await portfolio_service.get_portfolio_with_assets(portfolio_id)
        
        # Generate insights
        return await analytics_service.get_portfolio_insights(
            portfolio=portfolio,
            time_range=time_range
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating insights: {str(e)}"
        )

@router.get(
    "/portfolios/{portfolio_id}/performance",
    summary="Get portfolio performance metrics"
)
async def get_portfolio_performance(
    portfolio_id: str,
    time_range: str = "30d",
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get performance metrics for a portfolio
    """
    try:
        # Verify portfolio exists and belongs to user
        portfolio = await portfolio_service.get_portfolio(
            user_id=current_user["user_id"],
            portfolio_id=portfolio_id
        )
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
            
        # Get portfolio with all related data
        portfolio = await portfolio_service.get_portfolio_with_assets(portfolio_id)
        
        # Get performance data
        return await analytics_service.get_portfolio_performance(
            portfolio=portfolio,
            time_range=time_range
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting performance data: {str(e)}"
        )
