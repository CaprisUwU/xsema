"""
SAML Authentication Endpoints for XSEMA Enterprise SSO

This module provides SAML 2.0 endpoints for enterprise single sign-on:
- SAML metadata endpoint
- SAML login initiation
- SAML assertion consumer service (ACS)
- SAML logout
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Request, Response, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel

from core.saml_provider import get_saml_provider, SAMLConfig
from core.enterprise_auth import EnterpriseAuthService, User, UserRole

router = APIRouter()


class SAMLInitiateRequest(BaseModel):
    """Request to initiate SAML authentication"""
    relay_state: Optional[str] = None
    force_authn: bool = False


class SAMLResponse(BaseModel):
    """SAML response data"""
    saml_response: str
    relay_state: Optional[str] = None


@router.get("/metadata", response_class=HTMLResponse)
async def saml_metadata():
    """
    SAML metadata endpoint for identity provider configuration.
    
    Returns:
        HTMLResponse: SAML metadata XML
    """
    saml_provider = get_saml_provider()
    if not saml_provider:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SAML provider not configured"
        )
    
    metadata = saml_provider.create_metadata()
    return HTMLResponse(content=metadata, media_type="application/xml")


@router.post("/initiate")
async def saml_initiate(request: SAMLInitiateRequest):
    """
    Initiate SAML authentication flow.
    
    Args:
        request: SAML initiation request
        
    Returns:
        RedirectResponse: Redirect to identity provider
    """
    saml_provider = get_saml_provider()
    if not saml_provider:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SAML provider not configured"
        )
    
    # Create SAML authentication request
    auth_url = saml_provider.create_authn_request(
        relay_state=request.relay_state
    )
    
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/initiate")
async def saml_initiate_get(relay_state: Optional[str] = None):
    """
    Initiate SAML authentication flow (GET method).
    
    Args:
        relay_state: Optional relay state for SAML request
        
    Returns:
        RedirectResponse: Redirect to identity provider
    """
    saml_provider = get_saml_provider()
    if not saml_provider:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SAML provider not configured"
        )
    
    # Create SAML authentication request
    auth_url = saml_provider.create_authn_request(
        relay_state=relay_state
    )
    
    return RedirectResponse(url=auth_url, status_code=302)


@router.post("/acs")
async def saml_acs(
    SAMLResponse: str = Form(...),
    RelayState: Optional[str] = Form(None)
):
    """
    SAML Assertion Consumer Service (ACS).
    
    This endpoint receives the SAML response from the identity provider
    after successful authentication.
    
    Args:
        SAMLResponse: Base64 encoded SAML response
        RelayState: Optional relay state from SAML request
        
    Returns:
        HTMLResponse: Success page or redirect
    """
    try:
        saml_provider = get_saml_provider()
        if not saml_provider:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="SAML provider not configured"
            )
        
        # Parse SAML response
        result = saml_provider.parse_saml_response(SAMLResponse)
        user_data = result['user_data']
        
        # Create or update user in XSEMA system
        auth_service = EnterpriseAuthService()
        
        # Check if user exists
        existing_user = auth_service.get_user_by_email(user_data['email'])
        
        if existing_user:
            # Update existing user
            user = auth_service.update_user(
                user_id=existing_user.user_id,
                email=user_data['email'],
                full_name=user_data['full_name'],
                role=UserRole(user_data['role']),
                department=user_data.get('department')
            )
        else:
            # Create new user
            user = auth_service.create_user(
                email=user_data['email'],
                full_name=user_data['full_name'],
                username=user_data['username'],
                role=UserRole(user_data['role']),
                department=user_data.get('department'),
                auth_provider="saml"
            )
        
        # Generate JWT token
        token = auth_service.create_access_token(user.email)
        
        # Return success page with token
        success_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SAML Authentication Success</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .success {{ color: green; font-size: 24px; }}
                .token {{ background: #f0f0f0; padding: 20px; margin: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="success">✅ SAML Authentication Successful!</div>
            <p>Welcome, {user.full_name}!</p>
            <p>You have been successfully authenticated via SAML.</p>
            <div class="token">
                <strong>Access Token:</strong><br>
                <code>{token}</code>
            </div>
            <p><a href="/enterprise">Go to Enterprise Dashboard</a></p>
            <script>
                // Store token in localStorage for frontend use
                localStorage.setItem('xsema_token', '{token}');
                localStorage.setItem('xsema_user', JSON.stringify({{
                    email: '{user.email}',
                    full_name: '{user.full_name}',
                    role: '{user.role.value}'
                }}));
            </script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=success_html)
        
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SAML Authentication Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: red; font-size: 24px; }}
            </style>
        </head>
        <body>
            <div class="error">❌ SAML Authentication Failed</div>
            <p>Error: {str(e)}</p>
            <p><a href="/enterprise">Return to Enterprise Dashboard</a></p>
        </body>
        </html>
        """
        
        return HTMLResponse(content=error_html, status_code=400)


@router.get("/logout")
async def saml_logout(session_index: Optional[str] = None, name_id: Optional[str] = None):
    """
    Initiate SAML logout.
    
    Args:
        session_index: SAML session index
        name_id: SAML name ID
        
    Returns:
        RedirectResponse: Redirect to identity provider logout
    """
    saml_provider = get_saml_provider()
    if not saml_provider:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SAML provider not configured"
        )
    
    # Create SAML logout request
    logout_url = saml_provider.create_logout_request(
        session_index=session_index or "default",
        name_id=name_id or "default"
    )
    
    return RedirectResponse(url=logout_url, status_code=302)


@router.get("/status")
async def saml_status():
    """
    Check SAML provider status.
    
    Returns:
        dict: SAML provider configuration status
    """
    saml_provider = get_saml_provider()
    
    if saml_provider:
        return {
            "status": "configured",
            "entity_id": saml_provider.config.entity_id,
            "idp_entity_id": saml_provider.config.idp_entity_id,
            "acs_url": saml_provider.config.acs_url
        }
    else:
        return {
            "status": "not_configured",
            "message": "SAML provider not configured"
        }
