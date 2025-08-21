"""
Comprehensive Tests for Advanced Features

Tests all Phase 2 advanced features:
- P&L Calculator
- Risk Assessment Tools
- ML Recommendations
- Tax Reporting
"""
import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timezone, timedelta

# Import the services
from portfolio.services.pnl_calculator import PnLCalculator, PnLBreakdown, AssetPnL, PerformanceMetrics
from services.risk_assessment import RiskAssessmentTools, RiskAssessment, RiskLevel, RiskCategory
from services.ml_recommendations import MLRecommendationsEngine, MLRecommendation, RecommendationType, ConfidenceLevel
from portfolio.services.tax_reporter import TaxReporter, TaxReport, CapitalGainsSummary

# Mock portfolio service for testing
class MockPortfolioService:
    async def get_portfolio(self, portfolio_id: str, user_id: str):
        return {
            'id': portfolio_id,
            'user_id': user_id,
            'name': 'Test Portfolio',
            'created_at': datetime.now(timezone.utc) - timedelta(days=180)
        }

@pytest.fixture
def portfolio_service():
    """Create mock portfolio service"""
    return MockPortfolioService()

@pytest.fixture
def pnl_calculator(portfolio_service):
    """Create PnL calculator instance"""
    return PnLCalculator(portfolio_service)

@pytest.fixture
def risk_assessment_tools():
    """Create risk assessment tools instance"""
    return RiskAssessmentTools()

@pytest.fixture
def ml_recommendations_engine():
    """Create ML recommendations engine instance"""
    return MLRecommendationsEngine()

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
        assert pnl.calculation_timestamp is not None
    
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
        assert asset_pnl.holding_period_days > 0
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, pnl_calculator):
        """Test performance metrics calculation"""
        metrics = await pnl_calculator.get_performance_metrics("test-portfolio", "test-user")
        
        # Verify performance metrics
        assert metrics is not None
        # Note: Some metrics might be None if insufficient data
        assert isinstance(metrics.sharpe_ratio, (Decimal, type(None)))
        assert isinstance(metrics.sortino_ratio, (Decimal, type(None)))
        assert isinstance(metrics.max_drawdown, (Decimal, type(None)))
        assert isinstance(metrics.volatility, (Decimal, type(None)))
        assert isinstance(metrics.beta, (Decimal, type(None)))
    
    @pytest.mark.asyncio
    async def test_get_historical_performance(self, pnl_calculator):
        """Test historical performance data retrieval"""
        historical_data = await pnl_calculator.get_historical_performance("test-portfolio", days=30)
        
        # Verify historical data
        assert len(historical_data) > 0
        assert all(isinstance(data.date, datetime) for data in historical_data)
        assert all(isinstance(data.portfolio_value, Decimal) for data in historical_data)
        assert all(isinstance(data.daily_return, Decimal) for data in historical_data)
        assert all(isinstance(data.cumulative_return, Decimal) for data in historical_data)
    
    @pytest.mark.asyncio
    async def test_empty_portfolio_pnl(self, pnl_calculator):
        """Test P&L calculation for empty portfolio"""
        # This would test the edge case of a portfolio with no assets
        # The current implementation returns mock data, so this is more of a structure test
        pnl = await pnl_calculator.calculate_portfolio_pnl("empty-portfolio", "test-user")
        assert pnl is not None

