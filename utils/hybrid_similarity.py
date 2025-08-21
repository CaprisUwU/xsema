"""
Hybrid Similarity Analysis Module

This module provides multiple approaches to measure similarity between smart contracts,
combining techniques like SimHash, AST analysis, bytecode comparison, and embeddings.
Useful for detecting contract clones, verifying authenticity, and finding similar contracts.
"""
from typing import Dict, Optional, Tuple, Union, List
import difflib
import numpy as np
from dataclasses import dataclass
from functools import lru_cache

# Local imports
from utils.simhash import simhash

@dataclass
class SimilarityResult:
    """Container for similarity analysis results."""
    simhash_distance: int           # Hamming distance (0-64 for 64-bit hash)
    ast_similarity: float           # AST-based similarity (0-1)
    bytecode_similarity: float      # Bytecode similarity (0-1)
    embedding_similarity: float     # Embedding cosine similarity (-1 to 1)
    hybrid_score: float             # Combined weighted score (0-1)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSON serialization."""
        return {
            'simhash_distance': self.simhash_distance,
            'ast_similarity': self.ast_similarity,
            'bytecode_similarity': self.bytecode_similarity,
            'embedding_similarity': self.embedding_similarity,
            'hybrid_score': self.hybrid_score
        }

class SimilarityAnalyzer:
    """
    A configurable similarity analyzer for smart contracts.
    
    Args:
        weights: Dictionary of weights for each similarity metric
        simhash_bits: Number of bits for SimHash (64 or 128)
        cache_size: Maximum number of results to cache
    """
    
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        simhash_bits: int = 64,
        cache_size: int = 1000
    ):
        self.weights = weights or {
            'simhash': 0.3,
            'ast': 0.3,
            'bytecode': 0.3,
            'embedding': 0.1
        }
        self.simhash_bits = simhash_bits
        self._simhash_fn = simhash  # Assuming simhash supports bit length
        
        # Initialize caches
        self._simhash_cache = {}
        self._ast_cache = {}
        
        # Set up LRU caches for expensive operations
        self._cached_ast_similarity = lru_cache(maxsize=cache_size)(self._ast_similarity_impl)
        self._cached_bytecode_similarity = lru_cache(maxsize=cache_size)(self._bytecode_similarity_impl)
    
    def _normalize_simhash_distance(self, distance: int) -> float:
        """Convert Hamming distance to similarity score (0-1)."""
        return 1.0 - (distance / self.simhash_bits)
    
    def _simhash_similarity(self, code1: str, code2: str) -> Tuple[int, float]:
        """
        Calculate SimHash distance and normalized similarity.
        
        Returns:
            Tuple of (hamming_distance, normalized_similarity)
        """
        # Cache SimHashes for individual codes
        if code1 not in self._simhash_cache:
            self._simhash_cache[code1] = self._simhash_fn(code1, self.simhash_bits)
        if code2 not in self._simhash_cache:
            self._simhash_cache[code2] = self._simhash_fn(code2, self.simhash_bits)
            
        h1 = self._simhash_cache[code1]
        h2 = self._simhash_cache[code2]
        
        # Calculate Hamming distance
        distance = bin(h1 ^ h2).count('1')
        return distance, self._normalize_simhash_distance(distance)
    
    def _ast_similarity_impl(self, code1: str, code2: str) -> float:
        """Internal implementation of AST similarity with basic line matching."""
        # Simple line-based similarity as fallback
        lines1 = [l.strip() for l in code1.splitlines() if l.strip()]
        lines2 = [l.strip() for l in code2.splitlines() if l.strip()]
        
        if not lines1 and not lines2:
            return 1.0  # Both empty
        if not lines1 or not lines2:
            return 0.0  # One is empty, other isn't
            
        return difflib.SequenceMatcher(None, lines1, lines2).ratio()
    
    def _bytecode_similarity_impl(self, bytecode1: str, bytecode2: str) -> float:
        """Internal implementation of bytecode similarity."""
        if not bytecode1 or not bytecode2:
            return 0.0
            
        # Simple bytecode string similarity
        return difflib.SequenceMatcher(None, bytecode1, bytecode2).ratio()
    
    def _embedding_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings."""
        if emb1 is None or emb2 is None:
            return 0.0
            
        # Ensure embeddings are numpy arrays
        emb1 = np.asarray(emb1, dtype=np.float32)
        emb2 = np.asarray(emb2, dtype=np.float32)
        
        # Calculate cosine similarity
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(np.dot(emb1, emb2) / (norm1 * norm2))
    
    def compare(
        self,
        code1: str,
        code2: str,
        bytecode1: Optional[str] = None,
        bytecode2: Optional[str] = None,
        embedding1: Optional[np.ndarray] = None,
        embedding2: Optional[np.ndarray] = None
    ) -> SimilarityResult:
        """
        Compare two smart contracts using multiple similarity metrics.
        
        Args:
            code1, code2: Source code of the contracts
            bytecode1, bytecode2: Optional compiled bytecode
            embedding1, embedding2: Optional vector embeddings of the code
            
        Returns:
            SimilarityResult with all metrics and a combined score
        """
        # Calculate all similarity metrics
        simhash_dist, simhash_sim = self._simhash_similarity(code1, code2)
        ast_sim = self._cached_ast_similarity(code1, code2)
        
        bytecode_sim = 0.0
        if bytecode1 is not None and bytecode2 is not None:
            bytecode_sim = self._cached_bytecode_similarity(bytecode1, bytecode2)
            
        emb_sim = self._embedding_similarity(embedding1, embedding2)
        
        # Calculate weighted hybrid score
        weights = self.weights
        total_weight = sum(weights.values())
        
        hybrid_score = (
            weights['simhash'] * simhash_sim +
            weights['ast'] * ast_sim +
            weights['bytecode'] * bytecode_sim +
            weights['embedding'] * (emb_sim * 0.5 + 0.5)  # Convert -1..1 to 0..1
        ) / total_weight
        
        return SimilarityResult(
            simhash_distance=simhash_dist,
            ast_similarity=ast_sim,
            bytecode_similarity=bytecode_sim,
            embedding_similarity=emb_sim,
            hybrid_score=hybrid_score
        )

# Default global instance
default_analyzer = SimilarityAnalyzer()

def hybrid_similarity_score(
    code1: str,
    code2: str,
    bytecode1: Optional[str] = None,
    bytecode2: Optional[str] = None,
    embedding1: Optional[np.ndarray] = None,
    embedding2: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Convenience function using the default analyzer.
    """
    result = default_analyzer.compare(
        code1, code2, bytecode1, bytecode2, embedding1, embedding2
    )
    return result.to_dict()

