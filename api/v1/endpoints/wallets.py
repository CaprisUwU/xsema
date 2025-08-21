"""
Wallet Endpoints

Provides endpoints for wallet operations, analysis, and clustering.
"""
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks, status, WebSocket, WebSocketDisconnect, Request
from typing import List, Optional, Dict, Any, Set, Union, Tuple
from datetime import datetime, timedelta
from web3 import Web3
import json
import asyncio
import logging
import uuid
import time
import os
from pathlib import Path
from collections import defaultdict, namedtuple
from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import List as TypingList
from dataclasses import dataclass, asdict
from cachetools import LRUCache, TTLCache
from fastapi import APIRouter

# Create router for this module
router = APIRouter()

# Import wallet analysis endpoints
from .wallet_analysis import router as wallet_analysis_router

# Include wallet analysis router
router.include_router(
    wallet_analysis_router,
    prefix="/analysis",
    tags=["wallet-analysis"]
)

# Import our security analyzer and clustering
from services.security_analyzer import security_analyzer, SecurityScore
from core.security.wallet_clustering import WalletClustering, Wallet
from core.security.provenance import ProvenanceTracker
from core.utils.rate_limiter import BATCH_PROCESSING_LIMITER, rate_limit_check
from core.storage.batch_job_store import job_store as batch_job_store

# Define job statuses
class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Data classes for batch processing
@dataclass
class BatchJob:
    job_id: str
    status: JobStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress: int = 0
    total: int = 0
    results: Dict[str, Any] = None
    error: Optional[str] = None
    
    def to_dict(self):
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "progress": self.progress,
            "total": self.total,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error,
            "results": self.results
        }

# Cache for batch jobs (in-memory)
batch_jobs: Dict[str, BatchJob] = {}

# Clean up old jobs periodically
async def cleanup_old_jobs():
    """Background task to clean up old completed/failed jobs"""
    while True:
        try:
            # Clean up jobs older than 7 days
            deleted = await batch_job_store.cleanup_old_jobs(max_age_days=7)
            if deleted > 0:
                logging.info(f"Cleaned up {deleted} old batch jobs")
                
            # Also clean up in-memory cache
            current_time = time.time()
            week_ago = current_time - (7 * 24 * 60 * 60)
            
            to_delete = [
                job_id for job_id, job in batch_jobs.items()
                if job.completed_at and job.completed_at < week_ago
            ]
            
            for job_id in to_delete:
                del batch_jobs[job_id]
                
            if to_delete:
                logging.info(f"Cleaned up {len(to_delete)} old in-memory batch jobs")
                
        except Exception as e:
            logging.error(f"Error cleaning up old jobs: {str(e)}")
            
        # Run cleanup every hour
        await asyncio.sleep(3600)

# Start cleanup task
@router.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_old_jobs())

# Helper functions for batch processing
def create_batch_job(wallet_addresses: List[str]) -> BatchJob:
    job_id = str(uuid.uuid4())
    job = BatchJob(
        job_id=job_id,
        status=JobStatus.PENDING,
        created_at=time.time(),
        total=len(wallet_addresses),
        results={"clusters": [], "failed_addresses": []}
    )
    batch_jobs[job_id] = job
    return job

def update_job_status(job_id: str, status: JobStatus, **kwargs):
    if job_id in batch_jobs:
        job = batch_jobs[job_id]
        job.status = status
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)
        return True
    return False

class ClusterDepth(str, Enum):
    SHALLOW = "shallow"  # Direct connections only
    MEDIUM = "medium"    # 2nd degree connections
    DEEP = "deep"        # 3rd degree connections

class WalletClusterRequest(BaseModel):
    wallet_addresses: List[str] = Field(..., description="List of wallet addresses to cluster")
    depth: ClusterDepth = Field(ClusterDepth.MEDIUM, description="Depth of clustering analysis")
    include_risk: bool = Field(True, description="Include risk analysis in results")

