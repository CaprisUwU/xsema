"""
Market Analysis Utilities

This module provides functions to analyze NFT market data, including pricing, trading volume,
liquidity metrics, and market trends. It supports both real-time data fetching from various
NFT marketplaces and simulated data for development and testing.
"""
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import time
import json
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter, Retry
import pandas as pd
import numpy as np

# Type aliases
TokenId = Union[str, int]
Address = str
Price = float
Volume = float
Timestamp = int

@dataclass
class NFTMarketData:
    """Container for NFT market data."""
    token_id: TokenId
    current_price: Optional[Price] = None
    last_sale_price: Optional[Price] = None
    last_sale_timestamp: Optional[Timestamp] = None
    num_owners: int = 1
    total_volume: Volume = 0.0
    price_history: List[Tuple[Timestamp, Price]] = None
    traits: Dict[str, str] = None
    
    def __post_init__(self):
        if self.price_history is None:
            self.price_history = []
        if self.traits is None:
            self.traits = {}
    
    def add_price_point(self, timestamp: Timestamp, price: Price):
        """Add a price point to the price history."""
        self.price_history.append((timestamp, price))
        self.price_history.sort()  # Keep sorted by timestamp
        self.current_price = price
    
    def get_price_change(self, days: int = 7) -> Optional[float]:
        """Calculate price change over the specified number of days."""
        if not self.price_history or len(self.price_history) < 2:
            return None
            
        now = int(time.time())
        cutoff = now - (days * 24 * 60 * 60)
        
        # Find prices within the time window
        recent_prices = [p for t, p in self.price_history if t >= cutoff]
        
        if len(recent_prices) < 2:
            return None
            
        start_price = recent_prices[0]
        end_price = recent_prices[-1]
        
        if start_price == 0:
            return None
            
        return (end_price - start_price) / start_price

