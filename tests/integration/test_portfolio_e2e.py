"""
End-to-End Tests for Portfolio Service
"""
import asyncio
import time
import statistics
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging

from portfolio.services.portfolio_service import PortfolioService
from portfolio.models.portfolio import PortfolioCreate, PortfolioUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioE2ETestSuite:
    def __init__(self):
        self.service = PortfolioService()
        self.test_results = []
        self.performance_metrics = {}
        
    async def run_full_test_suite(self) -> Dict[str, Any]:
        logger.info("🚀 Starting Portfolio Service E2E Test Suite")
        
        start_time = time.time()
        
        # 1. CRUD Operations Testing
        await self.test_crud_operations()
        
        # 2. Performance Benchmarking
        await self.test_performance_benchmarks()
        
        # 3. Security Testing
        await self.test_security_scenarios()
        
        total_time = time.time() - start_time
        
        results = {
            "total_tests": len(self.test_results),
            "passed": len([r for r in self.test_results if r["status"] == "PASS"]),
            "failed": len([r for r in self.test_results if r["status"] == "FAIL"]),
            "total_time": total_time,
            "performance_metrics": self.performance_metrics,
            "test_details": self.test_results
        }
        
        logger.info(f"✅ E2E Test Suite Completed: {results['passed']}/{results['total_tests']} tests passed")
        return results

    async def test_crud_operations(self):
        logger.info("📝 Testing CRUD Operations")
        
        # Test 1: Create Portfolio
        test_result = await self._test_create_portfolio()
        self.test_results.append(test_result)
        
        # Test 2: Read Portfolio
        if test_result["status"] == "PASS":
            portfolio_id = test_result["data"]["portfolio_id"]
            test_result = await self._test_read_portfolio(portfolio_id)
            self.test_results.append(test_result)
            
            # Test 3: Update Portfolio
            if test_result["status"] == "PASS":
                test_result = await self._test_update_portfolio(portfolio_id)
                self.test_results.append(test_result)
                
                # Test 4: Delete Portfolio
                if test_result["status"] == "PASS":
                    test_result = await self._test_delete_portfolio(portfolio_id)
                    self.test_results.append(test_result)
    
    async def _test_create_portfolio(self) -> Dict[str, Any]:
        try:
            start_time = time.time()
            
            portfolio_data = PortfolioCreate(
                user_id="test-user-e2e",
                name="E2E Test Portfolio",
                description="Portfolio for end-to-end testing",
                risk_tolerance=0.7
            )
            
            portfolio = await self.service.create_portfolio(
                user_id=portfolio_data.user_id,
                portfolio=portfolio_data
            )
            
            execution_time = time.time() - start_time
            
            assert portfolio is not None
            assert portfolio.name == portfolio_data.name
            assert portfolio.user_id == portfolio_data.user_id
            
            return {
                "test": "Create Portfolio",
                "status": "PASS",
                "execution_time": execution_time,
                "data": {
                    "portfolio_id": portfolio.id,
                    "user_id": portfolio.user_id
                }
            }
            
        except Exception as e:
            return {
                "test": "Create Portfolio",
                "status": "FAIL",
                "error": str(e),
                "execution_time": 0
            }
    
    async def _test_read_portfolio(self, portfolio_id: str) -> Dict[str, Any]:
        try:
            start_time = time.time()
            
            portfolio = await self.service.get_portfolio(
                portfolio_id=portfolio_id,
                user_id="test-user-e2e"
            )
            
            execution_time = time.time() - start_time
            
            assert portfolio is not None
            assert portfolio.id == portfolio_id
            
            return {
                "test": "Read Portfolio",
                "status": "PASS",
                "execution_time": execution_time,
                "data": {"portfolio_id": portfolio_id}
            }
            
        except Exception as e:
            return {
                "test": "Read Portfolio",
                "status": "FAIL",
                "error": str(e),
                "execution_time": 0
            }
    
    async def _test_update_portfolio(self, portfolio_id: str) -> Dict[str, Any]:
        try:
            start_time = time.time()
            
            update_data = PortfolioUpdate(
                name="Updated E2E Portfolio",
                description="Updated description for E2E testing",
                risk_tolerance=0.8
            )
            
            updated_portfolio = await self.service.update_portfolio(
                portfolio_id=portfolio_id,
                user_id="test-user-e2e",
                portfolio_update=update_data
            )
            
            execution_time = time.time() - start_time
            
            assert updated_portfolio is not None
            assert updated_portfolio.name == update_data.name
            assert updated_portfolio.description == update_data.description
            
            return {
                "test": "Update Portfolio",
                "status": "PASS",
                "execution_time": execution_time,
                "data": {"portfolio_id": portfolio_id}
            }
            
        except Exception as e:
            return {
                "test": "Update Portfolio",
                "status": "FAIL",
                "error": str(e),
                "execution_time": 0
            }
    
    async def _test_delete_portfolio(self, portfolio_id: str) -> Dict[str, Any]:
        try:
            start_time = time.time()
            
            delete_result = await self.service.delete_portfolio(
                portfolio_id=portfolio_id,
                user_id="test-user-e2e"
            )
            
            execution_time = time.time() - start_time
            
            assert delete_result is True
            
            deleted_portfolio = await self.service.get_portfolio(
                portfolio_id=portfolio_id,
                user_id="test-user-e2e"
            )
            assert deleted_portfolio is None
            
            return {
                "test": "Delete Portfolio",
                "status": "PASS",
                "execution_time": execution_time,
                "data": {"portfolio_id": portfolio_id}
            }
            
        except Exception as e:
            return {
                "test": "Delete Portfolio",
                "status": "FAIL",
                "error": str(e),
                "execution_time": 0
            }

    async def test_performance_benchmarks(self):
        logger.info("⚡ Testing Performance Benchmarks")
        await self._benchmark_portfolio_creation()
    
    async def _benchmark_portfolio_creation(self):
        logger.info("📊 Benchmarking Portfolio Creation")
        
        execution_times = []
        num_portfolios = 50
        
        for i in range(num_portfolios):
            start_time = time.time()
            
            portfolio_data = PortfolioCreate(
                user_id=f"benchmark-user-{i}",
                name=f"Benchmark Portfolio {i}",
                description=f"Portfolio {i} for performance testing",
                risk_tolerance=0.5
            )
            
            await self.service.create_portfolio(
                user_id=portfolio_data.user_id,
                portfolio=portfolio_data
            )
            
            execution_time = time.time() - start_time
            execution_times.append(execution_time)
        
        avg_time = statistics.mean(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        self.performance_metrics["portfolio_creation"] = {
            "num_operations": num_portfolios,
            "avg_time_ms": avg_time * 1000,
            "min_time_ms": min_time * 1000,
            "max_time_ms": max_time * 1000,
            "throughput_ops_per_sec": num_portfolios / sum(execution_times)
        }
        
        logger.info(f"✅ Portfolio Creation Benchmark: Avg {avg_time*1000:.2f}ms, Throughput {self.performance_metrics['portfolio_creation']['throughput_ops_per_sec']:.2f} ops/sec")
        
        # Clean up
        for i in range(num_portfolios):
            try:
                portfolios = await self.service.list_portfolios(f"benchmark-user-{i}", limit=10)
                for portfolio in portfolios:
                    await self.service.delete_portfolio(portfolio.id, f"benchmark-user-{i}")
            except:
                pass

    async def test_security_scenarios(self):
        logger.info("🔒 Testing Security Scenarios")
        await self._test_unauthorized_access()
        await self._test_data_isolation()
    
    async def _test_unauthorized_access(self):
        logger.info("🚫 Testing Unauthorized Access")
        
        portfolio_data = PortfolioCreate(
            user_id="user-a",
            name="User A Portfolio",
            description="Portfolio for user A",
            risk_tolerance=0.5
        )
        
        portfolio = await self.service.create_portfolio(
            user_id=portfolio_data.user_id,
            portfolio=portfolio_data
        )
        
        unauthorized_portfolio = await self.service.get_portfolio(
            portfolio_id=portfolio.id,
            user_id="user-b"
        )
        
        assert unauthorized_portfolio is None
        
        await self.service.delete_portfolio(portfolio.id, "user-a")
        logger.info("✅ Unauthorized Access Prevention: All tests passed")
    
    async def _test_data_isolation(self):
        logger.info("🔐 Testing Data Isolation")
        
        user_a_portfolios = []
        user_b_portfolios = []
        
        for i in range(3):
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
        
        user_a_list = await self.service.list_portfolios("user-a")
        assert len(user_a_list) == 3
        for portfolio in user_a_list:
            assert portfolio.user_id == "user-a"
        
        user_b_list = await self.service.list_portfolios("user-b")
        assert len(user_b_list) == 3
        for portfolio in user_b_list:
            assert portfolio.user_id == "user-b"
        
        for portfolio in user_a_portfolios:
            await self.service.delete_portfolio(portfolio.id, "user-a")
        for portfolio in user_b_portfolios:
            await self.service.delete_portfolio(portfolio.id, "user-b")
        
        logger.info("✅ Data Isolation: All tests passed")

async def run_portfolio_e2e_tests():
    test_suite = PortfolioE2ETestSuite()
    results = await test_suite.run_full_test_suite()
    
    print("\n" + "="*80)
    print("🎯 PORTFOLIO SERVICE E2E TEST SUITE RESULTS")
    print("="*80)
    print(f"📊 Total Tests: {results['total_tests']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"⏱️  Total Time: {results['total_time']:.2f}s")
    
    print("\n📈 PERFORMANCE METRICS:")
    for metric_name, metrics in results['performance_metrics'].items():
        print(f"\n🔹 {metric_name.replace('_', ' ').title()}:")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
    
    print("\n📋 TEST DETAILS:")
    for test in results['test_details']:
        status_icon = "✅" if test['status'] == 'PASS' else "❌"
        print(f"   {status_icon} {test['test']}: {test['status']}")
        if test['status'] == 'FAIL':
            print(f"      Error: {test['error']}")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    asyncio.run(run_portfolio_e2e_tests())
