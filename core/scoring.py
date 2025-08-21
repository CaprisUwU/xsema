from utils.bitwise import bitwise_features

def hybrid_score(symbolic_score: float, model_score: float, alpha: float = 0.6) -> float:
    return alpha * symbolic_score + (1 - alpha) * model_score



#  define a simple hybrid scoring function that blends symbolic and model-based scores.

# This function can be adjusted based on the specific scoring logic you want to implement.
# For example, you might want to weight the symbolic score more heavily if it is more reliable  

def score_token(event):
    # Use bitwise features for scoring
    features = bitwise_features(event["tokenId"])
    # Example: combine bit_length and trailing_zeros for a simple score
    score = (features["bit_length"] - features["trailing_zeros"]) / features["bit_length"]
    print(f"Bitwise features for token {event['tokenId']}: {features}")
    return score