"""
Live WebSocket manager for real-time updates.
"""
from fastapi import WebSocket
from typing import Dict, Optional
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.lock = asyncio.Lock()

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

# Global instance
manager = ConnectionManager()
