"""
XSEMA Authentication Module - Phase 4
User authentication with JWT tokens and bcrypt password hashing
"""

import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
import os
from enum import Enum

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User roles for access control"""
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"

class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class UserRegistration(BaseModel):
    """User registration request model"""
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    """User login request model"""
    username: str
    password: str

class UserProfile(BaseModel):
    """User profile model"""
    id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime
    last_login: Optional[datetime] = None
    is_verified: bool = False

class TokenData(BaseModel):
    """JWT token payload data"""
    user_id: str
    username: str
    role: UserRole
    exp: datetime

class AuthenticationManager:
    """Manages user authentication and JWT tokens"""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "xsema_demo_secret_key_change_in_production")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.bcrypt_rounds = int(os.getenv("BCRYPT_ROUNDS", "12"))
        
        logger.info(f"🔐 Authentication manager initialized with {self.bcrypt_rounds} bcrypt rounds")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"❌ Password hashing failed: {e}")
            raise
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"❌ Password verification failed: {e}")
            return False
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        try:
            expire = datetime.now() + timedelta(minutes=self.access_token_expire_minutes)
            to_encode = {
                "user_id": user_data["id"],
                "username": user_data["username"],
                "role": user_data["role"],
                "exp": expire,
                "type": "access"
            }
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"✅ Access token created for user {user_data['username']}")
            return token
        except Exception as e:
            logger.error(f"❌ Access token creation failed: {e}")
            raise
    
    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        try:
            expire = datetime.now() + timedelta(days=self.refresh_token_expire_days)
            to_encode = {
                "user_id": user_data["id"],
                "username": user_data["username"],
                "exp": expire,
                "type": "refresh"
            }
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"✅ Refresh token created for user {user_data['username']}")
            return token
        except Exception as e:
            logger.error(f"❌ Refresh token creation failed: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("user_id")
            username = payload.get("username")
            role = payload.get("role")
            exp = payload.get("exp")
            
            if user_id is None or username is None or exp is None:
                logger.warning("❌ Invalid token payload")
                return None
            
            # Check if token is expired
            if datetime.now() > datetime.fromtimestamp(exp):
                logger.warning("❌ Token expired")
                return None
            
            return TokenData(
                user_id=user_id,
                username=username,
                role=UserRole(role) if role else UserRole.USER,
                exp=datetime.fromtimestamp(exp)
            )
        except jwt.ExpiredSignatureError:
            logger.warning("❌ Token expired")
            return None
        except jwt.PyJWTError as e:
            logger.error(f"❌ JWT verification failed: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Token verification failed: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("user_id")
            username = payload.get("username")
            token_type = payload.get("type")
            
            if token_type != "refresh":
                logger.warning("❌ Invalid token type for refresh")
                return None
            
            # Create new access token with string role (matching the format used in login)
            user_data = {"id": user_id, "username": username, "role": "user"}
            
            new_access_token = self.create_access_token(user_data)
            logger.info(f"✅ Access token refreshed for user {username}")
            return new_access_token
            
        except jwt.PyJWTError as e:
            logger.error(f"❌ JWT verification failed during refresh: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Token refresh failed: {e}")
            return None

# Global authentication manager instance
auth_manager = AuthenticationManager()

# Mock user database for development (will be replaced with PostgreSQL)
MOCK_USERS = {
    "demo": {
        "id": "1",
        "username": "demo",
        "email": "demo@xsema.co.uk",
        "password_hash": None,  # Will be set during initialization
        "first_name": "Demo",
        "last_name": "User",
        "role": UserRole.USER,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.now(),
        "last_login": None,
        "is_verified": True
    }
}

def initialize_mock_users():
    """Initialize mock users with hashed passwords"""
    try:
        # Hash demo user password
        demo_password = "xsema2025"
        MOCK_USERS["demo"]["password_hash"] = auth_manager.hash_password(demo_password)
        logger.info("✅ Mock users initialized with hashed passwords")
    except Exception as e:
        logger.error(f"❌ Failed to initialize mock users: {e}")

# Force re-initialization to get fresh password hash
initialize_mock_users()

# Initialize mock users on module import
initialize_mock_users()

class MockUserDatabase:
    """Mock user database for development (will be replaced with PostgreSQL)"""
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        user = MOCK_USERS.get(username)
        if user:
            return user.copy()
        return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        for user in MOCK_USERS.values():
            if user["email"] == email:
                return user.copy()
        return None
    
    @staticmethod
    def create_user(user_data: UserRegistration) -> Optional[Dict[str, Any]]:
        """Create new user"""
        try:
            # Check if username or email already exists
            if MockUserDatabase.get_user_by_username(user_data.username):
                logger.warning(f"❌ Username {user_data.username} already exists")
                return None
            
            if MockUserDatabase.get_user_by_email(user_data.email):
                logger.warning(f"❌ Email {user_data.email} already exists")
                return None
            
            # Create new user
            new_user = {
                "id": str(len(MOCK_USERS) + 1),
                "username": user_data.username,
                "email": user_data.email,
                "password_hash": auth_manager.hash_password(user_data.password),
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "role": UserRole.USER,
                "status": UserStatus.PENDING_VERIFICATION,
                "created_at": datetime.now(),
                "last_login": None,
                "is_verified": False
            }
            
            MOCK_USERS[user_data.username] = new_user
            logger.info(f"✅ User {user_data.username} created successfully")
            return new_user.copy()
            
        except Exception as e:
            logger.error(f"❌ User creation failed: {e}")
            return None
    
    @staticmethod
    def update_last_login(username: str):
        """Update user's last login timestamp"""
        if username in MOCK_USERS:
            MOCK_USERS[username]["last_login"] = datetime.now()
            logger.info(f"✅ Last login updated for user {username}")

# Global mock database instance
mock_db = MockUserDatabase()

async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with username and password"""
    try:
        user = mock_db.get_user_by_username(username)
        if not user:
            logger.warning(f"❌ Authentication failed: User {username} not found")
            return None
        
        if not auth_manager.verify_password(password, user["password_hash"]):
            logger.warning(f"❌ Authentication failed: Invalid password for user {username}")
            return None
        
        if user["status"] != UserStatus.ACTIVE:
            logger.warning(f"❌ Authentication failed: User {username} account not active")
            return None
        
        # Update last login
        mock_db.update_last_login(username)
        
        logger.info(f"✅ User {username} authenticated successfully")
        return user
        
    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        return None

async def register_user(user_data: UserRegistration) -> Optional[Dict[str, Any]]:
    """Register new user"""
    try:
        # Validate input
        if len(user_data.password) < 8:
            logger.warning("❌ Password too short (minimum 8 characters)")
            return None
        
        if len(user_data.username) < 3:
            logger.warning("❌ Username too short (minimum 3 characters)")
            return None
        
        # Create user
        new_user = mock_db.create_user(user_data)
        if new_user:
            logger.info(f"✅ User {user_data.username} registered successfully")
            return new_user
        else:
            logger.warning("❌ User registration failed")
            return None
            
    except Exception as e:
        logger.error(f"❌ User registration failed: {e}")
        return None
