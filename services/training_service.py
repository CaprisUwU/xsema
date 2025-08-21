import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from typing import List
import joblib
import os
from datetime import datetime
from sklearn.svm import SVR
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler




def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare features for training by selecting required columns.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with selected features
    """
    required = [
        "wallet_entropy", "wallet_root", "token_mod9",
        "token_entropy", "mint_phase", "gas_tier"
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required features: {missing}")
    return df[required]

def train_rarity_model(df: pd.DataFrame) -> tuple:
    """
    Train a rarity prediction model.
    
    Args:
        df: Input DataFrame with features and target
        
    Returns:
        tuple: (model, features_used)
    """
    # Prepare features and target
    X = prepare_features(df)
    y = df["rarity"]
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=50,
        max_depth=5,
        n_jobs=-1,
        random_state=42
    )
    model.fit(X, y)
    
    # Save model
    os.makedirs("models", exist_ok=True)
    model_path = "models/rarity_predictor.pkl"
    joblib.dump(model, model_path)
    
    return model, X.columns.tolist()

def train_auto_model(df: pd.DataFrame) -> dict:
    """
    Train multiple models and select the best one based on cross-validation.
    
    Args:
        df: Input DataFrame with features and target
        
    Returns:
        dict: Model training results
    """
    # Prepare features and target
    X = prepare_features(df)
    y = df["rarity"]
    
    # List of models to evaluate
    models = {
        "RandomForest": RandomForestRegressor(random_state=42),
        "GradientBoosting": GradientBoostingRegressor(random_state=42),
        "SVR": SVR(),
        "Ridge": Ridge()
    }
    
    # Evaluate each model using cross-validation
    results = []
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        results.append({
            "model_name": name,
            "cv_scores": scores.tolist(),
            "mean_score": scores.mean(),
            "std_score": scores.std()
        })
    
    # Select the best model
    best_model = max(results, key=lambda x: x["mean_score"])
    
    # Train the best model on full data
    best_name = best_model["model_name"]
    best_model = models[best_name]
    best_model.fit(X, y)
    
    # Save the model
    model_path = f"models/best_{best_name.lower()}_model.pkl"
    os.makedirs("models", exist_ok=True)
    joblib.dump(best_model, model_path)
    
    return {
        "model_name": best_name,
        "cv_scores": best_model["cv_scores"],
        "mean_score": best_model["mean_score"],
        "std_score": best_model["std_score"],
        "saved_path": model_path,
        "features_used": X.columns.tolist()
    }







