"""
Multi-Chain Configuration

Comprehensive configuration for multiple blockchain networks including
Ethereum, Polygon, BSC, Arbitrum, Optimism, and Solana.
"""
from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from enum import Enum
import os


class ChainType(str, Enum):
    """Supported blockchain types."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    SOLANA = "solana"
    BASE = "base"
    AVALANCHE = "avalanche"
    FANTOM = "fantom"


class NetworkConfig(BaseModel):
    """Configuration for a specific blockchain network."""
    
    chain_id: int
    name: str
    symbol: str
    rpc_url: str
    explorer_url: str
    native_currency: str
    decimals: int = 18
    is_testnet: bool = False
    supports_eip1559: bool = True
    block_time: float = 12.0  # seconds
    max_priority_fee: Optional[int] = None
    max_fee: Optional[int] = None
    
    # Network-specific features
    supports_contracts: bool = True
    supports_nfts: bool = True
    supports_defi: bool = True
    
    # Rate limiting
    requests_per_second: int = 10
    batch_size: int = 100
    
    class Config:
        extra = "ignore"


class MultiChainConfig:
    """Multi-chain configuration manager."""
    
    def __init__(self):
        self.networks: Dict[ChainType, NetworkConfig] = {}
        self._load_configurations()
    
    def _load_configurations(self):
        """Load network configurations from environment variables."""
        
        # Ethereum Mainnet
        self.networks[ChainType.ETHEREUM] = NetworkConfig(
            chain_id=1,
            name="Ethereum Mainnet",
            symbol="ETH",
            rpc_url=os.getenv("ETHEREUM_RPC_URL", "https://mainnet.infura.io/v3/YOUR-PROJECT-ID"),
            explorer_url="https://etherscan.io",
            native_currency="Ether",
            decimals=18,
            supports_eip1559=True,
            block_time=12,
            max_priority_fee=2000000000,  # 2 gwei
            max_fee=50000000000,  # 50 gwei
        )
        
        # Polygon Mainnet
        self.networks[ChainType.POLYGON] = NetworkConfig(
            chain_id=137,
            name="Polygon Mainnet",
            symbol="MATIC",
            rpc_url=os.getenv("POLYGON_RPC_URL", "https://polygon-mainnet.infura.io/v3/YOUR-PROJECT-ID"),
            explorer_url="https://polygonscan.com",
            native_currency="MATIC",
            decimals=18,
            supports_eip1559=False,  # Polygon doesn't support EIP-1559
            block_time=2,
            max_priority_fee=None,
            max_fee=30000000000,  # 30 gwei
        )
        
        # Binance Smart Chain
        self.networks[ChainType.BSC] = NetworkConfig(
            chain_id=56,
            name="Binance Smart Chain",
            symbol="BNB",
            rpc_url=os.getenv("BSC_RPC_URL", "https://bsc-dataseed1.binance.org/"),
            explorer_url="https://bscscan.com",
            native_currency="BNB",
            decimals=18,
            supports_eip1559=False,
            block_time=3,
            max_priority_fee=None,
            max_fee=20000000000,  # 20 gwei
        )
        
        # Arbitrum One
        self.networks[ChainType.ARBITRUM] = NetworkConfig(
            chain_id=42161,
            name="Arbitrum One",
            symbol="ETH",
            rpc_url=os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc"),
            explorer_url="https://arbiscan.io",
            native_currency="ETH",
            decimals=18,
            supports_eip1559=True,
            block_time=0.25,  # 250ms
            max_priority_fee=100000000,  # 0.1 gwei
            max_fee=1000000000,  # 1 gwei
        )
        
        # Optimism
        self.networks[ChainType.OPTIMISM] = NetworkConfig(
            chain_id=10,
            name="Optimism",
            symbol="ETH",
            rpc_url=os.getenv("OPTIMISM_RPC_URL", "https://mainnet.optimism.io"),
            explorer_url="https://optimistic.etherscan.io",
            native_currency="ETH",
            decimals=18,
            supports_eip1559=True,
            block_time=2,
            max_priority_fee=100000000,  # 0.1 gwei
            max_fee=1000000000,  # 1 gwei
        )
        
        # Base
        self.networks[ChainType.BASE] = NetworkConfig(
            chain_id=8453,
            name="Base",
            symbol="ETH",
            rpc_url=os.getenv("BASE_RPC_URL", "https://mainnet.base.org"),
            explorer_url="https://basescan.org",
            native_currency="ETH",
            decimals=18,
            supports_eip1559=True,
            block_time=2,
            max_priority_fee=100000000,  # 0.1 gwei
            max_fee=1000000000,  # 1 gwei
        )
        
        # Avalanche C-Chain
        self.networks[ChainType.AVALANCHE] = NetworkConfig(
            chain_id=43114,
            name="Avalanche C-Chain",
            symbol="AVAX",
            rpc_url=os.getenv("AVALANCHE_RPC_URL", "https://api.avax.network/ext/bc/C/rpc"),
            explorer_url="https://snowtrace.io",
            native_currency="AVAX",
            decimals=18,
            supports_eip1559=False,
            block_time=2,
            max_priority_fee=None,
            max_fee=25000000000,  # 25 gwei
        )
        
        # Fantom Opera
        self.networks[ChainType.FANTOM] = NetworkConfig(
            chain_id=250,
            name="Fantom Opera",
            symbol="FTM",
            rpc_url=os.getenv("FANTOM_RPC_URL_ALT", "https://rpcapi.fantom.network"),  # Use fallback URL
            explorer_url="https://ftmscan.com",
            native_currency="FTM",
            decimals=18,
            supports_eip1559=False,
            block_time=1,
            max_priority_fee=None,
            max_fee=100000000000,  # 100 gwei
        )
        
        # Solana Mainnet
        self.networks[ChainType.SOLANA] = NetworkConfig(
            chain_id=-1,  # Solana doesn't use chain_id like EVM chains
            name="Solana Mainnet",
            symbol="SOL",
            rpc_url=os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"),
            explorer_url="https://explorer.solana.com",
            native_currency="SOL",
            decimals=9,  # Solana uses 9 decimals
            supports_eip1559=False,  # Solana has different fee mechanism
            block_time=0.4,  # 400ms (0.4 seconds)
            max_priority_fee=None,
            max_fee=None,
            supports_contracts=False,  # Solana uses programs, not contracts
        )
    
    def get_network(self, chain_type: ChainType) -> Optional[NetworkConfig]:
        """Get configuration for a specific network."""
        return self.networks.get(chain_type)
    
    def get_network_by_chain_id(self, chain_id: int) -> Optional[NetworkConfig]:
        """Get network configuration by chain ID."""
        for network in self.networks.values():
            if network.chain_id == chain_id:
                return network
        return None
    
    def get_supported_networks(self) -> List[ChainType]:
        """Get list of supported network types."""
        return list(self.networks.keys())
    
    def get_evm_networks(self) -> List[ChainType]:
        """Get list of EVM-compatible networks."""
        return [chain for chain in self.networks.keys() if chain != ChainType.SOLANA]
    
    def get_network_names(self) -> Dict[ChainType, str]:
        """Get mapping of chain types to network names."""
        return {chain: network.name for chain, network in self.networks.items()}
    
    def is_network_supported(self, chain_type: ChainType) -> bool:
        """Check if a network is supported."""
        return chain_type in self.networks
    
    def get_rpc_url(self, chain_type: ChainType) -> Optional[str]:
        """Get RPC URL for a specific network."""
        network = self.get_network(chain_type)
        return network.rpc_url if network else None
    
    def get_explorer_url(self, chain_type: ChainType) -> Optional[str]:
        """Get explorer URL for a specific network."""
        network = self.get_network(chain_type)
        return network.explorer_url if network else None


# Global instance
multi_chain_config = MultiChainConfig()


def get_network_config(chain_type: ChainType) -> Optional[NetworkConfig]:
    """Get network configuration for a specific chain type."""
    return multi_chain_config.get_network(chain_type)


def get_supported_networks() -> List[ChainType]:
    """Get list of supported network types."""
    return multi_chain_config.get_supported_networks()


def is_network_supported(chain_type: ChainType) -> bool:
    """Check if a network is supported."""
    return multi_chain_config.is_network_supported(chain_type)
