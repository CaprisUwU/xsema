"""
Test script for caching and rate limiting implementation.

This script tests:
1. Caching behavior (hits/misses)
2. Rate limiting enforcement
3. Error handling and timeouts
"""
import asyncio
import time
import logging
from typing import List, Dict, Any
import aiohttp
from web3 import Web3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the blockchain service
from services.blockchain import BlockchainService, BlockchainServiceError, RateLimitExceeded
from utils.cache import cache_config

# Test configuration
TEST_WALLET = "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"  # Test wallet (Vitalik's)
TEST_CONTRACT = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"  # BAYC contract
TEST_TOKEN_ID = "1"

async def test_caching():
    """Test that caching is working correctly."""
    logger.info("=== Testing Caching ===")
    
    # Create a new blockchain service instance
    blockchain = BlockchainService()
    
    try:
        # First call (should be a cache miss)
        start_time = time.time()
        nfts1 = await blockchain.get_wallet_nfts(
            wallet_address=TEST_WALLET,
            page_size=5
        )
        duration1 = time.time() - start_time
        logger.info(f"First call (cache miss) took {duration1:.2f}s")
        
        # Second call (should be a cache hit)
        start_time = time.time()
        nfts2 = await blockchain.get_wallet_nfts(
            wallet_address=TEST_WALLET,
            page_size=5
        )
        duration2 = time.time() - start_time
        logger.info(f"Second call (cache hit) took {duration2:.2f}s")
        
        # Verify cache was faster
        assert duration2 < duration1, "Cache hit should be faster than cache miss"
        
        # Verify same data was returned
        assert nfts1 == nfts2, "Cached data should match original data"
        
        logger.info("✅ Caching test passed")
        return True
        
    except Exception as e:
        logger.error(f"Caching test failed: {str(e)}", exc_info=True)
        return False
    finally:
        await blockchain.close()

async def test_rate_limiting():
    """Test that rate limiting is working correctly."""
    logger.info("\n=== Testing Rate Limiting ===")
    
    # Create a new blockchain service instance
    blockchain = BlockchainService()
    
    try:
        # Make requests until we hit the rate limit
        requests = []
        rate_limit_hit = False
        
        for i in range(1, 40):  # Should hit the 30 req/min limit
            try:
                start_time = time.time()
                nfts = await blockchain.get_wallet_nfts(
                    wallet_address=TEST_WALLET,
                    page_size=5,
                    request=type('Request', (), {'client': type('Client', (), {'host': 'test'})})()
                )
                duration = time.time() - start_time
                requests.append({
                    'request': i,
                    'status': 'success',
                    'duration': duration
                })
                logger.info(f"Request {i}: Success ({duration:.2f}s)")
                
                # Small delay between requests
                await asyncio.sleep(0.1)
                
            except RateLimitExceeded as e:
                rate_limit_hit = True
                logger.info(f"✅ Rate limit hit at request {i} (expected)")
                logger.info(f"Rate limit details: {str(e)}")
                break
                
            except Exception as e:
                logger.error(f"Unexpected error on request {i}: {str(e)}")
                return False
        
        # Verify rate limit was hit
        assert rate_limit_hit, "Expected to hit rate limit but didn't"
        
        # Log request statistics
        if requests:
            avg_duration = sum(r['duration'] for r in requests) / len(requests)
            logger.info(f"Made {len(requests)} requests with avg duration {avg_duration:.2f}s")
        
        logger.info("✅ Rate limiting test passed")
        return True
        
    except Exception as e:
        logger.error(f"Rate limiting test failed: {str(e)}", exc_info=True)
        return False
    finally:
        await blockchain.close()

async def test_error_handling():
    """Test error handling and timeouts."""
    logger.info("\n=== Testing Error Handling ===")
    
    # Create a new blockchain service instance
    blockchain = BlockchainService()
    
    tests_passed = 0
    
    try:
        # Test 1: Invalid wallet address
        try:
            await blockchain.get_wallet_nfts(
                wallet_address="invalid-address",
                page_size=5
            )
            logger.error("❌ Expected error for invalid wallet address")
        except BlockchainServiceError as e:
            logger.info(f"✅ Got expected error for invalid wallet: {str(e)}")
            tests_passed += 1
        
        # Test 2: Invalid contract address
        try:
            await blockchain.get_token_metadata(
                contract_address="0xinvalid",
                token_id=TEST_TOKEN_ID
            )
            logger.error("❌ Expected error for invalid contract address")
        except BlockchainServiceError as e:
            logger.info(f"✅ Got expected error for invalid contract: {str(e)}")
            tests_passed += 1
        
        # Test 3: Non-existent token (should still return 200 but with empty data)
        try:
            result = await blockchain.get_token_metadata(
                contract_address=TEST_CONTRACT,
                token_id="999999999999999999999999"
            )
            logger.info(f"✅ Got response for non-existent token: {result}")
            tests_passed += 1
        except Exception as e:
            logger.error(f"Unexpected error for non-existent token: {str(e)}")
        
        return tests_passed == 3
        
    except Exception as e:
        logger.error(f"Error handling test failed: {str(e)}", exc_info=True)
        return False
    finally:
        await blockchain.close()

async def main():
    """Run all tests."""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    if not os.getenv("ALCHEMY_API_KEY"):
        logger.error("ALCHEMY_API_KEY environment variable not set")
        return
    
    # Enable debug logging for tests
    logging.getLogger().setLevel(logging.DEBUG)
    
    # Run tests
    results = {
        'caching': await test_caching(),
        'rate_limiting': await test_rate_limiting(),
        'error_handling': await test_error_handling()
    }
    
    # Print summary
    print("\n=== Test Summary ===")
    for test, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test.upper()}: {status}")
    
    if all(results.values()):
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main())
