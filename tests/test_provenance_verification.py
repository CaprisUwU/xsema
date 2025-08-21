"""
Integration tests for NFT provenance verification.

These tests verify that the provenance verification system correctly tracks
NFT ownership history and detects suspicious patterns.
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import numpy as np

# Import the modules to test
from core.security.provenance import ProvenanceVerifier, Transfer, TokenProvenance

# Sample test data
SAMPLE_TRANSFERS = [
    {
        'tx_hash': '0x1111111111111111111111111111111111111111111111111111111111111111',
        'from': '0x1111111111111111111111111111111111111111',
        'to': '0x2222222222222222222222222222222222222222',
        'token_id': '1',
        'timestamp': datetime.now(timezone.utc) - timedelta(days=30),
        'value': 1.0,
        'gas_price': 2000000000,
        'gas_used': 21000,
        'block_number': 10000000,
        'log_index': 0
    },
    {
        'tx_hash': '0x2222222222222222222222222222222222222222222222222222222222222222',
        'from': '0x2222222222222222222222222222222222222222',
        'to': '0x3333333333333333333333333333333333333333',
        'token_id': '1',
        'timestamp': datetime.now(timezone.utc) - timedelta(days=20),
        'value': 1.5,
        'gas_price': 2100000000,
        'gas_used': 21000,
        'block_number': 10001000,
        'log_index': 0
    },
    {
        'tx_hash': '0x3333333333333333333333333333333333333333333333333333333333333333',
        'from': '0x3333333333333333333333333333333333333333',
        'to': '0x2222222222222222222222222222222222222222',
        'token_id': '1',
        'timestamp': datetime.now(timezone.utc) - timedelta(days=10),
        'value': 1.2,
        'gas_price': 2000000000,
        'gas_used': 21000,
        'block_number': 10002000,
        'log_index': 0
    },
    {
        'tx_hash': '0x4444444444444444444444444444444444444444444444444444444444444444',
        'from': '0x2222222222222222222222222222222222222222',
        'to': '0x4444444444444444444444444444444444444444',
        'token_id': '1',
        'timestamp': datetime.now(timezone.utc),
        'value': 2.0,
        'gas_price': 2200000000,
        'gas_used': 21000,
        'block_number': 10003000,
        'log_index': 0
    }
]

class TestProvenanceVerifier:
    """Test cases for ProvenanceVerifier class."""
    
    @pytest.fixture
    def verifier(self):
        """Create a ProvenanceVerifier instance for testing."""
        return ProvenanceVerifier()
    
    def test_add_transfer(self, verifier):
        """Test adding transfers to the provenance system."""
        contract_address = '0x1234567890123456789012345678901234567890'
        
        # Add transfers
        for tx in SAMPLE_TRANSFERS:
            transfer = Transfer(**tx)
            verifier.add_transfer(transfer, contract_address)
        
        # Verify the token provenance was created
        token_key = f"{contract_address.lower()}_1"
        assert token_key in verifier.token_provenance
        
        provenance = verifier.token_provenance[token_key]
        assert len(provenance.transfers) == 4
        assert provenance.current_owner == '0x4444444444444444444444444444444444444444'
        assert provenance.creator == '0x1111111111111111111111111111111111111111'
    
    def test_verify_provenance(self, verifier):
        """Test provenance verification and risk detection."""
        contract_address = '0x1234567890123456789012345678901234567890'
        
        # Add transfers
        for tx in SAMPLE_TRANSFERS:
            transfer = Transfer(**tx)
            verifier.add_transfer(transfer, contract_address)
        
        # Verify provenance
        result = verifier.verify_provenance('1', contract_address)
        
        # Check basic info
        assert result['token_id'] == '1'
        assert result['contract_address'] == contract_address
        assert result['current_owner'] == '0x4444444444444444444444444444444444444444'
        assert result['creator'] == '0x1111111111111111111111111111111111111111'
        assert result['total_transfers'] == 4
        
        # Check risk factors (should detect wash trading)
        risk_factors = result['risk_factors']
        assert any(factor['type'] == 'wash_trading' for factor in risk_factors)
        
        # Check verification status (should be suspicious due to wash trading)
        assert result['verification_status'] == 'suspicious'
    
    def test_get_ownership_timeline(self, verifier):
        """Test retrieval of ownership timeline."""
        contract_address = '0x1234567890123456789012345678901234567890'
        
        # Add transfers
        for tx in SAMPLE_TRANSFERS:
            transfer = Transfer(**tx)
            verifier.add_transfer(transfer, contract_address)
        
        # Get timeline
        timeline = verifier.get_ownership_timeline('1', contract_address)
        
        # Should have 4 entries (initial owner + 3 transfers)
        assert len(timeline) == 4
        
        # First entry should have no transfer_in
        assert timeline[0]['transfer_in'] is None
        assert timeline[0]['owner'] == '0x1111111111111111111111111111111111111111'
        
        # Last entry should have no transfer_out
        assert timeline[-1]['transfer_out'] is None
        assert timeline[-1]['owner'] == '0x4444444444444444444444444444444444444444'

class TestProvenanceIntegration:
    """Integration tests for provenance verification with real-world data."""
    
    @pytest.fixture
    def mock_web3(self):
        """Mock Web3 provider for testing."""
        with patch('web3.Web3') as mock_web3:
            # Mock eth.get_block
            mock_web3.eth.get_block.return_value = {
                'timestamp': int(datetime.now(timezone.utc).timestamp())
            }
            
            # Mock eth.get_transaction_receipt
            def mock_get_transaction_receipt(tx_hash):
                return {
                    'gasUsed': 21000,
                    'logs': [{
                        'address': '0x1234567890123456789012345678901234567890',
                        'topics': [
                            '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
                            '0x0000000000000000000000001111111111111111111111111111111111111111',
                            '0x0000000000000000000000002222222222222222222222222222222222222222',
                            '0x0000000000000000000000000000000000000000000000000000000000000001'
                        ]
                    }]
                }
            
            mock_web3.eth.get_transaction_receipt.side_effect = mock_get_transaction_receipt
            
            yield mock_web3
    
    def test_end_to_end_provenance(self, mock_web3):
        """Test end-to-end provenance verification with mock blockchain data."""
        # Set up test data
        contract_address = '0x1234567890123456789012345678901234567890'
        token_id = '1'
        
        # Initialize verifier
        verifier = ProvenanceVerifier()
        
        # Mock transaction history
        def mock_get_transfers(contract_address, token_id, **kwargs):
            return [
                {
                    'tx_hash': tx['tx_hash'],
                    'from': tx['from'],
                    'to': tx['to'],
                    'token_id': tx['token_id'],
                    'timestamp': int(tx['timestamp'].timestamp()),
                    'value': tx['value'],
                    'gas_price': tx['gas_price'],
                    'gas_used': tx['gas_used'],
                    'block_number': tx['block_number'],
                    'log_index': tx['log_index']
                }
                for tx in SAMPLE_TRANSFERS
            ]
        
        with patch('live.blockchain.get_transfer_history', side_effect=mock_get_transfers):
            # Get transfer history and add to verifier
            transfers = mock_get_transfers(contract_address, token_id)
            for tx in transfers:
                transfer = Transfer(
                    tx_hash=tx['tx_hash'],
                    from_address=tx['from'],
                    to_address=tx['to'],
                    token_id=tx['token_id'],
                    timestamp=datetime.fromtimestamp(tx['timestamp']),
                    value=tx['value'],
                    gas_price=tx['gas_price'],
                    gas_used=tx['gas_used'],
                    block_number=tx['block_number'],
                    log_index=tx['log_index']
                )
                verifier.add_transfer(transfer, contract_address)
            
            # Verify provenance
            result = verifier.verify_provenance(token_id, contract_address)
            
            # Check basic info
            assert result['token_id'] == token_id
            assert result['contract_address'] == contract_address
            assert result['current_owner'] == '0x4444444444444444444444444444444444444444'
            assert result['creator'] == '0x1111111111111111111111111111111111111111'
            assert result['total_transfers'] == 4
            
            # Check risk factors (should detect wash trading)
            assert 'risk_factors' in result
            assert len(result['risk_factors']) > 0
            
            # Get timeline
            timeline = verifier.get_ownership_timeline(token_id, contract_address)
            assert len(timeline) == 4
            
            # Verify ownership changes
            assert timeline[0]['owner'] == '0x1111111111111111111111111111111111111111'
            assert timeline[1]['owner'] == '0x2222222222222222222222222222222222222222'
            assert timeline[2]['owner'] == '0x3333333333333333333333333333333333333333'
            assert timeline[3]['owner'] == '0x4444444444444444444444444444444444444444'
