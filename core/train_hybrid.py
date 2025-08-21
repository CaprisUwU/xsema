"""
Training Pipeline for Hybrid Symbolic-Statistical Model

This module handles the training and evaluation of our hybrid model,
including data loading, preprocessing, training, and validation.
"""
import os
import json
import joblib
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas as pd

from .hybrid_model import HybridModel, ModelConfig
from utils.logger import get_logger

logger = get_logger(__name__)

class HybridModelTrainer:
    """Handles training and evaluation of the hybrid model."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the trainer with optional config."""
        self.config = self._load_config(config_path)
        self.model = HybridModel(self.config)
        self.metrics = {}
        self.training_history = []
        
    def _load_config(self, config_path: Optional[str] = None) -> ModelConfig:
        """Load configuration from file or use defaults."""
        if config_path and os.path.exists(config_path):
            return ModelConfig.load(config_path)
        return ModelConfig()
    
    def prepare_data(self, data_path: str, test_size: float = 0.2, random_state: int = 42) -> Tuple:
        """
        Prepare training and testing data.
        
        Args:
            data_path: Path to the training data file
            test_size: Fraction of data to use for testing
            random_state: Random seed for reproducibility
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Load and preprocess data
        # Note: This is a placeholder - implement actual data loading
        # based on your data format
        if data_path.endswith('.json'):
            with open(data_path, 'r') as f:
                data = json.load(f)
            X = data.get('features', [])
            y = data.get('targets', [])
        else:
            # Assume CSV with features and target columns
            df = pd.read_csv(data_path)
            X = df.drop('target', axis=1).to_dict('records')
            y = df['target'].values
        
        # Split into train/test
        return train_test_split(X, y, test_size=test_size, random_state=random_state)
    
    def train(self, X_train: List[Dict], y_train: List[float], 
              X_val: Optional[List[Dict]] = None, y_val: Optional[List[float]] = None):
        """
        Train the hybrid model.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Optional validation features
            y_val: Optional validation targets
        """
        logger.info("Starting model training...")
        start_time = datetime.now()
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        # Calculate training metrics
        train_pred = self.model.predict(X_train)
        train_metrics = self._calculate_metrics(y_train, train_pred, 'train')
        
        # Calculate validation metrics if validation data is provided
        val_metrics = {}
        if X_val is not None and y_val is not None:
            val_pred = self.model.predict(X_val)
            val_metrics = self._calculate_metrics(y_val, val_pred, 'val')
        
        # Log metrics
        self.metrics = {**train_metrics, **val_metrics}
        training_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Training completed in {training_time:.2f} seconds")
        logger.info(f"Training metrics: {train_metrics}")
        if val_metrics:
            logger.info(f"Validation metrics: {val_metrics}")
        
        # Save training record
        self.training_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': self.metrics,
            'training_time_seconds': training_time,
            'config': self.config.__dict__
        })
        
        return self.metrics
    
    def evaluate(self, X: List[Dict], y: List[float], prefix: str = 'test') -> Dict[str, float]:
        """
        Evaluate the model on test data.
        
        Args:
            X: Test features
            y: True target values
            prefix: Prefix for metric names
            
        Returns:
            Dictionary of evaluation metrics
        """
        y_pred = self.model.predict(X)
        metrics = self._calculate_metrics(y, y_pred, prefix)
        
        # Update metrics
        self.metrics.update(metrics)
        return metrics
    
    def _calculate_metrics(self, y_true: List[float], y_pred: List[float], 
                          prefix: str = '') -> Dict[str, float]:
        """Calculate evaluation metrics."""
        prefix = f"{prefix}_" if prefix else ""
        
        return {
            f"{prefix}mse": mean_squared_error(y_true, y_pred),
            f"{prefix}rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
            f"{prefix}mae": mean_absolute_error(y_true, y_pred),
            f"{prefix}r2": r2_score(y_true, y_pred)
        }
    
    def save_model(self, output_dir: str, model_name: str = 'hybrid_model'):
        """
        Save the trained model and training artifacts.
        
        Args:
            output_dir: Directory to save the model
            model_name: Base name for model files
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Save model
        model_path = os.path.join(output_dir, f"{model_name}.joblib")
        self.model.save(model_path)
        
        # Save training history
        history_path = os.path.join(output_dir, f"{model_name}_history.json")
        with open(history_path, 'w') as f:
            json.dump(self.training_history, f, indent=2)
        
        # Save metrics
        metrics_path = os.path.join(output_dir, f"{model_name}_metrics.json")
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        logger.info(f"Model saved to {model_path}")
        logger.info(f"Training history saved to {history_path}")
        logger.info(f"Metrics saved to {metrics_path}")
    
    @classmethod
    def load_model(cls, model_path: str, config_path: Optional[str] = None) -> 'HybridModelTrainer':
        """
        Load a trained model.
        
        Args:
            model_path: Path to the saved model
            config_path: Optional path to model config
            
        Returns:
            Instance of HybridModelTrainer with loaded model
        """
        trainer = cls(config_path)
        trainer.model = HybridModel.load(model_path)
        return trainer

# Example usage
if __name__ == "__main__":
    # Initialize trainer
    trainer = HybridModelTrainer()
    
    # Prepare data (replace with actual data loading)
    X_train, X_test, y_train, y_test = trainer.prepare_data("data/training_data.json")
    
    # Train model
    metrics = trainer.train(X_train, y_train, X_test, y_test)
    
    # Evaluate on test set
    test_metrics = trainer.evaluate(X_test, y_test)
    print(f"Test metrics: {test_metrics}")
    
    # Save model
    trainer.save_model("models", "nft_hybrid_model")
