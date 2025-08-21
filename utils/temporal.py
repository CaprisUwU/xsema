"""
Temporal Analysis Utilities

This module provides functions for analyzing temporal patterns in time series data,
with a focus on detecting mathematical patterns like Fibonacci sequences and
golden ratio relationships in timestamped events.

Example usage:
    >>> import pandas as pd
    >>> from datetime import datetime, timedelta
    >>> 
    >>> # Create a sample time series with Fibonacci intervals
    >>> base_time = datetime(2023, 1, 1)
    >>> fib = [1, 1, 2, 3, 5, 8, 13, 21, 34]
    >>> timestamps = [base_time + timedelta(seconds=sum(fib[:i+1])) for i in range(len(fib))]
    >>> 
    >>> # Analyze the time series
    >>> fib_score = fibonacci_pattern_score(timestamps)
    >>> print(f"Fibonacci pattern score: {fib_score:.2f}")
"""

from typing import List, Tuple, Dict, Optional, Union, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from scipy import stats
from scipy.fft import fft
import warnings

# Type aliases
Timestamp = Union[datetime, pd.Timestamp, np.datetime64, str, int, float]
TimeSeries = Union[pd.Series, List[Timestamp], np.ndarray]

# Constants
GOLDEN_RATIO = (1 + 5 ** 0.5) / 2  # φ (phi), approximately 1.61803
FIBONACCI_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765]
FIBONACCI_SET = set(FIBONACCI_SEQUENCE)

@dataclass
class TemporalPatternResult:
    """Container for temporal pattern analysis results."""
    score: float                   # Overall pattern match score (0-1)
    confidence: float              # Confidence in the pattern (0-1)
    pattern_type: str              # Type of pattern detected
    parameters: dict               # Additional pattern-specific parameters
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'score': self.score,
            'confidence': self.confidence,
            'pattern_type': self.pattern_type,
            'parameters': self.parameters
        }

