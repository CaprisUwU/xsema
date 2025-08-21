import pandas as pd

REQUIRED_COLUMNS = ["wallet", "token_id", "timestamp", "gas_price"]

def load_drop_csv(path: str) -> pd.DataFrame:
    """
    Load a drop CSV and ensure required columns are present.
    """
    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValueError(f"❌ Failed to load CSV: {e}")

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"❌ Missing required columns: {missing}")

    return df

def validate_drop_df(df: pd.DataFrame) -> bool:
    """
    Check if a DataFrame has the required structure for feature extraction.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return len(missing) == 0

def preview_drop(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Return a preview of the drop data.
    """
    return df.head(n)