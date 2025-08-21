import pandas as pd
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def extract_symbolic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract various symbolic features from the input DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame containing raw data
        
    Returns:
        pd.DataFrame: DataFrame with extracted symbolic features
    
    Raises:
        ValueError: If input DataFrame is empty
        Exception: For other processing errors
    """
    try:
        if df.empty:
            raise ValueError("Input DataFrame is empty")
            
        logger.info("Starting feature extraction...")
        
        # Initialize features dictionary
        features = {}
        
        # 1. Basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            col_features = {
                f'{col}_mean': df[col].mean(),
                f'{col}_median': df[col].median(),
                f'{col}_std': df[col].std(),
                f'{col}_min': df[col].min(),
                f'{col}_max': df[col].max(),
                f'{col}_range': df[col].max() - df[col].min(),
                f'{col}_skew': df[col].skew(),
                f'{col}_kurtosis': df[col].kurtosis(),
                f'{col}_missing_pct': df[col].isna().mean() * 100
            }
            features.update(col_features)
            
        # 2. Categorical features
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            col_features = {
                f'{col}_unique_count': df[col].nunique(),
                f'{col}_mode': df[col].mode()[0],
                f'{col}_missing_pct': df[col].isna().mean() * 100,
                f'{col}_top_value': df[col].value_counts().idxmax(),
                f'{col}_top_value_pct': df[col].value_counts(normalize=True).max() * 100
            }
            features.update(col_features)
            
        # 3. Correlation features
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            abs_corr = corr_matrix.abs()
            features['max_abs_correlation'] = abs_corr.where(np.triu(np.ones(abs_corr.shape), k=1).astype(bool)).max().max()
            features['avg_correlation'] = abs_corr.where(np.triu(np.ones(abs_corr.shape), k=1).astype(bool)).mean().mean()
            
        # 4. Overall dataset features
        features['total_rows'] = len(df)
        features['total_columns'] = len(df.columns)
        features['numeric_columns'] = len(numeric_cols)
        features['categorical_columns'] = len(categorical_cols)
        features['total_missing_values'] = df.isna().sum().sum()
        
        logger.info("Feature extraction completed successfully")
        return pd.DataFrame([features])
        
    except ValueError as ve:
        logger.error(f"Value error during feature extraction: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Error during feature extraction: {str(e)}")
        raise Exception(f"Error extracting features: {str(e)}")