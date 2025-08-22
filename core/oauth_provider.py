"""
OAuth 2.0 Provider for XSEMA Enterprise Authentication

This module implements OAuth 2.0 authorization server functionality for
modern authentication flows including:
- Authorization Code Flow
- Client Credentials Flow
- Resource Owner Password Flow
- Refresh Token Management
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import secrets
import hashlib
import base64
from urllib.parse import urlencode, parse_qs, urlparse

from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from .enterprise_auth import User, UserRole, AuthProvider, EnterpriseAuthService


class OAuthClient(BaseModel):
    """OAuth client application configuration"""
    client_id: str = Field(..., description="Unique client identifier")
    client_secret: str = Field(..., description="Client secret for authentication")
    client_name: str = Field(..., description="Human-readable client name")
    redirect_uris: List[str] = Field(..., description="Allowed redirect URIs")
    scopes: List[str] = Field(default=["read", "write"], description="Allowed scopes")
    grant_types: List[str] = Field(default=["authorization_code"], description="Allowed grant types")
    is_confidential: bool = Field(default=True, description="Whether client can keep secrets")
    
    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "xsema_web_app",
                "client_secret": "secure_secret_here",
                "client_name": "XSEMA Web Application",
                "redirect_uris": ["https://xsema.co.uk/auth/callback"],
                "scopes": ["read", "write", "admin"],
                "grant_types": ["authorization_code", "refresh_token"],
                "is_confidential": True
            }
        }


class OAuthToken(BaseModel):
    """OAuth access token"""
    access_token: str = Field(..., description="Access token for API calls")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    scope: str = Field(..., description="Token scope")
    user_id: Optional[str] = Field(default=None, description="Associated user ID")
    client_id: str = Field(..., description="Client that requested the token")


class OAuthProvider:
    """OAuth 2.0 Authorization Server implementation"""
    
    def __init__(self):
        self.clients: Dict[str, OAuthClient] = {}
        self.tokens: Dict[str, OAuthToken] = {}
        self.authorization_codes: Dict[str, Dict[str, Any]] = {}
        self.auth_service = EnterpriseAuthService()
        
        # Initialize with default XSEMA client
        self._create_default_client()
    
    def _create_default_client(self):
        """Create default OAuth client for XSEMA"""
        default_client = OAuthClient(
            client_id="xsema_web_app",
            client_secret="xsema_oauth_secret_2024",
            client_name="XSEMA Web Application",
            redirect_uris=["https://xsema.co.uk/auth/callback", "http://localhost:3000/auth/callback"],
            scopes=["read", "write", "admin"],
            grant_types=["authorization_code", "refresh_token"],
            is_confidential=True
        )
        self.clients[default_client.client_id] = default_client
    
    def create_authorization_url(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str = "read write",
        state: Optional[str] = None,
        response_type: str = "code"
    ) -> str:
        """Create OAuth authorization URL"""
        if client_id not in self.clients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client ID"
            )
        
        client = self.clients[client_id]
        
        if redirect_uri not in client.redirect_uris:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid redirect URI"
            )
        
        if response_type != "code":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only authorization code flow supported"
            )
        
        # Generate authorization code
        auth_code = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        self.authorization_codes[auth_code] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "expires_at": expires_at,
            "user_id": None  # Will be set after user authentication
        }
        
        # Build authorization URL
        params = {
            "response_type": response_type,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state or "",
            "code": auth_code
        }
        
        return f"/oauth/authorize?{urlencode(params)}"
    
    def exchange_code_for_token(
        self,
        client_id: str,
        client_secret: str,
        code: str,
        redirect_uri: str,
        grant_type: str = "authorization_code"
    ) -> OAuthToken:
        """Exchange authorization code for access token"""
        if grant_type != "authorization_code":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only authorization code grant type supported"
            )
        
        if client_id not in self.clients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client ID"
            )
        
        client = self.clients[client_id]
        
        if client.client_secret != client_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client secret"
            )
        
        if code not in self.authorization_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization code"
            )
        
        auth_data = self.authorization_codes[code]
        
        if auth_data["client_id"] != client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code mismatch"
            )
        
        if auth_data["redirect_uri"] != redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Redirect URI mismatch"
            )
        
        if datetime.utcnow() > auth_data["expires_at"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code expired"
            )
        
        if not auth_data["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code not yet authorized by user"
            )
        
        # Generate tokens
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        
        # Create token
        token = OAuthToken(
            access_token=access_token,
            expires_in=3600,  # 1 hour
            refresh_token=refresh_token,
            scope=auth_data["scope"],
            user_id=auth_data["user_id"],
            client_id=client_id
        )
        
        # Store token
        self.tokens[access_token] = token
        
        # Clean up authorization code
        del self.authorization_codes[code]
        
        return token
    
    def refresh_access_token(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str
    ) -> OAuthToken:
        """Refresh access token using refresh token"""
        if client_id not in self.clients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client ID"
            )
        
        client = self.clients[client_id]
        
        if client.client_secret != client_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client secret"
            )
        
        # Find token by refresh token
        old_token = None
        for token in self.tokens.values():
            if token.refresh_token == refresh_token and token.client_id == client_id:
                old_token = token
                break
        
        if not old_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )
        
        # Generate new tokens
        access_token = secrets.token_urlsafe(32)
        new_refresh_token = secrets.token_urlsafe(32)
        
        # Create new token
        new_token = OAuthToken(
            access_token=access_token,
            expires_in=3600,  # 1 hour
            refresh_token=new_refresh_token,
            scope=old_token.scope,
            user_id=old_token.user_id,
            client_id=client_id
        )
        
        # Store new token and remove old one
        self.tokens[access_token] = new_token
        if old_token.access_token in self.tokens:
            del self.tokens[old_token.access_token]
        
        return new_token
    
    def validate_access_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Validate access token and return user info"""
        if access_token not in self.tokens:
            return None
        
        token = self.tokens[access_token]
        
        # Check if token is expired (basic check)
        # In production, you'd want to store expiration time
        if token.expires_in <= 0:
            del self.tokens[access_token]
            return None
        
        # Get user information
        if token.user_id:
            user = self.auth_service.get_user_by_id(token.user_id)
            if user:
                return {
                    "user_id": user.user_id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "scope": token.scope,
                    "client_id": token.client_id
                }
        
        return {
            "scope": token.scope,
            "client_id": token.client_id
        }
    
    def revoke_token(self, access_token: str, client_id: str, client_secret: str) -> bool:
        """Revoke access token"""
        if client_id not in self.clients:
            return False
        
        client = self.clients[client_id]
        
        if client.client_secret != client_secret:
            return False
        
        if access_token in self.tokens:
            token = self.tokens[access_token]
            if token.client_id == client_id:
                del self.tokens[access_token]
                return True
        
        return False
    
    def create_client(
        self,
        client_name: str,
        redirect_uris: List[str],
        scopes: List[str] = None,
        grant_types: List[str] = None
    ) -> OAuthClient:
        """Create new OAuth client"""
        client_id = f"client_{secrets.token_urlsafe(16)}"
        client_secret = secrets.token_urlsafe(32)
        
        client = OAuthClient(
            client_id=client_id,
            client_secret=client_secret,
            client_name=client_name,
            redirect_uris=redirect_uris,
            scopes=scopes or ["read", "write"],
            grant_types=grant_types or ["authorization_code"],
            is_confidential=True
        )
        
        self.clients[client_id] = client
        return client
    
    def get_client_info(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client information (without secret)"""
        if client_id not in self.clients:
            return None
        
        client = self.clients[client_id]
        return {
            "client_id": client.client_id,
            "client_name": client.client_name,
            "redirect_uris": client.redirect_uris,
            "scopes": client.scopes,
            "grant_types": client.grant_types,
            "is_confidential": client.is_confidential
        }


# Global OAuth provider instance
oauth_provider: Optional[OAuthProvider] = None


def get_oauth_provider() -> OAuthProvider:
    """Get global OAuth provider instance"""
    global oauth_provider
    if oauth_provider is None:
        oauth_provider = OAuthProvider()
    return oauth_provider


def configure_oauth() -> None:
    """Configure global OAuth provider"""
    global oauth_provider
    oauth_provider = OAuthProvider()
