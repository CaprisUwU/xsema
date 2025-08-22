"""
Enterprise Authentication API Endpoints

This module provides API endpoints for enterprise authentication including:
- SSO login and callback
- LDAP authentication
- User management
- Role and permission management
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from core.enterprise_auth import (
    EnterpriseAuthService, User, UserRole, AuthProvider, SSOConfig, LDAPConfig,
    get_current_user, require_admin, enterprise_auth_service
)

router = APIRouter()


# Request/Response Models
class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    provider: AuthProvider = Field(default=AuthProvider.LOCAL, description="Authentication provider")
    mfa_code: Optional[str] = Field(default=None, description="MFA code if required")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john.doe",
                "password": "secure_password",
                "provider": "ldap",
                "mfa_code": "123456"
            }
        }


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")
    user: User = Field(..., description="User information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user": {
                    "user_id": "usr_123456789",
                    "username": "john.doe",
                    "email": "john.doe@company.com",
                    "full_name": "John Doe",
                    "role": "analyst",
                    "auth_provider": "ldap",
                    "mfa_status": "enabled",
                    "is_active": True,
                    "permissions": ["read_portfolio", "write_reports", "run_analytics"],
                    "organization_id": "org_123",
                    "department": "Investment Analysis"
                }
            }
        }


class UserCreateRequest(BaseModel):
    """User creation request model"""
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: str = Field(..., description="Full name")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    department: Optional[str] = Field(default=None, description="Department")
    organization_id: Optional[str] = Field(default=None, description="Organization ID")
    manager_id: Optional[str] = Field(default=None, description="Manager user ID")
    auth_provider: AuthProvider = Field(default=AuthProvider.LOCAL, description="Authentication provider")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "jane.smith",
                "email": "jane.smith@company.com",
                "full_name": "Jane Smith",
                "role": "analyst",
                "department": "Portfolio Management",
                "organization_id": "org_123",
                "manager_id": "usr_123456789",
                "auth_provider": "local"
            }
        }


class UserUpdateRequest(BaseModel):
    """User update request model"""
    email: Optional[str] = Field(default=None, description="Email address")
    full_name: Optional[str] = Field(default=None, description="Full name")
    role: Optional[UserRole] = Field(default=None, description="User role")
    department: Optional[str] = Field(default=None, description="Department")
    organization_id: Optional[str] = Field(default=None, description="Organization ID")
    manager_id: Optional[str] = Field(default=None, description="Manager user ID")
    is_active: Optional[bool] = Field(default=None, description="Account status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "jane.smith.updated@company.com",
                "full_name": "Jane Smith (Updated)",
                "role": "manager",
                "department": "Senior Portfolio Management",
                "is_active": True
            }
        }


class SSOConfigRequest(BaseModel):
    """SSO configuration request model"""
    provider: AuthProvider = Field(..., description="SSO provider")
    client_id: str = Field(..., description="Client ID")
    client_secret: str = Field(..., description="Client secret")
    redirect_uri: str = Field(..., description="Redirect URI")
    authorization_url: str = Field(..., description="Authorization URL")
    token_url: str = Field(..., description="Token URL")
    userinfo_url: str = Field(..., description="User info URL")
    scopes: List[str] = Field(default_factory=list, description="OAuth scopes")
    enabled: bool = Field(default=True, description="Enable/disable provider")
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider": "oauth",
                "client_id": "xsema_oauth_client",
                "client_secret": "secret_key_here",
                "redirect_uri": "https://xsema.com/auth/oauth/callback",
                "authorization_url": "https://oauth.company.com/authorize",
                "token_url": "https://oauth.company.com/token",
                "userinfo_url": "https://oauth.company.com/userinfo",
                "scopes": ["openid", "profile", "email"],
                "enabled": True
            }
        }


class LDAPConfigRequest(BaseModel):
    """LDAP configuration request model"""
    server_url: str = Field(..., description="LDAP server URL")
    port: int = Field(default=389, description="LDAP port")
    use_ssl: bool = Field(default=False, description="Use SSL/TLS")
    bind_dn: str = Field(..., description="Bind DN")
    bind_password: str = Field(..., description="Bind password")
    search_base: str = Field(..., description="Search base")
    user_search_filter: str = Field(default="(sAMAccountName={username})", description="User search filter")
    group_search_filter: str = Field(default="(member={user_dn})", description="Group search filter")
    enabled: bool = Field(default=True, description="Enable/disable LDAP")
    
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


class AuthStatusResponse(BaseModel):
    """Authentication status response model"""
    is_authenticated: bool = Field(..., description="Authentication status")
    user: Optional[User] = Field(default=None, description="User information if authenticated")
    providers: List[AuthProvider] = Field(..., description="Available authentication providers")
    sso_enabled: bool = Field(..., description="SSO enabled status")
    ldap_enabled: bool = Field(..., description="LDAP enabled status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_authenticated": True,
                "user": {
                    "user_id": "usr_123456789",
                    "username": "john.doe",
                    "role": "analyst",
                    "auth_provider": "ldap"
                },
                "providers": ["local", "ldap", "oauth"],
                "sso_enabled": True,
                "ldap_enabled": True
            }
        }


# Authentication Endpoints
@router.post("/login", response_model=LoginResponse, summary="User Login")
async def login(request: LoginRequest):
    """
    Authenticate user with specified provider
    
    Supports:
    - Local authentication
    - LDAP/Active Directory
    - SSO providers (OAuth, SAML, OpenID Connect)
    """
    try:
        # Authenticate user
        user = enterprise_auth_service.authenticate_user(
            username=request.username,
            password=request.password,
            provider=request.provider
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # TODO: Handle MFA verification
        if request.mfa_code and user.mfa_status.value in ["enabled", "required"]:
            # Verify MFA code
            pass
        
        # Create JWT token
        access_token = enterprise_auth_service.create_jwt_token(user)
        
        # Update last login
        user.last_login = enterprise_auth_service._get_current_time()
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=enterprise_auth_service.jwt_expiry_hours * 3600,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/logout", summary="User Logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user
    
    Note: JWT tokens are stateless, so this endpoint is mainly for
    client-side cleanup. Consider implementing a token blacklist
    for enhanced security in production.
    """
    # TODO: Implement token blacklist for production
    return {"message": "Successfully logged out"}


