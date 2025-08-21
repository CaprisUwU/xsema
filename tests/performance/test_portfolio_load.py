"""
Portfolio Service Load Testing Script

This script performs comprehensive load testing on the portfolio service including:
- Stress testing with high concurrent users
- Performance profiling and bottleneck identification
"""
import asyncio
import time
import statistics
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
import random

from portfolio.services.portfolio_service import PortfolioService
from portfolio.models.portfolio import PortfolioCreate, PortfolioUpdate

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioLoadTester:
    """Load testing for portfolio service"""
    
    def __init__(self):
        self.service = PortfolioService()
        self.test_results = {}
        
    async def run_load_tests(self) -> Dict[str, Any]:
        """Run comprehensive load testing"""
        logger.info("🚀 Starting Portfolio Load Testing")
        
        start_time = time.time()
        
        # 1. Stress Testing
        await self.stress_test()
        
        # 2. Performance Profiling
        await self.performance_profiling()
        
        total_time = time.time() - start_time
        
        results = {
            "test_duration": total_time,
            "test_timestamp": datetime.now(timezone.utc).isoformat(),
            "stress_test": self.test_results.get("stress_test", {}),
            "performance_profiling": self.test_results.get("performance_profiling", {}),
            "summary": self._generate_summary()
        }
        
        # Save results
        self._save_results(results)
        
        return results
    
    async def stress_test(self):
        """Stress testing with increasing load"""
        logger.info("🏋️ Starting Stress Testing")
        
        test_scenarios = [
            {"concurrent_users": 10, "duration": 30},
            {"concurrent_users": 25, "duration": 30},
            {"concurrent_users": 50, "duration": 30},
            {"concurrent_users": 100, "duration": 30}
        ]
        
        stress_results = []
        
        for scenario in test_scenarios:
            logger.info(f"Testing {scenario['concurrent_users']} concurrent users")
            
            try:
                result = await self._run_stress_scenario(scenario)
                stress_results.append(result)
                
            except Exception as e:
                logger.error(f"Stress test failed: {str(e)}")
                break
        
        self.test_results["stress_test"] = {
            "scenarios": stress_results,
            "max_concurrent_users": max([r["concurrent_users"] for r in stress_results]) if stress_results else 0
        }
        
        logger.info("✅ Stress Testing Completed")
    
    async def _run_stress_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single stress test scenario"""
        concurrent_users = scenario["concurrent_users"]
        duration = scenario["duration"]
        
        start_time = time.time()
        end_time = start_time + duration
        
        # Create user tasks
        user_tasks = []
        for user_id in range(concurrent_users):
            task = self._simulate_user_workload(f"stress-user-{user_id}", end_time)
            user_tasks.append(task)
        
        # Run all user tasks concurrently
        results = await asyncio.gather(*user_tasks, return_exceptions=True)
        
        # Analyze results
        successful_operations = len([r for r in results if not isinstance(r, Exception)])
        failed_operations = len([r for r in results if isinstance(r, Exception)])
        total_operations = len(results)
        
        # Calculate metrics
        error_rate = (failed_operations / total_operations) * 100 if total_operations > 0 else 0
        throughput = successful_operations / duration
        
        return {
            "concurrent_users": concurrent_users,
            "duration": duration,
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "error_rate": error_rate,
            "throughput_ops_per_sec": throughput
        }
    
    async def _simulate_user_workload(self, user_id: str, end_time: float) -> Dict[str, Any]:
        """Simulate user workload"""
        operations = []
        
        while time.time() < end_time:
            operation_start = time.time()
            
            try:
                # Create portfolio
                portfolio_data = PortfolioCreate(
                    user_id=user_id,
                    name=f"Portfolio {random.randint(1, 1000)}",
                    description=f"Test portfolio {random.randint(1, 1000)}",
                    risk_tolerance=random.uniform(0.1, 1.0)
                )
                
                portfolio = await self.service.create_portfolio(
                    user_id=user_id,
                    portfolio=portfolio_data
                )
                
                operations.append({
                    "type": "create",
                    "success": True,
                    "response_time": time.time() - operation_start
                })
                
                # Random delay
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
            except Exception as e:
                operations.append({
                    "type": "create",
                    "success": False,
                    "response_time": time.time() - operation_start,
                    "error": str(e)
                })
        
        return {
            "user_id": user_id,
            "total_operations": len(operations),
            "successful_operations": len([op for op in operations if op["success"]]),
            "failed_operations": len([op for op in operations if not op["success"]])
        }
    
    async def performance_profiling(self):
        """Performance profiling"""
        logger.info("🔍 Starting Performance Profiling")
        
        # Profile portfolio creation
        creation_times = []
        for i in range(100):
            start_time = time.time()
            portfolio_data = PortfolioCreate(
                user_id=f"profile-user-{i}",
                name=f"Profile Portfolio {i}",
                description=f"Portfolio {i} for profiling",
                risk_tolerance=0.5
            )
            
            portfolio = await self.service.create_portfolio(
                user_id=portfolio_data.user_id,
                portfolio=portfolio_data
            )
            
            creation_time = time.time() - start_time
            creation_times.append(creation_time)
        
        operation_profiles = {
            "portfolio_creation": {
                "count": len(creation_times),
                "min_time": min(creation_times),
                "max_time": max(creation_times),
                "mean_time": statistics.mean(creation_times),
                "median_time": statistics.median(creation_times),
                "p95_time": statistics.quantiles(creation_times, n=20)[18]
            }
        }
        
        # Clean up
        for i in range(100):
            try:
                portfolios = await self.service.list_portfolios(f"profile-user-{i}", limit=10)
                for portfolio in portfolios:
                    await self.service.delete_portfolio(portfolio.id, f"profile-user-{i}")
            except:
                pass
        
        self.test_results["performance_profiling"] = {
            "operation_profiles": operation_profiles
        }
        
        logger.info("✅ Performance Profiling Completed")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        summary = {
            "overall_status": "PASS",
            "performance_score": 0
        }
        
        if "stress_test" in self.test_results:
            stress = self.test_results["stress_test"]
            max_users = stress["max_concurrent_users"]
            if max_users >= 100:
                summary["performance_score"] = 100
            elif max_users >= 50:
                summary["performance_score"] = 80
            elif max_users >= 25:
                summary["performance_score"] = 60
            else:
                summary["performance_score"] = 40
        
        return summary
    
    def _save_results(self, results: Dict[str, Any]):
        """Save test results to file"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"portfolio_load_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Test results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save test results: {str(e)}")

# Main execution
async def main():
    """Main function to run load testing"""
    load_tester = PortfolioLoadTester()
    
    try:
        results = await load_tester.run_load_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 PORTFOLIO SERVICE LOAD TESTING RESULTS")
        print("="*80)
        print(f"⏱️  Test Duration: {results['test_duration']:.2f}s")
        print(f"📊 Overall Status: {results['summary']['overall_status']}")
        print(f"🚀 Performance Score: {results['summary']['performance_score']}/100")
        
        if "stress_test" in results:
            stress = results["stress_test"]
            print(f"🏋️  Max Concurrent Users: {stress['max_concurrent_users']}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"Load testing failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
