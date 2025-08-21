"""
Provenance Verification Module

This module provides functionality to track and verify the provenance (ownership history)
of NFTs, detect suspicious transfers, and validate the chain of custody.
"""
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import hashlib
from collections import defaultdict, deque
import networkx as nx

# Import utility modules
from utils.graph_entropy import compute_wallet_graph_entropy

# Create a wrapper class to match the expected interface
class GraphEntropyAnalyzer:
    def __init__(self):
        self.entropy_cache = {}
    
    def analyze_graph(self, df, wallet_col="wallet", token_col="token_id"):
        """Analyze the graph and return entropy and other metrics."""
        return compute_wallet_graph_entropy(
            df, 
            wallet_col=wallet_col, 
            token_col=token_col,
            return_full_analysis=True
        )

logger = logging.getLogger(__name__)

@dataclass
class Transfer:
    """Represents a single transfer of an NFT."""
    tx_hash: str
    from_address: str
    to_address: str
    token_id: str
    timestamp: datetime
    value: Optional[float] = None  # In ETH or other native token
    gas_price: Optional[float] = None
    gas_used: Optional[int] = None
    block_number: Optional[int] = None
    log_index: Optional[int] = None
    
    def __hash__(self):
        return hash((self.tx_hash, self.token_id, self.log_index))

@dataclass
class TokenProvenance:
    """Tracks the complete provenance of a single token."""
    token_id: str
    contract_address: str
    creation_tx: Optional[str] = None
    creation_block: Optional[int] = None
    creator: Optional[str] = None
    transfers: List[Transfer] = field(default_factory=list)
    current_owner: Optional[str] = None
    
    def add_transfer(self, transfer: Transfer) -> None:
        """Add a transfer to the provenance record."""
        self.transfers.append(transfer)
        self.current_owner = transfer.to_address
        
        # If this is the first transfer, consider the 'from' as the creator
        if len(self.transfers) == 1 and not self.creator:
            self.creator = transfer.from_address
            self.creation_tx = transfer.tx_hash
    
    def get_ownership_history(self) -> List[Dict]:
        """Get a formatted history of ownership."""
        return [
            {
                'from': t.from_address,
                'to': t.to_address,
                'tx_hash': t.tx_hash,
                'timestamp': t.timestamp.isoformat(),
                'block_number': t.block_number,
                'value': t.value
            }
            for t in sorted(self.transfers, key=lambda x: x.timestamp)
        ]
    
    def get_owners_chronological(self) -> List[str]:
        """Get list of all owners in chronological order."""
        if not self.transfers:
            return []
            
        owners = [self.transfers[0].from_address]
        for t in self.transfers:
            owners.append(t.to_address)
        return owners

