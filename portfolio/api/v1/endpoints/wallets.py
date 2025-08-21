"""
Wallet API Endpoints

Handles wallet-related operations including CRUD and balance checking.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict
from datetime import datetime

from ....models.portfolio import Wallet, WalletCreate, WalletUpdate, WalletBalance
from ....services.portfolio_service import portfolio_service
from ....services.balance_service import balance_service
from .deps import get_current_user

# Create a router for wallet endpoints
router = APIRouter(tags=["wallets"])

# Wallet endpoints
@router.post(
    "/",
    response_model=Wallet,
    status_code=status.HTTP_201_CREATED,
    summary="Add a wallet to a portfolio"
)
async def create_wallet(
    portfolio_id: str,
    wallet: WalletCreate,
    current_user: dict = Depends(get_current_user)
) -> Wallet:
    """
    Add a new wallet to a portfolio
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
            
        return await portfolio_service.create_wallet(
            portfolio_id=portfolio_id,
            wallet=wallet
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
    response_model=List[Wallet],
    summary="List all wallets in a portfolio"
)
async def list_wallets(
    portfolio_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
) -> List[Wallet]:
    """
    List all wallets in a portfolio
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
            
        return await portfolio_service.list_wallets(
            portfolio_id=portfolio_id,
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
    "/{wallet_id}",
    response_model=Wallet,
    summary="Get a specific wallet by ID"
)
async def get_wallet(
    portfolio_id: str,
    wallet_id: str,
    current_user: dict = Depends(get_current_user)
) -> Wallet:
    """
    Get a specific wallet by ID
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
            
        wallet = await portfolio_service.get_wallet(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
            
        return wallet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/{wallet_id}",
    response_model=Wallet,
    summary="Update a wallet"
)
async def update_wallet(
    portfolio_id: str,
    wallet_id: str,
    wallet_update: WalletUpdate,
    current_user: dict = Depends(get_current_user)
) -> Wallet:
    """
    Update a wallet
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
            
        wallet = await portfolio_service.update_wallet(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id,
            wallet_update=wallet_update
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
            
        return wallet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete(
    "/{wallet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a wallet"
)
async def delete_wallet(
    portfolio_id: str,
    wallet_id: str,
    current_user: dict = Depends(get_current_user)
) -> None:
    """
    Delete a wallet
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
            
        success = await portfolio_service.delete_wallet(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{wallet_id}/balance",
    response_model=WalletBalance,
    summary="Get wallet balance"
)
async def get_wallet_balance(
    portfolio_id: str,
    wallet_id: str,
    current_user: dict = Depends(get_current_user)
) -> WalletBalance:
    """
    Get the current balance of a wallet
    
    Returns detailed information about the wallet's balance including:
    - Native token balance and its USD value
    - Token balances for all supported tokens
    - NFT count
    - Total portfolio value in USD
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
            
        # Get wallet
        wallet = await portfolio_service.get_wallet(
            portfolio_id=portfolio_id,
            wallet_id=wallet_id
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
            
        # Get wallet balance from the balance service
        balance_data = await balance_service.get_wallet_balance(
            address=wallet.address,
            chain=wallet.chain
        )
        
        # Create and return the WalletBalance response
        return WalletBalance(
            wallet_id=wallet_id,
            address=wallet.address,
            chain=wallet.chain,
            native_balance=balance_data.get("native_balance", 0.0),
            native_balance_usd=balance_data.get("native_balance_usd", 0.0),
            token_balances=balance_data.get("token_balances", {}),
            nft_count=balance_data.get("nft_count", 0),
            total_value_usd=balance_data.get("total_value_usd", 0.0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting wallet balance: {str(e)}"
        )
