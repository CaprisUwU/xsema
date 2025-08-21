"""
Graph Entropy Analysis Module

This module provides functions to analyze the structure and patterns in NFT ownership
networks using graph theory and information theory concepts. It's particularly useful
for understanding the distribution of NFTs across wallets and detecting unusual patterns.
"""
from typing import Dict, List, Tuple, Set, Optional, Union
import pandas as pd
import networkx as nx
import numpy as np
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class GraphAnalysis:
    """Container for graph analysis results."""
    entropy: float                 # Shannon entropy of degree distribution
    degree_assortativity: float    # Degree correlation coefficient (-1 to 1)
    density: float                 # Graph density (0-1)
    components: int                # Number of connected components
    largest_component_size: int    # Size of the largest connected component
    clustering: float              # Average clustering coefficient
    degree_centrality: Dict[str, float]  # Degree centrality for each node
    betweenness: Dict[str, float]  # Betweenness centrality for each node
    pagerank: Dict[str, float]     # PageRank scores for each node

def compute_wallet_graph_entropy(
    df: pd.DataFrame,
    wallet_col: str = "wallet",
    token_col: str = "token_id",
    return_full_analysis: bool = False
) -> Union[float, GraphAnalysis]:
    """
    Analyze the wallet-token bipartite graph and compute graph entropy.
    
    Args:
        df: DataFrame containing wallet-token relationships
        wallet_col: Name of the wallet column
        token_col: Name of the token ID column
        return_full_analysis: If True, returns a GraphAnalysis object with additional metrics
        
    Returns:
        float: Graph entropy value, or GraphAnalysis object if return_full_analysis is True
        
    Example:
        >>> df = pd.DataFrame({
        ...     'wallet': ['A', 'A', 'B', 'C', 'C', 'C'],
        ...     'token_id': [1, 2, 1, 3, 4, 5]
        ... })
        >>> entropy = compute_wallet_graph_entropy(df)
        >>> print(f"Graph entropy: {entropy:.4f}")
    """
    # Create bipartite graph
    B = nx.Graph()
    
    # Add nodes with bipartite attribute
    wallets = set(df[wallet_col])
    tokens = set(df[token_col])
    
    B.add_nodes_from(wallets, bipartite=0)  # Wallet nodes (type 0)
    B.add_nodes_from(tokens, bipartite=1)   # Token nodes (type 1)
    
    # Add edges
    edges = list(zip(df[wallet_col], df[token_col]))
    B.add_edges_from(edges)
    
    # Get wallet nodes and their degrees
    wallet_nodes = {n for n, d in B.nodes(data=True) if d['bipartite'] == 0}
    degrees = [B.degree(n) for n in wallet_nodes]
    
    # Calculate entropy of degree distribution
    total = sum(degrees)
    if total == 0:
        entropy_val = 0.0
    else:
        probs = np.array(degrees) / total
        entropy_val = -np.sum(probs * np.log2(probs + 1e-10))  # Add small epsilon to avoid log(0)
    
    if not return_full_analysis:
        return entropy_val
    
    # Calculate additional graph metrics if full analysis requested
    try:
        # Project to wallet graph (co-ownership network)
        wallet_graph = nx.bipartite.projected_graph(B, wallet_nodes)
        
        # Calculate metrics
        degree_assortativity = nx.degree_assortativity_coefficient(wallet_graph) if len(wallet_graph) > 1 else 0.0
        density = nx.density(wallet_graph)
        components = list(nx.connected_components(wallet_graph))
        largest_component = max(components, key=len) if components else set()
        clustering = nx.average_clustering(wallet_graph) if wallet_graph else 0.0
        
        # Centrality measures (compute only for a sample if graph is large)
        max_nodes = 1000  # Limit for performance
        sample_nodes = (list(wallet_graph.nodes())[:max_nodes] 
                       if len(wallet_graph) > max_nodes 
                       else list(wallet_graph.nodes()))
        
        degree_centrality = nx.degree_centrality(wallet_graph)
        betweenness = nx.betweenness_centrality(wallet_graph, k=min(100, len(wallet_graph)))
        pagerank = nx.pagerank(wallet_graph, max_iter=100)
        
        return GraphAnalysis(
            entropy=entropy_val,
            degree_assortativity=degree_assortativity,
            density=density,
            components=len(components),
            largest_component_size=len(largest_component),
            clustering=clustering,
            degree_centrality=degree_centrality,
            betweenness=betweenness,
            pagerank=pagerank
        )
    except Exception as e:
        print(f"Warning: Could not compute full graph analysis: {str(e)}")
        return entropy_val

