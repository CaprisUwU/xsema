"""
Test Portfolio Endpoints

This script tests the portfolio-related API endpoints.
Created: 2025-08-01
"""
import pytest
import httpx
import json
import os
import logging
import sys
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_ID = "test_user_123"
TEST_PORTFOLIO = {
    "user_id": "test_user_123",
    "name": "Test Portfolio",
    "description": "A test portfolio",
    "risk_tolerance": 0.5
}

# Test client fixture with auth
@pytest.fixture
async def client():
    """Create an authenticated test client."""
    headers = {
        "Authorization": f"Bearer test_token",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers) as client:
        yield client

# Test create portfolio
@pytest.mark.asyncio
async def test_create_portfolio(client):
    """Test creating a new portfolio."""
    logger.info("Testing portfolio creation...")
    try:
        response = await client.post("/portfolios/", json=TEST_PORTFOLIO)
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["name"] == TEST_PORTFOLIO["name"], f"Name mismatch: {data['name']} != {TEST_PORTFOLIO['name']}"
        assert data["description"] == TEST_PORTFOLIO["description"], f"Description mismatch"
        
        logger.info("✅ Portfolio creation test passed")
        return data
    except Exception as e:
        logger.error(f"Portfolio creation test failed: {str(e)}")
        raise

# Test get portfolio
@pytest.mark.asyncio
async def test_get_portfolio(client):
    """Test retrieving a portfolio."""
    logger.info("Testing portfolio retrieval...")
    try:
        # First create a portfolio to test with
        create_resp = await client.post("/portfolios/", json=TEST_PORTFOLIO)
        assert create_resp.status_code == 201, "Failed to create test portfolio"
        portfolio = create_resp.json()
        portfolio_id = portfolio["id"]
        
        logger.info(f"Retrieving portfolio with ID: {portfolio_id}")
        response = await client.get(f"/portfolios/{portfolio_id}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["id"] == portfolio_id, f"Portfolio ID mismatch: {data['id']} != {portfolio_id}"
        logger.info("✅ Portfolio retrieval test passed")
        return data
    except Exception as e:
        logger.error(f"Portfolio retrieval test failed: {str(e)}")
        raise

# Test list portfolios
@pytest.mark.asyncio
async def test_list_portfolios(client):
    """Test listing all portfolios."""
    logger.info("Testing portfolio listing...")
    try:
        # First create a test portfolio
        await client.post("/portfolios/", json=TEST_PORTFOLIO)
        
        response = await client.get("/portfolios/")
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), f"Expected a list, got {type(data)}"
        assert len(data) > 0, "Expected at least one portfolio"
        
        logger.info(f"Found {len(data)} portfolios")
        logger.info("✅ Portfolio listing test passed")
        return data
    except Exception as e:
        logger.error(f"Portfolio listing test failed: {str(e)}")
        raise

# Test update portfolio
@pytest.mark.asyncio
async def test_update_portfolio(client):
    """Test updating a portfolio."""
    logger.info("Testing portfolio update...")
    try:
        # First create a portfolio to test with
        create_resp = await client.post("/portfolios/", json=TEST_PORTFOLIO)
        assert create_resp.status_code == 201, "Failed to create test portfolio"
        portfolio_id = create_resp.json()["id"]
        
        update_data = {
            "name": "Updated Test Portfolio",
            "description": "An updated test portfolio",
            "risk_tolerance": 0.7
        }
        
        logger.info(f"Updating portfolio {portfolio_id} with data: {update_data}")
        response = await client.put(f"/portfolios/{portfolio_id}", json=update_data)
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["name"] == update_data["name"], f"Name not updated: {data['name']}"
        assert data["description"] == update_data["description"], "Description not updated"
        assert data["risk_tolerance"] == update_data["risk_tolerance"], "Risk tolerance not updated"
        
        logger.info("✅ Portfolio update test passed")
        return data
    except Exception as e:
        logger.error(f"Portfolio update test failed: {str(e)}")
        raise

# Test delete portfolio
@pytest.mark.asyncio
async def test_delete_portfolio(client):
    """Test deleting a portfolio."""
    logger.info("Testing portfolio deletion...")
    try:
        # First create a portfolio to test with
        create_resp = await client.post("/portfolios/", json=TEST_PORTFOLIO)
        assert create_resp.status_code == 201, "Failed to create test portfolio"
        portfolio_id = create_resp.json()["id"]
        
        # Test deletion
        logger.info(f"Deleting portfolio {portfolio_id}")
        response = await client.delete(f"/portfolios/{portfolio_id}")
        logger.info(f"Delete response status: {response.status_code}")
        logger.info(f"Delete response body: {response.text}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify deletion
        logger.info(f"Verifying portfolio {portfolio_id} is deleted")
        response = await client.get(f"/portfolios/{portfolio_id}")
        logger.info(f"Get after delete status: {response.status_code}")
        
        assert response.status_code == 404, f"Expected 404 after deletion, got {response.status_code}"
        logger.info("✅ Portfolio deletion test passed")
    except Exception as e:
        logger.error(f"Portfolio deletion test failed: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    
    async def run_tests():
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            print("Running portfolio endpoint tests...")
            
            # Run tests in order
            try:
                print("\n=== Testing portfolio creation ===")
                created_portfolio = await test_create_portfolio(client)
                print("✅ Portfolio creation test passed")
                
                print("\n=== Testing portfolio retrieval ===")
                portfolio = await test_get_portfolio(client)
                print("✅ Portfolio retrieval test passed")
                
                print("\n=== Testing portfolio listing ===")
                portfolios = await test_list_portfolios(client)
                print(f"✅ Found {len(portfolios)} portfolios")
                
                print("\n=== Testing portfolio update ===")
                updated_portfolio = await test_update_portfolio(client)
                print("✅ Portfolio update test passed")
                
                print("\n=== Testing portfolio deletion ===")
                await test_delete_portfolio(client)
                print("✅ Portfolio deletion test passed")
                
                print("\n✅ All portfolio endpoint tests completed successfully!")
                
            except AssertionError as e:
                print(f"❌ Test failed: {str(e)}")
                raise
    
    asyncio.run(run_tests())
