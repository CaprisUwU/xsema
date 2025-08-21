"""
Unit Tests for Phase 2 Services

Tests the new advanced portfolio management services:
- PnL Calculator
- Debt Tracker  
- Tax Reporter
"""
import pytest
from decimal import Decimal

from portfolio.services.pnl_calculator import PnLCalculator
from portfolio.services.debt_tracker import DebtTracker, RiskLevel
from portfolio.services.tax_reporter import TaxReporter

@pytest.fixture
def portfolio_service():
    """Create portfolio service instance"""
    from portfolio.services.portfolio_service import PortfolioService
    return PortfolioService()

@pytest.fixture
def pnl_calculator(portfolio_service):
    """Create PnL calculator instance"""
    return PnLCalculator(portfolio_service)

@pytest.fixture
def debt_tracker(portfolio_service):
    """Create debt tracker instance"""
    return DebtTracker(portfolio_service)

@pytest.fixture
def tax_reporter(portfolio_service):
    """Create tax reporter instance"""
    return TaxReporter(portfolio_service)

class TestPnLCalculator:
    """Test PnL Calculator service"""
    
    @pytest.mark.asyncio
    async def test_calculate_portfolio_pnl(self, pnl_calculator):
        """Test portfolio P&L calculation"""
        pnl = await pnl_calculator.calculate_portfolio_pnl("test-portfolio", "test-user")
        
        # Verify P&L calculation
        assert pnl is not None
        assert pnl.portfolio_id == "test-portfolio"
        assert pnl.total_cost_basis >= Decimal('0')
        assert pnl.current_value >= Decimal('0')
        assert pnl.total_pnl == pnl.unrealized_pnl + pnl.realized_pnl
    
    @pytest.mark.asyncio
    async def test_calculate_asset_pnl(self, pnl_calculator):
        """Test asset P&L calculation"""
        asset_pnl = await pnl_calculator.calculate_asset_pnl("asset_1", "test-portfolio", "test-user")
        
        # Verify asset P&L calculation
        assert asset_pnl is not None
        assert asset_pnl.asset_id == "asset_1"
        assert asset_pnl.asset_name is not None
        assert asset_pnl.quantity > Decimal('0')
        assert asset_pnl.cost_basis > Decimal('0')
        assert asset_pnl.current_value > Decimal('0')

class TestDebtTracker:
    """Test Debt Tracker service"""
    
    @pytest.mark.asyncio
    async def test_track_debt_position(self, debt_tracker):
        """Test debt position tracking"""
        debt_position = await debt_tracker.track_debt_position("test-portfolio", "test-user")
        
        # Verify debt position
        assert debt_position is not None
        assert debt_position.portfolio_id == "test-portfolio"
        assert debt_position.total_debt >= Decimal('0')
        assert debt_position.total_collateral >= Decimal('0')
        assert debt_position.leverage_ratio >= Decimal('0')
        assert debt_position.risk_level in RiskLevel
    
    @pytest.mark.asyncio
    async def test_calculate_leverage_metrics(self, debt_tracker):
        """Test leverage metrics calculation"""
        leverage_metrics = await debt_tracker.calculate_leverage_metrics("test-portfolio", "test-user")
        
        # Verify leverage metrics
        assert leverage_metrics is not None
        assert leverage_metrics.portfolio_id == "test-portfolio"
        assert leverage_metrics.current_leverage >= Decimal('0')
        assert leverage_metrics.max_safe_leverage > Decimal('0')
        assert leverage_metrics.risk_score >= 0 and leverage_metrics.risk_score <= 100

class TestTaxReporter:
    """Test Tax Reporter service"""
    
    @pytest.mark.asyncio
    async def test_generate_tax_report(self, tax_reporter):
        """Test tax report generation"""
        tax_report = await tax_reporter.generate_tax_report("test-portfolio", "test-user", "2024-25")
        
        # Verify tax report
        assert tax_report is not None
        assert tax_report.portfolio_id == "test-portfolio"
        assert tax_report.tax_year == "2024-25"
        assert tax_report.total_proceeds >= Decimal('0')
        assert tax_report.total_cost_basis >= Decimal('0')
        assert tax_report.total_gains >= Decimal('0')
    
    @pytest.mark.asyncio
    async def test_calculate_capital_gains(self, tax_reporter):
        """Test capital gains calculation"""
        capital_gains = await tax_reporter.calculate_capital_gains("test-portfolio", "test-user", "2024-25")
        
        # Verify capital gains
        assert capital_gains is not None
        assert capital_gains.portfolio_id == "test-portfolio"
        assert capital_gains.tax_year == "2024-25"
        assert capital_gains.short_term_gains >= Decimal('0')
        assert capital_gains.long_term_gains >= Decimal('0')
        assert capital_gains.annual_exemption > Decimal('0')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
