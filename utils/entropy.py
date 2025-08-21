"""
Entropy and Numerical Analysis Module

This module provides functions to analyze randomness, patterns, and numerical properties
in strings and numbers. Particularly useful for analyzing token IDs, traits, and other
categorical data in the NFT space.
"""
from typing import Dict, List, Union, Tuple
from collections import Counter, defaultdict
import math
import numpy as np
from functools import lru_cache

# Pre-compute small primes for factorization
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

def entropy(data: Union[str, List], normalize: bool = False) -> float:
    """
    Calculate the Shannon entropy of a string or list.
    
    Args:
        data: Input string or list of items
        normalize: If True, normalize the result to [0,1] by dividing by log2(alphabet_size)
        
    Returns:
        float: Shannon entropy in bits
        
    Example:
        >>> entropy("hello")
        2.321928094887362
        >>> entropy([1,2,2,3,3,3], normalize=True)
        0.9182958340544896
    """
    if not data:
        return 0.0
        
    counts = Counter(data)
    total = len(data)
    alphabet_size = len(counts)
    
    if total == 0 or alphabet_size <= 1:
        return 0.0
    
    # Calculate entropy
    entropy_val = -sum((count / total) * math.log2(count / total) 
                      for count in counts.values())
    
    # Normalize if requested (divide by log2 of alphabet size)
    if normalize:
        entropy_val /= math.log2(alphabet_size) if alphabet_size > 1 else 1
    
    return entropy_val

@lru_cache(maxsize=1024)
def digit_root(n: int) -> int:
    """
    Calculate the digital root of a non-negative integer.
    This is the recursive sum of all digits until a single digit is obtained.
    
    Args:
        n: Non-negative integer
        
    Returns:
        int: Digital root (1-9)
        
    Example:
        >>> digit_root(942)
        6  # 9 + 4 + 2 = 15 → 1 + 5 = 6
    """
    if n < 0:
        raise ValueError("Input must be non-negative")
    return n if n < 10 else digit_root(sum(int(d) for d in str(n)))

def prime_factors(n: int) -> Dict[int, int]:
    """
    Factorize a number into its prime factors with multiplicities.
    
    Args:
        n: Integer to factorize (must be > 1)
        
    Returns:
        dict: {prime: exponent} mapping
        
    Example:
        >>> prime_factors(84)
        {2: 2, 3: 1, 7: 1}  # 84 = 2² × 3¹ × 7¹
    """
    if n < 2:
        return {}
        
    factors = {}
    
    # Check small primes first
    for p in SMALL_PRIMES:
        if p * p > n:
            break
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
    
    # Check remaining odd numbers up to sqrt(n)
    d = 101  # Continue from next prime after our precomputed ones
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 2
    
    if n > 1:
        factors[n] = 1
    
    return factors

def prime_factor_count(n: int) -> int:
    """
    Count the total number of prime factors with multiplicity.
    
    Args:
        n: Integer to analyze
        
    Returns:
        int: Total count of prime factors
        
    Example:
        >>> prime_factor_count(84)  # 2×2×3×7
        4
    """
    if n < 2:
        return 0
    return sum(prime_factors(n).values())

def unique_prime_factors(n: int) -> int:
    """Count the number of unique prime factors."""
    if n < 2:
        return 0
    return len(prime_factors(n))

def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    return prime_factors(n) == {n: 1}

def analyze_numerical_patterns(numbers: List[int]) -> Dict[str, float]:
    """
    Analyze numerical patterns in a list of integers.
    
    Returns:
        dict: Dictionary containing various numerical pattern metrics
    """
    if not numbers:
        return {}
        
    diffs = [y - x for x, y in zip(numbers, numbers[1:])]
    ratios = [y/x for x, y in zip(numbers, numbers[1:]) if x != 0]
    
    return {
        'entropy': entropy(numbers, normalize=True),
        'digit_root_entropy': entropy([digit_root(n) for n in numbers], normalize=True),
        'prime_factor_entropy': entropy([prime_factor_count(n) for n in numbers], normalize=True),
        'mean_diff': np.mean(diffs) if diffs else 0,
        'mean_ratio': np.mean(ratios) if ratios else 0,
        'is_arithmetic': len(set(diffs)) == 1 if diffs else False,
        'is_geometric': len(set(round(r, 6) for r in ratios)) == 1 if ratios else False
    }

def calculate_entropy(items: List[str], normalize: bool = True) -> float:
    """
    Calculate the normalized entropy of a list of items.
    
    This is a convenience wrapper around the entropy() function that's specifically
    designed to work with the wash trading detector.
    
    Args:
        items: List of strings to analyze
        normalize: If True, normalize the result to [0,1]
        
    Returns:
        float: Normalized entropy value between 0 and 1
    """
    if not items:
        return 0.0
        
    # Calculate raw entropy
    raw_entropy_value = entropy(items, normalize=False)
    
    if not normalize:
        return raw_entropy_value
        
    # Calculate maximum possible entropy for this number of items
    unique_items = set(items)
    max_entropy = math.log2(len(unique_items)) if unique_items else 0
    
    # Normalize to [0,1]
    if max_entropy == 0:
        return 0.0
        
    return min(1.0, raw_entropy_value / max_entropy)

# Example usage
if __name__ == "__main__":
    # Test entropy
    test_str = "hello world"
    print(f"Entropy of '{test_str}': {entropy(test_str):.4f} bits")
    print(f"Normalized entropy: {entropy(test_str, normalize=True):.4f}")
    
    # Test digit root
    num = 942
    print(f"Digit root of {num}: {digit_root(num)}")
    
    # Test prime factorization
    num = 84
    factors = prime_factors(num)
    print(f"Prime factors of {num}: {factors}")
    print(f"Total prime factors: {prime_factor_count(num)}")
    print(f"Unique prime factors: {unique_prime_factors(num)}")
    
    # Test numerical pattern analysis
    sequence = [2, 4, 8, 16, 32, 64]
    print(f"\nAnalysis of sequence {sequence}:")
    for k, v in analyze_numerical_patterns(sequence).items():
        print(f"{k}: {v}")