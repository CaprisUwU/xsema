"""
Multi-Chain API Endpoints

API endpoints for interacting with multiple blockchain networks including
Ethereum, Polygon, BSC, Arbitrum, Optimism, and Solana.
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from core.multi_chain_config import ChainType, get_supported_networks as get_config_networks
from services.multi_chain_service import get_multi_chain_service

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic Models
class NetworkStatusResponse(BaseModel):
    """Response model for network status."""
    chain_type: str
    name: str
    connected: bool
    current_block: Optional[int] = None
    last_updated: str


class BalanceResponse(BaseModel):
    """Response model for balance information."""
    address: str
    chain: str
    balance_wei: Optional[int] = None
    balance_lamports: Optional[int] = None
    balance_decimal: float
    symbol: str
    decimals: int


class TransactionResponse(BaseModel):
    """Response model for transaction information."""
    chain: str
    hash: str
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    value: Optional[int] = None
    gas: Optional[int] = None
    gas_price: Optional[int] = None
    nonce: Optional[int] = None
    block_number: Optional[int] = None
    slot: Optional[int] = None
    block_time: Optional[int] = None
    fee: Optional[int] = None
    status: Optional[str] = None


class NetworkInfoResponse(BaseModel):
    """Response model for network information."""
    chain_type: str
    name: str
    symbol: str
    chain_id: int
    explorer_url: str
    native_currency: str
    decimals: int
    block_time: int
    supports_eip1559: bool
    current_block: Optional[int] = None
    connected: bool


class MultiChainSummaryResponse(BaseModel):
    """Response model for multi-chain summary."""
    total_networks: int
    connected_networks: int
    networks: List[NetworkInfoResponse]


# API Endpoints
@router.get("/networks", response_model=List[str], tags=["multi-chain"])
async def get_supported_networks():
    """
    Get list of supported blockchain networks.
    
    Returns:
        List of supported network identifiers (e.g., ["ethereum", "polygon", "bsc"])
    """
    try:
        networks = get_config_networks()
        return [network.value for network in networks]
    except Exception as e:
        logger.error(f"Error getting supported networks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported networks")


@router.get("/networks/status", response_model=List[NetworkStatusResponse], tags=["multi-chain"])
async def get_all_networks_status():
    """
    Get connection status for all supported networks.
    
    Returns:
        List of network status information including connection status and current block numbers.
    """
    try:
        service = await get_multi_chain_service()
        status = await service.get_connection_status()
        
        networks_status = []
        for chain_type, connected in status.items():
            try:
                network_info = await service.get_network_info(chain_type)
                if network_info:
                    networks_status.append(NetworkStatusResponse(
                        chain_type=network_info["chain_type"],
                        name=network_info["name"],
                        connected=network_info["connected"],
                        current_block=network_info["current_block"],
                        last_updated=network_info.get("last_updated", "N/A")
                    ))
            except Exception as e:
                logger.warning(f"Failed to get status for {chain_type}: {e}")
                # Add basic status info even if detailed info fails
                networks_status.append(NetworkStatusResponse(
                    chain_type=chain_type.value,
                    name=chain_type.value.title(),
                    connected=connected,
                    current_block=None,
                    last_updated="N/A"
                ))
        
        return networks_status
    except Exception as e:
        logger.error(f"Error getting networks status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get networks status")


@router.get("/networks/{chain_type}/status", response_model=NetworkStatusResponse, tags=["multi-chain"])
async def get_network_status(
    chain_type: str = Path(..., description="Blockchain network type (e.g., ethereum, polygon)")
):
    """
    Get connection status for a specific network.
    
    Args:
        chain_type: The blockchain network type
        
    Returns:
        Network status information including connection status and current block number.
    """
    try:
        # Validate chain type
        try:
            chain_enum = ChainType(chain_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported chain type: {chain_type}")
        
        service = await get_multi_chain_service()
        network_info = await service.get_network_info(chain_enum)
        
        if not network_info:
            raise HTTPException(status_code=404, detail=f"Network {chain_type} not found")
        
        return NetworkStatusResponse(
            chain_type=network_info["chain_type"],
            name=network_info["name"],
            connected=network_info["connected"],
            current_block=network_info["current_block"],
            last_updated=network_info.get("last_updated", "N/A")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting network status for {chain_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get network status for {chain_type}")


@router.get("/networks/{chain_type}/info", response_model=NetworkInfoResponse, tags=["multi-chain"])
async def get_network_info(
    chain_type: str = Path(..., description="Blockchain network type (e.g., ethereum, polygon)")
):
    """
    Get detailed information for a specific network.
    
    Args:
        chain_type: The blockchain network type
        
    Returns:
        Detailed network information including configuration and current status.
    """
    try:
        # Validate chain type
        try:
            chain_enum = ChainType(chain_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported chain type: {chain_type}")
        
        service = await get_multi_chain_service()
        network_info = await service.get_network_info(chain_enum)
        
        if not network_info:
            raise HTTPException(status_code=404, detail=f"Network {chain_type} not found")
        
        return NetworkInfoResponse(**network_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting network info for {chain_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get network info for {chain_type}")


@router.get("/networks/{chain_type}/block", tags=["multi-chain"])
async def get_current_block(
    chain_type: str = Path(..., description="Blockchain network type (e.g., ethereum, polygon)")
):
    """
    Get current block number for a specific network.
    
    Args:
        chain_type: The blockchain network type
        
    Returns:
        Current block number and network information.
    """
    try:
        # Validate chain type
        try:
            chain_enum = ChainType(chain_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported chain type: {chain_type}")
        
        service = await get_multi_chain_service()
        block_number = await service.get_block_number(chain_enum)
        
        if block_number is None:
            raise HTTPException(status_code=503, detail=f"Unable to get block number for {chain_type}")
        
        return {
            "chain_type": chain_type,
            "current_block": block_number,
            "timestamp": "N/A"  # Could be enhanced to include actual timestamp
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting block number for {chain_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get block number for {chain_type}")


@router.get("/networks/{chain_type}/balance/{address}", response_model=BalanceResponse, tags=["multi-chain"])
async def get_address_balance(
    chain_type: str = Path(..., description="Blockchain network type (e.g., ethereum, polygon)"),
    address: str = Path(..., description="Wallet address to check balance for")
):
    """
    Get native token balance for an address on a specific network.
    
    Args:
        chain_type: The blockchain network type
        address: The wallet address to check
        
    Returns:
        Balance information including amounts in different units.
    """
    try:
        # Validate chain type
        try:
            chain_enum = ChainType(chain_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported chain type: {chain_type}")
        
        # Basic address validation
        if not address or len(address) < 10:
            raise HTTPException(status_code=400, detail="Invalid address format")
        
        service = await get_multi_chain_service()
        balance_info = await service.get_balance(chain_enum, address)
        
        if not balance_info:
            raise HTTPException(status_code=404, detail=f"Unable to get balance for address {address} on {chain_type}")
        
        return BalanceResponse(**balance_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting balance for {address} on {chain_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get balance for {address} on {chain_type}")


@router.get("/networks/{chain_type}/transaction/{tx_hash}", response_model=TransactionResponse, tags=["multi-chain"])
async def get_transaction_info(
    chain_type: str = Path(..., description="Blockchain network type (e.g., ethereum, polygon)"),
    tx_hash: str = Path(..., description="Transaction hash to look up")
):
    """
    Get transaction information from a specific network.
    
    Args:
        chain_type: The blockchain network type
        tx_hash: The transaction hash to look up
        
    Returns:
        Transaction details including sender, recipient, value, and status.
    """
    try:
        # Validate chain type
        try:
            chain_enum = ChainType(chain_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported chain type: {chain_type}")
        
        # Basic hash validation
        if not tx_hash or len(tx_hash) < 10:
            raise HTTPException(status_code=400, detail="Invalid transaction hash format")
        
        service = await get_multi_chain_service()
        tx_info = await service.get_transaction(chain_enum, tx_hash)
        
        if not tx_info:
            raise HTTPException(status_code=404, detail=f"Transaction {tx_hash} not found on {chain_type}")
        
        # Map the response to our model
        response_data = {
            "chain": tx_info["chain"],
            "hash": tx_info["hash"],
            "from_address": tx_info.get("from"),
            "to_address": tx_info.get("to"),
            "value": tx_info.get("value"),
            "gas": tx_info.get("gas"),
            "gas_price": tx_info.get("gas_price"),
            "nonce": tx_info.get("nonce"),
            "block_number": tx_info.get("block_number"),
            "slot": tx_info.get("slot"),
            "block_time": tx_info.get("block_time"),
            "fee": tx_info.get("fee"),
            "status": tx_info.get("status")
        }
        
        return TransactionResponse(**response_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction {tx_hash} on {chain_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get transaction {tx_hash} on {chain_type}")


@router.post("/networks/{chain_type}/test", tags=["multi-chain"])
async def test_network_connection(
    chain_type: str = Path(..., description="Blockchain network type (e.g., ethereum, polygon)")
):
    """
    Test connection to a specific network.
    
    Args:
        chain_type: The blockchain network type
        
    Returns:
        Connection test results including success status and response time.
    """
    try:
        # Validate chain type
        try:
            chain_enum = ChainType(chain_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported chain type: {chain_type}")
        
        import time
        start_time = time.time()
        
        service = await get_multi_chain_service()
        is_connected = await service.test_connection(chain_enum)
        
        response_time = round((time.time() - start_time) * 1000, 2)  # milliseconds
        
        return {
            "chain_type": chain_type,
            "connected": is_connected,
            "response_time_ms": response_time,
            "timestamp": time.time()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing connection for {chain_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test connection for {chain_type}")


@router.get("/summary", response_model=MultiChainSummaryResponse, tags=["multi-chain"])
async def get_multi_chain_summary():
    """
    Get comprehensive summary of all supported networks.
    
    Returns:
        Summary information including total networks, connected networks, and detailed network info.
    """
    try:
        service = await get_multi_chain_service()
        networks_info = await service.get_all_networks_info()
        
        total_networks = len(networks_info)
        connected_networks = sum(1 for network in networks_info if network["connected"])
        
        return MultiChainSummaryResponse(
            total_networks=total_networks,
            connected_networks=connected_networks,
            networks=[NetworkInfoResponse(**network) for network in networks_info]
        )
    except Exception as e:
        logger.error(f"Error getting multi-chain summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get multi-chain summary")


@router.get("/health", tags=["multi-chain"])
async def get_multi_chain_health():
    """
    Get health status of multi-chain service.
    
    Returns:
        Health information including service status and network connectivity.
    """
    try:
        service = await get_multi_chain_service()
        status = await service.get_connection_status()
        
        total_networks = len(status)
        connected_networks = sum(1 for connected in status.values() if connected)
        health_percentage = (connected_networks / total_networks * 100) if total_networks > 0 else 0
        
        return {
            "service": "multi-chain",
            "status": "healthy" if health_percentage > 50 else "degraded",
            "total_networks": total_networks,
            "connected_networks": connected_networks,
            "health_percentage": round(health_percentage, 2),
            "networks": {
                chain.value: {
                    "connected": connected,
                    "status": "online" if connected else "offline"
                }
                for chain, connected in status.items()
            }
        }
    except Exception as e:
        logger.error(f"Error getting multi-chain health: {e}")
        return {
            "service": "multi-chain",
            "status": "unhealthy",
            "error": str(e),
            "total_networks": 0,
            "connected_networks": 0,
            "health_percentage": 0
        }
