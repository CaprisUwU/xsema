"""
Market Capitalization & Analytics Service

This service provides comprehensive market analysis including:
- Collection valuation and market cap
- Trading pattern analysis
- Market efficiency metrics
- Comparative analysis tools
"""
import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MarketCapData:
    """Market capitalization data for a collection"""
    collection_address: str
    chain: str
    total_market_cap: Decimal
    market_cap_usd: Decimal
    circulating_supply: int
    total_supply: int
    holders_count: int
    average_price: Decimal
    price_volatility: Decimal
    volume_market_cap_ratio: Decimal
    last_updated: datetime

@dataclass
class MarketMetrics:
    """Comprehensive market metrics"""
    collection_address: str
    chain: str
    market_dominance: Decimal
    price_efficiency: Decimal
    liquidity_score: Decimal
    trading_activity: Decimal
    market_maturity: str
    risk_level: str

@dataclass
class TradingAnalysis:
    """Trading pattern analysis"""
    collection_address: str
    chain: str
    trading_volume_trend: str
    price_momentum: str
    market_sentiment: str
    volatility_rating: str
    liquidity_rating: str
    trading_patterns: Dict[str, Any]

class MarketCapAnalyzer:
    """Advanced market capitalization and analytics service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.market_cache = {}
        self.analysis_cache = {}
        
        # Market efficiency thresholds
        self.EFFICIENCY_THRESHOLDS = {
            'high': Decimal('0.8'),
            'medium': Decimal('0.6'),
            'low': Decimal('0.4')
        }
    
    async def calculate_market_cap(self, collection_address: str, chain: str) -> Optional[MarketCapData]:
        """Calculate market capitalization for a collection"""
        try:
            # Check cache first
            cache_key = f"{chain}:{collection_address}:market_cap"
            if cache_key in self.market_cache:
                cached_data = self.market_cache[cache_key]
                if (datetime.now(timezone.utc) - cached_data.last_updated).seconds < 300:  # 5 minute cache
                    return cached_data
            
            # Fetch market data
            market_data = await self._fetch_market_data(collection_address, chain)
            if not market_data:
                return None
            
            # Calculate market cap
            market_cap_data = await self._calculate_market_cap_metrics(collection_address, chain, market_data)
            if market_cap_data:
                self.market_cache[cache_key] = market_cap_data
                return market_cap_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating market cap for {collection_address} on {chain}: {str(e)}")
            return None
    
    async def get_market_metrics(self, collection_address: str, chain: str) -> Optional[MarketMetrics]:
        """Get comprehensive market metrics for a collection"""
        try:
            # Check cache first
            cache_key = f"{chain}:{collection_address}:metrics"
            if cache_key in self.analysis_cache:
                cached_data = self.analysis_cache[cache_key]
                if (datetime.now(timezone.utc) - cached_data.last_updated).seconds < 600:  # 10 minute cache
                    return cached_data
            
            # Get market cap data
            market_cap_data = await self.calculate_market_cap(collection_address, chain)
            if not market_cap_data:
                return None
            
            # Calculate metrics
            market_metrics = await self._calculate_market_metrics(collection_address, chain, market_cap_data)
            if market_metrics:
                self.analysis_cache[cache_key] = market_metrics
                return market_metrics
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting market metrics for {collection_address} on {chain}: {str(e)}")
            return None
    
    async def analyze_trading_patterns(self, collection_address: str, chain: str) -> Optional[TradingAnalysis]:
        """Analyze trading patterns for a collection"""
        try:
            # Get market cap data
            market_cap_data = await self.calculate_market_cap(collection_address, chain)
            if not market_cap_data:
                return None
            
            # Analyze trading patterns
            trading_analysis = await self._analyze_trading_patterns(collection_address, chain, market_cap_data)
            return trading_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing trading patterns for {collection_address} on {chain}: {str(e)}")
            return None
    
    async def get_market_comparison(self, collections: List[str], chain: str) -> Dict[str, Any]:
        """Compare multiple collections on the same chain"""
        try:
            comparison_data = {}
            
            for collection_address in collections:
                market_cap_data = await self.calculate_market_cap(collection_address, chain)
                if market_cap_data:
                    comparison_data[collection_address] = {
                        'market_cap': float(market_cap_data.total_market_cap),
                        'market_cap_usd': float(market_cap_data.market_cap_usd),
                        'holders_count': market_cap_data.holders_count,
                        'volume_market_cap_ratio': float(market_cap_data.volume_market_cap_ratio),
                        'price_volatility': float(market_cap_data.price_volatility)
                    }
            
            # Calculate rankings
            if comparison_data:
                # Market cap ranking
                market_cap_ranking = sorted(
                    comparison_data.items(),
                    key=lambda x: x[1]['market_cap'],
                    reverse=True
                )
                
                # Volume efficiency ranking
                efficiency_ranking = sorted(
                    comparison_data.items(),
                    key=lambda x: x[1]['volume_market_cap_ratio'],
                    reverse=True
                )
                
                comparison_data['rankings'] = {
                    'by_market_cap': [item[0] for item in market_cap_ranking],
                    'by_efficiency': [item[0] for item in efficiency_ranking]
                }
            
            return comparison_data
            
        except Exception as e:
            self.logger.error(f"Error getting market comparison: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _fetch_market_data(self, collection_address: str, chain: str) -> Optional[Dict[str, Any]]:
        """Fetch market data from various sources"""
        try:
            # Mock data for now
            return {
                'floor_price': Decimal('15.5'),
                'total_supply': 10000,
                'circulating_supply': 9500,
                'holders_count': 8500,
                'volume_24h': Decimal('1500.0'),
                'price_history': [
                    {'price': Decimal('15.0'), 'timestamp': datetime.now(timezone.utc) - timedelta(hours=1)},
                    {'price': Decimal('15.5'), 'timestamp': datetime.now(timezone.utc)}
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return None
    
    async def _calculate_market_cap_metrics(self, collection_address: str, chain: str, market_data: Dict[str, Any]) -> Optional[MarketCapData]:
        """Calculate market capitalization metrics"""
        try:
            floor_price = market_data['floor_price']
            total_supply = market_data['total_supply']
            circulating_supply = market_data['circulating_supply']
            holders_count = market_data['holders_count']
            volume_24h = market_data['volume_24h']
            
            # Calculate market cap
            total_market_cap = floor_price * total_supply
            market_cap_usd = total_market_cap * Decimal('2000')  # Mock ETH price
            
            # Calculate average price
            average_price = floor_price
            
            # Calculate price volatility
            price_volatility = self._calculate_price_volatility(market_data['price_history'])
            
            # Calculate volume to market cap ratio
            volume_market_cap_ratio = volume_24h / total_market_cap if total_market_cap > 0 else Decimal('0')
            
            return MarketCapData(
                collection_address=collection_address,
                chain=chain,
                total_market_cap=total_market_cap,
                market_cap_usd=market_cap_usd,
                circulating_supply=circulating_supply,
                total_supply=total_supply,
                holders_count=holders_count,
                average_price=average_price,
                price_volatility=price_volatility,
                volume_market_cap_ratio=volume_market_cap_ratio,
                last_updated=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating market cap metrics: {str(e)}")
            return None
    
    async def _calculate_market_metrics(self, collection_address: str, chain: str, market_cap_data: MarketCapData) -> Optional[MarketMetrics]:
        """Calculate comprehensive market metrics"""
        try:
            # Market dominance (would need total market data for comparison)
            market_dominance = Decimal('0.01')  # Mock 1% dominance
            
            # Price efficiency (based on volume/market cap ratio)
            price_efficiency = min(Decimal('1.0'), market_cap_data.volume_market_cap_ratio * 10)
            
            # Liquidity score (based on trading volume and holder distribution)
            liquidity_score = min(Decimal('1.0'), 
                (market_cap_data.volume_market_cap_ratio * 5) + 
                (Decimal(str(market_cap_data.holders_count)) / Decimal('10000') * Decimal('0.5')))
            
            # Trading activity
            trading_activity = min(Decimal('1.0'), market_cap_data.volume_market_cap_ratio * 20)
            
            # Market maturity
            market_maturity = self._determine_market_maturity(market_cap_data)
            
            # Risk level
            risk_level = self._determine_risk_level(market_cap_data)
            
            return MarketMetrics(
                collection_address=collection_address,
                chain=chain,
                market_dominance=market_dominance,
                price_efficiency=price_efficiency,
                liquidity_score=liquidity_score,
                trading_activity=trading_activity,
                market_maturity=market_maturity,
                risk_level=risk_level
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating market metrics: {str(e)}")
            return None
    
    async def _analyze_trading_patterns(self, collection_address: str, chain: str, market_cap_data: MarketCapData) -> Optional[TradingAnalysis]:
        """Analyze trading patterns for a collection"""
        try:
            # Determine trading volume trend
            volume_trend = "stable"
            if market_cap_data.volume_market_cap_ratio > Decimal('0.1'):
                volume_trend = "high"
            elif market_cap_data.volume_market_cap_ratio < Decimal('0.01'):
                volume_trend = "low"
            
            # Determine price momentum
            price_momentum = "stable"
            if market_cap_data.price_volatility > Decimal('0.2'):
                price_momentum = "volatile"
            elif market_cap_data.price_volatility < Decimal('0.05'):
                price_momentum = "stable"
            
            # Determine market sentiment
            market_sentiment = "neutral"
            if market_cap_data.volume_market_cap_ratio > Decimal('0.15') and market_cap_data.price_volatility < Decimal('0.1'):
                market_sentiment = "bullish"
            elif market_cap_data.volume_market_cap_ratio < Decimal('0.01') and market_cap_data.price_volatility > Decimal('0.3'):
                market_sentiment = "bearish"
            
            # Determine volatility rating
            volatility_rating = "low"
            if market_cap_data.price_volatility > Decimal('0.3'):
                volatility_rating = "high"
            elif market_cap_data.price_volatility > Decimal('0.1'):
                volatility_rating = "medium"
            
            # Determine liquidity rating
            liquidity_rating = "low"
            if market_cap_data.volume_market_cap_ratio > Decimal('0.1'):
                liquidity_rating = "high"
            elif market_cap_data.volume_market_cap_ratio > Decimal('0.05'):
                liquidity_rating = "medium"
            
            # Analyze trading patterns
            trading_patterns = {
                'volume_profile': volume_trend,
                'price_stability': price_momentum,
                'market_efficiency': float(market_cap_data.volume_market_cap_ratio),
                'holder_distribution': market_cap_data.holders_count / market_cap_data.total_supply if market_cap_data.total_supply > 0 else 0
            }
            
            return TradingAnalysis(
                collection_address=collection_address,
                chain=chain,
                trading_volume_trend=volume_trend,
                price_momentum=price_momentum,
                market_sentiment=market_sentiment,
                volatility_rating=volatility_rating,
                liquidity_rating=liquidity_rating,
                trading_patterns=trading_patterns
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing trading patterns: {str(e)}")
            return None
    
    def _calculate_price_volatility(self, price_history: List[Dict[str, Any]]) -> Decimal:
        """Calculate price volatility from price history"""
        try:
            if len(price_history) < 2:
                return Decimal('0')
            
            prices = [point['price'] for point in price_history]
            mean_price = sum(prices) / len(prices)
            
            variance = sum((price - mean_price) ** 2 for price in prices) / len(prices)
            volatility = variance.sqrt()
            
            return volatility
            
        except Exception as e:
            self.logger.error(f"Error calculating price volatility: {str(e)}")
            return Decimal('0')
    
    def _determine_market_maturity(self, market_cap_data: MarketCapData) -> str:
        """Determine market maturity level"""
        try:
            # Based on holder count and supply distribution
            holder_ratio = market_cap_data.holders_count / market_cap_data.total_supply if market_cap_data.total_supply > 0 else 0
            
            if holder_ratio > 0.8:
                return "mature"
            elif holder_ratio > 0.5:
                return "developing"
            else:
                return "early"
                
        except Exception:
            return "unknown"
    
    def _determine_risk_level(self, market_cap_data: MarketCapData) -> str:
        """Determine risk level for the collection"""
        try:
            # Risk factors: volatility, liquidity, market cap
            risk_score = 0
            
            # Volatility risk
            if market_cap_data.price_volatility > Decimal('0.3'):
                risk_score += 3
            elif market_cap_data.price_volatility > Decimal('0.1'):
                risk_score += 2
            else:
                risk_score += 1
            
            # Liquidity risk
            if market_cap_data.volume_market_cap_ratio < Decimal('0.01'):
                risk_score += 3
            elif market_cap_data.volume_market_cap_ratio < Decimal('0.05'):
                risk_score += 2
            else:
                risk_score += 1
            
            # Market cap risk (smaller = higher risk)
            if market_cap_data.total_market_cap < Decimal('100'):
                risk_score += 3
            elif market_cap_data.total_market_cap < Decimal('1000'):
                risk_score += 2
            else:
                risk_score += 1
            
            # Determine risk level
            if risk_score >= 7:
                return "high"
            elif risk_score >= 4:
                return "medium"
            else:
                return "low"
                
        except Exception:
            return "unknown"
