"""
Analytics Service

Provides portfolio analytics, performance metrics, and insights.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd

from core.cache import cache
from portfolio.utils.logger import logger
from portfolio.models.portfolio import Portfolio, Asset, PortfolioInsights, Recommendation
from portfolio.services.price_service import price_service

class AnalyticsService:
    """Service for portfolio analytics and insights"""
    
    def __init__(self):
        self.cache_ttl = 3600  # 1 hour cache
    
    async def get_portfolio_insights(
        self, 
        portfolio: Portfolio,
        time_range: str = '30d'
    ) -> PortfolioInsights:
        """
        Generate comprehensive insights for a portfolio
        
        Args:
            portfolio: The portfolio to analyze
            time_range: Time range for analysis (e.g., '7d', '30d', '1y')
            
        Returns:
            PortfolioInsights object with analysis
        """
        try:
            # Get historical performance
            performance = await self.get_portfolio_performance(
                portfolio,
                time_range=time_range
            )
            
            # Get risk assessment
            risk = await self.assess_portfolio_risk(portfolio)
            
            # Generate recommendations
            recommendations = await self.generate_recommendations(portfolio)
            
            # Get market conditions
            market_conditions = await self.get_market_conditions()
            
            return PortfolioInsights(
                portfolio_id=portfolio.id,
                performance=performance,
                risk_assessment=risk,
                opportunities=recommendations['opportunities'],
                warnings=recommendations['warnings'],
                market_conditions=market_conditions,
                generated_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Error generating portfolio insights: {str(e)}")
            raise
    
    async def get_portfolio_performance(
        self,
        portfolio: Portfolio,
        time_range: str = '30d'
    ) -> Dict:
        """
        Calculate portfolio performance metrics
        
        Args:
            portfolio: The portfolio to analyze
            time_range: Time range for analysis
            
        Returns:
            Dictionary with performance metrics
        """
        try:
            # Get historical prices for all assets
            asset_prices = {}
            for wallet in portfolio.wallets:
                for asset in wallet.assets:
                    if asset.type == 'nft':
                        # Skip NFTs for now as they're harder to price historically
                        continue
                        
                    history = await price_service.get_price_history(
                        asset_id=asset.asset_id,
                        days=self._time_range_to_days(time_range)
                    )
                    
                    if history and 'prices' in history:
                        asset_prices[asset.asset_id] = {
                            'symbol': asset.symbol,
                            'prices': history['prices'],
                            'balance': asset.balance
                        }
            
            # Calculate portfolio value over time
            timestamps = set()
            for asset_data in asset_prices.values():
                for point in asset_data['prices']:
                    timestamps.add(point['timestamp'])
            
            if not timestamps:
                return {}
                
            # Sort timestamps
            sorted_timestamps = sorted(timestamps)
            
            # Calculate portfolio value at each timestamp
            portfolio_values = []
            for ts in sorted_timestamps:
                total_value = 0.0
                
                for asset_id, asset_data in asset_prices.items():
                    # Find the closest price point before or at this timestamp
                    price_point = None
                    for point in asset_data['prices']:
                        if point['timestamp'] <= ts:
                            price_point = point
                        else:
                            break
                    
                    if price_point:
                        total_value += float(asset_data['balance']) * price_point['price']
                
                portfolio_values.append({
                    'timestamp': ts,
                    'value': total_value
                })
            
            # Calculate performance metrics
            if len(portfolio_values) < 2:
                return {
                    'time_series': portfolio_values,
                    'metrics': {}
                }
            
            start_value = portfolio_values[0]['value']
            end_value = portfolio_values[-1]['value']
            
            # Calculate returns
            total_return = ((end_value - start_value) / start_value) * 100 if start_value > 0 else 0
            
            # Calculate volatility (standard deviation of daily returns)
            values = [p['value'] for p in portfolio_values]
            daily_returns = np.diff(values) / values[:-1]
            volatility = np.std(daily_returns) * np.sqrt(365)  # Annualized
            
            # Calculate Sharpe ratio (assuming risk-free rate of 0 for simplicity)
            sharpe_ratio = (np.mean(daily_returns) / np.std(daily_returns)) * np.sqrt(365) if np.std(daily_returns) > 0 else 0
            
            return {
                'time_series': portfolio_values,
                'metrics': {
                    'total_return_percent': round(total_return, 2),
                    'volatility': round(volatility, 4),
                    'sharpe_ratio': round(sharpe_ratio, 2),
                    'start_value': round(start_value, 2),
                    'end_value': round(end_value, 2),
                    'time_range': time_range
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio performance: {str(e)}")
            return {}
    
    async def assess_portfolio_risk(
        self, 
        portfolio: Portfolio
    ) -> Dict:
        """
        Assess portfolio risk
        
        Args:
            portfolio: The portfolio to analyze
            
        Returns:
            Dictionary with risk metrics
        """
        try:
            # Calculate concentration risk
            total_value = sum(w.balance for w in portfolio.wallets for a in w.assets if hasattr(a, 'value_usd'))
            
            if total_value == 0:
                return {
                    'concentration_risk': 0,
                    'liquidity_risk': 0,
                    'market_risk': 0,
                    'overall_risk': 0,
                    'metrics': {}
                }
            
            # Calculate asset concentration
            asset_values = {}
            for wallet in portfolio.wallets:
                for asset in wallet.assets:
                    if hasattr(asset, 'value_usd'):
                        asset_values[asset.asset_id] = asset_values.get(asset.asset_id, 0) + asset.value_usd
            
            # Sort assets by value
            sorted_assets = sorted(asset_values.items(), key=lambda x: x[1], reverse=True)
            
            # Calculate Herfindahl-Hirschman Index (HHI) for concentration
            hhi = sum((v / total_value) ** 2 for _, v in sorted_assets)
            
            # Calculate concentration risk (0-100)
            concentration_risk = min(int(hhi * 100), 100)
            
            # Simple risk metrics (placeholder for more sophisticated analysis)
            return {
                'concentration_risk': concentration_risk,
                'liquidity_risk': 30,  # Placeholder
                'market_risk': 50,     # Placeholder
                'overall_risk': min(int((concentration_risk + 30 + 50) / 3), 100),
                'metrics': {
                    'hhi_index': round(hhi, 4),
                    'top_assets': [
                        {'asset_id': k, 'allocation_percent': round((v / total_value) * 100, 2)}
                        for k, v in sorted_assets[:5]  # Top 5 assets
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error assessing portfolio risk: {str(e)}")
            return {}
    
    async def generate_recommendations(
        self, 
        portfolio: Portfolio
    ) -> Dict[str, List[Recommendation]]:
        """
        Generate portfolio recommendations
        
        Args:
            portfolio: The portfolio to analyze
            
        Returns:
            Dictionary with 'opportunities' and 'warnings'
        """
        opportunities = []
        warnings = []
        
        try:
            # Example recommendations (in a real app, these would be ML-driven)
            
            # Check for over-concentration
            risk = await self.assess_portfolio_risk(portfolio)
            if risk.get('concentration_risk', 0) > 70:
                warnings.append(Recommendation(
                    type='risk',
                    title="High Concentration Risk",
                    description=f"Your portfolio has high concentration risk (HHI: {risk.get('metrics', {}).get('hhi_index', 0):.2f}). Consider diversifying across more assets.",
                    priority=1,
                    action={
                        'type': 'rebalance',
                        'suggested_allocation': 'more_diversified'
                    }
                ))
            
            # Check for low-liquidity assets
            # This is a placeholder - in a real app, you'd check actual liquidity metrics
            
            # Example opportunity
            opportunities.append(Recommendation(
                type='opportunity',
                title="Potential Rebalancing Opportunity",
                description="Consider rebalancing your portfolio to maintain target allocations.",
                priority=2,
                action={
                    'type': 'rebalance',
                    'suggested_allocation': 'target'
                }
            ))
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
        
        return {
            'opportunities': opportunities,
            'warnings': warnings
        }
    
    async def get_market_conditions(self) -> Dict:
        """
        Get current market conditions
        
        Returns:
            Dictionary with market conditions
        """
        try:
            # In a real app, this would fetch from various data sources
            # This is a simplified version
            return {
                'market_sentiment': 'neutral',  # bullish, bearish, neutral
                'market_volatility': 'medium',  # low, medium, high
                'trending_assets': [
                    {'asset_id': 'bitcoin', 'reason': 'Institutional adoption'},
                    {'asset_id': 'ethereum', 'reason': 'Upcoming network upgrade'}
                ],
                'market_metrics': {
                    'fear_and_greed_index': 50,  # 0-100
                    'btc_dominance': 42.5,       # Percentage
                    'total_market_cap': 2000000000000,  # In USD
                    'market_cap_change_24h': 1.2  # Percentage
                }
            }
        except Exception as e:
            logger.error(f"Error getting market conditions: {str(e)}")
            return {}
    
    def _time_range_to_days(self, time_range: str) -> int:
        """Convert time range string to days"""
        if not time_range:
            return 30
            
        time_range = time_range.lower()
        if time_range.endswith('d'):
            return int(time_range[:-1])
        elif time_range.endswith('w'):
            return int(time_range[:-1]) * 7
        elif time_range.endswith('m'):
            return int(time_range[:-1]) * 30
        elif time_range.endswith('y'):
            return int(time_range[:-1]) * 365
        else:
            return int(time_range) if time_range.isdigit() else 30

# Singleton instance
analytics_service = AnalyticsService()
