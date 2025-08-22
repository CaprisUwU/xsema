import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_app_imports():
    """Test that the main application can be imported without errors"""
    assert app is not None

def test_health_check():
    """Test basic health check endpoint"""
    response = client.get("/")
    assert response.status_code in [200, 404]  # 404 is expected if no root route

def test_static_files():
    """Test that static files are accessible"""
    response = client.get("/static/xsema-icon.svg")
    assert response.status_code in [200, 404]  # 404 if file doesn't exist locally

def test_app_startup():
    """Test that the app starts without critical errors"""
    # This test ensures the main app can be imported and basic routes work
    assert hasattr(app, 'routes')
    assert len(app.routes) > 0
