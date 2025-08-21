import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from joblib import dump

from services.shap_service import compute_shap_values, summarize_shap
from services.feature_service import extract_symbolic_features

def train_model(df: pd.DataFrame, target_column: str = "rarity") -> dict:
    from core.train import prepare_features  # Ensure prepare_features is imported here to avoid circular imports
    # ...rest of your function...
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in DataFrame.")

    # Step 1: Extract symbolic features
    df = extract_symbolic_features(df)

    # Step 2: Prepare features and target
    X, y = prepare_features(df, target_column=target_column)

    # Step 3: Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Step 4: Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Step 5: Evaluate
    y_pred = model.predict(X_test)
    score = r2_score(y_test, y_pred)

    # Step 6: SHAP analysis
    shap_values = compute_shap_values(model, X)
    shap_summary = summarize_shap(shap_values, X.columns)

    # Step 7: Feature importance
    feature_importance = dict(zip(X.columns, model.feature_importances_))

    # Step 8: Save model
    model_path = "models/rarity_predictor.pkl"
    dump(model, model_path)

    return {
        "model_type": "RandomForestRegressor",
        "r2_score": round(score, 4),
        "feature_importance": feature_importance,
        "shap_summary": shap_summary,
        "saved_to": model_path,
        "features_used": list(X.columns)
    }


def predict_batch(df: pd.DataFrame, model_path: str = "models/rarity_predictor.pkl") -> dict:
    """
    Make batch predictions using a trained model.
    
    Args:
        df: DataFrame with features for prediction
        model_path: Path to the trained model file
        
    Returns:
        dict: Prediction results and metadata
    """
    from joblib import load
    from services.feature_service import extract_symbolic_features
    
    try:
        # Load the trained model
        model = load(model_path)
        
        # Extract symbolic features if not already done
        if 'symbolic_features' not in df.columns:
            df = extract_symbolic_features(df)
        
        # Prepare features (assuming prepare_features function exists)
        from core.train import prepare_features
        X, _ = prepare_features(df, target_column=None)  # No target needed for prediction
        
        # Make predictions
        predictions = model.predict(X)
        
        # Calculate confidence scores (for Random Forest, use prediction variance)
        if hasattr(model, 'estimators_'):
            # Get predictions from all trees
            tree_predictions = []
            for estimator in model.estimators_:
                tree_predictions.append(estimator.predict(X))
            
            # Calculate variance across trees as confidence measure
            import numpy as np
            tree_predictions = np.array(tree_predictions)
            confidence_scores = 1.0 / (1.0 + np.var(tree_predictions, axis=0))
        else:
            confidence_scores = [0.8] * len(predictions)  # Default confidence
        
        return {
            "predictions": predictions.tolist(),
            "confidence_scores": confidence_scores.tolist(),
            "model_path": model_path,
            "features_used": list(X.columns),
            "prediction_count": len(predictions),
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Model file not found: {model_path}")
    except Exception as e:
        raise RuntimeError(f"Error making predictions: {str(e)}")


def predict_batch_stub(df: pd.DataFrame, model_path: str = "models/rarity_predictor.pkl") -> dict:
    """
    Stub implementation of predict_batch for immediate market endpoint functionality.
    Provides mock predictions without external dependencies.
    
    Args:
        df: DataFrame with features for prediction
        model_path: Path to the trained model file (ignored in stub)
        
    Returns:
        dict: Mock prediction results and metadata
    """
    import pandas as pd
    import numpy as np
    from datetime import datetime
    
    try:
        # Generate mock predictions based on input data
        num_samples = len(df) if hasattr(df, '__len__') else 10
        
        # Mock predictions with some randomness
        base_score = 0.75
        predictions = np.random.normal(base_score, 0.15, num_samples)
        predictions = np.clip(predictions, 0.1, 1.0)  # Clamp between 0.1 and 1.0
        
        # Mock confidence scores
        confidence_scores = np.random.uniform(0.6, 0.95, num_samples)
        
        # Mock feature importance if columns exist
        features_used = []
        if hasattr(df, 'columns') and len(df.columns) > 0:
            features_used = list(df.columns[:min(5, len(df.columns))])
        else:
            features_used = ['mock_feature_1', 'mock_feature_2', 'mock_feature_3']
        
        return {
            "predictions": predictions.tolist(),
            "confidence_scores": confidence_scores.tolist(),
            "model_path": model_path,
            "features_used": features_used,
            "prediction_count": num_samples,
            "timestamp": datetime.now().isoformat(),
            "model_type": "mock_stub",
            "note": "This is a stub implementation for immediate functionality"
        }
        
    except Exception as e:
        # Fallback response if anything goes wrong
        return {
            "predictions": [0.5] * 10,
            "confidence_scores": [0.8] * 10,
            "model_path": model_path,
            "features_used": ["fallback_feature"],
            "prediction_count": 10,
            "timestamp": datetime.now().isoformat(),
            "model_type": "fallback_stub",
            "error": str(e),
            "note": "Fallback stub due to error"
        }

