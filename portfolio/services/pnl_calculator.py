"""
Profit & Loss Calculator Service

This service provides comprehensive P&L calculations for portfolios including:
- Real-time P&L tracking
- Unrealized vs. realized gains/losses
- Performance metrics and ratios
- Historical performance analysis
"""
import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass

from portfolio.models.portfolio import Portfolio, Asset
from portfolio.services.portfolio_service import PortfolioService

logger = logging.getLogger(__name__)

@dataclass
class PnLBreakdown:
    """Detailed P&L breakdown for a portfolio"""
    portfolio_id: str
    total_cost_basis: Decimal
    current_value: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    total_pnl: Decimal
    roi_percentage: Decimal
    annualized_roi: Optional[Decimal]
    calculation_timestamp: datetime

@dataclass
class AssetPnL:
    """P&L breakdown for a specific asset"""
    asset_id: str
    asset_name: str
    quantity: Decimal
    cost_basis: Decimal
    current_value: Decimal
    unrealized_pnl: Decimal
    roi_percentage: Decimal
    holding_period_days: int

@dataclass
class PerformanceMetrics:
    """Performance metrics for portfolio analysis"""
    sharpe_ratio: Optional[Decimal]
    sortino_ratio: Optional[Decimal]
    max_drawdown: Optional[Decimal]
    volatility: Optional[Decimal]
    beta: Optional[Decimal]

@dataclass
class HistoricalPerformance:
    """Historical performance data"""
    date: datetime
    portfolio_value: Decimal
    daily_return: Decimal
    cumulative_return: Decimal

