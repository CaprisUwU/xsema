"""
Blockchain Event Listener

This module provides real-time monitoring of blockchain events, specifically focused on
NFT transfers and related activities. It processes blockchain data and broadcasts events
to connected WebSocket clients.
"""
import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime

from web3 import Web3
from web3.types import BlockData, TxReceipt, LogReceipt, ChecksumAddress
from web3.contract import Contract

from .blockchain import Web3Connection
from .ws_manager import manager

logger = logging.getLogger(__name__)

# Common NFT contract addresses
COMMON_NFT_CONTRACTS = {
    # Ethereum Mainnet
    'ethereum': {
        'bayc': '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D',
        'mayc': '0x60E4d786628Fea6478F785A6d7e704777c86a7c6',
        'doodles': '0x8a90CAb2b38dba80c64b7734e58Ee1dB38B8992e',
        'azuki': '0xED5AF388653567Af2F388E6224dC7C4b3241C544',
        'clonex': '0x49cF6f5d44E70224e2E23fD2dC2558beEaB6Bf86',
    },
    # Polygon
    'polygon': {
        'aavegotchi': '0x385Eeac5cB85A38A9a07A70c73e0a3271CfB54A7',
    }
}

class BlockchainEventListener:
    """Listens to blockchain events and broadcasts them to WebSocket clients."""
    
    def __init__(self, rpc_url: Optional[str] = None, 
                contract_addresses: Optional[List[str]] = None):
        """Initialize the event listener.
        
        Args:
            rpc_url: Optional custom RPC URL. Uses WEB3_PROVIDER_URI env var if not provided.
            contract_addresses: Optional list of contract addresses to monitor.
                               If not provided, uses a default list of popular NFT contracts.
        """
        self.web3_conn = Web3Connection(rpc_url)
        self.w3 = None
        self.contracts: Dict[str, Contract] = {}
        self.running = False
        self.last_processed_block = 0
        self.poll_interval = 2.0
        self.max_reorg_blocks = 12
        self.contract_addresses = contract_addresses or self._get_default_contracts()
        self.event_handlers = {
            'Transfer': self._handle_transfer_event,
        }
        
    async def start(self, from_block: Optional[int] = None):
        """Start listening for blockchain events"""
        if self.running:
            logger.warning("Listener is already running")
            return
            
        self.running = True
        logger.info("Starting blockchain event listener")
        
        # Initialize last processed block
        if from_block is None:
            self.last_processed_block = self.w3.eth.block_number - 1  # Start from previous block
        else:
            self.last_processed_block = from_block - 1  # Process from the next block
            
        logger.info(f"Starting from block {self.last_processed_block + 1}")
        
        while self.running:
            try:
                await self._process_new_blocks()
            except Exception as e:
                logger.error(f"Error in event loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def stop(self):
        """Stop the event listener"""
        self.running = False
        logger.info("Stopping blockchain event listener")
        
    async def _process_new_blocks(self):
        """Process new blocks since last check"""
        try:
            current_block = self.w3.eth.block_number
            
            # Handle chain reorgs
            if self.last_processed_block >= current_block:
                await asyncio.sleep(self.poll_interval)
                return
                
            # Process blocks in batches
            start_block = self.last_processed_block + 1
            end_block = min(current_block, start_block + 99)  # Process max 100 blocks at once
            
            logger.debug(f"Processing blocks {start_block} to {end_block}")
            
            # Get all blocks in the range
            blocks = await self._get_blocks_in_range(start_block, end_block)
            
            # Process transactions in each block
            for block in blocks:
                await self._process_block(block)
                
            # Update last processed block
            self.last_processed_block = end_block
            
        except Exception as e:
            logger.error(f"Error processing blocks: {e}")
            raise
            
    async def _get_blocks_in_range(self, start_block: int, end_block: int) -> List[BlockData]:
        """Get blocks in the specified range"""
        blocks = []
        for block_num in range(start_block, end_block + 1):
            try:
                block = self.w3.eth.get_block(block_num, full_transactions=True)
                blocks.append(block)
            except Exception as e:
                logger.error(f"Error getting block {block_num}: {e}")
                raise
        return blocks
        
    async def _process_block(self, block: BlockData):
        """Process a single block and its transactions"""
        logger.debug(f"Processing block {block.number} with {len(block.transactions)} transactions")
        
        for tx in block.transactions:
            try:
                await self._process_transaction(tx, block)
            except Exception as e:
                logger.error(f"Error processing transaction {tx.hash.hex()}: {e}")
                continue
                
    async def _process_transaction(self, tx, block: BlockData):
        """Process a single transaction"""
        # Skip contract creation transactions
        if not tx.to:
            return
            
        # Process NFT transfers
        if self._is_nft_transfer(tx):
            await self._handle_nft_transfer(tx, block)
            
    def _is_nft_transfer(self, tx) -> bool:
        """Check if transaction is an NFT transfer"""
        # ERC-721 Transfer event signature
        transfer_signature = self.w3.keccak(text="Transfer(address,address,uint256)").hex()
        
        # Check if it's a contract interaction
        if not tx.input or tx.input == '0x':
            return False
            
        # Check if it's a transfer to a known NFT contract
        # You can add more contract addresses here
        nft_contracts = [
            "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",  # BAYC
            "0x60E4d786628Fea6478F785A6d7e704777c86a7c6",  # MAYC
            # Add more contract addresses as needed
        ]
        
        return tx.to and tx.to.lower() in [addr.lower() for addr in nft_contracts]
        
    async def _handle_nft_transfer(self, tx, block: BlockData):
        """Handle an NFT transfer event"""
        try:
            # Get transaction receipt to check for events
            receipt = self.w3.eth.get_transaction_receipt(tx.hash)
            
            # Process transfer events
            transfer_events = self._parse_transfer_events(receipt)
            
            for event in transfer_events:
                await self._process_transfer_event(event, tx, block, receipt)
                
        except Exception as e:
            logger.error(f"Error handling NFT transfer: {e}")
            
    def _parse_transfer_events(self, receipt: TxReceipt) -> List[dict]:
        """Parse transfer events from transaction receipt"""
        transfer_events = []
        transfer_topic = self.w3.keccak(text="Transfer(address,address,uint256)").hex()
        
        for log in receipt.logs:
            if not log.topics or len(log.topics) < 3:
                continue
                
            if log.topics[0].hex() == transfer_topic:
                try:
                    from_address = '0x' + log.topics[1].hex()[-40:]
                    to_address = '0x' + log.topics[2].hex()[-40:]
                    token_id = int(log.topics[3].hex(), 16) if len(log.topics) > 3 else None
                    
                    if not token_id and log.data != '0x':
                        try:
                            token_id = int(log.data.hex(), 16)
                        except:
                            pass
                            
                    transfer_events.append({
                        'from': from_address,
                        'to': to_address,
                        'tokenId': token_id,
                        'contract': log.address,
                        'transactionHash': receipt.transactionHash.hex(),
                        'blockNumber': receipt.blockNumber,
                        'logIndex': log.logIndex
                    })
                except Exception as e:
                    logger.error(f"Error parsing transfer event: {e}")
                    continue
                    
        return transfer_events
        
    async def _process_transfer_event(self, event: dict, tx, block: BlockData, receipt: TxReceipt):
        """Process a single transfer event and broadcast to WebSocket clients."""
        try:
            # Get token metadata
            token_metadata = await self._get_token_metadata(event['contract'], event['tokenId'])
            
            # Get price if available
            price = await self._get_transfer_price(tx, receipt)
            
            # Format the event data
            event_data = self._format_transfer_event(
                event=event,
                tx=tx,
                block=block,
                receipt=receipt,
                token_metadata=token_metadata,
                price=price
            )
            
            # Broadcast to WebSocket clients
            await self._broadcast_event('nft_transfer', event_data)
            
        except Exception as e:
            logger.error(f"Error processing transfer event: {e}", exc_info=True)
    
    def _format_transfer_event(self, event: dict, tx, block: BlockData, 
                             receipt: TxReceipt, token_metadata: dict, price: Optional[str]) -> dict:
        """Format a transfer event into a standardized format."""
        return {
            'event': 'nft_transfer',
            'timestamp': datetime.utcfromtimestamp(block.timestamp).isoformat(),
            'block_number': block.number,
            'transaction_hash': tx.hash.hex(),
            'from_address': event['from'],
            'to_address': event['to'],
            'contract_address': event['contract'],
            'token_id': str(event['tokenId']),
            'price_eth': price,
            'value_eth': str(self.w3.from_wei(tx.value, 'ether')) if tx.value else '0',
            'gas_used': receipt.gasUsed,
            'gas_price_gwei': str(self.w3.from_wei(tx.gasPrice, 'gwei')) if hasattr(tx, 'gasPrice') else None,
            'metadata': token_metadata or {},
            'network_id': self.w3.eth.chain_id,
            'network_name': self._get_network_name(self.w3.eth.chain_id)
        }
    
    async def _broadcast_event(self, event_type: str, data: dict):
        """Broadcast an event to all subscribed WebSocket clients."""
        try:
            # Broadcast to specific collection channel if available
            if 'contract_address' in data:
                collection_channel = f"collection:{data['contract_address'].lower()}"
                await manager.broadcast_event(collection_channel, data)
            
            # Broadcast to general channel
            await manager.broadcast_event(event_type, data)
            
        except Exception as e:
            logger.error(f"Error broadcasting event: {e}", exc_info=True)
    
    def _get_default_contracts(self) -> List[str]:
        """Get default list of NFT contract addresses to monitor."""
        # Flatten the nested dictionary of contracts
        return [
            address.lower()
            for chain_contracts in COMMON_NFT_CONTRACTS.values()
            for address in chain_contracts.values()
        ]

    async def _initialize_web3(self):
        """Initialize Web3 connection and contracts."""
        if not self.w3:
            self.w3 = await asyncio.get_event_loop().run_in_executor(
                None, self.web3_conn.connect
            )
            logger.info(f"Connected to {self.w3.provider.endpoint_uri}")
            
            # Initialize contracts
            for addr in self.contract_addresses:
                try:
                    contract = await asyncio.get_event_loop().run_in_executor(
                        None, self.web3_conn.get_contract, addr
                    )
                    if contract:
                        self.contracts[addr.lower()] = contract
                except Exception as e:
                    logger.warning(f"Failed to initialize contract {addr}: {e}")

    async def _get_token_metadata(self, contract_address: str, token_id: int) -> dict:
        """Get token metadata from contract or external API."""
        try:
            contract = self.contracts.get(contract_address.lower())
            if not contract:
                return {}
                
            # Try ERC-721 metadata
            try:
                token_uri = await asyncio.get_event_loop().run_in_executor(
                    None, contract.functions.tokenURI(token_id).call
                )
                if token_uri:
                    return {'token_uri': token_uri, 'standard': 'erc721'}
            except Exception:
                pass
                
            # Try ERC-1155 metadata
            try:
                token_uri = await asyncio.get_event_loop().run_in_executor(
                    None, contract.functions.uri(token_id).call
                )
                if token_uri:
                    return {'token_uri': token_uri, 'standard': 'erc1155'}
            except Exception:
                pass
                
            return {}
            
        except Exception as e:
            logger.error(f"Error getting token metadata: {e}")
            return {}
    
    async def _get_transfer_price(self, tx, receipt: TxReceipt) -> Optional[str]:
        """Extract price from transaction if it's a sale."""
        if not tx.value or tx.value <= 0:
            return None
            
        try:
            # Convert from wei to ETH
            eth_value = self.w3.from_wei(tx.value, 'ether')
            return str(eth_value)
        except Exception as e:
            logger.warning(f"Error parsing transaction value: {e}")
            return None
    
    @staticmethod
    def _get_network_name(chain_id: int) -> str:
        """Get human-readable network name from chain ID."""
        networks = {
            1: 'ethereum',
            5: 'goerli',
            137: 'polygon',
            80001: 'mumbai',
            56: 'bsc',
            97: 'bsc_testnet',
            42161: 'arbitrum',
            10: 'optimism',
            43114: 'avalanche',
        }
        return networks.get(chain_id, f'unknown_{chain_id}')