"""
Live market data integration for XSEMA.

This module provides real-time NFT market data through WebSocket connections,
price feeds, and market analytics updates.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import aiohttp
import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)

@dataclass
class MarketUpdate:
    """Market data update structure."""
    nft_id: str
    contract_address: str
    token_id: str
    price: float
    volume: float
    timestamp: datetime
    source: str
    event_type: str  # sale, listing, bid, etc.

class MarketDataProvider:
    """Base class for market data providers."""
    
    def __init__(self, name: str):
        self.name = name
        self.is_connected = False
        self.last_update = None
    
    async def connect(self):
        """Connect to the data provider."""
        raise NotImplementedError
    
    async def disconnect(self):
        """Disconnect from the data provider."""
        raise NotImplementedError
    
    async def subscribe_to_collection(self, contract_address: str):
        """Subscribe to updates for a specific collection."""
        raise NotImplementedError
    
    async def get_floor_price(self, contract_address: str) -> Optional[float]:
        """Get current floor price for a collection."""
        raise NotImplementedError

class OpenSeaProvider(MarketDataProvider):
    """OpenSea market data provider."""
    
    def __init__(self, api_key: str):
        super().__init__("OpenSea")
        self.api_key = api_key
        self.base_url = "https://api.opensea.io/api/v1"
        self.session = None
    
    async def connect(self):
        """Connect to OpenSea API."""
        try:
            self.session = aiohttp.ClientSession(
                headers={"X-API-KEY": self.api_key}
            )
            self.is_connected = True
            logger.info("✅ Connected to OpenSea API")
        except Exception as e:
            logger.error(f"❌ Failed to connect to OpenSea: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from OpenSea API."""
        if self.session:
            await self.session.close()
        self.is_connected = False
        logger.info("✅ Disconnected from OpenSea API")
    
    async def get_floor_price(self, contract_address: str) -> Optional[float]:
        """Get floor price for a collection."""
        if not self.is_connected:
            return None
        
        try:
            url = f"{self.base_url}/collection/{contract_address}/stats"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("stats", {}).get("floor_price")
                else:
                    logger.warning(f"OpenSea API returned {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching floor price from OpenSea: {e}")
            return None
    
    async def get_collection_stats(self, contract_address: str) -> Optional[Dict]:
        """Get comprehensive collection statistics."""
        if not self.is_connected:
            return None
        
        try:
            url = f"{self.base_url}/collection/{contract_address}/stats"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"OpenSea API returned {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching collection stats from OpenSea: {e}")
            return None

