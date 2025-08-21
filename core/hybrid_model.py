"""
Hybrid Symbolic-Statistical Model for NFT Analysis

This module implements a scientifically rigorous model that combines:
1. Symbolic analysis (mathematical patterns)
2. Statistical measures (entropy, distributions)
3. Hybrid approaches (combined metrics)

to provide interpretable and accurate analysis of NFTs and blockchain entities.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.base import BaseEstimator, RegressorMixin
import joblib
import json
import os
from datetime import datetime

# Import our utility modules
from utils.address_symmetry import check_address_symmetry
from utils.bitwise import analyze_bytecode_patterns
from utils.entropy import calculate_entropy
from utils.temporal import golden_ratio_proximity
from utils.graph_entropy import calculate_graph_entropy
from utils.hybrid_similarity import SimilarityAnalyzer
from utils.market import analyze_market_patterns
from utils.simhash import SimHasher
from utils.temporal import analyze_temporal_patterns

@dataclass
class ModelConfig:
    """Configuration for the hybrid model."""
    # Feature weights (can be learned)
    weights: Dict[str, float]
    
    # Model parameters
    model_type: str = 'random_forest'  # or 'gradient_boosting'
    n_estimators: int = 100
    max_depth: int = 5
    learning_rate: float = 0.1
    
    # Feature configuration
    use_symmetry: bool = True
    use_entropy: bool = True
    use_golden: bool = True
    use_graph: bool = True
    use_hybrid: bool = True
    use_market: bool = True
    use_temporal: bool = True
    
    @classmethod
    def load(cls, path: str) -> 'ModelConfig':
        """Load configuration from file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def save(self, path: str):
        """Save configuration to file."""
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)

class HybridModel(BaseEstimator, RegressorMixin):
    """
    Hybrid model that combines symbolic and statistical analysis.
    
    Features:
    1. Symbolic Features:
       - Address symmetry
       - Bitwise patterns
       - Golden ratio proximity
    
    2. Statistical Features:
       - Entropy measures
       - Graph entropy
       - Market patterns
       - Temporal patterns
    
    3. Hybrid Features:
       - Combined similarity scores
       - Weighted feature combinations
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Initialize the hybrid model."""
        self.config = config or ModelConfig(
            weights={
                'symmetry': 0.15,
                'entropy': 0.2,
                'golden': 0.1,
                'graph': 0.15,
                'hybrid': 0.2,
                'market': 0.1,
                'temporal': 0.1
            }
        )
        self.model = self._init_model()
        self.feature_importances_ = None
        self.last_trained = None
        
    def _init_model(self):
        """Initialize the underlying ML model."""
        if self.config.model_type == 'random_forest':
            return RandomForestRegressor(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                random_state=42
            )
        elif self.config.model_type == 'gradient_boosting':
            return GradientBoostingRegressor(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                learning_rate=self.config.learning_rate,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.config.model_type}")
    
    def extract_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features using all available utility modules."""
        features = {}
        
        # 1. Symbolic Features
        if self.config.use_symmetry and 'address' in data:
            sym = check_address_symmetry(data['address'])
            features.update({
                'symmetry_score': sym.get('score', 0),
                'symmetry_type': float(hash(sym.get('type', '')) % 100)  # Simple hash to float
            })
        
        if self.config.use_entropy and 'data' in data:
            entropy = calculate_entropy(data['data'])
            features['entropy'] = entropy
        
        # 2. Statistical Features
        if self.config.use_golden and 'values' in data:
            golden = golden_ratio_proximity(data['values'])
            features['golden_proximity'] = golden
        
        if self.config.use_graph and 'graph' in data:
            graph_entropy = calculate_graph_entropy(data['graph'])
            features['graph_entropy'] = graph_entropy
        
        # 3. Hybrid Features
        if self.config.use_hybrid and 'items' in data:
            hybrid = SimilarityAnalyzer()
            sim_scores = [hybrid.compare(data['items'][0], item) for item in data['items'][1:]]
            features.update({
                'min_similarity': min(sim_scores, default=0),
                'max_similarity': max(sim_scores, default=0),
                'avg_similarity': sum(sim_scores) / len(sim_scores) if sim_scores else 0
            })
        
        # Apply weights
        weighted_features = {}
        for name, value in features.items():
            weight = self.config.weights.get(name.split('_')[0], 1.0)
            weighted_features[name] = value * weight
        
        return weighted_features
    
    def fit(self, X: List[Dict], y: List[float]):
        """
        Train the model on extracted features.
        
        Args:
            X: List of input data dictionaries
            y: Target values
        """
        # Extract features
        X_features = [self.extract_features(x) for x in X]
        
        # Convert to numpy array
        feature_names = sorted(set().union(*(d.keys() for d in X_features)))
        X_array = np.array([
            [sample.get(feat, 0) for feat in feature_names]
            for sample in X_features
        ])
        
        # Train model
        self.model.fit(X_array, y)
        self.feature_importances_ = dict(zip(feature_names, self.model.feature_importances_))
        self.last_trained = datetime.utcnow().isoformat()
        
        return self
    
    def predict(self, X: List[Dict]) -> np.ndarray:
        """Make predictions on new data."""
        # Extract features
        X_features = [self.extract_features(x) for x in X]
        
        # Convert to numpy array using the same feature order as training
        feature_names = sorted(self.feature_importances_.keys())
        X_array = np.array([
            [sample.get(feat, 0) for feat in feature_names]
            for sample in X_features
        ])
        
        return self.model.predict(X_array)
    
    def save(self, path: str):
        """Save the model to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'config': self.config,
            'feature_importances': self.feature_importances_,
            'last_trained': self.last_trained
        }, path)
    
    @classmethod
    def load(cls, path: str) -> 'HybridModel':
        """Load a saved model from disk."""
        data = joblib.load(path)
        model = cls(config=data['config'])
        model.model = data['model']
        model.feature_importances_ = data['feature_importances']
        model.last_trained = data['last_trained']
        return model

# Example usage
if __name__ == "__main__":
    # Initialize model
    config = ModelConfig(
        weights={
            'symmetry': 0.2,
            'entropy': 0.2,
            'golden': 0.1,
            'graph': 0.2,
            'hybrid': 0.3
        },
        model_type='random_forest',
        n_estimators=100,
        max_depth=5
    )
    
    model = HybridModel(config)
    
    # Example training data
    X_train = [
        {'address': '0x1234...', 'data': 'some data', 'values': [1, 1, 2, 3, 5, 8]},
        # Add more training examples
    ]
    y_train = [0.8, 0.6]  # Target values
    
    # Train model
    model.fit(X_train, y_train)
    
    # Make predictions
    X_test = [{'address': '0xabcd...', 'data': 'test data', 'values': [1, 2, 3, 5, 8, 13]}]
    predictions = model.predict(X_test)
    print(f"Predictions: {predictions}")
    
    # Save model
    model.save("models/hybrid_model.joblib")
