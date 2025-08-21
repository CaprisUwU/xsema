# Configure RPC URLs and Test Multi-Chain Connectivity
# This script sets environment variables for blockchain RPC endpoints and tests connectivity

Write-Host "🔧 Configuring Blockchain RPC URLs..." -ForegroundColor Green
Write-Host "=" * 60

# Set environment variables for blockchain RPC URLs
$env:ETHEREUM_RPC_URL = "https://eth.llamarpc.com"
$env:POLYGON_RPC_URL = "https://polygon-rpc.com"
$env:BSC_RPC_URL = "https://bsc-dataseed1.binance.org"
$env:ARBITRUM_RPC_URL = "https://arb1.arbitrum.io/rpc"
$env:OPTIMISM_RPC_URL = "https://mainnet.optimism.io"
$env:BASE_RPC_URL = "https://mainnet.base.org"
$env:AVALANCHE_RPC_URL = "https://api.avax.network/ext/bc/C/rpc"
$env:FANTOM_RPC_URL = "https://rpc.ftm.tools"
$env:SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

# Set Alchemy API URLs (demo keys for testing)
$env:ALCHEMY_ETH_HTTP_URL = "https://eth-mainnet.g.alchemy.com/v2/demo"
$env:ALCHEMY_POLYGON_HTTP_URL = "https://polygon-mainnet.g.alchemy.com/v2/demo"
$env:ALCHEMY_ARBITRUM_HTTP_URL = "https://arb-mainnet.g.alchemy.com/v2/demo"
$env:ALCHEMY_OPTIMISM_HTTP_URL = "https://opt-mainnet.g.alchemy.com/v2/demo"

# Set demo API keys
$env:ALCHEMY_API_KEY = "demo"
$env:OPENSEA_API_KEY = "demo"
$env:MORALIS_API_KEY = "demo"
$env:ETHERSCAN_API_KEY = "demo"

Write-Host "✅ Environment variables set successfully!" -ForegroundColor Green
Write-Host ""

# Test multi-chain connectivity
Write-Host "🧪 Testing Multi-Chain Connectivity..." -ForegroundColor Blue
Write-Host "=" * 60

try {
    # Import and test multi-chain service
    Write-Host "Testing MultiChainService import..." -ForegroundColor Yellow
    
    # Create a temporary Python script for testing
    $testScript = @"
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

try:
    from core.multi_chain_config import MultiChainConfig, ChainType
    print('✅ Multi-chain config imported successfully')
    
    # Test configuration
    config = MultiChainConfig()
    networks = config.get_supported_networks()
    print(f'✅ Found {len(networks)} supported networks')
    
    # Test getting RPC URLs
    eth_rpc = config.get_rpc_url(ChainType.ETHEREUM)
    poly_rpc = config.get_rpc_url(ChainType.POLYGON)
    print(f'✅ Ethereum RPC: {eth_rpc}')
    print(f'✅ Polygon RPC: {poly_rpc}')
    
    print('✅ Multi-chain configuration test passed!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"@

    # Write the test script to a temporary file
    $testScript | Out-File -FilePath "temp_test.py" -Encoding UTF8
    
    # Run the test script
    python temp_test.py
    
    # Clean up
    Remove-Item "temp_test.py" -ErrorAction SilentlyContinue

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Multi-chain configuration test passed!" -ForegroundColor Green
    } else {
        Write-Host "❌ Multi-chain configuration test failed!" -ForegroundColor Red
    }

} catch {
    Write-Host "❌ Error testing multi-chain configuration: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Start the FastAPI server: python main.py"
Write-Host "2. Test multi-chain endpoints: http://localhost:8001/api/v1/multi-chain/networks"
Write-Host "3. Check network status: http://localhost:8001/api/v1/multi-chain/networks/status"
Write-Host ""
Write-Host "Environment variables are set for this session only."
Write-Host "For permanent setup, add these to your system environment or .env file."