class ClusterResult(BaseModel):
    cluster_id: str
    wallet_address: str
    cluster_members: List[str]
    cluster_size: int
    cluster_metadata: Dict[str, Any]
    risk_analysis: Optional[Dict[str, Any]] = None

# These imports have been moved to the top of the file

# Import Web3 connection
from live.blockchain import Web3Connection

# Initialize Web3 connection
web3_connection = Web3Connection()
w3 = web3_connection.connect()  # This will establish the connection

def get_transaction_history(wallet_address, start_block=0, end_block='latest'):
    """Get transaction history for a wallet.
    
    Args:
        wallet_address: The wallet address to get transactions for
        start_block: Starting block number (default: 0)
        end_block: Ending block number (default: 'latest')
        
    Returns:
        List of transaction hashes
    """
    # This is a simplified implementation - you'll want to enhance this
    # to include actual transaction details and pagination
    return []

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for storing clustering results with TTL
from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize caches
wallet_clusters_cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hour TTL
batch_jobs_cache = TTLCache(maxsize=100, ttl=86400)  # 24 hour TTL for batch jobs

# Thread pool for parallel processing
thread_pool = ThreadPoolExecutor(max_workers=10)

router = APIRouter()

# Global instance of WalletClustering with optimized parameters
WALLET_CLUSTERING = WalletClustering(
    hybrid_similarity_threshold=0.6,  # Balanced threshold for production
    min_cluster_size=2,  # Require at least 2 wallets for a cluster
    simhash_threshold=3  # Business-friendly term for similarity detection
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.lock = asyncio.Lock()

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {str(e)}")
                self.disconnect(client_id)

    async def broadcast_job_update(self, job_id: str, job: BatchJob):
        if job_id in self.active_connections:
            websocket = self.active_connections[job_id]
            try:
                await websocket.send_json({
                    "type": "progress",
                    "job_id": job_id,
                    "progress": job.progress,
                    "processed": job.progress,
                    "total": job.total
                })
            except Exception as e:
                logger.error(f"Error sending message to {job_id}: {str(e)}")
                self.disconnect(job_id)

# Initialize WebSocket manager
ws_manager = ConnectionManager()

# Background task to process wallet clusters in batches
async def process_wallet_batch(job_id: str, wallet_addresses: List[str], depth: ClusterDepth, include_risk: bool):
    """
    Background task to process a batch of wallet addresses.
    
    This function processes wallets in chunks, saves progress to persistent storage,
    and handles errors gracefully.
    """
    job = None
    try:
        # Get job from persistent storage
        job_data = await batch_job_store.get_job(job_id)
        if not job_data:
            logging.error(f"Job {job_id} not found in persistent storage")
            return
            
        # Update job status to processing
        job_data["status"] = JobStatus.PROCESSING.value
        job_data["started_at"] = time.time()
        await batch_job_store.save_job(job_id, job_data)
        
        # Also update in-memory job
        job = update_job_status(job_id, JobStatus.PROCESSING, started_at=time.time())
        
        # Initialize wallet clustering
        clustering = WalletClustering(
            simhash_threshold=3,  # Business-friendly term for similarity detection
            min_cluster_size=2,  # Require at least 2 wallets for a cluster
            hybrid_similarity_threshold=0.6  # Balanced threshold for production
        )
        results = []
        
        # Process wallets in chunks
        chunk_size = 10
        for i in range(0, len(wallet_addresses), chunk_size):
            chunk = wallet_addresses[i:i + chunk_size]
            
            # Process chunk
            for wallet_address in chunk:
                try:
                    # Get wallet cluster
                    cluster = await get_wallet_cluster(wallet_address, depth=depth, include_risk=include_risk)
                    results.append(cluster)
                    
                    # Update progress in both memory and persistent storage
                    job.progress += 1
                    job_data["progress"] = job.progress
                    job_data["results"] = {"clusters": results}
                    
                    # Save progress every 10 wallets or at the end
                    if job.progress % 10 == 0 or job.progress == job.total:
                        await batch_job_store.save_job(job_id, job_data)
                    
                    # Broadcast update to WebSocket clients
                    await ws_manager.broadcast_job_update(job_id, job)
                    
                except Exception as e:
                    error_msg = f"Error processing wallet {wallet_address}: {str(e)}"
                    logging.error(error_msg)
                    job_data.setdefault("errors", []).append(error_msg)
                    continue
        
        # Update job status to completed
        job_data.update({
            "status": JobStatus.COMPLETED.value,
            "completed_at": time.time(),
            "results": {"clusters": results},
            "progress": len(wallet_addresses)  # Ensure progress is 100%
        })
        await batch_job_store.save_job(job_id, job_data)
        
        # Also update in-memory job
        update_job_status(
            job_id,
            JobStatus.COMPLETED,
            completed_at=time.time(),
            results={"clusters": results}
        )
        
    except Exception as e:
        error_msg = f"Error in batch processing job {job_id}: {str(e)}"
        logging.error(error_msg)
        
        # Update both storage and memory
        if job_data:
            job_data.update({
                "status": JobStatus.FAILED.value,
                "completed_at": time.time(),
                "error": error_msg
            })
            await batch_job_store.save_job(job_id, job_data)
            
        if job:
            update_job_status(
                job_id,
                JobStatus.FAILED,
                completed_at=time.time(),
                error=error_msg
            )

@router.post("/batch/cluster", response_model=Dict[str, Any])
async def batch_cluster_wallets(
    request: WalletClusterRequest,
    background_tasks: BackgroundTasks,
    http_request: Request
):
    """
    Process multiple wallets in a batch and identify clusters.
    
    This endpoint starts an asynchronous job to cluster multiple wallets.
    Use the returned job_id to check the status or connect via WebSocket for real-time updates.
    
    Rate Limited: 5 requests per minute per IP.
    
    Args:
        request: Batch clustering request with wallet addresses and parameters
        
    Returns:
        dict: Job information including job_id for status checking
    """
    # Apply rate limiting
    await rate_limit_check(http_request, BATCH_PROCESSING_LIMITER)
    
    # Validate input
    if not request.wallet_addresses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one wallet address is required"
        )
    
    # Limit batch size
    MAX_BATCH_SIZE = 1000
    if len(request.wallet_addresses) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum batch size is {MAX_BATCH_SIZE} wallets"
        )
    
    # Create a new batch job
    job_id = str(uuid.uuid4())
    created_at = time.time()
    
    # Prepare job data for persistence
    job_data = {
        "job_id": job_id,
        "status": JobStatus.PENDING.value,
        "created_at": created_at,
        "total_wallets": len(request.wallet_addresses),
        "depth": request.depth.value,
        "include_risk": request.include_risk,
        "wallet_addresses": request.wallet_addresses,
        "progress": 0,
        "results": None,
        "error": None
    }
    
    # Store the job in persistent storage
    await batch_job_store.save_job(job_id, job_data)
    
    # Also keep in memory for fast access
    job = BatchJob(
        job_id=job_id,
        status=JobStatus.PENDING,
        created_at=created_at,
        started_at=None,
        completed_at=None,
        progress=0,
        total=len(request.wallet_addresses),
        results=None,
        error=None
    )
    
    batch_jobs[job_id] = job
    
    # Start background processing
    background_tasks.add_task(
        process_wallet_batch,
        job_id=job_id,
        wallet_addresses=request.wallet_addresses,
        depth=request.depth,
        include_risk=request.include_risk
    )
    
    return {
        "job_id": job_id,
        "status": job.status.value,
        "created_at": job.created_at,
        "total_wallets": job.total,
        "websocket_url": f"/api/v1/ws/batch/{job_id}",
        "status_url": f"/api/v1/wallets/batch/{job_id}/status"
    }

