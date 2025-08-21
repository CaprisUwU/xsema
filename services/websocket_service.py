"""
WebSocket Connection Manager

This module manages WebSocket connections and implements a publish-subscribe
pattern for real-time event broadcasting. It supports multiple channels and
efficient message routing to connected clients.

Example usage:
    # Client side (JavaScript)
    const ws = new WebSocket('ws://your-api/ws')
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received:', data);
    }
    
    // Subscribe to channels
    ws.send(JSON.stringify({
        type: 'subscribe',
        channels: ['nft_events', 'collection:bayc']
    }));
"""
import json
import asyncio
import logging
import uuid
from typing import Dict, List, Set, Optional, Any, Callable, Awaitable
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

# Type aliases
MessageHandler = Callable[[Dict[str, Any], 'Connection'], Awaitable[None]]

class Connection:
    """Represents a WebSocket connection with subscription management."""
    
    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.subscriptions: Set[str] = set()
        self.connected_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.metadata: Dict[str, Any] = {}
    
    async def send_json(self, data: Any) -> bool:
        """Send JSON data to the client."""
        try:
            await self.websocket.send_text(json.dumps(data))
            self.last_activity = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Error sending to {self.client_id}: {e}")
            return False
    
    def is_subscribed(self, channel: str) -> bool:
        """Check if the connection is subscribed to a channel."""
        # Check for exact match or wildcard subscription
        return (channel in self.subscriptions or 
                any(channel.startswith(sub.split(':')[0] + ':') 
                    for sub in self.subscriptions if ':' in sub))