@router.get("/status", response_model=AuthStatusResponse, summary="Authentication Status")
async def get_auth_status(current_user: Optional[User] = Depends(get_current_user)):
    """
    Get current authentication status and available providers
    """
    providers = [AuthProvider.LOCAL]
    
    if enterprise_auth_service.sso_configs:
        providers.extend(list(enterprise_auth_service.sso_configs.keys()))
    
    if enterprise_auth_service.ldap_config:
        providers.append(AuthProvider.LDAP)
    
    return AuthStatusResponse(
        is_authenticated=current_user is not None,
        user=current_user,
        providers=providers,
        sso_enabled=len(enterprise_auth_service.sso_configs) > 0,
        ldap_enabled=enterprise_auth_service.ldap_config is not None
    )


# User Management Endpoints
@router.post("/users", response_model=User, summary="Create User")
async def create_user(
    request: UserCreateRequest,
    current_user: User = Depends(require_admin)
):
    """
    Create a new user (Admin only)
    """
    # TODO: Implement user creation with database
    # For now, return a mock user
    new_user = User(
        user_id=f"usr_{len(str(hash(request.username)))}",
        username=request.username,
        email=request.email,
        full_name=request.full_name,
        role=request.role,
        department=request.department,
        organization_id=request.organization_id,
        manager_id=request.manager_id,
        auth_provider=request.auth_provider,
        permissions=enterprise_auth_service._get_permissions_from_role(request.role)
    )
    
    return new_user


@router.get("/users", response_model=List[User], summary="List Users")
async def list_users(
    current_user: User = Depends(require_admin),
    skip: int = 0,
    limit: int = 100
):
    """
    List all users (Admin only)
    """
    # TODO: Implement user listing with database
    # For now, return mock users
    mock_users = [
        User(
            user_id="usr_123456789",
            username="john.doe",
            email="john.doe@company.com",
            full_name="John Doe",
            role=UserRole.ANALYST,
            department="Investment Analysis",
            auth_provider=AuthProvider.LDAP
        ),
        User(
            user_id="usr_987654321",
            username="jane.smith",
            email="jane.smith@company.com",
            full_name="Jane Smith",
            role=UserRole.MANAGER,
            department="Portfolio Management",
            auth_provider=AuthProvider.LOCAL
        )
    ]
    
    return mock_users[skip:skip + limit]


