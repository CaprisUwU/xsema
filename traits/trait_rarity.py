"""
Trait Rarity and Analysis Module

This module provides functionality for calculating and analyzing NFT trait rarity,
symmetry features, and other metadata-based metrics.
"""

from typing import Dict, List, Optional, TypedDict, Union
from dataclasses import dataclass
import math
import statistics
from functools import lru_cache

from utils.address_symmetry import address_symmetry_features, hamming_distance

# Type aliases
TraitValue = Union[str, int, float, bool]
TraitCounts = Dict[str, Dict[TraitValue, int]]
TraitWeights = Dict[str, float]
TokenTraits = Dict[str, TraitValue]

class RarityScores(TypedDict):
    """Container for different rarity score types."""
    trait_rarity: float
    statistical_rarity: float
    normalized_rarity: float
    weighted_rarity: float

@dataclass
class TraitAnalysis:
    """Comprehensive trait analysis for an NFT."""
    token_id: str
    traits: TokenTraits
    scores: RarityScores
    trait_rarities: Dict[str, float]
    symmetry_features: Dict[str, float]

# Default weights for different trait categories (can be overridden)
DEFAULT_TRAIT_WEIGHTS = {
    'background': 1.0,
    'body': 1.2,
    'clothing': 1.1,
    'accessory': 1.3,
    'head': 1.4,
    'eyes': 1.2,
    'mouth': 1.1,
    'special': 1.5
}

def trait_rarity_score(
    token_traits: TokenTraits,
    collection_trait_counts: TraitCounts,
    total_tokens: int,
    weights: Optional[TraitWeights] = None,
    normalize: bool = True
) -> Dict[str, float]:
    """
    Compute multiple rarity scores for a token based on its traits.
    
    Args:
        token_traits: Dictionary of trait_type -> value for this token
        collection_trait_counts: Dictionary of trait_type -> {value: count}
        total_tokens: Total number of tokens in the collection
        weights: Optional dictionary of trait_type -> weight
        normalize: Whether to normalize scores between 0 and 1
        
    Returns:
        Dictionary containing different rarity scores
    """
    if not token_traits or not collection_trait_counts or total_tokens <= 0:
        raise ValueError("Invalid input parameters")
        
    weights = weights or {}
    trait_rarities = {}
    statistical_rarity = 1.0
    weighted_rarity = 0.0
    total_weight = 0.0
    
    for trait_type, value in token_traits.items():
        if trait_type not in collection_trait_counts:
            continue
            
        count = collection_trait_counts[trait_type].get(value, 1)
        rarity = (total_tokens - count + 1) / total_tokens  # Normalized between 0 and 1
        trait_rarities[trait_type] = rarity
        
        # Statistical rarity (product of inverse frequencies)
        statistical_rarity *= (1 / count) if count > 0 else 1
        
        # Weighted rarity
        weight = weights.get(trait_type, 1.0)
        weighted_rarity += rarity * weight
        total_weight += weight
    
    # Calculate final scores
    trait_rarity = math.prod(trait_rarities.values()) ** (1/len(trait_rarities)) if trait_rarities else 0
    weighted_rarity = weighted_rarity / total_weight if total_weight > 0 else 0
    
    # Normalize statistical rarity
    if statistical_rarity > 0:
        statistical_rarity = 1 / (1 + math.log(statistical_rarity))
    
    return {
        'trait_rarity': trait_rarity,
        'statistical_rarity': statistical_rarity,
        'weighted_rarity': weighted_rarity,
        'normalized_rarity': (trait_rarity + statistical_rarity + weighted_rarity) / 3
    }

@lru_cache(maxsize=1024)
def trait_symmetry_score(
    token_address: str,
    reference_address: Optional[str] = None
) -> Dict[str, float]:
    """
    Compute symmetry features for a token address against a reference address.
    
    Args:
        token_address: The address of the token
        reference_address: The address to compare against (default is zero address)
        
    Returns:
        Dictionary containing symmetry features
    """
    if not token_address or not token_address.startswith('0x'):
        raise ValueError("Invalid token address")
        
    reference_address = reference_address or ("0x" + "0" * 40)
    
    try:
        return address_symmetry_features(token_address, reference_address)
    except Exception as e:
        # Return default values on error
        return {
            'is_palindrome': 0.0,
            'hamming_distance': 0.0,
            'symmetry_score': 0.0
        }

def analyze_token_traits(
    token_id: str,
    token_traits: TokenTraits,
    collection_trait_counts: TraitCounts,
    total_tokens: int,
    weights: Optional[TraitWeights] = None,
    reference_address: Optional[str] = None
) -> TraitAnalysis:
    """
    Perform comprehensive trait analysis for a token.
    
    Args:
        token_id: Unique identifier for the token
        token_traits: Dictionary of trait_type -> value
        collection_trait_counts: Dictionary of trait_type -> {value: count}
        total_tokens: Total number of tokens in the collection
        weights: Optional dictionary of trait weights
        reference_address: Optional reference address for symmetry analysis
        
    Returns:
        TraitAnalysis object with comprehensive trait information
    """
    if not token_traits or not collection_trait_counts or total_tokens <= 0:
        raise ValueError("Invalid input parameters")
    
    # Calculate rarity scores
    scores = trait_rarity_score(token_traits, collection_trait_counts, total_tokens, weights)
    
    # Calculate trait rarities
    trait_rarities = {}
    for trait_type, value in token_traits.items():
        if trait_type not in collection_trait_counts:
            continue
        count = collection_trait_counts[trait_type].get(value, 1)
        trait_rarities[trait_type] = (total_tokens - count + 1) / total_tokens
    
    # Calculate symmetry features using token ID as address if not provided
    token_address = f"0x{token_id.zfill(40)}"
    symmetry_features = trait_symmetry_score(token_address, reference_address)
    
    return TraitAnalysis(
        token_id=token_id,
        traits=token_traits,
        scores=scores,
        trait_rarities=trait_rarities,
        symmetry_features=symmetry_features
    )

def get_trait_statistics(collection_trait_counts: TraitCounts) -> Dict[str, Dict[str, float]]:
    """
    Calculate statistics for each trait in the collection.
    
    Args:
        collection_trait_counts: Dictionary of trait_type -> {value: count}
        
    Returns:
        Dictionary of trait statistics
    """
    stats = {}
    
    for trait_type, value_counts in collection_trait_counts.items():
        if not value_counts:
            continue
            
        counts = list(value_counts.values())
        total = sum(counts)
        
        stats[trait_type] = {
            'unique_values': len(counts),
            'min_count': min(counts),
            'max_count': max(counts),
            'avg_count': statistics.mean(counts),
            'median_count': statistics.median(counts),
            'std_dev': statistics.stdev(counts) if len(counts) > 1 else 0,
            'entropy': -sum((c/total) * math.log2(c/total) for c in counts if c > 0)
        }
    
    return stats