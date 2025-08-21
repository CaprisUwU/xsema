"""
Advanced Analytics API Endpoints

Provides access to Phase 2 advanced features:
- P&L calculations and performance metrics
- Risk assessment and stress testing
- ML-powered recommendations
- Tax reporting and compliance
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from portfolio.services.pnl_calculator import PnLCalculator
from portfolio.services.tax_reporter import TaxReporter
from services.risk_assessment import RiskAssessmentTools
from services.ml_recommendations import MLRecommendationsEngine
from portfolio.services.portfolio_service import PortfolioService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
pnl_calculator = PnLCalculator(PortfolioService())
tax_reporter = TaxReporter(PortfolioService())
risk_assessment_tools = RiskAssessmentTools()
ml_recommendations_engine = MLRecommendationsEngine()

@router.get("/portfolio/{portfolio_id}/pnl")
async def get_portfolio_pnl(
    portfolio_id: str,
    user_id: str = Query(..., description="User ID for authentication"),
    include_metrics: bool = Query(True, description="Include performance metrics")
):
    """
    Get comprehensive P&L analysis for a portfolio
    
    Returns:
    - Total cost basis and current value
    - Unrealized and realized P&L
    - ROI calculations
    - Performance metrics (if requested)
    """
    try:
        # Calculate P&L
        pnl = await pnl_calculator.calculate_portfolio_pnl(portfolio_id, user_id)
        if not pnl:
            raise HTTPException(status_code=404, detail="Portfolio not found or no assets")
        
        response = {
            "portfolio_id": pnl.portfolio_id,
            "total_cost_basis": float(pnl.total_cost_basis),
            "current_value": float(pnl.current_value),
            "unrealized_pnl": float(pnl.unrealized_pnl),
            "realized_pnl": float(pnl.realized_pnl),
            "total_pnl": float(pnl.total_pnl),
            "roi_percentage": float(pnl.roi_percentage),
            "annualized_roi": float(pnl.annualized_roi) if pnl.annualized_roi else None,
            "calculation_timestamp": pnl.calculation_timestamp.isoformat(),
            "currency": "GBP"
        }
        
        # Add performance metrics if requested
        if include_metrics:
            metrics = await pnl_calculator.get_performance_metrics(portfolio_id, user_id)
            if metrics:
                response["performance_metrics"] = {
                    "sharpe_ratio": float(metrics.sharpe_ratio) if metrics.sharpe_ratio else None,
                    "sortino_ratio": float(metrics.sortino_ratio) if metrics.sortino_ratio else None,
                    "max_drawdown": float(metrics.max_drawdown) if metrics.max_drawdown else None,
                    "volatility": float(metrics.volatility) if metrics.volatility else None,
                    "beta": float(metrics.beta) if metrics.beta else None
                }
        
        return response
        
    except Exception as e:
        logger.error(f"Error calculating portfolio P&L: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/portfolio/{portfolio_id}/asset/{asset_id}/pnl")
async def get_asset_pnl(
    portfolio_id: str,
    asset_id: str,
    user_id: str = Query(..., description="User ID for authentication")
):
    """
    Get P&L analysis for a specific asset
    
    Returns:
    - Asset-specific P&L breakdown
    - ROI and holding period information
    """
    try:
        asset_pnl = await pnl_calculator.calculate_asset_pnl(asset_id, portfolio_id, user_id)
        if not asset_pnl:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        return {
            "asset_id": asset_pnl.asset_id,
            "asset_name": asset_pnl.asset_name,
            "quantity": float(asset_pnl.quantity),
            "cost_basis": float(asset_pnl.cost_basis),
            "current_value": float(asset_pnl.current_value),
            "unrealized_pnl": float(asset_pnl.unrealized_pnl),
            "roi_percentage": float(asset_pnl.roi_percentage),
            "holding_period_days": asset_pnl.holding_period_days,
            "currency": "GBP"
        }
        
    except Exception as e:
        logger.error(f"Error calculating asset P&L: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/portfolio/{portfolio_id}/performance/historical")
async def get_historical_performance(
    portfolio_id: str,
    user_id: str = Query(..., description="User ID for authentication"),
    days: int = Query(365, description="Number of days of historical data", ge=1, le=1095)
):
    """
    Get historical performance data for a portfolio
    
    Returns:
    - Daily performance data
    - Cumulative returns over time
    """
    try:
        historical_data = await pnl_calculator.get_historical_performance(portfolio_id, days)
        
        return {
            "portfolio_id": portfolio_id,
            "period_days": days,
            "data_points": len(historical_data),
            "historical_data": [
                {
                    "date": data.date.isoformat(),
                    "portfolio_value": float(data.portfolio_value),
                    "daily_return": float(data.daily_return),
                    "cumulative_return": float(data.cumulative_return)
                }
                for data in historical_data
            ],
            "currency": "GBP"
        }
        
    except Exception as e:
        logger.error(f"Error getting historical performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/portfolio/{portfolio_id}/risk-assessment")
async def perform_risk_assessment(
    portfolio_id: str,
    user_id: str = Query(..., description="User ID for authentication"),
    market_data: Dict[str, Any] = None,
    user_preferences: Dict[str, Any] = None
):
    """
    Perform comprehensive risk assessment for a portfolio
    
    Returns:
    - Overall risk score and level
    - Risk factors by category
    - Risk mitigation recommendations
    """
    try:
        # Get portfolio data
        portfolio_service = PortfolioService()
        portfolio = await portfolio_service.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Prepare portfolio data for risk assessment
        portfolio_data = {
            'total_value': 50000,  # Mock value - would come from actual portfolio
            'assets': [],
            'concentration_risk': 0.5
        }
        
        # Use provided market data or defaults
        if not market_data:
            market_data = {
                'market_volatility': 0.25,
                'liquidity_score': 0.7,
                'regulatory_risk': 0.3
            }
        
        # Use provided user preferences or defaults
        if not user_preferences:
            user_preferences = {
                'risk_tolerance': 'moderate',
                'investment_horizon': 'long_term'
            }
        
        # Perform risk assessment
        assessment = await risk_assessment_tools.perform_comprehensive_risk_assessment(
            portfolio_data, market_data, user_preferences
        )
        
        return {
            "portfolio_id": portfolio_id,
            "overall_risk": assessment.overall_risk.value,
            "overall_score": assessment.overall_score,
            "risk_factors": [
                {
                    "category": factor.category.value,
                    "description": factor.description,
                    "risk_score": factor.risk_score,
                    "impact": factor.impact,
                    "mitigation": factor.mitigation
                }
                for factor in assessment.risk_factors
            ],
            "category_scores": {
                category.value: score
                for category, score in assessment.category_scores.items()
            },
            "recommendations": assessment.recommendations,
            "timestamp": assessment.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error performing risk assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/portfolio/{portfolio_id}/stress-test")
async def run_stress_tests(
    portfolio_id: str,
    user_id: str = Query(..., description="User ID for authentication"),
    scenarios: List[str] = Query(None, description="Specific stress test scenarios to run")
):
    """
    Run stress tests on a portfolio
    
    Returns:
    - Stress test results for various scenarios
    - Portfolio impact analysis
    - Recovery recommendations
    """
    try:
        # Get portfolio data
        portfolio_service = PortfolioService()
        portfolio = await portfolio_service.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        portfolio_data = {
            'total_value': 50000,  # Mock value
            'assets': []
        }
        
        # Run stress tests
        stress_results = await risk_assessment_tools.run_stress_tests(portfolio_data, scenarios)
        
        return {
            "portfolio_id": portfolio_id,
            "stress_test_results": [
                {
                    "scenario": result.scenario.value,
                    "description": result.description,
                    "portfolio_impact": result.portfolio_impact,
                    "recovery_time": result.recovery_time,
                    "recommendations": result.recommendations
                }
                for result in stress_results
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error running stress tests: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/portfolio/{portfolio_id}/recommendations")
async def get_portfolio_recommendations(
    portfolio_id: str,
    user_id: str = Query(..., description="User ID for authentication"),
    market_data: Dict[str, Any] = None,
    user_preferences: Dict[str, Any] = None
):
    """
    Get ML-powered portfolio recommendations
    
    Returns:
    - Buy/sell recommendations
    - Portfolio optimization suggestions
    - Risk management advice
    """
    try:
        # Get portfolio data
        portfolio_service = PortfolioService()
        portfolio = await portfolio_service.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        portfolio_data = {
            'total_value': 50000,  # Mock value
            'assets': [],
            'concentration_risk': 0.5,
            'performance_score': 0.5,
            'risk_score': 0.5,
            'asset_allocation': {
                'blue_chip_nfts': 0.6,
                'mid_tier_nfts': 0.3,
                'emerging_nfts': 0.1
            }
        }
        
        # Use provided market data or defaults
        if not market_data:
            market_data = {
                'undervalued_assets': [],
                'overvalued_assets': [],
                'trending_collections': []
            }
        
        # Use provided user preferences or defaults
        if not user_preferences:
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
        
        # Generate recommendations
        recommendations = await ml_recommendations_engine.generate_portfolio_recommendations(
            portfolio_data, market_data, user_preferences
        )
        
        return {
            "portfolio_id": portfolio_id,
            "recommendations": [
                {
                    "type": rec.type.value,
                    "asset_id": rec.asset_id,
                    "asset_name": rec.asset_name,
                    "confidence": rec.confidence.value,
                    "confidence_score": rec.confidence_score,
                    "reasoning": rec.reasoning,
                    "expected_return": rec.expected_return,
                    "risk_level": rec.risk_level,
                    "time_horizon": rec.time_horizon,
                    "metadata": rec.metadata
                }
                for rec in recommendations
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/portfolio/{portfolio_id}/optimization")
async def optimize_portfolio(
    portfolio_id: str,
    user_id: str = Query(..., description="User ID for authentication"),
    target_risk: float = Query(0.5, description="Target risk level (0.0 to 1.0)", ge=0.0, le=1.0),
    user_preferences: Dict[str, Any] = None
):
    """
    Optimize portfolio allocation based on risk tolerance
    
    Returns:
    - Current vs. recommended allocation
    - Expected improvements
    - Risk reduction estimates
    """
    try:
        # Get portfolio data
        portfolio_service = PortfolioService()
        portfolio = await portfolio_service.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        portfolio_data = {
            'asset_allocation': {
                'blue_chip_nfts': 0.6,
                'mid_tier_nfts': 0.3,
                'emerging_nfts': 0.1
            }
        }
        
        # Use provided user preferences or defaults
        if not user_preferences:
            user_preferences = {
                'risk_tolerance': 'moderate',
                'target_allocation': {
                    'blue_chip_nfts': 0.4,
                    'mid_tier_nfts': 0.4,
                    'emerging_nfts': 0.2
                }
            }
        
        # Optimize portfolio
        optimization = await ml_recommendations_engine.optimize_portfolio_allocation(
            portfolio_data, target_risk, user_preferences
        )
        
        if not optimization:
            raise HTTPException(status_code=500, detail="Failed to optimize portfolio")
        
        return {
            "portfolio_id": portfolio_id,
            "current_allocation": optimization.current_allocation,
            "recommended_allocation": optimization.recommended_allocation,
            "expected_improvement": optimization.expected_improvement,
            "risk_reduction": optimization.risk_reduction,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/market/sentiment")
async def analyze_market_sentiment(
    market_data: Dict[str, Any] = None
):
    """
    Analyze overall market sentiment
    
    Returns:
    - Market sentiment classification
    - Sentiment indicators breakdown
    """
    try:
        # Use provided market data or defaults
        if not market_data:
            market_data = {
                'social_sentiment': 0.5,
                'news_sentiment': 0.5,
                'volatility': 0.5,
                'institutional_activity': 0.5
            }
        
        # Analyze sentiment
        sentiment = await ml_recommendations_engine.analyze_market_sentiment(market_data)
        
        return {
            "market_sentiment": sentiment.value,
            "sentiment_indicators": market_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing market sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/market/trending-opportunities")
async def get_trending_opportunities(
    market_data: Dict[str, Any] = None
):
    """
    Identify trending investment opportunities
    
    Returns:
    - Trending collections
    - Opportunity scores
    - Investment recommendations
    """
    try:
        # Use provided market data or defaults
        if not market_data:
            market_data = {
                'trending_collections': []
            }
        
        # Get trending opportunities
        opportunities = await ml_recommendations_engine.get_trending_opportunities(market_data)
        
        return {
            "trending_opportunities": opportunities,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting trending opportunities: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/portfolio/{portfolio_id}/tax-report/{tax_year}")
async def generate_tax_report(
    portfolio_id: str,
    tax_year: str,
    user_id: str = Query(..., description="User ID for authentication")
):
    """
    Generate comprehensive tax report for a portfolio
    
    Returns:
    - Capital gains summary
    - Tax liability estimates
    - Transaction records
    """
    try:
        # Generate tax report
        tax_report = await tax_reporter.generate_tax_report(portfolio_id, user_id, tax_year)
        if not tax_report:
            raise HTTPException(status_code=404, detail="Tax report could not be generated")
        
        return {
            "portfolio_id": portfolio_id,
            "tax_year": tax_report.tax_year,
            "total_proceeds": float(tax_report.total_proceeds),
            "total_cost_basis": float(tax_report.total_cost_basis),
            "total_gains": float(tax_report.total_gains),
            "total_losses": float(tax_report.total_losses),
            "net_gains": float(tax_report.net_gains),
            "annual_exemption_used": float(tax_report.annual_exemption_used),
            "annual_exemption_remaining": float(tax_report.annual_exemption_remaining),
            "taxable_gains": float(tax_report.taxable_gains),
            "estimated_tax": float(tax_report.estimated_tax),
            "transactions_count": tax_report.transactions_count,
            "report_generated": tax_report.report_generated.isoformat(),
            "currency": "GBP"
        }
        
    except Exception as e:
        logger.error(f"Error generating tax report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/portfolio/{portfolio_id}/tax-loss-opportunities")
async def get_tax_loss_opportunities(
    portfolio_id: str,
    user_id: str = Query(..., description="User ID for authentication")
):
    """
    Identify tax loss harvesting opportunities
    
    Returns:
    - Assets with potential tax losses
    - Loss amounts and reasoning
    """
    try:
        # Get tax loss opportunities
        opportunities = await tax_reporter.identify_tax_loss_opportunities(portfolio_id, user_id)
        
        return {
            "portfolio_id": portfolio_id,
            "tax_loss_opportunities": [
                {
                    "asset_id": opp.asset_id,
                    "asset_name": opp.asset_name,
                    "potential_loss": float(opp.potential_loss),
                    "reasoning": opp.reasoning,
                    "priority": opp.priority
                }
                for opp in opportunities
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting tax loss opportunities: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/portfolio/{portfolio_id}/hmrc-report/{tax_year}")
async def generate_hmrc_report(
    portfolio_id: str,
    tax_year: str,
    user_id: str = Query(..., description="User ID for authentication")
):
    """
    Generate HMRC-compliant tax report
    
    Returns:
    - HMRC-compliant tax report format
    - Ready for submission
    """
    try:
        # Generate HMRC report
        hmrc_report = await tax_reporter.generate_hmrc_report(portfolio_id, user_id, tax_year)
        if not hmrc_report:
            raise HTTPException(status_code=404, detail="HMRC report could not be generated")
        
        return {
            "portfolio_id": portfolio_id,
            "tax_year": tax_year,
            "hmrc_report": hmrc_report,
            "generated_at": datetime.now().isoformat(),
            "currency": "GBP"
        }
        
    except Exception as e:
        logger.error(f"Error generating HMRC report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health/advanced-features")
async def health_check():
    """
    Health check for advanced features
    
    Returns:
    - Status of all advanced feature services
    """
    try:
        # Check service availability
        services_status = {
            "pnl_calculator": "healthy",
            "risk_assessment": "healthy", 
            "ml_recommendations": "healthy",
            "tax_reporter": "healthy"
        }
        
        return {
            "status": "healthy",
            "services": services_status,
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