class WebSocketMarketServer:
    """WebSocket server for real-time market data."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8001):
        self.host = host
        self.port = port
        self.clients: List[WebSocketServerProtocol] = []
        self.providers: List[MarketDataProvider] = []
        self.collection_subscriptions: Dict[str, List[WebSocketServerProtocol]] = {}
        self.server = None
    
    async def start(self):
        """Start the WebSocket server."""
        try:
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            logger.info(f"🚀 WebSocket market server started on {self.host}:{self.port}")
            
            # Start background tasks
            asyncio.create_task(self.market_data_loop())
            asyncio.create_task(self.health_check_loop())
            
        except Exception as e:
            logger.error(f"❌ Failed to start WebSocket server: {e}")
            raise
    
    async def stop(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        logger.info("✅ WebSocket market server stopped")
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle incoming WebSocket connections."""
        client_id = id(websocket)
        logger.info(f"🔌 New WebSocket client connected: {client_id}")
        
        try:
            self.clients.append(websocket)
            
            async for message in websocket:
                await self.process_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"❌ Error handling client {client_id}: {e}")
        finally:
            await self.remove_client(websocket)
    
    async def process_message(self, websocket: WebSocketServerProtocol, message: str):
        """Process incoming WebSocket messages."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                await self.handle_subscription(websocket, data)
            elif message_type == "unsubscribe":
                await self.handle_unsubscription(websocket, data)
            elif message_type == "ping":
                await websocket.send(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.warning("Invalid JSON message received")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def handle_subscription(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle collection subscription requests."""
        contract_address = data.get("contract_address")
        if not contract_address:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "contract_address is required"
            }))
            return
        
        # Add to collection subscriptions
        if contract_address not in self.collection_subscriptions:
            self.collection_subscriptions[contract_address] = []
        
        if websocket not in self.collection_subscriptions[contract_address]:
            self.collection_subscriptions[contract_address].append(websocket)
        
        # Subscribe to data providers
        for provider in self.providers:
            try:
                await provider.subscribe_to_collection(contract_address)
            except Exception as e:
                logger.error(f"Failed to subscribe {provider.name} to {contract_address}: {e}")
        
        await websocket.send(json.dumps({
            "type": "subscribed",
            "contract_address": contract_address,
            "timestamp": datetime.now().isoformat()
        }))
        
        logger.info(f"Client subscribed to {contract_address}")
    
    async def handle_unsubscription(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle collection unsubscription requests."""
        contract_address = data.get("contract_address")
        if contract_address and contract_address in self.collection_subscriptions:
            if websocket in self.collection_subscriptions[contract_address]:
                self.collection_subscriptions[contract_address].remove(websocket)
            
            # Remove empty subscription lists
            if not self.collection_subscriptions[contract_address]:
                del self.collection_subscriptions[contract_address]
        
        await websocket.send(json.dumps({
            "type": "unsubscribed",
            "contract_address": contract_address,
            "timestamp": datetime.now().isoformat()
        }))
    
    async def remove_client(self, websocket: WebSocketServerProtocol):
        """Remove a disconnected client."""
        if websocket in self.clients:
            self.clients.remove(websocket)
        
        # Remove from all subscriptions
        for contract_address in list(self.collection_subscriptions.keys()):
            if websocket in self.collection_subscriptions[contract_address]:
                self.collection_subscriptions[contract_address].remove(websocket)
            
            if not self.collection_subscriptions[contract_address]:
                del self.collection_subscriptions[contract_address]
    
    async def broadcast_market_update(self, update: MarketUpdate):
        """Broadcast market update to subscribed clients."""
        if not update.contract_address in self.collection_subscriptions:
            return
        
        message = {
            "type": "market_update",
            "data": {
                "nft_id": update.nft_id,
                "contract_address": update.contract_address,
                "token_id": update.token_id,
                "price": update.price,
                "volume": update.volume,
                "timestamp": update.timestamp.isoformat(),
                "source": update.source,
                "event_type": update.event_type
            }
        }
        
        message_json = json.dumps(message)
        disconnected_clients = []
        
        for client in self.collection_subscriptions[update.contract_address]:
            try:
                await client.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            await self.remove_client(client)
    
    async def market_data_loop(self):
        """Main loop for processing market data."""
        while True:
            try:
                # Process updates from providers
                for provider in self.providers:
                    if provider.is_connected:
                        # Simulate market updates (replace with real provider logic)
                        await self.simulate_market_updates()
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in market data loop: {e}")
                await asyncio.sleep(10)
    
    async def simulate_market_updates(self):
        """Simulate market updates for testing."""
        # This would be replaced with real data from providers
        sample_collections = [
            "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",  # BAYC
            "0x60e4d786628fea6478f785a6d7e704777c86a7c6",  # MAYC
            "0x49cf6f5d44e70224e2e9fd2d90585dfb8c8c6ef8"   # Doodles
        ]
        
        for contract_address in sample_collections:
            if contract_address in self.collection_subscriptions:
                # Simulate a market update
                update = MarketUpdate(
                    nft_id=f"sim_{contract_address[:8]}",
                    contract_address=contract_address,
                    token_id="1234",
                    price=15.5,
                    volume=1250.0,
                    timestamp=datetime.now(),
                    source="simulation",
                    event_type="sale"
                )
                
                await self.broadcast_market_update(update)
    
    async def health_check_loop(self):
        """Health check loop for the server."""
        while True:
            try:
                # Send health check to all clients
                health_message = {
                    "type": "health_check",
                    "timestamp": datetime.now().isoformat(),
                    "active_clients": len(self.clients),
                    "active_subscriptions": len(self.collection_subscriptions)
                }
                
                message_json = json.dumps(health_message)
                disconnected_clients = []
                
                for client in self.clients:
                    try:
                        await client.send(message_json)
                    except websockets.exceptions.ConnectionClosed:
                        disconnected_clients.append(client)
                    except Exception as e:
                        logger.error(f"Health check failed for client: {e}")
                        disconnected_clients.append(client)
                
                # Remove disconnected clients
                for client in disconnected_clients:
                    await self.remove_client(client)
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)

# Global market server instance
market_server = WebSocketMarketServer()

async def start_market_server():
    """Start the market data server."""
    await market_server.start()

async def stop_market_server():
    """Stop the market data server."""
    await market_server.stop()
