"""
ML-Powered Recommendations Service
Provides intelligent portfolio suggestions, market predictions, and automated insights
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
import random
from enum import Enum
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    REBALANCE = "rebalance"
    DIVERSIFY = "diversify"
    HEDGE = "hedge"

class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class MarketSentiment(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    VOLATILE = "volatile"

@dataclass
class MLRecommendation:
    type: RecommendationType
    asset_id: str
    asset_name: str
    confidence: ConfidenceLevel
    confidence_score: float  # 0.0 to 1.0
    reasoning: str
    expected_return: float
    risk_level: str
    time_horizon: str
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class MarketPrediction:
    collection_id: str
    collection_name: str
    predicted_movement: str  # "up", "down", "stable"
    confidence_score: float
    time_horizon: str
    key_factors: List[str]
    timestamp: datetime

@dataclass
class PortfolioOptimization:
    current_allocation: Dict[str, float]
    recommended_allocation: Dict[str, float]
    expected_improvement: float
    risk_reduction: float

class MLRecommendationsEngine:
    """ML-powered recommendations and predictions engine"""
    
    def __init__(self):
        self.model_version = "1.0.0"
        self.last_training = datetime.now() - timedelta(days=7)
        self.confidence_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'very_high': 0.9
        }
        
        # Enhanced ML model parameters with more sophisticated weights
        self.model_weights = {
            'price_momentum': 0.25,
            'volume_analysis': 0.20,
            'social_sentiment': 0.15,
            'technical_indicators': 0.20,
            'market_correlation': 0.20
        }
        
        # Market sentiment indicators
        self.sentiment_indicators = {
            'social_media_buzz': 0.3,
            'news_sentiment': 0.25,
            'market_volatility': 0.25,
            'institutional_activity': 0.20
        }
        
        # Risk tolerance mapping
        self.risk_tolerance_mapping = {
            'conservative': 0.2,
            'moderate': 0.5,
            'aggressive': 0.8
        }
        
        logger.info("ML Recommendations Engine initialized successfully")
    
    async def generate_portfolio_recommendations(
        self,
        portfolio_data: Dict,
        market_data: Dict,
        user_preferences: Dict
    ) -> List[MLRecommendation]:
        """Generate ML-powered portfolio recommendations"""
        
        try:
            recommendations = []
            
            # Analyze current portfolio
            portfolio_analysis = await self._analyze_portfolio(portfolio_data)
            
            # Generate buy recommendations
            buy_recommendations = await self._generate_buy_recommendations(
                portfolio_analysis, market_data, user_preferences
            )
            recommendations.extend(buy_recommendations)
            
            # Generate sell recommendations
            sell_recommendations = await self._generate_sell_recommendations(
                portfolio_analysis, market_data
            )
            recommendations.extend(sell_recommendations)
            
            # Generate rebalancing recommendations
            rebalance_recommendations = await self._generate_rebalancing_recommendations(
                portfolio_analysis, user_preferences
            )
            recommendations.extend(rebalance_recommendations)
            
            # Sort by confidence score
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            
            logger.info(f"Generated {len(recommendations)} portfolio recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating portfolio recommendations: {str(e)}")
            return []
    
    async def predict_market_movements(
        self,
        collections: List[str],
        time_horizon: str = "30d"
    ) -> List[MarketPrediction]:
        """Predict market movements for specific collections"""
        
        try:
            predictions = []
            
            for collection_id in collections:
                # Get collection data
                collection_data = await self._get_collection_data(collection_id)
                if not collection_data:
                    continue
                
                # Analyze market indicators
                market_indicators = await self._analyze_market_indicators(collection_data)
                
                # Generate prediction
                prediction = await self._generate_market_prediction(
                    collection_id, collection_data, market_indicators, time_horizon
                )
                
                if prediction:
                    predictions.append(prediction)
            
            logger.info(f"Generated {len(predictions)} market predictions")
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting market movements: {str(e)}")
            return []
    
    async def optimize_portfolio_allocation(
        self,
        portfolio_data: Dict,
        target_risk: float,
        user_preferences: Dict
    ) -> Optional[PortfolioOptimization]:
        """Optimize portfolio allocation based on risk tolerance"""
        
        try:
            current_allocation = portfolio_data.get('asset_allocation', {})
            
            # Calculate optimal allocation using modern portfolio theory
            optimal_allocation = await self._calculate_optimal_allocation(
                portfolio_data, target_risk, user_preferences
            )
            
            # Calculate expected improvements
            expected_improvement = await self._estimate_return_improvement(
                current_allocation, optimal_allocation
            )
            
            risk_reduction = await self._estimate_risk_reduction(
                current_allocation, optimal_allocation
            )
            
            return PortfolioOptimization(
                current_allocation=current_allocation,
                recommended_allocation=optimal_allocation,
                expected_improvement=expected_improvement,
                risk_reduction=risk_reduction
            )
            
        except Exception as e:
            logger.error(f"Error optimizing portfolio allocation: {str(e)}")
            return None
    
    async def analyze_market_sentiment(self, market_data: Dict) -> MarketSentiment:
        """Analyze overall market sentiment"""
        
        try:
            # Calculate sentiment score from various indicators
            sentiment_score = 0.0
            
            # Social media sentiment
            social_sentiment = market_data.get('social_sentiment', 0.5)
            sentiment_score += social_sentiment * self.sentiment_indicators['social_media_buzz']
            
            # News sentiment
            news_sentiment = market_data.get('news_sentiment', 0.5)
            sentiment_score += news_sentiment * self.sentiment_indicators['news_sentiment']
            
            # Market volatility (inverse relationship)
            volatility = market_data.get('volatility', 0.5)
            sentiment_score += (1 - volatility) * self.sentiment_indicators['market_volatility']
            
            # Institutional activity
            institutional_activity = market_data.get('institutional_activity', 0.5)
            sentiment_score += institutional_activity * self.sentiment_indicators['institutional_activity']
            
            # Determine sentiment category
            if sentiment_score > 0.7:
                return MarketSentiment.BULLISH
            elif sentiment_score < 0.3:
                return MarketSentiment.BEARISH
            elif volatility > 0.7:
                return MarketSentiment.VOLATILE
            else:
                return MarketSentiment.NEUTRAL
                
        except Exception as e:
            logger.error(f"Error analyzing market sentiment: {str(e)}")
            return MarketSentiment.NEUTRAL
    
    async def get_trending_opportunities(self, market_data: Dict) -> List[Dict]:
        """Identify trending investment opportunities"""
        
        try:
            opportunities = []
            
            # Get trending collections
            trending_collections = market_data.get('trending_collections', [])
            
            for collection in trending_collections[:5]:  # Top 5 trending
                opportunity = await self._analyze_trending_opportunity(collection)
                if opportunity:
                    opportunities.append(opportunity)
            
            # Sort by opportunity score
            opportunities.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error getting trending opportunities: {str(e)}")
            return []
    
    # Private helper methods
    async def _analyze_portfolio(self, portfolio_data: Dict) -> Dict:
        """Analyze current portfolio for ML insights"""
        
        try:
            analysis = {
                'total_value': portfolio_data.get('total_value', 0),
                'asset_count': len(portfolio_data.get('assets', [])),
                'chain_diversity': len(set(asset.get('chain') for asset in portfolio_data.get('assets', []))),
                'concentration_risk': portfolio_data.get('concentration_risk', 0),
                'performance_score': portfolio_data.get('performance_score', 0),
                'risk_score': portfolio_data.get('risk_score', 0),
                'asset_allocation': portfolio_data.get('asset_allocation', {}),
                'recent_performance': portfolio_data.get('recent_performance', [])
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {str(e)}")
            return {}
    
    async def _generate_buy_recommendations(
        self,
        portfolio_analysis: Dict,
        market_data: Dict,
        user_preferences: Dict
    ) -> List[MLRecommendation]:
        """Generate buy recommendations using ML"""
        
        recommendations = []
        
        try:
            # Check for diversification opportunities
            if portfolio_analysis.get('chain_diversity', 0) < 3:
                # Recommend diversifying across chains
                recommendations.append(MLRecommendation(
                    type=RecommendationType.DIVERSIFY,
                    asset_id='polygon_nft',
                    asset_name='Polygon NFT Collection',
                    confidence=ConfidenceLevel.HIGH,
                    confidence_score=0.85,
                    reasoning='Portfolio lacks chain diversity, Polygon offers good opportunities',
                    expected_return=0.12,
                    risk_level='medium',
                    time_horizon='6-12 months',
                    timestamp=datetime.now(),
                    metadata={'reason': 'chain_diversification', 'priority': 'high'}
                ))
            
            # Check for undervalued opportunities
            undervalued = market_data.get('undervalued_assets', [])
            for asset in undervalued[:2]:  # Top 2 undervalued
                confidence_score = self._calculate_confidence_score(asset)
                confidence_level = self._get_confidence_level(confidence_score)
                
                recommendations.append(MLRecommendation(
                    type=RecommendationType.BUY,
                    asset_id=asset.get('id'),
                    asset_name=asset.get('name'),
                    confidence=confidence_level,
                    confidence_score=confidence_score,
                    reasoning=f"Asset appears undervalued based on {', '.join(asset.get('factors', []))}",
                    expected_return=asset.get('expected_return', 0.15),
                    risk_level=asset.get('risk_level', 'medium'),
                    time_horizon='3-6 months',
                    timestamp=datetime.now(),
                    metadata={'reason': 'undervalued_opportunity', 'factors': asset.get('factors', [])}
                ))
            
            # Generate momentum-based recommendations
            momentum_opportunities = await self._identify_momentum_opportunities(market_data)
            for opp in momentum_opportunities:
                recommendations.append(MLRecommendation(
                    type=RecommendationType.BUY,
                    asset_id=opp['asset_id'],
                    asset_name=opp['asset_name'],
                    confidence=ConfidenceLevel.MEDIUM,
                    confidence_score=0.65,
                    reasoning=f"Strong momentum detected: {opp['momentum_factors']}",
                    expected_return=opp['expected_return'],
                    risk_level='high',
                    time_horizon='1-3 months',
                    timestamp=datetime.now(),
                    metadata={'reason': 'momentum_trading', 'momentum_factors': opp['momentum_factors']}
                ))
            
        except Exception as e:
            logger.error(f"Error generating buy recommendations: {str(e)}")
        
        return recommendations
    
    async def _generate_sell_recommendations(
        self,
        portfolio_analysis: Dict,
        market_data: Dict
    ) -> List[MLRecommendation]:
        """Generate sell recommendations using ML"""
        
        recommendations = []
        
        try:
            # Check for overvalued assets
            overvalued = market_data.get('overvalued_assets', [])
            for asset in overvalued[:2]:  # Top 2 overvalued
                recommendations.append(MLRecommendation(
                    type=RecommendationType.SELL,
                    asset_id=asset.get('id'),
                    asset_name=asset.get('name'),
                    confidence=ConfidenceLevel.HIGH,
                    confidence_score=0.80,
                    reasoning=f"Asset appears overvalued: {', '.join(asset.get('factors', []))}",
                    expected_return=asset.get('expected_return', -0.10),
                    risk_level='high',
                    time_horizon='1-3 months',
                    timestamp=datetime.now(),
                    metadata={'reason': 'overvalued_asset', 'factors': asset.get('factors', [])}
                ))
            
            # Check for concentration risk
            if portfolio_analysis.get('concentration_risk', 0) > 0.7:
                # Recommend selling some concentrated positions
                concentrated_assets = await self._identify_concentrated_assets(portfolio_analysis)
                for asset in concentrated_assets[:2]:
                    recommendations.append(MLRecommendation(
                        type=RecommendationType.SELL,
                        asset_id=asset['asset_id'],
                        asset_name=asset['asset_name'],
                        confidence=ConfidenceLevel.MEDIUM,
                        confidence_score=0.70,
                        reasoning="Reduce concentration risk in portfolio",
                        expected_return=-0.05,  # Small loss for risk reduction
                        risk_level='medium',
                        time_horizon='1-2 months',
                        timestamp=datetime.now(),
                        metadata={'reason': 'concentration_risk_reduction', 'priority': 'medium'}
                    ))
            
        except Exception as e:
            logger.error(f"Error generating sell recommendations: {str(e)}")
        
        return recommendations
    
    async def _generate_rebalancing_recommendations(
        self,
        portfolio_analysis: Dict,
        user_preferences: Dict
    ) -> List[MLRecommendation]:
        """Generate portfolio rebalancing recommendations"""
        
        recommendations = []
        
        try:
            # Check if portfolio needs rebalancing
            current_allocation = portfolio_analysis.get('asset_allocation', {})
            target_allocation = user_preferences.get('target_allocation', {})
            
            if not target_allocation:
                return recommendations
            
            # Calculate allocation drift
            allocation_drift = await self._calculate_allocation_drift(
                current_allocation, target_allocation
            )
            
            # Generate rebalancing recommendations for significant drifts
            for asset_class, drift in allocation_drift.items():
                if abs(drift) > 0.05:  # 5% threshold
                    action = RecommendationType.BUY if drift < 0 else RecommendationType.SELL
                    confidence_score = min(0.9, 0.5 + abs(drift) * 2)  # Higher drift = higher confidence
                    
                    recommendations.append(MLRecommendation(
                        type=action,
                        asset_id=f"rebalance_{asset_class}",
                        asset_name=f"Rebalance {asset_class}",
                        confidence=self._get_confidence_level(confidence_score),
                        confidence_score=confidence_score,
                        reasoning=f"Portfolio allocation for {asset_class} has drifted {drift:.1%} from target",
                        expected_return=0.02,  # Small expected improvement from rebalancing
                        risk_level='low',
                        time_horizon='1 month',
                        timestamp=datetime.now(),
                        metadata={'reason': 'portfolio_rebalancing', 'asset_class': asset_class, 'drift': drift}
                    ))
            
        except Exception as e:
            logger.error(f"Error generating rebalancing recommendations: {str(e)}")
        
        return recommendations
    
    async def _calculate_optimal_allocation(
        self,
        portfolio_data: Dict,
        target_risk: float,
        user_preferences: Dict
    ) -> Dict[str, float]:
        """Calculate optimal asset allocation using modern portfolio theory"""
        
        try:
            # This would use sophisticated optimization algorithms in production
            # For now, use a simplified approach based on risk tolerance
            
            risk_tolerance = user_preferences.get('risk_tolerance', 'moderate')
            risk_score = self.risk_tolerance_mapping.get(risk_tolerance, 0.5)
            
            # Adjust allocation based on risk tolerance
            if risk_score < 0.3:  # Conservative
                return {
                    'blue_chip_nfts': 0.60,
                    'mid_tier_nfts': 0.30,
                    'emerging_nfts': 0.10
                }
            elif risk_score < 0.7:  # Moderate
                return {
                    'blue_chip_nfts': 0.40,
                    'mid_tier_nfts': 0.40,
                    'emerging_nfts': 0.20
                }
            else:  # Aggressive
                return {
                    'blue_chip_nfts': 0.20,
                    'mid_tier_nfts': 0.40,
                    'emerging_nfts': 0.40
                }
                
        except Exception as e:
            logger.error(f"Error calculating optimal allocation: {str(e)}")
            return {}
    
    async def _estimate_return_improvement(
        self,
        current_allocation: Dict[str, float],
        optimal_allocation: Dict[str, float]
    ) -> float:
        """Estimate expected return improvement from reallocation"""
        
        try:
            # Simplified estimation based on historical performance
            # In production, this would use sophisticated models
            
            improvement = 0.0
            for asset_class, target_weight in optimal_allocation.items():
                current_weight = current_allocation.get(asset_class, 0.0)
                weight_diff = abs(target_weight - current_weight)
                
                # Assume 2% improvement per 10% allocation correction
                improvement += weight_diff * 0.2
            
            return min(improvement, 0.15)  # Cap at 15%
            
        except Exception as e:
            logger.error(f"Error estimating return improvement: {str(e)}")
            return 0.0
    
    async def _estimate_risk_reduction(
        self,
        current_allocation: Dict[str, float],
        optimal_allocation: Dict[str, float]
    ) -> float:
        """Estimate risk reduction from reallocation"""
        
        try:
            # Simplified risk reduction estimation
            # In production, this would use variance-covariance matrices
            
            risk_reduction = 0.0
            for asset_class, target_weight in optimal_allocation.items():
                current_weight = current_allocation.get(asset_class, 0.0)
                weight_diff = abs(target_weight - current_weight)
                
                # Assume 3% risk reduction per 10% allocation correction
                risk_reduction += weight_diff * 0.3
            
            return min(risk_reduction, 0.25)  # Cap at 25%
            
        except Exception as e:
            logger.error(f"Error estimating risk reduction: {str(e)}")
            return 0.0
    
    def _calculate_confidence_score(self, asset_data: Dict) -> float:
        """Calculate confidence score for a recommendation"""
        
        try:
            # Base confidence score
            base_score = 0.5
            
            # Adjust based on data quality
            if asset_data.get('data_quality', 'low') == 'high':
                base_score += 0.2
            
            # Adjust based on market conditions
            market_volatility = asset_data.get('market_volatility', 0.5)
            if market_volatility < 0.3:  # Low volatility = higher confidence
                base_score += 0.1
            
            # Adjust based on historical accuracy
            historical_accuracy = asset_data.get('historical_accuracy', 0.5)
            base_score += historical_accuracy * 0.2
            
            return min(max(base_score, 0.1), 0.95)  # Clamp between 0.1 and 0.95
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 0.5
    
    def _get_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """Convert confidence score to confidence level"""
        
        if confidence_score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.6:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.4:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    async def _identify_momentum_opportunities(self, market_data: Dict) -> List[Dict]:
        """Identify momentum-based trading opportunities"""
        
        try:
            # This would analyze price momentum, volume trends, etc.
            # For now, return mock data
            return [
                {
                    'asset_id': 'momentum_1',
                    'asset_name': 'Trending Collection A',
                    'expected_return': 0.25,
                    'momentum_factors': ['volume_spike', 'price_momentum', 'social_buzz']
                },
                {
                    'asset_id': 'momentum_2',
                    'asset_name': 'Trending Collection B',
                    'expected_return': 0.18,
                    'momentum_factors': ['price_momentum', 'institutional_interest']
                }
            ]
            
        except Exception as e:
            logger.error(f"Error identifying momentum opportunities: {str(e)}")
            return []
    
    async def _identify_concentrated_assets(self, portfolio_analysis: Dict) -> List[Dict]:
        """Identify assets with high concentration in portfolio"""
        
        try:
            # This would analyze actual portfolio data
            # For now, return mock data
            return [
                {
                    'asset_id': 'concentrated_1',
                    'asset_name': 'High Concentration Asset',
                    'concentration': 0.45
                }
            ]
            
        except Exception as e:
            logger.error(f"Error identifying concentrated assets: {str(e)}")
            return []
    
    async def _calculate_allocation_drift(
        self,
        current_allocation: Dict[str, float],
        target_allocation: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate allocation drift from target"""
        
        try:
            drift = {}
            for asset_class in target_allocation:
                current = current_allocation.get(asset_class, 0.0)
                target = target_allocation.get(asset_class, 0.0)
                drift[asset_class] = current - target
            
            return drift
            
        except Exception as e:
            logger.error(f"Error calculating allocation drift: {str(e)}")
            return {}
    
    async def _get_collection_data(self, collection_id: str) -> Optional[Dict]:
        """Get collection data for analysis"""
        
        try:
            # This would query the database or external APIs
            # For now, return mock data
            return {
                'id': collection_id,
                'name': f'Collection {collection_id}',
                'floor_price': 1000,
                'volume_24h': 50000,
                'holders': 1000,
                'market_cap': 10000000
            }
            
        except Exception as e:
            logger.error(f"Error getting collection data: {str(e)}")
            return None
    
    async def _analyze_market_indicators(self, collection_data: Dict) -> Dict:
        """Analyze market indicators for a collection"""
        
        try:
            # This would perform technical analysis
            # For now, return mock analysis
            return {
                'price_trend': 'bullish',
                'volume_trend': 'increasing',
                'momentum_score': 0.7,
                'volatility': 0.3
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market indicators: {str(e)}")
            return {}
    
    async def _generate_market_prediction(
        self,
        collection_id: str,
        collection_data: Dict,
        market_indicators: Dict,
        time_horizon: str
    ) -> Optional[MarketPrediction]:
        """Generate market prediction for a collection"""
        
        try:
            # Analyze indicators to determine prediction
            price_trend = market_indicators.get('price_trend', 'neutral')
            momentum_score = market_indicators.get('momentum_score', 0.5)
            
            if price_trend == 'bullish' and momentum_score > 0.6:
                predicted_movement = 'up'
                confidence_score = momentum_score
            elif price_trend == 'bearish' and momentum_score < 0.4:
                predicted_movement = 'down'
                confidence_score = 1 - momentum_score
            else:
                predicted_movement = 'stable'
                confidence_score = 0.5
            
            key_factors = []
            if market_indicators.get('volume_trend') == 'increasing':
                key_factors.append('increasing_volume')
            if market_indicators.get('momentum_score', 0) > 0.6:
                key_factors.append('strong_momentum')
            if market_indicators.get('volatility', 0) < 0.4:
                key_factors.append('low_volatility')
            
            return MarketPrediction(
                collection_id=collection_id,
                collection_name=collection_data.get('name', 'Unknown'),
                predicted_movement=predicted_movement,
                confidence_score=confidence_score,
                time_horizon=time_horizon,
                key_factors=key_factors,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating market prediction: {str(e)}")
            return None
    
    async def _analyze_trending_opportunity(self, collection: Dict) -> Optional[Dict]:
        """Analyze a trending collection for investment opportunity"""
        
        try:
            # Calculate opportunity score based on various factors
            opportunity_score = 0.0
            
            # Volume growth
            volume_growth = collection.get('volume_growth', 0)
            if volume_growth > 0.5:  # 50% growth
                opportunity_score += 0.3
            
            # Price momentum
            price_momentum = collection.get('price_momentum', 0)
            if price_momentum > 0.2:  # 20% price increase
                opportunity_score += 0.3
            
            # Social buzz
            social_buzz = collection.get('social_buzz', 0)
            if social_buzz > 0.7:  # High social engagement
                opportunity_score += 0.2
            
            # Market cap to volume ratio
            market_cap = collection.get('market_cap', 0)
            volume = collection.get('volume_24h', 0)
            if market_cap > 0 and volume > 0:
                volume_ratio = volume / market_cap
                if volume_ratio > 0.1:  # High volume relative to market cap
                    opportunity_score += 0.2
            
            if opportunity_score > 0.3:  # Minimum threshold
                return {
                    'collection': collection,
                    'opportunity_score': opportunity_score,
                    'recommendation': 'Strong buy opportunity' if opportunity_score > 0.7 else 'Consider buying'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing trending opportunity: {str(e)}")
            return None

# Example usage and testing
async def main():
    """Test the ML Recommendations Engine"""
    engine = MLRecommendationsEngine()
    
    # Mock data
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
        ],
        'trending_collections': [
            {'id': 'trend1', 'name': 'Trending A', 'volume_growth': 0.8, 'price_momentum': 0.3, 'social_buzz': 0.8, 'market_cap': 1000000, 'volume_24h': 150000},
            {'id': 'trend2', 'name': 'Trending B', 'volume_growth': 0.6, 'price_momentum': 0.25, 'social_buzz': 0.7, 'market_cap': 2000000, 'volume_24h': 200000}
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
    
    print("🤖 Generating ML-Powered Recommendations...")
    recommendations = await engine.generate_portfolio_recommendations(
        portfolio_data, market_data, user_preferences
    )
    
    print(f"\n📊 Generated {len(recommendations)} recommendations:")
    for rec in recommendations:
        print(f"  • {rec.type.value.upper()}: {rec.asset_name}")
        print(f"    Confidence: {rec.confidence.value} ({rec.confidence_score:.0%})")
        print(f"    Reasoning: {rec.reasoning}")
        print(f"    Expected Return: {rec.expected_return:.1%}")
    
    print("\n🔮 Market Predictions:")
    predictions = await engine.predict_market_movements(['bayc', 'doodles'], '30d')
    for pred in predictions:
        print(f"  • {pred.collection_name}: {pred.predicted_movement.upper()}")
        print(f"    Confidence: {pred.confidence_score:.0%}")
        print(f"    Factors: {', '.join(pred.key_factors)}")
    
    print("\n⚖️  Portfolio Optimization:")
    optimization = await engine.optimize_portfolio_allocation(
        portfolio_data, 0.5, user_preferences
    )
    if optimization:
        print(f"  Expected Improvement: {optimization.expected_improvement:.1%}")
        print(f"  Risk Reduction: {optimization.risk_reduction:.1%}")
    
    print("\n📈 Market Sentiment:")
    sentiment = await engine.analyze_market_sentiment(market_data)
    print(f"  Overall Sentiment: {sentiment.value}")
    
    print("\n🚀 Trending Opportunities:")
    opportunities = await engine.get_trending_opportunities(market_data)
    for opp in opportunities:
        print(f"  • {opp['collection']['name']}: {opp['recommendation']}")

if __name__ == "__main__":
    asyncio.run(main())
