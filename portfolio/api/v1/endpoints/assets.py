"""
Asset API Endpoints

Handles asset-related operations including CRUD and price data.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ....models.portfolio import (
    Asset, AssetCreate, AssetUpdate, 
    AssetValueHistory, AssetPerformance
)
from ....services.asset_service import asset_service
from ....services.price_service import price_service
from ....services.portfolio_service import portfolio_service
from ....services.nft_service import nft_service
from .deps import get_current_user

# Create a router for asset endpoints
router = APIRouter(tags=["assets"])

# Asset endpoints
@router.post(
    "/",
    response_model=Asset,
    status_code=status.HTTP_201_CREATED,
    summary="Add an asset to a wallet"
)
async def create_asset(
    portfolio_id: str,
    wallet_id: str,
    asset: AssetCreate,
    current_user: dict = Depends(get_current_user)
) -> Asset:
    print("\n=== ASSET ENDPOINT DEBUG ===")
    print(f"Current user: {current_user}")
    print(f"Portfolio ID: {portfolio_id}")
    print(f"Wallet ID: {wallet_id}")
    print(f"Asset data: {asset.dict()}")
    print("==========================\n")
    """
    Add a new asset to a wallet
    """
    print(f"\n=== CREATE ASSET DEBUG ===")
    print(f"Current user: {current_user}")
    print(f"Portfolio ID: {portfolio_id}")
    print(f"Wallet ID: {wallet_id}")
    print(f"Asset data: {asset}")
    
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
            
        # Verify wallet exists in portfolio
        wallet = await portfolio_service.get_wallet(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
            
        return await portfolio_service.create_asset(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id,
            asset=asset
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/",
    response_model=List[Asset],
    summary="List all assets in a wallet"
)
async def list_assets(
    portfolio_id: str,
    wallet_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
) -> List[Asset]:
    """
    List all assets in a wallet
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
            
        # Verify wallet exists in portfolio
        wallet = await portfolio_service.get_wallet(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
            
        return await portfolio_service.list_assets(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id,
            skip=skip,
            limit=limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{asset_id}",
    response_model=Asset,
    summary="Get a specific asset by ID"
)
async def get_asset(
    portfolio_id: str,
    wallet_id: str,
    asset_id: str,
    current_user: dict = Depends(get_current_user)
) -> Asset:
    """
    Get a specific asset by ID
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
            
        # Verify wallet exists in portfolio
        wallet = await portfolio_service.get_wallet(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
            
        asset = await portfolio_service.get_asset(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id,
            asset_id=asset_id
        )
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
            
        return asset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/{asset_id}",
    response_model=Asset,
    summary="Update an asset"
)
async def update_asset(
    portfolio_id: str,
    wallet_id: str,
    asset_id: str,
    asset_update: AssetUpdate,
    current_user: dict = Depends(get_current_user)
) -> Asset:
    """
    Update an asset
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
            
        # Verify wallet exists in portfolio
        wallet = await portfolio_service.get_wallet(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
            
        asset = await portfolio_service.update_asset(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id,
            asset_id=asset_id,
            asset_update=asset_update
        )
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
            
        return asset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an asset"
)
async def delete_asset(
    portfolio_id: str,
    wallet_id: str,
    asset_id: str,
    current_user: dict = Depends(get_current_user)
) -> None:
    """
    Delete an asset
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
            
        # Verify wallet exists in portfolio
        wallet = await portfolio_service.get_wallet(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
            
        success = await portfolio_service.delete_asset(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id,
            asset_id=asset_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{asset_id}/price",
    response_model=Dict[str, Any],
    summary="Get current price of an asset"
)
async def get_asset_price(
    portfolio_id: str,
    wallet_id: str,
    asset_id: str,
    vs_currencies: List[str] = Query(['usd'], description="Target currencies"),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the current price of an asset
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
            
        # Verify wallet exists in portfolio
        wallet = await portfolio_service.get_wallet(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
            
        # Get asset
        asset = await portfolio_service.get_asset(
            wallet_id=wallet_id,
            asset_id=asset_id
        )
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
            
        # Get price data
        prices = await price_service.get_prices(
            asset_ids=[asset.asset_id],
            vs_currencies=vs_currencies
        )
        
        if not prices or asset.asset_id not in prices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Price data not available"
            )
            
        return {
            "asset_id": asset.asset_id,
            "symbol": asset.symbol,
            "prices": prices[asset.asset_id],
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting asset price: {str(e)}"
        )

@router.get(
    "/{asset_id}/history",
    response_model=List[Dict[str, Any]],
    summary="Get price history of an asset"
)
async def get_asset_price_history(
    portfolio_id: str,
    wallet_id: str,
    asset_id: str,
    days: int = 30,
    vs_currency: str = 'usd',
    current_user: dict = Depends(get_current_user)
) -> List[AssetValueHistory]:
    """
    Get price history of an asset
    
    Returns a list of historical price points for the specified asset over the given time period.
    Each point includes price, market data, and timestamp information.
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
            
        # Verify wallet exists in portfolio
        wallet = await portfolio_service.get_wallet(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
            
        # Get asset
        asset = await portfolio_service.get_asset(
            wallet_id=wallet_id,
            asset_id=asset_id
        )
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
            
        # Get price history
        history_data = await price_service.get_price_history(
            asset_id=asset.asset_id,
            days=days,
            vs_currency=vs_currency
        )
        
        # Convert raw history data to AssetValueHistory objects
        history = []
        for item in history_data:
            history.append(AssetValueHistory(
                timestamp=item["timestamp"],
                asset_id=asset.asset_id,
                price=item.get("price", 0),
                price_usd=item.get("price_usd", 0),
                market_cap=item.get("market_cap"),
                total_volume=item.get("total_volume")
            ))
            
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting price history: {str(e)}"
        )
