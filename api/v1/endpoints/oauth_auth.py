"""
OAuth 2.0 Authentication Endpoints for XSEMA Enterprise

This module provides OAuth 2.0 endpoints for modern authentication:
- Authorization endpoint
- Token endpoint
- Token introspection
- Client management
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel, Field

from core.oauth_provider import get_oauth_provider, OAuthClient
from core.enterprise_auth import EnterpriseAuthService, UserRole

router = APIRouter()


class OAuthAuthorizationRequest(BaseModel):
    """OAuth authorization request"""
    response_type: str = Field(..., description="Response type (code)")
    client_id: str = Field(..., description="Client identifier")
    redirect_uri: str = Field(..., description="Redirect URI")
    scope: Optional[str] = Field(default="read write", description="Requested scopes")
    state: Optional[str] = Field(default=None, description="State parameter")


class OAuthTokenRequest(BaseModel):
    """OAuth token request"""
    grant_type: str = Field(..., description="Grant type")
    client_id: str = Field(..., description="Client identifier")
    client_secret: str = Field(..., description="Client secret")
    code: Optional[str] = Field(default=None, description="Authorization code")
    redirect_uri: Optional[str] = Field(default=None, description="Redirect URI")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")


class OAuthClientRequest(BaseModel):
    """OAuth client creation request"""
    client_name: str = Field(..., description="Client name")
    redirect_uris: list[str] = Field(..., description="Allowed redirect URIs")
    scopes: Optional[list[str]] = Field(default=["read", "write"], description="Allowed scopes")
    grant_types: Optional[list[str]] = Field(default=["authorization_code"], description="Allowed grant types")


@router.get("/authorize")
async def oauth_authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: Optional[str] = "read write",
    state: Optional[str] = None
):
    """
    OAuth 2.0 authorization endpoint.
    
    This endpoint initiates the OAuth authorization flow.
    Users are redirected here to authorize applications.
    
    Args:
        response_type: Must be "code"
        client_id: Client application identifier
        redirect_uri: Where to redirect after authorization
        scope: Requested permissions
        state: Optional state parameter
        
    Returns:
        HTMLResponse: Authorization page
    """
    try:
        oauth_provider = get_oauth_provider()
        
        # Validate request
        if response_type != "code":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only authorization code flow supported"
            )
        
        # Create authorization URL
        auth_url = oauth_provider.create_authorization_url(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state
        )
        
        # For now, return a simple authorization page
        # In production, this would be a proper login form
        auth_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>XSEMA OAuth Authorization</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .form {{ background: white; padding: 30px; border: 1px solid #ddd; border-radius: 5px; }}
                .btn {{ background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
                .btn:hover {{ background: #0056b3; }}
                .info {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 XSEMA OAuth Authorization</h1>
                    <p>Authorize application access to your account</p>
                </div>
                
                <div class="info">
                    <strong>Application:</strong> {client_id}<br>
                    <strong>Scopes:</strong> {scope}<br>
                    <strong>Redirect URI:</strong> {redirect_uri}
                </div>
                
                <div class="form">
                    <h3>Login to Authorize</h3>
                    <form action="/api/v1/oauth/authorize" method="post">
                        <input type="hidden" name="response_type" value="{response_type}">
                        <input type="hidden" name="client_id" value="{client_id}">
                        <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                        <input type="hidden" name="scope" value="{scope}">
                        <input type="hidden" name="state" value="{state or ''}">
                        
                        <p><strong>Email:</strong><br>
                        <input type="email" name="email" required style="width: 100%; padding: 8px; margin: 5px 0;"></p>
                        
                        <p><strong>Password:</strong><br>
                        <input type="password" name="password" required style="width: 100%; padding: 8px; margin: 5px 0;"></p>
                        
                        <button type="submit" class="btn">Authorize Application</button>
                    </form>
                    
                    <p style="margin-top: 20px;">
                        <a href="/enterprise" style="color: #007bff;">Cancel and return to dashboard</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=auth_html)
        
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: red; font-size: 24px; }}
            </style>
        </head>
        <body>
            <div class="error">❌ OAuth Authorization Error</div>
            <p>Error: {str(e)}</p>
            <p><a href="/enterprise">Return to Enterprise Dashboard</a></p>
        </body>
        </html>
        """
        
        return HTMLResponse(content=error_html, status_code=400)


