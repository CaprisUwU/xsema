"""
WebSocket manager for real-time updates.

This module provides a WebSocket manager that handles real-time communication
with clients, including job progress updates and batch processing status.
"""
from fastapi import WebSocket
from typing import Dict, Optional, Set, Any, List
import asyncio
import json
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts messages to clients.
    
    This class handles:
    - Maintaining active WebSocket connections
    - Job-specific subscriptions
    - Broadcasting messages to individual clients or groups
    - Graceful connection handling and cleanup
    """
    
    def __init__(self):
        # Map of client_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Map of job_id -> set of client_ids subscribed to this job
        self.job_subscriptions: Dict[str, Set[str]] = {}
        # Map of client_id -> set of job_ids the client is subscribed to
        self.client_subscriptions: Dict[str, Set[str]] = {}
        # Lock for thread-safe operations
        self.lock = asyncio.Lock()
        # Heartbeat task
        self.heartbeat_task = None

    async def start(self):
        """Start the WebSocket manager, including background tasks."""
        self.heartbeat_task = asyncio.create_task(self._send_heartbeats())

    async def stop(self):
        """Stop the WebSocket manager and clean up resources."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass

    async def connect(self, client_id: str, websocket: WebSocket):
        """
        Accept a new WebSocket connection.
        
        Args:
            client_id: Unique identifier for the client
            websocket: The WebSocket connection object
        """
        await websocket.accept()
        async with self.lock:
            self.active_connections[client_id] = websocket
            self.client_subscriptions[client_id] = set()
            logger.info(f"Client connected: {client_id}")

    async def disconnect(self, client_id: str):
        """
        Close a WebSocket connection and clean up subscriptions.
        
        Args:
            client_id: The ID of the client to disconnect
        """
        async with self.lock:
            # Remove from active connections
            if client_id in self.active_connections:
                del self.active_connections[client_id]
                logger.info(f"Client disconnected: {client_id}")
            
            # Clean up subscriptions
            if client_id in self.client_subscriptions:
                # Remove client from all job subscriptions
                for job_id in self.client_subscriptions[client_id]:
                    if job_id in self.job_subscriptions:
                        self.job_subscriptions[job_id].discard(client_id)
                        if not self.job_subscriptions[job_id]:
                            del self.job_subscriptions[job_id]
                
                # Remove client's subscription tracking
                del self.client_subscriptions[client_id]

    async def subscribe_to_job(self, client_id: str, job_id: str):
        """
        Subscribe a client to updates for a specific job.
        
        Args:
            client_id: The client ID to subscribe
            job_id: The job ID to subscribe to
        """
        async with self.lock:
            if client_id not in self.active_connections:
                raise ValueError(f"Client {client_id} is not connected")
                
            # Initialize job subscription set if needed
            if job_id not in self.job_subscriptions:
                self.job_subscriptions[job_id] = set()
            
            # Add subscription
            self.job_subscriptions[job_id].add(client_id)
            self.client_subscriptions[client_id].add(job_id)
            logger.debug(f"Client {client_id} subscribed to job {job_id}")

    async def unsubscribe_from_job(self, client_id: str, job_id: str):
        """
        Unsubscribe a client from updates for a specific job.
        
        Args:
            client_id: The client ID to unsubscribe
            job_id: The job ID to unsubscribe from
        """
        async with self.lock:
            if job_id in self.job_subscriptions:
                self.job_subscriptions[job_id].discard(client_id)
                if not self.job_subscriptions[job_id]:
                    del self.job_subscriptions[job_id]
            
            if client_id in self.client_subscriptions:
                self.client_subscriptions[client_id].discard(job_id)
            
            logger.debug(f"Client {client_id} unsubscribed from job {job_id}")

    async def send_message(self, client_id: str, message: dict):
        """
        Send a message to a specific client.
        
        Args:
            client_id: The recipient client ID
            message: The message to send (must be JSON-serializable)
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                await self.disconnect(client_id)

    async def broadcast_to_job(self, job_id: str, message: dict):
        """
        Broadcast a message to all clients subscribed to a job.
        
        Args:
            job_id: The job ID to broadcast to
            message: The message to send (must be JSON-serializable)
        """
        if job_id not in self.job_subscriptions:
            return
            
        # Create a copy of client IDs to avoid modification during iteration
        client_ids = list(self.job_subscriptions[job_id])
        
        for client_id in client_ids:
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_json({
                        "type": "job_update",
                        "job_id": job_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        **message
                    })
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    await self.disconnect(client_id)

    async def update_job_progress(
        self, 
        job_id: str, 
        progress: int, 
        total: int, 
        status: str,
        message: Optional[str] = None
    ):
        """
        Broadcast a progress update for a job.
        
        Args:
            job_id: The job ID to update
            progress: Current progress value
            total: Total value for 100% completion
            status: Job status (e.g., 'processing', 'completed', 'failed')
            message: Optional status message
        """
        await self.broadcast_to_job(job_id, {
            "type": "progress",
            "progress": progress,
            "total": total,
            "status": status,
            "message": message or f"Processing: {progress}/{total}",
            "percentage": min(100, int((progress / max(1, total)) * 100)) if total > 0 else 0
        })

    async def _send_heartbeats(self):
        """Background task to send periodic heartbeats to all clients."""
        while True:
            try:
                # Create a copy of client IDs to avoid modification during iteration
                client_ids = list(self.active_connections.keys())
                
                for client_id in client_ids:
                    if client_id in self.active_connections:
                        try:
                            await self.active_connections[client_id].send_json({
                                "type": "heartbeat",
                                "timestamp": datetime.utcnow().isoformat()
                            })
                        except Exception as e:
                            logger.error(f"Error sending heartbeat to {client_id}: {e}")
                            await self.disconnect(client_id)
                
                # Send heartbeats every 30 seconds
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                logger.info("Heartbeat task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in heartbeat task: {e}")
                await asyncio.sleep(5)  # Prevent tight loop on errors

# Global instance
manager = WebSocketManager()
