#!/usr/bin/env python3
"""
WebSocket Client for NFT Events

This script demonstrates how to connect to the NFT event stream
and process real-time NFT transfer events.
"""
import asyncio
import json
import logging
from typing import Optional, Dict, Any
import websockets
from websockets.client import WebSocketClientProtocol
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NFTEventClient:
    """WebSocket client for receiving NFT events."""
    
    def __init__(self, ws_url: str = "ws://localhost:8000"):
        """Initialize the WebSocket client.
        
        Args:
            ws_url: Base WebSocket URL (e.g., ws://localhost:8000)
        """
        self.ws_url = ws_url
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.running = False
        self.subscriptions = set()
    
    def _get_ws_endpoint(self, path: str = "") -> str:
        """Get full WebSocket URL for the given path."""
        return urljoin(f"{self.ws_url.rstrip('/')}/", path.lstrip('/'))
    
    async def connect(self):
        """Connect to the WebSocket server."""
        if self.websocket is not None and not self.websocket.closed:
            logger.warning("Already connected to WebSocket server")
            return
            
        ws_url = self._get_ws_endpoint("ws")
        logger.info(f"Connecting to WebSocket server at {ws_url}")
        
        try:
            self.websocket = await websockets.connect(ws_url, ping_interval=30, ping_timeout=10)
            logger.info("Connected to WebSocket server")
            
            # Resubscribe to any existing subscriptions
            for channel in self.subscriptions:
                await self.subscribe(channel)
                
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket server: {e}")
            raise
    
    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
            logger.info("WebSocket connection closed")
    
    async def subscribe(self, channel: str):
        """Subscribe to a channel.
        
        Args:
            channel: Channel to subscribe to (e.g., 'nft_transfer' or 'collection:0x123...')
        """
        if not self.websocket or self.websocket.closed:
            await self.connect()
            
        message = {
            "type": "subscribe",
            "channel": channel
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            self.subscriptions.add(channel)
            logger.info(f"Subscribed to channel: {channel}")
        except Exception as e:
            logger.error(f"Failed to subscribe to {channel}: {e}")
            await self._handle_disconnect()
    
    async def unsubscribe(self, channel: str):
        """Unsubscribe from a channel."""
        if not self.websocket or self.websocket.closed:
            return
            
        message = {
            "type": "unsubscribe",
            "channel": channel
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            self.subscriptions.discard(channel)
            logger.info(f"Unsubscribed from channel: {channel}")
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {channel}: {e}")
    
    async def _handle_disconnect(self):
        """Handle WebSocket disconnection."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        if self.running:
            logger.info("Attempting to reconnect...")
            await asyncio.sleep(5)  # Wait before reconnecting
            await self.connect()
    
    async def listen(self):
        """Start listening for events."""
        if not self.websocket or self.websocket.closed:
            await self.connect()
            
        self.running = True
        logger.info("Listening for NFT events...")
        
        try:
            while self.running:
                try:
                    # Wait for a message
                    message = await self.websocket.recv()
                    
                    # Parse the message
                    try:
                        data = json.loads(message)
                        await self._handle_message(data)
                    except json.JSONDecodeError:
                        logger.warning(f"Received invalid JSON: {message}")
                        
                except websockets.exceptions.ConnectionClosed as e:
                    logger.warning(f"WebSocket connection closed: {e}")
                    await self._handle_disconnect()
                    
                except Exception as e:
                    logger.error(f"Error receiving message: {e}", exc_info=True)
                    await self._handle_disconnect()
                    
        except asyncio.CancelledError:
            logger.info("Listener task cancelled")
        finally:
            self.running = False
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket message."""
        event_type = data.get('event')
        
        if event_type == 'nft_transfer':
            await self._handle_nft_transfer(data)
        elif event_type == 'ping':
            await self._handle_ping()
        else:
            logger.debug(f"Received unhandled event type: {event_type}")
    
    async def _handle_nft_transfer(self, data: Dict[str, Any]):
        """Handle an NFT transfer event."""
        # Extract relevant data
        transfer = {
            'network': data.get('network_name', 'unknown'),
            'timestamp': data.get('timestamp'),
            'tx_hash': data.get('transaction_hash'),
            'from': data.get('from_address'),
            'to': data.get('to_address'),
            'contract': data.get('contract_address'),
            'token_id': data.get('token_id'),
            'price_eth': data.get('price_eth'),
            'metadata': data.get('metadata', {})
        }
        
        # Log the transfer
        logger.info(
            f"NFT Transfer: {transfer['token_id']} "
            f"from {transfer['from'][:8]}...{transfer['from'][-6:]} "
            f"to {transfer['to'][:8]}...{transfer['to'][-6:]} "
            f"on {transfer['network']} "
            f"for {transfer['price_eth'] or '?'} ETH"
        )
        
        # Here you could add your custom processing logic
        # For example, update a database, send notifications, etc.
    
    async def _handle_ping(self):
        """Handle ping message from server."""
        if self.websocket and not self.websocket.closed:
            await self.websocket.pong()


async def main():
    """Run the WebSocket client example."""
    import argparse
    
    parser = argparse.ArgumentParser(description='NFT Event WebSocket Client')
    parser.add_argument('--url', type=str, default="ws://localhost:8000",
                      help='WebSocket server URL')
    parser.add_argument('--collections', nargs='+', default=[],
                      help='Collection addresses to monitor')
    args = parser.parse_args()
    
    client = NFTEventClient(ws_url=args.url)
    
    try:
        # Connect to the WebSocket server
        await client.connect()
        
        # Subscribe to general NFT transfers
        await client.subscribe('nft_transfer')
        
        # Subscribe to specific collections if provided
        for collection in args.collections:
            await client.subscribe(f'collection:{collection.lower()}')
        
        # Start listening for events
        await client.listen()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Client stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
