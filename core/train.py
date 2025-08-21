# core/train.py
from io import StringIO
import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.linear_model import Ridge
from services.model_service import train_model
from services.training_service import train_rarity_model, train_auto_model
from services.model_registry import register_model
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from datetime import datetime
from core.features import extract_features


def prepare_features(df):
    required = [
        "wallet_entropy", "wallet_root", "token_mod9",
        "token_entropy", "mint_phase", "gas_tier"
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required features: {missing}")
    return df[required], df["rarity"]

def train_rarity_model(df):
    df = extract_features(df)
    X, y = prepare_features(df)

    model = RandomForestRegressor(
        n_estimators=50,
        max_depth=5,
        n_jobs=-1,
        random_state=42
    )
    model.fit(X, y)

    os.makedirs("models", exist_ok=True)
    model_path = "models/rarity_predictor.pkl"
    joblib.dump(model, model_path)

    # Register the model in the registry
    model_id = f"rarity_predictor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    performance = {
        "cv_score": None,  # No CV score available for this model
        "r2": None,  # No R2 score available for this model
        "rmse": None  # No RMSE score available for this model
    }
    features = X.columns.tolist()
    
    register_model(
        model_id=model_id,
        filename=model_path,
        performance=performance,
        description="Rarity predictor model",
        features=features
    )

    return model, X.columns.tolist()

class ModelMetrics(BaseModel):
    model_name: str
    cv_scores: List[float]
    mean_score: float
    std_score: float
    saved_path: str

router = APIRouter(prefix="/train", tags=["Train"])

@router.post("/auto")
async def auto_train_model(file: UploadFile = File(...)):
    try:
        # Read the CSV file
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = ["wallet", "token_id", "timestamp"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
            
        # Extract features
        df = extract_features(df)
        
        # Prepare features and target
        X = df.drop(columns=["wallet", "token_id", "timestamp", "rarity"])
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
        
        # Register the model in the registry
        model_id = f"best_{best_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        performance = {
            "cv_score": best_model["mean_score"],
            "r2": best_model["mean_score"],  # CV score is our R2
            "rmse": np.sqrt(1 - best_model["mean_score"])  # Approximate RMSE from R2
        }
        features = X.columns.tolist()
        
        register_model(
            model_id=model_id,
            filename=model_path,
            performance=performance,
            description=f"Auto-trained {best_name} model",
            features=features
        )
        
        return ModelMetrics(
            model_name=best_name,
            cv_scores=best_model["cv_scores"],
            mean_score=best_model["mean_score"],
            std_score=best_model["std_score"],
            saved_path=model_path
        )
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        await file.close()

@router.post("/")
async def train_csv(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    result = train_model(df)
    return {
        "success": True,
        "metrics": result,
        "message": "Model trained and saved successfully"
    }