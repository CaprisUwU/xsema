"""
Portfolio Insights Engine - Advanced Analytics Service
Provides ML-powered portfolio analysis, recommendations, and risk assessment
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from enum import Enum


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InsightType(Enum):
    PERFORMANCE = "performance"
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    DIVERSIFICATION = "diversification"
    TIMING = "timing"


@dataclass
class PortfolioInsight:
    type: InsightType
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    impact_score: float  # 0.0 to 10.0
    recommendation: str
    timestamp: datetime
    metadata: Dict


@dataclass
class RiskAssessment:
    overall_risk: RiskLevel
    risk_score: float  # 0.0 to 100.0
    risk_factors: List[str]
    volatility_score: float
    concentration_risk: float
    liquidity_risk: float
    market_risk: float
    recommendations: List[str]


@dataclass
class PerformanceMetrics:
    total_return: Decimal
    annualized_return: Decimal
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    risk_adjusted_return: float


@dataclass
class DiversificationAnalysis:
    chain_distribution: Dict[str, float]
    collection_diversity: float
    asset_class_mix: Dict[str, float]
    correlation_matrix: Dict[str, Dict[str, float]]
    concentration_risk: float


class PortfolioInsightsEngine:
    """Advanced portfolio analytics and insights engine"""
    
    def __init__(self):
        self.risk_thresholds = {
            'low': 25,
            'medium': 50,
            'high': 75,
            'critical': 90
        }
        
        self.performance_weights = {
            'return': 0.3,
            'risk': 0.25,
            'diversification': 0.2,
            'liquidity': 0.15,
            'timing': 0.1
        }
    
    async def generate_portfolio_insights(
        self, 
        portfolio_data: Dict,
        market_data: Dict,
        user_preferences: Dict
    ) -> List[PortfolioInsight]:
        """Generate comprehensive portfolio insights"""
        
        insights = []
        
        # Performance insights
        performance_insights = await self._analyze_performance(portfolio_data, market_data)
        insights.extend(performance_insights)
        
        # Risk insights
        risk_insights = await self._analyze_risk_factors(portfolio_data, market_data)
        insights.extend(risk_insights)
        
        # Opportunity insights
        opportunity_insights = await self._identify_opportunities(portfolio_data, market_data, user_preferences)
        insights.extend(opportunity_insights)
        
        # Diversification insights
        diversification_insights = await self._analyze_diversification(portfolio_data)
        insights.extend(diversification_insights)
        
        # Sort by impact score
        insights.sort(key=lambda x: x.impact_score, reverse=True)
        
        return insights
    
    async def assess_portfolio_risk(self, portfolio_data: Dict) -> RiskAssessment:
        """Comprehensive risk assessment"""
        
        # Calculate various risk metrics
        volatility_score = await self._calculate_volatility(portfolio_data)
        concentration_risk = await self._calculate_concentration_risk(portfolio_data)
        liquidity_risk = await self._calculate_liquidity_risk(portfolio_data)
        market_risk = await self._calculate_market_risk(portfolio_data)
        
        # Overall risk score (weighted average)
        overall_score = (
            volatility_score * 0.3 +
            concentration_risk * 0.25 +
            liquidity_risk * 0.25 +
            market_risk * 0.2
        )
        
        # Determine risk level
        risk_level = await self._determine_risk_level(overall_score)
        
        # Generate recommendations
        recommendations = await self._generate_risk_recommendations(
            volatility_score, concentration_risk, liquidity_risk, market_risk
        )
        
        return RiskAssessment(
            overall_risk=risk_level,
            risk_score=overall_score,
            risk_factors=await self._identify_risk_factors(portfolio_data),
            volatility_score=volatility_score,
            concentration_risk=concentration_risk,
            liquidity_risk=liquidity_risk,
            market_risk=market_risk,
            recommendations=recommendations
        )
    
    async def calculate_performance_metrics(self, portfolio_data: Dict) -> PerformanceMetrics:
        """Calculate advanced performance metrics"""
        
        # Mock calculation - in production, this would use real historical data
        total_return = Decimal('0.15')  # 15% return
        annualized_return = Decimal('0.08')  # 8% annualized
        sharpe_ratio = 1.2
        max_drawdown = 0.12  # 12% max drawdown
        win_rate = 0.65  # 65% win rate
        profit_factor = 1.8
        risk_adjusted_return = 0.06  # 6% risk-adjusted return
        
        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            risk_adjusted_return=risk_adjusted_return
        )
    
    async def analyze_diversification(self, portfolio_data: Dict) -> DiversificationAnalysis:
        """Analyze portfolio diversification"""
        
        # Calculate chain distribution
        chain_distribution = await self._calculate_chain_distribution(portfolio_data)
        
        # Calculate collection diversity
        collection_diversity = await self._calculate_collection_diversity(portfolio_data)
        
        # Asset class mix
        asset_class_mix = await self._calculate_asset_class_mix(portfolio_data)
        
        # Correlation matrix (simplified)
        correlation_matrix = await self._calculate_correlation_matrix(portfolio_data)
        
        # Concentration risk
        concentration_risk = await self._calculate_concentration_risk(portfolio_data)
        
        return DiversificationAnalysis(
            chain_distribution=chain_distribution,
            collection_diversity=collection_diversity,
            asset_class_mix=asset_class_mix,
            correlation_matrix=correlation_matrix,
            concentration_risk=concentration_risk
        )
    
    async def generate_recommendations(
        self, 
        portfolio_data: Dict,
        market_data: Dict,
        user_preferences: Dict
    ) -> List[Dict]:
        """Generate personalized portfolio recommendations"""
        
        recommendations = []
        
        # Rebalancing recommendations
        rebalancing = await self._generate_rebalancing_recommendations(portfolio_data)
        if rebalancing:
            recommendations.append(rebalancing)
        
        # New investment opportunities
        opportunities = await self._identify_investment_opportunities(portfolio_data, market_data)
        recommendations.extend(opportunities)
        
        # Risk mitigation
        risk_mitigation = await self._generate_risk_mitigation_recommendations(portfolio_data)
        recommendations.extend(risk_mitigation)
        
        # Tax optimization
        tax_optimization = await self._generate_tax_optimization_recommendations(portfolio_data)
        if tax_optimization:
            recommendations.append(tax_optimization)
        
        return recommendations
    
    # Private helper methods
    async def _analyze_performance(self, portfolio_data: Dict, market_data: Dict) -> List[PortfolioInsight]:
        """Analyze portfolio performance"""
        insights = []
        
        # Check if portfolio is outperforming market
        portfolio_return = portfolio_data.get('total_return', 0)
        market_return = market_data.get('market_return', 0)
        
        if portfolio_return > market_return * 1.2:
            insights.append(PortfolioInsight(
                type=InsightType.PERFORMANCE,
                title="Portfolio Outperforming Market",
                description=f"Your portfolio is outperforming the market by {((portfolio_return/market_return)-1)*100:.1f}%",
                confidence=0.85,
                impact_score=8.5,
                recommendation="Consider taking some profits and rebalancing",
                timestamp=datetime.now(),
                metadata={'portfolio_return': portfolio_return, 'market_return': market_return}
            ))
        
        return insights
    
    async def _analyze_risk_factors(self, portfolio_data: Dict, market_data: Dict) -> List[PortfolioInsight]:
        """Analyze risk factors"""
        insights = []
        
        # Check for high concentration
        if portfolio_data.get('concentration_risk', 0) > 0.7:
            insights.append(PortfolioInsight(
                type=InsightType.RISK,
                title="High Portfolio Concentration",
                description="Your portfolio is heavily concentrated in a few assets",
                confidence=0.9,
                impact_score=9.0,
                recommendation="Diversify across more collections and chains",
                timestamp=datetime.now(),
                metadata={'concentration_risk': portfolio_data.get('concentration_risk', 0)}
            ))
        
        return insights
    
    async def _identify_opportunities(self, portfolio_data: Dict, market_data: Dict, user_preferences: Dict) -> List[PortfolioInsight]:
        """Identify investment opportunities"""
        insights = []
        
        # Check for undervalued collections
        undervalued = market_data.get('undervalued_collections', [])
        if undervalued:
            insights.append(PortfolioInsight(
                type=InsightType.OPPORTUNITY,
                title="Undervalued Collection Opportunity",
                description=f"Found {len(undervalued)} potentially undervalued collections",
                confidence=0.75,
                impact_score=7.5,
                recommendation="Research these collections for potential investment",
                timestamp=datetime.now(),
                metadata={'collections': undervalued}
            ))
        
        return insights
    
    async def _analyze_diversification(self, portfolio_data: Dict) -> List[PortfolioInsight]:
        """Analyze portfolio diversification"""
        insights = []
        
        # Check chain diversity
        chains = portfolio_data.get('chains', [])
        if len(chains) < 3:
            insights.append(PortfolioInsight(
                type=InsightType.DIVERSIFICATION,
                title="Limited Chain Diversity",
                description="Your portfolio is concentrated on few blockchain networks",
                confidence=0.8,
                impact_score=7.0,
                recommendation="Consider diversifying across more chains",
                timestamp=datetime.now(),
                metadata={'chains': chains}
            ))
        
        return insights
    
    async def _calculate_volatility(self, portfolio_data: Dict) -> float:
        """Calculate portfolio volatility"""
        # Mock calculation - in production, use real price data
        return 0.18  # 18% volatility
    
    async def _calculate_concentration_risk(self, portfolio_data: Dict) -> float:
        """Calculate concentration risk"""
        # Mock calculation - in production, use real portfolio weights
        return 0.35  # 35% concentration risk
    
    async def _calculate_liquidity_risk(self, portfolio_data: Dict) -> float:
        """Calculate liquidity risk"""
        # Mock calculation - in production, use real trading volume data
        return 0.22  # 22% liquidity risk
    
    async def _calculate_market_risk(self, portfolio_data: Dict) -> float:
        """Calculate market risk"""
        # Mock calculation - in production, use real market data
        return 0.28  # 28% market risk
    
    async def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score"""
        if risk_score <= self.risk_thresholds['low']:
            return RiskLevel.LOW
        elif risk_score <= self.risk_thresholds['medium']:
            return RiskLevel.MEDIUM
        elif risk_score <= self.risk_thresholds['high']:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    async def _generate_risk_recommendations(
        self, 
        volatility_score: float,
        concentration_risk: float,
        liquidity_risk: float,
        market_risk: float
    ) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if volatility_score > 0.3:
            recommendations.append("Consider adding stable assets to reduce volatility")
        
        if concentration_risk > 0.5:
            recommendations.append("Diversify across more collections and asset types")
        
        if liquidity_risk > 0.3:
            recommendations.append("Ensure adequate liquidity for emergency exits")
        
        if market_risk > 0.4:
            recommendations.append("Consider hedging strategies or defensive positioning")
        
        return recommendations
    
    async def _identify_risk_factors(self, portfolio_data: Dict) -> List[str]:
        """Identify specific risk factors"""
        risk_factors = []
        
        if portfolio_data.get('concentration_risk', 0) > 0.5:
            risk_factors.append("High asset concentration")
        
        if portfolio_data.get('chain_diversity', 0) < 3:
            risk_factors.append("Limited blockchain diversity")
        
        if portfolio_data.get('liquidity_score', 0) < 0.5:
            risk_factors.append("Low liquidity exposure")
        
        return risk_factors
    
    async def _calculate_chain_distribution(self, portfolio_data: Dict) -> Dict[str, float]:
        """Calculate distribution across blockchain networks"""
        # Mock data - in production, calculate from real portfolio
        return {
            'Ethereum': 0.45,
            'Polygon': 0.25,
            'BSC': 0.15,
            'Arbitrum': 0.10,
            'Other': 0.05
        }
    
    async def _calculate_collection_diversity(self, portfolio_data: Dict) -> float:
        """Calculate collection diversity score"""
        # Mock calculation - in production, use real collection data
        return 0.72  # 72% diversity score
    
    async def _calculate_asset_class_mix(self, portfolio_data: Dict) -> Dict[str, float]:
        """Calculate asset class distribution"""
        # Mock data - in production, categorize real assets
        return {
            'Art': 0.30,
            'Gaming': 0.25,
            'Collectibles': 0.20,
            'Music': 0.15,
            'Other': 0.10
        }
    
    async def _calculate_correlation_matrix(self, portfolio_data: Dict) -> Dict[str, Dict[str, float]]:
        """Calculate asset correlation matrix"""
        # Mock correlation matrix - in production, use real price data
        return {
            'BAYC': {'BAYC': 1.0, 'MAYC': 0.8, 'Doodles': 0.6},
            'MAYC': {'BAYC': 0.8, 'MAYC': 1.0, 'Doodles': 0.7},
            'Doodles': {'BAYC': 0.6, 'MAYC': 0.7, 'Doodles': 1.0}
        }
    
    async def _generate_rebalancing_recommendations(self, portfolio_data: Dict) -> Optional[Dict]:
        """Generate portfolio rebalancing recommendations"""
        # Check if rebalancing is needed
        if portfolio_data.get('rebalancing_needed', False):
            return {
                'type': 'rebalancing',
                'title': 'Portfolio Rebalancing Recommended',
                'description': 'Your portfolio has drifted from target allocations',
                'priority': 'medium',
                'actions': ['Sell overweight positions', 'Buy underweight positions']
            }
        return None
    
    async def _identify_investment_opportunities(self, portfolio_data: Dict, market_data: Dict) -> List[Dict]:
        """Identify new investment opportunities"""
        opportunities = []
        
        # Check for trending collections
        trending = market_data.get('trending_collections', [])
        for collection in trending[:3]:  # Top 3 trending
            opportunities.append({
                'type': 'opportunity',
                'title': f'Invest in {collection["name"]}',
                'description': f'{collection["name"]} is trending with {collection["growth"]}% growth',
                'priority': 'high',
                'actions': ['Research fundamentals', 'Consider small position']
            })
        
        return opportunities
    
    async def _generate_risk_mitigation_recommendations(self, portfolio_data: Dict) -> List[Dict]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        # Check for high-risk positions
        if portfolio_data.get('high_risk_exposure', 0) > 0.3:
            recommendations.append({
                'type': 'risk_mitigation',
                'title': 'Reduce High-Risk Exposure',
                'description': 'Consider reducing exposure to high-risk assets',
                'priority': 'high',
                'actions': ['Review riskiest positions', 'Consider partial exits']
            })
        
        return recommendations
    
    async def _generate_tax_optimization_recommendations(self, portfolio_data: Dict) -> Optional[Dict]:
        """Generate tax optimization recommendations"""
        # Check for tax loss harvesting opportunities
        if portfolio_data.get('tax_loss_opportunities', 0) > 0:
            return {
                'type': 'tax_optimization',
                'title': 'Tax Loss Harvesting Opportunity',
                'description': 'Consider selling losing positions for tax benefits',
                'priority': 'medium',
                'actions': ['Identify loss positions', 'Plan tax-efficient sales']
            }
        return None


