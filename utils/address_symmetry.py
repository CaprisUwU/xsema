"""
Address Symmetry Analysis Module

This module provides functions to analyze patterns and symmetries in Ethereum addresses.
It's useful for identifying vanity addresses, potential scams, or interesting patterns.
"""
from typing import Dict, Tuple
from functools import lru_cache
import re

# Pre-compile regex for common patterns
REPEATED_PATTERN = re.compile(r'(\w{2,}?)\1+')
HEX_PAIRS = re.compile(r'([0-9a-f])\1')

def is_palindrome(s: str) -> bool:
    """
    Check if a string is a palindrome (reads the same forwards and backwards).
    
    Args:
        s: Input string to check
        
    Returns:
        bool: True if palindrome, False otherwise
    """
    return s == s[::-1]

@lru_cache(maxsize=1024)
def hamming_distance(a: str, b: str) -> int:
    """
    Calculate the Hamming distance between two strings of equal length.
    Cached for performance with common inputs.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        int: Number of positions where the strings differ
        
    Raises:
        ValueError: If strings are of different lengths
    """
    if len(a) != len(b):
        raise ValueError("Strings must be of equal length")
    return sum(c1 != c2 for c1, c2 in zip(a, b))

def get_repeated_patterns(s: str) -> Dict[str, int]:
    """
    Find all repeated patterns in a string.
    
    Args:
        s: Input string to analyze
        
    Returns:
        dict: Dictionary of patterns and their counts
    """
    return {match.group(1): len(match.group(0))//len(match.group(1)) 
            for match in REPEATED_PATTERN.finditer(s)}

def address_symmetry_features(address: str, 
                            reference: str = "0x0000000000000000000000000000000000000000") -> Dict[str, float]:
    """
    Calculate various symmetry and pattern features for an Ethereum address.
    
    Args:
        address: Ethereum address to analyze (with or without 0x prefix)
        reference: Reference address for comparison (default: zero address)
        
    Returns:
        dict: Dictionary containing symmetry features:
            - is_palindrome: 1 if address is a palindrome, 0 otherwise
            - hamming_to_zero: Hamming distance to the zero address
            - repeated_pairs: Number of repeated character pairs (e.g., 'aa', 'bb')
            - pattern_score: Score based on repeated patterns (higher = more patterns)
            - symmetry_score: Normalized score (0-1) of overall address symmetry
    """
    # Normalize addresses
    addr = address.lower().replace("0x", "")
    ref = reference.lower().replace("0x", "")
    
    # Basic features
    palindrome = int(is_palindrome(addr))
    hamming = hamming_distance(addr, ref)
    
    # Pattern analysis
    repeated_pairs = len(HEX_PAIRS.findall(addr))
    patterns = get_repeated_patterns(addr)
    pattern_score = sum(count * len(pat) for pat, count in patterns.items())
    
    # Calculate symmetry score (0-1)
    max_hamming = len(addr)  # Maximum possible hamming distance
    symmetry = 1 - (hamming / max_hamming) if max_hamming > 0 else 0
    
    return {
        "is_palindrome": palindrome,
        "hamming_to_zero": hamming,
        "repeated_pairs": repeated_pairs,
        "pattern_score": pattern_score,
        "symmetry_score": round(symmetry, 4)
    }

def check_address_symmetry(address: str) -> dict:
    """
    Simplified interface to check address symmetry patterns.
    
    This is a compatibility wrapper around address_symmetry_features that returns
    a simplified result suitable for the security analyzer.
    
    Args:
        address: Ethereum address to analyze (with or without 0x prefix)
        
    Returns:
        dict: Simplified symmetry analysis with boolean flags for common patterns
    """
    # Get detailed symmetry features
    features = address_symmetry_features(address)
    
    # Return a simplified result with boolean flags
    return {
        'is_palindrome': features['is_palindrome'] == 1,
        'has_repeated_pairs': features['repeated_pairs'] > 0,
        'has_patterns': features['pattern_score'] > 0.5,  # Arbitrary threshold
        'symmetry_score': features['symmetry_score']
    }

# Example usage
if __name__ == "__main__":
    test_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    features = address_symmetry_features(test_address)
    print(f"Analysis for {test_address}:")
    for k, v in features.items():
        print(f"{k}: {v}")