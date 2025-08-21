"""
Batch Ranking Endpoints

Provides endpoints for ranking NFTs in batch using hybrid scoring.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, BackgroundTasks, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import pandas as pd
import uuid
import json
import logging
import asyncio
from datetime import datetime, timedelta
import io
import time
import json

from core.features import extract_features
from core.scoring import hybrid_score
from services.model_service import train_model, predict_batch, predict_batch_stub
from services.model_registry import ModelRegistry
from core.storage.batch_job_store import BatchJobStore
from api.live.ws_manager import manager as ws_manager

router = APIRouter(prefix="/ranking", tags=["ranking"])

# Initialize services
model_registry = ModelRegistry()
batch_job_store = BatchJobStore()

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class BatchRankingJob(BaseModel):
    job_id: str
    status: JobStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress: int = 0
    total: int = 0
    results: Optional[List[Dict[str, Any]]] = None
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

class RankingRequest(BaseModel):
    model_id: Optional[str] = Field(
        None,
        description="ID of the model to use for ranking. If not provided, uses the production model."
    )
    include_symbolic: bool = Field(
        True,
        description="Include symbolic scoring in the hybrid score"
    )
    include_ml: bool = Field(
        True,
        description="Include machine learning model in the hybrid score"
    )
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="Weights for hybrid scoring. Keys: 'symbolic', 'ml'"
    )

# In-memory storage for batch jobs (complemented by persistent storage)
batch_jobs: Dict[str, BatchRankingJob] = {}

# WebSocket connection timeout (seconds)
WEBSOCKET_TIMEOUT = 300  # 5 minutes

# Background task to clean up old jobs
async def cleanup_old_jobs():
    """Background task to clean up old completed/failed jobs"""
    while True:
        try:
            # Clean up jobs older than 7 days
            deleted = await batch_job_store.cleanup_old_jobs(max_age_days=7)
            if deleted > 0:
                logging.info(f"Cleaned up {deleted} old batch ranking jobs")
                
            # Also clean up in-memory cache
            current_time = datetime.utcnow().timestamp()
            week_ago = current_time - (7 * 24 * 60 * 60)
            
            to_delete = [
                job_id for job_id, job in batch_jobs.items()
                if job.completed_at and job.completed_at < week_ago
            ]
            
            for job_id in to_delete:
                del batch_jobs[job_id]
                
            if to_delete:
                logging.info(f"Cleaned up {len(to_delete)} old in-memory batch ranking jobs")
                
        except Exception as e:
            logging.error(f"Error cleaning up old ranking jobs: {str(e)}")
            
        # Run cleanup every hour
        await asyncio.sleep(3600)

@router.on_event("startup")
async def startup_event():
    """Start background tasks on application startup"""
    asyncio.create_task(cleanup_old_jobs())

async def process_ranking_batch(
    job_id: str,
    df: pd.DataFrame,
    ranking_request: RankingRequest,
    client_id: Optional[str] = None
):
    """
    Process a batch of tokens for ranking.
    
    This runs in a background task and updates the job status as it progresses.
    """
    try:
        # Update job status to processing
        job = batch_jobs[job_id]
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow().timestamp()
        job.total = len(df)
        
        # Save to persistent storage
        await batch_job_store.update_job(job_id, job.to_dict())
        
        # Notify WebSocket subscribers
        await ws_manager.update_job_progress(
            job_id=job_id,
            progress=0,
            total=job.total,
            status=job.status,
            message="Starting batch processing..."
        )
        
        # Load the specified model or get production model
        model = None
        if ranking_request.include_ml:
            if ranking_request.model_id:
                model_info = model_registry.get_model(ranking_request.model_id)
                if not model_info:
                    raise ValueError(f"Model {ranking_request.model_id} not found")
                model_path = model_info.get("path")
                if not model_path:
                    raise ValueError("Model path not found in model info")
                # Load model from path - implementation depends on your model service
                # model = load_model(model_path)
            else:
                # Get production model
                model_info = model_registry.get_production_model("nft_ranking")
                if not model_info:
                    raise ValueError("No production model found")
                model_path = model_info.get("path")
                # model = load_model(model_path)
        
        # Extract features
        df = extract_features(df)
        
        # Get predictions if using ML
        model_scores = None
        if model and ranking_request.include_ml:
            X = df.drop(columns=["wallet", "token_id", "timestamp"])
            model_scores = predict_batch_stub(X)
        
        # Calculate scores
        results = []
        for idx, row in df.iterrows():
            # Update progress
            job.progress = idx + 1
            if idx % 10 == 0:  # Update more frequently for better UX
                # Save to persistent storage
                await batch_job_store.update_job(job_id, job.to_dict())
                
                # Notify WebSocket subscribers
                await ws_manager.update_job_progress(
                    job_id=job_id,
                    progress=job.progress,
                    total=job.total,
                    status=job.status,
                    message=f"Processed {job.progress} of {job.total} items"
                )
            
            # Calculate symbolic score (combining rarity and uniqueness)
            symbolic_score = row.get("token_complexity", 0) + row.get("wallet_diversity", 0)  # Business-friendly terms
            
            # Calculate market momentum score
            momentum_score = row.get("price_change_24h", 0) * 0.4 + row.get("volume_change_24h", 0) * 0.6
            
            model_score = model_scores[idx] if model_scores is not None else 0
            
            # Calculate hybrid score
            hybrid_score_value = 0
            if ranking_request.include_symbolic and ranking_request.include_ml:
                weights = ranking_request.weights or {"symbolic": 0.5, "ml": 0.5}
                hybrid_score_value = (
                    weights.get("symbolic", 0.5) * symbolic_score +
                    weights.get("ml", 0.5) * model_score
                )
            elif ranking_request.include_symbolic:
                hybrid_score_value = symbolic_score
            else:
                hybrid_score_value = model_score
            
            results.append({
                "wallet": row["wallet"],
                "token_id": row["token_id"],
                "hybrid_score": float(hybrid_score_value),
                "model_score": float(model_score) if model_scores is not None else None,
                "symbolic_score": float(symbolic_score) if ranking_request.include_symbolic else None
            })
        
        # Sort results by hybrid score
        results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        
        # Add ranks
        for i, result in enumerate(results, 1):
            result["rank"] = i
        
        # Update job with results
        job.results = results
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow().timestamp()
        
        # Save final results
        await batch_job_store.update_job(job_id, job.to_dict())
        
        # Notify WebSocket subscribers of completion
        await ws_manager.update_job_progress(
            job_id=job_id,
            progress=job.total,
            total=job.total,
            status=job.status,
            message="Batch processing completed successfully"
        )
        
    except Exception as e:
        logging.error(f"Error processing batch ranking job {job_id}: {str(e)}", exc_info=True)
        if job_id in batch_jobs:
            job = batch_jobs[job_id]
        job.status = JobStatus.FAILED
        error_msg = str(e)
        job.error = error_msg
        job.completed_at = datetime.utcnow().timestamp()
        await batch_job_store.update_job(job_id, job.to_dict())
        
        # Notify WebSocket subscribers of failure
        await ws_manager.update_job_progress(
            job_id=job_id,
            progress=job.progress,
            total=job.total,
            status=job.status,
            message=f"Batch processing failed: {error_msg}"
        )

@router.post("/batch", status_code=202)
async def create_batch_ranking(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    ranking_request: RankingRequest = None
):
    """
    Create a new batch ranking job.
    
    Upload a CSV file with wallet addresses and token IDs to rank them.
    The endpoint returns a job ID that can be used to check the status and retrieve results.
    """
    if ranking_request is None:
        ranking_request = RankingRequest()
    
    try:
        # Read and validate the CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = ["wallet", "token_id", "timestamp"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Create a new job
        job_id = str(uuid.uuid4())
        job = BatchRankingJob(
            job_id=job_id,
            status=JobStatus.PENDING,
            created_at=datetime.utcnow().timestamp(),
            total=len(df)
        )
        
        # Store job in memory and persistent storage
        batch_jobs[job_id] = job
        await batch_job_store.create_job(job_id, job.to_dict())
        
        # Generate a client ID for WebSocket tracking
        client_id = str(uuid.uuid4())
        
        # Start background processing
        background_tasks.add_task(
            process_ranking_batch, 
            job_id, 
            df, 
            ranking_request,
            client_id
        )
        
        # Return job information
        base_url = str(request.base_url).rstrip('/')
        response = {
            "job_id": job_id,
            "status": job.status,
            "created_at": job.created_at,
            "status_url": f"{base_url}/api/v1/ranking/batch/{job_id}",
            "results_url": f"{base_url}/api/v1/ranking/batch/{job_id}/results",
            "websocket_url": f"{base_url.replace('http', 'ws')}/api/v1/ranking/ws/{job_id}"
        }
        
        return response
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    except Exception as e:
        logging.error(f"Error creating batch ranking job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch/{job_id}")
async def get_batch_ranking_status(job_id: str):
    """
    Get the status of a batch ranking job.
    """
    try:
        # Try to get from memory first
        job = batch_jobs.get(job_id)
        
        # If not in memory, try to load from persistent storage
        if not job:
            job_data = await batch_job_store.get_job(job_id)
            if not job_data:
                raise HTTPException(status_code=404, detail="Job not found")
            job = BatchRankingJob(**job_data)
            batch_jobs[job_id] = job
        
        return job.to_dict()
        
    except Exception as e:
        logging.error(f"Error getting batch ranking status {job_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch/{job_id}/results")
async def get_batch_ranking_results(job_id: str):
    """
    Get the results of a completed batch ranking job.
    """
    try:
        # Try to get from memory first
        job = batch_jobs.get(job_id)
        
        # If not in memory, try to load from persistent storage
        if not job:
            job_data = await batch_job_store.get_job(job_id)
            if not job_data:
                raise HTTPException(status_code=404, detail="Job not found")
            job = BatchRankingJob(**job_data)
            batch_jobs[job_id] = job
        
        # Check if job is completed
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Job is not completed. Current status: {job.status}"
            )
        
        if not job.results:
            raise HTTPException(status_code=404, detail="No results found for this job")
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "results": job.results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting batch ranking results {job_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{job_id}")
async def websocket_ranking_updates(
    websocket: WebSocket,
    job_id: str,
    token: str = None
):
    """
    WebSocket endpoint for real-time batch ranking updates.
    
    Clients can connect to this endpoint to receive real-time updates about
    the status of a batch ranking job, including progress and completion.
    
    Args:
        job_id: The ID of the batch job to monitor
        token: Optional authentication token (not implemented)
    """
    # Generate a unique client ID
    client_id = f"ws_{job_id}_{int(time.time())}"
    
    try:
        # Accept the WebSocket connection
        await ws_manager.connect(client_id, websocket)
        
        # Subscribe to job updates
        await ws_manager.subscribe_to_job(client_id, job_id)
        
        # Get current job status
        job = batch_jobs.get(job_id)
        if not job:
            job_data = await batch_job_store.get_job(job_id)
            if not job_data:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Job {job_id} not found",
                    "timestamp": datetime.utcnow().isoformat()
                })
                return
            job = BatchRankingJob(**job_data)
            batch_jobs[job_id] = job
        
        # Send initial status
        await ws_manager.update_job_progress(
            job_id=job_id,
            progress=job.progress,
            total=job.total,
            status=job.status,
            message=f"Connected to job {job_id}"
        )
        
        # Keep connection alive and process messages
        last_activity = time.time()
        while True:
            try:
                # Set a timeout for receiving messages
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0
                )
                last_activity = time.time()
                
                # Handle ping/pong
                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                # Handle other message types here if needed
                
            except asyncio.TimeoutError:
                # Check if connection has been inactive for too long
                if time.time() - last_activity > WEBSOCKET_TIMEOUT:
                    logger.info(f"Closing idle WebSocket connection {client_id}")
                    break
                
                # Send a heartbeat to keep the connection alive
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            except WebSocketDisconnect:
                logger.info(f"Client {client_id} disconnected")
                break
                
            except Exception as e:
                logger.error(f"WebSocket error for {client_id}: {str(e)}")
                break
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected during connection")
        
    except Exception as e:
        logger.error(f"Error in WebSocket connection {client_id}: {str(e)}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Internal server error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })
        except:
            pass
            
    finally:
        # Clean up
        try:
            await ws_manager.disconnect(client_id)
        except Exception as e:
            logger.error(f"Error during WebSocket cleanup for {client_id}: {str(e)}")
            
        logger.info(f"WebSocket connection closed for {client_id}")
