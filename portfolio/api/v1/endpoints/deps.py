"""
Dependency injection utilities for API endpoints.
"""
from typing import Dict

async def get_current_user() -> Dict[str, str]:
    """
    Get current user (placeholder for actual auth)
    
    In a production environment, this would validate a JWT or session
    and return the authenticated user's information.
    
    Returns:
        Dictionary containing user information (currently a demo user)
    """
    return {
        "user_id": "demo-user",
        "email": "demo@example.com",
        "is_authenticated": True
    }
