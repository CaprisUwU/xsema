"""
Balance Service

Responsible for fetching and managing token balances across multiple blockchains.
Supports caching and rate limiting for optimal performance.
"""
import asyncio
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import aiohttp
import json
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from portfolio.models.portfolio import Asset, Wallet
from portfolio.core.config import settings
from portfolio.core.cache import cache
from portfolio.utils.logger import logger

# RPC endpoints for different blockchains
RPC_ENDPOINTS = {
    'ethereum': settings.ETHEREUM_RPC_URL,
    'polygon': settings.POLYGON_RPC_URL,
    'bsc': settings.BSC_RPC_URL,
}

# Common ERC20 ABI for balance checking
ERC20_ABI = [
    {
        'constant': True,
        'inputs': [{'name': '_owner', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'name': 'balance', 'type': 'uint256'}],
        'type': 'function'
    },
    {
        'constant': True,
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'name': '', 'type': 'uint8'}],
        'type': 'function'
    },
    {
        'constant': True,
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'name': '', 'type': 'string'}],
        'type': 'function'
    },
    {
        'constant': True,
        'inputs': [],
        'name': 'name',
        'outputs': [{'name': '', 'type': 'string'}],
        'type': 'function'
    }
]

class BalanceService:
    """Service for fetching and managing token balances"""
    
    def __init__(self):
        self.sessions = {}
        self.web3_instances = {}
        self._init_web3_instances()
    
    def _init_web3_instances(self):
        """Initialize Web3 instances for different blockchains"""
        for chain, rpc_url in RPC_ENDPOINTS.items():
            if not rpc_url:
                logger.warning(f"No RPC URL configured for {chain}")
                continue
                
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            # Inject POA middleware for chains that need it
            if chain in ['polygon', 'bsc']:
                w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            
            self.web3_instances[chain] = w3
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session"""
        loop = asyncio.get_event_loop()
        if loop not in self.sessions or self.sessions[loop].closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.sessions[loop] = aiohttp.ClientSession(timeout=timeout)
        return self.sessions[loop]
    
    @cache(ttl=300)  # Cache for 5 minutes
    async def get_native_balance(
        self, 
        address: str, 
        chain: str = 'ethereum'
    ) -> Dict[str, Union[str, float]]:
        """Get native token balance (ETH, MATIC, BNB, etc.)"""
        if chain not in self.web3_instances:
            raise ValueError(f"Unsupported chain: {chain}")
        
        w3 = self.web3_instances[chain]
        
        try:
            # Convert address to checksum address
            address = Web3.to_checksum_address(address)
            
            # Get balance in wei and convert to ether
            balance_wei = await asyncio.get_event_loop().run_in_executor(
                None, 
                w3.eth.get_balance,
                address
            )
            
            balance_eth = w3.from_wei(balance_wei, 'ether')
            
            return {
                'address': address,
                'balance': float(balance_eth),
                'balance_wei': balance_wei,
                'chain': chain,
                'token_address': None,  # Native token
                'decimals': 18,
                'symbol': chain.upper(),
                'name': chain.capitalize(),
                'is_native': True,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting native balance for {address} on {chain}: {str(e)}")
            raise
    
    @cache(ttl=300)  # Cache for 5 minutes
    async def get_token_balance(
        self,
        wallet_address: str,
        token_address: str,
        chain: str = 'ethereum'
    ) -> Dict[str, Union[str, float, int]]:
        """Get ERC20 token balance for a wallet"""
        if chain not in self.web3_instances:
            raise ValueError(f"Unsupported chain: {chain}")
            
        w3 = self.web3_instances[chain]
        
        try:
            # Convert addresses to checksum addresses
            wallet_address = Web3.to_checksum_address(wallet_address)
            token_address = Web3.to_checksum_address(token_address)
            
            # Create contract instance
            contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
            
            # Get token metadata
            symbol = await asyncio.get_event_loop().run_in_executor(
                None,
                contract.functions.symbol().call
            )
            
            name = await asyncio.get_event_loop().run_in_executor(
                None,
                contract.functions.name().call
            )
            
            decimals = await asyncio.get_event_loop().run_in_executor(
                None,
                contract.functions.decimals().call
            )
            
            # Get token balance
            balance = await asyncio.get_event_loop().run_in_executor(
                None,
                contract.functions.balanceOf(wallet_address).call
            )
            
            # Calculate human-readable balance
            balance_human = balance / (10 ** decimals)
            
            return {
                'wallet_address': wallet_address,
                'token_address': token_address,
                'balance': float(balance_human),
                'balance_raw': balance,
                'chain': chain,
                'decimals': decimals,
                'symbol': symbol,
                'name': name,
                'is_native': False,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting token balance: {str(e)}")
            raise
    
    async def get_all_balances(self, wallet_address: str, chain: str = 'ethereum') -> List[Dict]:
        """Get all token balances (native + ERC20) for a wallet"""
        try:
            # Get native token balance
            native_balance = await self.get_native_balance(wallet_address, chain)
            
            # Get ERC20 token balances (implementation depends on your setup)
            # This is a placeholder - you'd typically use something like Alchemy or Moralis
            token_balances = await self._get_erc20_balances(wallet_address, chain)
            
            return [native_balance] + token_balances
            
        except Exception as e:
            logger.error(f"Error getting all balances: {str(e)}")
            raise
    
    async def _get_erc20_balances(
        self, 
        wallet_address: str, 
        chain: str
    ) -> List[Dict]:
        """Get all ERC20 token balances for a wallet"""
        # This is a placeholder implementation
        # In a real app, you'd use Alchemy, Moralis, or similar service
        # to get all token balances in a single call
        return []
    
    async def get_wallet_assets(self, wallet: Wallet) -> List[Asset]:
        """Get all assets for a wallet"""
        assets = []
        
        # Get native token balance
        try:
            native_balance = await self.get_native_balance(wallet.address, wallet.chain)
            if native_balance['balance'] > 0:
                assets.append(Asset(
                    asset_id=f"{wallet.chain}_native",
                    symbol=native_balance['symbol'],
                    name=native_balance['name'],
                    type='native',
                    balance=native_balance['balance'],
                    value_usd=0,  # Will be updated by price service
                    metadata={
                        'chain': wallet.chain,
                        'is_native': True,
                        'contract_address': None
                    }
                ))
        except Exception as e:
            logger.error(f"Error getting native balance for {wallet.address}: {str(e)}")
        
        # Get token balances (placeholder implementation)
        # In a real app, you'd implement this to get all token balances
        
        return assets
    
    async def close(self):
        """Close all open sessions"""
        for session in self.sessions.values():
            if not session.closed:
                await session.close()
        self.sessions.clear()

# Singleton instance
balance_service = BalanceService()
