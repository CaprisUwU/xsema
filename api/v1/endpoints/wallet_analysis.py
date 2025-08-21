"""
Wallet Analysis Endpoint

This module provides endpoints for analyzing NFT wallets, including:
- Fetching wallet tokens and metadata
- Calculating wallet statistics
- Analyzing wallet activity and patterns
"""
from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
import logging
import os

# Import blockchain service
from services.blockchain import blockchain_service, BlockchainServiceError

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["wallet-analysis"])

class WalletToken(BaseModel):
    """Represents an NFT token in a wallet."""
    contract_address: str
    token_id: str
    token_standard: str = "ERC721"  # or "ERC1155"
    name: Optional[str] = None
    symbol: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    last_transferred_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WalletAnalysis(BaseModel):
    """Represents the analysis results for a wallet."""
    wallet_address: str
    total_tokens: int
    unique_collections: int
    tokens: List[WalletToken]
    last_updated: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

def normalize_wallet_address(address: str) -> str:
    """Normalize Ethereum address to checksum format."""
    try:
        return Web3.to_checksum_address(address)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Ethereum address: {address}"
        )

@router.get("/analysis/{wallet_address}", response_model=WalletAnalysis)
async def get_wallet_analysis(
    wallet_address: str,
    include_metadata: bool = False,
    chain: str = "eth-mainnet"
):
    """
    Get analysis of an NFT wallet.
    
    Args:
        wallet_address: The wallet address to analyze (Ethereum address)
        include_metadata: Whether to include full token metadata (may be slow)
        chain: Blockchain network (default: eth-mainnet)
        
    Returns:
        WalletAnalysis: Analysis of the wallet's NFT holdings
    """
    # Normalize wallet address
    try:
        wallet_address = normalize_wallet_address(wallet_address)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Invalid wallet address {wallet_address}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid wallet address: {wallet_address}"
        )
    
    try:
        # Get NFTs from blockchain
        nft_data = await blockchain_service.get_wallet_nfts(
            wallet_address=wallet_address,
            chain=chain,
            page_size=100  # Limit to first 100 NFTs for performance
        )
        
        # Process NFTs
        tokens = []
        for nft in nft_data.get("ownedNfts", [])[:100]:  # Limit to 100 NFTs
            contract_address = nft.get("contract", {}).get("address")
            token_id = nft.get("id", {}).get("tokenId")
            
            if not contract_address or token_id is None:
                continue
                
            # Get metadata if requested
            metadata = None
            if include_metadata:
                try:
                    metadata = await blockchain_service.get_token_metadata(
                        contract_address=contract_address,
                        token_id=token_id,
                        chain=chain
                    )
                except Exception as meta_err:
                    logger.warning(
                        f"Failed to fetch metadata for {contract_address}/{token_id}: {str(meta_err)}"
                    )
            
            # Get last transfer time if available
            last_transfer = None
            if "timeLastUpdated" in nft:
                try:
                    last_transfer = datetime.fromisoformat(nft["timeLastUpdated"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            
            token = {
                "contract_address": contract_address,
                "token_id": str(token_id),
                "token_standard": nft.get("id", {}).get("tokenMetadata", {}).get("tokenType") or "ERC721",
                "name": nft.get("title") or f"NFT #{token_id}",
                "symbol": nft.get("contract", {}).get("symbol", ""),
                "metadata": metadata if include_metadata else None,
                "last_transferred_at": last_transfer
            }
            tokens.append(token)
        
        # Get token balances
        try:
            token_balances = await blockchain_service.get_wallet_token_balances(
                wallet_address=wallet_address,
                chain=chain
            )
            token_count = len(token_balances.get("tokenBalances", []))
        except Exception as balance_err:
            logger.warning(f"Failed to fetch token balances: {str(balance_err)}")
            token_count = 0
        
        # Prepare response
        analysis = {
            "wallet_address": wallet_address,
            "total_tokens": len(tokens),
            "unique_collections": len({t['contract_address'] for t in tokens}),
            "token_balance_count": token_count,
            "tokens": tokens,
            "last_updated": datetime.utcnow()
        }
        
        return analysis
        
    except BlockchainServiceError as e:
        logger.error(f"Blockchain service error for wallet {wallet_address}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Blockchain service error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing wallet {wallet_address}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze wallet: {str(e)}"
        )

@router.get("/tokens/{wallet_address}")
async def get_wallet_tokens(
    wallet_address: str,
    contract_address: Optional[str] = None,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    chain: str = "eth-mainnet",
    include_metadata: bool = False
):
    """
    Get tokens owned by a wallet.
    
    Args:
        wallet_address: The wallet address to query (Ethereum address)
        contract_address: Optional filter by contract address
        limit: Maximum number of tokens to return (1-100)
        offset: Pagination offset
        chain: Blockchain network (default: eth-mainnet)
        include_metadata: Whether to include full token metadata (slower)
        
    Returns:
        List of tokens owned by the wallet with pagination info
    """
    # Normalize wallet address
    try:
        wallet_address = normalize_wallet_address(wallet_address)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Invalid wallet address {wallet_address}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid wallet address: {wallet_address}"
        )
    
    # Normalize contract address if provided
    if contract_address:
        try:
            contract_address = Web3.to_checksum_address(contract_address)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid contract address: {contract_address}"
            )
    
    try:
        # Get NFTs from blockchain with pagination
        nft_data = await blockchain_service.get_wallet_nfts(
            wallet_address=wallet_address,
            contract_address=contract_address,
            chain=chain,
            page_size=min(limit, 100),  # Max page size is 100
            page_key=str(offset) if offset > 0 else None
        )
        
        # Process NFTs
        tokens = []
        for nft in nft_data.get("ownedNfts", []):
            contract_addr = nft.get("contract", {}).get("address")
            token_id = nft.get("id", {}).get("tokenId")
            
            if not contract_addr or token_id is None:
                continue
            
            # Get metadata if requested
            metadata = None
            if include_metadata:
                try:
                    metadata = await blockchain_service.get_token_metadata(
                        contract_address=contract_addr,
                        token_id=token_id,
                        chain=chain
                    )
                except Exception as meta_err:
                    logger.warning(
                        f"Failed to fetch metadata for {contract_addr}/{token_id}: {str(meta_err)}"
                    )
            
            # Get last transfer time if available
            last_transfer = None
            if "timeLastUpdated" in nft:
                try:
                    last_transfer = datetime.fromisoformat(nft["timeLastUpdated"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            
            token = {
                "contract_address": contract_addr,
                "token_id": str(token_id),
                "token_standard": nft.get("id", {}).get("tokenMetadata", {}).get("tokenType") or "ERC721",
                "name": nft.get("title") or f"NFT #{token_id}",
                "symbol": nft.get("contract", {}).get("symbol", ""),
                "metadata_uri": nft.get("tokenUri", {}).get("raw"),
                "metadata": metadata if include_metadata else None,
                "last_transferred_at": last_transfer.isoformat() if last_transfer else None
            }
            tokens.append(token)
        
        # Prepare response with pagination info
        response = {
            "wallet_address": wallet_address,
            "total": nft_data.get("totalCount", len(tokens)),
            "limit": limit,
            "offset": offset,
            "page_key": nft_data.get("pageKey"),  # For pagination
            "tokens": tokens
        }
        
        return response
        
    except BlockchainServiceError as e:
        logger.error(f"Blockchain service error for wallet {wallet_address}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Blockchain service error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tokens for wallet {wallet_address}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch wallet tokens: {str(e)}"
        )
