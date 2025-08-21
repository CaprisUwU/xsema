"""
Automated ML Model Retraining Pipeline for XSEMA

This module provides:
- Scheduled model retraining
- Performance monitoring and comparison
- Automated model deployment
- A/B testing capabilities
- Model versioning and rollback
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import pickle
import shutil

from core.logging_config import get_logger, log_performance_metric
from core.ml.model_registry import ModelRegistry
from core.ml.hybrid_model import HybridModel
from core.ml.features import FeatureEngineer
from core.ml.scoring import ScoringSystem

logger = get_logger("retraining_pipeline")

@dataclass
class TrainingConfig:
    """Configuration for model training."""
    model_type: str = "hybrid"
    batch_size: int = 32
    epochs: int = 100
    learning_rate: float = 0.001
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    min_delta: float = 0.001

@dataclass
class ModelPerformance:
    """Model performance metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_score: float
    training_time: float
    inference_time: float
    model_size_mb: float
    timestamp: datetime

class AutomatedRetrainingPipeline:
    """Automated pipeline for ML model retraining and deployment."""
    
    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        self.model_registry = ModelRegistry()
        self.feature_engineer = FeatureEngineer()
        self.scoring_system = ScoringSystem()
        
        # Pipeline state
        self.is_training = False
        self.last_training = None
        self.training_schedule = "weekly"  # daily, weekly, monthly
        self.performance_threshold = 0.02  # 2% improvement required
        
        # Model versions
        self.current_model_version = None
        self.previous_model_version = None
        
        logger.info("Automated retraining pipeline initialized")
    
    async def start_scheduled_training(self):
        """Start the scheduled training loop."""
        logger.info("Starting scheduled training loop")
        
        while True:
            try:
                if self._should_retrain():
                    await self._execute_training_cycle()
                
                # Wait for next check (check every hour)
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in scheduled training: {e}")
                await asyncio.sleep(3600)  # Wait before retry
    
    def _should_retrain(self) -> bool:
        """Determine if retraining is needed."""
        if self.is_training:
            return False
        
        if not self.last_training:
            return True
        
        # Check schedule
        now = datetime.utcnow()
        if self.training_schedule == "daily":
            return (now - self.last_training).days >= 1
        elif self.training_schedule == "weekly":
            return (now - self.last_training).days >= 7
        elif self.training_schedule == "monthly":
            return (now - self.last_training).days >= 30
        
        return False
    
    async def _execute_training_cycle(self):
        """Execute a complete training cycle."""
        logger.info("Starting training cycle")
        self.is_training = True
        
        try:
            # 1. Data preparation
            training_data = await self._prepare_training_data()
            
            # 2. Model training
            new_model, training_metrics = await self._train_model(training_data)
            
            # 3. Performance evaluation
            new_performance = await self._evaluate_model(new_model)
            
            # 4. Performance comparison
            if await self._should_deploy_model(new_performance):
                await self._deploy_model(new_model, new_performance)
            else:
                logger.info("New model performance below threshold, keeping current model")
            
            # 5. Update pipeline state
            self.last_training = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Training cycle failed: {e}")
        finally:
            self.is_training = False
    
    async def _prepare_training_data(self) -> Dict[str, Any]:
        """Prepare training data from various sources."""
        logger.info("Preparing training data")
        
        # This would integrate with your data sources
        # For now, using mock data structure
        training_data = {
            "features": [],
            "labels": [],
            "metadata": {
                "data_source": "blockchain_events",
                "collection_size": 10000,
                "feature_count": 50,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"Training data prepared: {training_data['metadata']}")
        return training_data
    
    async def _train_model(self, training_data: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
        """Train the ML model."""
        logger.info("Starting model training")
        start_time = time.time()
        
        try:
            # Initialize model
            if self.config.model_type == "hybrid":
                model = HybridModel()
            else:
                raise ValueError(f"Unsupported model type: {self.config.model_type}")
            
            # Train model (this would use your actual training logic)
            training_metrics = {
                "epochs_completed": self.config.epochs,
                "final_loss": 0.1,
                "final_accuracy": 0.95,
                "training_time": 0
            }
            
            training_time = time.time() - start_time
            training_metrics["training_time"] = training_time
            
            log_performance_metric("model_training", training_time * 1000, **training_metrics)
            
            logger.info(f"Model training completed in {training_time:.2f}s")
            return model, training_metrics
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise
    
    async def _evaluate_model(self, model: Any) -> ModelPerformance:
        """Evaluate model performance on test data."""
        logger.info("Evaluating model performance")
        
        # This would use your actual evaluation logic
        # For now, using mock metrics
        performance = ModelPerformance(
            accuracy=0.95,
            precision=0.94,
            recall=0.93,
            f1_score=0.935,
            auc_score=0.96,
            training_time=0,
            inference_time=0.001,  # 1ms
            model_size_mb=15.5,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Model evaluation completed: accuracy={performance.accuracy:.3f}")
        return performance
    
    async def _should_deploy_model(self, new_performance: ModelPerformance) -> bool:
        """Determine if new model should be deployed."""
        if not self.current_model_version:
            logger.info("No current model, deploying new model")
            return True
        
        # Get current model performance
        current_performance = await self._get_current_model_performance()
        if not current_performance:
            logger.info("No current performance data, deploying new model")
            return True
        
        # Calculate improvement
        accuracy_improvement = new_performance.accuracy - current_performance.accuracy
        
        logger.info(f"Performance comparison: current={current_performance.accuracy:.3f}, "
                   f"new={new_performance.accuracy:.3f}, improvement={accuracy_improvement:.3f}")
        
        return accuracy_improvement >= self.performance_threshold
    
    async def _deploy_model(self, model: Any, performance: ModelPerformance):
        """Deploy the new model."""
        logger.info("Deploying new model")
        
        try:
            # 1. Save current model as backup
            if self.current_model_version:
                await self._backup_current_model()
            
            # 2. Save new model
            new_version = await self._save_model(model, performance)
            
            # 3. Update model registry
            await self._update_model_registry(new_version, performance)
            
            # 4. Update pipeline state
            self.previous_model_version = self.current_model_version
            self.current_model_version = new_version
            
            # 5. Notify deployment
            await self._notify_model_deployment(new_version, performance)
            
            logger.info(f"Model deployed successfully: version={new_version}")
            
        except Exception as e:
            logger.error(f"Model deployment failed: {e}")
            # Rollback if possible
            await self._rollback_deployment()
            raise
    
    async def _backup_current_model(self):
        """Backup the current model."""
        if not self.current_model_version:
            return
        
        backup_path = Path(f"models/backup/{self.current_model_version}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy current model files
        current_path = Path(f"models/{self.current_model_version}")
        if current_path.exists():
            shutil.copytree(current_path, backup_path, dirs_exist_ok=True)
            logger.info(f"Current model backed up to {backup_path}")
    
    async def _save_model(self, model: Any, performance: ModelPerformance) -> str:
        """Save the trained model."""
        # Generate version ID
        version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        model_path = Path(f"models/{version}")
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Save model files
        model_file = model_path / "model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        
        # Save performance metrics
        perf_file = model_path / "performance.json"
        with open(perf_file, 'w') as f:
            json.dump({
                "accuracy": performance.accuracy,
                "precision": performance.precision,
                "recall": performance.recall,
                "f1_score": performance.f1_score,
                "auc_score": performance.auc_score,
                "training_time": performance.training_time,
                "inference_time": performance.inference_time,
                "model_size_mb": performance.model_size_mb,
                "timestamp": performance.timestamp.isoformat()
            }, f, indent=2)
        
        # Save model metadata
        metadata_file = model_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump({
                "version": version,
                "model_type": self.config.model_type,
                "training_config": {
                    "batch_size": self.config.batch_size,
                    "epochs": self.config.epochs,
                    "learning_rate": self.config.learning_rate
                },
                "created_at": datetime.utcnow().isoformat()
            }, f, indent=2)
        
        logger.info(f"Model saved to {model_path}")
        return version
    
    async def _update_model_registry(self, version: str, performance: ModelPerformance):
        """Update the model registry with new model."""
        await self.model_registry.register_model(
            version=version,
            performance_metrics=performance,
            deployment_status="active"
        )
        logger.info(f"Model registry updated: {version}")
    
    async def _notify_model_deployment(self, version: str, performance: ModelPerformance):
        """Notify stakeholders about model deployment."""
        # This could send emails, Slack messages, etc.
        deployment_notification = {
            "event": "model_deployed",
            "version": version,
            "performance": {
                "accuracy": performance.accuracy,
                "improvement": "calculated_improvement"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Model deployment notification: {deployment_notification}")
    
    async def _rollback_deployment(self):
        """Rollback to previous model version."""
        if not self.previous_model_version:
            logger.warning("No previous model version available for rollback")
            return
        
        try:
            # Restore previous model
            self.current_model_version = self.previous_model_version
            await self.model_registry.set_active_model(self.previous_model_version)
            
            logger.info(f"Rollback completed: restored {self.previous_model_version}")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
    
    async def _get_current_model_performance(self) -> Optional[ModelPerformance]:
        """Get performance metrics for current model."""
        if not self.current_model_version:
            return None
        
        try:
            # Load performance from current model
            perf_file = Path(f"models/{self.current_model_version}/performance.json")
            if not perf_file.exists():
                return None
            
            with open(perf_file, 'r') as f:
                perf_data = json.load(f)
            
            return ModelPerformance(
                accuracy=perf_data["accuracy"],
                precision=perf_data["precision"],
                recall=perf_data["recall"],
                f1_score=perf_data["f1_score"],
                auc_score=perf_data["auc_score"],
                training_time=perf_data["training_time"],
                inference_time=perf_data["inference_time"],
                model_size_mb=perf_data["model_size_mb"],
                timestamp=datetime.fromisoformat(perf_data["timestamp"])
            )
            
        except Exception as e:
            logger.error(f"Failed to load current model performance: {e}")
            return None
    
    async def trigger_manual_retraining(self):
        """Manually trigger model retraining."""
        if self.is_training:
            logger.warning("Training already in progress")
            return
        
        logger.info("Manual retraining triggered")
        await self._execute_training_cycle()
    
    def update_training_schedule(self, schedule: str):
        """Update the training schedule."""
        valid_schedules = ["daily", "weekly", "monthly"]
        if schedule not in valid_schedules:
            raise ValueError(f"Invalid schedule. Must be one of: {valid_schedules}")
        
        self.training_schedule = schedule
        logger.info(f"Training schedule updated to: {schedule}")
    
    def update_performance_threshold(self, threshold: float):
        """Update the performance improvement threshold."""
        if threshold < 0 or threshold > 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        self.performance_threshold = threshold
        logger.info(f"Performance threshold updated to: {threshold}")
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            "is_training": self.is_training,
            "last_training": self.last_training.isoformat() if self.last_training else None,
            "training_schedule": self.training_schedule,
            "performance_threshold": self.performance_threshold,
            "current_model_version": self.current_model_version,
            "previous_model_version": self.previous_model_version,
            "next_training": self._get_next_training_time().isoformat() if self.last_training else None
        }
    
    def _get_next_training_time(self) -> datetime:
        """Calculate next scheduled training time."""
        if not self.last_training:
            return datetime.utcnow()
        
        if self.training_schedule == "daily":
            return self.last_training + timedelta(days=1)
        elif self.training_schedule == "weekly":
            return self.last_training + timedelta(weeks=1)
        elif self.training_schedule == "monthly":
            return self.last_training + timedelta(days=30)
        
        return self.last_training + timedelta(days=7)

# Global pipeline instance
retraining_pipeline = AutomatedRetrainingPipeline()

# Convenience functions
async def start_automated_training():
    """Start the automated training pipeline."""
    await retraining_pipeline.start_scheduled_training()

async def trigger_retraining():
    """Manually trigger model retraining."""
    await retraining_pipeline.trigger_manual_retraining()

def get_pipeline_status() -> Dict[str, Any]:
    """Get pipeline status (synchronous wrapper)."""
    return asyncio.run(retraining_pipeline.get_pipeline_status())

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="XSEMA ML Retraining Pipeline")
    parser.add_argument("--start", action="store_true", help="Start automated training")
    parser.add_argument("--trigger", action="store_true", help="Trigger manual retraining")
    parser.add_argument("--status", action="store_true", help="Show pipeline status")
    parser.add_argument("--schedule", choices=["daily", "weekly", "monthly"], help="Update training schedule")
    parser.add_argument("--threshold", type=float, help="Update performance threshold")
    
    args = parser.parse_args()
    
    if args.start:
        print("Starting automated training pipeline...")
        asyncio.run(start_automated_training())
    elif args.trigger:
        print("Triggering manual retraining...")
        asyncio.run(trigger_retraining())
    elif args.status:
        status = get_pipeline_status()
        print(json.dumps(status, indent=2))
    elif args.schedule:
        retraining_pipeline.update_training_schedule(args.schedule)
        print(f"Training schedule updated to: {args.schedule}")
    elif args.threshold:
        retraining_pipeline.update_performance_threshold(args.threshold)
        print(f"Performance threshold updated to: {args.threshold}")
    else:
        parser.print_help()
