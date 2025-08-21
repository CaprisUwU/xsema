"""
Circuit Breaker Pattern for RPC Connections

Implements a circuit breaker to handle unstable blockchain RPC connections
and automatically failover to alternative providers.
"""
import asyncio
import time
from typing import Optional, Callable, Any, Dict
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5        # Number of failures before opening circuit
    recovery_timeout: float = 60.0    # Seconds to wait before trying to close circuit
    expected_exception: type = Exception  # Exception type that indicates failure
    monitor_interval: float = 10.0    # Seconds between health checks


class CircuitBreaker:
    """Circuit breaker implementation for RPC connections"""
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        # Circuit state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.last_success_time = time.time()
        
        # Health monitoring
        self.health_check_task: Optional[asyncio.Task] = None
        self._start_health_monitoring()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info(f"Circuit {self.name}: Attempting to close circuit")
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception(f"Circuit {self.name} is OPEN - service unavailable")
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.last_success_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit {self.name}: Closing circuit after successful recovery")
            self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            logger.warning(f"Circuit {self.name}: Opening circuit after {self.failure_count} failures")
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt circuit reset"""
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _start_health_monitoring(self):
        """Start background health monitoring"""
        # Only start monitoring if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            async def monitor():
                while True:
                    try:
                        await asyncio.sleep(self.config.monitor_interval)
                        await self._health_check()
                    except Exception as e:
                        logger.error(f"Health monitoring error for circuit {self.name}: {e}")
            
            self.health_check_task = asyncio.create_task(monitor())
        except RuntimeError:
            # No running event loop, skip monitoring for now
            logger.info(f"Circuit {self.name}: No event loop, skipping health monitoring")
            self.health_check_task = None
    
    async def _health_check(self):
        """Perform health check on the circuit"""
        if self.state == CircuitState.OPEN and self._should_attempt_reset():
            logger.info(f"Circuit {self.name}: Health check suggests circuit reset")
            self.state = CircuitState.HALF_OPEN
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "is_healthy": self.state == CircuitState.CLOSED
        }
    
    def force_close(self):
        """Force close the circuit (for manual recovery)"""
        logger.info(f"Circuit {self.name}: Forcing circuit to close")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
    
    def force_open(self):
        """Force open the circuit (for manual maintenance)"""
        logger.info(f"Circuit {self.name}: Forcing circuit to open")
        self.state = CircuitState.OPEN
        self.failure_count = self.config.failure_threshold


class RPCConnectionManager:
    """Manages RPC connections with circuit breaker protection"""
    
    def __init__(self):
        self.circuits: Dict[str, CircuitBreaker] = {}
        self.alternative_providers = {
            'ethereum': [
                'https://eth.llamarpc.com',
                'https://rpc.ankr.com/eth',
                'https://cloudflare-eth.com',
                'https://ethereum.publicnode.com'
            ],
            'polygon': [
                'https://polygon.llamarpc.com',
                'https://rpc.ankr.com/polygon',
                'https://polygon-rpc.com',
                'https://polygon.chainstacklabs.com'
            ],
            'bsc': [
                'https://bsc.llamarpc.com',
                'https://bsc-dataseed1.binance.org/',
                'https://bsc-dataseed2.binance.org/',
                'https://bsc-dataseed3.binance.org/'
            ],
            'arbitrum': [
                'https://arbitrum.llamarpc.com',
                'https://rpc.ankr.com/arbitrum',
                'https://arb1.arbitrum.io/rpc',
                'https://arbitrum-one.publicnode.com'
            ],
            'optimism': [
                'https://optimism.llamarpc.com',
                'https://rpc.ankr.com/optimism',
                'https://mainnet.optimism.io',
                'https://optimism.publicnode.com'
            ],
            'base': [
                'https://mainnet.base.org',
                'https://base.llamarpc.com',
                'https://rpc.ankr.com/base',
                'https://base.blockpi.network/v1/rpc/public'
            ],
            'avalanche': [
                'https://api.avax.network/ext/bc/C/rpc',
                'https://avalanche.llamarpc.com',
                'https://rpc.ankr.com/avalanche',
                'https://avalanche.publicnode.com'
            ],
            'fantom': [
                'https://rpc.ftm.tools',
                'https://fantom.llamarpc.com',
                'https://rpc.ankr.com/fantom',
                'https://fantom.publicnode.com'
            ],
            'solana': [
                'https://api.mainnet-beta.solana.com',
                'https://solana.llamarpc.com',
                'https://rpc.ankr.com/solana',
                'https://solana.publicnode.com'
            ]
        }
    
    def get_circuit(self, network: str) -> CircuitBreaker:
        """Get or create circuit breaker for a network"""
        if network not in self.circuits:
            self.circuits[network] = CircuitBreaker(f"rpc_{network}")
        return self.circuits[network]
    
    async def test_connection_with_fallback(self, network: str) -> bool:
        """Test connection with automatic fallback to alternative providers"""
        circuit = self.get_circuit(network)
        
        async def test_provider(url: str) -> bool:
            """Test a specific RPC provider"""
            try:
                import aiohttp
                
                # Use appropriate RPC method based on network type
                if network == 'solana':
                    # Solana uses different RPC method
                    payload = {"jsonrpc": "2.0", "method": "getSlot", "params": [], "id": 1}
                else:
                    # EVM chains use eth_blockNumber
                    payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=5) as response:
                        return response.status == 200
            except Exception:
                return False
        
        # Try primary provider first
        primary_url = self.alternative_providers[network][0]
        try:
            result = await circuit.call(test_provider, primary_url)
            if result:
                return True
        except Exception as e:
            logger.warning(f"Primary provider failed for {network}: {e}")
        
        # Try alternative providers
        for url in self.alternative_providers[network][1:]:
            try:
                if await test_provider(url):
                    logger.info(f"Found working alternative provider for {network}: {url}")
                    return True
            except Exception:
                continue
        
        return False
    
    def get_network_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all network circuits"""
        return {
            network: circuit.get_status()
            for network, circuit in self.circuits.items()
        }
    
    def get_working_providers(self) -> Dict[str, str]:
        """Get list of working providers for each network"""
        working = {}
        for network, providers in self.alternative_providers.items():
            # For now, return the first provider - in production, test each one
            working[network] = providers[0]
        return working


# Global instance
rpc_manager = RPCConnectionManager()
