# live/routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from .ws_manager import manager
from .event_listener import BlockchainEventListener
import json
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time event streaming"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Wait for messages from client
            try:
                data = await websocket.receive_text()
                await _handle_client_message(client_id, data)
            except WebSocketDisconnect:
                logger.info(f"Client {client_id} disconnected")
                break
            except Exception as e:
                logger.error(f"Error handling client message: {e}")
                await manager.send_personal_message(client_id, {
                    'type': 'error',
                    'message': str(e)
                })
                
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        await manager.disconnect(client_id)

async def _handle_client_message(client_id: str, message: str):
    """Handle incoming WebSocket messages from clients"""
    try:
        data = json.loads(message)
        message_type = data.get('type')
        
        if message_type == 'subscribe':
            channels = data.get('channels', [])
            if not isinstance(channels, list):
                raise ValueError("Channels must be a list")
            await manager.subscribe(client_id, channels)
            await manager.send_personal_message(client_id, {
                'type': 'subscription_update',
                'status': 'subscribed',
                'channels': channels
            })
            
        elif message_type == 'unsubscribe':
            channels = data.get('channels', [])
            if not isinstance(channels, list):
                raise ValueError("Channels must be a list")
            await manager.unsubscribe(client_id, channels)
            await manager.send_personal_message(client_id, {
                'type': 'subscription_update',
                'status': 'unsubscribed',
                'channels': channels
            })
            
        elif message_type == 'ping':
            await manager.send_personal_message(client_id, {
                'type': 'pong',
                'timestamp': int(asyncio.get_event_loop().time())
            })
            
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON message")
    except Exception as e:
        logger.error(f"Error processing client message: {e}")
        raise

# Add startup/shutdown event handlers
@router.on_event("startup")
async def startup_event():
    """Start the blockchain event listener when the app starts"""
    global event_listener
    event_listener = BlockchainEventListener()
    asyncio.create_task(event_listener.start())

@router.on_event("shutdown")
async def shutdown_event():
    """Stop the blockchain event listener when the app shuts down"""
    if 'event_listener' in globals():
        await event_listener.stop()