# Example usage and testing
async def main():
    """Test the Portfolio Insights Engine"""
    engine = PortfolioInsightsEngine()
    
    # Mock portfolio data
    portfolio_data = {
        'total_return': 0.15,
        'concentration_risk': 0.35,
        'chain_diversity': 4,
        'liquidity_score': 0.65,
        'rebalancing_needed': True,
        'high_risk_exposure': 0.25,
        'tax_loss_opportunities': 2
    }
    
    # Mock market data
    market_data = {
        'market_return': 0.10,
        'undervalued_collections': [
            {'name': 'Cool Cats', 'growth': 15},
            {'name': 'Azuki', 'growth': 12}
        ],
        'trending_collections': [
            {'name': 'Bored Ape Yacht Club', 'growth': 25},
            {'name': 'Mutant Ape Yacht Club', 'growth': 20}
        ]
    }
    
    # Mock user preferences
    user_preferences = {
        'risk_tolerance': 'moderate',
        'investment_horizon': 'long_term',
        'preferred_chains': ['Ethereum', 'Polygon']
    }
    
    print("🔍 Generating Portfolio Insights...")
    insights = await engine.generate_portfolio_insights(portfolio_data, market_data, user_preferences)
    
    print(f"\n📊 Generated {len(insights)} insights:")
    for insight in insights:
        print(f"  • {insight.title}: {insight.description}")
    
    print("\n⚠️  Risk Assessment:")
    risk_assessment = await engine.assess_portfolio_risk(portfolio_data)
    print(f"  Overall Risk: {risk_assessment.overall_risk.value.upper()}")
    print(f"  Risk Score: {risk_assessment.risk_score:.1f}/100")
    
    print("\n📈 Performance Metrics:")
    performance = await engine.calculate_performance_metrics(portfolio_data)
    print(f"  Total Return: {performance.total_return:.1%}")
    print(f"  Sharpe Ratio: {performance.sharpe_ratio:.2f}")
    
    print("\n🎯 Recommendations:")
    recommendations = await engine.generate_recommendations(portfolio_data, market_data, user_preferences)
    for rec in recommendations:
        print(f"  • {rec['title']}: {rec['description']}")


if __name__ == "__main__":
    asyncio.run(main())
