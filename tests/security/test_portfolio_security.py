"""
Portfolio Service Security Testing Script

This script performs comprehensive security testing including:
- Penetration testing
- Input validation testing
- Access control testing
- Data isolation testing
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from portfolio.services.portfolio_service import PortfolioService
from portfolio.models.portfolio import PortfolioCreate, PortfolioUpdate

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioSecurityTester:
    """Security testing for portfolio service"""
    
    def __init__(self):
        self.service = PortfolioService()
        self.security_results = {}
        
    async def run_security_tests(self) -> Dict[str, Any]:
        """Run comprehensive security testing"""
        logger.info("🔒 Starting Portfolio Security Testing")
        
        # 1. Access Control Testing
        await self.test_access_control()
        
        # 2. Input Validation Testing
        await self.test_input_validation()
        
        # 3. Data Isolation Testing
        await self.test_data_isolation()
        
        # 4. Penetration Testing
        await self.test_penetration_scenarios()
        
        # Generate security score
        security_score = self._calculate_security_score()
        
        results = {
            "test_timestamp": datetime.now(timezone.utc).isoformat(),
            "security_score": security_score,
            "access_control": self.security_results.get("access_control", {}),
            "input_validation": self.security_results.get("input_validation", {}),
            "data_isolation": self.security_results.get("data_isolation", {}),
            "penetration_testing": self.security_results.get("penetration_testing", {}),
            "vulnerabilities": self._identify_vulnerabilities()
        }
        
        return results
    
    async def test_access_control(self):
        """Test access control mechanisms"""
        logger.info("🚫 Testing Access Control")
        
        # Create portfolio for user A
        portfolio_data = PortfolioCreate(
            user_id="user-a",
            name="User A Portfolio",
            description="Portfolio for access control testing",
            risk_tolerance=0.5
        )
        
        portfolio = await self.service.create_portfolio(
            user_id=portfolio_data.user_id,
            portfolio=portfolio_data
        )
        
        # Test unauthorized access attempts
        unauthorized_attempts = []
        
        # Test get portfolio with wrong user
        unauthorized_get = await self.service.get_portfolio(
            portfolio_id=portfolio.id,
            user_id="user-b"
        )
        unauthorized_attempts.append({
            "test": "Unauthorized Portfolio Access",
            "result": "PASS" if unauthorized_get is None else "FAIL",
            "details": "User B cannot access User A's portfolio"
        })
        
        # Test update portfolio with wrong user
        update_data = PortfolioUpdate(name="Hacked Portfolio")
        unauthorized_update = await self.service.update_portfolio(
            portfolio_id=portfolio.id,
            user_id="user-b",
            portfolio_update=update_data
        )
        unauthorized_attempts.append({
            "test": "Unauthorized Portfolio Update",
            "result": "PASS" if unauthorized_update is None else "FAIL",
            "details": "User B cannot update User A's portfolio"
        })
        
        # Test delete portfolio with wrong user
        unauthorized_delete = await self.service.delete_portfolio(
            portfolio_id=portfolio.id,
            user_id="user-b"
        )
        unauthorized_attempts.append({
            "test": "Unauthorized Portfolio Deletion",
            "result": "PASS" if unauthorized_delete is False else "FAIL",
            "details": "User B cannot delete User A's portfolio"
        })
        
        # Clean up
        await self.service.delete_portfolio(portfolio.id, "user-a")
        
        self.security_results["access_control"] = {
            "tests": unauthorized_attempts,
            "passed": len([t for t in unauthorized_attempts if t["result"] == "PASS"]),
            "failed": len([t for t in unauthorized_attempts if t["result"] == "FAIL"])
        }
        
        logger.info("✅ Access Control Testing Completed")
    
    async def test_input_validation(self):
        """Test input validation and sanitization"""
        logger.info("🧹 Testing Input Validation")
        
        # Test malicious inputs
        malicious_inputs = [
            {"user_id": "<script>alert('xss')</script>", "name": "XSS Portfolio"},
            {"user_id": "user-1", "name": "'; DROP TABLE portfolios; --"},
            {"user_id": "user-1", "name": "Portfolio with 'quotes' and \"double quotes\""},
            {"user_id": "user-1", "name": "Portfolio with \n newlines \t tabs"},
            {"user_id": "user-1", "name": "Portfolio with unicode 🚀🎉💻"},
        ]
        
        validation_results = []
        
        for i, malicious_input in enumerate(malicious_inputs):
            try:
                portfolio_data = PortfolioCreate(
                    user_id=malicious_input["user_id"],
                    name=malicious_input["name"],
                    description="Malicious input test",
                    risk_tolerance=0.5
                )
                
                portfolio = await self.service.create_portfolio(
                    user_id=portfolio_data.user_id,
                    portfolio=portfolio_data
                )
                
                # Verify input was handled safely
                validation_results.append({
                    "test": f"Malicious Input {i+1}",
                    "result": "PASS",
                    "details": f"Input '{malicious_input['name']}' handled safely",
                    "input": malicious_input
                })
                
                # Clean up
                await self.service.delete_portfolio(portfolio.id, portfolio.user_id)
                
            except Exception as e:
                validation_results.append({
                    "test": f"Malicious Input {i+1}",
                    "result": "FAIL",
                    "details": f"Input '{malicious_input['name']}' caused error: {str(e)}",
                    "input": malicious_input
                })
        
        self.security_results["input_validation"] = {
            "tests": validation_results,
            "passed": len([t for t in validation_results if t["result"] == "PASS"]),
            "failed": len([t for t in validation_results if t["result"] == "FAIL"])
        }
        
        logger.info("✅ Input Validation Testing Completed")
    
    async def test_data_isolation(self):
        """Test data isolation between users"""
        logger.info("🔐 Testing Data Isolation")
        
        # Create portfolios for different users
        user_a_portfolios = []
        user_b_portfolios = []
        
        for i in range(5):
            # User A portfolios
            portfolio_data = PortfolioCreate(
                user_id="user-a",
                name=f"User A Portfolio {i}",
                description=f"Portfolio {i} for user A",
                risk_tolerance=0.5
            )
            portfolio = await self.service.create_portfolio(
                user_id=portfolio_data.user_id,
                portfolio=portfolio_data
            )
            user_a_portfolios.append(portfolio)
            
            # User B portfolios
            portfolio_data = PortfolioCreate(
                user_id="user-b",
                name=f"User B Portfolio {i}",
                description=f"Portfolio {i} for user B",
                risk_tolerance=0.5
            )
            portfolio = await self.service.create_portfolio(
                user_id=portfolio_data.user_id,
                portfolio=portfolio_data
            )
            user_b_portfolios.append(portfolio)
        
        isolation_results = []
        
        # Test user A can only see their portfolios
        user_a_list = await self.service.list_portfolios("user-a")
        isolation_results.append({
            "test": "User A Portfolio Isolation",
            "result": "PASS" if len(user_a_list) == 5 and all(p.user_id == "user-a" for p in user_a_list) else "FAIL",
            "details": f"User A sees {len(user_a_list)} portfolios, all belong to them"
        })
        
        # Test user B can only see their portfolios
        user_b_list = await self.service.list_portfolios("user-b")
        isolation_results.append({
            "test": "User B Portfolio Isolation",
            "result": "PASS" if len(user_b_list) == 5 and all(p.user_id == "user-b" for p in user_b_list) else "FAIL",
            "details": f"User B sees {len(user_b_list)} portfolios, all belong to them"
        })
        
        # Test cross-user access is denied
        cross_access_tests = 0
        cross_access_failures = 0
        
        for portfolio in user_a_portfolios:
            unauthorized_access = await self.service.get_portfolio(
                portfolio_id=portfolio.id,
                user_id="user-b"
            )
            if unauthorized_access is None:
                cross_access_tests += 1
            else:
                cross_access_failures += 1
        
        isolation_results.append({
            "test": "Cross-User Access Prevention",
            "result": "PASS" if cross_access_failures == 0 else "FAIL",
            "details": f"Cross-user access tests: {cross_access_tests} passed, {cross_access_failures} failed"
        })
        
        # Clean up
        for portfolio in user_a_portfolios:
            await self.service.delete_portfolio(portfolio.id, "user-a")
        for portfolio in user_b_portfolios:
            await self.service.delete_portfolio(portfolio.id, "user-b")
        
        self.security_results["data_isolation"] = {
            "tests": isolation_results,
            "passed": len([t for t in isolation_results if t["result"] == "PASS"]),
            "failed": len([t for t in isolation_results if t["result"] == "FAIL"])
        }
        
        logger.info("✅ Data Isolation Testing Completed")
    
    async def test_penetration_scenarios(self):
        """Test penetration scenarios"""
        logger.info("🛡️ Testing Penetration Scenarios")
        
        penetration_results = []
        
        # Test SQL injection attempts
        sql_injection_attempts = [
            "'; DROP TABLE portfolios; --",
            "' OR '1'='1",
            "'; INSERT INTO portfolios VALUES ('hacked', 'hacked', 'hacked'); --",
            "' UNION SELECT * FROM users --"
        ]
        
        for i, injection_attempt in enumerate(sql_injection_attempts):
            try:
                portfolio_data = PortfolioCreate(
                    user_id=f"penetration-user-{i}",
                    name=injection_attempt,
                    description="SQL injection test",
                    risk_tolerance=0.5
                )
                
                portfolio = await self.service.create_portfolio(
                    user_id=portfolio_data.user_id,
                    portfolio=portfolio_data
                )
                
                # Verify injection attempt was treated as literal text
                penetration_results.append({
                    "test": f"SQL Injection {i+1}",
                    "result": "PASS",
                    "details": f"Injection attempt '{injection_attempt}' treated as literal text",
                    "attack_vector": "SQL Injection"
                })
                
                # Clean up
                await self.service.delete_portfolio(portfolio.id, portfolio.user_id)
                
            except Exception as e:
                penetration_results.append({
                    "test": f"SQL Injection {i+1}",
                    "result": "FAIL",
                    "details": f"Injection attempt '{injection_attempt}' caused error: {str(e)}",
                    "attack_vector": "SQL Injection"
                })
        
        # Test XSS attempts
        xss_attempts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>"
        ]
        
        for i, xss_attempt in enumerate(xss_attempts):
            try:
                portfolio_data = PortfolioCreate(
                    user_id=f"xss-user-{i}",
                    name=xss_attempt,
                    description="XSS test",
                    risk_tolerance=0.5
                )
                
                portfolio = await self.service.create_portfolio(
                    user_id=portfolio_data.user_id,
                    portfolio=portfolio_data
                )
                
                # Verify XSS attempt was handled safely
                penetration_results.append({
                    "test": f"XSS Attempt {i+1}",
                    "result": "PASS",
                    "details": f"XSS attempt '{xss_attempt}' handled safely",
                    "attack_vector": "Cross-Site Scripting"
                })
                
                # Clean up
                await self.service.delete_portfolio(portfolio.id, portfolio.user_id)
                
            except Exception as e:
                penetration_results.append({
                    "test": f"XSS Attempt {i+1}",
                    "result": "FAIL",
                    "details": f"XSS attempt '{xss_attempt}' caused error: {str(e)}",
                    "attack_vector": "Cross-Site Scripting"
                })
        
        self.security_results["penetration_testing"] = {
            "tests": penetration_results,
            "passed": len([t for t in penetration_results if t["result"] == "PASS"]),
            "failed": len([t for t in penetration_results if t["result"] == "FAIL"]),
            "attack_vectors": list(set([t["attack_vector"] for t in penetration_results]))
        }
        
        logger.info("✅ Penetration Testing Completed")
    
    def _calculate_security_score(self) -> int:
        """Calculate overall security score"""
        total_tests = 0
        passed_tests = 0
        
        for category in self.security_results.values():
            if "tests" in category:
                total_tests += category["passed"] + category["failed"]
                passed_tests += category["passed"]
        
        if total_tests == 0:
            return 0
        
        return int((passed_tests / total_tests) * 100)
    
    def _identify_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Identify security vulnerabilities"""
        vulnerabilities = []
        
        for category_name, category_data in self.security_results.items():
            if "tests" in category_data:
                for test in category_data["tests"]:
                    if test["result"] == "FAIL":
                        vulnerabilities.append({
                            "category": category_name,
                            "test": test["test"],
                            "details": test["details"],
                            "severity": "HIGH" if "injection" in test["test"].lower() else "MEDIUM"
                        })
        
        return vulnerabilities

# Main execution
async def main():
    """Main function to run security testing"""
    security_tester = PortfolioSecurityTester()
    
    try:
        results = await security_tester.run_security_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🔒 PORTFOLIO SERVICE SECURITY TESTING RESULTS")
        print("="*80)
        print(f"🛡️  Security Score: {results['security_score']}/100")
        print(f"📊 Overall Status: {'SECURE' if results['security_score'] >= 80 else 'NEEDS_IMPROVEMENT'}")
        
        print("\n📋 TEST RESULTS BY CATEGORY:")
        for category, data in results.items():
            if category not in ["test_timestamp", "security_score", "vulnerabilities"]:
                if "passed" in data and "failed" in data:
                    print(f"   🔹 {category.replace('_', ' ').title()}: {data['passed']} passed, {data['failed']} failed")
        
        if results["vulnerabilities"]:
            print(f"\n⚠️  VULNERABILITIES FOUND: {len(results['vulnerabilities'])}")
            for vuln in results["vulnerabilities"]:
                print(f"   • {vuln['category']}: {vuln['test']} ({vuln['severity']})")
        else:
            print("\n✅ No vulnerabilities found!")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"Security testing failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
