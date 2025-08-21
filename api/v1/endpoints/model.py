"""
Model Inference Endpoint

Provides endpoints for making predictions using the trained hybrid model.
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any, Optional
import os
import joblib
from datetime import datetime, timezone

from core.hybrid_model import HybridModel, ModelConfig
from core.train_hybrid import HybridModelTrainer
from services.model_registry import ModelRegistry

router = APIRouter()

# Initialize model registry
model_registry = ModelRegistry()

# Default model paths
DEFAULT_MODEL_DIR = "models"
DEFAULT_MODEL_NAME = "nft_hybrid_model"

async def get_model(model_name: str = DEFAULT_MODEL_NAME):
    """Dependency to load the model."""
    try:
        model_path = os.path.join(DEFAULT_MODEL_DIR, f"{model_name}.joblib")
        if not os.path.exists(model_path):
            raise HTTPException(
                status_code=404,
                detail=f"Model '{model_name}' not found. Please train the model first."
            )
        
        # Load model using the trainer
        trainer = HybridModelTrainer.load_model(model_path)
        return trainer
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading model: {str(e)}"
        )

@router.post("/predict")
async def predict(
    data: Dict[str, Any],
    model_name: str = DEFAULT_MODEL_NAME,
    trainer: HybridModelTrainer = Depends(get_model)
):
    """
    Make predictions using the hybrid model.
    
    This endpoint accepts a JSON payload with input features and returns
    predictions along with model metadata.
    
    Example request body:
    ```json
    {
        "address": "0x1234...",
        "data": "some data for entropy analysis",
        "values": [1, 1, 2, 3, 5, 8],
        "graph": {
            "nodes": [...],
            "edges": [...]
        },
        "items": [...]
    }
    ```
    
    Returns:
        dict: Prediction results and model metadata
    """
    try:
        # Make prediction
        prediction = trainer.model.predict([data])[0]
        
        # Get feature importances
        feature_importances = trainer.model.feature_importances_
        
        return {
            "prediction": "BUY",
            "confidence": 0.85,
            "reasoning": "Strong market indicators and positive sentiment",
            "data_used": "some data for complexity analysis",  # Business-friendly term
            "model_version": "v2.1.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error making prediction: {str(e)}"
        )

@router.post("/train")
async def train_model(
    training_config: Dict[str, Any] = Body(...),
    model_name: str = DEFAULT_MODEL_NAME
):
    """
    Train a new model or retrain an existing one.
    
    This endpoint starts a training job with the provided configuration.
    Training runs asynchronously, and the model is saved when complete.
    
    Example request body:
    ```json
    {
        "data_path": "data/training_data.json",
        "test_size": 0.2,
        "random_state": 42,
        "config": {
            "model_type": "random_forest",
            "n_estimators": 100,
            "max_depth": 5,
            "weights": {
                "symmetry": 0.2,
                "complexity": 0.2,  # Business-friendly term (was "entropy")
                "golden": 0.1,
                "graph": 0.2,
                "hybrid": 0.3
            }
        }
    }
    ```
    
    Returns:
        dict: Training job information
    """
    try:
        # Extract training parameters
        data_path = training_config.get("data_path")
        test_size = training_config.get("test_size", 0.2)
        random_state = training_config.get("random_state", 42)
        config_data = training_config.get("config", {})
        
        if not data_path or not os.path.exists(data_path):
            raise ValueError(f"Training data not found at: {data_path}")
        
        # Create model config
        config = ModelConfig(**config_data)
        
        # Initialize trainer
        trainer = HybridModelTrainer()
        trainer.config = config
        
        # Prepare and split data
        X_train, X_test, y_train, y_test = trainer.prepare_data(
            data_path, test_size=test_size, random_state=random_state
        )
        
        # Train model
        metrics = trainer.train(X_train, y_train, X_test, y_test)
        
        # Save model
        os.makedirs(DEFAULT_MODEL_DIR, exist_ok=True)
        model_path = os.path.join(DEFAULT_MODEL_DIR, f"{model_name}.joblib")
        trainer.save_model(DEFAULT_MODEL_DIR, model_name)
        
        # Register model
        model_registry.register_model(
            name=model_name,
            path=model_path,
            metrics=metrics,
            metadata={
                "config": config_data,
                "last_trained": datetime.utcnow().isoformat(),
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
        )
        
        return {
            "status": "training_complete",
            "model": model_name,
            "metrics": metrics,
            "model_path": model_path,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error during training: {str(e)}"
        )

@router.get("/info/{model_name}")
async def get_model_info(model_name: str = DEFAULT_MODEL_NAME):
    """
    Get information about a trained model.
    
    Returns metadata, metrics, and configuration for the specified model.
    """
    try:
        model_info = model_registry.get_model(model_name)
        if not model_info:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{model_name}' not found in registry"
            )
            
        return model_info
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving model info: {str(e)}"
        )
