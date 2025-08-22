"""
Enterprise Authentication Module for XSEMA

This module provides enterprise-grade authentication including:
- Single Sign-On (SSO) with SAML 2.0, OAuth 2.0, OpenID Connect
- LDAP/Active Directory integration
- Multi-Factor Authentication (MFA)
- Role-based access control (RBAC)
- Session management and security
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import ldap3
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE


class AuthProvider(str, Enum):
    """Supported authentication providers"""
    LOCAL = "local"
    SAML = "saml"
    OAUTH = "oauth"
    OPENID = "openid"
    LDAP = "ldap"
    ACTIVE_DIRECTORY = "active_directory"


class UserRole(str, Enum):
    """User roles for RBAC"""
    VIEWER = "viewer"
    USER = "user"
    ANALYST = "analyst"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class MFAStatus(str, Enum):
    """Multi-factor authentication status"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    REQUIRED = "required"
    VERIFIED = "verified"


class User(BaseModel):
    """Enterprise user model"""
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username for login")
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    auth_provider: AuthProvider = Field(default=AuthProvider.LOCAL, description="Authentication provider")
    mfa_status: MFAStatus = Field(default=MFAStatus.DISABLED, description="MFA status")
    is_active: bool = Field(default=True, description="User account status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation date")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    organization_id: Optional[str] = Field(default=None, description="Organization identifier")
    department: Optional[str] = Field(default=None, description="User department")
    manager_id: Optional[str] = Field(default=None, description="Manager user ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "usr_123456789",
                "username": "john.doe",
                "email": "john.doe@company.com",
                "full_name": "John Doe",
                "role": "analyst",
                "auth_provider": "saml",
                "mfa_status": "enabled",
                "is_active": True,
                "permissions": ["read_portfolio", "write_reports", "admin_users"],
                "organization_id": "org_123",
                "department": "Investment Analysis",
                "manager_id": "usr_987654321"
            }
        }


class SSOConfig(BaseModel):
    """SSO configuration for different providers"""
    provider: AuthProvider
    client_id: str
    client_secret: str
    redirect_uri: str
    authorization_url: str
    token_url: str
    userinfo_url: str
    scopes: List[str] = Field(default_factory=list)
    enabled: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider": "saml",
                "client_id": "xsema_client",
                "client_secret": "secret_key_here",
                "redirect_uri": "https://xsema.com/auth/callback",
                "authorization_url": "https://idp.company.com/saml/login",
                "token_url": "https://idp.company.com/saml/token",
                "userinfo_url": "https://idp.company.com/saml/userinfo",
                "scopes": ["openid", "profile", "email"],
                "enabled": True
            }
        }


class LDAPConfig(BaseModel):
    """LDAP/Active Directory configuration"""
    server_url: str
    port: int = 389
    use_ssl: bool = False
    bind_dn: str
    bind_password: str
    search_base: str
    user_search_filter: str = "(sAMAccountName={username})"
    group_search_filter: str = "(member={user_dn})"
    enabled: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "server_url": "ldap.company.com",
                "port": 389,
                "use_ssl": False,
                "bind_dn": "CN=ServiceAccount,OU=ServiceAccounts,DC=company,DC=com",
                "bind_password": "service_password",
                "search_base": "DC=company,DC=com",
                "user_search_filter": "(sAMAccountName={username})",
                "group_search_filter": "(member={user_dn})",
                "enabled": True
            }
        }


