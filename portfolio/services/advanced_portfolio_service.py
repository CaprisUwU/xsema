"""
Advanced Portfolio Management Service for XSEMA

This service provides:
- Advanced P&L calculations (realized/unrealized)
- Debt tracking and management
- Tax reporting and calculations
- Portfolio performance analytics
- Risk assessment and management
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass

from portfolio.models.portfolio import Portfolio, Asset, Transaction, TransactionType
from portfolio.services.price_service import price_service
from portfolio.core.cache import cache

logger = logging.getLogger(__name__)

@dataclass
class PnLBreakdown:
    """Detailed P&L breakdown for an asset or portfolio."""
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    total_pnl: Decimal
    realized_pnl_percentage: Decimal
    unrealized_pnl_percentage: Decimal
    total_pnl_percentage: Decimal
    cost_basis: Decimal
    current_value: Decimal
    total_invested: Decimal
    fees_paid: Decimal
    taxes_paid: Decimal

@dataclass
class DebtPosition:
    """Represents a debt position in the portfolio."""
    asset_id: str
    asset_name: str
    borrowed_amount: Decimal
    borrowed_value_usd: Decimal
    interest_rate: Decimal
    interest_accrued: Decimal
    collateral_value: Decimal
    liquidation_ratio: Decimal
    risk_level: str  # low, medium, high, critical
    due_date: Optional[datetime]
    lender: str

@dataclass
class TaxReport:
    """Tax reporting information for a portfolio."""
    tax_year: int
    total_realized_gains: Decimal
    total_realized_losses: Decimal
    net_capital_gains: Decimal
    short_term_gains: Decimal
    long_term_gains: Decimal
    wash_sale_losses: Decimal
    total_fees: Decimal
    total_interest_paid: Decimal
    tax_liability_estimate: Decimal
    transactions_count: int

class AdvancedPortfolioService:
    """Advanced portfolio management with P&L, debt, and tax features."""
    
    def __init__(self):
        self.price_service = price_service
        self.cache_ttl = 3600  # 1 hour cache
    
    async def calculate_advanced_pnl(
        self, 
        portfolio: Portfolio, 
        include_debt: bool = True
    ) -> Dict[str, Any]:
        """Calculate comprehensive P&L including debt and fees."""
        
        try:
            # Get current prices for all assets
            asset_prices = await self._get_asset_prices(portfolio)
            
            # Calculate P&L for each asset
            asset_pnls = {}
            total_realized_pnl = Decimal('0')
            total_unrealized_pnl = Decimal('0')
            total_fees = Decimal('0')
            total_cost_basis = Decimal('0')
            total_current_value = Decimal('0')
            
            for wallet in portfolio.wallets:
                for asset in wallet.assets:
                    asset_pnl = await self._calculate_asset_pnl(
                        asset, wallet, asset_prices.get(asset.asset_id, {})
                    )
                    asset_pnls[asset.asset_id] = asset_pnl
                    
                    total_realized_pnl += asset_pnl.realized_pnl
                    total_unrealized_pnl += asset_pnl.unrealized_pnl
                    total_fees += asset_pnl.fees_paid
                    total_cost_basis += asset_pnl.cost_basis
                    total_current_value += asset_pnl.current_value
            
            # Calculate debt impact if requested
            debt_impact = Decimal('0')
            debt_positions = []
            if include_debt:
                debt_positions = await self._get_debt_positions(portfolio)
                debt_impact = sum(debt.loan_value for debt in debt_positions)
            
            # Calculate portfolio-level metrics
            total_invested = total_cost_basis + total_fees
            net_portfolio_value = total_current_value - debt_impact
            total_pnl = total_realized_pnl + total_unrealized_pnl
            
            # Calculate percentages
            total_pnl_percentage = (
                (total_pnl / total_invested * 100) if total_invested > 0 else Decimal('0')
            )
            
            portfolio_pnl = PnLBreakdown(
                realized_pnl=total_realized_pnl,
                unrealized_pnl=total_unrealized_pnl,
                total_pnl=total_pnl,
                realized_pnl_percentage=(
                    (total_realized_pnl / total_invested * 100) if total_invested > 0 else Decimal('0')
                ),
                unrealized_pnl_percentage=(
                    (total_unrealized_pnl / total_invested * 100) if total_invested > 0 else Decimal('0')
                ),
                total_pnl_percentage=total_pnl_percentage,
                cost_basis=total_cost_basis,
                current_value=net_portfolio_value,
                total_invested=total_invested,
                fees_paid=total_fees,
                taxes_paid=Decimal('0')  # Will be calculated separately
            )
            
            return {
                "portfolio_pnl": portfolio_pnl,
                "asset_pnls": asset_pnls,
                "debt_positions": debt_positions,
                "debt_impact": debt_impact,
                "risk_metrics": await self._calculate_risk_metrics(portfolio, debt_positions),
                "performance_metrics": await self._calculate_performance_metrics(portfolio),
                "last_updated": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error calculating advanced P&L: {e}")
            raise
    
    async def _calculate_asset_pnl(
        self, 
        asset: Asset, 
        wallet, 
        current_prices: Dict
    ) -> PnLBreakdown:
        """Calculate P&L for a specific asset."""
        
        try:
            # Get asset transactions
            transactions = await self._get_asset_transactions(asset.asset_id, wallet.id)
            
            # Calculate cost basis and realized P&L
            cost_basis = Decimal('0')
            realized_pnl = Decimal('0')
            fees_paid = Decimal('0')
            total_quantity = Decimal('0')
            
            for tx in transactions:
                if tx.type in [TransactionType.BUY, TransactionType.TRANSFER_IN]:
                    cost_basis += Decimal(str(tx.total_value or 0))
                    total_quantity += Decimal(str(tx.quantity))
                    fees_paid += Decimal(str(tx.fee or 0))
                elif tx.type in [TransactionType.SELL, TransactionType.TRANSFER_OUT]:
                    # Calculate realized P&L for sales
                    avg_cost = cost_basis / total_quantity if total_quantity > 0 else Decimal('0')
                    sale_value = Decimal(str(tx.total_value or 0))
                    sale_cost = avg_cost * Decimal(str(tx.quantity))
                    realized_pnl += sale_value - sale_cost
                    total_quantity -= Decimal(str(tx.quantity))
                    cost_basis = avg_cost * total_quantity
                    fees_paid += Decimal(str(tx.fee or 0))
            
            # Get current price
            current_price = Decimal(str(current_prices.get('usd', 0)))
            current_value = current_price * total_quantity
            
            # Calculate unrealized P&L
            unrealized_pnl = current_value - cost_basis
            
            # Calculate percentages
            total_invested = cost_basis + fees_paid
            realized_pnl_percentage = (
                (realized_pnl / total_invested * 100) if total_invested > 0 else Decimal('0')
            )
            unrealized_pnl_percentage = (
                (unrealized_pnl / total_invested * 100) if total_invested > 0 else Decimal('0')
            )
            total_pnl_percentage = realized_pnl_percentage + unrealized_pnl_percentage
            
            return PnLBreakdown(
                realized_pnl=realized_pnl,
                unrealized_pnl=unrealized_pnl,
                total_pnl=realized_pnl + unrealized_pnl,
                realized_pnl_percentage=realized_pnl_percentage,
                unrealized_pnl_percentage=unrealized_pnl_percentage,
                total_pnl_percentage=total_pnl_percentage,
                cost_basis=cost_basis,
                current_value=current_value,
                total_invested=total_invested,
                fees_paid=fees_paid,
                taxes_paid=Decimal('0')
            )
            
        except Exception as e:
            logger.error(f"Error calculating asset P&L for {asset.asset_id}: {e}")
            raise
    
    async def generate_tax_report(
        self, 
        portfolio: Portfolio, 
        tax_year: int,
        include_debt: bool = True
    ) -> TaxReport:
        """Generate comprehensive tax report for a portfolio."""
        
        try:
            # Get all transactions for the tax year
            start_date = datetime(tax_year, 1, 1, tzinfo=timezone.utc)
            end_date = datetime(tax_year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
            
            all_transactions = []
            for wallet in portfolio.wallets:
                wallet_transactions = await self._get_wallet_transactions(
                    wallet.id, start_date, end_date
                )
                all_transactions.extend(wallet_transactions)
            
            # Calculate tax metrics
            realized_gains = Decimal('0')
            realized_losses = Decimal('0')
            short_term_gains = Decimal('0')
            long_term_gains = Decimal('0')
            wash_sale_losses = Decimal('0')
            total_fees = Decimal('0')
            total_interest = Decimal('0')
            
            # Group transactions by asset for wash sale detection
            asset_transactions = {}
            for tx in all_transactions:
                if tx.asset_id not in asset_transactions:
                    asset_transactions[tx.asset_id] = []
                asset_transactions[tx.asset_id].append(tx)
            
            # Process each asset's transactions
            for asset_id, transactions in asset_transactions.items():
                asset_pnl, wash_sales = await self._calculate_tax_pnl(transactions)
                
                if asset_pnl > 0:
                    realized_gains += asset_pnl
                    # Determine if short-term or long-term
                    for tx in transactions:
                        if tx.type == TransactionType.SELL:
                            holding_period = tx.timestamp - tx.created_at
                            if holding_period.days <= 365:
                                short_term_gains += asset_pnl
                            else:
                                long_term_gains += asset_pnl
                            break
                else:
                    realized_losses += abs(asset_pnl)
                
                wash_sale_losses += wash_sales
                total_fees += sum(Decimal(str(tx.fee or 0)) for tx in transactions)
            
            # Calculate net capital gains
            net_capital_gains = realized_gains - realized_losses
            
            # Estimate tax liability (simplified calculation)
            # This would need to be customized based on tax jurisdiction
            tax_liability = self._estimate_tax_liability(
                net_capital_gains, short_term_gains, long_term_gains
            )
            
            return TaxReport(
                tax_year=tax_year,
                total_realized_gains=realized_gains,
                total_realized_losses=realized_losses,
                net_capital_gains=net_capital_gains,
                short_term_gains=short_term_gains,
                long_term_gains=long_term_gains,
                wash_sale_losses=wash_sale_losses,
                total_fees=total_fees,
                total_interest_paid=total_interest,
                tax_liability_estimate=tax_liability,
                transactions_count=len(all_transactions)
            )
            
        except Exception as e:
            logger.error(f"Error generating tax report: {e}")
            raise
    
    async def _calculate_tax_pnl(self, transactions: List[Transaction]) -> Tuple[Decimal, Decimal]:
        """Calculate P&L for tax purposes with wash sale detection."""
        
        # Sort transactions by timestamp
        sorted_tx = sorted(transactions, key=lambda x: x.timestamp)
        
        # Track positions and calculate P&L
        position = Decimal('0')
        cost_basis = Decimal('0')
        wash_sale_losses = Decimal('0')
        
        for tx in sorted_tx:
            if tx.type == TransactionType.BUY:
                position += Decimal(str(tx.quantity))
                cost_basis += Decimal(str(tx.total_value or 0))
            elif tx.type == TransactionType.SELL:
                if position > 0:
                    # Calculate P&L for this sale
                    sale_quantity = min(position, Decimal(str(tx.quantity)))
                    avg_cost = cost_basis / position
                    sale_cost = avg_cost * sale_quantity
                    sale_value = Decimal(str(tx.total_value or 0))
                    
                    # Check for wash sale (simplified logic)
                    if sale_value < sale_cost:
                        # Potential wash sale - would need more sophisticated logic
                        wash_sale_losses += sale_cost - sale_value
                    
                    position -= sale_quantity
                    cost_basis = avg_cost * position
        
        # Calculate final P&L
        final_pnl = (position * Decimal('0')) - cost_basis  # Assuming 0 value for remaining position
        
        return final_pnl, wash_sale_losses
    
    def _estimate_tax_liability(
        self, 
        net_capital_gains: Decimal, 
        short_term_gains: Decimal, 
        long_term_gains: Decimal
    ) -> Decimal:
        """Estimate tax liability (simplified US tax calculation)."""
        
        # This is a simplified calculation - real tax software would be much more complex
        if net_capital_gains <= 0:
            return Decimal('0')
        
        # Simplified tax brackets (2024 US rates)
        if net_capital_gains <= 44625:  # 0% bracket
            return Decimal('0')
        elif net_capital_gains <= 200000:  # 15% bracket
            return (net_capital_gains - Decimal('44625')) * Decimal('0.15')
        else:  # 20% bracket
            return (net_capital_gains - Decimal('200000')) * Decimal('0.20') + Decimal('23306.25')
    
    async def _get_asset_prices(self, portfolio: Portfolio) -> Dict[str, Dict]:
        """Get current prices for all assets in the portfolio."""
        
        try:
            asset_ids = set()
            for wallet in portfolio.wallets:
                for asset in wallet.assets:
                    asset_ids.add(asset.asset_id)
            
            # Get prices from price service
            prices = await self.price_service.get_prices(list(asset_ids))
            
            return prices or {}
            
        except Exception as e:
            logger.error(f"Error getting asset prices: {e}")
            return {}
    
    async def _get_asset_transactions(self, asset_id: str, wallet_id: str) -> List[Transaction]:
        """Get all transactions for a specific asset in a wallet."""
        
        # This would integrate with your actual transaction storage
        # For now, returning empty list
        return []
    
    async def _get_wallet_transactions(
        self, 
        wallet_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Transaction]:
        """Get all transactions for a wallet within a date range."""
        
        # This would integrate with your actual transaction storage
        # For now, returning empty list
        return []
    
    async def _get_debt_positions(self, portfolio: Portfolio) -> List[DebtPosition]:
        """Get debt positions for the portfolio."""
        
        # This would integrate with your debt tracking system
        # For now, returning empty list
        return []
    
    async def _calculate_risk_metrics(
        self, 
        portfolio: Portfolio, 
        debt_positions: List[DebtPosition]
    ) -> Dict[str, Any]:
        """Calculate portfolio risk metrics."""
        
        try:
            # Calculate portfolio volatility, beta, Sharpe ratio, etc.
            # This is a simplified implementation
            
            total_value = sum(
                sum(asset.value_usd for asset in wallet.assets)
                for wallet in portfolio.wallets
            )
            
            debt_value = sum(debt.borrowed_value_usd for debt in debt_positions)
            debt_ratio = debt_value / total_value if total_value > 0 else 0
            
            # Risk levels based on debt ratio
            if debt_ratio <= 0.1:
                risk_level = "low"
            elif debt_ratio <= 0.3:
                risk_level = "medium"
            elif debt_ratio <= 0.5:
                risk_level = "high"
            else:
                risk_level = "critical"
            
            return {
                "debt_ratio": float(debt_ratio),
                "risk_level": risk_level,
                "total_value": float(total_value),
                "debt_value": float(debt_value),
                "collateral_ratio": float(
                    sum(debt.collateral_value for debt in debt_positions) / debt_value
                ) if debt_value > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    async def _calculate_performance_metrics(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Calculate portfolio performance metrics."""
        
        try:
            # Calculate time-weighted returns, etc.
            # This is a simplified implementation
            
            return {
                "total_return": 0.0,  # Would calculate actual returns
                "volatility": 0.0,    # Would calculate actual volatility
                "sharpe_ratio": 0.0,  # Would calculate actual Sharpe ratio
                "max_drawdown": 0.0,  # Would calculate actual max drawdown
                "beta": 1.0           # Would calculate actual beta
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}

# Global instance
advanced_portfolio_service = AdvancedPortfolioService()
