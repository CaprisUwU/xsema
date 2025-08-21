"""
Model Registry API Endpoints

Provides endpoints for managing model versions, promoting to production,
and retrieving model information.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import os

from services.model_registry import model_registry, ModelMetadata

router = APIRouter(prefix="/registry", tags=["model_registry"])

class ModelVersionResponse(BaseModel):
    """Response model for model version information."""
    model_id: str
    name: str
    version: str
    created_at: str
    is_production: bool
    metrics: Dict[str, float] = {}
    description: str = ""

class RegisterModelRequest(BaseModel):
    """Request model for registering a new model version."""
    name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version string (e.g., '1.0.0')")
    model_type: str = Field(..., description="Type of model")
    model_path: str = Field(..., description="Path to the model file")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Evaluation metrics")
    feature_importances: Dict[str, float] = Field(default_factory=dict, description="Feature importances")
    tags: List[str] = Field(default_factory=list, description="Tags for the model")
    description: str = Field(default="", description="Description of the model")
    training_params: Dict[str, Any] = Field(default_factory=dict, description="Training parameters")
    dataset_info: Dict[str, Any] = Field(default_factory=dict, description="Dataset information")
    is_production: bool = Field(default=False, description="Set as production model")

@router.post("/models", response_model=ModelVersionResponse)
async def register_model(request: RegisterModelRequest):
    """
    Register a new model version in the registry.
    
    This endpoint registers a trained model with its metadata and optionally
    sets it as the production version.
    """
    try:
        # Verify model file exists
        if not os.path.exists(request.model_path):
            raise HTTPException(
                status_code=400,
                detail=f"Model file not found at {request.model_path}"
            )
        
        # Register the model
        model_id = model_registry.register_model(
            name=request.name,
            version=request.version,
            model_type=request.model_type,
            model_path=request.model_path,
            metrics=request.metrics,
            feature_importances=request.feature_importances,
            tags=request.tags,
            description=request.description,
            training_params=request.training_params,
            dataset_info=request.dataset_info,
            is_production=request.is_production
        )
        
        # Get the registered model info
        model_info = model_registry.get_model(model_id)
        if not model_info:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve registered model information"
            )
            
        return model_info
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register model: {str(e)}")

@router.get("/models", response_model=List[ModelVersionResponse])
async def list_models(
    name: Optional[str] = Query(None, description="Filter by model name"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    List all registered models with optional filtering.
    
    Returns a paginated list of model versions that match the specified filters.
    """
    try:
        models = model_registry.list_models(
            name=name,
            tags=tags,
            limit=limit,
            offset=offset
        )
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

@router.get("/models/{model_id}", response_model=ModelVersionResponse)
async def get_model(model_id: str):
    """
    Get detailed information about a specific model version.
    
    Returns metadata, metrics, and configuration for the specified model.
    """
    model_info = model_registry.get_model(model_id)
    if not model_info:
        raise HTTPException(status_code=404, detail="Model not found")
    return model_info

@router.post("/models/{model_id}/production", response_model=ModelVersionResponse)
async def set_production_model(model_id: str):
    """
    Set a specific model version as the production version.
    
    This will unset the production flag from any other versions of the same model.
    """
    if not model_registry.set_production(model_id):
        raise HTTPException(status_code=404, detail="Model not found")
    
    model_info = model_registry.get_model(model_id)
    if not model_info:
        raise HTTPException(status_code=500, detail="Failed to retrieve model information")
        
    return model_info

@router.get("/models/name/{model_name}/production", response_model=ModelVersionResponse)
async def get_production_model(model_name: str):
    """
    Get the current production version of a model.
    
    Returns the production model for the specified model name.
    """
    model_info = model_registry.get_production_model(model_name)
    if not model_info:
        raise HTTPException(
            status_code=404,
            detail=f"No production model found for {model_name}"
        )
    return model_info

@router.delete("/models/{model_id}", status_code=204)
async def delete_model(model_id: str):
    """
    Delete a model version from the registry.
    
    This will permanently remove the model and its metadata.
    Cannot delete the current production model.
    """
    try:
        if not model_registry.delete_model(model_id):
            raise HTTPException(status_code=404, detail="Model not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
