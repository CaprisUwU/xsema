"""
Bitwise Analysis Module

This module provides functions to analyze integer values at the bit level.
Particularly useful for analyzing token IDs, transaction values, and other
numeric blockchain data to find interesting patterns and properties.
"""
from typing import Dict, List, Tuple, Any
from functools import lru_cache
import math
import numpy as np

# Pre-compute powers of 2 for faster bit manipulation
POWERS_OF_2 = [1 << i for i in range(256)]

def bitwise_features(n: int) -> Dict[str, float]:
    """
    Calculate various bit-level features for an integer.
    
    Args:
        n: Integer to analyze
        
    Returns:
        dict: Dictionary containing bitwise features:
            - bit_length: Number of bits required to represent the number
            - trailing_zeros: Number of trailing 0 bits
            - bit_entropy: Shannon entropy of the bit distribution (0-1)
            - parity: 1 if number of 1 bits is odd, 0 if even
            - max_run_ones: Length of the longest sequence of consecutive 1s
            - max_run_zeros: Length of the longest sequence of consecutive 0s
            - bit_density: Ratio of 1 bits to total bits
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("Input must be a non-negative integer")
    
    if n == 0:
        return {
            "bit_length": 0,
            "trailing_zeros": 0,
            "bit_entropy": 0.0,
            "parity": 0,
            "max_run_ones": 0,
            "max_run_zeros": 0,
            "bit_density": 0.0
        }
    
    # Convert to binary string and analyze
    b = bin(n)[2:]  # binary string without '0b' prefix
    bit_len = len(b)
    
    # Basic features
    trailing_zeros = len(b) - len(b.rstrip('0'))
    ones_count = b.count('1')
    zeros_count = bit_len - ones_count
    
    # Calculate runs of 1s and 0s
    max_run_ones = max(len(run) for run in b.split('0')) if '1' in b else 0
    max_run_zeros = max(len(run) for run in b.split('1')) if '0' in b else 0
    
    # Calculate bit entropy
    p1 = ones_count / bit_len
    p0 = 1 - p1
    
    # Handle edge cases for log calculations
    if p0 > 0 and p1 > 0:
        bit_entropy = -(p0 * math.log2(p0) + p1 * math.log2(p1))
    else:
        bit_entropy = 0.0
    
    return {
        "bit_length": bit_len,
        "trailing_zeros": trailing_zeros,
        "bit_entropy": round(bit_entropy, 6),
        "parity": ones_count % 2,
        "max_run_ones": max_run_ones,
        "max_run_zeros": max_run_zeros,
        "bit_density": round(ones_count / bit_len, 4) if bit_len > 0 else 0.0
    }

def is_power_of_two(n: int) -> bool:
    """Check if a number is a power of two."""
    return n > 0 and (n & (n - 1)) == 0

def count_set_bits(n: int) -> int:
    """Count the number of set bits (1s) in the binary representation."""
    return bin(n).count('1')

def get_bit_ranges(n: int) -> List[Tuple[int, int]]:
    """
    Get ranges of consecutive set bits in the binary representation.
    
    Returns:
        List of (start, end) tuples for each range of consecutive 1s
    """
    b = bin(n)[2:]
    ranges = []
    start = None
    
    for i, bit in enumerate(b):
        if bit == '1' and start is None:
            start = i
        elif bit == '0' and start is not None:
            ranges.append((start, i-1))
            start = None
    
    if start is not None:
        ranges.append((start, len(b)-1))
    
    return ranges

def analyze_bytecode_patterns(bytecode: str) -> Dict[str, Any]:
    """
    Analyze EVM bytecode for common patterns and potential vulnerabilities.
    
    Args:
        bytecode: The EVM bytecode as a hex string (with or without 0x prefix)
        
    Returns:
        dict: Analysis results including patterns, vulnerabilities, and statistics
    """
    if not bytecode:
        return {
            'error': 'Empty bytecode',
            'patterns': {},
            'vulnerabilities': [],
            'statistics': {}
        }
    
    # Remove 0x prefix if present
    if bytecode.startswith('0x'):
        bytecode = bytecode[2:]
    
    # Convert to bytes for analysis
    try:
        byte_array = bytes.fromhex(bytecode)
    except ValueError:
        return {
            'error': 'Invalid hex string',
            'patterns': {},
            'vulnerabilities': ['INVALID_BYTECODE'],
            'statistics': {}
        }
    
    # Basic statistics
    byte_count = len(byte_array)
    unique_bytes = len(set(byte_array))
    
    # Common patterns to detect
    patterns = {
        'delegatecall': False,
        'selfdestruct': False,
        'create2': False,
        'staticcall': False,
        'callcode': False,
        'extcodesize': False,
        'extcodecopy': False,
        'callvalue': False,
        'sstore': False,
        'sload': False,
        'reentrancy_risk': False,
        'unchecked_call': False,
        'zero_value_call': False,
        'unchecked_arithmetic': False,
        'timestamp_dependency': False
    }
    
    # Vulnerabilities found
    vulnerabilities = []
    
    # Check for common opcodes (simplified)
    opcode_map = {
        b'\xf4': 'selfdestruct',
        b'\xf1': 'callcode',
        b'\x5a': 'gas',
        b'\x54': 'sload',
        b'\x55': 'sstore',
        b'\x34': 'callvalue',
        b'\x3d': 'returndatasize',
        b'\xf2': 'delegatecall',
        b'\xf5': 'create2',
        b'\xfa': 'staticcall',
        b'\x3b': 'extcodesize',
        b'\x3c': 'extcodecopy'
    }
    
    # Scan for opcodes
    for i in range(len(byte_array)):
        opcode = bytes([byte_array[i]])
        if opcode in opcode_map:
            op_name = opcode_map[opcode]
            if op_name in patterns:
                patterns[op_name] = True
    
    # Check for common vulnerability patterns
    if patterns['delegatecall'] and patterns['callvalue']:
        vulnerabilities.append('DELEGATECALL_WITH_VALUE')
        patterns['reentrancy_risk'] = True
    
    if patterns['selfdestruct']:
        vulnerabilities.append('SELFDESTRUCT_PRESENT')
    
    if patterns['delegatecall'] and not patterns['staticcall']:
        patterns['reentrancy_risk'] = True
    
    # Calculate statistics
    statistics = {
        'byte_count': byte_count,
        'unique_bytes': unique_bytes,
        'entropy': len(set(byte_array)) / 256.0 if byte_count > 0 else 0,
        'vulnerability_count': len(vulnerabilities)
    }
    
    return {
        'patterns': patterns,
        'vulnerabilities': vulnerabilities,
        'statistics': statistics
    }

# Example usage
if __name__ == "__main__":
    test_number = 0x742d35cc6634c0532925a3b844bc454e4438f44e
    features = bitwise_features(test_number)
    print(f"Analysis for {test_number} (0x{test_number:x}):")
    for k, v in features.items():
        print(f"{k}: {v}")
    
    print(f"\nIs power of two? {is_power_of_two(test_number)}")
    print(f"Set bits count: {count_set_bits(test_number)}")
    print(f"Bit ranges: {get_bit_ranges(test_number)}")