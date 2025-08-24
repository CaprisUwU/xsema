"""
XSEMA Blockchain Integration Module - Phase 4
Real blockchain API connections for live data
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BASE = "base"
    AVALANCHE = "avalanche"
    FANTOM = "fantom"
    SOLANA = "solana"

@dataclass
class BlockchainConfig:
    """Configuration for blockchain networks"""
    network: BlockchainNetwork
    rpc_url: str
    api_key: Optional[str] = None
    chain_id: Optional[int] = None
    block_time: Optional[int] = None
    enabled: bool = True

@dataclass
class NFTData:
    """Real NFT data structure"""
    token_id: str
    contract_address: str
    network: BlockchainNetwork
    name: str
    description: str
    image_url: str
    attributes: List[Dict[str, Any]]
    current_price: Optional[float] = None
    floor_price: Optional[float] = None
    last_sale_price: Optional[float] = None
    last_sale_date: Optional[datetime] = None
    rarity_score: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    holders_count: Optional[int] = None
    timestamp: datetime = None

class BlockchainIntegrationManager:
    """Manages real blockchain API connections"""
    
    def __init__(self):
        self.configs: Dict[BlockchainNetwork, BlockchainConfig] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, datetime] = {}
        self.cache_duration = timedelta(minutes=5)
        
        # Initialize configurations
        self._load_configurations()
    
    def _load_configurations(self):
        """Load blockchain configurations from environment"""
        # Ethereum configuration
        self.configs[BlockchainNetwork.ETHEREUM] = BlockchainConfig(
            network=BlockchainNetwork.ETHEREUM,
            rpc_url=os.getenv("ETHEREUM_RPC_URL", "https://mainnet.infura.io/v3/"),
            api_key=os.getenv("INFURA_API_KEY"),
            chain_id=1,
            block_time=12,
            enabled=bool(os.getenv("ETHEREUM_ENABLED", "true").lower() == "true")
        )
        
        # Polygon configuration
        self.configs[BlockchainNetwork.POLYGON] = BlockchainConfig(
            network=BlockchainNetwork.POLYGON,
            rpc_url=os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com/"),
            api_key=os.getenv("POLYGON_API_KEY"),
            chain_id=137,
            block_time=2,
            enabled=bool(os.getenv("POLYGON_ENABLED", "true").lower() == "true")
        )
        
        # BSC configuration
        self.configs[BlockchainNetwork.BSC] = BlockchainConfig(
            network=BlockchainNetwork.BSC,
            rpc_url=os.getenv("BSC_RPC_URL", "https://bsc-dataseed.binance.org/"),
            api_key=None,  # BSC public RPC
            chain_id=56,
            block_time=3,
            enabled=bool(os.getenv("BSC_ENABLED", "true").lower() == "true")
        )
        
        # Arbitrum configuration
        self.configs[BlockchainNetwork.ARBITRUM] = BlockchainConfig(
            network=BlockchainNetwork.ARBITRUM,
            rpc_url=os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc"),
            api_key=os.getenv("ARBITRUM_API_KEY"),
            chain_id=42161,
            block_time=1,
            enabled=bool(os.getenv("ARBITRUM_ENABLED", "true").lower() == "true")
        )
        
        # Optimism configuration
        self.configs[BlockchainNetwork.OPTIMISM] = BlockchainConfig(
            network=BlockchainNetwork.OPTIMISM,
            rpc_url=os.getenv("OPTIMISM_RPC_URL", "https://mainnet.optimism.io"),
            api_key=os.getenv("OPTIMISM_API_KEY"),
            chain_id=10,
            block_time=2,
            enabled=bool(os.getenv("OPTIMISM_ENABLED", "true").lower() == "true")
        )
        
        # Base configuration
        self.configs[BlockchainNetwork.BASE] = BlockchainConfig(
            network=BlockchainNetwork.BASE,
            rpc_url=os.getenv("BASE_RPC_URL", "https://mainnet.base.org"),
            api_key=os.getenv("BASE_API_KEY"),
            chain_id=8453,
            block_time=2,
            enabled=bool(os.getenv("BASE_ENABLED", "true").lower() == "true")
        )
        
        # Avalanche configuration
        self.configs[BlockchainNetwork.AVALANCHE] = BlockchainConfig(
            network=BlockchainNetwork.AVALANCHE,
            rpc_url=os.getenv("AVALANCHE_RPC_URL", "https://api.avax.network/ext/bc/C/rpc"),
            api_key=os.getenv("AVALANCHE_API_KEY"),
            chain_id=43114,
            block_time=2,
            enabled=bool(os.getenv("AVALANCHE_ENABLED", "true").lower() == "true")
        )
        
        # Fantom configuration
        self.configs[BlockchainNetwork.FANTOM] = BlockchainConfig(
            network=BlockchainNetwork.FANTOM,
            rpc_url=os.getenv("FANTOM_RPC_URL", "https://rpc.ftm.tools/"),
            api_key=os.getenv("FANTOM_API_KEY"),
            chain_id=250,
            block_time=1,
            enabled=bool(os.getenv("FANTOM_ENABLED", "true").lower() == "true")
        )
        
        # Solana configuration
        self.configs[BlockchainNetwork.SOLANA] = BlockchainConfig(
            network=BlockchainNetwork.SOLANA,
            rpc_url=os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"),
            api_key=os.getenv("SOLANA_API_KEY"),
            chain_id=None,  # Solana doesn't use chain IDs
            block_time=0.4,
            enabled=bool(os.getenv("SOLANA_ENABLED", "true").lower() == "true")
        )
        
        logger.info(f"Loaded {len([c for c in self.configs.values() if c.enabled])} enabled blockchain configurations")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": "XSEMA-Blockchain-Integration/2.0.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def test_connection(self, network: BlockchainNetwork) -> bool:
        """Test connection to a specific blockchain network"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        config = self.configs.get(network)
        if not config or not config.enabled:
            logger.warning(f"Network {network.value} not configured or disabled")
            return False
        
        try:
            if network == BlockchainNetwork.SOLANA:
                # Solana uses different RPC format
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getHealth"
                }
            else:
                # Ethereum-compatible RPC
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "eth_blockNumber",
                    "params": []
                }
            
            async with self.session.post(
                config.rpc_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data or "error" not in data:
                        logger.info(f"✅ Successfully connected to {network.value}")
                        return True
                    else:
                        logger.warning(f"❌ RPC error from {network.value}: {data.get('error')}")
                        return False
                else:
                    logger.warning(f"❌ HTTP {response.status} from {network.value}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Connection test failed for {network.value}: {e}")
            return False
    
    async def test_all_connections(self) -> Dict[BlockchainNetwork, bool]:
        """Test connections to all enabled blockchain networks"""
        results = {}
        
        for network, config in self.configs.items():
            if config.enabled:
                logger.info(f"Testing connection to {network.value}...")
                results[network] = await self.test_connection(network)
                await asyncio.sleep(0.5)  # Rate limiting
        
        return results
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get status of all blockchain networks"""
        status = {}
        
        for network, config in self.configs.items():
            status[network.value] = {
                "enabled": config.enabled,
                "rpc_url": config.rpc_url,
                "chain_id": config.chain_id,
                "block_time": config.block_time,
                "has_api_key": bool(config.api_key)
            }
        
        return status
    
    async def get_latest_block(self, network: BlockchainNetwork) -> Optional[int]:
        """Get the latest block number for a network"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        config = self.configs.get(network)
        if not config or not config.enabled:
            return None
        
        try:
            if network == BlockchainNetwork.SOLANA:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getSlot"
                }
            else:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "eth_blockNumber",
                    "params": []
                }
            
            async with self.session.post(
                config.rpc_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data:
                        if network == BlockchainNetwork.SOLANA:
                            return int(data["result"])
                        else:
                            return int(data["result"], 16)
                    else:
                        logger.warning(f"RPC error getting block number for {network.value}: {data.get('error')}")
                        return None
                else:
                    logger.warning(f"HTTP {response.status} getting block number for {network.value}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting latest block for {network.value}: {e}")
            return None

# Global instance
blockchain_manager = BlockchainIntegrationManager()

async def test_blockchain_connections():
    """Test all blockchain connections"""
    async with blockchain_manager as manager:
        results = await manager.test_all_connections()
        
        print("\n🔗 Blockchain Connection Test Results:")
        print("=" * 50)
        
        for network, success in results.items():
            status = "✅ CONNECTED" if success else "❌ FAILED"
            print(f"{network.upper():<15} {status}")
        
        print(f"\n📊 Summary: {sum(results.values())}/{len(results)} networks connected")
        return results

if __name__ == "__main__":
    # Test the blockchain integration
    asyncio.run(test_blockchain_connections())
