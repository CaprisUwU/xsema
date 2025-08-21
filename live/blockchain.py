"""
Blockchain Connection Manager

This module provides a robust Web3 connection with retry logic, middleware support,
and event listening capabilities for NFT-related blockchain interactions.
"""
import os
import time
import json
import asyncio
from typing import Dict, List, Optional, Any, Callable, Awaitable
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.exceptions import ContractLogicError, BlockNotFound, TimeExhausted
from web3.contract import Contract
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Common ERC-721 and ERC-1155 ABI snippets for NFT transfers
ERC721_TRANSFER_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": True, "name": "tokenId", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    }
]

ERC1155_TRANSFER_SINGLE_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "operator", "type": "address"},
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "id", "type": "uint256"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "TransferSingle",
        "type": "event"
    }
]

class Web3Connection:
    """Manages Web3 connections and blockchain event listening."""
    
    def __init__(self, rpc_url: Optional[str] = None):
        """Initialize the Web3 connection manager.
        
        Args:
            rpc_url: Optional custom RPC URL. If not provided, will use WEB3_PROVIDER_URI env var.
        """
        self.rpc_url = rpc_url or os.getenv('WEB3_PROVIDER_URI', 'https://mainnet.infura.io/v3/YOUR-PROJECT-ID')
        self.w3 = None
        self.connection_retries = 5
        self.retry_delay = 5
        self.max_reorg_blocks = 12  # Number of blocks to account for potential chain reorganizations
        self.last_processed_block = 0
        
    async def connect(self) -> Web3:
        """Establish Web3 connection with retry logic.
        
        Returns:
            Web3: Connected Web3 instance
            
        Raises:
            ConnectionError: If connection cannot be established after retries
        """
        for attempt in range(self.connection_retries):
            try:
                # Use async HTTP provider if available, otherwise fall back to sync
                try:
                    from web3 import AsyncHTTPProvider
                    provider = AsyncHTTPProvider(self.rpc_url)
                    self.w3 = Web3(provider, modules={'eth': (AsyncEth,)}, middlewares=[])
                except ImportError:
                    self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
                
                if not self.w3.is_connected():
                    raise ConnectionError("Failed to connect to Web3 provider")
                    
                # Add middleware for PoA chains and other configurations
                await self._add_middleware()
                
                chain_id = await self.w3.eth.chain_id
                logger.info(f"Connected to Web3 provider (Chain ID: {chain_id})")
                return self.w3
                
            except Exception as e:
                if attempt == self.connection_retries - 1:
                    logger.error(f"Failed to connect after {self.connection_retries} attempts: {e}")
                    raise ConnectionError(f"Failed to connect to Web3 provider: {e}")
                    
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {self.retry_delay} seconds...")
                await asyncio.sleep(self.retry_delay)
    
    async def _add_middleware(self):
        """Add necessary middleware to Web3 instance."""
        # Add PoA middleware for chains like Polygon, BSC, etc.
        chain_id = await self.w3.eth.chain_id
        
        # Known PoA chain IDs
        poa_chains = {
            137: 'Polygon Mainnet',
            80001: 'Mumbai Testnet',
            56: 'BSC Mainnet',
            97: 'BSC Testnet',
            100: 'xDAI Chain',
            250: 'Fantom Opera',
            4002: 'Fantom Testnet',
            43114: 'Avalanche C-Chain',
            43113: 'Avalanche Fuji Testnet'
        }
        
        if chain_id in poa_chains:
            logger.info(f"Adding PoA middleware for {poa_chains[chain_id]} (Chain ID: {chain_id})")
            # Add POA middleware for compatibility with POA networks
            self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    
    async def get_contract(self, address: str, abi: Optional[list] = None) -> Contract:
        """Get contract instance with error handling.
        
        Args:
            address: Contract address
            abi: Optional ABI. If not provided, will try to determine from standard interfaces.
            
        Returns:
            Contract: Web3 contract instance
            
        Raises:
            ValueError: If contract address is invalid
            ContractLogicError: If there's an issue with the contract
        """
        if not self.w3 or not self.w3.is_connected():
            await self.connect()
            
        try:
            address = self.w3.to_checksum_address(address)
            
            # If no ABI provided, try to determine from standard interfaces
            if not abi:
                # Try ERC-721 first, then ERC-1155
                try:
                    contract = self.w3.eth.contract(address=address, abi=ERC721_TRANSFER_ABI)
                    # Simple check to see if it's an ERC-721 contract
                    await contract.functions.supportsInterface('0x80ac58cd').call()
                    logger.debug(f"Detected ERC-721 contract at {address}")
                    return contract
                except:
                    try:
                        contract = self.w3.eth.contract(address=address, abi=ERC1155_TRANSFER_SINGLE_ABI)
                        # Check if it's an ERC-1155 contract
                        await contract.functions.supportsInterface('0xd9b67a26').call()
                        logger.debug(f"Detected ERC-1155 contract at {address}")
                        return contract
                    except:
                        logger.warning(f"Could not determine contract standard for {address}, using minimal ABI")
                        return self.w3.eth.contract(address=address, abi=[])
            
            return self.w3.eth.contract(address=address, abi=abi)
            
        except ValueError as e:
            logger.error(f"Invalid contract address {address}: {e}")
            raise
        except ContractLogicError as e:
            logger.error(f"Contract error for {address}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting contract {address}: {e}")
            raise
    
    async def get_latest_block(self) -> int:
        """Get the latest block number with error handling.
        
        Returns:
            int: Latest block number
            
        Raises:
            ConnectionError: If unable to fetch block number
        """
        try:
            return await self.w3.eth.block_number
        except Exception as e:
            logger.error(f"Error getting latest block: {e}")
            raise ConnectionError(f"Failed to get latest block: {e}")
    
    async def process_block_events(self, from_block: int, to_block: int, 
                                 event_abis: List[dict], 
                                 addresses: Optional[List[str]] = None) -> List[dict]:
        """Process events from multiple contracts across a block range.
        
        Args:
            from_block: Starting block number (inclusive)
            to_block: Ending block number (inclusive)
            event_abis: List of event ABIs to filter for
            addresses: Optional list of contract addresses to filter by
            
        Returns:
            List[dict]: List of decoded events
        """
        if not self.w3 or not self.w3.is_connected():
            await self.connect()
        
        try:
            # Create filter parameters
            filter_params = {
                'fromBlock': from_block,
                'toBlock': to_block,
                'topics': [abi[0]['topics'][0] for abi in event_abis if abi and abi[0].get('topics')]
            }
            
            if addresses:
                filter_params['address'] = addresses
            
            # Get logs
            logs = await self.w3.eth.get_logs(filter_params)
            
            # Process logs into events
            events = []
            for log in logs:
                try:
                    # Find matching ABI for this event
                    for abi in event_abis:
                        if abi[0].get('topics') and abi[0]['topics'][0] == log['topics'][0]:
                            # Decode the log
                            contract = self.w3.eth.contract(address=log['address'], abi=abi)
                            event = contract.events[abi[0]['name']]().process_log(log)
                            events.append({
                                'event': event['event'],
                                'args': dict(event['args']),
                                'address': log['address'],
                                'blockNumber': log['blockNumber'],
                                'transactionHash': log['transactionHash'].hex(),
                                'logIndex': log['logIndex'],
                                'timestamp': datetime.utcnow().isoformat() + 'Z'
                            })
                            break
                except Exception as e:
                    logger.warning(f"Error processing log: {e}")
                    continue
            
            return events
            
        except Exception as e:
            logger.error(f"Error processing block events: {e}")
            raise
    
    async def listen_for_events(self, callback: Callable[[dict], Awaitable[None]], 
                              event_abis: List[dict],
                              poll_interval: int = 2,
                              max_blocks_per_poll: int = 2000,
                              addresses: Optional[List[str]] = None):
        """Continuously listen for events and call the callback when they occur.
        
        Args:
            callback: Async function to call with each event
            event_abis: List of event ABIs to listen for
            poll_interval: How often to poll for new blocks (seconds)
            max_blocks_per_poll: Maximum number of blocks to process in one poll
            addresses: Optional list of contract addresses to filter by
            
        Returns:
            Never returns unless an unrecoverable error occurs
        """
        if not self.w3 or not self.w3.is_connected():
            await self.connect()
        
        # Start from current block minus some blocks to handle reorgs
        current_block = await self.get_latest_block()
        self.last_processed_block = max(0, current_block - self.max_reorg_blocks)
        
        logger.info(f"Starting event listener from block {self.last_processed_block}")
        
        while True:
            try:
                # Get latest block
                latest_block = await self.get_latest_block()
                
                # Determine block range to process
                to_block = min(latest_block, self.last_processed_block + max_blocks_per_poll)
                
                if to_block > self.last_processed_block:
                    # Process events in this block range
                    logger.debug(f"Processing blocks {self.last_processed_block + 1} to {to_block}")
                    events = await self.process_block_events(
                        from_block=self.last_processed_block + 1,
                        to_block=to_block,
                        event_abis=event_abis,
                        addresses=addresses
                    )
                    
                    # Process each event
                    for event in events:
                        try:
                            await callback(event)
                        except Exception as e:
                            logger.error(f"Error in event callback: {e}")
                    
                    # Update last processed block
                    self.last_processed_block = to_block
                else:
                    # No new blocks, wait before polling again
                    await asyncio.sleep(poll_interval)
                
            except (BlockNotFound, TimeExhausted) as e:
                # Handle chain reorganizations
                logger.warning(f"Chain reorganization detected: {e}")
                self.last_processed_block = max(0, self.last_processed_block - self.max_reorg_blocks)
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
                await asyncio.sleep(poll_interval)

