"""
Golden Ratio Analysis Module

This module provides functions to analyze data using the golden ratio (φ ≈ 1.618),
which is often associated with aesthetic harmony, natural patterns, and balance.
Particularly useful for analyzing visual traits, time patterns, and numerical
sequences in NFT collections.
"""
from typing import List, Tuple, Union, Dict, Optional
import numpy as np
import pandas as pd
from dataclasses import dataclass
from scipy.stats import norm

# Mathematical constants
PHI = (1 + 5 ** 0.5) / 2  # ≈ 1.618033988749895
PHI_CONJUGATE = 1 - PHI     # ≈ -0.6180339887498949

@dataclass
class GoldenRatioAnalysis:
    """Container for golden ratio analysis results."""
    alignment_score: float       # How well ratios match φ (0-1)
    gaps_score: float            # How many gaps are close to φ (0-1)
    fibonacci_score: float       # How close values are to Fibonacci sequence (0-1)
    spiral_score: float          # How well points fit a golden spiral (0-1)
    is_harmonic: bool            # If multiple aspects show golden ratio patterns


def golden_ratio_alignment(series: pd.Series, tolerance: float = 0.1) -> float:
    """
    Measure how closely consecutive value ratios align with the golden ratio.
    
    Args:
        series: Pandas Series of numerical values
        tolerance: How close to φ a ratio needs to be (as fraction of φ)
        
    Returns:
        float: Score from 0 (no alignment) to 1 (perfect alignment)
        
    Example:
        >>> data = pd.Series([1, 1, 2, 3, 5, 8, 13])
        >>> golden_ratio_alignment(data)
        0.98  # Very close to Fibonacci sequence
    """
    values = series.dropna().astype(float).sort_values().values
    if len(values) < 3:
        return 0.0
        
    ratios = values[1:] / values[:-1]
    # Filter out zeros and infinities
    valid_ratios = ratios[(ratios > 0) & (ratios < 1e6)]
    if len(valid_ratios) == 0:
        return 0.0
        
    # Calculate how close each ratio is to φ
    deviations = np.abs(valid_ratios - PHI) / PHI
    # Convert to score where 1 is perfect match, 0 is outside tolerance
    scores = np.maximum(0, 1 - deviations / tolerance)
    return float(np.mean(scores))

def golden_ratio_gaps(timestamps: pd.Series, window_seconds: float = 1.0) -> float:
    """
    Analyze time gaps between events for golden ratio patterns.
    
    Args:
        timestamps: Series of datetime objects or timestamps
        window_seconds: Time window in seconds to consider as "close" to φ
        
    Returns:
        float: Fraction of gaps close to φ seconds apart (0-1)
    """
    if len(timestamps) < 2:
        return 0.0
        
    # Convert to seconds since epoch
    ts = pd.to_datetime(timestamps).sort_values()
    gaps = np.diff(ts.astype(np.int64) // 10**9)  # Convert to seconds
    
    if len(gaps) == 0:
        return 0.0
        
    # Normalize gaps by dividing by φ and finding fractional part
    normalized_gaps = np.abs((gaps / PHI) - np.round(gaps / PHI))
    # Count gaps that are close to a multiple of φ
    close_gaps = np.mean(normalized_gaps < (window_seconds / PHI))
    return float(close_gaps)

def is_fibonacci_like(sequence: List[float], tolerance: float = 0.1) -> Tuple[bool, float]:
    """
    Check if a sequence follows the Fibonacci pattern (each number is the sum of the two preceding ones).
    
    Returns:
        Tuple of (is_fibonacci, confidence_score)
    """
    if len(sequence) < 3:
        return False, 0.0
        
    errors = []
    for i in range(2, len(sequence)):
        if sequence[i-1] == 0 or sequence[i-2] == 0:
            continue  # Avoid division by zero
        ratio = sequence[i] / (sequence[i-1] + sequence[i-2])
        errors.append(abs(ratio - 1))
    
    if not errors:
        return False, 0.0
        
    avg_error = np.mean(errors)
    return avg_error < tolerance, 1 - min(avg_error, 1.0)

def analyze_golden_patterns(
    values: Union[pd.Series, List[float]],
    timestamps: Optional[Union[pd.Series, List]] = None
) -> GoldenRatioAnalysis:
    """
    Comprehensive golden ratio analysis of a sequence of values.
    
    Args:
        values: Sequence of numerical values to analyze
        timestamps: Optional timestamps for temporal analysis
        
    Returns:
        GoldenRatioAnalysis object with various golden ratio metrics
    """
    if not isinstance(values, pd.Series):
        values = pd.Series(values)
        
    # Calculate alignment with golden ratio
    alignment = golden_ratio_alignment(values)
    
    # Calculate temporal patterns if timestamps are provided
    gaps = golden_ratio_gaps(timestamps) if timestamps is not None else 0.0
    
    # Check for Fibonacci-like sequences
    fib_check = is_fibonacci_like(values.sort_values().values.tolist())
    fibonacci_score = fib_check[1] if fib_check[0] else 0.0
    
    # Calculate spiral fit (simplified)
    # This is a placeholder - in practice you'd map values to polar coordinates
    spiral_score = 0.0
    if len(values) >= 5:
        angles = np.linspace(0, 8 * np.pi, len(values))
        radii = values.rank(pct=True) * 10  # Normalize to similar scale
        # Check if points follow a golden spiral pattern
        spiral_score = min(np.corrcoef(angles, np.log(radii + 1))[0, 1], 1.0)
    
    return GoldenRatioAnalysis(
        alignment_score=alignment,
        gaps_score=gaps,
        fibonacci_score=fibonacci_score,
        spiral_score=max(0, spiral_score),  # Ensure non-negative
        is_harmonic=(alignment + gaps + fibonacci_score + max(0, spiral_score)) / 4 > 0.7
    )

# Example usage
if __name__ == "__main__":
    # Test with Fibonacci sequence
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34]
    analysis = analyze_golden_patterns(fib)
    
    print(f"Fibonacci sequence analysis:")
    print(f"Alignment with φ: {analysis.alignment_score:.2f}")
    print(f"Fibonacci pattern confidence: {analysis.fibonacci_score:.2f}")
    print(f"Overall harmonic: {analysis.is_harmonic}")
    
    # Test with random data
    import random
    random_data = [random.uniform(1, 100) for _ in range(20)]
    analysis = analyze_golden_patterns(random_data)
    
    print("\nRandom data analysis:")
    print(f"Alignment with φ: {analysis.alignment_score:.2f}")
    print(f"Fibonacci pattern confidence: {analysis.fibonacci_score:.2f}")
    print(f"Overall harmonic: {analysis.is_harmonic}")