class TemporalAnalyzer:
    """
    Analyzes temporal patterns in time series data.
    
    This class provides methods to detect various temporal patterns in timestamped
    event data, including Fibonacci sequences, golden ratio relationships, and
    other mathematical patterns.
    """
    
    def __init__(self, min_events: int = 5, tolerance: float = 0.1):
        """
        Initialize the temporal analyzer.
        
        Args:
            min_events: Minimum number of events required for analysis
            tolerance: Tolerance for pattern matching (0-1)
        """
        self.min_events = max(3, min_events)  # Require at least 3 events for any pattern
        self.tolerance = max(0.01, min(0.5, tolerance))  # Keep tolerance in reasonable range
    
    def _prepare_timestamps(self, timestamps: TimeSeries) -> np.ndarray:
        """
        Convert and prepare timestamps for analysis.
        
        Args:
            timestamps: Input timestamps in any supported format
            
        Returns:
            Numpy array of UNIX timestamps (seconds since epoch)
        """
        # Convert to pandas Series if not already
        if not isinstance(timestamps, (pd.Series, pd.DatetimeIndex)):
            timestamps = pd.Series(timestamps)
        
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(timestamps):
            timestamps = pd.to_datetime(timestamps, errors='coerce')
        
        # Drop NaT values and sort
        timestamps = timestamps.dropna().sort_values()
        
        if len(timestamps) < 2:
            raise ValueError("At least 2 valid timestamps are required")
        
        # Convert to UNIX timestamps (seconds since epoch)
        return timestamps.astype(np.int64) // 10**9
    
    def fibonacci_pattern_score(self, timestamps: TimeSeries) -> TemporalPatternResult:
        """
        Calculate how closely the intervals between events match the Fibonacci sequence.
        
        Args:
            timestamps: Sequence of timestamps
            
        Returns:
            TemporalPatternResult with score and confidence
        """
        try:
            # Prepare and validate timestamps
            ts = self._prepare_timestamps(timestamps)
            if len(ts) < self.min_events:
                return TemporalPatternResult(
                    score=0.0,
                    confidence=0.0,
                    pattern_type="fibonacci",
                    parameters={"message": f"Insufficient data points (min {self.min_events} required)"}
                )
            
            # Calculate time differences in seconds
            diffs = np.diff(ts)
            
            # Find Fibonacci numbers up to the maximum interval
            max_diff = np.max(diffs)
            fibs = []
            a, b = 1, 1
            while a <= max_diff * 1.5:  # Include some margin
                fibs.append(a)
                a, b = b, a + b
            
            # Check how many intervals are close to Fibonacci numbers
            fib_matches = 0
            for d in diffs:
                # Find the closest Fibonacci number
                closest = min(fibs, key=lambda x: abs(x - d))
                if abs(closest - d) / (d + 1e-9) <= self.tolerance:
                    fib_matches += 1
            
            # Calculate score and confidence
            score = fib_matches / len(diffs)
            confidence = min(1.0, len(diffs) / 10.0)  # More points = higher confidence
            
            return TemporalPatternResult(
                score=score,
                confidence=confidence,
                pattern_type="fibonacci",
                parameters={
                    "matched_intervals": fib_matches,
                    "total_intervals": len(diffs),
                    "tolerance": self.tolerance
                }
            )
            
        except Exception as e:
            warnings.warn(f"Error in fibonacci_pattern_score: {str(e)}")
            return TemporalPatternResult(
                score=0.0,
                confidence=0.0,
                pattern_type="fibonacci",
                parameters={"error": str(e)}
            )
    
    def golden_ratio_pattern_score(self, timestamps: TimeSeries) -> TemporalPatternResult:
        """
        Calculate how closely consecutive time intervals match the golden ratio.
        
        Args:
            timestamps: Sequence of timestamps
            
        Returns:
            TemporalPatternResult with score and confidence
        """
        try:
            # Prepare and validate timestamps
            ts = self._prepare_timestamps(timestamps)
            if len(ts) < self.min_events:
                return TemporalPatternResult(
                    score=0.0,
                    confidence=0.0,
                    pattern_type="golden_ratio",
                    parameters={"message": f"Insufficient data points (min {self.min_events} required)"}
                )
            
            # Calculate time differences in seconds
            diffs = np.diff(ts)
            
            # Calculate consecutive ratios, avoiding division by zero
            with np.errstate(divide='ignore', invalid='ignore'):
                ratios = diffs[1:] / diffs[:-1]
            
            # Filter out invalid ratios (zeros, infinities, NaNs)
            valid_ratios = ratios[(ratios > 0) & np.isfinite(ratios)]
            
            if len(valid_ratios) == 0:
                return TemporalPatternResult(
                    score=0.0,
                    confidence=0.0,
                    pattern_type="golden_ratio",
                    parameters={"message": "No valid ratios could be calculated"}
                )
            
            # Calculate how close ratios are to the golden ratio
            phi_scores = 1 - np.minimum(
                np.abs(valid_ratios - GOLDEN_RATIO) / GOLDEN_RATIO,
                1.0  # Cap at 1.0
            )
            
            # Final score is the average of all valid ratios
            score = float(np.mean(phi_scores))
            confidence = min(1.0, len(valid_ratios) / 10.0)  # More points = higher confidence
            
            return TemporalPatternResult(
                score=score,
                confidence=confidence,
                pattern_type="golden_ratio",
                parameters={
                    "mean_ratio": float(np.mean(valid_ratios)),
                    "median_ratio": float(np.median(valid_ratios)),
                    "num_valid_ratios": len(valid_ratios),
                    "tolerance": self.tolerance
                }
            )
            
        except Exception as e:
            warnings.warn(f"Error in golden_ratio_pattern_score: {str(e)}")
            return TemporalPatternResult(
                score=0.0,
                confidence=0.0,
                pattern_type="golden_ratio",
                parameters={"error": str(e)}
            )
    
    def detect_periodicity(self, timestamps: TimeSeries, max_periods: int = 10) -> TemporalPatternResult:
        """
        Detect periodic patterns in the time series using FFT.
        
        Args:
            timestamps: Sequence of timestamps
            max_periods: Maximum number of periodic patterns to detect
            
        Returns:
            TemporalPatternResult with detected periodicities
        """
        try:
            # Prepare and validate timestamps
            ts = self._prepare_timestamps(timestamps)
            if len(ts) < self.min_events:
                return TemporalPatternResult(
                    score=0.0,
                    confidence=0.0,
                    pattern_type="periodicity",
                    parameters={"message": f"Insufficient data points (min {self.min_events} required)"}
                )
            
            # Convert to relative timestamps (seconds from first event)
            t0 = ts[0]
            rel_ts = ts - t0
            
            # Create a dense time series (1-second resolution)
            duration = rel_ts[-1] - rel_ts[0]
            if duration < 1:
                duration = 1
            
            # Use FFT to find dominant frequencies
            signal = np.zeros(int(duration) + 1)
            for t in rel_ts:
                idx = int(t - rel_ts[0])
                if 0 <= idx < len(signal):
                    signal[idx] += 1
            
            # Apply FFT
            fft_result = np.abs(fft(signal))
            freqs = np.fft.fftfreq(len(signal))
            
            # Get top frequencies (excluding DC component and negative freqs)
            positive_freqs = freqs[:len(freqs)//2]
            positive_fft = fft_result[:len(fft_result)//2]
            
            # Sort by magnitude and get top periods
            if len(positive_fft) > 1:
                # Exclude the DC component (index 0)
                top_indices = np.argsort(positive_fft[1:])[-max_periods:][::-1] + 1
                periods = []
                
                for idx in top_indices:
                    if positive_freqs[idx] > 0:  # Only consider positive frequencies
                        period = 1.0 / positive_freqs[idx]
                        if period > 1.0:  # Only consider periods > 1 second
                            periods.append({
                                'period': period,
                                'strength': float(positive_fft[idx] / np.max(positive_fft[1:])),
                                'frequency': float(positive_freqs[idx])
                            })
                
                if periods:
                    # Overall score is the strength of the strongest period
                    score = periods[0]['strength']
                    confidence = min(1.0, len(ts) / 50.0)  # More points = higher confidence
                    
                    return TemporalPatternResult(
                        score=score,
                        confidence=confidence,
                        pattern_type="periodicity",
                        parameters={
                            'detected_periods': periods[:max_periods],
                            'total_events': len(ts),
                            'duration_seconds': float(duration)
                        }
                    )
            
            # If no significant periods found
            return TemporalPatternResult(
                score=0.0,
                confidence=0.0,
                pattern_type="periodicity",
                parameters={"message": "No significant periodic patterns detected"}
            )
            
        except Exception as e:
            warnings.warn(f"Error in detect_periodicity: {str(e)}")
            return TemporalPatternResult(
                score=0.0,
                confidence=0.0,
                pattern_type="periodicity",
                parameters={"error": str(e)}
            )
    
    def analyze_all_patterns(self, timestamps: TimeSeries) -> Dict[str, TemporalPatternResult]:
        """
        Run all pattern detection algorithms on the time series.
        
        Args:
            timestamps: Sequence of timestamps
            
        Returns:
            Dictionary mapping pattern types to their results
        """
        return {
            'fibonacci': self.fibonacci_pattern_score(timestamps),
            'golden_ratio': self.golden_ratio_pattern_score(timestamps),
            'periodicity': self.detect_periodicity(timestamps)
        }

# Default instance
default_analyzer = TemporalAnalyzer()

def analyze_temporal_patterns(timestamps, **kwargs):
    """
    Analyze temporal patterns in a sequence of timestamps.
    
    This is a convenience function that uses the default TemporalAnalyzer instance
    to analyze temporal patterns in the provided timestamps.
    
    Args:
        timestamps: Sequence of datetime objects or timestamps
        **kwargs: Additional arguments to pass to the analyzer
        
    Returns:
        dict: Dictionary containing analysis results for different temporal patterns
    """
    # Use the default analyzer
    analyzer = kwargs.pop('analyzer', default_analyzer)
    
    # If a single analyzer method is specified, use it directly
    if 'method' in kwargs:
        method_name = kwargs.pop('method')
        if hasattr(analyzer, method_name):
            return getattr(analyzer, method_name)(timestamps, **kwargs)
        else:
            raise ValueError(f"Unknown analysis method: {method_name}")
    
    # Otherwise, run all pattern analyses
    return analyzer.analyze_all_patterns(timestamps)

# Alias for backward compatibility
detect_anomalies = analyze_temporal_patterns

def fibonacci_intervals(n: int = 10) -> List[int]:
    """
    Generate a list of the first n Fibonacci numbers.
    
    Args:
        n: Number of Fibonacci numbers to generate (default: 10)
        
    Returns:
        List of Fibonacci numbers
    """
    if n <= 0:
        return []
    elif n == 1:
        return [1]
    
    fib = [1, 1]
    while len(fib) < n:
        fib.append(fib[-1] + fib[-2])
    
    return fib[:n]

def golden_ratio_proximity(value: float, tolerance: float = 0.1) -> float:
    """
    Calculate how close a value is to the golden ratio.
    
    Args:
        value: The value to check
        tolerance: Tolerance for the proximity check (default: 0.1)
        
    Returns:
        A score between 0 and 1, where 1 means the value is exactly the golden ratio
    """
    if value <= 0:
        return 0.0
        
    ratio = value / GOLDEN_RATIO
    if abs(1 - ratio) <= tolerance:
        return 1.0 - (abs(1 - ratio) / tolerance)
    return 0.0

# Convenience functions
def fibonacci_pattern_score(timestamps: TimeSeries) -> float:
    """
    Convenience function to get Fibonacci pattern score using the default analyzer.
    """
    return default_analyzer.fibonacci_pattern_score(timestamps).score

def golden_ratio_pattern_score(timestamps: TimeSeries) -> float:
    """
    Convenience function to get golden ratio pattern score using the default analyzer.
    """
    return default_analyzer.golden_ratio_pattern_score(timestamps).score

def detect_periodicity(timestamps: TimeSeries) -> dict:
    """
    Convenience function to detect periodicity using the default analyzer.
    """
    result = default_analyzer.detect_periodicity(timestamps)
    return {
        'score': result.score,
        'confidence': result.confidence,
        **result.parameters
    }

# Example usage
if __name__ == "__main__":
    import numpy as np
    from datetime import datetime, timedelta
    
    # Create a sample time series with Fibonacci intervals
    base_time = datetime(2023, 1, 1)
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34]
    timestamps = [base_time + timedelta(seconds=sum(fib[:i+1])) for i in range(len(fib))]
    
    # Analyze the time series
    analyzer = TemporalAnalyzer()
    
    print("Analyzing time series with Fibonacci intervals:")
    fib_result = analyzer.fibonacci_pattern_score(timestamps)
    print(f"Fibonacci pattern score: {fib_result.score:.2f} (confidence: {fib_result.confidence:.2f})")
    
    phi_result = analyzer.golden_ratio_pattern_score(timestamps)
    print(f"Golden ratio pattern score: {phi_result.score:.2f} (confidence: {phi_result.confidence:.2f})")
    
    # Analyze all patterns
    print("\nRunning full analysis:")
    all_results = analyzer.analyze_all_patterns(timestamps)
    for pattern, result in all_results.items():
        print(f"\n{pattern.replace('_', ' ').title()}:")
        print(f"  Score: {result.score:.2f}")
        print(f"  Confidence: {result.confidence:.2f}")
        if result.parameters:
            print("  Parameters:")
            for k, v in result.parameters.items():
                print(f"    {k}: {v}")
