"""
Tax Reporting & Compliance Service

This service provides comprehensive tax reporting including:
- Capital gains calculations
- HMRC-compliant reports
- Tax loss harvesting opportunities
- Audit trail generation
"""
import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum

from portfolio.models.portfolio import Portfolio
from portfolio.services.portfolio_service import PortfolioService

logger = logging.getLogger(__name__)

class TaxYear(Enum):
    """UK tax year definitions"""
    TAX_YEAR_2024_25 = "2024-25"  # 6 April 2024 to 5 April 2025
    TAX_YEAR_2023_24 = "2023-24"  # 6 April 2023 to 5 April 2025
    TAX_YEAR_2022_23 = "2022-23"  # 6 April 2022 to 5 April 2023

class GainType(Enum):
    """Type of capital gain"""
    SHORT_TERM = "short_term"  # < 1 year
    LONG_TERM = "long_term"     # >= 1 year

@dataclass
class TaxReport:
    """Comprehensive tax report for a portfolio"""
    portfolio_id: str
    tax_year: str
    total_proceeds: Decimal
    total_cost_basis: Decimal
    total_gains: Decimal
    total_losses: Decimal
    net_gains: Decimal
    annual_exemption_used: Decimal
    annual_exemption_remaining: Decimal
    taxable_gains: Decimal
    estimated_tax: Decimal
    report_generated: datetime
    transactions_count: int

@dataclass
class CapitalGainsSummary:
    """Capital gains summary for tax reporting"""
    portfolio_id: str
    tax_year: str
    short_term_gains: Decimal
    long_term_gains: Decimal
    short_term_losses: Decimal
    long_term_losses: Decimal
    net_short_term: Decimal
    net_long_term: Decimal
    total_net_gains: Decimal
    annual_exemption: Decimal
    taxable_amount: Decimal

@dataclass
class TaxOpportunity:
    """Tax loss harvesting opportunity"""
    opportunity_id: str
    asset_id: str
    asset_name: str
    current_loss: Decimal
    potential_tax_savings: Decimal
    holding_period_days: int
    recommendation: str
    created_at: datetime

@dataclass
class TransactionRecord:
    """Transaction record for tax purposes"""
    transaction_id: str
    asset_id: str
    asset_name: str
    transaction_type: str  # "buy", "sell", "transfer"
    quantity: Decimal
    price_per_unit: Decimal
    total_amount: Decimal
    transaction_date: datetime
    cost_basis: Decimal
    proceeds: Decimal
    gain_loss: Decimal
    gain_type: GainType
    fees: Decimal
    notes: str