# Example usage
if __name__ == "__main__":
    # Sample contract code
    contract1 = """
    pragma solidity ^0.8.0;
    
    contract SimpleStorage {
        uint storedData;
        
        function set(uint x) public {
            storedData = x;
        }
        
        function get() public view returns (uint) {
            return storedData;
        }
    }
    """
    
    # Slightly modified version
    contract2 = """
    pragma solidity ^0.8.0;
    
    contract SimpleStorage {
        uint private storedData;  // Made private
        
        function set(uint x) public {
            storedData = x;  // Same functionality
        }
        
        // Added a comment
        function get() public view returns (uint) {
            return storedData;
        }
    }
    """
    
    # Compare the contracts
    analyzer = SimilarityAnalyzer()
    result = analyzer.compare(contract1, contract2)
    
    print("Similarity Analysis Results:")
    print(f"- SimHash Distance: {result.simhash_distance}")
    print(f"- AST Similarity: {result.ast_similarity:.2f}")
    print(f"- Hybrid Score: {result.hybrid_score:.2f}")
    
    # Using the convenience function
    print("\nUsing convenience function:")
    print(hybrid_similarity_score(contract1, contract2))

# Example usage (mock):
# result = hybrid_similarity_score(code1, code2, bytecode1, bytecode2, embedding1, embedding2)
# print(result)
