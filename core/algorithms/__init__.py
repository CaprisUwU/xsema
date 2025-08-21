"""
Core Analytics Algorithms

This module contains the fundamental algorithms that power the NFT Analytics Engine.
These are core components, not "advanced" features - they are essential for basic functionality.

Core Algorithms:
- SimHash: Similarity detection and clustering
- Entropy: Graph and statistical analysis  
- Hybrid Similarity: Advanced clustering algorithms
- Address Symmetry: Security pattern detection
- Temporal Analysis: Time-based pattern recognition
- Trait Rarity: NFT trait scoring and rarity calculation
"""

# Import algorithms from utils (will eventually be moved here)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from utils.simhash import simhash, simhash_distance
    from utils.entropy import *
    from utils.graph_entropy import compute_wallet_graph_entropy
    from utils.hybrid_similarity import *
    from utils.address_symmetry import check_address_symmetry
    from utils.temporal import *
    from utils.bitwise import *
    from utils.golden import *
    from traits.trait_rarity import trait_rarity_score, trait_symmetry_score, analyze_token_traits
except ImportError as e:
    print(f"Warning: Could not import some core algorithms: {e}")
    # Provide fallback implementations or raise

__all__ = [
    # Similarity & Clustering
    'simhash',
    'simhash_distance',
    'hybrid_similarity_score',
    
    # Entropy & Analysis  
    'calculate_entropy',
    'compute_wallet_graph_entropy',
    
    # Security & Pattern Detection
    'check_address_symmetry',
    
    # Trait Analysis
    'trait_rarity_score',
    'trait_symmetry_score',
    'analyze_token_traits',
    
    # Temporal Analysis
    'analyze_temporal_patterns',
    
    # Utility Functions
    'golden_ratio_analysis',
    'bitwise_analysis'
]
