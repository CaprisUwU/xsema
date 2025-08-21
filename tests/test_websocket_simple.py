"""
Simple WebSocket Test Script

This script provides a basic test of the WebSocket functionality
without relying on pytest. It's useful for debugging WebSocket issues.
"""
import asyncio
import websockets
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket server URL
WS_URL = "ws://localhost:8000/api/v1/ranking/ws/test_job_123"

async def test_websocket_connection():
    """Test WebSocket connection and message exchange."""
    logger.info(f"Connecting to WebSocket server at {WS_URL}")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            logger.info("WebSocket connection established")
            
            # Send a test message
            test_message = {
                "type": "ping",
                "timestamp": int(time.time())
            }
            await websocket.send(json.dumps(test_message))
            logger.info(f"Sent message: {test_message}")
            
            # Wait for a response
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            response_data = json.loads(response)
            logger.info(f"Received response: {response_data}")
            
            # Verify the response
            if response_data.get("type") == "pong":
                logger.info("✅ WebSocket test passed!")
                return True
            else:
                logger.error(f"Unexpected response: {response_data}")
                return False
                
    except Exception as e:
        logger.error(f"WebSocket test failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Run the test
    logger.info("Starting WebSocket test...")
    result = asyncio.get_event_loop().run_until_complete(test_websocket_connection())
    
    # Exit with appropriate status code
    exit(0 if result else 1)