class NFTMarketAnalyzer:
    """
    Analyzes NFT market data from various sources.
    
    Args:
        cache_dir: Directory to cache API responses
        mock_mode: If True, use mock data instead of real API calls
        mock_data: Pre-loaded mock data for testing
    """
    
    def __init__(
        self,
        cache_dir: str = "./market_cache",
        mock_mode: bool = False,
        mock_data: Optional[Dict[TokenId, NFTMarketData]] = None
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.mock_mode = mock_mode
        self.mock_data = mock_data or {}
        
        # Configure HTTP session with retries
        self.session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
    
    def _get_cache_path(self, key: str) -> Path:
        """Get path for a cache file."""
        return self.cache_dir / f"{key}.json"
    
    def _load_from_cache(self, key: str, max_age_hours: int = 24) -> Optional[dict]:
        """Load data from cache if it exists and is fresh."""
        cache_file = self._get_cache_path(key)
        
        if not cache_file.exists():
            return None
            
        # Check cache age
        cache_age = time.time() - cache_file.stat().st_mtime
        if cache_age > (max_age_hours * 3600):
            return None
            
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _save_to_cache(self, key: str, data: dict):
        """Save data to cache."""
        cache_file = self._get_cache_path(key)
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save cache: {e}")
    
    def _generate_mock_data(self, token_id: TokenId) -> NFTMarketData:
        """Generate realistic mock market data for testing."""
        if token_id in self.mock_data:
            return self.mock_data[token_id]
            
        # Generate some realistic-looking mock data
        now = int(time.time())
        days_ago = random.randint(0, 365)
        last_sale = now - (days_ago * 24 * 60 * 60)
        
        # Base price based on token ID (lower IDs are more valuable)
        base_price = 1.0 / (1 + (int(str(token_id)) % 1000) * 0.001)
        
        # Add some randomness
        price = base_price * random.uniform(0.8, 1.2)
        last_sale_price = price * random.uniform(0.7, 1.3)
        
        # Generate price history
        price_history = []
        for i in range(random.randint(5, 20)):
            timestamp = now - (random.randint(0, 90) * 24 * 60 * 60)
            hist_price = last_sale_price * random.uniform(0.5, 1.5)
            price_history.append((timestamp, hist_price))
        
        # Sort by timestamp
        price_history.sort()
        
        data = NFTMarketData(
            token_id=token_id,
            current_price=price,
            last_sale_price=last_sale_price,
            last_sale_timestamp=last_sale,
            num_owners=random.randint(1, 10),
            total_volume=last_sale_price * random.uniform(1, 5),
            price_history=price_history,
            traits={
                "rarity": random.choice(["common", "uncommon", "rare", "epic", "legendary"]),
                "background": random.choice(["red", "blue", "green", "gold"]),
                "type": f"type_{random.randint(1, 10)}"
            }
        )
        
        self.mock_data[token_id] = data
        return data
    
    def get_nft_data(self, token_id: TokenId) -> NFTMarketData:
        """
        Get market data for a specific NFT.
        
        Args:
            token_id: The token ID to fetch data for
            
        Returns:
            NFTMarketData object containing the market data
        """
        if self.mock_mode:
            return self._generate_mock_data(token_id)
            
        # TODO: Implement real API calls to OpenSea, LooksRare, etc.
        # For now, return mock data
        return self._generate_mock_data(token_id)
    
    def get_collection_stats(self, collection_address: Address) -> Dict:
        """
        Get statistics for an entire collection.
        
        Args:
            collection_address: The contract address of the collection
            
        Returns:
            Dictionary containing collection statistics
        """
        cache_key = f"collection_{collection_address.lower()}"
        cached = self._load_from_cache(cache_key)
        
        if cached is not None:
            return cached
            
        if self.mock_mode:
            # Generate mock collection stats
            stats = {
                "total_supply": random.randint(5000, 20000),
                "num_owners": random.randint(1000, 15000),
                "floor_price": random.uniform(0.1, 10.0),
                "total_volume": random.uniform(1000, 1000000),
                "seven_day_volume": random.uniform(100, 100000),
                "seven_day_change": random.uniform(-0.5, 1.5),
                "average_price": random.uniform(0.5, 5.0),
                "market_cap": random.uniform(5000, 5000000)
            }
            
            self._save_to_cache(cache_key, stats)
            return stats
            
        # TODO: Implement real API calls
        return {}
    
    def get_rarity_score(self, token_id: TokenId, traits: Dict[str, str]) -> float:
        """
        Calculate a rarity score based on traits.
        
        Args:
            token_id: The token ID
            traits: Dictionary of trait names to values
            
        Returns:
            Rarity score (higher is more rare)
        """
        # In a real implementation, this would analyze the distribution of traits
        # across the collection. For now, we'll use a simple mock implementation.
        
        # Base rarity based on token ID (lower IDs are rarer)
        rarity = 1.0 / (1 + (int(str(token_id)) % 1000) * 0.001)
        
        # Adjust based on traits
        for trait, value in traits.items():
            # Simple mock: some traits are rarer than others
            if trait == "background" and value == "gold":
                rarity *= 5.0
            elif trait == "type" and value.endswith("_1"):
                rarity *= 3.0
                
        return round(rarity, 4)
    
    def get_market_score(self, token_id: TokenId) -> float:
        """
        Get a market score for an NFT (0-1 scale).
        Combines price, rarity, and other factors into a single score.
        
        Args:
            token_id: The token ID to score
            
        Returns:
            Market score between 0 and 1
        """
        data = self.get_nft_data(token_id)
        
        if not data:
            return 0.0
            
        # Get collection stats for normalization
        collection_stats = self.get_collection_stats("0x...")  # Would use actual collection address
        
        # Calculate price score (0-1)
        if data.current_price is not None and collection_stats.get('floor_price', 0) > 0:
            price_ratio = collection_stats['floor_price'] / data.current_price
            price_score = min(1.0, price_ratio)
        else:
            price_score = 0.5  # Neutral score if no price data
        
        # Calculate rarity score (0-1)
        rarity = self.get_rarity_score(token_id, data.traits or {})
        rarity_score = min(1.0, rarity / 10.0)  # Normalize to 0-1 range
        
        # Calculate recency score (0-1, higher for more recent sales)
        if data.last_sale_timestamp:
            days_since_sale = (time.time() - data.last_sale_timestamp) / (24 * 60 * 60)
            recency_score = 1.0 / (1.0 + days_since_sale / 30.0)  # Halflife of 30 days
        else:
            recency_score = 0.5
        
        # Combine scores with weights
        weights = {
            'price': 0.4,
            'rarity': 0.4,
            'recency': 0.2
        }
        
        total_score = (
            weights['price'] * price_score +
            weights['rarity'] * rarity_score +
            weights['recency'] * recency_score
        )
        
        return round(total_score, 4)

# Default instance
default_analyzer = NFTMarketAnalyzer(mock_mode=True)

def get_market_score(token_id: TokenId) -> float:
    """
    Convenience function to get a market score for a token using the default analyzer.
    
    Args:
        token_id: The token ID to score
        
    Returns:
        Market score between 0 and 1
    """
    return default_analyzer.get_market_score(token_id)

def get_trade_history(collection_address: str, days: int = 30) -> List[Dict]:
    """
    Get trade history for a collection.
    
    Args:
        collection_address: The contract address of the collection
        days: Number of days of history to retrieve
        
    Returns:
        List of trade dictionaries with timestamp, price, and other metadata
    """
    # In a real implementation, this would fetch from an API or database
    # For now, return mock data
    now = int(time.time())
    day_seconds = 24 * 60 * 60
    
    trades = []
    for i in range(days * 3):  # 3 trades per day
        timestamp = now - (i * day_seconds // 3)
        price = random.uniform(0.5, 5.0)  # Random price in ETH
        
        trades.append({
            'timestamp': timestamp,
            'price': round(price, 4),
            'token_id': str(random.randint(1, 10000)),
            'seller': f"0x{'%040x' % random.getrandbits(160)}",
            'buyer': f"0x{'%040x' % random.getrandbits(160)}", 
            'tx_hash': f"0x{'%064x' % random.getrandbits(256)}"
        })
    
    return trades

def get_price_data(collection_address: str, days: int = 30) -> Dict[str, List]:
    """
    Get price data for a collection.
    
    Args:
        collection_address: The contract address of the collection
        days: Number of days of price history to retrieve
        
    Returns:
        Dictionary with 'timestamps' and 'prices' lists
    """
    # In a real implementation, this would fetch from an API or database
    # For now, return mock data
    now = int(time.time())
    day_seconds = 24 * 60 * 60
    
    timestamps = []
    prices = []
    
    for i in range(days):
        timestamp = now - ((days - i - 1) * day_seconds)
        price = random.uniform(1.0, 10.0)  # Random price in ETH
        
        timestamps.append(timestamp)
        prices.append(round(price, 4))
    
    return {
        'timestamps': timestamps,
        'prices': prices,
        'min_price': min(prices) if prices else 0,
        'max_price': max(prices) if prices else 0,
        'avg_price': round(sum(prices) / len(prices), 4) if prices else 0
    }

def analyze_market_patterns(collection_address: str, days: int = 30) -> Dict[str, Any]:
    """
    Analyze market patterns for a collection including trends, volatility, and anomalies.
    
    Args:
        collection_address: The contract address of the collection
        days: Number of days of data to analyze
        
    Returns:
        Dictionary containing pattern analysis results
    """
    # Get price and trade data
    price_data = get_price_data(collection_address, days)
    trade_history = get_trade_history(collection_address, days)
    
    if not price_data['prices'] or not trade_history:
        return {
            'trend': 'insufficient_data',
            'volatility': 0.0,
            'volume_trend': 'insufficient_data',
            'price_momentum': 0.0,
            'anomalies': [],
            'support_resistance': {'support': 0.0, 'resistance': 0.0}
        }
    
    prices = price_data['prices']
    timestamps = price_data['timestamps']
    
    # Calculate trend (simple linear regression)
    if len(prices) > 1:
        x = np.array(range(len(prices)))
        y = np.array(prices)
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.01:
            trend = 'bullish'
        elif slope < -0.01:
            trend = 'bearish'
        else:
            trend = 'sideways'
    else:
        trend = 'insufficient_data'
        slope = 0.0
    
    # Calculate volatility (standard deviation of price changes)
    if len(prices) > 1:
        price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        volatility = np.std(price_changes) if price_changes else 0.0
    else:
        volatility = 0.0
    
    # Calculate volume trend
    if trade_history:
        daily_volumes = {}
        for trade in trade_history:
            day = trade['timestamp'] // (24 * 60 * 60)
            if day not in daily_volumes:
                daily_volumes[day] = 0
            daily_volumes[day] += trade['price']
        
        if len(daily_volumes) > 1:
            volume_values = list(daily_volumes.values())
            volume_slope = np.polyfit(range(len(volume_values)), volume_values, 1)[0]
            
            if volume_slope > 0.01:
                volume_trend = 'increasing'
            elif volume_slope < -0.01:
                volume_trend = 'decreasing'
            else:
                volume_trend = 'stable'
        else:
            volume_trend = 'insufficient_data'
    else:
        volume_trend = 'insufficient_data'
    
    # Calculate price momentum (rate of change)
    if len(prices) >= 7:
        recent_prices = prices[-7:]  # Last 7 days
        momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] if recent_prices[0] > 0 else 0.0
    else:
        momentum = 0.0
    
    # Detect anomalies (prices that are 2+ standard deviations from mean)
    anomalies = []
    if len(prices) > 1:
        mean_price = np.mean(prices)
        std_price = np.std(prices)
        threshold = 2 * std_price
        
        for i, price in enumerate(prices):
            if abs(price - mean_price) > threshold:
                anomalies.append({
                    'index': i,
                    'price': price,
                    'timestamp': timestamps[i] if i < len(timestamps) else 0,
                    'deviation': abs(price - mean_price) / std_price
                })
    
    # Calculate support and resistance levels
    if len(prices) > 1:
        support = min(prices) * 0.95  # 5% below lowest price
        resistance = max(prices) * 1.05  # 5% above highest price
    else:
        support = resistance = prices[0] if prices else 0.0
    
    return {
        'trend': trend,
        'volatility': round(volatility, 4),
        'volume_trend': volume_trend,
        'price_momentum': round(momentum, 4),
        'anomalies': anomalies,
        'support_resistance': {
            'support': round(support, 4),
            'resistance': round(resistance, 4)
        },
        'price_data': price_data,
        'trade_count': len(trade_history)
    }

# Example usage
if __name__ == "__main__":
    # Create an analyzer (in mock mode for this example)
    analyzer = NFTMarketAnalyzer(mock_mode=True)
    
    # Get data for a few tokens
    for token_id in ["1", "42", "999"]:
        data = analyzer.get_nft_data(token_id)
        score = analyzer.get_market_score(token_id)
        
        print(f"\nToken {token_id}:")
        print(f"  Current Price: {data.current_price or 'N/A'}")
        print(f"  Last Sale: {data.last_sale_price or 'N/A'}")
        print(f"  Rarity: {analyzer.get_rarity_score(token_id, data.traits or {})}")
        print(f"  Market Score: {score:.2f}")
    
    # Get collection stats
    stats = analyzer.get_collection_stats("0x123...")
    print("\nCollection Stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