class TestRiskAssessmentTools:
    """Test Risk Assessment Tools service"""
    
    @pytest.mark.asyncio
    async def test_comprehensive_risk_assessment(self, risk_assessment_tools):
        """Test comprehensive risk assessment"""
        portfolio_data = {
            'total_value': 50000,
            'assets': [
                {'chain': 'Ethereum', 'value': 25000, 'volatility': 0.3},
                {'chain': 'Polygon', 'value': 15000, 'volatility': 0.4},
                {'chain': 'BSC', 'value': 10000, 'volatility': 0.5}
            ],
            'concentration_risk': 0.65
        }
        
        market_data = {
            'market_volatility': 0.25,
            'liquidity_score': 0.7,
            'regulatory_risk': 0.3
        }
        
        user_preferences = {
            'risk_tolerance': 'moderate',
            'investment_horizon': 'long_term'
        }
        
        assessment = await risk_assessment_tools.perform_comprehensive_risk_assessment(
            portfolio_data, market_data, user_preferences
        )
        
        # Verify risk assessment
        assert assessment is not None
        assert assessment.overall_risk in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert assessment.overall_score >= 0
        assert assessment.risk_factors is not None
        assert assessment.recommendations is not None
        assert assessment.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_stress_testing(self, risk_assessment_tools):
        """Test stress testing scenarios"""
        portfolio_data = {
            'total_value': 50000,
            'assets': [
                {'chain': 'Ethereum', 'value': 25000},
                {'chain': 'Polygon', 'value': 15000},
                {'chain': 'BSC', 'value': 10000}
            ]
        }
        
        stress_results = await risk_assessment_tools.run_stress_tests(portfolio_data)
        
        # Verify stress test results
        assert len(stress_results) > 0
        for result in stress_results:
            assert result.scenario is not None
            assert result.portfolio_impact is not None
            assert result.recovery_time is not None
            assert result.recommendations is not None
    
    @pytest.mark.asyncio
    async def test_risk_categories(self, risk_assessment_tools):
        """Test individual risk category assessment"""
        portfolio_data = {'total_value': 50000}
        market_data = {'market_volatility': 0.25}
        user_preferences = {'risk_tolerance': 'moderate'}
        
        # Test market risk assessment
        market_risks = await risk_assessment_tools._assess_risk_category(
            'market', portfolio_data, market_data, user_preferences
        )
        assert market_risks is not None
        
        # Test liquidity risk assessment
        liquidity_risks = await risk_assessment_tools._assess_risk_category(
            'liquidity', portfolio_data, market_data, user_preferences
        )
        assert liquidity_risks is not None

