"""
NFT Service

Handles all NFT-related operations including fetching collections,
ownership details, and metadata.
"""
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Union
from datetime import datetime, timezone, timedelta
from web3 import Web3
from eth_typing import ChecksumAddress

from portfolio.core.config import settings
from portfolio.core.cache import cache
from portfolio.utils.logger import logger
from portfolio.models.nft import NFTMetadata, NFTCollection, NFTAttribute

class NFTService:
    """Service for handling NFT-related operations"""
    
    def __init__(self):
        self.sessions = {}
        self.alchemy_urls = {
            'ethereum': settings.ALCHEMY_ETH_HTTP_URL,
            'polygon': settings.ALCHEMY_POLYGON_HTTP_URL,
            'arbitrum': settings.ALCHEMY_ARBITRUM_HTTP_URL,
        }
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session"""
        loop = asyncio.get_event_loop()
        if loop not in self.sessions or self.sessions[loop].closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.sessions[loop] = aiohttp.ClientSession(timeout=timeout)
        return self.sessions[loop]
    
    @cache(ttl=3600)  # Cache for 1 hour
    async def get_nft_collections(
        self, 
        owner: str,
        chain: str = 'ethereum',
        with_metadata: bool = True
    ) -> List[NFTCollection]:
        """
        Get all NFT collections owned by an address
        
        Args:
            owner: Wallet address to check
            chain: Blockchain network
            with_metadata: Whether to include collection metadata
            
        Returns:
            List of NFT collections with their NFTs
        """
        if chain not in self.alchemy_urls or not self.alchemy_urls[chain]:
            raise ValueError(f"Unsupported or misconfigured chain: {chain}")
        
        try:
            # Get all NFTs for the owner
            nfts = await self._get_nfts_for_owner(owner, chain)
            
            # Group NFTs by collection
            collections_map = {}
            for nft in nfts:
                contract_address = nft.get('contract', {}).get('address', '').lower()
                if not contract_address:
                    continue
                    
                if contract_address not in collections_map:
                    collections_map[contract_address] = {
                        'contract': nft['contract'],
                        'nfts': []
                    }
                
                collections_map[contract_address]['nfts'].append(nft)
            
            # Convert to NFTCollection objects
            collections = []
            for contract_data in collections_map.values():
                contract = contract_data['contract']
                nfts = contract_data['nfts']
                
                # Get collection metadata if requested
                metadata = {}
                if with_metadata and nfts:
                    metadata = await self.get_contract_metadata(
                        contract['address'],
                        chain=chain
                    )
                
                collection = NFTCollection(
                    address=contract['address'],
                    name=metadata.get('name', contract.get('name', 'Unknown')),
                    symbol=metadata.get('symbol', contract.get('symbol', '')),
                    chain=chain,
                    nfts=[self._parse_nft_metadata(nft) for nft in nfts],
                    metadata=metadata
                )
                collections.append(collection)
            
            return collections
            
        except Exception as e:
            logger.error(f"Error getting NFT collections: {str(e)}")
            raise
    
    async def get_nfts_for_collection(
        self,
        contract_address: str,
        chain: str = 'ethereum',
        limit: int = 100,
        with_metadata: bool = True
    ) -> List[NFTMetadata]:
        """
        Get all NFTs for a specific collection
        
        Args:
            contract_address: NFT contract address
            chain: Blockchain network
            limit: Maximum number of NFTs to return
            with_metadata: Whether to include metadata
            
        Returns:
            List of NFTs in the collection
        """
        try:
            nfts = await self._get_nfts_for_contract(
                contract_address,
                chain=chain,
                limit=limit
            )
            
            if with_metadata:
                return [self._parse_nft_metadata(nft) for nft in nfts]
            return nfts
            
        except Exception as e:
            logger.error(f"Error getting NFTs for collection {contract_address}: {str(e)}")
            raise
    
    @cache(ttl=86400)  # Cache for 24 hours
    async def get_contract_metadata(
        self,
        contract_address: str,
        chain: str = 'ethereum'
    ) -> Dict:
        """
        Get metadata for an NFT contract
        
        Args:
            contract_address: NFT contract address
            chain: Blockchain network
            
        Returns:
            Contract metadata
        """
        try:
            # Try to get from cache first
            cache_key = f"nft:contract_metadata:{chain}:{contract_address.lower()}"
            
            # Use Alchemy's NFT API to get contract metadata
            url = f"{self.alchemy_urls[chain]}/getContractMetadata"
            params = {
                'contractAddress': contract_address
            }
            
            session = await self.get_session()
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                if 'contractMetadata' in data and data['contractMetadata']:
                    return data['contractMetadata']
                
                return {}
                
        except Exception as e:
            logger.error(f"Error getting contract metadata: {str(e)}")
            return {}
    
    async def get_nft_metadata(
        self,
        contract_address: str,
        token_id: str,
        chain: str = 'ethereum',
        refresh_cache: bool = False
    ) -> Optional[NFTMetadata]:
        """
        Get metadata for a specific NFT
        
        Args:
            contract_address: NFT contract address
            token_id: NFT token ID
            chain: Blockchain network
            refresh_cache: Whether to force refresh the cache
            
        Returns:
            NFT metadata or None if not found
        """
        cache_key = f"nft:metadata:{chain}:{contract_address.lower()}:{token_id}"
        
        # Try to get from cache if not refreshing
        if not refresh_cache:
            cached = cache.get(cache_key)
            if cached:
                return NFTMetadata(**json.loads(cached))
        
        try:
            # Use Alchemy's NFT API to get token metadata
            url = f"{self.alchemy_urls[chain]}/getNFTMetadata"
            params = {
                'contractAddress': contract_address,
                'tokenId': str(token_id)
            }
            
            session = await self.get_session()
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                if 'error' in data:
                    logger.error(f"Error from Alchemy: {data['error']['message']}")
                    return None
                
                # Parse the NFT metadata
                nft_metadata = self._parse_nft_metadata(data)
                
                # Cache the result
                cache.set(cache_key, nft_metadata.json())  # 24h cache
                
                return nft_metadata
                
        except Exception as e:
            logger.error(f"Error getting NFT metadata: {str(e)}")
            return None
    
    async def _get_nfts_for_owner(
        self,
        owner: str,
        chain: str,
        page_key: str = None,
        page_size: int = 100
    ) -> List[Dict]:
        """Get all NFTs owned by an address using pagination"""
        try:
            url = f"{self.alchemy_urls[chain]}/getNFTs"
            params = {
                'owner': owner,
                'withMetadata': 'true',
                'pageSize': page_size
            }
            
            if page_key:
                params['pageKey'] = page_key
            
            session = await self.get_session()
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                nfts = data.get('ownedNfts', [])
                
                # If there are more results, fetch them recursively
                if 'pageKey' in data and data['pageKey']:
                    more_nfts = await self._get_nfts_for_owner(
                        owner=owner,
                        chain=chain,
                        page_key=data['pageKey'],
                        page_size=page_size
                    )
                    nfts.extend(more_nfts)
                
                return nfts
                
        except Exception as e:
            logger.error(f"Error getting NFTs for owner: {str(e)}")
            return []
    
    async def _get_nfts_for_contract(
        self,
        contract_address: str,
        chain: str,
        limit: int = 100,
        page_key: str = None
    ) -> List[Dict]:
        """Get all NFTs for a contract using pagination"""
        try:
            url = f"{self.alchemy_urls[chain]}/getNFTsForCollection"
            params = {
                'contractAddress': contract_address,
                'withMetadata': 'true',
                'limit': min(limit, 100)  # Max 100 per request
            }
            
            if page_key:
                params['startToken'] = page_key
            
            session = await self.get_session()
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                nfts = data.get('nfts', [])
                
                # If there are more results and we haven't hit the limit
                if len(nfts) < limit and 'nextToken' in data and data['nextToken']:
                    more_nfts = await self._get_nfts_for_contract(
                        contract_address=contract_address,
                        chain=chain,
                        limit=limit - len(nfts),
                        page_key=data['nextToken']
                    )
                    nfts.extend(more_nfts)
                
                return nfts
                
        except Exception as e:
            logger.error(f"Error getting NFTs for contract: {str(e)}")
            return []
    
    def _parse_nft_metadata(self, nft_data: Dict) -> NFTMetadata:
        """Parse raw NFT data into NFTMetadata object"""
        metadata = nft_data.get('metadata', {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata) if metadata else {}
            except json.JSONDecodeError:
                metadata = {}
        
        # Parse attributes if they exist
        attributes = []
        if 'attributes' in metadata and isinstance(metadata['attributes'], list):
            for attr in metadata['attributes']:
                if isinstance(attr, dict):
                    attributes.append(NFTAttribute(
                        trait_type=attr.get('trait_type', ''),
                        value=attr.get('value', ''),
                        display_type=attr.get('display_type')
                    ))
        
        # Get media URLs
        media_url = None
        if 'image' in metadata:
            media_url = metadata['image']
        elif 'image_url' in metadata:
            media_url = metadata['image_url']
        
        # Parse token ID
        token_id = nft_data.get('id', {}).get('tokenId')
        if not token_id and 'tokenId' in nft_data:
            token_id = nft_data['tokenId']
        
        return NFTMetadata(
            token_id=str(token_id) if token_id is not None else '',
            name=nft_data.get('title') or metadata.get('name') or f"#{token_id}",
            description=metadata.get('description', ''),
            image=media_url,
            image_url=media_url,
            external_url=metadata.get('external_url'),
            animation_url=metadata.get('animation_url'),
            attributes=attributes,
            background_color=metadata.get('background_color'),
            collection=metadata.get('collection'),
            contract=metadata.get('contract'),
            token_standard=metadata.get('token_standard'),
            owner=metadata.get('owner'),
            last_updated=datetime.now(timezone.utc)
        )
    
    async def close(self):
        """Close all open sessions"""
        for session in self.sessions.values():
            if not session.closed:
                await session.close()
        self.sessions.clear()

# Singleton instance
nft_service = NFTService()
