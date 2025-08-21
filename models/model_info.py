from pydantic import BaseModel
from typing import Optional, List

class ModelInfo(BaseModel):
    model_id: str
    trained_date: Optional[str]
    performance: Optional[float]
    status: Optional[str]
    description: Optional[str] = ""
    features: Optional[List[str]] = []