@router.post("/authorize")
async def oauth_authorize_post(
    response_type: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    scope: str = Form(...),
    state: str = Form(None),
    email: str = Form(...),
    password: str = Form(...)
):
    """
    Handle OAuth authorization form submission.
    
    Args:
        response_type: Response type from form
        client_id: Client ID from form
        redirect_uri: Redirect URI from form
        scope: Requested scopes from form
        state: State parameter from form
        email: User email
        password: User password
        
    Returns:
        RedirectResponse: Redirect to client with authorization code
    """
    try:
        oauth_provider = get_oauth_provider()
        auth_service = EnterpriseAuthService()
        
        # Authenticate user
        user = auth_service.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create authorization code
        auth_url = oauth_provider.create_authorization_url(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state
        )
        
        # Extract authorization code from URL
        from urllib.parse import parse_qs, urlparse
        parsed_url = urlparse(auth_url)
        query_params = parse_qs(parsed_url.query)
        auth_code = query_params.get('code', [None])[0]
        
        # Set user ID for the authorization code
        if auth_code in oauth_provider.authorization_codes:
            oauth_provider.authorization_codes[auth_code]["user_id"] = user.user_id
        
        # Build redirect URL with authorization code
        redirect_params = {
            "code": auth_code,
            "state": state or ""
        }
        
        redirect_url = f"{redirect_uri}?{urlencode(redirect_params)}"
        
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Authorization Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: red; font-size: 24px; }}
            </style>
        </head>
        <body>
            <div class="error">❌ OAuth Authorization Failed</div>
            <p>Error: {str(e)}</p>
            <p><a href="/enterprise">Return to Enterprise Dashboard</a></p>
        </body>
        </html>
        """
        
        return HTMLResponse(content=error_html, status_code=400)


@router.post("/token")
async def oauth_token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None)
):
    """
    OAuth 2.0 token endpoint.
    
    This endpoint exchanges authorization codes for access tokens
    and handles token refresh.
    
    Args:
        grant_type: Grant type (authorization_code, refresh_token)
        client_id: Client identifier
        client_secret: Client secret
        code: Authorization code (for authorization_code grant)
        redirect_uri: Redirect URI (for authorization_code grant)
        refresh_token: Refresh token (for refresh_token grant)
        
    Returns:
        dict: Token response
    """
    try:
        oauth_provider = get_oauth_provider()
        
        if grant_type == "authorization_code":
            if not code or not redirect_uri:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Code and redirect_uri required for authorization_code grant"
                )
            
            token = oauth_provider.exchange_code_for_token(
                client_id=client_id,
                client_secret=client_secret,
                code=code,
                redirect_uri=redirect_uri,
                grant_type=grant_type
            )
            
        elif grant_type == "refresh_token":
            if not refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Refresh token required for refresh_token grant"
                )
            
            token = oauth_provider.refresh_access_token(
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=refresh_token
            )
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported grant type: {grant_type}"
            )
        
        return {
            "access_token": token.access_token,
            "token_type": token.token_type,
            "expires_in": token.expires_in,
            "refresh_token": token.refresh_token,
            "scope": token.scope
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token request failed: {str(e)}"
        )


@router.post("/introspect")
async def oauth_introspect(token: str = Form(...)):
    """
    OAuth 2.0 token introspection endpoint.
    
    This endpoint allows clients to check the validity and
    metadata of an access token.
    
    Args:
        token: Access token to introspect
        
    Returns:
        dict: Token introspection result
    """
    try:
        oauth_provider = get_oauth_provider()
        token_info = oauth_provider.validate_access_token(token)
        
        if token_info:
            return {
                "active": True,
                "scope": token_info.get("scope", ""),
                "client_id": token_info.get("client_id", ""),
                "user_id": token_info.get("user_id"),
                "email": token_info.get("email"),
                "full_name": token_info.get("full_name"),
                "role": token_info.get("role")
            }
        else:
            return {
                "active": False
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token introspection failed: {str(e)}"
        )


@router.post("/revoke")
async def oauth_revoke(
    token: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...)
):
    """
    OAuth 2.0 token revocation endpoint.
    
    This endpoint allows clients to revoke access tokens.
    
    Args:
        token: Access token to revoke
        client_id: Client identifier
        client_secret: Client secret
        
    Returns:
        dict: Revocation result
    """
    try:
        oauth_provider = get_oauth_provider()
        success = oauth_provider.revoke_token(token, client_id, client_secret)
        
        if success:
            return {"message": "Token revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to revoke token"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token revocation failed: {str(e)}"
        )


@router.post("/clients")
async def create_oauth_client(request: OAuthClientRequest):
    """
    Create new OAuth client.
    
    Args:
        request: OAuth client creation request
        
    Returns:
        dict: Created client information
    """
    try:
        oauth_provider = get_oauth_provider()
        client = oauth_provider.create_client(
            client_name=request.client_name,
            redirect_uris=request.redirect_uris,
            scopes=request.scopes,
            grant_types=request.grant_types
        )
        
        return {
            "message": "OAuth client created successfully",
            "client": {
                "client_id": client.client_id,
                "client_secret": client.client_secret,
                "client_name": client.client_name,
                "redirect_uris": client.redirect_uris,
                "scopes": client.scopes,
                "grant_types": client.grant_types
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create OAuth client: {str(e)}"
        )


@router.get("/clients/{client_id}")
async def get_oauth_client(client_id: str):
    """
    Get OAuth client information.
    
    Args:
        client_id: Client identifier
        
    Returns:
        dict: Client information
    """
    try:
        oauth_provider = get_oauth_provider()
        client_info = oauth_provider.get_client_info(client_id)
        
        if client_info:
            return client_info
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OAuth client not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get OAuth client: {str(e)}"
        )


@router.get("/.well-known/oauth-authorization-server")
async def oauth_discovery():
    """
    OAuth 2.0 discovery endpoint.
    
    This endpoint provides OAuth 2.0 server metadata
    for client discovery and configuration.
    
    Returns:
        dict: OAuth server metadata
    """
    return {
        "issuer": "https://xsema.co.uk",
        "authorization_endpoint": "https://xsema.co.uk/api/v1/oauth/authorize",
        "token_endpoint": "https://xsema.co.uk/api/v1/oauth/token",
        "token_introspection_endpoint": "https://xsema.co.uk/api/v1/oauth/introspect",
        "revocation_endpoint": "https://xsema.co.uk/api/v1/oauth/revoke",
        "scopes_supported": ["read", "write", "admin"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "response_types_supported": ["code"],
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
        "revocation_endpoint_auth_methods_supported": ["client_secret_post"],
        "introspection_endpoint_auth_methods_supported": ["client_secret_post"]
    }
