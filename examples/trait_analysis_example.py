"""
Trait Analysis Example
=====================

This example demonstrates how to use the trait analysis functionality to analyze NFT traits,
calculate rarity scores, and integrate with the API endpoints.

Key Features:
- Loading and analyzing NFT traits
- Calculating various rarity metrics
- Generating collection statistics
- Integration with API endpoints
- Caching and performance optimization
"""

import asyncio
import json
from typing import Dict, List, Optional
from pathlib import Path

# Import the trait analysis module
from traits.trait_rarity import (
    analyze_token_traits,
    get_trait_statistics,
    TraitAnalysis,
    DEFAULT_TRAIT_WEIGHTS
)

# Import API client utilities (assuming they exist in your project)
from api.client import NFTApiClient
from utils.cache import cache_config

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SAMPLE_DATA_DIR = Path(__file__).parent / "data"
CACHE_TTL = 3600  # 1 hour

class TraitAnalysisExample:
    """Example class demonstrating trait analysis functionality."""
    
    def __init__(self, api_client: Optional[NFTApiClient] = None):
        """Initialize with optional API client."""
        self.api_client = api_client
        self.cache = {}
        
    async def load_collection_data(self, collection_slug: str) -> Dict:
        """
        Load collection data from API or cache.
        
        Args:
            collection_slug: Unique identifier for the collection
            
        Returns:
            Dictionary containing collection data
        """
        cache_key = f"collection_{collection_slug}"
        
        # Try to get from cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Fetch from API if client is available
        if self.api_client:
            try:
                data = await self.api_client.get_collection(collection_slug)
                self.cache[cache_key] = data
                return data
            except Exception as e:
                logger.warning(f"Failed to fetch collection data: {e}")
        
        # Fall back to sample data
        sample_file = SAMPLE_DATA_DIR / f"{collection_slug}.json"
        if sample_file.exists():
            with open(sample_file, 'r') as f:
                return json.load(f)
                
        raise ValueError(f"Could not load data for collection: {collection_slug}")
    
    def analyze_single_token(
        self,
        token_id: str,
        token_traits: Dict[str, str],
        collection_trait_counts: Dict,
        total_tokens: int,
        weights: Optional[Dict] = None
    ) -> TraitAnalysis:
        """
        Analyze a single token's traits.
        
        Args:
            token_id: Unique identifier for the token
            token_traits: Dictionary of trait_type -> value
            collection_trait_counts: Dictionary of trait_type -> {value: count}
            total_tokens: Total number of tokens in the collection
            weights: Optional dictionary of trait weights
            
        Returns:
            TraitAnalysis object with analysis results
        """
        return analyze_token_traits(
            token_id=token_id,
            token_traits=token_traits,
            collection_trait_counts=collection_trait_counts,
            total_tokens=total_tokens,
            weights=weights or DEFAULT_TRAIT_WEIGHTS
        )
    
    def analyze_collection(self, collection_data: Dict) -> Dict:
        """
        Analyze an entire collection.
        
        Args:
            collection_data: Dictionary containing collection data
            
        Returns:
            Dictionary with collection analysis results
        """
        tokens = collection_data.get('tokens', [])
        trait_counts = collection_data.get('trait_counts', {})
        total_tokens = collection_data.get('total_supply', len(tokens))
        
        # Calculate collection-wide statistics
        stats = get_trait_statistics(trait_counts)
        
        # Analyze each token
        analyzed_tokens = []
        for token in tokens[:100]:  # Limit to first 100 tokens for example
            analysis = self.analyze_single_token(
                token_id=token['id'],
                token_traits=token.get('traits', {}),
                collection_trait_counts=trait_counts,
                total_tokens=total_tokens
            )
            analyzed_tokens.append({
                'token_id': token['id'],
                'scores': analysis.scores,
                'traits': token.get('traits', {})
            })
        
        return {
            'collection_stats': stats,
            'tokens_analyzed': len(analyzed_tokens),
            'sample_tokens': analyzed_tokens[:5],  # Return first 5 as sample
            'average_rarity': sum(t['scores']['normalized_rarity'] for t in analyzed_tokens) / len(analyzed_tokens)
        }

    async def run_example(self, collection_slug: str = "boredapeyachtclub") -> None:
        """
        Run the complete trait analysis example.
        
        Args:
            collection_slug: Collection identifier (default: boredapeyachtclub)
        """
        print(f"\n{'='*50}")
        print(f"Trait Analysis Example: {collection_slug}")
        print(f"{'='*50}\n")
        
        # 1. Load collection data
        print("1. Loading collection data...")
        try:
            collection_data = await self.load_collection_data(collection_slug)
            print(f"   ✓ Loaded data for {collection_data.get('name', collection_slug)}")
            print(f"   - Total supply: {collection_data.get('total_supply', 'N/A')}")
            print(f"   - Traits tracked: {len(collection_data.get('trait_counts', {}))}")
        except Exception as e:
            print(f"   ✗ Failed to load collection data: {e}")
            return
        
        # 2. Analyze collection
        print("\n2. Analyzing collection traits...")
        try:
            analysis = self.analyze_collection(collection_data)
            print(f"   ✓ Analyzed {analysis['tokens_analyzed']} tokens")
            print(f"   - Average rarity score: {analysis['average_rarity']:.4f}")
            
            # Print sample token analysis
            print("\n   Sample token analysis:")
            for token in analysis['sample_tokens']:
                print(f"   - Token #{token['token_id']}")
                print(f"     Rarity: {token['scores']['normalized_rarity']:.4f}")
                print(f"     Traits: {', '.join(f'{k}:{v}' for k, v in token['traits'].items()[:3])}...")
                
        except Exception as e:
            print(f"   ✗ Failed to analyze collection: {e}")
            return
        
        print("\nExample completed successfully!")
        print(f"{'='*50}\n")

# Example usage
if __name__ == "__main__":
    # Initialize with or without API client
    example = TraitAnalysisExample(api_client=None)
    
    # Run the example
    asyncio.run(example.run_example("boredapeyachtclub"))
