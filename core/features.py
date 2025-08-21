import pandas as pd
import numpy as np
from utils.entropy import entropy, digit_root, prime_factor_count
from utils.graph_entropy import compute_wallet_graph_entropy

from utils.graph_entropy import compute_wallet_graph_entropy
from utils.address_symmetry import address_symmetry_features
from utils.bitwise import bitwise_features
from utils.simhash import simhash, simhash_distance
from utils.temporal import fibonacci_intervals, golden_ratio_proximity


def classify_mint_phase(timestamp):
    ts = pd.to_datetime(timestamp)
    if ts.tzinfo:
        ts = ts.tz_convert(None)
    if ts < pd.Timestamp("2023-01-02"):
        return "early"
    elif ts < pd.Timestamp("2023-01-04"):
        return "mid"
    else:
        return "late"

def classify_gas_tier(gas_price):
    if gas_price < 40:
        return "low"
    elif gas_price < 70:
        return "medium"
    else:
        return "high"

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["token_id"] = df["token_id"].astype(str)

    # Token-level symbolic features
    df["token_mod9"] = df["token_id"].apply(lambda x: int(x) % 9 if x.isdigit() else np.nan)
    df["token_root"] = df["token_id"].apply(lambda x: digit_root(int(x)) if x.isdigit() else np.nan)
    df["token_entropy"] = df["token_id"].apply(lambda x: entropy(str(x)) if pd.notnull(x) else np.nan)
    df["token_prime_factors"] = df["token_id"].apply(lambda x: prime_factor_count(int(x)) if x.isdigit() else np.nan)

    # Wallet-level symbolic features
    df["wallet_entropy"] = df["wallet"].apply(lambda x: entropy(str(x)) if pd.notnull(x) else np.nan)
    df["wallet_root"] = df["wallet"].apply(lambda x: digit_root(int(x, 16)) if pd.notnull(x) else np.nan)
    
    # wallet graph entropy ## another gem
    df["wallet_graph_entropy"] = compute_wallet_graph_entropy(df)

    df["wallet_graph_entropy"] = compute_wallet_graph_entropy(df)

    df["wallet_palindrome"] = df["wallet"].apply(lambda w: address_symmetry_features(w)["is_palindrome"])
    df["token_bit_entropy"] = df["token_id"].apply(lambda t: bitwise_features(int(t))["bit_entropy"])
    df["wallet_simhash"] = df["wallet"].apply(lambda w: simhash(w))

    df["fibonacci_mint_ratio"] = fibonacci_intervals(df["timestamp"])
    df["golden_ratio_alignment"] = golden_ratio_proximity(df["timestamp"])

    

    # Contextual features
    if "timestamp" in df.columns:
        df["mint_phase"] = df["timestamp"].apply(classify_mint_phase)
    else:
        df["mint_phase"] = np.nan

    if "gas_price" in df.columns:
        df["gas_tier"] = df["gas_price"].apply(classify_gas_tier)
    else:
        df["gas_tier"] = np.nan

    return df


    
   