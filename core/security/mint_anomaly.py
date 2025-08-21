"""
Mint Anomaly Detection Module

This module identifies unusual patterns in NFT minting activities that may indicate
bot activity, wash trading, or other suspicious behavior.
"""
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, Counter

# Import our utility modules
from utils.temporal import analyze_temporal_patterns, detect_anomalies
from utils.entropy import calculate_entropy
from utils.bitwise import analyze_bytecode_patterns

class MintAnomalyDetector:
    """Detects anomalies in NFT minting patterns."""
    
    def __init__(self, 
                 min_mints_for_analysis: int = 10,
                 time_window_minutes: int = 5):
        """
        Initialize the mint anomaly detector.
        
        Args:
            min_mints_for_analysis: Minimum number of mints needed for analysis
            time_window_minutes: Time window to analyze for burst detection
        """
        self.min_mints = min_mints_for_analysis
        self.time_window = timedelta(minutes=time_window_minutes)
    
    def analyze_collection_mints(self, collection_address: str) -> Dict:
        """
        Analyze minting patterns for a collection.
        
        Args:
            collection_address: The NFT collection contract address
            
        Returns:
            Dict containing mint anomaly analysis results
        """
        # Get mint history (mock function - implement based on your data source)
        mints = self._get_mint_history(collection_address)
        
        if len(mints) < self.min_mints:
            return {
                "score": 0,
                "confidence": 0,
                "anomalies": [],
                "insufficient_data": True
            }
        
        # Detect different types of anomalies
        anomalies = []
        
        # 1. Burst detection (many mints in short time)
        burst_anomalies = self._detect_burst_minting(mints)
        anomalies.extend(burst_anomalies)
        
        # 2. Sequential minting
        seq_anomalies = self._detect_sequential_minting(mints)
        anomalies.extend(seq_anomalies)
        
        # 3. Wallet concentration
        conc_anomalies = self._detect_wallet_concentration(mints)
        anomalies.extend(conc_anomalies)
        
        # 4. Gas price analysis
        gas_anomalies = self._analyze_gas_patterns(mints)
        anomalies.extend(gas_anomalies)
        
        # Calculate overall risk score
        score = self._calculate_risk_score(mints, anomalies)
        
        return {
            "score": min(100, int(score * 100)),
            "confidence": self._calculate_confidence(mints, anomalies),
            "anomalies": sorted(anomalies, key=lambda x: x.get('confidence', 0), reverse=True)[:50],
            "total_mints_analyzed": len(mints),
            "anomaly_count": len(anomalies)
        }
    
    def _get_mint_history(self, collection_address: str) -> List[Dict]:
        """
        Retrieve mint history for a collection.
        Replace with actual implementation based on your data source.
        """
        # This is a mock implementation
        # In production, replace with actual data fetching logic
        return []
    
    def _detect_burst_minting(self, mints: List[Dict]) -> List[Dict]:
        """Detect unusual bursts of minting activity."""
        if not mints:
            return []
            
        # Sort mints by timestamp
        mints_sorted = sorted(mints, key=lambda x: x['timestamp'])
        
        # Group mints into time windows
        window_counts = defaultdict(int)
        for mint in mints_sorted:
            window = mint['timestamp'].replace(second=0, microsecond=0)
            window_counts[window] += 1
        
        # Calculate statistics
        counts = list(window_counts.values())
        if not counts:
            return []
            
        mean = np.mean(counts)
        std = np.std(counts)
        
        # Find anomalous windows
        anomalies = []
        for window, count in window_counts.items():
            if count > mean + 3 * std:  # 3 std devs from mean
                anomalies.append({
                    'type': 'burst_minting',
                    'timestamp': window.isoformat(),
                    'mint_count': count,
                    'mean_mints': mean,
                    'std_dev': std,
                    'confidence': min(0.99, (count - mean) / (3 * std) * 0.3 + 0.7)
                })
                
        return anomalies
    
    def _detect_sequential_minting(self, mints: List[Dict]) -> List[Dict]:
        """Detect sequential token ID minting patterns."""
        if len(mints) < 10:  # Need enough mints to detect patterns
            return []
            
        # Sort by block number and transaction index
        sorted_mints = sorted(
            mints, 
            key=lambda x: (x.get('block_number', 0), x.get('transaction_index', 0))
        )
        
        # Extract token IDs
        token_ids = [int(mint['token_id']) for mint in sorted_mints]
        
        # Check for sequential patterns
        sequential_blocks = []
        current_block = []
        
        for i in range(1, len(token_ids)):
            if token_ids[i] == token_ids[i-1] + 1:
                if not current_block:
                    current_block = [token_ids[i-1], token_ids[i]]
                else:
                    current_block.append(token_ids[i])
            else:
                if len(current_block) >= 5:  # Minimum sequence length
                    sequential_blocks.append(current_block)
                current_block = []
        
        # Check the last block
        if len(current_block) >= 5:
            sequential_blocks.append(current_block)
            
        # Create anomaly records
        anomalies = []
        for block in sequential_blocks:
            if len(block) >= 10:  # Only flag significant sequences
                confidence = min(0.95, 0.7 + 0.05 * len(block))  # Longer sequences get higher confidence
                anomalies.append({
                    'type': 'sequential_minting',
                    'token_ids': block[:10] + ['...'] if len(block) > 10 else block,
                    'sequence_length': len(block),
                    'confidence': confidence
                })
                
        return anomalies
    
    def _detect_wallet_concentration(self, mints: List[Dict]) -> List[Dict]:
        """Detect if a small number of wallets are responsible for most mints."""
        if not mints:
            return []
            
        # Count mints per wallet
        wallet_counts = Counter(mint['minter'] for mint in mints)
        
        # Calculate Gini coefficient (measure of inequality)
        values = sorted(wallet_counts.values())
        n = len(values)
        if n == 0:
            return []
            
        # Gini coefficient calculation
        gini = sum((i + 1) * val for i, val in enumerate(values))
        gini = 2 * gini / (n * sum(values)) - (n + 1) / n
        
        # Flag high concentration
        if gini > 0.7:  # Threshold for high concentration
            top_wallets = wallet_counts.most_common(3)
            return [{
                'type': 'wallet_concentration',
                'gini_coefficient': gini,
                'top_wallets': [
                    {'address': addr, 'mint_count': count}
                    for addr, count in top_wallets
                ],
                'confidence': min(0.99, (gini - 0.7) * 5 + 0.7)  # Scale confidence
            }]
            
        return []
    
    def _analyze_gas_patterns(self, mints: List[Dict]) -> List[Dict]:
        """Analyze gas patterns for potential bot activity."""
        if len(mints) < 10:  # Need enough data points
            return []
            
        # Extract gas prices and timestamps
        gas_prices = [mint.get('gas_price', 0) for mint in mints]
        timestamps = [mint['timestamp'].timestamp() for mint in mints]
        
        # Calculate gas price percentiles
        p25 = np.percentile(gas_prices, 25)
        p75 = np.percentile(gas_prices, 75)
        iqr = p75 - p25
        
        # Find high gas price outliers
        outliers = []
        for i, (gas, ts) in enumerate(zip(gas_prices, timestamps)):
            if gas > p75 + 3 * iqr:  # High gas price
                outliers.append({
                    'type': 'high_gas_mint',
                    'gas_price': gas,
                    'percentile': np.mean(gas_prices <= gas) * 100,
                    'timestamp': datetime.fromtimestamp(ts).isoformat(),
                    'transaction_hash': mints[i].get('transaction_hash', '')
                })
        
        # If many high gas mints, calculate confidence based on percentage
        if outliers:
            outlier_percent = len(outliers) / len(mints)
            for outlier in outliers:
                outlier['confidence'] = min(0.9, outlier_percent * 2)
                
        return outliers
    
    def _calculate_risk_score(self, mints: List[Dict], anomalies: List[Dict]) -> float:
        """Calculate overall risk score (0-1)."""
        if not mints or not anomalies:
            return 0.0
            
        # Base score on number and severity of anomalies
        anomaly_scores = {
            'burst_minting': 0.7,
            'sequential_minting': 0.8,
            'wallet_concentration': 0.9,
            'high_gas_mint': 0.6
        }
        
        total_score = 0.0
        max_possible = 0.0
        
        for anomaly in anomalies:
            weight = anomaly_scores.get(anomaly['type'], 0.5)
            confidence = anomaly.get('confidence', 0.5)
            total_score += weight * confidence
            max_possible += weight
            
        return min(1.0, total_score / max(1, max_possible))
    
    def _calculate_confidence(self, mints: List[Dict], anomalies: List[Dict]) -> float:
        """Calculate confidence in the analysis (0-1)."""
        if not mints:
            return 0.0
            
        # Base confidence on number of mints analyzed
        mint_count = len(mints)
        count_confidence = min(1.0, np.log10(max(1, mint_count)) / 3)
        
        # Adjust based on anomaly consistency
        if not anomalies:
            return count_confidence * 0.8  # High confidence in negative result
            
        # If we have anomalies, confidence depends on their strength
        anomaly_confidences = [a.get('confidence', 0.5) for a in anomalies]
        avg_confidence = sum(anomaly_confidences) / len(anomaly_confidences)
        
        return min(1.0, (count_confidence * 0.3) + (avg_confidence * 0.7))

# Example usage
if __name__ == "__main__":
    detector = MintAnomalyDetector()
    result = detector.analyze_collection_mints("0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D")  # BAYC
    print(f"Mint Anomaly Score: {result['score']}/100")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Anomalies detected: {len(result['anomalies'])}")