def detect_whales(
    df: pd.DataFrame,
    wallet_col: str = "wallet",
    token_col: str = "token_id",
    threshold_std: float = 2.0
) -> Dict[str, Dict]:
    """
    Detect whale wallets (wallets with unusually high NFT holdings).
    
    Args:
        df: DataFrame containing wallet-token relationships
        wallet_col: Name of the wallet column
        token_col: Name of the token ID column
        threshold_std: Number of standard deviations above mean to consider a whale
        
    Returns:
        Dict mapping wallet addresses to their whale metrics
    """
    # Count NFTs per wallet
    wallet_counts = df[wallet_col].value_counts()
    
    if len(wallet_counts) == 0:
        return {}
    
    # Calculate statistics
    mean_count = wallet_counts.mean()
    std_count = wallet_counts.std()
    
    if std_count == 0:
        return {}
    
    # Find whales (wallets with count > mean + threshold_std * std)
    threshold = mean_count + threshold_std * std_count
    whales = wallet_counts[wallet_counts > threshold]
    
    # Calculate whale metrics
    whale_data = {}
    for wallet, count in whales.items():
        percentile = (count - mean_count) / std_count
        whale_data[wallet] = {
            'nft_count': int(count),
            'percentile': float(percentile),
            'threshold_exceeded': float(count - threshold),
            'is_whale': True
        }
    
    return whale_data


def calculate_graph_entropy(graph_data: Union[pd.DataFrame, Dict, List]) -> float:
    """
    Calculate graph entropy from various input formats.
    
    Args:
        graph_data: Graph data in various formats:
            - DataFrame: wallet-token relationships
            - Dict: adjacency matrix or edge list
            - List: list of edges
            
    Returns:
        float: Graph entropy value
    """
    if isinstance(graph_data, pd.DataFrame):
        # Assume it's a wallet-token relationship DataFrame
        return compute_wallet_graph_entropy(graph_data)
    elif isinstance(graph_data, dict):
        # Assume it's an adjacency matrix or edge list
        if 'edges' in graph_data:
            # Edge list format
            df = pd.DataFrame(graph_data['edges'], columns=['wallet', 'token_id'])
            return compute_wallet_graph_entropy(df)
        else:
            # Adjacency matrix format - convert to edge list
            edges = []
            for wallet, tokens in graph_data.items():
                if isinstance(tokens, (list, set)):
                    for token in tokens:
                        edges.append([wallet, token])
            df = pd.DataFrame(edges, columns=['wallet', 'token_id'])
            return compute_wallet_graph_entropy(df)
    elif isinstance(graph_data, list):
        # Assume it's a list of edges
        if graph_data and len(graph_data[0]) == 2:
            df = pd.DataFrame(graph_data, columns=['wallet', 'token_id'])
            return compute_wallet_graph_entropy(df)
        else:
            raise ValueError("List must contain edge pairs [wallet, token_id]")
    else:
        raise ValueError(f"Unsupported graph data type: {type(graph_data)}")

# Example usage
if __name__ == "__main__":
    # Create sample data
    data = {
        'wallet': ['A', 'A', 'B', 'C', 'C', 'C', 'D', 'D', 'D', 'D'],
        'token_id': [1, 2, 1, 3, 4, 5, 6, 7, 8, 9]
    }
    df = pd.DataFrame(data)
    
    # Basic entropy calculation
    entropy = compute_wallet_graph_entropy(df)
    print(f"Graph entropy: {entropy:.4f}")
    
    # Full graph analysis
    analysis = compute_wallet_graph_entropy(df, return_full_analysis=True)
    print(f"\nGraph Analysis:")
    print(f"- Entropy: {analysis.entropy:.4f}")
    print(f"- Density: {analysis.density:.4f}")
    print(f"- Connected components: {analysis.components}")
    print(f"- Largest component size: {analysis.largest_component_size}")
    
    # Detect whales
    print("\nDetecting whales:")
    whales = detect_whales(df)
    for wallet, stats in whales.items():
        print(f"- {wallet}: {stats['nft_count']} NFTs "
              f"({stats['percent_of_collection']:.1f}% of collection)")
