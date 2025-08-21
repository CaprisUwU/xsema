"""
Wash Trading Detection Module

This module identifies potential wash trading activities by analyzing trading patterns
that may indicate artificial volume inflation or price manipulation.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

# Import our utility modules
from utils.market import get_trade_history, get_price_data
from utils.entropy import calculate_entropy
from utils.temporal import analyze_temporal_patterns

class WashTradingDetector:
    """Detects potential wash trading patterns in NFT collections."""
    
    def __init__(self, min_volume_eth: float = 0.1, time_window_hours: int = 24):
        """
        Initialize the wash trading detector.
        
        Args:
            min_volume_eth: Minimum trade volume in ETH to consider
            time_window_hours: Time window to analyze for suspicious patterns
        """
        self.min_volume_eth = min_volume_eth
        self.time_window = timedelta(hours=time_window_hours)
        
    def analyze_collection(self, collection_address: str) -> Dict:
        """
        Analyze a collection for wash trading patterns.
        
        Args:
            collection_address: The NFT collection contract address
            
        Returns:
            Dict containing wash trading analysis results
        """
        # Get trade history
        trades = get_trade_history(collection_address)
        
        if not trades:
            return {"score": 0, "confidence": 0, "suspicious_trades": []}
            
        # Filter by minimum volume
        trades = [t for t in trades if t['value_eth'] >= self.min_volume_eth]
        
        # Detect suspicious patterns
        suspicious_trades = []
        
        # 1. Check for circular trades (A->B->A)
        circular = self._detect_circular_trades(trades)
        suspicious_trades.extend(circular)
        
        # 2. Check for rapid buy/sell patterns
        rapid = self._detect_rapid_turnaround(trades)
        suspicious_trades.extend(rapid)
        
        # 3. Check for volume anomalies
        volume_anomalies = self._detect_volume_anomalies(trades)
        suspicious_trades.extend(volume_anomalies)
        
        # Calculate overall score (0-100)
        score = self._calculate_wash_score(trades, suspicious_trades)
        
        return {
            "score": min(100, int(score * 100)),
            "confidence": self._calculate_confidence(trades, suspicious_trades),
            "suspicious_trades": suspicious_trades[:100],  # Limit to top 100
            "total_trades_analyzed": len(trades),
            "suspicious_count": len(suspicious_trades)
        }
    
    def _detect_circular_trades(self, trades: List[Dict]) -> List[Dict]:
        """Detect circular trading patterns (A->B->A)."""
        suspicious = []
        trade_graph = defaultdict(set)
        
        # Build trade graph
        for trade in trades:
            seller = trade['from']
            buyer = trade['to']
            trade_graph[seller].add((buyer, trade['transaction_hash']))
        
        # Check for cycles
        for seller in trade_graph:
            for buyer, tx_hash in trade_graph[seller]:
                if buyer in trade_graph and any(seller == b for b, _ in trade_graph[buyer]):
                    suspicious.append({
                        'type': 'circular_trade',
                        'addresses': [seller, buyer],
                        'transaction_hash': tx_hash,
                        'confidence': 0.85
                    })
                    
        return suspicious
    
    def _detect_rapid_turnaround(self, trades: List[Dict], max_hours: int = 1) -> List[Dict]:
        """Detect rapid buy/sell patterns."""
        suspicious = []
        token_activity = defaultdict(list)
        
        # Group trades by token
        for trade in trades:
            token_activity[trade['token_id']].append(trade)
        
        # Check for rapid trades
        for token_id, token_trades in token_activity.items():
            if len(token_trades) < 2:
                continue
                
            # Sort by timestamp
            token_trades.sort(key=lambda x: x['timestamp'])
            
            for i in range(1, len(token_trades)):
                prev_trade = token_trades[i-1]
                curr_trade = token_trades[i]
                
                time_diff = curr_trade['timestamp'] - prev_trade['timestamp']
                if time_diff.total_seconds() / 3600 <= max_hours:
                    suspicious.append({
                        'type': 'rapid_turnaround',
                        'token_id': token_id,
                        'time_diff_hours': time_diff.total_seconds() / 3600,
                        'transactions': [prev_trade['transaction_hash'], curr_trade['transaction_hash']],
                        'confidence': 0.75
                    })
                    
        return suspicious
    
    def _detect_volume_anomalies(self, trades: List[Dict]) -> List[Dict]:
        """Detect unusual trading volume patterns."""
        if not trades:
            return []
            
        suspicious = []
        volumes = [t['value_eth'] for t in trades]
        
        if len(volumes) < 5:  # Need at least 5 trades for meaningful stats
            return []
            
        # Calculate statistical measures
        mean_vol = np.mean(volumes)
        std_vol = np.std(volumes)
        
        # Flag trades > 3 standard deviations from mean
        for trade in trades:
            if trade['value_eth'] > mean_vol + 3 * std_vol:
                suspicious.append({
                    'type': 'volume_anomaly',
                    'transaction_hash': trade['transaction_hash'],
                    'value_eth': trade['value_eth'],
                    'mean_volume': mean_vol,
                    'std_dev': std_vol,
                    'confidence': 0.8
                })
                
        return suspicious
    
    def _calculate_wash_score(self, trades: List[Dict], suspicious: List[Dict]) -> float:
        """Calculate a wash trading score (0-1)."""
        if not trades:
            return 0.0
            
        # Base score on percentage of suspicious volume
        total_volume = sum(t['value_eth'] for t in trades)
        suspicious_volume = sum(
            t.get('value_eth', 0) 
            for t in suspicious 
            if t.get('value_eth') is not None
        )
        
        # Normalize score
        score = min(1.0, (suspicious_volume / total_volume) * 2)  # Cap at 1.0
        
        # Adjust based on entropy of trade patterns
        trade_patterns = [
            f"{t['from'][:8]}_{t['to'][:8]}_{t['token_id']}" 
            for t in trades
        ]
        entropy = calculate_entropy(trade_patterns)
        
        # Lower entropy suggests more repetitive patterns (more suspicious)
        return score * (1.0 - entropy)
    
    def _calculate_confidence(self, trades: List[Dict], suspicious: List[Dict]) -> float:
        """Calculate confidence in wash trading detection (0-1)."""
        if not suspicious:
            return 0.0
            
        # Base confidence on number of suspicious patterns found
        base_confidence = min(1.0, len(suspicious) / 10)  # Cap at 1.0
        
        # Adjust based on trade volume and diversity
        total_volume = sum(t['value_eth'] for t in trades)
        avg_volume = total_volume / len(trades) if trades else 0
        
        # More confidence with higher volumes
        volume_factor = min(1.0, np.log10(max(1, total_volume)) / 5)
        
        return min(1.0, base_confidence * (0.7 + 0.3 * volume_factor))

# Example usage
if __name__ == "__main__":
    detector = WashTradingDetector()
    result = detector.analyze_collection("0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D")  # BAYC
    print(f"Wash Trading Score: {result['score']}/100")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Suspicious trades found: {len(result['suspicious_trades'])}")