@router.get("/users/{user_id}", response_model=User, summary="Get User")
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get user by ID
    
    Users can view their own profile, admins can view any user
    """
    if current_user.user_id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # TODO: Implement user retrieval from database
    # For now, return mock user
    mock_user = User(
        user_id=user_id,
        username="mock_user",
        email="mock@company.com",
        full_name="Mock User",
        role=UserRole.USER,
        auth_provider=AuthProvider.LOCAL
    )
    
    return mock_user


@router.put("/users/{user_id}", response_model=User, summary="Update User")
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    current_user: User = Depends(require_admin)
):
    """
    Update user (Admin only)
    """
    # TODO: Implement user update with database
    # For now, return updated mock user
    updated_user = User(
        user_id=user_id,
        username="mock_user",
        email=request.email or "mock@company.com",
        full_name=request.full_name or "Mock User",
        role=request.role or UserRole.USER,
        department=request.department,
        organization_id=request.organization_id,
        manager_id=request.manager_id,
        auth_provider=AuthProvider.LOCAL,
        is_active=request.is_active if request.is_active is not None else True
    )
    
    return updated_user


@router.delete("/users/{user_id}", summary="Delete User")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Delete user (Admin only)
    """
    # TODO: Implement user deletion with database
    return {"message": f"User {user_id} deleted successfully"}


# Configuration Endpoints
@router.post("/config/sso", summary="Configure SSO Provider")
async def configure_sso(
    request: SSOConfigRequest,
    current_user: User = Depends(require_admin)
):
    """
    Configure SSO provider (Admin only)
    """
    config = SSOConfig(**request.dict())
    enterprise_auth_service.configure_sso(config)
    
    return {"message": f"SSO provider {config.provider.value} configured successfully"}


@router.post("/config/ldap", summary="Configure LDAP")
async def configure_ldap(
    request: LDAPConfigRequest,
    current_user: User = Depends(require_admin)
):
    """
    Configure LDAP/Active Directory (Admin only)
    """
    config = LDAPConfig(**request.dict())
    enterprise_auth_service.configure_ldap(config)
    
    return {"message": "LDAP configured successfully"}


@router.get("/config/sso", summary="Get SSO Configuration")
async def get_sso_config(current_user: User = Depends(require_admin)):
    """
    Get SSO configuration (Admin only)
    """
    configs = []
    for provider, config in enterprise_auth_service.sso_configs.items():
        config_dict = config.dict()
        config_dict["client_secret"] = "***"  # Hide sensitive data
        configs.append(config_dict)
    
    return {"sso_configs": configs}


@router.get("/config/ldap", summary="Get LDAP Configuration")
async def get_ldap_config(current_user: User = Depends(require_admin)):
    """
    Get LDAP configuration (Admin only)
    """
    if not enterprise_auth_service.ldap_config:
        return {"ldap_config": None}
    
    config = enterprise_auth_service.ldap_config.dict()
    config["bind_password"] = "***"  # Hide sensitive data
    
    return {"ldap_config": config}


# SSO Callback Endpoints
@router.get("/sso/{provider}/callback", summary="SSO Callback")
async def sso_callback(
    provider: AuthProvider,
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None
):
    """
    Handle SSO callback from identity provider
    """
    if provider not in enterprise_auth_service.sso_configs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSO provider {provider.value} not configured"
        )
    
    # TODO: Implement SSO callback handling
    # This will vary based on the provider (OAuth, SAML, OpenID Connect)
    
    return {"message": f"SSO callback for {provider.value} received", "code": code, "state": state}


@router.get("/sso/{provider}/login", summary="SSO Login")
async def sso_login(provider: AuthProvider):
    """
    Initiate SSO login with specified provider
    """
    if provider not in enterprise_auth_service.sso_configs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSO provider {provider.value} not configured"
        )
    
    config = enterprise_auth_service.sso_configs[provider]
    
    # TODO: Implement SSO login initiation
    # This will vary based on the provider
    
    return {"message": f"Redirecting to {provider.value} login", "auth_url": config.authorization_url}
