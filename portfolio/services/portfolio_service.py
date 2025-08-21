"""
Portfolio Service

This module provides services for managing user portfolios, including CRUD operations,
portfolio analysis, and performance tracking.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging
from fastapi import HTTPException, status

from ..models.portfolio import (
    Portfolio, 
    PortfolioCreate, 
    PortfolioUpdate,
    PortfolioInsights,
    Asset,
    AssetCreate,
    AssetUpdate,
    Wallet,
    WalletCreate,
    WalletUpdate,
    Recommendation,
    RecommendationType
)
from ..core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

class PortfolioService:
    """Service for portfolio-related operations"""
    
    def __init__(self):
        # In a real application, this would be a database connection
        self.portfolios = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create_portfolio(self, user_id: str, portfolio: PortfolioCreate) -> Portfolio:
        """Create a new portfolio for a user"""
        try:
            # In a real app, this would be a database operation
            portfolio_id = f"pf_{len(self.portfolios) + 1}"
            now = datetime.now(timezone.utc)
            
            new_portfolio = Portfolio(
                id=portfolio_id,
                user_id=user_id,
                name=portfolio.name,
                description=portfolio.description,
                risk_tolerance=portfolio.risk_tolerance,
                created_at=now,
                updated_at=now
            )
            
            self.portfolios[portfolio_id] = new_portfolio
            self.logger.info(f"Created portfolio {portfolio_id} for user {user_id}")
            return new_portfolio
            
        except Exception as e:
            self.logger.error(f"Error creating portfolio: {str(e)}")
            raise
    
    async def get_portfolio(self, portfolio_id: str, user_id: str) -> Optional[Portfolio]:
        """Get a portfolio by ID for a specific user"""
        try:
            portfolio = self.portfolios.get(portfolio_id)
            if portfolio and portfolio.user_id == user_id:
                return portfolio
            return None
        except Exception as e:
            self.logger.error(f"Error getting portfolio {portfolio_id}: {str(e)}")
            return None
    
    async def list_portfolios(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Portfolio]:
        """List all portfolios for a user with pagination"""
        try:
            user_portfolios = [
                p for p in self.portfolios.values() 
                if p.user_id == user_id
            ]
            return user_portfolios[skip:skip + limit]
        except Exception as e:
            self.logger.error(f"Error listing portfolios for user {user_id}: {str(e)}")
            return []
    
    async def update_portfolio(
        self, 
        portfolio_id: str, 
        user_id: str, 
        portfolio_update: PortfolioUpdate
    ) -> Optional[Portfolio]:
        """Update a portfolio's details"""
        try:
            portfolio = await self.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                return None
                
            update_data = portfolio_update.model_dump(exclude_unset=True)
            
            # Update fields that were provided
            for field, value in update_data.items():
                if hasattr(portfolio, field):
                    setattr(portfolio, field, value)
            
            portfolio.updated_at = datetime.now(timezone.utc)
            self.portfolios[portfolio_id] = portfolio
            self.logger.info(f"Updated portfolio {portfolio_id}")
            return portfolio
        except Exception as e:
            self.logger.error(f"Error updating portfolio {portfolio_id}: {str(e)}")
            return None
    
    async def delete_portfolio(self, portfolio_id: str, user_id: str) -> bool:
        """Delete a portfolio if it belongs to the user"""
        try:
            portfolio = await self.get_portfolio(portfolio_id, user_id)
            if portfolio:
                del self.portfolios[portfolio_id]
                self.logger.info(f"Deleted portfolio {portfolio_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting portfolio {portfolio_id}: {str(e)}")
            return False
    
    async def get_portfolio_insights(
        self, 
        portfolio_id: str, 
        user_id: str,
        time_range: str = "30d"
    ) -> Optional[PortfolioInsights]:
        """Generate insights and recommendations for a portfolio"""
        try:
            portfolio = await self.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                return None
                
            # In a real app, this would analyze the portfolio and generate insights
            # For now, we'll return some mock data
            insights = PortfolioInsights(
                portfolio_id=portfolio_id,
                risk_assessment={
                    "score": 0.65,
                    "level": "Moderate",
                    "factors": ["Diversified assets", "Balanced risk profile"]
                },
                opportunities=[
                    Recommendation(
                        type=RecommendationType.BUY,
                        asset_id="ethereum",
                        current_value=0.0,
                        suggested_value=1000.0,
                        confidence=0.75,
                        reasons=["Diversification opportunity"],
                        priority=2
                    )
                ],
                warnings=[],
                market_conditions={
                    "sentiment": "neutral",
                    "trend": "slightly_bullish",
                    "volatility": "medium"
                }
            )
            
            return insights
        except Exception as e:
            self.logger.error(f"Error getting portfolio insights for {portfolio_id}: {str(e)}")
            return None
    
    async def get_portfolio_performance(
        self, 
        portfolio_id: str, 
        user_id: str,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """Get performance metrics for a portfolio"""
        try:
            portfolio = await self.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                return {}
                
            # In a real app, this would calculate actual performance metrics
            # For now, we'll return some mock data
            return {
                "portfolio_id": portfolio_id,
                "time_range": time_range,
                "total_return": 0.1245,  # 12.45%
                "benchmark_return": 0.0892,
                "sharpe_ratio": 1.23,
                "volatility": 0.156,
                "max_drawdown": -0.087,
                "start_value": 10000.0,
                "end_value": 11245.0,
                "asset_allocation": [
                    {"asset": "Ethereum", "allocation": 0.45},
                    {"asset": "Bitcoin", "allocation": 0.35},
                    {"asset": "Stablecoins", "allocation": 0.20}
                ]
            }
        except Exception as e:
            self.logger.error(f"Error getting portfolio performance for {portfolio_id}: {str(e)}")
            return {}
            
    # Wallet Management Methods
    
    async def create_wallet(
        self,
        portfolio_id: str,
        wallet: WalletCreate
    ) -> Wallet:
        """
        Create a new wallet in a portfolio
        
        Args:
            portfolio_id: ID of the portfolio to add the wallet to
            wallet: Wallet creation data
            
        Returns:
            The created wallet
        """
        try:
            # In a real app, this would be a database operation
            portfolio = self.portfolios.get(portfolio_id)
            if not portfolio:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Portfolio not found"
                )
                
            # Create a new wallet with a unique ID
            wallet_id = f"wallet_{len(portfolio.wallets) + 1}"
            new_wallet = Wallet(
                id=wallet_id,
                **wallet.dict()
            )
            
            # Add the wallet to the portfolio
            portfolio.wallets.append(new_wallet)
            portfolio.updated_at = datetime.now(timezone.utc)
            
            self.logger.info(f"Created wallet {wallet_id} in portfolio {portfolio_id}")
            return new_wallet
            
        except Exception as e:
            self.logger.error(f"Error creating wallet: {str(e)}")
            raise
    
    async def list_wallets(
        self,
        portfolio_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Wallet]:
        """
        List all wallets in a portfolio with pagination
        
        Args:
            portfolio_id: ID of the portfolio
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of wallets in the portfolio
        """
        try:
            portfolio = self.portfolios.get(portfolio_id)
            if not portfolio:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Portfolio not found"
                )
                
            return portfolio.wallets[skip:skip + limit]
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error listing wallets: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving wallets"
            )
    
    async def get_wallet(
        self,
        portfolio_id: str,
        wallet_id: str
    ) -> Optional[Wallet]:
        """
        Get a specific wallet by ID
        
        Args:
            portfolio_id: ID of the portfolio
            wallet_id: ID of the wallet to retrieve
            
        Returns:
            The requested wallet, or None if not found
        """
        try:
            portfolio = self.portfolios.get(portfolio_id)
            if not portfolio:
                return None
                
            for wallet in portfolio.wallets:
                if wallet.id == wallet_id:  # Use id for lookup
                    return wallet
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting wallet {wallet_id}: {str(e)}")
            return None
    
    async def update_wallet(
        self,
        portfolio_id: str,
        wallet_id: str,
        wallet_update: WalletUpdate
    ) -> Optional[Wallet]:
        """
        Update a wallet's details
        
        Args:
            portfolio_id: ID of the portfolio
            wallet_id: ID of the wallet to update
            wallet_update: Updated wallet data
            
        Returns:
            The updated wallet, or None if not found
        """
        try:
            portfolio = self.portfolios.get(portfolio_id)
            if not portfolio:
                return None
                
            for i, wallet in enumerate(portfolio.wallets):
                if wallet.id == wallet_id:
                    update_data = wallet_update.dict(exclude_unset=True)
                    
                    # Update fields that were provided
                    for field, value in update_data.items():
                        if hasattr(wallet, field):
                            setattr(wallet, field, value)
                    
                    wallet.updated_at = datetime.now(timezone.utc)
                    portfolio.updated_at = datetime.now(timezone.utc)
                    
                    self.logger.info(f"Updated wallet {wallet_id} in portfolio {portfolio_id}")
                    return wallet
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Error updating wallet {wallet_id}: {str(e)}")
            return None
    
    async def delete_wallet(
        self,
        portfolio_id: str,
        wallet_id: str
    ) -> bool:
        """
        Delete a wallet from a portfolio
        
        Args:
            portfolio_id: ID of the portfolio
            wallet_id: ID of the wallet to delete
            
        Returns:
            True if the wallet was deleted, False otherwise
        """
        try:
            portfolio = self.portfolios.get(portfolio_id)
            if not portfolio:
                return False
                
            for i, wallet in enumerate(portfolio.wallets):
                if wallet.id == wallet_id:
                    del portfolio.wallets[i]
                    portfolio.updated_at = datetime.now(timezone.utc)
                    
                    self.logger.info(f"Deleted wallet {wallet_id} from portfolio {portfolio_id}")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting wallet {wallet_id}: {str(e)}")
            return False
            
    async def create_asset(
        self,
        portfolio_id: str,
        wallet_id: str,
        asset: AssetCreate
    ) -> Asset:
        """
        Create a new asset in a wallet
        
        Args:
            portfolio_id: ID of the portfolio
            wallet_id: ID of the wallet to add the asset to
            asset: Asset creation data
            
        Returns:
            The created asset
        """
        try:
            # Get the portfolio
            portfolio = self.portfolios.get(portfolio_id)
            if not portfolio:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Portfolio not found"
                )
                
            # Find the wallet in the portfolio
            wallet = None
            for w in portfolio.wallets:
                if w.id == wallet_id:  # Using id as the identifier
                    wallet = w
                    break
                    
            if not wallet:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Wallet not found in the specified portfolio"
                )
                
            # Create the asset with default values
            new_asset = Asset(
                **asset.dict(),
                value_usd=0.0,  # Will be updated by price service
                last_updated=datetime.now(timezone.utc)
            )
            
            # Add the asset to the wallet
            if not hasattr(wallet, 'assets'):
                wallet.assets = []
                
            wallet.assets.append(new_asset)
            portfolio.updated_at = datetime.now(timezone.utc)
            
            self.logger.info(f"Created asset {asset.asset_id} in wallet {wallet_id} of portfolio {portfolio_id}")
            return new_asset
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating asset: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create asset: {str(e)}"
            )
    
    async def get_asset(
        self,
        portfolio_id: str,
        wallet_id: str,
        asset_id: str
    ) -> Optional[Asset]:
        """
        Get a specific asset by ID
        
        Args:
            portfolio_id: ID of the portfolio
            wallet_id: ID of the wallet
            asset_id: ID of the asset to retrieve
            
        Returns:
            The requested asset, or None if not found
        """
        try:
            # Get the portfolio
            portfolio = self.portfolios.get(portfolio_id)
            if not portfolio:
                return None
                
            # Find the wallet in the portfolio
            wallet = None
            for w in portfolio.wallets:
                if w.id == wallet_id:
                    wallet = w
                    break
                    
            if not wallet:
                return None
                
            # Find the asset in the wallet
            for asset in wallet.assets:
                if asset.asset_id == asset_id:
                    return asset
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting asset {asset_id}: {str(e)}")
            return None
    
    async def list_assets(
        self,
        portfolio_id: str,
        wallet_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        List all assets in a wallet
        
        Args:
            portfolio_id: ID of the portfolio
            wallet_id: ID of the wallet
            skip: Number of assets to skip
            limit: Maximum number of assets to return
            
        Returns:
            List of assets in the wallet
        """
        try:
            # Get the portfolio
            portfolio = self.portfolios.get(portfolio_id)
            if not portfolio:
                return []
                
            # Find the wallet in the portfolio
            wallet = None
            for w in portfolio.wallets:
                if w.id == wallet_id:
                    wallet = w
                    break
                    
            if not wallet:
                return []
                
            # Return the assets with pagination
            assets = wallet.assets[skip:skip + limit]
            return assets
            
        except Exception as e:
            self.logger.error(f"Error listing assets: {str(e)}")
            return []
    
    async def update_asset(
        self,
        portfolio_id: str,
        wallet_id: str,
        asset_id: str,
        asset_update: AssetUpdate
    ) -> Optional[Asset]:
        """
        Update an existing asset
        
        Args:
            portfolio_id: ID of the portfolio
            wallet_id: ID of the wallet
            asset_id: ID of the asset to update
            asset_update: Updated asset data
            
        Returns:
            The updated asset, or None if not found
        """
        try:
            # Get the portfolio
            portfolio = self.portfolios.get(portfolio_id)
            if not portfolio:
                return None
                
            # Find the wallet in the portfolio
            wallet = None
            for w in portfolio.wallets:
                if w.id == wallet_id:
                    wallet = w
                    break
                    
            if not wallet:
                return None
                
            # Find and update the asset
            for asset in wallet.assets:
                if asset.asset_id == asset_id:
                    update_data = asset_update.model_dump(exclude_unset=True)
                    
                    # Update fields that were provided
                    for field, value in update_data.items():
                        if hasattr(asset, field):
                            setattr(asset, field, value)
                    
                    asset.last_updated = datetime.now(timezone.utc)
                    portfolio.updated_at = datetime.now(timezone.utc)
                    
                    self.logger.info(f"Updated asset {asset_id} in wallet {wallet_id} of portfolio {portfolio_id}")
                    return asset
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Error updating asset {asset_id}: {str(e)}")
            return None
    
    async def delete_asset(
        self,
        portfolio_id: str,
        wallet_id: str,
        asset_id: str
    ) -> bool:
        """
        Delete an asset from a wallet
        
        Args:
            portfolio_id: ID of the portfolio
            wallet_id: ID of the wallet
            asset_id: ID of the asset to delete
            
        Returns:
            True if the asset was deleted, False otherwise
        """
        try:
            # Get the portfolio
            portfolio = self.portfolios.get(portfolio_id)
            if not portfolio:
                return False
                
            # Find the wallet in the portfolio
            wallet = None
            for w in portfolio.wallets:
                if w.id == wallet_id:
                    wallet = w
                    break
                    
            if not wallet:
                return False
                
            # Find and delete the asset
            for i, asset in enumerate(wallet.assets):
                if asset.asset_id == asset_id:
                    del wallet.assets[i]
                    portfolio.updated_at = datetime.now(timezone.utc)
                    
                    self.logger.info(f"Deleted asset {asset_id} from wallet {wallet_id} of portfolio {portfolio_id}")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting asset {asset_id}: {str(e)}")
            return False

# Create a singleton instance of the service
portfolio_service = PortfolioService()