@router.get("/batch/{job_id}/status", response_model=Dict[str, Any])
async def get_batch_job_status(job_id: str):
    """
    Get the status of a batch clustering job.
    
    This endpoint checks both in-memory and persistent storage for the job status.
    
    Args:
        job_id: The ID of the batch job to check
        
    Returns:
        dict: Current status and results (if available) of the batch job
    """
    # First check in-memory cache
    job = batch_jobs.get(job_id)
    
    # If not in memory, try persistent storage
    if not job:
        job_data = await batch_job_store.get_job(job_id)
        if not job_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
            
        # Convert stored job data to BatchJob object
        job = BatchJob(
            job_id=job_data["job_id"],
            status=JobStatus(job_data["status"]),
            created_at=job_data["created_at"],
            started_at=job_data.get("started_at"),
            completed_at=job_data.get("completed_at"),
            progress=job_data.get("progress", 0),
            total=job_data.get("total_wallets", 0),
            results=job_data.get("results"),
            error=job_data.get("error")
        )
        
        # Cache in memory
        batch_jobs[job_id] = job
    
    response = {
        "job_id": job.job_id,
        "status": job.status.value,
        "progress": job.progress,
        "total": job.total,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "websocket_url": f"/api/v1/ws/batch/{job_id}",
        "self": f"/api/v1/wallets/batch/{job_id}/status"
    }
    
    # Include results if available
    if job.results:
        response["results"] = job.results
        
    # Include error if present
    if job.error:
        response["error"] = job.error
    
    return response