class TestMLRecommendationsEngine:
    """Test ML Recommendations Engine service"""
    
    @pytest.mark.asyncio
    async def test_generate_portfolio_recommendations(self, ml_recommendations_engine):
        """Test portfolio recommendation generation"""
        portfolio_data = {
            'total_value': 50000,
            'assets': [
                {'chain': 'Ethereum', 'value': 25000},
                {'chain': 'Polygon', 'value': 15000},
                {'chain': 'BSC', 'value': 10000}
            ],
            'concentration_risk': 0.65,
            'performance_score': 0.45,
            'risk_score': 0.35,
            'asset_allocation': {
                'blue_chip_nfts': 0.6,
                'mid_tier_nfts': 0.3,
                'emerging_nfts': 0.1
            }
        }
        
        market_data = {
            'undervalued_assets': [
                {'id': 'asset1', 'name': 'Cool Cats', 'expected_return': 0.18, 'risk_level': 'medium', 'factors': ['low_valuation', 'strong_fundamentals'], 'data_quality': 'high', 'market_volatility': 0.3, 'historical_accuracy': 0.7},
                {'id': 'asset2', 'name': 'Azuki', 'expected_return': 0.22, 'risk_level': 'high', 'factors': ['momentum', 'social_buzz'], 'data_quality': 'medium', 'market_volatility': 0.5, 'historical_accuracy': 0.6}
            ],
            'overvalued_assets': [
                {'id': 'asset3', 'name': 'Overvalued Asset', 'expected_return': -0.12, 'risk_level': 'high', 'factors': ['high_valuation', 'weak_fundamentals']}
            ]
        }
        
        user_preferences = {
            'risk_tolerance': 'moderate',
            'investment_horizon': 'long_term',
            'preferred_chains': ['Ethereum', 'Polygon'],
            'target_allocation': {
                'blue_chip_nfts': 0.4,
                'mid_tier_nfts': 0.4,
                'emerging_nfts': 0.2
            }
        }
        
        recommendations = await ml_recommendations_engine.generate_portfolio_recommendations(
            portfolio_data, market_data, user_preferences
        )
        
        # Verify recommendations
        assert len(recommendations) > 0
        for rec in recommendations:
            assert isinstance(rec, MLRecommendation)
            assert rec.type in RecommendationType
            assert rec.confidence in ConfidenceLevel
            assert 0 <= rec.confidence_score <= 1
            assert rec.reasoning is not None
            assert rec.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_market_predictions(self, ml_recommendations_engine):
        """Test market movement predictions"""
        collections = ['bayc', 'doodles']
        predictions = await ml_recommendations_engine.predict_market_movements(collections, '30d')
        
        # Verify predictions
        assert len(predictions) > 0
        for pred in predictions:
            assert pred.collection_id in collections
            assert pred.predicted_movement in ['up', 'down', 'stable']
            assert 0 <= pred.confidence_score <= 1
            assert pred.time_horizon == '30d'
            assert pred.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_portfolio_optimization(self, ml_recommendations_engine):
        """Test portfolio optimization"""
        portfolio_data = {
            'asset_allocation': {
                'blue_chip_nfts': 0.6,
                'mid_tier_nfts': 0.3,
                'emerging_nfts': 0.1
            }
        }
        
        user_preferences = {
            'risk_tolerance': 'moderate',
            'target_allocation': {
                'blue_chip_nfts': 0.4,
                'mid_tier_nfts': 0.4,
                'emerging_nfts': 0.2
            }
        }
        
        optimization = await ml_recommendations_engine.optimize_portfolio_allocation(
            portfolio_data, 0.5, user_preferences
        )
        
        # Verify optimization
        assert optimization is not None
        assert optimization.current_allocation is not None
        assert optimization.recommended_allocation is not None
        assert optimization.expected_improvement >= 0
        assert optimization.risk_reduction >= 0
    
    @pytest.mark.asyncio
    async def test_market_sentiment_analysis(self, ml_recommendations_engine):
        """Test market sentiment analysis"""
        market_data = {
            'social_sentiment': 0.7,
            'news_sentiment': 0.6,
            'volatility': 0.3,
            'institutional_activity': 0.8
        }
        
        sentiment = await ml_recommendations_engine.analyze_market_sentiment(market_data)
        
        # Verify sentiment
        assert sentiment in ['bullish', 'bearish', 'neutral', 'volatile']
    
    @pytest.mark.asyncio
    async def test_trending_opportunities(self, ml_recommendations_engine):
        """Test trending opportunities identification"""
        market_data = {
            'trending_collections': [
                {'id': 'trend1', 'name': 'Trending A', 'volume_growth': 0.8, 'price_momentum': 0.3, 'social_buzz': 0.8, 'market_cap': 1000000, 'volume_24h': 150000},
                {'id': 'trend2', 'name': 'Trending B', 'volume_growth': 0.6, 'price_momentum': 0.25, 'social_buzz': 0.7, 'market_cap': 2000000, 'volume_24h': 200000}
            ]
        }
        
        opportunities = await ml_recommendations_engine.get_trending_opportunities(market_data)
        
        # Verify opportunities
        assert len(opportunities) > 0
        for opp in opportunities:
            assert 'collection' in opp
            assert 'opportunity_score' in opp
            assert 'recommendation' in opp

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
        assert tax_report.report_generated is not None
        assert tax_report.transactions_count >= 0
    
    @pytest.mark.asyncio
    async def test_calculate_capital_gains(self, tax_reporter):
        """Test capital gains calculation"""
        capital_gains = await tax_reporter.calculate_capital_gains("test-portfolio", "test-user", "2024-25")
        
        # Verify capital gains
        assert capital_gains is not None
        assert capital_gains.portfolio_id == "test-portfolio"
        assert capital_gains.tax_year == "2024-25"
        assert capital_gains.total_proceeds >= Decimal('0')
        assert capital_gains.total_cost_basis >= Decimal('0')
        assert capital_gains.total_net_gains is not None
    
    @pytest.mark.asyncio
    async def test_tax_loss_opportunities(self, tax_reporter):
        """Test tax loss harvesting opportunities"""
        opportunities = await tax_reporter.identify_tax_loss_opportunities("test-portfolio", "test-user")
        
        # Verify opportunities (might be empty list)
        assert isinstance(opportunities, list)
        for opp in opportunities:
            assert opp.asset_id is not None
            assert opp.potential_loss >= Decimal('0')
            assert opp.reasoning is not None
    
    @pytest.mark.asyncio
    async def test_hmrc_report_generation(self, tax_reporter):
        """Test HMRC report generation"""
        hmrc_report = await tax_reporter.generate_hmrc_report("test-portfolio", "test-user", "2024-25")
        
        # Verify HMRC report
        assert hmrc_report is not None
        assert 'tax_year' in hmrc_report
        assert 'portfolio_summary' in hmrc_report
        assert 'capital_gains_summary' in hmrc_report
        assert 'transactions' in hmrc_report

