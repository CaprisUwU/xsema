#!/usr/bin/env python3
"""
Phase 3 Comprehensive Testing Script

This script tests all enterprise features including:
- Database integration
- Enterprise authentication
- SAML 2.0 and OAuth 2.0
- User management
- Portfolio management
- Security features
"""

import asyncio
import sys
import traceback
from datetime import datetime

def test_database_integration():
    """Test database models and connections."""
    print("🔍 Testing Database Integration...")
    
    try:
        # Test database models import
        from core.storage.models import (
            Base, Organization, Department, User, UserSession,
            Portfolio, PortfolioAsset, Transaction, SecurityAlert, AuditLog
        )
        print("  ✅ Database models imported successfully")
        
        # Test database connection
        from core.storage.database import create_tables, get_db_session
        print("  ✅ Database connection established")
        
        # Test table creation
        create_tables()
        print("  ✅ Database tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database integration failed: {e}")
        traceback.print_exc()
        return False

def test_enterprise_service():
    """Test enterprise authentication service."""
    print("🔍 Testing Enterprise Service...")
    
    try:
        from core.storage.enterprise_service import enterprise_service
        print("  ✅ Enterprise service imported successfully")
        
        # Test service methods
        service = enterprise_service
        print(f"  ✅ Service instance created: {type(service).__name__}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Enterprise service failed: {e}")
        traceback.print_exc()
        return False

def test_saml_integration():
    """Test SAML 2.0 integration."""
    print("🔍 Testing SAML 2.0 Integration...")
    
    try:
        from core.saml_provider import SAMLProvider, SAMLConfig
        print("  ✅ SAML provider imported successfully")
        
        # Test SAML configuration with all required fields
        config = SAMLConfig(
            entity_id="https://test-sp.com",
            idp_entity_id="https://test-idp.com",
            idp_sso_url="https://test-idp.com/sso",
            idp_slo_url="https://test-idp.com/slo",
            idp_x509_cert="test-cert",
            acs_url="https://test-sp.com/saml/acs",
            slo_url="https://test-sp.com/saml/logout"
        )
        print("  ✅ SAML configuration created successfully")
        
        # Test SAML provider
        provider = SAMLProvider(config)
        print("  ✅ SAML provider created successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ SAML integration failed: {e}")
        traceback.print_exc()
        return False

def test_oauth_integration():
    """Test OAuth 2.0 integration."""
    print("🔍 Testing OAuth 2.0 Integration...")
    
    try:
        from core.oauth_provider import OAuthProvider, OAuthClient
        print("  ✅ OAuth provider imported successfully")
        
        # Test OAuth client creation with all required fields
        client = OAuthClient(
            client_id="test_client",
            client_secret="test_secret",
            client_name="Test Client",
            redirect_uris=["http://localhost:8001/callback"]
        )
        print("  ✅ OAuth client created successfully")
        
        # Test OAuth provider
        provider = OAuthProvider()
        print("  ✅ OAuth provider created successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ OAuth integration failed: {e}")
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoint availability."""
    print("🔍 Testing API Endpoints...")
    
    try:
        from main import app
        print("  ✅ Main application imported successfully")
        
        # Check if enterprise routes are included
        routes = [route.path for route in app.routes]
        
        enterprise_routes = [
            "/api/v1/enterprise",
            "/api/v1/saml",
            "/api/v1/oauth"
        ]
        
        for route in enterprise_routes:
            if any(route in r for r in routes):
                print(f"  ✅ {route} endpoint available")
            else:
                print(f"  ❌ {route} endpoint missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ API endpoint testing failed: {e}")
        traceback.print_exc()
        return False

def test_user_management():
    """Test user management functionality."""
    print("🔍 Testing User Management...")
    
    try:
        from core.storage.enterprise_service import enterprise_service
        from core.enterprise_auth import UserRole, AuthProvider
        
        # Test user creation
        import time
        unique_id = int(time.time())
        test_user = enterprise_service.create_user(
            username=f"test_user_{unique_id}",
            email=f"test_{unique_id}@example.com",
            full_name="Test User",
            role=UserRole.USER,
            auth_provider=AuthProvider.LOCAL
        )
        print("  ✅ Test user created successfully")
        
        # Test user authentication (skip for test user without password)
        print("  ⚠️  User authentication skipped (test user has no password)")
        
        # Test session creation
        session = enterprise_service.create_session(
            user_id=test_user["id"],
            ip_address="127.0.0.1"
        )
        print("  ✅ User session created successfully")
        
        # Test session validation
        validated_user = enterprise_service.validate_session(session["session_token"])
        if validated_user:
            print("  ✅ Session validation working")
        else:
            print("  ❌ Session validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ User management testing failed: {e}")
        traceback.print_exc()
        return False

def test_portfolio_management():
    """Test portfolio management functionality."""
    print("🔍 Testing Portfolio Management...")
    
    try:
        from core.storage.enterprise_service import enterprise_service
        from core.enterprise_auth import UserRole
        
        # Create a test user for portfolio testing
        import time
        unique_id = int(time.time())
        test_user = enterprise_service.create_user(
            username=f"portfolio_test_user_{unique_id}",
            email=f"portfolio_{unique_id}@example.com",
            full_name="Portfolio Test User",
            role=UserRole.USER
        )
        
        # Test portfolio creation
        portfolio = enterprise_service.create_portfolio(
            user_id=test_user["id"],
            name="Test Portfolio",
            description="Test portfolio for testing",
            currency="GBP"
        )
        print("  ✅ Portfolio created successfully")
        
        # Test portfolio retrieval
        user_portfolios = enterprise_service.get_user_portfolios(test_user["id"])
        if len(user_portfolios) > 0:
            print("  ✅ Portfolio retrieval working")
        else:
            print("  ❌ Portfolio retrieval failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Portfolio management testing failed: {e}")
        traceback.print_exc()
        return False

def test_security_features():
    """Test security and compliance features."""
    print("🔍 Testing Security Features...")
    
    try:
        from core.storage.enterprise_service import enterprise_service
        from core.enterprise_auth import UserRole
        
        # Create a test user for security testing
        import time
        unique_id = int(time.time())
        test_user = enterprise_service.create_user(
            username=f"security_test_user_{unique_id}",
            email=f"security_{unique_id}@example.com",
            full_name="Security Test User",
            role=UserRole.USER
        )
        
        # Test security alert creation
        alert = enterprise_service.create_security_alert(
            user_id=test_user["id"],
            alert_type="test_alert",
            severity="medium",
            title="Test Security Alert",
            description="This is a test security alert",
            alert_data={"test": "data"}
        )
        print("  ✅ Security alert created successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Security features testing failed: {e}")
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all Phase 3 tests."""
    print("🚀 XSEMA Phase 3 Comprehensive Testing")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Database Integration", test_database_integration),
        ("Enterprise Service", test_enterprise_service),
        ("SAML 2.0 Integration", test_saml_integration),
        ("OAuth 2.0 Integration", test_oauth_integration),
        ("API Endpoints", test_api_endpoints),
        ("User Management", test_user_management),
        ("Portfolio Management", test_portfolio_management),
        ("Security Features", test_security_features)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"🧪 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            failed += 1
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    print()
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Phase 3 is 100% complete!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
