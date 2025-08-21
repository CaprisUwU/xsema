"""
Test script to verify Web3 connection and middleware injection.

This script tests connectivity to various Ethereum-compatible networks
using public RPC endpoints and verifies Web3.py functionality.
"""
import sys
import time
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.exceptions import Web3Exception

# Configure logging for better output handling
import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def safe_print(message, level='info'):
    """Print function that handles encoding issues and logs messages"""
    try:
        # Remove any non-ASCII characters to prevent encoding issues
        if isinstance(message, str):
            message = ''.join(c if ord(c) < 128 else '' for c in message)
        
        # Log the message
        if level.lower() == 'error':
            logger.error(message)
        elif level.lower() == 'warning':
            logger.warning(message)
        elif level.lower() == 'debug':
            logger.debug(message)
        else:
            logger.info(message)
            
        # Also print to console with basic formatting
        print(f"[{level.upper()}] {message}")
        
    except Exception as e:
        # If all else fails, use basic print
        print(f"[PRINT_ERROR] Failed to log message: {e}")

def safe_print(message, level='info', **kwargs):
    """Print function that handles encoding issues and logs messages with different levels.
    
    Args:
        message (str): The message to print
        level (str): Log level - 'debug', 'info', 'warning', or 'error'
        **kwargs: Additional keyword arguments to pass to print()
    """
    try:
        # Ensure message is a string
        if not isinstance(message, str):
            message = str(message)
        
        # Create a clean version of the message for logging
        clean_message = message
        
        # Add level prefix if not already present
        if not clean_message.strip().startswith('['):
            level_prefix = f'[{level.upper()}] '
            clean_message = level_prefix + clean_message
        
        # Try to print with default encoding first
        try:
            print(clean_message, **kwargs)
            return
        except UnicodeEncodeError:
            # If that fails, try with ASCII-only characters
            ascii_message = clean_message.encode('ascii', 'ignore').decode('ascii')
            print(ascii_message, **kwargs)
            
    except Exception as e:
        # If all else fails, use the most basic print possible
        try:
            print(f"[PRINT_ERROR] {str(e)[:100]}")
            print(str(message)[:200])  # Print original message, truncated
        except:
            print("[CRITICAL] Failed to print message")

def test_connection(rpc_url, chain_name="Ethereum", max_retries=2, retry_delay=1):
    """Test connection to an Ethereum-compatible network with retry logic.
    
    Args:
        rpc_url (str): The RPC URL to test
        chain_name (str): Human-readable name of the chain
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        tuple: (success: bool, message: str, details: dict)
    """
    result = {
        'success': False,
        'chain': chain_name,
        'rpc_url': rpc_url,
        'connection_time': 0,
        'block_number': None,
        'block_details': {},
        'middleware_injected': False,
        'balance_check': None,
        'error': None,
        'warnings': []
    }
    
    for attempt in range(max_retries + 1):
        try:
            # Initialize Web3 with timeout
            w3 = Web3(Web3.HTTPProvider(
                rpc_url,
                request_kwargs={
                    'timeout': 15,  # Increased timeout
                    'proxies': None  # Explicitly disable proxies if not needed
                }
            ))
            
            # Test connection
            start_time = time.time()
            is_connected = w3.is_connected()
            connection_time = time.time() - start_time
            result['connection_time'] = connection_time
            
            if not is_connected:
                raise ConnectionError("Failed to connect to the RPC endpoint")
            
            # Connection successful, proceed with tests
            result['success'] = True
            
            # Get current block number
            result['block_number'] = w3.eth.block_number
            
            # Get block details
            try:
                block = w3.eth.get_block('latest')
                result['block_details'] = {
                    'hash': block['hash'].hex(),
                    'timestamp': block['timestamp'],
                    'transaction_count': len(block.get('transactions', [])),
                    'gas_used': block.get('gasUsed', 'N/A'),
                    'gas_limit': block.get('gasLimit', 'N/A')
                }
            except Exception as e:
                result['warnings'].append(f"Could not get block details: {str(e)}")
            
            # Test middleware injection
            try:
                from web3.middleware import ExtraDataToPOAMiddleware
                w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
                result['middleware_injected'] = True
                
                # Test balance check
                try:
                    vitalik_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                    balance_wei = w3.eth.get_balance(vitalik_address)
                    result['balance_check'] = {
                        'address': vitalik_address,
                        'balance_wei': balance_wei,
                        'balance_eth': float(w3.from_wei(balance_wei, 'ether'))
                    }
                except Exception as e:
                    result['warnings'].append(f"Balance check failed: {str(e)}")
                    
            except Exception as e:
                result['warnings'].append(f"Middleware injection failed: {str(e)}")
            
            # If we got here, all tests passed
            return True, "Connection and tests completed successfully", result
            
        except Exception as e:
            result['error'] = str(e)
            if attempt < max_retries:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            
            return False, f"Failed after {max_retries + 1} attempts: {str(e)}", result
    
    return False, "Unexpected error in test_connection", result