# Async HTTP provider for Web3.py
class AsyncHTTPProvider(Web3.HTTPProvider):
    """Async HTTP provider for Web3.py"""
    async def make_request(self, method, params):
        request_data = self.encode_rpc_request(method, params or [])
        raw_response = await self._make_post_request(
            self.endpoint_uri,
            request_data,
            self.get_request_kwargs()
        )
        response = self.decode_rpc_response(raw_response)
        return response
    
    async def _make_post_request(self, url, request_data, request_kwargs):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=request_data, **request_kwargs) as response:
                response.raise_for_status()
                return await response.text()

# Async Ethereum client
class AsyncEth:
    """Async Ethereum client for Web3.py"""
    def __init__(self, w3):
        self.w3 = w3
    
    async def get_logs(self, *args, **kwargs):
        return await self.w3.manager.coro_request('eth_getLogs', [kwargs])
    
    async def block_number(self):
        return await self.w3.manager.coro_request('eth_blockNumber', [])
    
    async def chain_id(self):
        return await self.w3.manager.coro_request('eth_chainId', [])


# Legacy function for backward compatibility
def get_web3():
    """Get Web3 instance for backward compatibility with existing code."""
    # Return a default Web3 instance using environment variables
    rpc_url = os.getenv('WEB3_PROVIDER_URI', 'https://mainnet.infura.io/v3/YOUR-PROJECT-ID')
    return Web3(Web3.HTTPProvider(rpc_url))