@router.websocket("/ws/batch/{job_id}")
async def websocket_batch_updates(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time updates on batch processing.
    
    Connect to this endpoint to receive real-time updates about the batch job progress.
    """
    # Check if job exists
    if job_id not in batch_jobs:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Add client to connection manager
    await ws_manager.connect(job_id, websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        ws_manager.disconnect(job_id)
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {str(e)}")
        ws_manager.disconnect(job_id)

@router.get("/{wallet_address}/cluster")
async def get_wallet_cluster(
    wallet_address: str,
    depth: int = Query(1, description="Depth of clustering analysis (1-3)", ge=1, le=3),
    include_risk: bool = Query(True, description="Include risk analysis in results")
):
    """
    Get wallet cluster information for a given wallet address.
    
    This endpoint identifies wallets that are likely controlled by the same entity
    based on transaction patterns, interactions, and behavioral analysis.
    
    Args:
        wallet_address: The wallet address to analyze
        depth: Depth of clustering analysis (1-3, where 1 is direct connections only)
        include_risk: Whether to include risk analysis for the cluster
        
    Returns:
        dict: Cluster information including related wallets and risk analysis
    """
    logger.info(f"Received request to cluster wallet: {wallet_address}")
    logger.info(f"Request parameters - depth: {depth}, include_risk: {include_risk}")
    
    try:
        # Validate wallet address
        if not Web3.is_address(wallet_address):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid wallet address format"
            )
            
        # Convert to checksum address
        wallet_address = Web3.to_checksum_address(wallet_address)
        
        # Check cache first
        cache_key = f"{wallet_address}:{depth}"
        if cache_key in wallet_clusters_cache:
            logger.info(f"Returning cached result for {wallet_address}")
            return wallet_clusters_cache[cache_key]
            
        # Get transaction history
        logger.info(f"Fetching transaction history for {wallet_address}")
        transactions = await get_transaction_history(wallet_address, limit=1000)
        
        if not transactions:
            return {
                "wallet_address": wallet_address,
                "cluster_members": [wallet_address],
                "cluster_size": 1,
                "risk_analysis": {
                    "risk_score": 0.0,
                    "risk_level": "low",
                    "indicators": []
                } if include_risk else None,
                "message": "No transaction history found for this wallet"
            }
            
        # Build wallet profiles
        wallet_profiles = {}
        
        # Process transactions to build wallet profiles
        for tx in transactions:
            # Initialize wallets if they don't exist
            for addr in [tx['from'], tx['to']]:
                if addr and addr not in wallet_profiles:
                    wallet_profiles[addr] = Wallet(addr)
            
            # Update sender profile
            if tx['from'] in wallet_profiles:
                wallet_profiles[tx['from']].update_from_transaction(tx)
                
            # Track interactions
            if tx['to'] and tx['to'] in wallet_profiles:
                wallet_profiles[tx['to']].add_interaction(tx['from'])
                
        # Finalize all wallets
        for wallet in wallet_profiles.values():
            wallet.finalize()
            
        # Cluster the wallets
        clusters = WALLET_CLUSTERING.cluster_wallets(wallet_profiles)
        
        # Find the cluster containing our target wallet
        target_cluster = None
        for cluster in clusters:
            if wallet_address in [w.address for w in cluster.members]:
                target_cluster = cluster
                break
                
        if not target_cluster:
            # If no cluster found, create a single-wallet cluster
            target_cluster = clusters[0] if clusters else None
            
        # Prepare response
        response = {
            "wallet_address": wallet_address,
            "cluster_members": [w.address for w in target_cluster.members],
            "cluster_size": len(target_cluster.members),
            "cluster_metadata": {
                "average_transactions": target_cluster.average_transactions,
                "common_contracts": list(target_cluster.common_contracts)[:10],
                "first_seen": target_cluster.first_seen.isoformat() if target_cluster.first_seen else None,
                "last_seen": target_cluster.last_seen.isoformat() if target_cluster.last_seen else None
            }
        }
        
        # Add risk analysis if requested
        if include_risk:
            risk_analysis = WALLET_CLUSTERING.analyze_cluster_risk(target_cluster)
            response["risk_analysis"] = risk_analysis
            
        # Cache the result
        wallet_clusters_cache[cache_key] = response
        
        return response
        
    except Exception as e:
        logger.error(f"Error in wallet clustering: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing wallet cluster: {str(e)}"
        )

@router.get("/{wallet_address}")
async def get_wallet(wallet_address: str):
    """
    Get detailed information about a wallet.
    
    Args:
        wallet_address: The wallet address to analyze
        
    Returns:
        dict: Wallet details including portfolio, security analysis, and cluster info
    """
    try:
        # Run security analysis
        fingerprint = calculate_wallet_fingerprint(wallet_address)
        patterns = analyze_wallet_patterns(wallet_address)
        symmetry = check_address_symmetry(wallet_address)
        
        # Get cluster info (first level only for performance)
        cluster_info = await get_wallet_cluster(wallet_address, depth=1, include_risk=True)
        
        return {
            "wallet_address": wallet_address,
            "portfolio": {
                "nfts": [],  # TODO: Implement actual NFT fetching
                "tokens": [],  # TODO: Implement token balance fetching
                "total_value": 0.0
            },
            "security_analysis": {
                "fingerprint": fingerprint,
                "patterns": patterns,
                "symmetry": symmetry,
                "risk_score": 0.0  # TODO: Implement risk scoring
            },
            "first_seen": None,  # TODO: Implement first seen tracking
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{wallet_address}/activity")
async def get_wallet_activity(
    wallet_address: str,
    limit: int = 100,
    offset: int = 0
):
    """
    Get activity history for a wallet.
    
    Args:
        wallet_address: The wallet address to query
        limit: Maximum number of activities to return
        offset: Pagination offset
    """
    # TODO: Implement actual activity fetching
    return {
        "wallet_address": wallet_address,
        "activities": [],
        "count": 0,
        "limit": limit,
        "offset": offset
    }

@router.get("/{wallet_address}/nfts")
async def get_wallet_nfts(
    wallet_address: str,
    collection: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Get NFTs owned by a wallet.
    
    Args:
        wallet_address: The wallet address to query
        collection: Optional collection address to filter by
        limit: Maximum number of NFTs to return
        offset: Pagination offset
    """
    # TODO: Implement actual NFT fetching
    return {
        "wallet_address": wallet_address,
        "nfts": [],
        "count": 0,
        "limit": limit,
        "offset": offset,
        "filters": {
            "collection": collection
        }
    }
