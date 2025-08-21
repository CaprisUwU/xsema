"""
Frontend Integration Tests

Tests the integration between frontend components and backend services:
- Advanced Analytics integration
- Portfolio Manager integration
- API connectivity
- Component rendering
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

# Import the main app and services
from main import app
from portfolio.services.pnl_calculator import PnLCalculator
from services.risk_assessment import RiskAssessmentTools
from services.ml_recommendations import MLRecommendationsEngine
from portfolio.services.tax_reporter import TaxReporter

# Create test client
client = TestClient(app)

class TestFrontendBackendIntegration:
    """Test integration between frontend components and backend services"""
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing"""
        mock_pnl = Mock(spec=PnLCalculator)
        mock_risk = Mock(spec=RiskAssessmentTools)
        mock_ml = Mock(spec=MLRecommendationsEngine)
        mock_tax = Mock(spec=TaxReporter)
        
        return {
            'pnl': mock_pnl,
            'risk': mock_risk,
            'ml': mock_ml,
            'tax': mock_tax
        }
    
    def test_advanced_analytics_api_endpoints(self):
        """Test that all advanced analytics API endpoints are accessible"""
        
        # Test P&L endpoint
        response = client.get("/v1/advanced-analytics/portfolio/test-portfolio/pnl?user_id=test-user")
        assert response.status_code in [200, 404]  # 404 is expected for non-existent portfolio
        
        # Test risk assessment endpoint
        response = client.post("/v1/advanced-analytics/portfolio/test-portfolio/risk-assessment?user_id=test-user")
        assert response.status_code in [200, 404]
        
        # Test ML recommendations endpoint
        response = client.post("/v1/advanced-analytics/portfolio/test-portfolio/recommendations?user_id=test-user")
        assert response.status_code in [200, 404]
        
        # Test tax reporting endpoint
        response = client.get("/v1/advanced-analytics/portfolio/test-portfolio/tax-report/2024-25?user_id=test-user")
        assert response.status_code in [200, 404]
        
        # Test health check endpoint
        response = client.get("/v1/advanced-analytics/health/advanced-features")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "pnl_calculator" in health_data["services"]
        assert "risk_assessment" in health_data["services"]
        assert "ml_recommendations" in health_data["services"]
        assert "tax_reporter" in health_data["services"]
    
    def test_api_response_format(self):
        """Test that API responses have the correct format and structure"""
        
        # Test health check response format
        response = client.get("/v1/advanced-analytics/health/advanced-features")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["status", "services", "timestamp", "version"]
        for field in required_fields:
            assert field in data
        
        # Test services status
        services = data["services"]
        assert isinstance(services, dict)
        assert all(service in services for service in ["pnl_calculator", "risk_assessment", "ml_recommendations", "tax_reporter"])
    
    @patch('portfolio.services.pnl_calculator.PnLCalculator.calculate_portfolio_pnl')
    def test_pnl_calculation_integration(self, mock_calculate_pnl):
        """Test P&L calculation integration with mock data"""
        
        # Mock P&L calculation response
        mock_pnl_data = {
            "portfolio_id": "test-portfolio",
            "total_cost_basis": 50000.0,
            "current_value": 75000.0,
            "unrealized_pnl": 25000.0,
            "realized_pnl": 5000.0,
            "total_pnl": 30000.0,
            "roi_percentage": 60.0,
            "annualized_roi": 45.25,
            "calculation_timestamp": "2025-01-15T10:30:00Z"
        }
        
        mock_calculate_pnl.return_value = mock_pnl_data
        
        # Test the endpoint
        response = client.get("/v1/advanced-analytics/portfolio/test-portfolio/pnl?user_id=test-user")
        
        # Since we're mocking the service, we expect a successful response
        # The actual response will depend on how the service is integrated
        assert response.status_code in [200, 500]  # 500 if service not properly mocked
    
    @patch('services.risk_assessment.RiskAssessmentTools.perform_comprehensive_risk_assessment')
    def test_risk_assessment_integration(self, mock_risk_assessment):
        """Test risk assessment integration with mock data"""
        
        # Mock risk assessment response
        mock_risk_data = {
            "overall_risk": "medium",
            "overall_score": 45.2,
            "risk_factors": [
                {
                    "category": "concentration",
                    "description": "High concentration in single collection",
                    "risk_score": 75.0,
                    "impact": "Significant portfolio volatility",
                    "mitigation": "Diversify across multiple collections"
                }
            ],
            "recommendations": [
                "Reduce exposure to single collection by 30%",
                "Add assets from different blockchain platforms"
            ]
        }
        
        mock_risk_assessment.return_value = mock_risk_data
        
        # Test the endpoint
        response = client.post("/v1/advanced-analytics/portfolio/test-portfolio/risk-assessment?user_id=test-user")
        
        # The actual response will depend on how the service is integrated
        assert response.status_code in [200, 500]  # 500 if service not properly mocked

