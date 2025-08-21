"""
SimHash (Similarity Hash) Implementation

This module provides an efficient implementation of the SimHash algorithm, which is used
to generate fingerprints for documents that can be compared to estimate their similarity.
SimHash is particularly useful for near-duplicate detection and clustering of text documents.

Example usage:
    >>> text1 = "This is a test document about blockchain technology"
    >>> text2 = "This is another document discussing blockchain and crypto"
    >>> hash1 = simhash(text1)
    >>> hash2 = simhash(text2)
    >>> distance = simhash_distance(hash1, hash2)
    >>> similarity = 1 - (distance / 64.0)  # For 64-bit hashes
"""

import hashlib
import numpy as np
from typing import List, Dict, Set, Tuple, Optional, Union, Callable
from dataclasses import dataclass
from functools import lru_cache
import mmh3  # MurmurHash3 for faster hashing

# Type aliases
HashBits = int
Token = str
HashFunction = Callable[[bytes], int]

@dataclass
class SimHashConfig:
    """Configuration for SimHash generation."""
    hash_bits: int = 64                # Number of bits in the hash (64 or 128)
    tokenizer: Callable[[str], List[Token]] = str.split  # Function to split text into tokens
    hash_func: HashFunction = lambda x: mmh3.hash_bytes(x).hex()  # Default hash function
    weighted: bool = True              # Whether to use token weights
    token_weights: Optional[Dict[Token, float]] = None  # Custom token weights
    normalize: bool = True             # Whether to normalize token weights

class SimHasher:
    """
    A configurable SimHash implementation with support for different tokenization
    strategies, hash functions, and weighting schemes.
    
    Args:
        config: Configuration object for SimHash generation
    """
    
    def __init__(self, config: Optional[SimHashConfig] = None):
        self.config = config or SimHashConfig()
        self._validate_config()
    
    def _validate_config(self):
        """Validate the configuration parameters."""
        if self.config.hash_bits not in (64, 128):
            raise ValueError("hash_bits must be either 64 or 128")
    
    def _compute_token_hash(self, token: str) -> int:
        """Compute the hash of a token using the configured hash function."""
        # Use MurmurHash3 for better performance than MD5
        return mmh3.hash(token, signed=False)
    
    def _get_token_weight(self, token: str) -> float:
        """Get the weight for a token."""
        if not self.config.weighted:
            return 1.0
            
        if self.config.token_weights and token in self.config.token_weights:
            return self.config.token_weights[token]
            
        # Default weight based on token frequency (inverse document frequency)
        # In a real implementation, you might want to pre-compute IDF scores
        return 1.0
    
    def _tokenize(self, text: str) -> List[Tuple[str, float]]:
        """Tokenize the input text and return (token, weight) pairs."""
        if not text:
            return []
            
        tokens = self.config.tokenizer(text)
        if not self.config.weighted:
            return [(t, 1.0) for t in tokens]
            
        # Calculate token frequencies for TF-IDF like weighting
        token_counts = {}
        for token in tokens:
            token_counts[token] = token_counts.get(token, 0) + 1
        
        # Apply custom weights if available, otherwise use TF-IDF like weights
        max_count = max(token_counts.values()) if token_counts else 1
        weighted_tokens = []
        
        for token, count in token_counts.items():
            if self.config.token_weights and token in self.config.token_weights:
                weight = self.config.token_weights[token]
            else:
                # Simple TF-IDF like weighting
                weight = 0.5 + 0.5 * (count / max_count)
            weighted_tokens.append((token, weight))
        
        return weighted_tokens
    
    def simhash(self, text: str) -> int:
        """
        Generate a SimHash fingerprint for the input text.
        
        Args:
            text: Input text to hash
            
        Returns:
            Integer representing the SimHash fingerprint
        """
        if not text:
            return 0
            
        # Initialize vector to 0 with size equal to hash bits
        vector = [0.0] * self.config.hash_bits
        
        # Tokenize and process each token
        for token, weight in self._tokenize(text):
            # Get token hash
            h = self._compute_token_hash(token)
            
            # Update vector based on token hash bits
            for i in range(self.config.hash_bits):
                bitmask = 1 << i
                vector[i] += weight if (h & bitmask) else -weight
        
        # Generate fingerprint from vector
        fingerprint = 0
        for i in range(self.config.hash_bits):
            if vector[i] > 0:
                fingerprint |= 1 << i
                
        return fingerprint
    
    @classmethod
    def simhash_distance(cls, hash1: int, hash2: int, hash_bits: int = 64) -> int:
        """
        Calculate the Hamming distance between two SimHash values.
        
        Args:
            hash1: First SimHash value
            hash2: Second SimHash value
            hash_bits: Number of bits in the hash (must match the hash length)
            
        Returns:
            Hamming distance (number of differing bits)
        """
        # XOR the two hashes and count the number of set bits
        x = hash1 ^ hash2
        return bin(x).count('1')
    
    @classmethod
    def similarity(cls, hash1: int, hash2: int, hash_bits: int = 64) -> float:
        """
        Calculate the similarity between two SimHash values.
        
        Args:
            hash1: First SimHash value
            hash2: Second SimHash value
            hash_bits: Number of bits in the hash (must match the hash length)
            
        Returns:
            Similarity score between 0.0 (completely different) and 1.0 (identical)
        """
        distance = cls.simhash_distance(hash1, hash2, hash_bits)
        return 1.0 - (distance / hash_bits)

