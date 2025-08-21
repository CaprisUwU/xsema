"""
Model Registry Service

Manages the lifecycle of trained models, including registration, versioning,
and retrieval of model metadata and artifacts.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import shutil
from dataclasses import asdict

from pydantic import BaseModel, Field

# Default registry path
REGISTRY_PATH = Path("data/models/registry.json")
MODELS_DIR = Path("data/models")

# Ensure directories exist
os.makedirs(MODELS_DIR, exist_ok=True)

class ModelMetadata(BaseModel):
    """Metadata for a trained model."""
    model_id: str
    name: str
    version: str
    path: str
    model_type: str
    created_at: str
    last_updated: str
    metrics: Dict[str, float] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    description: str = ""
    is_production: bool = False
    feature_importances: Dict[str, float] = Field(default_factory=dict)
    training_params: Dict[str, Any] = Field(default_factory=dict)
    dataset_info: Dict[str, Any] = Field(default_factory=dict)

class ModelRegistry:
    """Manages the model registry and model artifacts."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize the model registry."""
        self.registry_path = registry_path or REGISTRY_PATH
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, dict]:
        """Load the model registry from disk."""
        if not self.registry_path.exists():
            return {}
        
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
        except Exception as e:
            raise RuntimeError(f"Failed to load model registry: {str(e)}")
    
    def _save_registry(self):
        """Save the model registry to disk."""
        try:
            temp_path = f"{self.registry_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(self._registry, f, indent=2, default=str)
            
            # Atomic write
            if os.path.exists(self.registry_path):
                os.remove(self.registry_path)
            os.rename(temp_path, self.registry_path)
            
        except Exception as e:
            raise RuntimeError(f"Failed to save model registry: {str(e)}")
    
    def register_model(
        self,
        name: str,
        version: str,
        model_type: str,
        model_path: Union[str, Path],
        metrics: Optional[Dict[str, float]] = None,
        feature_importances: Optional[Dict[str, float]] = None,
        tags: Optional[List[str]] = None,
        description: str = "",
        training_params: Optional[Dict[str, Any]] = None,
        dataset_info: Optional[Dict[str, Any]] = None,
        is_production: bool = False
    ) -> str:
        """
        Register a new model in the registry.
        
        Args:
            name: Name of the model
            version: Version string (e.g., '1.0.0')
            model_type: Type of model (e.g., 'random_forest', 'gradient_boosting')
            model_path: Path to the model file
            metrics: Dictionary of evaluation metrics
            feature_importances: Dictionary of feature importances
            tags: List of tags for the model
            description: Description of the model
            training_params: Parameters used during training
            dataset_info: Information about the training dataset
            is_production: Whether this is a production model
            
        Returns:
            str: The model ID
        """
        # Generate a unique model ID
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_id = f"{name.lower()}_{timestamp}"
        
        # Create destination directory
        model_dir = MODELS_DIR / model_id
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy model file to registry
        dest_path = model_dir / Path(model_path).name
        shutil.copy2(model_path, dest_path)
        
        # Create metadata
        metadata = ModelMetadata(
            model_id=model_id,
            name=name,
            version=version,
            path=str(dest_path.absolute()),
            model_type=model_type,
            created_at=datetime.utcnow().isoformat(),
            last_updated=datetime.utcnow().isoformat(),
            metrics=metrics or {},
            feature_importances=feature_importances or {},
            tags=tags or [],
            description=description,
            training_params=training_params or {},
            dataset_info=dataset_info or {},
            is_production=is_production
        )
        
        # Save metadata
        metadata_path = model_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata.model_dump(), f, indent=2)
        
        # Update registry
        self._registry[model_id] = {
            "id": model_id,
            "name": name,
            "version": version,
            "path": str(dest_path.absolute()),
            "metadata_path": str(metadata_path.absolute()),
            "created_at": datetime.utcnow().isoformat(),
            "is_production": is_production
        }
        
        # If this is a production model, unset production flag on others
        if is_production:
            self._unset_production_flag(name)
        
        self._save_registry()
        return model_id
    
    def _unset_production_flag(self, model_name: str):
        """Unset production flag for all versions of a model."""
        for model_id, model_info in self._registry.items():
            if model_info["name"] == model_name and model_info.get("is_production", False):
                model_info["is_production"] = False
                
                # Update metadata file
                metadata_path = Path(model_info.get("metadata_path", ""))
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    metadata["is_production"] = False
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
    
    def get_model(self, model_id: str) -> Optional[Dict]:
        """
        Get a model by ID.
        
        Args:
            model_id: ID of the model to retrieve
            
        Returns:
            Optional[Dict]: Model metadata if found, None otherwise
        """
        model_info = self._registry.get(model_id)
        if not model_info:
            return None
            
        metadata_path = Path(model_info.get("metadata_path", ""))
        if not metadata_path.exists():
            return None
            
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def get_production_model(self, name: str) -> Optional[Dict]:
        """
        Get the current production model for a given name.
        
        Args:
            name: Name of the model
            
        Returns:
            Optional[Dict]: Production model metadata if found, None otherwise
        """
        for model_id, model_info in self._registry.items():
            if model_info["name"] == name and model_info.get("is_production", False):
                return self.get_model(model_id)
        return None
    
    def list_models(
        self, 
        name: Optional[str] = None, 
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        List models in the registry with optional filtering.
        
        Args:
            name: Filter by model name
            tags: Filter by tags
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List[Dict]: List of model metadata
        """
        results = []
        
        for model_id in sorted(self._registry.keys(), reverse=True):
            if len(results) >= limit + offset:
                break
                
            model_info = self._registry[model_id]
            
            # Apply filters
            if name and model_info["name"] != name:
                continue
                
            if tags and not all(tag in model_info.get("tags", []) for tag in tags):
                continue
                
            results.append(self.get_model(model_id))
        
        return results[offset:offset+limit]
    
    def set_production(self, model_id: str) -> bool:
        """
        Set a model as the production version.
        
        Args:
            model_id: ID of the model to set as production
            
        Returns:
            bool: True if successful, False if model not found
        """
        if model_id not in self._registry:
            return False
            
        model_info = self._registry[model_id]
        
        # Unset production flag for other versions
        self._unset_production_flag(model_info["name"])
        
        # Set production flag
        self._registry[model_id]["is_production"] = True
        
        # Update metadata
        metadata_path = Path(model_info.get("metadata_path", ""))
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            metadata["is_production"] = True
            metadata["last_updated"] = datetime.utcnow().isoformat()
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        self._save_registry()
        return True
    
    def delete_model(self, model_id: str) -> bool:
        """
        Delete a model from the registry.
        
        Args:
            model_id: ID of the model to delete
            
        Returns:
            bool: True if successful, False if model not found
        """
        if model_id not in self._registry:
            return False
            
        # Don't allow deletion of production models
        if self._registry[model_id].get("is_production", False):
            raise ValueError("Cannot delete a production model. Set another model as production first.")
        
        # Remove model directory
        model_dir = MODELS_DIR / model_id
        if model_dir.exists():
            shutil.rmtree(model_dir)
        
        # Remove from registry
        del self._registry[model_id]
        self._save_registry()
        
        return True

# Singleton instance
model_registry = ModelRegistry()

def load_model_registry() -> ModelRegistry:
    """
    Get the singleton model registry instance.
    
    Returns:
        ModelRegistry: The singleton model registry instance
    """
    return model_registry

def register_model(model_metadata: Dict[str, Any], model_path: Optional[Path] = None) -> str:
    """
    Register a new model in the registry.
    
    Args:
        model_metadata: Dictionary containing model metadata
        model_path: Optional path to the model file to be copied to the registry
        
    Returns:
        str: The model ID of the registered model
    """
    # Create a ModelMetadata object from the dictionary
    metadata = ModelMetadata(**model_metadata)
    
    # If a model file is provided, copy it to the models directory
    if model_path and model_path.exists():
        # Create a unique filename for the model
        model_filename = f"{metadata.model_id}_{metadata.version}.pkl"
        dest_path = MODELS_DIR / model_filename
        shutil.copy2(model_path, dest_path)
        
        # Update the model path in the metadata
        metadata.path = str(dest_path)
    
    # Add or update the model in the registry
    model_registry._registry[metadata.model_id] = metadata.dict()
    model_registry._save_registry()
    
    return metadata.model_id



