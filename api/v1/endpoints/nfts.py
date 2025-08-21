"""
NFT Endpoints

Provides endpoints for NFT-related operations including details, transfers, events, and provenance verification.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timezone
from web3 import Web3

# Import our security modules
from ...live.ws_manager import manager
from core.security.provenance import ProvenanceVerifier, Transfer
from utils.graph_entropy import compute_wallet_graph_entropy
from utils.simhash import simhash as calculate_simhash, simhash_distance as hamming_distance

# Create a wrapper class to maintain compatibility
class GraphEntropyAnalyzer:
    def __init__(self):
        self.entropy_cache = {}
    
    def analyze_graph(self, df, wallet_col="wallet", token_col="token_id"):
        """Analyze the graph and return entropy and other metrics."""
        return compute_wallet_graph_entropy(
            df, 
            wallet_col=wallet_col, 
            token_col=token_col,
            return_full_analysis=True
        )

# Import Web3 connection
from live.blockchain import Web3Connection

router = APIRouter()

# Initialize the Web3 connection
web3_connection = Web3Connection()
w3 = web3_connection.connect()

# Initialize the provenance verifier
provenance_verifier = ProvenanceVerifier()

# Cache for storing verification results
provenance_cache = {}

def get_provenance_verifier() -> ProvenanceVerifier:
    """Dependency to get the provenance verifier instance."""
    return provenance_verifier

@router.get("/{contract_address}/{token_id}", response_model=dict)
async def get_nft_details(
    contract_address: str, 
    token_id: str,
    include_provenance: bool = Query(True, description="Include provenance verification")
):
    """
    Get detailed information about a specific NFT.
    
    Args:
        contract_address: The contract address of the NFT collection
        token_id: The token ID of the NFT
        include_provenance: Whether to include provenance verification
        
    Returns:
        dict: NFT details including metadata, ownership, and security analysis
    """
    # Get basic NFT data
    nft_data = {
        "contract_address": contract_address,
        "token_id": token_id,
        "metadata": await _fetch_nft_metadata(contract_address, token_id, w3),
        "owner": await _fetch_nft_owner(contract_address, token_id, w3),
        "security_analysis": {
            "uniqueness_signature": calculate_simhash(f"{contract_address}_{token_id}"),  # Business-friendly term
            "bitwise_patterns": analyze_bitwise_patterns(contract_address, token_id),
            "address_symmetry": check_address_symmetry(contract_address)
        },
        "last_updated": datetime.utcnow().isoformat()
    }
    
    # Add provenance verification if requested
    if include_provenance:
        try:
            # Check cache first
            cache_key = f"{contract_address.lower()}_{token_id}"
            if cache_key in provenance_cache:
                nft_data["provenance"] = provenance_cache[cache_key]
            else:
                # Fetch transfer history
                transfers = await get_transfer_history(contract_address, token_id, w3)
                
                # Add transfers to provenance verifier
                for tx in transfers:
                    transfer = Transfer(
                        tx_hash=tx["tx_hash"],
                        from_address=tx["from"],
                        to_address=tx["to"],
                        token_id=token_id,
                        timestamp=datetime.fromisoformat(tx["timestamp"].replace("Z", "+00:00")),
                        value=float(tx.get("value", 0)),
                        gas_price=float(tx.get("gas_price", 0)),
                        gas_used=int(tx.get("gas_used", 0)) if tx.get("gas_used") else None,
                        block_number=int(tx["block_number"]) if tx.get("block_number") else None,
                        log_index=int(tx["log_index"]) if tx.get("log_index") else None
                    )
                    provenance_verifier.add_transfer(transfer, contract_address)
                
                # Get verification results
                verification = provenance_verifier.verify_provenance(token_id, contract_address)
                nft_data["provenance"] = verification
                
                # Cache the result
                provenance_cache[cache_key] = verification
                
                # Keep cache size manageable
                if len(provenance_cache) > 1000:
                    # Remove oldest entries (FIFO)
                    for _ in range(100):
                        if provenance_cache:
                            provenance_cache.pop(next(iter(provenance_cache)))
                            
        except Exception as e:
            nft_data["provenance"] = {
                "error": f"Failed to verify provenance: {str(e)}",
                "status": "error"
            }
    
    return nft_data

@router.websocket("/events")
async def nft_events_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time NFT events.
    
    Clients can subscribe to different event types:
    - sales
    - transfers
    - listings
    - all_events
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    channels = message.get("channels", [])
                    await manager.subscribe(websocket, channels)
                elif message.get("type") == "unsubscribe":
                    channels = message.get("channels", [])
                    await manager.unsubscribe(websocket, channels)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@router.get("/{contract_address}/{token_id}/provenance", response_model=dict)
async def get_nft_provenance(
    contract_address: str, 
    token_id: str,
    include_timeline: bool = Query(True, description="Include ownership timeline")
):
    """
    Get detailed provenance information for an NFT.
    
    This includes the complete ownership history, verification status,
    and any detected risks or anomalies.
    
    Args:
        contract_address: The contract address of the NFT collection
        token_id: The token ID of the NFT
        include_timeline: Whether to include detailed ownership timeline
        
    Returns:
        dict: Detailed provenance information
    """
    try:
        # Get the verification results
        cache_key = f"{contract_address.lower()}_{token_id}"
        if cache_key in provenance_cache:
            verification = provenance_cache[cache_key]
        else:
            # If not in cache, fetch and verify
            nft_data = await get_nft_details(contract_address, token_id, True)
            verification = nft_data.get("provenance", {})
        
        result = {
            "contract_address": contract_address,
            "token_id": token_id,
            "verification": verification,
            "last_verified": datetime.utcnow().isoformat()
        }
        
        # Add ownership timeline if requested
        if include_timeline and verification.get("status") != "not_found":
            timeline = provenance_verifier.get_ownership_timeline(token_id, contract_address)
            result["ownership_timeline"] = timeline
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get provenance: {str(e)}"
        )

@router.get("/{contract_address}/{token_id}/history", response_model=dict)
async def get_nft_history(
    contract_address: str, 
    token_id: str, 
    limit: int = Query(100, description="Maximum number of transactions to return", ge=1, le=1000)
):
    """
    Get transaction history for a specific NFT.
    
    Args:
        contract_address: The contract address of the NFT collection
        token_id: The token ID of the NFT
        limit: Maximum number of transactions to return (1-1000)
        
    Returns:
        dict: Transaction history with pagination info
    """
    try:
        # Fetch transfer history from blockchain
        transfers = await get_transfer_history(contract_address, token_id, w3, limit)
        
        # Add to provenance verifier
        for tx in transfers:
            transfer = Transfer(
                tx_hash=tx["tx_hash"],
                from_address=tx["from"],
                to_address=tx["to"],
                token_id=token_id,
                timestamp=datetime.fromisoformat(tx["timestamp"].replace("Z", "+00:00")),
                value=float(tx.get("value", 0)),
                gas_price=float(tx.get("gas_price", 0)),
                gas_used=int(tx.get("gas_used", 0)) if tx.get("gas_used") else None,
                block_number=int(tx["block_number"]) if tx.get("block_number") else None,
                log_index=int(tx["log_index"]) if tx.get("log_index") else None
            )
            provenance_verifier.add_transfer(transfer, contract_address)
        
        return {
            "contract_address": contract_address,
            "token_id": token_id,
            "transactions": transfers,
            "total": len(transfers),
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch transaction history: {str(e)}"
        )

async def _fetch_nft_metadata(contract_address: str, token_id: str, w3: Web3) -> Dict[str, Any]:
    """Fetch NFT metadata from the blockchain."""
    # TODO: Implement actual metadata fetching
    return {
        "name": f"NFT #{token_id}",
        "description": "An NFT from the collection",
        "image": f"https://example.com/nfts/{contract_address}/{token_id}.png"
    }

async def _fetch_nft_owner(contract_address: str, token_id: str, w3: Web3) -> str:
    """Fetch the current owner of an NFT."""
    # TODO: Implement actual owner fetching
    return "0x0000000000000000000000000000000000000000"

async def get_transfer_history(
    contract_address: str, 
    token_id: str, 
    w3: Web3, 
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get transfer history for an NFT from the blockchain.
    
    Args:
        contract_address: The contract address
        token_id: The token ID
        w3: Web3 instance
        limit: Maximum number of transfers to return
        
    Returns:
        List of transfer events
    """
    # TODO: Implement actual transfer history fetching from blockchain
    # This is a placeholder implementation
    return []