def format_connection_result(success, message, details):
    """Format the connection test results into a human-readable string."""
    output = [f"\n{'='*80}"]
    output.append(f"[TEST] {details['chain']}")
    output.append(f"[URL] {details['rpc_url']}")
    output.append(f"[STATUS] {'✅ SUCCESS' if success else '❌ FAILED'}")
    output.append(f"[TIME] {details.get('connection_time', 0):.2f}s")
    
    if not success:
        output.append(f"[ERROR] {message}")
        return "\n".join(output)
    
    # Add successful test details
    output.append(f"[BLOCK] #{details.get('block_number', 'N/A')}")
    
    if details.get('block_details'):
        bd = details['block_details']
        output.append(f"[LATEST BLOCK] {bd.get('hash', 'N/A')}")
        output.append(f"[TIMESTAMP] {bd.get('timestamp', 'N/A')}")
        output.append(f"[TX COUNT] {bd.get('transaction_count', 'N/A')}")
    
    output.append(f"[MIDDLEWARE] {'✅ Injected' if details.get('middleware_injected') else '❌ Failed'}")
    
    if details.get('balance_check'):
        bal = details['balance_check']
        output.append(f"[BALANCE] {bal['balance_eth']:.4f} ETH ({bal['balance_wei']} wei)")
    
    # Add any warnings
    for warning in details.get('warnings', []):
        output.append(f"[WARNING] {warning}")
    
    output.append(f"\n{message}")
    output.append("="*80)
    return "\n".join(output)

def main():
    """Main function to test Web3 connections to various networks."""
    safe_print("🌐 Web3 Connection Tester")
    safe_print("=" * 80)
    safe_print("Testing connectivity to various Ethereum-compatible networks...")
    
    # List of RPC endpoints to test with various providers
    endpoints = [
        # Ethereum Mainnet
        {
            "name": "Ethereum Mainnet (Infura)",
            "url": "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
        },
        {
            "name": "Ethereum Mainnet (Ankr)",
            "url": "https://rpc.ankr.com/eth"
        },
        {
            "name": "Ethereum Mainnet (Cloudflare)",
            "url": "https://cloudflare-eth.com"
        },
        # Polygon
        {
            "name": "Polygon Mainnet (Public RPC)",
            "url": "https://polygon-rpc.com"
        },
        {
            "name": "Polygon Mainnet (Ankr)",
            "url": "https://rpc.ankr.com/polygon"
        },
        # Binance Smart Chain
        {
            "name": "Binance Smart Chain (Public RPC)",
            "url": "https://bsc-dataseed.binance.org/"
        },
        # Avalanche
        {
            "name": "Avalanche C-Chain (Public RPC)",
            "url": "https://api.avax.network/ext/bc/C/rpc"
        },
        # Fantom
        {
            "name": "Fantom Opera (Public RPC)",
            "url": "https://rpc.ftm.tools/"
        }
    ]
    
    safe_print(f"\nTesting {len(endpoints)} different RPC endpoints...")
    safe_print("-" * 80)
    
    successful_tests = 0
    test_results = []
    
    for i, endpoint in enumerate(endpoints, 1):
        safe_print(f"\nTest {i}/{len(endpoints)}: {endpoint['name']}")
        safe_print("-" * 40)
        
        start_time = time.time()
        success = test_connection(endpoint["url"], endpoint["name"])
        test_time = time.time() - start_time
        
        result = {
            "name": endpoint["name"],
            "url": endpoint["url"],
            "success": success,
            "time": test_time
        }
        test_results.append(result)
        
        if success:
            successful_tests += 1
            safe_print(f"✅ {endpoint['name']} - SUCCESS ({test_time:.2f}s)")
        else:
            safe_print(f"❌ {endpoint['name']} - FAILED ({test_time:.2f}s)")
    
    # Print summary
    safe_print("\n" + "=" * 80)
    safe_print("TEST SUMMARY")
    safe_print("=" * 80)
    safe_print(f"Total tests  : {len(endpoints)}")
    safe_print(f"Successful   : {successful_tests}")
    safe_print(f"Failed      : {len(endpoints) - successful_tests}")
    safe_print("-" * 80)
    
    # Print successful connections first
    if successful_tests > 0:
        safe_print("\nSUCCESSFUL CONNECTIONS:")
        for result in test_results:
            if result["success"]:
                safe_print(f"- {result['name']} ({result['url']}) - {result['time']:.2f}s")
    
    # Then print failed connections
    failed_tests = [r for r in test_results if not r["success"]]
    if failed_tests:
        safe_print("\nFAILED CONNECTIONS:")
        for result in failed_tests:
            safe_print(f"- {result['name']} ({result['url']})")
    
    safe_print("\n" + "=" * 80)
    
    if successful_tests == 0:
        safe_print("\nERROR: All connection tests failed. Please check:")
        safe_print("1. Your internet connection")
        safe_print("2. Firewall settings that might block the connection")
        safe_print("3. If you're behind a proxy, configure it properly")
        return False
    else:
        safe_print(f"\nSUCCESS: {successful_tests} out of {len(endpoints)} endpoints connected successfully!")
        safe_print("Web3 connection tests completed.")
        return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
        sys.exit(1)