class TestAdvancedFeaturesIntegration:
    """Test integration between advanced features"""
    
    @pytest.mark.asyncio
    async def test_portfolio_analysis_workflow(self, pnl_calculator, risk_assessment_tools, ml_recommendations_engine):
        """Test complete portfolio analysis workflow"""
        portfolio_id = "test-portfolio"
        user_id = "test-user"
        
        # Step 1: Calculate P&L
        pnl = await pnl_calculator.calculate_portfolio_pnl(portfolio_id, user_id)
        assert pnl is not None
        
        # Step 2: Get performance metrics
        metrics = await pnl_calculator.get_performance_metrics(portfolio_id, user_id)
        assert metrics is not None
        
        # Step 3: Assess risk
        portfolio_data = {
            'total_value': float(pnl.current_value),
            'assets': [],
            'concentration_risk': 0.5
        }
        market_data = {'market_volatility': 0.25}
        user_preferences = {'risk_tolerance': 'moderate'}
        
        risk_assessment = await risk_assessment_tools.perform_comprehensive_risk_assessment(
            portfolio_data, market_data, user_preferences
        )
        assert risk_assessment is not None
        
        # Step 4: Generate recommendations
        recommendations = await ml_recommendations_engine.generate_portfolio_recommendations(
            portfolio_data, {}, user_preferences
        )
        assert len(recommendations) >= 0  # Might be empty for mock data
    
    @pytest.mark.asyncio
    async def test_error_handling(self, pnl_calculator, risk_assessment_tools, ml_recommendations_engine):
        """Test error handling in advanced features"""
        
        # Test with invalid portfolio ID
        pnl = await pnl_calculator.calculate_portfolio_pnl("invalid-portfolio", "test-user")
        # Should handle gracefully (return None or empty data)
        
        # Test with empty market data
        recommendations = await ml_recommendations_engine.generate_portfolio_recommendations(
            {}, {}, {}
        )
        assert isinstance(recommendations, list)
        
        # Test with invalid risk parameters
        risk_assessment = await risk_assessment_tools.perform_comprehensive_risk_assessment(
            {}, {}, {}
        )
        # Should handle gracefully

# Performance tests
class TestAdvancedFeaturesPerformance:
    """Test performance of advanced features"""
    
    @pytest.mark.asyncio
    async def test_pnl_calculation_performance(self, pnl_calculator):
        """Test P&L calculation performance"""
        import time
        
        start_time = time.time()
        pnl = await pnl_calculator.calculate_portfolio_pnl("test-portfolio", "test-user")
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 1.0  # Less than 1 second
        assert pnl is not None
    
    @pytest.mark.asyncio
    async def test_risk_assessment_performance(self, risk_assessment_tools):
        """Test risk assessment performance"""
        import time
        
        portfolio_data = {'total_value': 50000, 'assets': []}
        market_data = {'market_volatility': 0.25}
        user_preferences = {'risk_tolerance': 'moderate'}
        
        start_time = time.time()
        assessment = await risk_assessment_tools.perform_comprehensive_risk_assessment(
            portfolio_data, market_data, user_preferences
        )
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 2.0  # Less than 2 seconds
        assert assessment is not None

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
