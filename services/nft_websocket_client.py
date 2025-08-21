"""
NFT WebSocket Client Service

This service provides a WebSocket client for connecting to external NFT event streams
and forwarding events to the application's WebSocket manager.
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Set, Any, Callable, Awaitable
from datetime import datetime
import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)

class NFTWebSocketClient:
    """
    A WebSocket client for connecting to external NFT event streams and forwarding
    events to the application's WebSocket manager.
    
    This client handles reconnection, message processing, and event forwarding.
    """
    
    def __init__(
        self,
        ws_url: str,
        manager: Any,  # Reference to the WebSocket manager
        reconnect_interval: int = 5,
        max_reconnect_attempts: int = 5,
        debug: bool = False
    ):
        """
        Initialize the NFT WebSocket client.
        
        Args:
            ws_url: WebSocket URL to connect to
            manager: Reference to the application's WebSocket manager
            reconnect_interval: Seconds between reconnection attempts
            max_reconnect_attempts: Maximum number of reconnection attempts
            debug: Enable debug logging
        """
        self.ws_url = ws_url
        self.manager = manager
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self.debug = debug
        self.websocket = None
        self.connected = False
        self.reconnect_attempts = 0
        self.stop_event = asyncio.Event()
        self.subscribed_collections: Set[str] = set()
        
        # Event handlers for different message types
        self.event_handlers = {
            'transfer': self._handle_transfer_event,
            'sale': self._handle_sale_event,
            'listing': self._handle_listing_event,
            'offer': self._handle_offer_event,
            'mint': self._handle_mint_event,
            'burn': self._handle_burn_event,
        }
    
    async def connect(self) -> bool:
        """
        Connect to the WebSocket server and start listening for messages.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        self.reconnect_attempts = 0
        
        while not self.stop_event.is_set() and self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                if self.debug:
                    logger.info(f"Connecting to WebSocket server at {self.ws_url} (attempt {self.reconnect_attempts + 1}/{self.max_reconnect_attempts})...")
                
                async with websockets.connect(self.ws_url) as ws:
                    self.websocket = ws
                    self.connected = True
                    self.reconnect_attempts = 0
                    
                    if self.debug:
                        logger.info("Connected to WebSocket server")
                    
                    # Resubscribe to any collections we were previously subscribed to
                    if self.subscribed_collections:
                        await self._resubscribe()
                    
                    # Start listening for messages
                    await self._listen()
                    
            except (ConnectionRefusedError, ConnectionClosed) as e:
                self.connected = False
                self.reconnect_attempts += 1
                
                if self.reconnect_attempts >= self.max_reconnect_attempts:
                    logger.error(f"Failed to connect after {self.max_reconnect_attempts} attempts")
                    return False
                
                logger.warning(f"Connection failed (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}): {e}")
                await asyncio.sleep(self.reconnect_interval)
                
            except Exception as e:
                logger.error(f"Unexpected error in WebSocket client: {e}", exc_info=True)
                self.connected = False
                await asyncio.sleep(self.reconnect_interval)
        
        return self.connected
    
    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server and clean up resources."""
        self.stop_event.set()
        
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
            self.connected = False
    
    async def _listen(self) -> None:
        """Listen for incoming WebSocket messages and process them."""
        try:
            async for message in self.websocket:
                try:
                    if self.debug:
                        logger.debug(f"Received message: {message}")
                    
                    # Parse the message
                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError:
                        logger.warning(f"Received invalid JSON: {message}")
                        continue
                    
                    # Process the message based on its type
                    await self._process_message(data)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning(f"WebSocket connection closed: {e}")
            self.connected = False
            
        except Exception as e:
            logger.error(f"Error in WebSocket listener: {e}", exc_info=True)
            self.connected = False
    
    async def _process_message(self, message: Dict[str, Any]) -> None:
        """
        Process an incoming WebSocket message.
        
        Args:
            message: The parsed message data
        """
        try:
            event_type = message.get('type')
            if not event_type:
                logger.warning(f"Message missing 'type' field: {message}")
                return
            
            # Forward the message to the appropriate handler
            handler = self.event_handlers.get(event_type)
            if handler:
                await handler(message)
            else:
                logger.warning(f"No handler for message type: {event_type}")
                
            # Forward the message to all connected clients
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
    
    async def _broadcast_message(self, message: Dict[str, Any]) -> None:
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: The message to broadcast
        """
        if not hasattr(self.manager, 'broadcast'):
            logger.warning("WebSocket manager does not have a broadcast method")
            return
        
        try:
            await self.manager.broadcast(message)
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}", exc_info=True)
    
    async def subscribe_to_collection(self, collection_address: str) -> bool:
        """
        Subscribe to events for a specific collection.
        
        Args:
            collection_address: The collection contract address to subscribe to
            
        Returns:
            bool: True if subscription was successful, False otherwise
        """
        if not self.connected or not self.websocket:
            logger.warning("Cannot subscribe: Not connected to WebSocket server")
            return False
        
        try:
            # Add to our set of subscribed collections
            self.subscribed_collections.add(collection_address.lower())
            
            # Send subscription message
            await self.websocket.send(json.dumps({
                'type': 'subscribe',
                'collection': collection_address.lower(),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }))
            
            if self.debug:
                logger.info(f"Subscribed to collection: {collection_address}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to collection {collection_address}: {e}")
            return False
    
    async def unsubscribe_from_collection(self, collection_address: str) -> bool:
        """
        Unsubscribe from events for a specific collection.
        
        Args:
            collection_address: The collection contract address to unsubscribe from
            
        Returns:
            bool: True if unsubscription was successful, False otherwise
        """
        if not self.connected or not self.websocket:
            logger.warning("Cannot unsubscribe: Not connected to WebSocket server")
            return False
        
        try:
            # Remove from our set of subscribed collections
            self.subscribed_collections.discard(collection_address.lower())
            
            # Send unsubscription message
            await self.websocket.send(json.dumps({
                'type': 'unsubscribe',
                'collection': collection_address.lower(),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }))
            
            if self.debug:
                logger.info(f"Unsubscribed from collection: {collection_address}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing from collection {collection_address}: {e}")
            return False
    
    async def _resubscribe(self) -> None:
        """Resubscribe to all previously subscribed collections."""
        if not self.subscribed_collections:
            return
            
        if self.debug:
            logger.info(f"Resubscribing to {len(self.subscribed_collections)} collections...")
        
        for collection in list(self.subscribed_collections):
            await self.subscribe_to_collection(collection)
    
    # Event handlers for different message types
    
    async def _handle_transfer_event(self, data: Dict[str, Any]) -> None:
        """Handle an NFT transfer event."""
        if self.debug:
            logger.info(f"Processing transfer event: {data}")
        
        # Extract relevant data
        event_data = data.get('data', {})
        collection = event_data.get('collection', {})
        
        # Forward to clients subscribed to this collection
        if isinstance(collection, dict):
            collection_address = collection.get('address')
        else:
            collection_address = str(collection)
            
        if collection_address:
            channel = f"collection:{collection_address.lower()}"
            await self.manager.broadcast({
                'type': 'nft_transfer',
                'data': event_data
            }, channel=channel)
    
    async def _handle_sale_event(self, data: Dict[str, Any]) -> None:
        """Handle an NFT sale event."""
        if self.debug:
            logger.info(f"Processing sale event: {data}")
        
        # Extract relevant data
        event_data = data.get('data', {})
        collection = event_data.get('collection', {})
        
        # Forward to clients subscribed to this collection
        if isinstance(collection, dict):
            collection_address = collection.get('address')
        else:
            collection_address = str(collection)
            
        if collection_address:
            channel = f"collection:{collection_address.lower()}"
            await self.manager.broadcast({
                'type': 'nft_sale',
                'data': event_data
            }, channel=channel)
    
    async def _handle_listing_event(self, data: Dict[str, Any]) -> None:
        """Handle an NFT listing event."""
        if self.debug:
            logger.info(f"Processing listing event: {data}")
        
        # Extract relevant data
        event_data = data.get('data', {})
        collection = event_data.get('collection', {})
        
        # Forward to clients subscribed to this collection
        if isinstance(collection, dict):
            collection_address = collection.get('address')
        else:
            collection_address = str(collection)
            
        if collection_address:
            channel = f"collection:{collection_address.lower()}"
            await self.manager.broadcast({
                'type': 'nft_listing',
                'data': event_data
            }, channel=channel)
    
    async def _handle_offer_event(self, data: Dict[str, Any]) -> None:
        """Handle an NFT offer event."""
        if self.debug:
            logger.info(f"Processing offer event: {data}")
        
        # Extract relevant data
        event_data = data.get('data', {})
        collection = event_data.get('collection', {})
        
        # Forward to clients subscribed to this collection
        if isinstance(collection, dict):
            collection_address = collection.get('address')
        else:
            collection_address = str(collection)
            
        if collection_address:
            channel = f"collection:{collection_address.lower()}"
            await self.manager.broadcast({
                'type': 'nft_offer',
                'data': event_data
            }, channel=channel)
    
    async def _handle_mint_event(self, data: Dict[str, Any]) -> None:
        """Handle an NFT mint event."""
        if self.debug:
            logger.info(f"Processing mint event: {data}")
        
        # Extract relevant data
        event_data = data.get('data', {})
        collection = event_data.get('collection', {})
        
        # Forward to clients subscribed to this collection
        if isinstance(collection, dict):
            collection_address = collection.get('address')
        else:
            collection_address = str(collection)
            
        if collection_address:
            channel = f"collection:{collection_address.lower()}"
            await self.manager.broadcast({
                'type': 'nft_mint',
                'data': event_data
            }, channel=channel)
    
    async def _handle_burn_event(self, data: Dict[str, Any]) -> None:
        """Handle an NFT burn event."""
        if self.debug:
            logger.info(f"Processing burn event: {data}")
        
        # Extract relevant data
        event_data = data.get('data', {})
        collection = event_data.get('collection', {})
        
        # Forward to clients subscribed to this collection
        if isinstance(collection, dict):
            collection_address = collection.get('address')
        else:
            collection_address = str(collection)
            
        if collection_address:
            channel = f"collection:{collection_address.lower()}"
            await self.manager.broadcast({
                'type': 'nft_burn',
                'data': event_data
            }, channel=channel)

# Global instance
nft_ws_client = None