class PnLCalculator:
    """Advanced P&L calculation service"""
    
    def __init__(self, portfolio_service: PortfolioService):
        self.portfolio_service = portfolio_service
        self.logger = logging.getLogger(__name__)
    
    async def calculate_portfolio_pnl(self, portfolio_id: str, user_id: str) -> Optional[PnLBreakdown]:
        """Calculate comprehensive P&L for a portfolio"""
        try:
            # Get portfolio and assets
            portfolio = await self.portfolio_service.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                self.logger.warning(f"Portfolio {portfolio_id} not found for user {user_id}")
                return None
            
            # Get portfolio assets
            assets = await self._get_portfolio_assets(portfolio_id)
            if not assets:
                self.logger.info(f"No assets found in portfolio {portfolio_id}")
                return await self._create_empty_pnl(portfolio_id)
            
            # Calculate P&L components
            total_cost_basis = sum(asset.cost_basis for asset in assets)
            current_value = sum(asset.current_value for asset in assets)
            
            # Calculate P&L
            unrealized_pnl = current_value - total_cost_basis
            realized_pnl = await self._calculate_realized_pnl(portfolio_id)
            total_pnl = unrealized_pnl + realized_pnl
            
            # Calculate ROI
            roi_percentage = (total_pnl / total_cost_basis * 100) if total_cost_basis > 0 else Decimal('0')
            
            # Calculate annualized ROI
            annualized_roi = await self._calculate_annualized_roi(portfolio_id, total_pnl, total_cost_basis)
            
            pnl_breakdown = PnLBreakdown(
                portfolio_id=portfolio_id,
                total_cost_basis=total_cost_basis,
                current_value=current_value,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl,
                total_pnl=total_pnl,
                roi_percentage=roi_percentage,
                annualized_roi=annualized_roi,
                calculation_timestamp=datetime.now(timezone.utc)
            )
            
            return pnl_breakdown
            
        except Exception as e:
            self.logger.error(f"Error calculating P&L for portfolio {portfolio_id}: {str(e)}")
            return None
    
    async def calculate_asset_pnl(self, asset_id: str, portfolio_id: str, user_id: str) -> Optional[AssetPnL]:
        """Calculate P&L for a specific asset"""
        try:
            # Get asset details
            asset = await self._get_asset(asset_id, portfolio_id)
            if not asset:
                return None
            
            # Calculate P&L
            unrealized_pnl = asset.current_value - asset.cost_basis
            roi_percentage = (unrealized_pnl / asset.cost_basis * 100) if asset.cost_basis > 0 else Decimal('0')
            
            # Calculate holding period
            holding_period_days = await self._calculate_holding_period(asset_id)
            
            asset_pnl = AssetPnL(
                asset_id=asset_id,
                asset_name=asset.name,
                quantity=asset.quantity,
                cost_basis=asset.cost_basis,
                current_value=asset.current_value,
                unrealized_pnl=unrealized_pnl,
                roi_percentage=roi_percentage,
                holding_period_days=holding_period_days
            )
            
            return asset_pnl
            
        except Exception as e:
            self.logger.error(f"Error calculating P&L for asset {asset_id}: {str(e)}")
            return None
    
    async def get_performance_metrics(self, portfolio_id: str, user_id: str) -> Optional[PerformanceMetrics]:
        """Get comprehensive performance metrics for a portfolio"""
        try:
            # Get historical performance data
            historical_data = await self._get_historical_performance(portfolio_id)
            if not historical_data or len(historical_data) < 2:
                return None
            
            # Calculate metrics
            returns = [data.daily_return for data in historical_data[1:]]  # Skip first entry
            sharpe_ratio = self._calculate_sharpe_ratio(returns)
            sortino_ratio = self._calculate_sortino_ratio(returns)
            max_drawdown = self._calculate_max_drawdown(historical_data)
            volatility = self._calculate_volatility(returns)
            beta = await self._calculate_beta(portfolio_id, historical_data)
            
            return PerformanceMetrics(
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                max_drawdown=max_drawdown,
                volatility=volatility,
                beta=beta
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics for portfolio {portfolio_id}: {str(e)}")
            return None
    
    async def get_historical_performance(self, portfolio_id: str, days: int = 365) -> List[HistoricalPerformance]:
        """Get historical performance data for a portfolio"""
        try:
            # This would typically query a database for historical data
            # For now, return mock data
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            historical_data = []
            current_date = start_date
            cumulative_value = Decimal('10000')  # Starting value
            
            while current_date <= end_date:
                # Mock daily performance (in real implementation, get from database)
                daily_return = Decimal('0.001')  # 0.1% daily return
                portfolio_value = cumulative_value * (1 + daily_return)
                cumulative_return = (portfolio_value / Decimal('10000') - 1) * 100
                
                historical_data.append(HistoricalPerformance(
                    date=current_date,
                    portfolio_value=portfolio_value,
                    daily_return=daily_return * 100,
                    cumulative_return=cumulative_return
                ))
                
                cumulative_value = portfolio_value
                current_date += timedelta(days=1)
            
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Error getting historical performance for portfolio {portfolio_id}: {str(e)}")
            return []
    
    # Private helper methods
    async def _get_portfolio_assets(self, portfolio_id: str) -> List[Asset]:
        """Get all assets in a portfolio"""
        try:
            # This would typically query the database
            # For now, return mock data
            return [
                Asset(
                    asset_id="asset_1",
                    name="Bored Ape #1234",
                    quantity=Decimal('1'),
                    cost_basis=Decimal('50000'),
                    current_value=Decimal('75000')
                ),
                Asset(
                    asset_id="asset_2", 
                    name="Doodle #5678",
                    quantity=Decimal('2'),
                    cost_basis=Decimal('20000'),
                    current_value=Decimal('25000')
                )
            ]
        except Exception as e:
            self.logger.error(f"Error getting portfolio assets: {str(e)}")
            return []
    
    async def _get_asset(self, asset_id: str, portfolio_id: str) -> Optional[Asset]:
        """Get a specific asset"""
        assets = await self._get_portfolio_assets(portfolio_id)
        return next((asset for asset in assets if asset.asset_id == asset_id), None)
    
    async def _calculate_realized_pnl(self, portfolio_id: str) -> Decimal:
        """Calculate realized P&L from completed transactions"""
        try:
            # This would query transaction history
            # For now, return mock data
            return Decimal('5000')  # £5,000 realized gains
        except Exception as e:
            self.logger.error(f"Error calculating realized P&L: {str(e)}")
            return Decimal('0')
    
    async def _calculate_annualized_roi(self, portfolio_id: str, total_pnl: Decimal, cost_basis: Decimal) -> Optional[Decimal]:
        """Calculate annualized ROI"""
        try:
            if cost_basis <= 0:
                return None
            
            # Get portfolio creation date (mock for now)
            creation_date = datetime.now(timezone.utc) - timedelta(days=180)  # 6 months ago
            days_held = (datetime.now(timezone.utc) - creation_date).days
            
            if days_held <= 0:
                return None
            
            # Annualized ROI formula: (1 + total_return)^(365/days_held) - 1
            total_return = total_pnl / cost_basis
            annualized_roi = ((1 + total_return) ** (365 / days_held) - 1) * 100
            
            return annualized_roi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            self.logger.error(f"Error calculating annualized ROI: {str(e)}")
            return None
    
    async def _calculate_holding_period(self, asset_id: str) -> int:
        """Calculate holding period in days for an asset"""
        try:
            # Mock holding period (in real implementation, get from transaction history)
            return 90  # 90 days
        except Exception as e:
            self.logger.error(f"Error calculating holding period: {str(e)}")
            return 0
    
    async def _create_empty_pnl(self, portfolio_id: str) -> PnLBreakdown:
        """Create empty P&L breakdown for portfolios with no assets"""
        return PnLBreakdown(
            portfolio_id=portfolio_id,
            total_cost_basis=Decimal('0'),
            current_value=Decimal('0'),
            unrealized_pnl=Decimal('0'),
            realized_pnl=Decimal('0'),
            total_pnl=Decimal('0'),
            roi_percentage=Decimal('0'),
            annualized_roi=None,
            calculation_timestamp=datetime.now(timezone.utc)
        )
    
    def _calculate_sharpe_ratio(self, returns: List[Decimal], risk_free_rate: Decimal = Decimal('0.02')) -> Optional[Decimal]:
        """Calculate Sharpe ratio (risk-adjusted return)"""
        try:
            if not returns:
                return None
            
            # Convert to float for calculations
            returns_float = [float(r) for r in returns]
            avg_return = sum(returns_float) / len(returns_float)
            
            # Calculate standard deviation
            variance = sum((r - avg_return) ** 2 for r in returns_float) / len(returns_float)
            std_dev = variance ** 0.5
            
            if std_dev == 0:
                return None
            
            # Sharpe ratio = (return - risk_free_rate) / std_dev
            sharpe = (avg_return - float(risk_free_rate)) / std_dev
            
            return Decimal(str(sharpe)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            self.logger.error(f"Error calculating Sharpe ratio: {str(e)}")
            return None
    
    def _calculate_sortino_ratio(self, returns: List[Decimal], risk_free_rate: Decimal = Decimal('0.02')) -> Optional[Decimal]:
        """Calculate Sortino ratio (downside risk-adjusted return)"""
        try:
            if not returns:
                return None
            
            # Convert to float for calculations
            returns_float = [float(r) for r in returns]
            avg_return = sum(returns_float) / len(returns_float)
            
            # Calculate downside deviation (only negative returns)
            downside_returns = [r for r in returns_float if r < avg_return]
            if not downside_returns:
                return None
            
            downside_variance = sum((r - avg_return) ** 2 for r in downside_returns) / len(downside_returns)
            downside_deviation = downside_variance ** 0.5
            
            if downside_deviation == 0:
                return None
            
            # Sortino ratio = (return - risk_free_rate) / downside_deviation
            sortino = (avg_return - float(risk_free_rate)) / downside_deviation
            
            return Decimal(str(sortino)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            self.logger.error(f"Error calculating Sortino ratio: {str(e)}")
            return None
    
    def _calculate_max_drawdown(self, historical_data: List[HistoricalPerformance]) -> Optional[Decimal]:
        """Calculate maximum drawdown"""
        try:
            if not historical_data:
                return None
            
            peak_value = historical_data[0].portfolio_value
            max_drawdown = Decimal('0')
            
            for data in historical_data:
                if data.portfolio_value > peak_value:
                    peak_value = data.portfolio_value
                else:
                    drawdown = (peak_value - data.portfolio_value) / peak_value
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
            
            return max_drawdown * 100  # Convert to percentage
            
        except Exception as e:
            self.logger.error(f"Error calculating max drawdown: {str(e)}")
            return None
    
    def _calculate_volatility(self, returns: List[Decimal]) -> Optional[Decimal]:
        """Calculate volatility (standard deviation of returns)"""
        try:
            if not returns:
                return None
            
            returns_float = [float(r) for r in returns]
            avg_return = sum(returns_float) / len(returns_float)
            
            variance = sum((r - avg_return) ** 2 for r in returns_float) / len(returns_float)
            volatility = variance ** 0.5
            
            return Decimal(str(volatility * 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {str(e)}")
            return None
    
    async def _calculate_beta(self, portfolio_id: str, historical_data: List[HistoricalPerformance]) -> Optional[Decimal]:
        """Calculate beta (market correlation)"""
        try:
            # This would compare portfolio returns to market returns
            # For now, return mock beta
            return Decimal('1.2')  # Slightly more volatile than market
            
        except Exception as e:
            self.logger.error(f"Error calculating beta: {str(e)}")
            return None
