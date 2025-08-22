"""
Multi-Chain Blockchain Service

Unified service for interacting with multiple blockchain networks including
Ethereum, Polygon, BSC, Arbitrum, Optimism, and Solana.
"""
import asyncio
import aiohttp
from typing import Dict, Optional, List, Any, Union
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.exceptions import Web3Exception
import json
import logging
import time
import os

from core.multi_chain_config import (
    ChainType, 
    NetworkConfig, 
    multi_chain_config,
    get_network_config
)

logger = logging.getLogger(__name__)


class MultiChainService:
    """Service for interacting with multiple blockchain networks."""
    
    def __init__(self):
        self.web3_instances: Dict[ChainType, Web3] = {}
        self.sessions: Dict[ChainType, aiohttp.ClientSession] = {}
        self.connection_status: Dict[ChainType, bool] = {}
        # Don't initialize connections in constructor - will be done lazily
    
    async def _initialize_connections_async(self):
        """Initialize Web3 connections asynchronously without blocking."""
        for chain_type in multi_chain_config.get_supported_networks():
            try:
                network_config = get_network_config(chain_type)
                if not network_config or not network_config.rpc_url:
                    logger.warning(f"No RPC URL configured for {chain_type}")
                    continue
                
                # Initialize Web3 for EVM chains
                if chain_type != ChainType.SOLANA:
                    await self._init_web3_connection_async(chain_type, network_config)
                else:
                    # Solana will be handled separately
                    self.connection_status[chain_type] = False
                    
            except Exception as e:
                logger.error(f"Failed to initialize {chain_type}: {e}")
                self.connection_status[chain_type] = False
    
    def _initialize_connections(self):
        """Initialize Web3 connections for all supported networks."""
        for chain_type in multi_chain_config.get_supported_networks():
            try:
                network_config = get_network_config(chain_type)
                if not network_config or not network_config.rpc_url:
                    logger.warning(f"No RPC URL configured for {chain_type}")
                    continue
                
                # Initialize Web3 for EVM chains
                if chain_type != ChainType.SOLANA:
                    self._init_web3_connection(chain_type, network_config)
                else:
                    # Solana will be handled separately
                    self.connection_status[chain_type] = False
                    
            except Exception as e:
                logger.error(f"Failed to initialize {chain_type}: {e}")
                self.connection_status[chain_type] = False
    
    def _init_web3_connection(self, chain_type: ChainType, network_config: NetworkConfig):
        """Initialize Web3 connection for an EVM chain."""
        # Try primary RPC URL first, then fallback if available
        rpc_urls = [network_config.rpc_url]
        
        # Add fallback URLs if they exist in environment
        fallback_key = f"{chain_type.upper()}_RPC_URL_ALT"
        fallback_url = os.getenv(fallback_key)
        if fallback_url:
            rpc_urls.append(fallback_url)
        
        # Try each RPC URL
        for rpc_url in rpc_urls:
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 30}))
                
                # Inject POA middleware for chains that need it
                if chain_type in [ChainType.POLYGON, ChainType.BSC, ChainType.AVALANCHE, ChainType.FANTOM]:
                    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
                
                # Test connection with retry logic
                max_retries = 3
                retry_delay = 2  # seconds
                
                for attempt in range(max_retries):
                    try:
                        # Test connection
                        if w3.is_connected():
                            # Double-check with a simple RPC call
                            chain_id = w3.eth.chain_id
                            block_number = w3.eth.block_number
                            
                            self.web3_instances[chain_type] = w3
                            self.connection_status[chain_type] = True
                            logger.info(f"Connected to {chain_type} via {rpc_url} (Chain ID: {chain_id}, Block: {block_number})")
                            return
                        else:
                            if attempt < max_retries - 1:
                                logger.debug(f"Connection attempt {attempt + 1} failed for {chain_type} via {rpc_url}, retrying in {retry_delay}s...")
                                time.sleep(retry_delay)
                            else:
                                logger.debug(f"Failed to connect to {chain_type} via {rpc_url} after {max_retries} attempts")
                                
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.debug(f"Connection attempt {attempt + 1} failed for {chain_type} via {rpc_url}: {e}, retrying...")
                            time.sleep(retry_delay)
                        else:
                            logger.debug(f"All connection attempts failed for {chain_type} via {rpc_url}: {e}")
                
            except Exception as e:
                logger.debug(f"Error initializing {chain_type} via {rpc_url}: {e}")
                continue
        
        # If we get here, all RPC URLs failed
        logger.warning(f"Failed to connect to {chain_type} via all available RPC URLs")
        self.connection_status[chain_type] = False
    
    async def _init_web3_connection_async(self, chain_type: ChainType, network_config: NetworkConfig):
        """Initialize Web3 connection for an EVM chain asynchronously."""
        # Try primary RPC URL first, then fallback if available
        rpc_urls = [network_config.rpc_url]
        
        # Add fallback URLs if they exist in environment
        fallback_key = f"{chain_type.upper()}_RPC_URL_ALT"
        fallback_url = os.getenv(fallback_key)
        if fallback_url:
            rpc_urls.append(fallback_url)
        
        # Try each RPC URL
        for rpc_url in rpc_urls:
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 30}))
                
                # Inject POA middleware for chains that need it
                if chain_type in [ChainType.POLYGON, ChainType.BSC, ChainType.AVALANCHE, ChainType.FANTOM]:
                    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
                
                # Test connection with retry logic
                max_retries = 3
                retry_delay = 2  # seconds
                
                for attempt in range(max_retries):
                    try:
                        # Test connection
                        if w3.is_connected():
                            # Double-check with a simple RPC call
                            chain_id = w3.eth.chain_id
                            block_number = w3.eth.block_number
                            
                            self.web3_instances[chain_type] = w3
                            self.connection_status[chain_type] = True
                            logger.info(f"Connected to {chain_type} via {rpc_url} (Chain ID: {chain_id}, Block: {block_number})")
                            return
                        else:
                            if attempt < max_retries - 1:
                                logger.debug(f"Connection attempt {attempt + 1} failed for {chain_type} via {rpc_url}, retrying in {retry_delay}s...")
                                await asyncio.sleep(retry_delay)
                            else:
                                logger.debug(f"Failed to connect to {chain_type} via {rpc_url} after {max_retries} attempts")
                                
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.debug(f"Connection attempt {attempt + 1} failed for {chain_type} via {rpc_url}: {e}, retrying...")
                            await asyncio.sleep(retry_delay)
                        else:
                            logger.debug(f"All connection attempts failed for {chain_type} via {rpc_url}: {e}")
                
            except Exception as e:
                logger.debug(f"Error initializing {chain_type} via {rpc_url}: {e}")
                continue
        
        # If we get here, all RPC URLs failed
        logger.warning(f"Failed to connect to {chain_type} via all available RPC URLs")
        self.connection_status[chain_type] = False
    
    async def get_connection_status(self) -> Dict[ChainType, bool]:
        """Get connection status for all networks."""
        return self.connection_status.copy()
    
    async def test_connection(self, chain_type: ChainType) -> bool:
        """Test connection to a specific network."""
        try:
            if chain_type == ChainType.SOLANA:
                return await self._test_solana_connection()
            else:
                return await self._test_evm_connection(chain_type)
        except Exception as e:
            logger.error(f"Connection test failed for {chain_type}: {e}")
            return False
    
    async def test_connection_by_name(self, network_name: str) -> bool:
        """Test connection to a network by name string."""
        try:
            # Convert network name to ChainType enum
            network_mapping = {
                'ethereum': ChainType.ETHEREUM,
                'polygon': ChainType.POLYGON,
                'bsc': ChainType.BSC,
                'arbitrum': ChainType.ARBITRUM,
                'optimism': ChainType.OPTIMISM,
                'base': ChainType.BASE,
                'avalanche': ChainType.AVALANCHE,
                'fantom': ChainType.FANTOM,
                'solana': ChainType.SOLANA
            }
            
            if network_name.lower() not in network_mapping:
                logger.error(f"Unknown network: {network_name}")
                return False
            
            chain_type = network_mapping[network_name.lower()]
            return await self.test_connection(chain_type)
            
        except Exception as e:
            logger.error(f"Connection test failed for {network_name}: {e}")
            return False
    
    async def _test_evm_connection(self, chain_type: ChainType) -> bool:
        """Test connection to an EVM network."""
        if chain_type not in self.web3_instances:
            return False
        
        try:
            w3 = self.web3_instances[chain_type]
            # Test with a simple call
            block_number = w3.eth.block_number
            chain_id = w3.eth.chain_id
            logger.info(f"{chain_type} connection test: Block {block_number}, Chain ID {chain_id}")
            return True
        except Exception as e:
            logger.error(f"EVM connection test failed for {chain_type}: {e}")
            return False
    
    async def _test_solana_connection(self) -> bool:
        """Test connection to Solana network."""
        try:
            network_config = get_network_config(ChainType.SOLANA)
            if not network_config:
                return False
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    network_config.rpc_url,
                    json={"jsonrpc": "2.0", "id": 1, "method": "getHealth"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "result" in data and data["result"] == "ok":
                            logger.info("Solana connection test successful")
                            self.connection_status[ChainType.SOLANA] = True
                            return True
            
            return False
        except Exception as e:
            logger.error(f"Solana connection test failed: {e}")
            return False
    
    async def get_block_number(self, chain_type: ChainType) -> Optional[int]:
        """Get current block number for a network."""
        try:
            if chain_type == ChainType.SOLANA:
                return await self._get_solana_block_number()
            else:
                return await self._get_evm_block_number(chain_type)
        except Exception as e:
            logger.error(f"Failed to get block number for {chain_type}: {e}")
            return None
    
    async def _get_evm_block_number(self, chain_type: ChainType) -> Optional[int]:
        """Get block number for an EVM network."""
        if chain_type not in self.web3_instances:
            return None
        
        try:
            w3 = self.web3_instances[chain_type]
            return w3.eth.block_number
        except Exception as e:
            logger.error(f"Failed to get EVM block number for {chain_type}: {e}")
            return None
    
    async def _get_solana_block_number(self) -> Optional[int]:
        """Get block number for Solana."""
        try:
            network_config = get_network_config(ChainType.SOLANA)
            if not network_config:
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    network_config.rpc_url,
                    json={"jsonrpc": "2.0", "id": 1, "method": "getSlot"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "result" in data:
                            return data["result"]
            return None
        except Exception as e:
            logger.error(f"Failed to get Solana block number: {e}")
            return None
    
    async def get_balance(self, chain_type: ChainType, address: str) -> Optional[Dict[str, Any]]:
        """Get native token balance for an address."""
        try:
            if chain_type == ChainType.SOLANA:
                return await self._get_solana_balance(address)
            else:
                return await self._get_evm_balance(chain_type, address)
        except Exception as e:
            logger.error(f"Failed to get balance for {chain_type}: {e}")
            return None
    
    async def _get_evm_balance(self, chain_type: ChainType, address: str) -> Optional[Dict[str, Any]]:
        """Get native token balance for an EVM address."""
        if chain_type not in self.web3_instances:
            return None
        
        try:
            w3 = self.web3_instances[chain_type]
            network_config = get_network_config(chain_type)
            
            # Validate address
            if not w3.is_address(address):
                logger.error(f"Invalid address: {address}")
                return None
            
            balance_wei = w3.eth.get_balance(address)
            balance_decimal = w3.from_wei(balance_wei, 'ether')
            
            return {
                "address": address,
                "chain": chain_type.value,
                "balance_wei": balance_wei,
                "balance_decimal": float(balance_decimal),
                "symbol": network_config.symbol if network_config else "ETH",
                "decimals": network_config.decimals if network_config else 18
            }
        except Exception as e:
            logger.error(f"Failed to get EVM balance for {chain_type}: {e}")
            return None
    
    async def _get_solana_balance(self, address: str) -> Optional[Dict[str, Any]]:
        """Get SOL balance for a Solana address."""
        try:
            network_config = get_network_config(ChainType.SOLANA)
            if not network_config:
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    network_config.rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getBalance",
                        "params": [address]
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "result" in data and "value" in data["result"]:
                            balance_lamports = data["result"]["value"]
                            balance_sol = balance_lamports / (10 ** network_config.decimals)
                            
                            return {
                                "address": address,
                                "chain": "solana",
                                "balance_lamports": balance_lamports,
                                "balance_decimal": balance_sol,
                                "symbol": "SOL",
                                "decimals": 9
                            }
            return None
        except Exception as e:
            logger.error(f"Failed to get Solana balance: {e}")
            return None
    
    async def get_transaction(self, chain_type: ChainType, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction details."""
        try:
            if chain_type == ChainType.SOLANA:
                return await self._get_solana_transaction(tx_hash)
            else:
                return await self._get_evm_transaction(chain_type, tx_hash)
        except Exception as e:
            logger.error(f"Failed to get transaction for {chain_type}: {e}")
            return None
    
    async def _get_evm_transaction(self, chain_type: ChainType, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction details for an EVM network."""
        if chain_type not in self.web3_instances:
            return None
        
        try:
            w3 = self.web3_instances[chain_type]
            tx = w3.eth.get_transaction(tx_hash)
            
            if tx:
                return {
                    "chain": chain_type.value,
                    "hash": tx_hash,
                    "from": tx.get('from'),
                    "to": tx.get('to'),
                    "value": tx.get('value'),
                    "gas": tx.get('gas'),
                    "gas_price": tx.get('gasPrice'),
                    "nonce": tx.get('nonce'),
                    "block_number": tx.get('blockNumber'),
                    "input": tx.get('input')
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get EVM transaction for {chain_type}: {e}")
            return None
    
    async def _get_solana_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction details for Solana."""
        try:
            network_config = get_network_config(ChainType.SOLANA)
            if not network_config:
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    network_config.rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTransaction",
                        "params": [
                            tx_hash,
                            {"encoding": "json", "maxSupportedTransactionVersion": 0}
                        ]
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "result" in data and data["result"]:
                            tx = data["result"]
                            return {
                                "chain": "solana",
                                "hash": tx_hash,
                                "slot": tx.get("slot"),
                                "block_time": tx.get("blockTime"),
                                "fee": tx.get("meta", {}).get("fee"),
                                "status": tx.get("meta", {}).get("err"),
                                "instructions": tx.get("transaction", {}).get("message", {}).get("instructions", [])
                            }
            return None
        except Exception as e:
            logger.error(f"Failed to get Solana transaction: {e}")
            return None
    
    async def get_network_info(self, chain_type: ChainType) -> Optional[Dict[str, Any]]:
        """Get network information and statistics."""
        try:
            network_config = get_network_config(chain_type)
            if not network_config:
                return None
            
            # Get current block number
            block_number = await self.get_block_number(chain_type)
            
            info = {
                "chain_type": chain_type.value,
                "name": network_config.name,
                "symbol": network_config.symbol,
                "chain_id": network_config.chain_id,
                "rpc_url": network_config.rpc_url,
                "explorer_url": network_config.explorer_url,
                "native_currency": network_config.native_currency,
                "decimals": network_config.decimals,
                "block_time": network_config.block_time,
                "supports_eip1559": network_config.supports_eip1559,
                "current_block": block_number,
                "connected": self.connection_status.get(chain_type, False)
            }
            
            return info
        except Exception as e:
            logger.error(f"Failed to get network info for {chain_type}: {e}")
            return None
    
    async def get_all_networks_info(self) -> List[Dict[str, Any]]:
        """Get information for all supported networks."""
        networks_info = []
        
        for chain_type in multi_chain_config.get_supported_networks():
            try:
                info = await self.get_network_info(chain_type)
                if info:
                    networks_info.append(info)
            except Exception as e:
                logger.error(f"Failed to get info for {chain_type}: {e}")
        
        return networks_info
    
    async def close_connections(self):
        """Close all network connections."""
        for chain_type in self.web3_instances:
            try:
                # Web3 connections are automatically managed
                pass
            except Exception as e:
                logger.error(f"Error closing {chain_type} connection: {e}")
        
        for session in self.sessions.values():
            try:
                if not session.closed:
                    await session.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")


# Global instance - lazy initialization
_multi_chain_service = None


async def get_multi_chain_service() -> MultiChainService:
    """Get the global multi-chain service instance with lazy initialization."""
    global _multi_chain_service
    
    if _multi_chain_service is None:
        _multi_chain_service = MultiChainService()
        # Initialize connections asynchronously without blocking
        asyncio.create_task(_multi_chain_service._initialize_connections_async())
    
    return _multi_chain_service


async def close_multi_chain_service():
    """Close the global multi-chain service."""
    global _multi_chain_service
    
    if _multi_chain_service:
        await _multi_chain_service.close_connections()
        _multi_chain_service = None