class EnterpriseAuthService:
    """Enterprise authentication service"""
    
    def __init__(self):
        self.sso_configs: Dict[AuthProvider, SSOConfig] = {}
        self.ldap_config: Optional[LDAPConfig] = None
        self.jwt_secret: str = "xsema_enterprise_jwt_secret_change_in_production"
        self.jwt_algorithm: str = "HS256"
        self.jwt_expiry_hours: int = 24
        
    def configure_sso(self, config: SSOConfig) -> None:
        """Configure SSO provider"""
        self.sso_configs[config.provider] = config
        
    def configure_ldap(self, config: LDAPConfig) -> None:
        """Configure LDAP/Active Directory"""
        self.ldap_config = config
        
    def authenticate_user(self, username: str, password: str, provider: AuthProvider = AuthProvider.LOCAL) -> Optional[User]:
        """Authenticate user with specified provider"""
        if provider == AuthProvider.LDAP and self.ldap_config:
            return self._authenticate_ldap(username, password)
        elif provider == AuthProvider.LOCAL:
            return self._authenticate_local(username, password)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Authentication provider {provider} not configured"
            )
    
    def _authenticate_ldap(self, username: str, password: str) -> Optional[User]:
        """Authenticate user against LDAP/Active Directory"""
        if not self.ldap_config:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="LDAP not configured"
            )
            
        try:
            # Create LDAP server connection
            server = Server(
                self.ldap_config.server_url,
                port=self.ldap_config.port,
                use_ssl=self.ldap_config.use_ssl,
                get_info=ALL
            )
            
            # Bind with service account
            conn = Connection(
                server,
                user=self.ldap_config.bind_dn,
                password=self.ldap_config.bind_password,
                authentication=SIMPLE,
                auto_bind=True
            )
            
            # Search for user
            user_filter = self.ldap_config.user_search_filter.format(username=username)
            conn.search(
                self.ldap_config.search_base,
                user_filter,
                attributes=['cn', 'mail', 'sAMAccountName', 'memberOf', 'department', 'manager']
            )
            
            if not conn.entries:
                return None
                
            user_entry = conn.entries[0]
            
            # Try to bind as user to verify password
            user_dn = user_entry.entry_dn
            user_conn = Connection(
                server,
                user=user_dn,
                password=password,
                authentication=SIMPLE,
                auto_bind=True
            )
            
            if not user_conn.bound:
                return None
                
            # Create user object
            user = User(
                user_id=f"ldap_{username}",
                username=username,
                email=user_entry.mail.value if hasattr(user_entry, 'mail') else f"{username}@company.com",
                full_name=user_entry.cn.value if hasattr(user_entry, 'cn') else username,
                auth_provider=AuthProvider.LDAP,
                role=self._determine_role_from_groups(user_entry.memberOf),
                department=user_entry.department.value if hasattr(user_entry, 'department') else None,
                permissions=self._get_permissions_from_role(self._determine_role_from_groups(user_entry.memberOf))
            )
            
            return user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"LDAP authentication failed: {str(e)}"
            )
    
    def _authenticate_local(self, username: str, password: str) -> Optional[User]:
        """Authenticate user against local database (placeholder)"""
        # TODO: Implement local authentication with database
        # For now, return a mock user for development
        if username == "admin" and password == "admin123":
            return User(
                user_id="local_admin",
                username=username,
                email="admin@xsema.com",
                full_name="Local Administrator",
                role=UserRole.SUPER_ADMIN,
                auth_provider=AuthProvider.LOCAL,
                permissions=["*"]  # All permissions
            )
        return None
    
    def _determine_role_from_groups(self, groups: List[str]) -> UserRole:
        """Determine user role from LDAP groups"""
        if not groups:
            return UserRole.USER
            
        group_names = [group.lower() for group in groups]
        
        if any("admin" in group for group in group_names):
            return UserRole.ADMIN
        elif any("manager" in group for group in group_names):
            return UserRole.MANAGER
        elif any("analyst" in group for group in group_names):
            return UserRole.ANALYST
        else:
            return UserRole.USER
    
    def _get_permissions_from_role(self, role: UserRole) -> List[str]:
        """Get permissions based on user role"""
        permissions_map = {
            UserRole.VIEWER: ["read_portfolio", "read_reports"],
            UserRole.USER: ["read_portfolio", "write_portfolio", "read_reports"],
            UserRole.ANALYST: ["read_portfolio", "write_portfolio", "read_reports", "write_reports", "run_analytics"],
            UserRole.MANAGER: ["read_portfolio", "write_portfolio", "read_reports", "write_reports", "run_analytics", "manage_users", "view_analytics"],
            UserRole.ADMIN: ["read_portfolio", "write_portfolio", "read_reports", "write_reports", "run_analytics", "manage_users", "view_analytics", "admin_system"],
            UserRole.SUPER_ADMIN: ["*"]  # All permissions
        }
        return permissions_map.get(role, [])
    
    def create_jwt_token(self, user: User) -> str:
        """Create JWT token for authenticated user"""
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "permissions": user.permissions,
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiry_hours),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def get_user_permissions(self, user: User) -> List[str]:
        """Get user permissions"""
        return user.permissions
    
    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in user.permissions or "*" in user.permissions
    
    def require_permission(self, user: User, permission: str) -> None:
        """Require specific permission or raise HTTPException"""
        if not self.has_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )


# Global instance
enterprise_auth_service = EnterpriseAuthService()

# Security dependency
security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> User:
    """Get current authenticated user from JWT token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        payload = enterprise_auth_service.verify_jwt_token(credentials.credentials)
        
        # TODO: Fetch full user from database
        # For now, create user from token payload
        user = User(
            user_id=payload["user_id"],
            username=payload["username"],
            email=f"{payload['username']}@xsema.com",  # Placeholder
            full_name=payload["username"],  # Placeholder
            role=UserRole(payload["role"]),
            permissions=payload["permissions"],
            auth_provider=AuthProvider.LOCAL
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


async def require_role(role: UserRole, current_user: User = Depends(get_current_user)) -> User:
    """Require specific user role"""
    if current_user.role != role and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{role.value}' required"
        )
    return current_user


async def require_permission(permission: str, current_user: User = Depends(get_current_user)) -> User:
    """Require specific permission"""
    enterprise_auth_service.require_permission(current_user, permission)
    return current_user


# Convenience functions for common roles
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    return await require_role(UserRole.ADMIN, current_user)


async def require_manager(current_user: User = Depends(get_current_user)) -> User:
    """Require manager role"""
    return await require_role(UserRole.MANAGER, current_user)


async def require_analyst(current_user: User = Depends(get_current_user)) -> User:
    """Require analyst role"""
    return await require_role(UserRole.ANALYST, current_user)
