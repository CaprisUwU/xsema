"""
Tests for security detection modules.

This module contains unit tests for the wash trading and mint anomaly detection
features to ensure they correctly identify suspicious patterns in NFT trading and minting.
"""
import pytest
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import numpy as np

# Import the modules to test
from core.security.wash_trading import WashTradingDetector
from core.security.mint_anomaly import MintAnomalyDetector

# Sample test data
SAMPLE_TRADES = [
    {
        'from': '0x1111111111111111111111111111111111111111',
        'to': '0x2222222222222222222222222222222222222222',
        'token_id': '1',
        'value_eth': 0.1,
        'transaction_hash': '0xaaa',
        'timestamp': datetime.now(timezone.utc) - timedelta(hours=2)
    },
    # Add more test trades as needed
]

SAMPLE_MINTS = [
    {
        'minter': '0x1111111111111111111111111111111111111111',
        'token_id': '1001',
        'transaction_hash': '0xbbb',
        'timestamp': datetime.now(timezone.utc) - timedelta(minutes=10),
        'gas_price': 1000000000
    },
    # Add more test mints as needed
]

class TestWashTradingDetector:
    """Test cases for WashTradingDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create a WashTradingDetector instance for testing."""
        return WashTradingDetector(min_volume_eth=0.01, time_window_hours=24)
    
    def test_detect_circular_trades(self, detector):
        """Test detection of circular trading patterns."""
        # Create circular trades: A->B->A
        trades = [
            {
                'from': '0xA',
                'to': '0xB',
                'token_id': '1',
                'value_eth': 0.1,
                'transaction_hash': '0x1',
                'timestamp': datetime.now(timezone.utc)
            },
            {
                'from': '0xB',
                'to': '0xA',
                'token_id': '1',
                'value_eth': 0.1,
                'transaction_hash': '0x2',
                'timestamp': datetime.now(timezone.utc) + timedelta(minutes=5)
            }
        ]
        
        suspicious = detector._detect_circular_trades(trades)
        assert len(suspicious) > 0
        assert suspicious[0]['type'] == 'circular_trade'
        assert '0xA' in suspicious[0]['addresses']
        assert '0xB' in suspicious[0]['addresses']
    
    def test_detect_rapid_turnaround(self, detector):
        """Test detection of rapid buy/sell patterns."""
        # Create rapid trades of the same token
        now = datetime.now(timezone.utc)
        trades = [
            {
                'from': '0xA',
                'to': '0xB',
                'token_id': '1',
                'value_eth': 0.1,
                'transaction_hash': '0x1',
                'timestamp': now
            },
            {
                'from': '0xB',
                'to': '0xC',
                'token_id': '1',
                'value_eth': 0.1,
                'transaction_hash': '0x2',
                'timestamp': now + timedelta(minutes=30)  # Within 1 hour
            }
        ]
        
        suspicious = detector._detect_rapid_turnaround(trades)
        assert len(suspicious) > 0
        assert suspicious[0]['type'] == 'rapid_turnaround'
        assert suspicious[0]['time_diff_hours'] < 1
    
    @patch('core.security.wash_trading.get_trade_history')
    def test_analyze_collection(self, mock_get_trades, detector):
        """Test end-to-end wash trading analysis."""
        # Mock the trade history
        mock_get_trades.return_value = SAMPLE_TRADES
        
        # Run the analysis
        result = detector.analyze_collection('0x1234')
        
        # Verify the results
        assert 'score' in result
        assert 'suspicious_trades' in result
        assert isinstance(result['score'], (int, float))
        assert 0 <= result['score'] <= 100

class TestMintAnomalyDetector:
    """Test cases for MintAnomalyDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create a MintAnomalyDetector instance for testing."""
        return MintAnomalyDetector(min_mints_for_analysis=1, time_window_minutes=5)
    
    def test_detect_burst_minting(self, detector):
        """Test detection of burst minting patterns."""
        # Create a burst of mints in a short time
        now = datetime.now(timezone.utc)
        mints = [
            {
                'minter': f'0x{i:040x}',
                'token_id': str(1000 + i),
                'transaction_hash': f'0x{i:064x}',
                'timestamp': now + timedelta(seconds=i),
                'gas_price': 1000000000
            }
            for i in range(10)  # 10 mints in quick succession
        ]
        
        anomalies = detector._detect_burst_minting(mints)
        assert len(anomalies) > 0
        assert anomalies[0]['type'] == 'burst_minting'
        assert anomalies[0]['mint_count'] >= 10
    
    def test_detect_sequential_minting(self, detector):
        """Test detection of sequential token ID minting."""
        # Create sequential token mints
        now = datetime.now(timezone.utc)
        mints = [
            {
                'minter': '0xA',
                'token_id': str(1000 + i),
                'transaction_hash': f'0x{i:064x}',
                'timestamp': now + timedelta(minutes=i),
                'gas_price': 1000000000
            }
            for i in range(10)  # 10 sequential token IDs
        ]
        
        anomalies = detector._detect_sequential_minting(mints)
        assert len(anomalies) > 0
        assert anomalies[0]['type'] == 'sequential_minting'
        assert anomalies[0]['sequence_length'] >= 5  # Minimum sequence length
    
    @patch('core.security.mint_anomaly.MintAnomalyDetector._get_mint_history')
    def test_analyze_collection_mints(self, mock_get_mints, detector):
        """Test end-to-end mint anomaly detection."""
        # Mock the mint history
        mock_get_mints.return_value = SAMPLE_MINTS
        
        # Run the analysis
        result = detector.analyze_collection_mints('0x1234')
        
        # Verify the results
        assert 'score' in result
        assert 'anomalies' in result
        assert isinstance(result['score'], (int, float))
        assert 0 <= result['score'] <= 100

# Integration test with the security analyzer
class TestSecurityAnalyzerIntegration:
    """Integration tests for security analyzer with the new detectors."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a SecurityAnalyzer instance for testing."""
        from services.security_analyzer import SecurityAnalyzer
        return SecurityAnalyzer()
    
    @pytest.mark.asyncio
    @patch('services.security_analyzer.SecurityAnalyzer._get_mint_history')
    @patch('core.security.wash_trading.get_trade_history')
    async def test_analyze_contract_with_detectors(self, mock_get_trades, mock_get_mints, analyzer):
        """Test contract analysis with the new detectors."""
        # Mock the external dependencies
        mock_get_trades.return_value = SAMPLE_TRADES
        mock_get_mints.return_value = SAMPLE_MINTS
        
        # Mock Web3 contract code
        analyzer.w3 = MagicMock()
        analyzer.w3.eth.get_code.return_value = b'\x60\x60\x60'  # Some bytecode
        
        # Run the analysis
        result = await analyzer.analyze_contract('0x1234')
        
        # Verify the results
        assert 'wash_trading_analysis' in result
        assert 'mint_anomaly_analysis' in result
        assert 'security_score' in result
        assert 0 <= result['security_score'] <= 100