class ProvenanceVerifier:
    """Verifies and analyzes NFT provenance data."""
    
    def __init__(self):
        self.graph_analyzer = GraphEntropyAnalyzer()
        self.token_provenance: Dict[str, TokenProvenance] = {}
        self.address_aliases: Dict[str, Set[str]] = defaultdict(set)
    
    def add_transfer(self, transfer: Transfer, contract_address: str) -> None:
        """
        Add a transfer to the provenance system.
        
        Args:
            transfer: The transfer to add
            contract_address: The contract address of the NFT collection
        """
        token_key = f"{contract_address.lower()}_{transfer.token_id}"
        
        if token_key not in self.token_provenance:
            self.token_provenance[token_key] = TokenProvenance(
                token_id=transfer.token_id,
                contract_address=contract_address,
                creation_tx=transfer.tx_hash,
                creation_block=transfer.block_number,
                creator=transfer.from_address,
                current_owner=transfer.to_address
            )
        
        self.token_provenance[token_key].add_transfer(transfer)
    
    def verify_provenance(self, token_id: str, contract_address: str) -> Dict:
        """
        Verify the provenance of a specific token.
        
        Args:
            token_id: The token ID to verify
            contract_address: The contract address of the NFT collection
            
        Returns:
            Dict containing verification results and risk analysis
        """
        token_key = f"{contract_address.lower()}_{token_id}"
        if token_key not in self.token_provenance:
            return {
                'status': 'not_found',
                'message': 'No provenance data available for this token'
            }
        
        provenance = self.token_provenance[token_key]
        risk_factors = []
        
        # Check for suspicious patterns
        if self._detect_wash_trading(provenance):
            risk_factors.append({
                'type': 'wash_trading',
                'severity': 'high',
                'description': 'Potential wash trading detected in token history'
            })
        
        if self._detect_rapid_ownership_change(provenance):
            risk_factors.append({
                'type': 'rapid_ownership_change',
                'severity': 'medium',
                'description': 'Rapid changes in ownership detected'
            })
        
        if self._detect_blacklisted_address(provenance):
            risk_factors.append({
                'type': 'blacklisted_address',
                'severity': 'critical',
                'description': 'Token has been associated with blacklisted addresses'
            })
        
        # Calculate graph entropy for the token's transfer graph
        transfer_graph = self._build_transfer_graph(provenance)
        entropy_analysis = self.graph_analyzer.analyze(transfer_graph)
        
        # Check address symmetry
        symmetry_analysis = self._analyze_address_symmetry(provenance)
        
        # Calculate overall risk score (0-100)
        risk_score = min(100, len(risk_factors) * 20 + 
                        (10 if entropy_analysis.get('is_suspicious', False) else 0) +
                        (15 if symmetry_analysis.get('is_suspicious', False) else 0))
        
        return {
            'token_id': token_id,
            'contract_address': contract_address,
            'current_owner': provenance.current_owner,
            'creator': provenance.creator,
            'total_transfers': len(provenance.transfers),
            'ownership_history': provenance.get_ownership_history(),
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'entropy_analysis': entropy_analysis,
            'symmetry_analysis': symmetry_analysis,
            'verification_status': 'verified' if risk_score < 30 else 'suspicious',
            'last_verified': datetime.utcnow().isoformat()
        }
    
    def _build_transfer_graph(self, provenance: TokenProvenance) -> nx.DiGraph:
        """Build a directed graph of transfers for a token."""
        G = nx.DiGraph()
        
        for transfer in provenance.transfers:
            if not G.has_node(transfer.from_address):
                G.add_node(transfer.from_address, type='wallet')
            if not G.has_node(transfer.to_address):
                G.add_node(transfer.to_address, type='wallet')
            
            G.add_edge(
                transfer.from_address,
                transfer.to_address,
                tx_hash=transfer.tx_hash,
                timestamp=transfer.timestamp,
                value=transfer.value,
                token_id=provenance.token_id
            )
        
        return G
    
    def _analyze_address_symmetry(self, provenance: TokenProvenance) -> Dict:
        """Analyze address symmetry patterns in the token's history."""
        addresses = set()
        for transfer in provenance.transfers:
            addresses.add(transfer.from_address)
            addresses.add(transfer.to_address)
        
        symmetry_scores = []
        for addr in addresses:
            score = self.symmetry_analyzer.analyze(addr)
            symmetry_scores.append({
                'address': addr,
                'symmetry_score': score,
                'is_suspicious': score > 0.8  # High symmetry might indicate generated address
            })
        
        return {
            'symmetry_scores': symmetry_scores,
            'avg_symmetry': sum(s['symmetry_score'] for s in symmetry_scores) / len(symmetry_scores) if symmetry_scores else 0,
            'is_suspicious': any(s['is_suspicious'] for s in symmetry_scores)
        }
    
    def _detect_wash_trading(self, provenance: TokenProvenance) -> bool:
        """Detect potential wash trading patterns."""
        if len(provenance.transfers) < 3:
            return False
        
        # Look for circular trading patterns (A -> B -> A)
        for i in range(len(provenance.transfers) - 1):
            t1 = provenance.transfers[i]
            t2 = provenance.transfers[i + 1]
            
            if (t1.from_address == t2.to_address and 
                t1.to_address == t2.from_address):
                # Check if these transfers happened close in time
                time_diff = (t2.timestamp - t1.timestamp).total_seconds()
                if time_diff < 3600:  # Within 1 hour
                    return True
        
        return False
    
    def _detect_rapid_ownership_change(self, provenance: TokenProvenance, 
                                     max_transfers: int = 5, 
                                     time_window_hours: int = 24) -> bool:
        """Detect rapid changes in ownership."""
        if len(provenance.transfers) < max_transfers:
            return False
        
        # Check the most recent transfers
        recent_transfers = sorted(
            provenance.transfers, 
            key=lambda x: x.timestamp, 
            reverse=True
        )[:max_transfers]
        
        if not recent_transfers:
            return False
            
        # Check if all transfers happened within the time window
        time_diff = (recent_transfers[0].timestamp - 
                    recent_transfers[-1].timestamp).total_seconds()
        
        return time_diff < time_window_hours * 3600
    
    def _detect_blacklisted_address(self, provenance: TokenProvenance) -> bool:
        """Check if any address in the provenance is blacklisted."""
        # In a real implementation, this would check against a database or API
        # of known malicious addresses
        blacklisted = set()  # This would be populated from a real data source
        
        for transfer in provenance.transfers:
            if (transfer.from_address in blacklisted or 
                transfer.to_address in blacklisted):
                return True
        
        return False
    
    def get_token_provenance(self, token_id: str, contract_address: str) -> Optional[TokenProvenance]:
        """Get the provenance record for a specific token."""
        token_key = f"{contract_address.lower()}_{token_id}"
        return self.token_provenance.get(token_key)
    
    def get_tokens_by_owner(self, owner_address: str) -> List[Dict]:
        """Get all tokens currently owned by an address."""
        result = []
        for token_key, provenance in self.token_provenance.items():
            if provenance.current_owner.lower() == owner_address.lower():
                result.append({
                    'token_id': provenance.token_id,
                    'contract_address': provenance.contract_address,
                    'transfers': len(provenance.transfers),
                    'first_seen': min(t.timestamp for t in provenance.transfers).isoformat() if provenance.transfers else None,
                    'last_transfer': max(t.timestamp for t in provenance.transfers).isoformat() if provenance.transfers else None
                })
        return result
    
    def get_ownership_timeline(self, token_id: str, contract_address: str) -> List[Dict]:
        """Get a timeline of ownership for a token."""
        token_key = f"{contract_address.lower()}_{token_id}"
        if token_key not in self.token_provenance:
            return []
            
        timeline = []
        provenance = self.token_provenance[token_key]
        
        if not provenance.transfers:
            return timeline
        
        # Sort transfers by timestamp
        sorted_transfers = sorted(provenance.transfers, key=lambda x: x.timestamp)
        
        # Add initial owner (minter/creator)
        timeline.append({
            'owner': sorted_transfers[0].from_address,
            'start_time': sorted_transfers[0].timestamp.isoformat(),
            'end_time': sorted_transfers[0].timestamp.isoformat(),
            'duration_seconds': 0,
            'transfer_in': None,
            'transfer_out': sorted_transfers[0].tx_hash
        })
        
        # Add each transfer
        for i in range(1, len(sorted_transfers)):
            prev_tx = sorted_transfers[i-1]
            current_tx = sorted_transfers[i]
            
            # Update end time of previous owner
            if timeline:
                timeline[-1]['end_time'] = current_tx.timestamp.isoformat()
                timeline[-1]['duration_seconds'] = (
                    current_tx.timestamp - prev_tx.timestamp
                ).total_seconds()
            
            # Add current owner
            timeline.append({
                'owner': current_tx.to_address,
                'start_time': current_tx.timestamp.isoformat(),
                'end_time': datetime.utcnow().isoformat(),  # Current time for last owner
                'duration_seconds': (
                    datetime.utcnow() - current_tx.timestamp
                ).total_seconds(),
                'transfer_in': current_tx.tx_hash,
                'transfer_out': None
            })
        
        return timeline


class ProvenanceTracker(ProvenanceVerifier):
    """
    Alias for ProvenanceVerifier to maintain backward compatibility.
    
    This class is being phased out in favor of ProvenanceVerifier.
    All functionality is inherited from ProvenanceVerifier.
    """
    def __init__(self):
        super().__init__()
        import warnings
        warnings.warn(
            "ProvenanceTracker is deprecated and will be removed in a future version. "
            "Use ProvenanceVerifier instead.",
            DeprecationWarning,
            stacklevel=2
        )
