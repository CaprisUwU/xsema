"""
Advanced Performance Analytics Service
Provides comprehensive portfolio performance metrics, benchmarking, and analysis
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
from decimal import Decimal
from enum import Enum


class MetricType(Enum):
    RETURN = "return"
    RISK = "risk"
    RATIO = "ratio"
    VOLATILITY = "volatility"
    DRAWDOWN = "drawdown"
    CORRELATION = "correlation"


class BenchmarkType(Enum):
    MARKET = "market"
    SECTOR = "sector"
    PEER = "peer"
    CUSTOM = "custom"


@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    change: Optional[float] = None
    change_percentage: Optional[float] = None
    benchmark: Optional[float] = None
    benchmark_difference: Optional[float] = None
    timestamp: datetime = None


@dataclass
class RiskMetrics:
    volatility: float
    var_95: float  # Value at Risk (95% confidence)
    var_99: float  # Value at Risk (99% confidence)
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    information_ratio: float
    treynor_ratio: float


@dataclass
class ReturnMetrics:
    total_return: Decimal
    annualized_return: Decimal
    monthly_return: Decimal
    weekly_return: Decimal
    daily_return: Decimal
    cumulative_return: Decimal
    geometric_mean: float
    arithmetic_mean: float


@dataclass
class BenchmarkComparison:
    benchmark_name: str
    benchmark_type: BenchmarkType
    portfolio_return: float
    benchmark_return: float
    excess_return: float
    tracking_error: float
    information_ratio: float
    correlation: float
    beta: float
    alpha: float


@dataclass
class PerformanceAttribution:
    asset_allocation: float
    stock_selection: float
    interaction: float
    total_excess_return: float
    benchmark_return: float
    portfolio_return: float


class AdvancedPerformanceAnalytics:
    """Advanced portfolio performance analytics engine"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate
        self.benchmark_data = {
            'market': {
                'ethereum': {'return': 0.12, 'volatility': 0.25},
                'polygon': {'return': 0.18, 'volatility': 0.30},
                'bsc': {'return': 0.15, 'volatility': 0.28},
                'overall': {'return': 0.15, 'volatility': 0.28}
            },
            'sector': {
                'art': {'return': 0.14, 'volatility': 0.26},
                'gaming': {'return': 0.20, 'volatility': 0.32},
                'collectibles': {'return': 0.16, 'volatility': 0.29},
                'music': {'return': 0.18, 'volatility': 0.31}
            }
        }
    
    async def calculate_comprehensive_metrics(
        self,
        portfolio_data: Dict,
        historical_data: Dict,
        benchmark_data: Dict
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        metrics = {}
        
        # Return metrics
        metrics['returns'] = await self._calculate_return_metrics(portfolio_data, historical_data)
        
        # Risk metrics
        metrics['risk'] = await self._calculate_risk_metrics(portfolio_data, historical_data)
        
        # Benchmark comparisons
        metrics['benchmarks'] = await self._calculate_benchmark_comparisons(
            portfolio_data, benchmark_data
        )
        
        # Performance attribution
        metrics['attribution'] = await self._calculate_performance_attribution(
            portfolio_data, benchmark_data
        )
        
        # Advanced ratios
        metrics['ratios'] = await self._calculate_advanced_ratios(metrics['returns'], metrics['risk'])
        
        return metrics
    
    async def generate_performance_report(
        self,
        portfolio_data: Dict,
        time_period: str = "1Y"
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        # Mock historical data - in production, fetch from database
        historical_data = await self._generate_mock_historical_data(portfolio_data, time_period)
        
        # Calculate metrics
        metrics = await self.calculate_comprehensive_metrics(
            portfolio_data, historical_data, self.benchmark_data
        )
        
        # Generate insights
        insights = await self._generate_performance_insights(metrics)
        
        # Generate recommendations
        recommendations = await self._generate_performance_recommendations(metrics)
        
        return {
            'summary': {
                'total_return': metrics['returns'].total_return,
                'annualized_return': metrics['returns'].annualized_return,
                'sharpe_ratio': metrics['risk'].sharpe_ratio,
                'max_drawdown': metrics['risk'].max_drawdown,
                'volatility': metrics['risk'].volatility
            },
            'detailed_metrics': metrics,
            'insights': insights,
            'recommendations': recommendations,
            'generated_at': datetime.now(),
            'time_period': time_period
        }
    
    async def calculate_rolling_metrics(
        self,
        portfolio_data: Dict,
        window: str = "30D"
    ) -> List[Dict]:
        """Calculate rolling performance metrics"""
        
        # Mock rolling calculation - in production, use real time series data
        rolling_metrics = []
        
        # Generate mock rolling data for the last 12 months
        for i in range(12):
            date = datetime.now() - timedelta(days=30 * i)
            
            # Mock metrics for each period
            rolling_metrics.append({
                'date': date,
                'return': 0.08 + (i * 0.002),  # Gradually increasing returns
                'volatility': 0.25 + (i * 0.01),  # Gradually increasing volatility
                'sharpe_ratio': 0.8 + (i * 0.05),  # Gradually improving Sharpe ratio
                'max_drawdown': 0.15 - (i * 0.01),  # Gradually decreasing drawdown
                'value': 50000 + (i * 1000)  # Gradually increasing portfolio value
            })
        
        return rolling_metrics
    
    async def perform_risk_analysis(
        self,
        portfolio_data: Dict,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """Perform comprehensive risk analysis"""
        
        # Mock risk analysis - in production, use real statistical models
        risk_analysis = {
            'var_analysis': {
                'var_95': 0.08,  # 8% Value at Risk (95% confidence)
                'var_99': 0.12,  # 12% Value at Risk (99% confidence)
                'expected_shortfall': 0.10,  # Expected loss beyond VaR
                'var_confidence': confidence_level
            },
            'stress_testing': {
                'market_crash_scenario': -0.25,  # 25% loss in market crash
                'liquidity_crisis': -0.15,  # 15% loss in liquidity crisis
                'regulatory_change': -0.10,  # 10% loss in regulatory change
                'black_swan_event': -0.40   # 40% loss in extreme event
            },
            'scenario_analysis': {
                'bull_market': 0.30,  # 30% gain in bull market
                'bear_market': -0.20,  # 20% loss in bear market
                'sideways_market': 0.05,  # 5% gain in sideways market
                'volatile_market': 0.15   # 15% gain in volatile market
            }
        }
        
        return risk_analysis
    
    async def calculate_correlation_analysis(
        self,
        portfolio_data: Dict,
        market_data: Dict
    ) -> Dict[str, Any]:
        """Calculate correlation analysis between portfolio and market factors"""
        
        # Mock correlation analysis - in production, use real statistical calculations
        correlation_analysis = {
            'market_correlation': 0.75,  # 75% correlation with market
            'sector_correlations': {
                'art': 0.68,
                'gaming': 0.82,
                'collectibles': 0.71,
                'music': 0.76
            },
            'chain_correlations': {
                'ethereum': 0.85,
                'polygon': 0.72,
                'bsc': 0.78,
                'arbitrum': 0.69
            },
            'asset_correlations': {
                'bayc': {'mayc': 0.88, 'doodles': 0.65, 'azuki': 0.58},
                'mayc': {'bayc': 0.88, 'doodles': 0.70, 'azuki': 0.62},
                'doodles': {'bayc': 0.65, 'mayc': 0.70, 'azuki': 0.55},
                'azuki': {'bayc': 0.58, 'mayc': 0.62, 'doodles': 0.55}
            }
        }
        
        return correlation_analysis
    
    # Private helper methods
    async def _calculate_return_metrics(
        self,
        portfolio_data: Dict,
        historical_data: Dict
    ) -> ReturnMetrics:
        """Calculate comprehensive return metrics"""
        
        # Mock calculations - in production, use real historical data
        total_return = Decimal('0.15')  # 15% total return
        annualized_return = Decimal('0.08')  # 8% annualized
        monthly_return = Decimal('0.006')  # 0.6% monthly
        weekly_return = Decimal('0.0015')  # 0.15% weekly
        daily_return = Decimal('0.0003')  # 0.03% daily
        cumulative_return = Decimal('1.15')  # 115% cumulative
        
        # Calculate geometric and arithmetic means
        geometric_mean = 1.08  # 8% geometric mean
        arithmetic_mean = 1.085  # 8.5% arithmetic mean
        
        return ReturnMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            monthly_return=monthly_return,
            weekly_return=weekly_return,
            daily_return=daily_return,
            cumulative_return=cumulative_return,
            geometric_mean=geometric_mean,
            arithmetic_mean=arithmetic_mean
        )
    
    async def _calculate_risk_metrics(
        self,
        portfolio_data: Dict,
        historical_data: Dict
    ) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        
        # Mock calculations - in production, use real historical data
        volatility = 0.25  # 25% volatility
        var_95 = 0.08  # 8% VaR (95% confidence)
        var_99 = 0.12  # 12% VaR (99% confidence)
        max_drawdown = 0.15  # 15% maximum drawdown
        
        # Calculate ratios
        sharpe_ratio = await self._calculate_sharpe_ratio(0.08, 0.25, 0.02)
        sortino_ratio = await self._calculate_sortino_ratio(0.08, 0.20, 0.02)
        calmar_ratio = await self._calculate_calmar_ratio(0.08, 0.15)
        information_ratio = await self._calculate_information_ratio(0.08, 0.15, 0.05)
        treynor_ratio = await self._calculate_treynor_ratio(0.08, 0.75, 0.02)
        
        return RiskMetrics(
            volatility=volatility,
            var_95=var_95,
            var_99=var_99,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            information_ratio=information_ratio,
            treynor_ratio=treynor_ratio
        )
    
    async def _calculate_benchmark_comparisons(
        self,
        portfolio_data: Dict,
        benchmark_data: Dict
    ) -> List[BenchmarkComparison]:
        """Calculate benchmark comparisons"""
        
        comparisons = []
        
        # Market benchmark comparison
        market_benchmark = BenchmarkComparison(
            benchmark_name="NFT Market Index",
            benchmark_type=BenchmarkType.MARKET,
            portfolio_return=0.15,
            benchmark_return=0.12,
            excess_return=0.03,
            tracking_error=0.08,
            information_ratio=0.375,
            correlation=0.85,
            beta=1.1,
            alpha=0.018
        )
        comparisons.append(market_benchmark)
        
        # Sector benchmark comparison
        sector_benchmark = BenchmarkComparison(
            benchmark_name="Art & Collectibles Sector",
            benchmark_type=BenchmarkType.SECTOR,
            portfolio_return=0.15,
            benchmark_return=0.14,
            excess_return=0.01,
            tracking_error=0.06,
            information_ratio=0.167,
            correlation=0.78,
            beta=0.95,
            alpha=0.007
        )
        comparisons.append(sector_benchmark)
        
        return comparisons
    
    async def _calculate_performance_attribution(
        self,
        portfolio_data: Dict,
        benchmark_data: Dict
    ) -> PerformanceAttribution:
        """Calculate performance attribution analysis"""
        
        # Mock attribution calculation - in production, use real attribution models
        asset_allocation = 0.02  # 2% from asset allocation
        stock_selection = 0.01   # 1% from stock selection
        interaction = 0.005      # 0.5% from interaction
        total_excess_return = 0.035  # 3.5% total excess return
        benchmark_return = 0.12  # 12% benchmark return
        portfolio_return = 0.155  # 15.5% portfolio return
        
        return PerformanceAttribution(
            asset_allocation=asset_allocation,
            stock_selection=stock_selection,
            interaction=interaction,
            total_excess_return=total_excess_return,
            benchmark_return=benchmark_return,
            portfolio_return=portfolio_return
        )
    
    async def _calculate_advanced_ratios(
        self,
        returns: ReturnMetrics,
        risk: RiskMetrics
    ) -> Dict[str, float]:
        """Calculate advanced performance ratios"""
        
        ratios = {
            'sharpe_ratio': risk.sharpe_ratio,
            'sortino_ratio': risk.sortino_ratio,
            'calmar_ratio': risk.calmar_ratio,
            'information_ratio': risk.information_ratio,
            'treynor_ratio': risk.treynor_ratio,
            'jensen_alpha': 0.018,  # 1.8% Jensen's alpha
            'modigliani_ratio': 0.12,  # 12% Modigliani ratio
            'gain_loss_ratio': 1.8,  # 1.8 gain/loss ratio
            'profit_factor': 2.1,  # 2.1 profit factor
            'win_rate': 0.65  # 65% win rate
        }
        
        return ratios
    
    async def _generate_mock_historical_data(
        self,
        portfolio_data: Dict,
        time_period: str
    ) -> Dict:
        """Generate mock historical data for testing"""
        
        # Mock historical data - in production, fetch from database
        return {
            'daily_returns': [0.001, -0.002, 0.003, -0.001, 0.002],
            'monthly_returns': [0.02, -0.01, 0.03, 0.01, 0.02],
            'portfolio_values': [50000, 51000, 50800, 51200, 51500],
            'benchmark_values': [100, 102, 101, 103, 105]
        }
    
    async def _generate_performance_insights(self, metrics: Dict) -> List[str]:
        """Generate performance insights"""
        
        insights = []
        
        # Analyze returns
        if metrics['returns'].annualized_return > Decimal('0.10'):
            insights.append("Portfolio is outperforming typical market returns")
        
        # Analyze risk
        if metrics['risk'].sharpe_ratio > 1.0:
            insights.append("Portfolio has excellent risk-adjusted returns")
        
        if metrics['risk'].max_drawdown > 0.20:
            insights.append("Portfolio has experienced significant drawdowns")
        
        # Analyze benchmarks
        for benchmark in metrics['benchmarks']:
            if benchmark.excess_return > 0.02:
                insights.append(f"Portfolio outperforming {benchmark.benchmark_name}")
        
        return insights
    
    async def _generate_performance_recommendations(self, metrics: Dict) -> List[str]:
        """Generate performance recommendations"""
        
        recommendations = []
        
        # Risk management recommendations
        if metrics['risk'].volatility > 0.30:
            recommendations.append("Consider reducing portfolio volatility through diversification")
        
        if metrics['risk'].max_drawdown > 0.25:
            recommendations.append("Implement stop-loss strategies to limit drawdowns")
        
        # Return optimization recommendations
        if metrics['returns'].annualized_return < Decimal('0.05'):
            recommendations.append("Review asset allocation to improve returns")
        
        # Benchmark recommendations
        for benchmark in metrics['benchmarks']:
            if benchmark.information_ratio < 0.5:
                recommendations.append(f"Improve tracking of {benchmark.benchmark_name}")
        
        return recommendations
    
    # Ratio calculation methods
    async def _calculate_sharpe_ratio(
        self,
        return_rate: float,
        volatility: float,
        risk_free_rate: float
    ) -> float:
        """Calculate Sharpe ratio"""
        if volatility == 0:
            return 0
        return (return_rate - risk_free_rate) / volatility
    
    async def _calculate_sortino_ratio(
        self,
        return_rate: float,
        downside_deviation: float,
        risk_free_rate: float
    ) -> float:
        """Calculate Sortino ratio"""
        if downside_deviation == 0:
            return 0
        return (return_rate - risk_free_rate) / downside_deviation
    
    async def _calculate_calmar_ratio(
        self,
        return_rate: float,
        max_drawdown: float
    ) -> float:
        """Calculate Calmar ratio"""
        if max_drawdown == 0:
            return 0
        return return_rate / max_drawdown
    
    async def _calculate_information_ratio(
        self,
        return_rate: float,
        benchmark_return: float,
        tracking_error: float
    ) -> float:
        """Calculate Information ratio"""
        if tracking_error == 0:
            return 0
        return (return_rate - benchmark_return) / tracking_error
    
    async def _calculate_treynor_ratio(
        self,
        return_rate: float,
        beta: float,
        risk_free_rate: float
    ) -> float:
        """Calculate Treynor ratio"""
        if beta == 0:
            return 0
        return (return_rate - risk_free_rate) / beta


# Example usage and testing
async def main():
    """Test the Advanced Performance Analytics"""
    analytics = AdvancedPerformanceAnalytics()
    
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
    
    print("📊 Calculating Advanced Performance Metrics...")
    
    # Generate performance report
    report = await analytics.generate_performance_report(portfolio_data, "1Y")
    
    print(f"\n📈 Performance Summary:")
    print(f"  Total Return: {report['summary']['total_return']:.1%}")
    print(f"  Annualized Return: {report['summary']['annualized_return']:.1%}")
    print(f"  Sharpe Ratio: {report['summary']['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown: {report['summary']['max_drawdown']:.1%}")
    print(f"  Volatility: {report['summary']['volatility']:.1%}")
    
    print(f"\n⚠️  Risk Analysis:")
    risk_analysis = await analytics.perform_risk_analysis(portfolio_data)
    print(f"  VaR (95%): {risk_analysis['var_analysis']['var_95']:.1%}")
    print(f"  VaR (99%): {risk_analysis['var_analysis']['var_99']:.1%}")
    print(f"  Market Crash Scenario: {risk_analysis['stress_testing']['market_crash_scenario']:.1%}")
    
    print(f"\n🔗 Correlation Analysis:")
    correlation_analysis = await analytics.calculate_correlation_analysis(portfolio_data, {})
    print(f"  Market Correlation: {correlation_analysis['market_correlation']:.0%}")
    print(f"  Art Sector Correlation: {correlation_analysis['sector_correlations']['art']:.0%}")
    
    print(f"\n📊 Rolling Metrics (Last 12 months):")
    rolling_metrics = await analytics.calculate_rolling_metrics(portfolio_data, "30D")
    for metric in rolling_metrics[:3]:  # Show first 3 months
        print(f"  {metric['date'].strftime('%b %Y')}: Return {metric['return']:.1%}, Sharpe {metric['sharpe_ratio']:.2f}")
    
    print(f"\n💡 Performance Insights:")
    for insight in report['insights']:
        print(f"  • {insight}")
    
    print(f"\n🎯 Recommendations:")
    for recommendation in report['recommendations']:
        print(f"  • {recommendation}")


if __name__ == "__main__":
    asyncio.run(main())