class TaxReporter:
    """Advanced tax reporting and compliance service"""
    
    def __init__(self, portfolio_service: PortfolioService):
        self.portfolio_service = portfolio_service
        self.logger = logging.getLogger(__name__)
        
        # UK tax constants
        self.ANNUAL_EXEMPTION_2024_25 = Decimal('3000')  # £3,000 for 2024-25
        self.ANNUAL_EXEMPTION_2023_24 = Decimal('6000')  # £6,000 for 2023-24
        self.CAPITAL_GAINS_RATES = {
            'basic_rate': Decimal('0.10'),      # 10% for basic rate taxpayers
            'higher_rate': Decimal('0.20'),     # 20% for higher rate taxpayers
            'additional_rate': Decimal('0.20')  # 20% for additional rate taxpayers
        }
        
        # Tax year dates
        self.TAX_YEAR_DATES = {
            TaxYear.TAX_YEAR_2024_25: {
                'start': datetime(2024, 4, 6, tzinfo=timezone.utc),
                'end': datetime(2025, 4, 5, tzinfo=timezone.utc)
            },
            TaxYear.TAX_YEAR_2023_24: {
                'start': datetime(2023, 4, 6, tzinfo=timezone.utc),
                'end': datetime(2024, 4, 5, tzinfo=timezone.utc)
            }
        }
    
    async def generate_tax_report(self, portfolio_id: str, user_id: str, tax_year: str) -> Optional[TaxReport]:
        """Generate comprehensive tax report for a portfolio"""
        try:
            # Get portfolio
            portfolio = await self.portfolio_service.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                self.logger.warning(f"Portfolio {portfolio_id} not found for user {user_id}")
                return None
            
            # Get transactions for the tax year
            transactions = await self._get_transactions_for_tax_year(portfolio_id, tax_year)
            if not transactions:
                return await self._create_empty_tax_report(portfolio_id, tax_year)
            
            # Calculate tax summary
            tax_summary = await self.calculate_capital_gains(portfolio_id, user_id, tax_year)
            if not tax_summary:
                return None
            
            # Calculate tax liability
            annual_exemption = self._get_annual_exemption(tax_year)
            annual_exemption_used = min(annual_exemption, tax_summary.total_net_gains)
            annual_exemption_remaining = annual_exemption - annual_exemption_used
            taxable_gains = max(Decimal('0'), tax_summary.total_net_gains - annual_exemption_used)
            
            # Estimate tax (assuming basic rate for now)
            estimated_tax = taxable_gains * self.CAPITAL_GAINS_RATES['basic_rate']
            
            # Calculate totals
            total_proceeds = sum(t.proceeds for t in transactions if t.transaction_type == "sell")
            total_cost_basis = sum(t.cost_basis for t in transactions if t.transaction_type == "sell")
            
            tax_report = TaxReport(
                portfolio_id=portfolio_id,
                tax_year=tax_year,
                total_proceeds=total_proceeds,
                total_cost_basis=total_cost_basis,
                total_gains=tax_summary.total_net_gains,
                total_losses=abs(min(Decimal('0'), tax_summary.total_net_gains)),
                net_gains=tax_summary.total_net_gains,
                annual_exemption_used=annual_exemption_used,
                annual_exemption_remaining=annual_exemption_remaining,
                taxable_gains=taxable_gains,
                estimated_tax=estimated_tax,
                report_generated=datetime.now(timezone.utc),
                transactions_count=len(transactions)
            )
            
            self.logger.info(f"Tax report generated for portfolio {portfolio_id}, tax year {tax_year}")
            return tax_report
            
        except Exception as e:
            self.logger.error(f"Error generating tax report for portfolio {portfolio_id}: {str(e)}")
            return None
    
    async def calculate_capital_gains(self, portfolio_id: str, user_id: str, tax_year: str) -> Optional[CapitalGainsSummary]:
        """Calculate capital gains for tax reporting"""
        try:
            # Get transactions for the tax year
            transactions = await self._get_transactions_for_tax_year(portfolio_id, tax_year)
            if not transactions:
                return None
            
            # Separate gains and losses by holding period
            short_term_gains = Decimal('0')
            long_term_gains = Decimal('0')
            short_term_losses = Decimal('0')
            long_term_losses = Decimal('0')
            
            for transaction in transactions:
                if transaction.transaction_type == "sell":
                    if transaction.gain_loss > 0:
                        if transaction.gain_type == GainType.SHORT_TERM:
                            short_term_gains += transaction.gain_loss
                        else:
                            long_term_gains += transaction.gain_loss
                    else:
                        if transaction.gain_type == GainType.SHORT_TERM:
                            short_term_losses += abs(transaction.gain_loss)
                        else:
                            long_term_losses += abs(transaction.gain_loss)
            
            # Calculate net amounts
            net_short_term = short_term_gains - short_term_losses
            net_long_term = long_term_gains - long_term_losses
            total_net_gains = net_short_term + net_long_term
            
            # Get annual exemption
            annual_exemption = self._get_annual_exemption(tax_year)
            taxable_amount = max(Decimal('0'), total_net_gains - annual_exemption)
            
            capital_gains_summary = CapitalGainsSummary(
                portfolio_id=portfolio_id,
                tax_year=tax_year,
                short_term_gains=short_term_gains,
                long_term_gains=long_term_gains,
                short_term_losses=short_term_losses,
                long_term_losses=long_term_losses,
                net_short_term=net_short_term,
                net_long_term=net_long_term,
                total_net_gains=total_net_gains,
                annual_exemption=annual_exemption,
                taxable_amount=taxable_amount
            )
            
            return capital_gains_summary
            
        except Exception as e:
            self.logger.error(f"Error calculating capital gains for portfolio {portfolio_id}: {str(e)}")
            return None
    
    async def identify_tax_loss_opportunities(self, portfolio_id: str, user_id: str) -> List[TaxOpportunity]:
        """Identify tax loss harvesting opportunities"""
        try:
            opportunities = []
            
            # Get current portfolio assets
            assets = await self._get_portfolio_assets(portfolio_id)
            if not assets:
                return opportunities
            
            # Check each asset for potential losses
            for asset in assets:
                if asset.current_value < asset.cost_basis:
                    # Potential loss
                    current_loss = asset.cost_basis - asset.current_value
                    holding_period_days = await self._calculate_holding_period(asset.id)
                    
                    # Calculate potential tax savings (assuming 20% rate)
                    potential_tax_savings = current_loss * self.CAPITAL_GAINS_RATES['higher_rate']
                    
                    # Generate recommendation
                    if holding_period_days < 365:
                        recommendation = "Consider selling to realize short-term loss for tax purposes"
                    else:
                        recommendation = "Consider selling to realize long-term loss for tax purposes"
                    
                    opportunity = TaxOpportunity(
                        opportunity_id=f"tax_loss_{asset.id}",
                        asset_id=asset.id,
                        asset_name=asset.name,
                        current_loss=current_loss,
                        potential_tax_savings=potential_tax_savings,
                        holding_period_days=holding_period_days,
                        recommendation=recommendation,
                        created_at=datetime.now(timezone.utc)
                    )
                    
                    opportunities.append(opportunity)
            
            # Sort by potential tax savings
            opportunities.sort(key=lambda x: x.potential_tax_savings, reverse=True)
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error identifying tax loss opportunities for portfolio {portfolio_id}: {str(e)}")
            return []
    
    async def generate_hmrc_report(self, portfolio_id: str, user_id: str, tax_year: str) -> Optional[Dict[str, Any]]:
        """Generate HMRC-compliant tax report"""
        try:
            # Get tax report
            tax_report = await self.generate_tax_report(portfolio_id, user_id, tax_year)
            if not tax_report:
                return None
            
            # Get capital gains summary
            capital_gains = await self.calculate_capital_gains(portfolio_id, user_id, tax_year)
            if not capital_gains:
                return None
            
            # Get transactions
            transactions = await self._get_transactions_for_tax_year(portfolio_id, tax_year)
            
            # Format for HMRC
            hmrc_report = {
                "tax_year": tax_year,
                "portfolio_id": portfolio_id,
                "summary": {
                    "total_proceeds": float(tax_report.total_proceeds),
                    "total_cost_basis": float(tax_report.total_cost_basis),
                    "total_gains": float(tax_report.total_gains),
                    "total_losses": float(tax_report.total_losses),
                    "net_gains": float(tax_report.net_gains),
                    "annual_exemption_used": float(tax_report.annual_exemption_used),
                    "annual_exemption_remaining": float(tax_report.annual_exemption_remaining),
                    "taxable_gains": float(tax_report.taxable_gains),
                    "estimated_tax": float(tax_report.estimated_tax)
                },
                "capital_gains": {
                    "short_term_gains": float(capital_gains.short_term_gains),
                    "long_term_gains": float(capital_gains.long_term_gains),
                    "short_term_losses": float(capital_gains.short_term_losses),
                    "long_term_losses": float(capital_gains.long_term_losses),
                    "net_short_term": float(capital_gains.net_short_term),
                    "net_long_term": float(capital_gains.net_long_term),
                    "total_net_gains": float(capital_gains.total_net_gains)
                },
                "transactions": [
                    {
                        "date": t.transaction_date.strftime("%d/%m/%Y"),
                        "asset_name": t.asset_name,
                        "type": t.transaction_type,
                        "quantity": float(t.quantity),
                        "proceeds": float(t.proceeds),
                        "cost_basis": float(t.cost_basis),
                        "gain_loss": float(t.gain_loss),
                        "gain_type": t.gain_type.value
                    }
                    for t in transactions if t.transaction_type == "sell"
                ],
                "report_generated": tax_report.report_generated.strftime("%d/%m/%Y %H:%M"),
                "hmrc_compliance": "This report is formatted for HMRC Self Assessment"
            }
            
            return hmrc_report
            
        except Exception as e:
            self.logger.error(f"Error generating HMRC report for portfolio {portfolio_id}: {str(e)}")
            return None
    
    async def get_tax_year_summary(self, portfolio_id: str, user_id: str) -> Dict[str, Any]:
        """Get summary of all tax years for a portfolio"""
        try:
            tax_years = [year.value for year in TaxYear]
            summary = {}
            
            for tax_year in tax_years:
                # Get basic tax info for each year
                capital_gains = await self.calculate_capital_gains(portfolio_id, user_id, tax_year)
                if capital_gains:
                    summary[tax_year] = {
                        "net_gains": float(capital_gains.total_net_gains),
                        "taxable_amount": float(capital_gains.taxable_amount),
                        "annual_exemption": float(capital_gains.annual_exemption),
                        "transactions_count": await self._get_transaction_count(portfolio_id, tax_year)
                    }
                else:
                    summary[tax_year] = {
                        "net_gains": 0.0,
                        "taxable_amount": 0.0,
                        "annual_exemption": float(self._get_annual_exemption(tax_year)),
                        "transactions_count": 0
                    }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting tax year summary for portfolio {portfolio_id}: {str(e)}")
            return {}
    
    # Private helper methods
    
    def _get_annual_exemption(self, tax_year: str) -> Decimal:
        """Get annual exemption amount for a tax year"""
        if tax_year == TaxYear.TAX_YEAR_2024_25.value:
            return self.ANNUAL_EXEMPTION_2024_25
        elif tax_year == TaxYear.TAX_YEAR_2023_24.value:
            return self.ANNUAL_EXEMPTION_2023_24
        else:
            return self.ANNUAL_EXEMPTION_2024_25  # Default to current year
    
    async def _get_transactions_for_tax_year(self, portfolio_id: str, tax_year: str) -> List[TransactionRecord]:
        """Get transactions for a specific tax year"""
        try:
            # Get tax year dates
            if tax_year == TaxYear.TAX_YEAR_2024_25.value:
                start_date = self.TAX_YEAR_DATES[TaxYear.TAX_YEAR_2024_25]['start']
                end_date = self.TAX_YEAR_DATES[TaxYear.TAX_YEAR_2024_25]['end']
            elif tax_year == TaxYear.TAX_YEAR_2023_24.value:
                start_date = self.TAX_YEAR_DATES[TaxYear.TAX_YEAR_2023_24]['start']
                end_date = self.TAX_YEAR_DATES[TaxYear.TAX_YEAR_2023_24]['end']
            else:
                # Default to current tax year
                start_date = self.TAX_YEAR_DATES[TaxYear.TAX_YEAR_2024_25]['start']
                end_date = self.TAX_YEAR_DATES[TaxYear.TAX_YEAR_2024_25]['end']
            
            # This would typically fetch from a transaction service
            # For now, return mock data
            return [
                TransactionRecord(
                    transaction_id="tx_1",
                    asset_id="asset_1",
                    asset_name="Bored Ape #1234",
                    transaction_type="sell",
                    quantity=Decimal('1'),
                    price_per_unit=Decimal('75.0'),
                    total_amount=Decimal('75.0'),
                    transaction_date=datetime(2024, 12, 15, tzinfo=timezone.utc),
                    cost_basis=Decimal('50.0'),
                    proceeds=Decimal('75.0'),
                    gain_loss=Decimal('25.0'),
                    gain_type=GainType.SHORT_TERM,
                    fees=Decimal('2.0'),
                    notes="Sold for profit"
                ),
                TransactionRecord(
                    transaction_id="tx_2",
                    asset_id="asset_2",
                    asset_name="CryptoPunk #5678",
                    transaction_type="sell",
                    quantity=Decimal('1'),
                    price_per_unit=Decimal('30.0'),
                    total_amount=Decimal('30.0'),
                    transaction_date=datetime(2024, 10, 20, tzinfo=timezone.utc),
                    cost_basis=Decimal('35.0'),
                    proceeds=Decimal('30.0'),
                    gain_loss=Decimal('-5.0'),
                    gain_type=GainType.SHORT_TERM,
                    fees=Decimal('1.5'),
                    notes="Sold at loss"
                )
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting transactions for tax year {tax_year}: {str(e)}")
            return []
    
    async def _get_portfolio_assets(self, portfolio_id: str) -> List[Any]:
        """Get portfolio assets"""
        # This would typically fetch from an asset service
        # For now, return mock data
        return [
            type('Asset', (), {
                'id': 'asset_1',
                'name': 'Bored Ape #1234',
                'cost_basis': Decimal('50.0'),
                'current_value': Decimal('45.0')  # Loss position
            })(),
            type('Asset', (), {
                'id': 'asset_2',
                'name': 'CryptoPunk #5678',
                'cost_basis': Decimal('25.0'),
                'current_value': Decimal('30.0')  # Gain position
            })()
        ]
    
    async def _calculate_holding_period(self, asset_id: str) -> int:
        """Calculate holding period in days for an asset"""
        # This would typically fetch from asset purchase history
        # For now, return mock data
        return 180  # 6 months
    
    async def _get_transaction_count(self, portfolio_id: str, tax_year: str) -> int:
        """Get transaction count for a tax year"""
        transactions = await self._get_transactions_for_tax_year(portfolio_id, tax_year)
        return len(transactions)
    
    async def _create_empty_tax_report(self, portfolio_id: str, tax_year: str) -> TaxReport:
        """Create empty tax report for portfolios with no transactions"""
        return TaxReport(
            portfolio_id=portfolio_id,
            tax_year=tax_year,
            total_proceeds=Decimal('0'),
            total_cost_basis=Decimal('0'),
            total_gains=Decimal('0'),
            total_losses=Decimal('0'),
            net_gains=Decimal('0'),
            annual_exemption_used=Decimal('0'),
            annual_exemption_remaining=self._get_annual_exemption(tax_year),
            taxable_gains=Decimal('0'),
            estimated_tax=Decimal('0'),
            report_generated=datetime.now(timezone.utc),
            transactions_count=0
        )
