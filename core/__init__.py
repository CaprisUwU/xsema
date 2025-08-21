# Core package initialization
# Expose public API
from .cache import cache
from .config import settings
from .security.authentication import validate_api_key
