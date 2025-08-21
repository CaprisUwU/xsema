import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

REGISTRY_PATH = Path("model_registry.json")

def load_model_registry() -> dict:
    """
    Load the model registry from file.
    
    Returns:
        dict: Model registry dictionary
    """
    if not REGISTRY_PATH.exists():
        return {}
    
    try:
        with open(REGISTRY_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
    except Exception as e:
        raise RuntimeError(f"Failed to load model registry: {str(e)}")

def save_model_registry(registry: dict) -> None:
    """
    Save model registry to JSON file.
    
    Args:
        registry: Model registry dictionary
    """
    try:
        with open(REGISTRY_PATH, "w") as f:
            json.dump(registry, f, indent=4)
    except Exception as e:
        raise RuntimeError(f"Failed to save model registry: {str(e)}")

def get_model_by_id(model_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a model by its ID.
    
    Args:
        model_id: ID of the model to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: Model entry if found, None otherwise
    """
    registry = load_model_registry()
    return registry.get(model_id)

def update_model_status(model_id: str, status: str) -> None:
    """
    Update the status of a model.
    
    Args:
        model_id: ID of the model to update
        status: New status (e.g., "active", "inactive")
    """
    registry = load_model_registry()
    if model_id not in registry:
        raise ValueError(f"Model with ID '{model_id}' not found")
    
    registry[model_id]["status"] = status
    save_model_registry(registry)