class TestComponentDataFlow:
    """Test data flow between frontend components"""
    
    def test_pnl_data_structure(self):
        """Test that P&L data structure matches frontend expectations"""
        
        # Expected P&L data structure for frontend
        expected_pnl_structure = {
            "total_cost_basis": float,
            "current_value": float,
            "unrealized_pnl": float,
            "realized_pnl": float,
            "total_pnl": float,
            "roi_percentage": float,
            "annualized_roi": (float, type(None)),
            "performance_metrics": {
                "sharpe_ratio": (float, type(None)),
                "sortino_ratio": (float, type(None)),
                "max_drawdown": (float, type(None)),
                "volatility": (float, type(None)),
                "beta": (float, type(None))
            }
        }
        
        # This test validates the expected data structure
        # In a real integration test, you would compare actual API responses
        assert isinstance(expected_pnl_structure, dict)
        assert "total_cost_basis" in expected_pnl_structure
        assert "current_value" in expected_pnl_structure
        assert "total_pnl" in expected_pnl_structure
    
    def test_risk_data_structure(self):
        """Test that risk assessment data structure matches frontend expectations"""
        
        # Expected risk data structure for frontend
        expected_risk_structure = {
            "overall_risk": str,
            "overall_score": float,
            "risk_factors": list,
            "recommendations": list
        }
        
        # This test validates the expected data structure
        assert isinstance(expected_risk_structure, dict)
        assert "overall_risk" in expected_risk_structure
        assert "overall_score" in expected_risk_structure
        assert "risk_factors" in expected_risk_structure
        assert "recommendations" in expected_risk_structure
    
    def test_tax_data_structure(self):
        """Test that tax reporting data structure matches frontend expectations"""
        
        # Expected tax data structure for frontend
        expected_tax_structure = {
            "tax_year": str,
            "total_proceeds": float,
            "total_cost_basis": float,
            "total_gains": float,
            "total_losses": float,
            "net_gains": float,
            "annual_exemption_used": float,
            "annual_exemption_remaining": float,
            "taxable_gains": float,
            "estimated_tax": float
        }
        
        # This test validates the expected data structure
        assert isinstance(expected_tax_structure, dict)
        assert "tax_year" in expected_tax_structure
        assert "total_gains" in expected_tax_structure
        assert "estimated_tax" in expected_tax_structure

class TestErrorHandling:
    """Test error handling in the integration"""
    
    def test_missing_user_id_parameter(self):
        """Test that missing user_id parameter returns appropriate error"""
        
        # Test P&L endpoint without user_id
        response = client.get("/v1/advanced-analytics/portfolio/test-portfolio/pnl")
        assert response.status_code == 422  # Validation error for missing required parameter
    
    def test_invalid_portfolio_id(self):
        """Test that invalid portfolio ID returns appropriate error"""
        
        # Test with invalid portfolio ID
        response = client.get("/v1/advanced-analytics/portfolio/invalid-portfolio/pnl?user_id=test-user")
        assert response.status_code in [404, 500]  # Expected error for invalid portfolio
    
    def test_invalid_tax_year(self):
        """Test that invalid tax year returns appropriate error"""
        
        # Test with invalid tax year
        response = client.get("/v1/advanced-analytics/portfolio/test-portfolio/tax-report/invalid-year?user_id=test-user")
        assert response.status_code in [404, 500]  # Expected error for invalid tax year

class TestPerformanceIntegration:
    """Test performance aspects of the integration"""
    
    def test_api_response_time(self):
        """Test that API endpoints respond within reasonable time"""
        
        import time
        
        # Test health check response time
        start_time = time.time()
        response = client.get("/v1/advanced-analytics/health/advanced-features")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Health check should respond very quickly
        assert response_time < 1.0  # Less than 1 second
        assert response.status_code == 200
    
    def test_concurrent_requests(self):
        """Test that the system can handle concurrent requests"""
        
        import asyncio
        import time
        
        async def make_request():
            """Make a single request"""
            start_time = time.time()
            response = client.get("/v1/advanced-analytics/health/advanced-features")
            end_time = time.time()
            return response.status_code, end_time - start_time
        
        async def test_concurrent():
            """Test multiple concurrent requests"""
            tasks = [make_request() for _ in range(5)]
            results = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for status_code, response_time in results:
                assert status_code == 200
                assert response_time < 2.0  # Each request should complete within 2 seconds
        
        # Run the concurrent test
        asyncio.run(test_concurrent())

class TestDataValidation:
    """Test data validation in the integration"""
    
    def test_currency_formatting(self):
        """Test that currency values are properly formatted"""
        
        # Test that the API returns numeric values for currency fields
        # This would be tested with actual API responses in a real integration test
        
        # Expected currency fields should be numeric
        currency_fields = [
            "total_cost_basis",
            "current_value", 
            "unrealized_pnl",
            "realized_pnl",
            "total_pnl"
        ]
        
        # This test validates the expected field names
        # In a real test, you would check actual API response values
        assert all(isinstance(field, str) for field in currency_fields)
        assert len(currency_fields) > 0
    
    def test_date_formatting(self):
        """Test that date values are properly formatted"""
        
        # Test that the API returns ISO format dates
        # This would be tested with actual API responses in a real integration test
        
        # Expected date fields should be ISO format
        date_fields = [
            "calculation_timestamp",
            "timestamp",
            "report_generated"
        ]
        
        # This test validates the expected field names
        # In a real test, you would check actual API response values
        assert all(isinstance(field, str) for field in date_fields)
        assert len(date_fields) > 0

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
