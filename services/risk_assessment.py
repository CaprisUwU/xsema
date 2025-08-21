"""
Risk Assessment Tools Service
Provides comprehensive risk analysis, stress testing, and risk management recommendations
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
from decimal import Decimal
from enum import Enum


class RiskCategory(Enum):
    MARKET = "market"
    LIQUIDITY = "liquidity"
    CONCENTRATION = "concentration"
    OPERATIONAL = "operational"
    REGULATORY = "regulatory"
    TECHNICAL = "technical"
    COUNTERPARTY = "counterparty"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StressTestScenario(Enum):
    MARKET_CRASH = "market_crash"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    REGULATORY_CHANGE = "regulatory_change"
    TECHNICAL_FAILURE = "technical_failure"
    BLACK_SWAN = "black_swan"


@dataclass
class RiskFactor:
    category: RiskCategory
    name: str
    description: str
    risk_level: RiskLevel
    risk_score: float  # 0.0 to 100.0
    impact: str
    probability: float  # 0.0 to 1.0
    mitigation_strategies: List[str]
    timestamp: datetime


@dataclass
class RiskAssessment:
    overall_risk: RiskLevel
    overall_score: float  # 0.0 to 100.0
    risk_factors: List[RiskFactor]
    category_scores: Dict[RiskCategory, float]
    recommendations: List[str]
    timestamp: datetime


@dataclass
class StressTestResult:
    scenario: StressTestScenario
    portfolio_impact: float  # Percentage change
    risk_score_change: float
    affected_assets: List[str]
    recovery_time: str
    recommendations: List[str]
    timestamp: datetime


@dataclass
class RiskMetrics:
    var_95: float  # Value at Risk (95% confidence)
    var_99: float  # Value at Risk (99% confidence)
    expected_shortfall: float
    conditional_var: float
    max_drawdown: float
    volatility: float
    beta: float
    correlation: float


class RiskAssessmentTools:
    """Comprehensive risk assessment and management tools"""
    
    def __init__(self):
        self.risk_thresholds = {
            'low': 25,
            'medium': 50,
            'high': 75,
            'critical': 90
        }
        
        self.category_weights = {
            RiskCategory.MARKET: 0.35,
            RiskCategory.LIQUIDITY: 0.20,
            RiskCategory.CONCENTRATION: 0.25,
            RiskCategory.OPERATIONAL: 0.10,
            RiskCategory.REGULATORY: 0.05,
            RiskCategory.TECHNICAL: 0.03,
            RiskCategory.COUNTERPARTY: 0.02
        }
        
        self.stress_test_scenarios = {
            StressTestScenario.MARKET_CRASH: {
                'description': 'Severe market downturn (2008-style crash)',
                'market_impact': -0.40,
                'liquidity_impact': -0.60,
                'recovery_time': '2-3 years'
            },
            StressTestScenario.LIQUIDITY_CRISIS: {
                'description': 'Sudden loss of market liquidity',
                'market_impact': -0.25,
                'liquidity_impact': -0.80,
                'recovery_time': '6-12 months'
            },
            StressTestScenario.REGULATORY_CHANGE: {
                'description': 'Major regulatory changes affecting NFTs',
                'market_impact': -0.20,
                'liquidity_impact': -0.30,
                'recovery_time': '3-6 months'
            },
            StressTestScenario.TECHNICAL_FAILURE: {
                'description': 'Blockchain or platform technical issues',
                'market_impact': -0.15,
                'liquidity_impact': -0.40,
                'recovery_time': '1-3 months'
            },
            StressTestScenario.BLACK_SWAN: {
                'description': 'Unprecedented catastrophic event',
                'market_impact': -0.60,
                'liquidity_impact': -0.90,
                'recovery_time': '3-5 years'
            }
        }
    
    async def perform_comprehensive_risk_assessment(
        self,
        portfolio_data: Dict,
        market_data: Dict,
        user_preferences: Dict
    ) -> RiskAssessment:
        """Perform comprehensive risk assessment"""
        
        risk_factors = []
        category_scores = {}
        
        # Assess each risk category
        for category in RiskCategory:
            category_risks = await self._assess_risk_category(
                category, portfolio_data, market_data, user_preferences
            )
            risk_factors.extend(category_risks)
            
            # Calculate category score
            if category_risks:
                category_score = sum(risk.risk_score for risk in category_risks) / len(category_risks)
                category_scores[category] = category_score
        
        # Calculate overall risk score
        overall_score = await self._calculate_overall_risk_score(category_scores)
        overall_risk = await self._determine_risk_level(overall_score)
        
        # Generate recommendations
        recommendations = await self._generate_risk_recommendations(risk_factors, category_scores)
        
        return RiskAssessment(
            overall_risk=overall_risk,
            overall_score=overall_score,
            risk_factors=risk_factors,
            category_scores=category_scores,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    async def run_stress_tests(
        self,
        portfolio_data: Dict,
        scenarios: Optional[List[StressTestScenario]] = None
    ) -> List[StressTestResult]:
        """Run comprehensive stress tests"""
        
        if scenarios is None:
            scenarios = list(StressTestScenario)
        
        results = []
        
        for scenario in scenarios:
            result = await self._run_single_stress_test(scenario, portfolio_data)
            if result:
                results.append(result)
        
        return results
    
    async def calculate_risk_metrics(
        self,
        portfolio_data: Dict,
        historical_data: Dict
    ) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        
        # Mock calculations - in production, use real statistical models
        var_95 = await self._calculate_var(portfolio_data, 0.95)
        var_99 = await self._calculate_var(portfolio_data, 0.99)
        expected_shortfall = await self._calculate_expected_shortfall(portfolio_data, 0.95)
        conditional_var = await self._calculate_conditional_var(portfolio_data, 0.95)
        max_drawdown = await self._calculate_max_drawdown(portfolio_data, historical_data)
        volatility = await self._calculate_volatility(portfolio_data, historical_data)
        beta = await self._calculate_beta(portfolio_data, historical_data)
        correlation = await self._calculate_correlation(portfolio_data, historical_data)
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            expected_shortfall=expected_shortfall,
            conditional_var=conditional_var,
            max_drawdown=max_drawdown,
            volatility=volatility,
            beta=beta,
            correlation=correlation
        )
    
    async def generate_risk_report(
        self,
        portfolio_data: Dict,
        market_data: Dict,
        user_preferences: Dict
    ) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        
        # Perform risk assessment
        risk_assessment = await self.perform_comprehensive_risk_assessment(
            portfolio_data, market_data, user_preferences
        )
        
        # Run stress tests
        stress_test_results = await self.run_stress_tests(portfolio_data)
        
        # Calculate risk metrics
        risk_metrics = await self.calculate_risk_metrics(portfolio_data, {})
        
        # Generate risk heatmap
        risk_heatmap = await self._generate_risk_heatmap(risk_assessment)
        
        return {
            'summary': {
                'overall_risk': risk_assessment.overall_risk.value,
                'overall_score': risk_assessment.overall_score,
                'risk_level': risk_assessment.overall_risk.value,
                'critical_risks': len([r for r in risk_assessment.risk_factors if r.risk_level == RiskLevel.CRITICAL])
            },
            'risk_assessment': risk_assessment,
            'stress_tests': stress_test_results,
            'risk_metrics': risk_metrics,
            'risk_heatmap': risk_heatmap,
            'generated_at': datetime.now()
        }
    
    async def monitor_risk_indicators(
        self,
        portfolio_data: Dict,
        market_data: Dict
    ) -> List[Dict]:
        """Monitor real-time risk indicators"""
        
        indicators = []
        
        # Market risk indicators
        market_volatility = market_data.get('volatility', 0)
        if market_volatility > 0.4:
            indicators.append({
                'type': 'market_risk',
                'level': 'high',
                'message': f'Market volatility is high: {market_volatility:.1%}',
                'recommendation': 'Consider reducing exposure to volatile assets'
            })
        
        # Liquidity risk indicators
        portfolio_liquidity = await self._calculate_portfolio_liquidity(portfolio_data)
        if portfolio_liquidity < 0.3:
            indicators.append({
                'type': 'liquidity_risk',
                'level': 'high',
                'message': f'Portfolio liquidity is low: {portfolio_liquidity:.1%}',
                'recommendation': 'Increase allocation to liquid assets'
            })
        
        # Concentration risk indicators
        concentration_risk = await self._calculate_concentration_risk(portfolio_data)
        if concentration_risk > 0.7:
            indicators.append({
                'type': 'concentration_risk',
                'level': 'critical',
                'message': f'Portfolio concentration is very high: {concentration_risk:.1%}',
                'recommendation': 'Immediately diversify portfolio holdings'
            })
        
        return indicators
    
    # Private helper methods
    async def _assess_risk_category(
        self,
        category: RiskCategory,
        portfolio_data: Dict,
        market_data: Dict,
        user_preferences: Dict
    ) -> List[RiskFactor]:
        """Assess risks for a specific category"""
        
        risk_factors = []
        
        if category == RiskCategory.MARKET:
            risk_factors = await self._assess_market_risks(portfolio_data, market_data)
        elif category == RiskCategory.LIQUIDITY:
            risk_factors = await self._assess_liquidity_risks(portfolio_data, market_data)
        elif category == RiskCategory.CONCENTRATION:
            risk_factors = await self._assess_concentration_risks(portfolio_data)
        elif category == RiskCategory.OPERATIONAL:
            risk_factors = await self._assess_operational_risks(portfolio_data)
        elif category == RiskCategory.REGULATORY:
            risk_factors = await self._assess_regulatory_risks(portfolio_data, market_data)
        elif category == RiskCategory.TECHNICAL:
            risk_factors = await self._assess_technical_risks(portfolio_data)
        elif category == RiskCategory.COUNTERPARTY:
            risk_factors = await self._assess_counterparty_risks(portfolio_data)
        
        return risk_factors
    
    async def _assess_market_risks(
        self,
        portfolio_data: Dict,
        market_data: Dict
    ) -> List[RiskFactor]:
        """Assess market-related risks"""
        
        risks = []
        
        # Market volatility risk
        market_volatility = market_data.get('volatility', 0)
        if market_volatility > 0.3:
            risks.append(RiskFactor(
                category=RiskCategory.MARKET,
                name='High Market Volatility',
                description=f'Market volatility is {market_volatility:.1%}, indicating unstable conditions',
                risk_level=RiskLevel.HIGH if market_volatility > 0.5 else RiskLevel.MEDIUM,
                risk_score=min(market_volatility * 100, 90),
                impact='Portfolio value fluctuations and potential losses',
                probability=0.7,
                mitigation_strategies=[
                    'Diversify across asset classes',
                    'Consider hedging strategies',
                    'Reduce exposure to volatile assets'
                ],
                timestamp=datetime.now()
            ))
        
        # Market correlation risk
        market_correlation = market_data.get('correlation', 0)
        if market_correlation > 0.8:
            risks.append(RiskFactor(
                category=RiskCategory.MARKET,
                name='High Market Correlation',
                description=f'Portfolio correlation with market is {market_correlation:.1%}',
                risk_level=RiskLevel.MEDIUM,
                risk_score=market_correlation * 80,
                impact='Limited diversification benefits during market downturns',
                probability=0.6,
                mitigation_strategies=[
                    'Add uncorrelated assets',
                    'Consider alternative investments',
                    'Review asset allocation strategy'
                ],
                timestamp=datetime.now()
            ))
        
        return risks
    
    async def _assess_liquidity_risks(
        self,
        portfolio_data: Dict,
        market_data: Dict
    ) -> List[RiskFactor]:
        """Assess liquidity-related risks"""
        
        risks = []
        
        # Portfolio liquidity risk
        portfolio_liquidity = await self._calculate_portfolio_liquidity(portfolio_data)
        if portfolio_liquidity < 0.5:
            risks.append(RiskFactor(
                category=RiskCategory.LIQUIDITY,
                name='Low Portfolio Liquidity',
                description=f'Portfolio liquidity score is {portfolio_liquidity:.1%}',
                risk_level=RiskLevel.HIGH if portfolio_liquidity < 0.3 else RiskLevel.MEDIUM,
                risk_score=(1 - portfolio_liquidity) * 80,
                impact='Difficulty selling assets quickly without significant losses',
                probability=0.5,
                mitigation_strategies=[
                    'Increase allocation to liquid assets',
                    'Maintain emergency cash reserves',
                    'Diversify across trading venues'
                ],
                timestamp=datetime.now()
            ))
        
        return risks
    
    async def _assess_concentration_risks(self, portfolio_data: Dict) -> List[RiskFactor]:
        """Assess concentration-related risks"""
        
        risks = []
        
        # Asset concentration risk
        concentration_risk = await self._calculate_concentration_risk(portfolio_data)
        if concentration_risk > 0.6:
            risks.append(RiskFactor(
                category=RiskCategory.CONCENTRATION,
                name='High Asset Concentration',
                description=f'Portfolio concentration risk is {concentration_risk:.1%}',
                risk_level=RiskLevel.CRITICAL if concentration_risk > 0.8 else RiskLevel.HIGH,
                risk_score=concentration_risk * 100,
                impact='Excessive exposure to single assets or sectors',
                probability=0.8,
                mitigation_strategies=[
                    'Diversify across more assets',
                    'Reduce largest positions',
                    'Add different asset classes'
                ],
                timestamp=datetime.now()
            ))
        
        # Chain concentration risk
        chain_diversity = len(set(asset.get('chain') for asset in portfolio_data.get('assets', [])))
        if chain_diversity < 3:
            risks.append(RiskFactor(
                category=RiskCategory.CONCENTRATION,
                name='Limited Chain Diversity',
                description=f'Portfolio spans only {chain_diversity} blockchain networks',
                risk_level=RiskLevel.MEDIUM,
                risk_score=(3 - chain_diversity) * 25,
                impact='Exposure to single blockchain risks',
                probability=0.6,
                mitigation_strategies=[
                    'Add assets on different chains',
                    'Consider cross-chain bridges',
                    'Evaluate chain-specific risks'
                ],
                timestamp=datetime.now()
            ))
        
        return risks
    
    async def _assess_operational_risks(self, portfolio_data: Dict) -> List[RiskFactor]:
        """Assess operational risks"""
        
        risks = []
        
        # Mock operational risk assessment
        risks.append(RiskFactor(
            category=RiskCategory.OPERATIONAL,
            name='Smart Contract Risk',
            description='Potential vulnerabilities in NFT smart contracts',
            risk_level=RiskLevel.MEDIUM,
            risk_score=45,
            impact='Loss of assets due to contract bugs or exploits',
            probability=0.3,
            mitigation_strategies=[
                'Audit smart contracts before use',
                'Use established, well-tested contracts',
                'Monitor for security updates'
            ],
            timestamp=datetime.now()
        ))
        
        return risks
    
    async def _assess_regulatory_risks(
        self,
        portfolio_data: Dict,
        market_data: Dict
    ) -> List[RiskFactor]:
        """Assess regulatory risks"""
        
        risks = []
        
        # Mock regulatory risk assessment
        risks.append(RiskFactor(
            category=RiskCategory.REGULATORY,
            name='Regulatory Uncertainty',
            description='Evolving NFT regulations may impact market',
            risk_level=RiskLevel.MEDIUM,
            risk_score=35,
            impact='Potential restrictions or compliance requirements',
            probability=0.4,
            mitigation_strategies=[
                'Stay informed about regulations',
                'Diversify across jurisdictions',
                'Consult legal professionals'
            ],
            timestamp=datetime.now()
        ))
        
        return risks
    
    async def _assess_technical_risks(self, portfolio_data: Dict) -> List[RiskFactor]:
        """Assess technical risks"""
        
        risks = []
        
        # Mock technical risk assessment
        risks.append(RiskFactor(
            category=RiskCategory.TECHNICAL,
            name='Blockchain Network Risk',
            description='Potential blockchain network issues or congestion',
            risk_level=RiskLevel.LOW,
            risk_score=25,
            impact='Transaction delays or failures',
            probability=0.2,
            mitigation_strategies=[
                'Use multiple blockchain networks',
                'Monitor network status',
                'Have backup transaction methods'
            ],
            timestamp=datetime.now()
        ))
        
        return risks
    
    async def _assess_counterparty_risks(self, portfolio_data: Dict) -> List[RiskFactor]:
        """Assess counterparty risks"""
        
        risks = []
        
        # Mock counterparty risk assessment
        risks.append(RiskFactor(
            category=RiskCategory.COUNTERPARTY,
            name='Exchange Risk',
            description='Risk of exchange or marketplace failure',
            risk_level=RiskLevel.LOW,
            risk_score=20,
            impact='Loss of access to trading platforms',
            probability=0.1,
            mitigation_strategies=[
                'Use multiple exchanges',
                'Keep assets in personal wallets',
                'Monitor exchange health'
            ],
            timestamp=datetime.now()
        ))
        
        return risks
    
    async def _calculate_overall_risk_score(self, category_scores: Dict[RiskCategory, float]) -> float:
        """Calculate overall risk score using weighted average"""
        
        if not category_scores:
            return 0
        
        weighted_score = 0
        total_weight = 0
        
        for category, score in category_scores.items():
            weight = self.category_weights.get(category, 0.1)
            weighted_score += score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0
    
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
        risk_factors: List[RiskFactor],
        category_scores: Dict[RiskCategory, float]
    ) -> List[str]:
        """Generate risk management recommendations"""
        
        recommendations = []
        
        # High-level recommendations based on overall risk
        high_risk_categories = [
            category for category, score in category_scores.items()
            if score > 70
        ]
        
        if high_risk_categories:
            recommendations.append(
                f"Focus on reducing risks in: {', '.join(cat.value for cat in high_risk_categories)}"
            )
        
        # Specific recommendations from risk factors
        critical_risks = [r for r in risk_factors if r.risk_level == RiskLevel.CRITICAL]
        if critical_risks:
            recommendations.append(
                f"Address {len(critical_risks)} critical risks immediately"
            )
        
        # Add top mitigation strategies
        for risk in sorted(risk_factors, key=lambda x: x.risk_score, reverse=True)[:3]:
            if risk.mitigation_strategies:
                recommendations.append(
                    f"Mitigate {risk.name}: {risk.mitigation_strategies[0]}"
                )
        
        return recommendations
    
    async def _run_single_stress_test(
        self,
        scenario: StressTestScenario,
        portfolio_data: Dict
    ) -> Optional[StressTestResult]:
        """Run a single stress test scenario"""
        
        if scenario not in self.stress_test_scenarios:
            return None
        
        scenario_data = self.stress_test_scenarios[scenario]
        
        # Calculate portfolio impact
        portfolio_impact = scenario_data['market_impact']
        
        # Calculate risk score change
        risk_score_change = abs(portfolio_impact) * 50  # Convert to risk score change
        
        # Identify affected assets
        affected_assets = [
            asset['name'] for asset in portfolio_data.get('assets', [])
            if asset.get('chain') in ['Ethereum', 'Polygon']  # Most affected chains
        ]
        
        # Generate recommendations
        recommendations = [
            'Review asset allocation strategy',
            'Consider defensive positioning',
            'Maintain adequate liquidity'
        ]
        
        return StressTestResult(
            scenario=scenario,
            portfolio_impact=portfolio_impact,
            risk_score_change=risk_score_change,
            affected_assets=affected_assets,
            recovery_time=scenario_data['recovery_time'],
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    async def _generate_risk_heatmap(self, risk_assessment: RiskAssessment) -> Dict[str, Any]:
        """Generate risk heatmap data"""
        
        heatmap_data = {}
        
        for category in RiskCategory:
            score = risk_assessment.category_scores.get(category, 0)
            risk_level = await self._determine_risk_level(score)
            heatmap_data[category.value] = {
                'score': score,
                'level': risk_level.value,
                'color': self._get_risk_color(score)
            }
        
        return heatmap_data
    
    async def _get_risk_color(self, risk_score: float) -> str:
        """Get color for risk score visualization"""
        
        if risk_score <= 25:
            return '#10B981'  # Green
        elif risk_score <= 50:
            return '#F59E0B'  # Yellow
        elif risk_score <= 75:
            return '#EF4444'  # Red
        else:
            return '#7C2D12'  # Dark red
    
    # Risk calculation methods
    async def _calculate_var(self, portfolio_data: Dict, confidence: float) -> float:
        """Calculate Value at Risk"""
        # Mock calculation - in production, use real statistical models
        base_var = 0.08  # 8% base VaR
        return base_var * (1 + (1 - confidence) * 2)  # Higher confidence = higher VaR
    
    async def _calculate_expected_shortfall(self, portfolio_data: Dict, confidence: float) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        var = await self._calculate_var(portfolio_data, confidence)
        return var * 1.25  # ES is typically 25% higher than VaR
    
    async def _calculate_conditional_var(self, portfolio_data: Dict, confidence: float) -> float:
        """Calculate Conditional Value at Risk"""
        return await self._calculate_expected_shortfall(portfolio_data, confidence)
    
    async def _calculate_max_drawdown(self, portfolio_data: Dict, historical_data: Dict) -> float:
        """Calculate maximum drawdown"""
        # Mock calculation - in production, use real historical data
        return 0.15  # 15% maximum drawdown
    
    async def _calculate_volatility(self, portfolio_data: Dict, historical_data: Dict) -> float:
        """Calculate portfolio volatility"""
        # Mock calculation - in production, use real historical data
        return 0.25  # 25% volatility
    
    async def _calculate_beta(self, portfolio_data: Dict, historical_data: Dict) -> float:
        """Calculate portfolio beta"""
        # Mock calculation - in production, use real historical data
        return 1.1  # 1.1 beta
    
    async def _calculate_correlation(self, portfolio_data: Dict, historical_data: Dict) -> float:
        """Calculate portfolio correlation with market"""
        # Mock calculation - in production, use real historical data
        return 0.75  # 75% correlation
    
    async def _calculate_portfolio_liquidity(self, portfolio_data: Dict) -> float:
        """Calculate portfolio liquidity score"""
        # Mock calculation - in production, use real liquidity data
        return 0.65  # 65% liquidity score
    
    async def _calculate_concentration_risk(self, portfolio_data: Dict) -> float:
        """Calculate portfolio concentration risk"""
        # Mock calculation - in production, use real portfolio weights
        return 0.35  # 35% concentration risk


# Example usage and testing
async def main():
    """Test the Risk Assessment Tools"""
    risk_tools = RiskAssessmentTools()
    
    # Mock portfolio data
    portfolio_data = {
        'total_value': 50000,
        'assets': [
            {'name': 'BAYC #123', 'value': 15000, 'chain': 'Ethereum'},
            {'name': 'Doodles #456', 'value': 12000, 'chain': 'Ethereum'},
            {'name': 'Azuki #789', 'value': 10000, 'chain': 'Ethereum'},
            {'name': 'Polygon NFT', 'value': 8000, 'chain': 'Polygon'},
            {'name': 'BSC NFT', 'value': 5000, 'chain': 'BSC'}
        ]
    }
    
    # Mock market data
    market_data = {
        'volatility': 0.35,
        'correlation': 0.82,
        'market_trend': 'declining'
    }
    
    # Mock user preferences
    user_preferences = {
        'risk_tolerance': 'moderate',
        'investment_horizon': 'long_term'
    }
    
    print("⚠️  Performing Comprehensive Risk Assessment...")
    
    # Generate risk report
    risk_report = await risk_tools.generate_risk_report(
        portfolio_data, market_data, user_preferences
    )
    
    print(f"\n📊 Risk Summary:")
    print(f"  Overall Risk: {risk_report['summary']['overall_risk'].upper()}")
    print(f"  Risk Score: {risk_report['summary']['overall_score']:.1f}/100")
    print(f"  Critical Risks: {risk_report['summary']['critical_risks']}")
    
    print(f"\n🔍 Risk Categories:")
    for category, data in risk_report['risk_heatmap'].items():
        print(f"  {category.title()}: {data['level'].upper()} ({data['score']:.1f})")
    
    print(f"\n⚠️  Top Risk Factors:")
    for risk in risk_report['risk_assessment'].risk_factors[:3]:
        print(f"  • {risk.name}: {risk.risk_level.value.upper()} ({risk.risk_score:.1f})")
        print(f"    {risk.description}")
    
    print(f"\n🧪 Stress Test Results:")
    for test in risk_report['stress_tests'][:3]:
        print(f"  • {test.scenario.value.replace('_', ' ').title()}: {test.portfolio_impact:.1%} impact")
        print(f"    Recovery Time: {test.recovery_time}")
    
    print(f"\n📈 Risk Metrics:")
    metrics = risk_report['risk_metrics']
    print(f"  VaR (95%): {metrics.var_95:.1%}")
    print(f"  VaR (99%): {metrics.var_99:.1%}")
    print(f"  Max Drawdown: {metrics.max_drawdown:.1%}")
    print(f"  Volatility: {metrics.volatility:.1%}")
    
    print(f"\n💡 Risk Recommendations:")
    for rec in risk_report['risk_assessment'].recommendations[:3]:
        print(f"  • {rec}")
    
    print(f"\n🚨 Risk Indicators:")
    indicators = await risk_tools.monitor_risk_indicators(portfolio_data, market_data)
    for indicator in indicators:
        print(f"  • {indicator['type'].replace('_', ' ').title()}: {indicator['message']}")


if __name__ == "__main__":
    asyncio.run(main())
