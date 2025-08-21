"""
User model for the Portfolio Management API.

This module defines the User model and related Pydantic schemas.
"""
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: bool = False
    risk_tolerance: float = Field(0.5, ge=0.0, le=1.0, 
                                description="User's risk tolerance from 0 (low) to 1 (high)")

class UserCreate(UserBase):
    """Model for creating a new user (includes password)."""
    password: str

class UserInDB(UserBase):
    """Model for user data in the database."""
    id: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class User(UserBase):
    """Public user model (excludes sensitive data like password hashes)."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enables ORM mode for SQLAlchemy

# Example user database (replace with actual database in production)
fake_users_db = {
    "testuser": {
        "id": "1",
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "fakehashedpassword",  # In a real app, use proper password hashing
        "full_name": "Test User",
        "disabled": False,
        "risk_tolerance": 0.7,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
}
