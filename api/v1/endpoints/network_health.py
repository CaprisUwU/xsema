"""
Network Health Dashboard Endpoint

Provides real-time monitoring of blockchain network connectivity,
circuit breaker states, and RPC provider health.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any
import asyncio
import logging
from datetime import datetime, timezone

from core.circuit_breaker import rpc_manager
from services.multi_chain_service import MultiChainService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/network-health", tags=["network-health"])

# All supported networks including Solana, Base, Avalanche, and Fantom
SUPPORTED_NETWORKS = [
    'ethereum', 'polygon', 'bsc', 'arbitrum', 'optimism', 
    'base', 'avalanche', 'fantom', 'solana'
]

@router.get("/", summary="Get Network Health Overview")
async def get_network_health_overview():
    """
    Get comprehensive overview of all network health statuses.
    """
    try:
        # Get circuit breaker statuses
        circuit_statuses = rpc_manager.get_network_status()
        
        # Test current connections
        multi_chain_service = MultiChainService()
        network_tests = {}
        
        # Test each network
        for network in SUPPORTED_NETWORKS:
            try:
                result = await multi_chain_service.test_connection_by_name(network)
                network_tests[network] = result
            except Exception as e:
                logger.error(f"Error testing {network} connection: {e}")
                network_tests[network] = False
        
        # Calculate overall health metrics
        total_networks = len(SUPPORTED_NETWORKS)
        healthy_networks = sum(1 for status in network_tests.values() if status)
        unhealthy_networks = total_networks - healthy_networks
        health_percentage = (healthy_networks / total_networks) * 100 if total_networks > 0 else 0
        
        # Determine overall status
        if health_percentage >= 80:
            overall_status = "healthy"
        elif health_percentage >= 50:
            overall_status = "degraded"
        else:
            overall_status = "critical"
        
        return {
            "overview": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "overall_status": overall_status,
                "health_percentage": round(health_percentage, 2),
                "total_networks": total_networks,
                "healthy_networks": healthy_networks,
                "unhealthy_networks": unhealthy_networks
            },
            "network_status": {
                network: {
                    "connection_test": network_tests.get(network, False),
                    "circuit_breaker": circuit_statuses.get(f"rpc_{network}", {}),
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
                for network in SUPPORTED_NETWORKS
            },
            "working_providers": rpc_manager.get_working_providers()
        }
        
    except Exception as e:
        logger.error(f"Error getting network health overview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get network health: {str(e)}")


@router.get("/{network}", summary="Get Specific Network Health")
async def get_network_health(network: str):
    """
    Get detailed health status for a specific network.
    """
    try:
        # Validate network
        if network not in SUPPORTED_NETWORKS:
            raise HTTPException(status_code=400, detail=f"Invalid network. Must be one of: {SUPPORTED_NETWORKS}")
        
        # Get circuit breaker status
        circuit = rpc_manager.get_circuit(network)
        circuit_status = circuit.get_status()
        
        # Test connection
        multi_chain_service = MultiChainService()
        connection_test = await multi_chain_service.test_connection_by_name(network)
        
        # Get alternative providers
        providers = rpc_manager.alternative_providers.get(network, [])
        
        return {
            "network": network,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "connection_test": connection_test,
            "circuit_breaker": circuit_status,
            "alternative_providers": providers,
            "status": "healthy" if connection_test and circuit_status["is_healthy"] else "unhealthy"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting {network} health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get {network} health: {str(e)}")


@router.post("/{network}/force-close", summary="Force Close Circuit Breaker")
async def force_close_circuit(network: str):
    """
    Force close the circuit breaker for a specific network.
    Use this for manual recovery after maintenance.
    """
    try:
        # Validate network
        if network not in SUPPORTED_NETWORKS:
            raise HTTPException(status_code=400, detail=f"Invalid network. Must be one of: {SUPPORTED_NETWORKS}")
        
        # Force close circuit
        circuit = rpc_manager.get_circuit(network)
        circuit.force_close()
        
        logger.info(f"Circuit breaker for {network} force closed")
        
        return {
            "message": f"Circuit breaker for {network} force closed successfully",
            "network": network,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "new_status": circuit.get_status()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error force closing {network} circuit: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to force close circuit: {str(e)}")


@router.post("/{network}/force-open", summary="Force Open Circuit Breaker")
async def force_open_circuit(network: str):
    """
    Force open the circuit breaker for a specific network.
    Use this for planned maintenance or emergency shutdown.
    """
    try:
        # Validate network
        if network not in SUPPORTED_NETWORKS:
            raise HTTPException(status_code=400, detail=f"Invalid network. Must be one of: {SUPPORTED_NETWORKS}")
        
        # Force open circuit
        circuit = rpc_manager.get_circuit(network)
        circuit.force_open()
        
        logger.info(f"Circuit breaker for {network} force opened")
        
        return {
            "message": f"Circuit breaker for {network} force opened successfully",
            "network": network,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "new_status": circuit.get_status()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error force opening {network} circuit: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to force open circuit: {str(e)}")


@router.post("/test-all", summary="Test All Network Connections")
async def test_all_networks(background_tasks: BackgroundTasks):
    """
    Test all network connections and update health status.
    This is a background task that may take some time.
    """
    try:
        # Start background testing
        background_tasks.add_task(_test_all_networks_background)
        
        return {
            "message": "Network testing started in background",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Check /network-health endpoint for updated results"
        }
        
    except Exception as e:
        logger.error(f"Error starting network tests: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start network tests: {str(e)}")


async def _test_all_networks_background():
    """Background task to test all networks"""
    try:
        logger.info("Starting background network testing...")
        
        multi_chain_service = MultiChainService()
        
        for network in SUPPORTED_NETWORKS:
            try:
                logger.info(f"Testing {network} connection...")
                result = await multi_chain_service.test_connection_by_name(network)
                logger.info(f"{network} connection test result: {result}")
                
                # Small delay between tests
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error testing {network}: {e}")
        
        logger.info("Background network testing completed")
        
    except Exception as e:
        logger.error(f"Background network testing failed: {e}")


@router.get("/providers/working", summary="Get Working RPC Providers")
async def get_working_providers():
    """
    Get list of currently working RPC providers for each network.
    """
    try:
        providers = rpc_manager.get_working_providers()
        
        return {
            "working_providers": providers,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "This shows the primary provider for each network. Use /network-health/{network} for detailed status."
        }
        
    except Exception as e:
        logger.error(f"Error getting working providers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get working providers: {str(e)}")