class ConnectionManager:
    """Manages WebSocket connections and message routing."""
    
    def __init__(self):
        self.connections: Dict[str, Connection] = {}
        self.channel_subscribers: Dict[str, Set[str]] = {}
        self.handlers: Dict[str, MessageHandler] = {
            'subscribe': self._handle_subscribe,
            'unsubscribe': self._handle_unsubscribe,
            'ping': self._handle_ping,
        }
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """Register a new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
            client_id: Optional client ID, will generate one if not provided
            
        Returns:
            The client ID for this connection
        """
        client_id = client_id or f"client_{uuid.uuid4().hex[:8]}"
        connection = Connection(websocket, client_id)
        
        async with self.lock:
            self.connections[client_id] = connection
            logger.info(f"Client connected: {client_id}")
            
        # Send welcome message with client ID
        await connection.send_json({
            'type': 'connection_established',
            'client_id': client_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
        return client_id
    
    async def disconnect(self, client_id: str):
        """Remove a WebSocket connection and all its subscriptions."""
        async with self.lock:
            if client_id in self.connections:
                connection = self.connections[client_id]
                
                # Remove from all channel subscriptions
                for channel in list(connection.subscriptions):
                    await self._unsubscribe_channel(client_id, channel)
                
                # Remove the connection
                del self.connections[client_id]
                logger.info(f"Client disconnected: {client_id}")
    
    async def handle_message(self, client_id: str, message: str):
        """Handle an incoming message from a client."""
        if client_id not in self.connections:
            return
            
        connection = self.connections[client_id]
        connection.last_activity = datetime.utcnow()
        
        try:
            data = json.loads(message)
            message_type = data.get('type', '').lower()
            
            if message_type in self.handlers:
                await self.handlers[message_type](data, connection)
            else:
                await self._send_error(connection, 'unknown_message_type', 
                                     f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self._send_error(connection, 'invalid_json', 'Invalid JSON message')
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            await self._send_error(connection, 'server_error', 'Internal server error')
    
    async def broadcast(self, channel: str, message: Any, condition: Optional[Callable[[Connection], bool]] = None):
        """Broadcast a message to all subscribers of a channel.
        
        Args:
            channel: The channel to broadcast to
            message: The message to send (will be JSON-serialized)
            condition: Optional function to filter which connections receive the message
        """
        if not isinstance(message, dict) or 'type' not in message:
            raise ValueError("Message must be a dict with a 'type' field")
            
        # Add timestamp if not present
        if 'timestamp' not in message:
            message['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Get all subscribers for this channel
        subscribers = set()
        async with self.lock:
            # Exact match subscribers
            subscribers.update(self.channel_subscribers.get(channel, set()))
            
            # Wildcard subscribers (e.g., 'collection:*')
            channel_parts = channel.split(':', 1)
            if len(channel_parts) > 1:
                wildcard = f"{channel_parts[0]}:*"
                subscribers.update(self.channel_subscribers.get(wildcard, set()))
        
        # Send to each subscriber
        tasks = []
        for client_id in subscribers:
            if client_id in self.connections:
                connection = self.connections[client_id]
                if condition is None or condition(connection):
                    tasks.append(connection.send_json(message))
        
        # Run sends in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _handle_subscribe(self, data: Dict[str, Any], connection: Connection):
        """Handle subscription requests."""
        channels = data.get('channels', [])
        if not isinstance(channels, list):
            await self._send_error(connection, 'invalid_request', 'channels must be a list')
            return
            
        for channel in channels:
            if not isinstance(channel, str):
                continue
                
            if channel not in connection.subscriptions:
                await self._subscribe_channel(connection.client_id, channel)
                
        await connection.send_json({
            'type': 'subscription_update',
            'subscribed': list(connection.subscriptions),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    
    async def _handle_unsubscribe(self, data: Dict[str, Any], connection: Connection):
        """Handle unsubscription requests."""
        channels = data.get('channels', [])
        if not isinstance(channels, list):
            await self._send_error(connection, 'invalid_request', 'channels must be a list')
            return
            
        for channel in channels:
            if channel in connection.subscriptions:
                await self._unsubscribe_channel(connection.client_id, channel)
                
        await connection.send_json({
            'type': 'subscription_update',
            'subscribed': list(connection.subscriptions),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    
    async def _handle_ping(self, data: Dict[str, Any], connection: Connection):
        """Handle ping/pong for connection keep-alive."""
        await connection.send_json({
            'type': 'pong',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    
    async def _subscribe_channel(self, client_id: str, channel: str):
        """Subscribe a client to a channel."""
        async with self.lock:
            if client_id not in self.connections:
                return
                
            connection = self.connections[client_id]
            
            # Add to connection's subscriptions
            connection.subscriptions.add(channel)
            
            # Add to channel's subscribers
            if channel not in self.channel_subscribers:
                self.channel_subscribers[channel] = set()
            self.channel_subscribers[channel].add(client_id)
            
            logger.debug(f"Client {client_id} subscribed to {channel}")
    
    async def _unsubscribe_channel(self, client_id: str, channel: str):
        """Unsubscribe a client from a channel."""
        async with self.lock:
            if client_id in self.connections:
                self.connections[client_id].subscriptions.discard(channel)
                
            if channel in self.channel_subscribers:
                self.channel_subscribers[channel].discard(client_id)
                if not self.channel_subscribers[channel]:
                    del self.channel_subscribers[channel]
            
            logger.debug(f"Client {client_id} unsubscribed from {channel}")
    
    async def _send_error(self, connection: Connection, error_type: str, message: str):
        """Send an error message to a client."""
        await connection.send_json({
            'type': 'error',
            'error': error_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.connections)
    
    def get_subscription_count(self) -> int:
        """Get the total number of subscriptions across all channels."""
        return sum(len(subscribers) for subscribers in self.channel_subscribers.values())

    async def subscribe(self, client_id: str, channels: List[str]) -> bool:
        """Subscribe client to channels"""
        if not channels or client_id not in self.connections:
            return False
            
        async with self.lock:
            for channel in channels:
                # Add to client's subscriptions
                self.connections[client_id].subscriptions.add(channel)
                
                # Add to channel's subscribers
                if channel not in self.channel_subscribers:
                    self.channel_subscribers[channel] = set()
                self.channel_subscribers[channel].add(client_id)
                
            logger.debug(f"Client {client_id} subscribed to {channels}")
            return True
            
    async def unsubscribe(self, client_id: str, channels: List[str]) -> None:
        """Unsubscribe client from channels"""
        if not channels or client_id not in self.connections:
            return
            
        async with self.lock:
            connection = self.connections.get(client_id)
            if not connection:
                return
                
            for channel in channels:
                # Remove from client's subscriptions
                if channel in connection.subscriptions:
                    connection.subscriptions.remove(channel)
                
                # Remove from channel's subscribers
                if channel in self.channel_subscribers:
                    self.channel_subscribers[channel].discard(client_id)
                    if not self.channel_subscribers[channel]:
                        del self.channel_subscribers[channel]
                        
            logger.debug(f"Client {client_id} unsubscribed from {channels}")
            
    async def broadcast_event(self, event_type: str, data: dict, channel: str = None) -> None:
        """Broadcast an event to all subscribed clients"""
        message = {
            'type': event_type,
            'data': data,
            'timestamp': int(asyncio.get_event_loop().time())
        }
        
        # If no channel specified, use event_type as channel
        target_channel = channel or event_type
        message_json = json.dumps(message)
        
        # Get subscribers for this channel
        async with self.lock:
            subscribers = set()
            if target_channel in self.channel_subscribers:
                subscribers.update(self.channel_subscribers[target_channel])
            if '*' in self.channel_subscribers:  # Global subscribers
                subscribers.update(self.channel_subscribers['*'])
                
        # Send message to all subscribers
        disconnected = []
        for client_id in subscribers:
            connection = self.connections.get(client_id)
            if connection:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to client {client_id}: {e}")
                    disconnected.append(client_id)
                
        # Clean up disconnected clients
        for client_id in disconnected:
            await self.disconnect(client_id)
            
    async def send_personal_message(self, client_id: str, message: dict) -> bool:
        """Send a message to a specific client"""
        async with self.lock:
            connection = self.connections.get(client_id)
            if not connection:
                return False
                
        try:
            await self.active_connections[client_id].send_text(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")
            await self.disconnect(client_id)
            return False

# Global instance
manager = ConnectionManager()