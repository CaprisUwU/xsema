from pydantic import RootModel
from typing import List, Dict, Any

class FeatureRow(RootModel[Dict[str, Any]]):
    pass

class FeatureList(RootModel[List[Dict[str, Any]]]):
    pass