# Default instance with standard configuration
default_hasher = SimHasher()

# Convenience functions that use the default hasher
def simhash(text: str, hash_bits: int = 64) -> int:
    """
    Generate a SimHash fingerprint for the input text using default settings.
    
    Args:
        text: Input text to hash
        hash_bits: Number of bits in the hash (64 or 128)
        
    Returns:
        Integer representing the SimHash fingerprint
    """
    if hash_bits not in (64, 128):
        raise ValueError("hash_bits must be either 64 or 128")
    config = SimHashConfig(hash_bits=hash_bits)
    return SimHasher(config).simhash(text)

def simhash_distance(hash1: int, hash2: int, hash_bits: int = 64) -> int:
    """
    Calculate the Hamming distance between two SimHash values.
    
    Args:
        hash1: First SimHash value
        hash2: Second SimHash value
        hash_bits: Number of bits in the hash (must match the hash length)
        
    Returns:
        Hamming distance (number of differing bits)
    """
    return SimHasher.simhash_distance(hash1, hash2, hash_bits)

def similarity(hash1: int, hash2: int, hash_bits: int = 64) -> float:
    """
    Calculate the similarity between two SimHash values.
    
    Args:
        hash1: First SimHash value
        hash2: Second SimHash value
        hash_bits: Number of bits in the hash (must match the hash length)
        
    Returns:
        Similarity score between 0.0 (completely different) and 1.0 (identical)
    """
    return SimHasher.similarity(hash1, hash2, hash_bits)

# Example usage
if __name__ == "__main__":
    # Example 1: Basic usage
    text1 = "The quick brown fox jumps over the lazy dog"
    text2 = "A quick brown fox jumps over the lazy dog"
    
    hash1 = simhash(text1)
    hash2 = simhash(text2)
    
    print(f"Text 1 hash: {hash1:016x}")
    print(f"Text 2 hash: {hash2:016x}")
    print(f"Hamming distance: {simhash_distance(hash1, hash2)}")
    print(f"Similarity: {similarity(hash1, hash2):.2f}")
    
    # Example 2: Using the SimHasher class directly with custom configuration
    config = SimHashConfig(
        hash_bits=128,
        tokenizer=lambda x: x.split(),  # Simple whitespace tokenizer
        weighted=True
    )
    
    hasher = SimHasher(config)
    hash3 = hasher.simhash(text1)
    hash4 = hasher.simhash(text2)
    
    print(f"\nWith custom config (128-bit hashes):")
    print(f"Text 1 hash: {hash3:032x}")
    print(f"Text 2 hash: {hash4:032x}")
    print(f"Hamming distance: {hasher.simhash_distance(hash3, hash4, 128)}")
    print(f"Similarity: {hasher.similarity(hash3, hash4, 128):.2f}")
