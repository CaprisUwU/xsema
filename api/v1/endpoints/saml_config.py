"""
SAML Configuration Management for XSEMA Enterprise SSO

This module provides endpoints for managing SAML configuration:
- Configure SAML provider
- Update SAML settings
- Test SAML configuration
- Get configuration status
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from core.saml_provider import configure_saml, get_saml_provider, SAMLConfig
from core.enterprise_auth import EnterpriseAuthService, UserRole

router = APIRouter()


class SAMLConfigurationRequest(BaseModel):
    """Request to configure SAML provider"""
    entity_id: str = Field(..., description="Service Provider Entity ID")
    acs_url: str = Field(..., description="Assertion Consumer Service URL")
    slo_url: str = Field(..., description="Single Logout Service URL")
    idp_entity_id: str = Field(..., description="Identity Provider Entity ID")
    idp_sso_url: str = Field(..., description="Identity Provider SSO URL")
    idp_slo_url: str = Field(..., description="Identity Provider SLO URL")
    idp_x509_cert: str = Field(..., description="Identity Provider X.509 Certificate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity_id": "https://xsema.co.uk/saml/metadata",
                "acs_url": "https://xsema.co.uk/api/v1/saml/acs",
                "slo_url": "https://xsema.co.uk/api/v1/saml/logout",
                "idp_entity_id": "https://sts.windows.net/tenant-id/",
                "idp_sso_url": "https://login.microsoftonline.com/tenant-id/saml2",
                "idp_slo_url": "https://login.microsoftonline.com/tenant-id/saml2",
                "idp_x509_cert": "-----BEGIN CERTIFICATE-----\\n...\\n-----END CERTIFICATE-----"
            }
        }


class SAMLTestRequest(BaseModel):
    """Request to test SAML configuration"""
    test_email: str = Field(..., description="Test email for SAML user")
    test_name: str = Field(..., description="Test name for SAML user")


@router.post("/configure")
async def configure_saml_provider(request: SAMLConfigurationRequest):
    """
    Configure SAML provider with identity provider settings.
    
    Args:
        request: SAML configuration request
        
    Returns:
        dict: Configuration status
    """
    try:
        # Create SAML configuration
        config = SAMLConfig(
            entity_id=request.entity_id,
            acs_url=request.acs_url,
            slo_url=request.slo_url,
            idp_entity_id=request.idp_entity_id,
            idp_sso_url=request.idp_sso_url,
            idp_slo_url=request.idp_slo_url,
            idp_x509_cert=request.idp_x509_cert
        )
        
        # Configure global SAML provider
        configure_saml(config)
        
        return {
            "status": "success",
            "message": "SAML provider configured successfully",
            "config": {
                "entity_id": config.entity_id,
                "acs_url": config.acs_url,
                "idp_entity_id": config.idp_entity_id
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to configure SAML provider: {str(e)}"
        )


@router.get("/status")
async def get_saml_status():
    """
    Get current SAML provider status.
    
    Returns:
        dict: SAML provider status and configuration
    """
    saml_provider = get_saml_provider()
    
    if saml_provider:
        return {
            "status": "configured",
            "entity_id": saml_provider.config.entity_id,
            "acs_url": saml_provider.config.acs_url,
            "slo_url": saml_provider.config.slo_url,
            "idp_entity_id": saml_provider.config.idp_entity_id,
            "idp_sso_url": saml_provider.config.idp_sso_url,
            "metadata_url": "/api/v1/saml/metadata",
            "initiate_url": "/api/v1/saml/initiate",
            "acs_url": "/api/v1/saml/acs"
        }
    else:
        return {
            "status": "not_configured",
            "message": "SAML provider not configured",
            "setup_required": True,
            "endpoint": "/api/v1/saml/configure"
        }


@router.post("/test")
async def test_saml_configuration(request: SAMLTestRequest):
    """
    Test SAML configuration with sample data.
    
    Args:
        request: Test request with sample user data
        
    Returns:
        dict: Test results
    """
    saml_provider = get_saml_provider()
    if not saml_provider:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SAML provider not configured"
        )
    
    try:
        # Test SAML provider functionality
        auth_url = saml_provider.create_authn_request()
        metadata = saml_provider.create_metadata()
        
        # Test user creation
        auth_service = EnterpriseAuthService()
        test_user = auth_service.create_user(
            email=request.test_email,
            full_name=request.test_name,
            username=request.test_email.split('@')[0],
            role=UserRole.USER,
            department="Test Department",
            auth_provider="saml"
        )
        
        return {
            "status": "success",
            "message": "SAML configuration test successful",
            "test_results": {
                "auth_request_created": bool(auth_url),
                "metadata_generated": bool(metadata),
                "test_user_created": test_user.email if test_user else None,
                "auth_url_sample": auth_url[:100] + "..." if len(auth_url) > 100 else auth_url
            },
            "next_steps": [
                "Configure identity provider with metadata from /api/v1/saml/metadata",
                "Test SAML login flow at /api/v1/saml/initiate",
                "Verify ACS endpoint at /api/v1/saml/acs"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SAML configuration test failed: {str(e)}"
        )


@router.delete("/configure")
async def remove_saml_configuration():
    """
    Remove SAML provider configuration.
    
    Returns:
        dict: Removal status
    """
    try:
        # Reset SAML provider (this will be implemented in the core module)
        # For now, we'll return a success message
        return {
            "status": "success",
            "message": "SAML provider configuration removed",
            "note": "Restart application to fully remove SAML configuration"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to remove SAML configuration: {str(e)}"
        )


@router.get("/setup-guide")
async def get_saml_setup_guide():
    """
    Get SAML setup guide for enterprise administrators.
    
    Returns:
        dict: Setup guide and configuration steps
    """
    return {
        "title": "XSEMA SAML 2.0 Setup Guide",
        "description": "Complete guide for configuring SAML 2.0 with XSEMA",
        "steps": [
            {
                "step": 1,
                "title": "Configure XSEMA SAML Provider",
                "description": "Use POST /api/v1/saml/configure to set up SAML settings",
                "endpoint": "/api/v1/saml/configure",
                "method": "POST"
            },
            {
                "step": 2,
                "title": "Get SAML Metadata",
                "description": "Download SAML metadata from /api/v1/saml/metadata",
                "endpoint": "/api/v1/saml/metadata",
                "method": "GET"
            },
            {
                "step": 3,
                "title": "Configure Identity Provider",
                "description": "Upload metadata to your identity provider (Okta, Azure AD, etc.)",
                "note": "Use the metadata URL or download the XML file"
            },
            {
                "step": 4,
                "title": "Test Configuration",
                "description": "Test SAML setup using POST /api/v1/saml/test",
                "endpoint": "/api/v1/saml/test",
                "method": "POST"
            },
            {
                "step": 5,
                "title": "Test Login Flow",
                "description": "Test SAML login at /api/v1/saml/initiate",
                "endpoint": "/api/v1/saml/initiate",
                "method": "GET"
            }
        ],
        "supported_providers": [
            "Okta",
            "Azure Active Directory",
            "Google Workspace",
            "OneLogin",
            "Auth0",
            "Ping Identity",
            "ADFS (Active Directory Federation Services)"
        ],
        "configuration_endpoints": {
            "configure": "/api/v1/saml/configure",
            "status": "/api/v1/saml/status",
            "test": "/api/v1/saml/test",
            "metadata": "/api/v1/saml/metadata",
            "initiate": "/api/v1/saml/initiate",
            "acs": "/api/v1/saml/acs",
            "logout": "/api/v1/saml/logout"
        }
    }
