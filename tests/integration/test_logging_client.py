"""
Test Logging WebSocket Client

A simple WebSocket client to test the logging WebSocket server.
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('websocket_client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def test_websocket():
    uri = "ws://localhost:8001"
    logger.info(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as websocket:
            logger.info("Connected to WebSocket server")
            
            # Wait for welcome message
            try:
                welcome = await asyncio.wait_for(websocket.recv(), timeout=5)
                logger.info(f"Received welcome: {welcome}")
            except asyncio.TimeoutError:
                logger.warning("No welcome message received")
            
            # Send a test message
            test_msg = {
                "type": "test",
                "message": "Hello, server!",
                "timestamp": datetime.now().isoformat()
            }
            logger.info(f"Sending test message: {json.dumps(test_msg, indent=2)}")
            await websocket.send(json.dumps(test_msg))
            
            # Wait for echo response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                logger.info(f"Received response: {response}")
                return True
            except asyncio.TimeoutError:
                logger.warning("No response received within timeout")
                return False
                
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("=== WebSocket Client Test ===")
    logger.info(f"Starting test at {datetime.now().isoformat()}")
    
    try:
        success = asyncio.run(test_websocket())
        if success:
            logger.info("✅ Test completed successfully")
        else:
            logger.error("❌ Test failed")
    except KeyboardInterrupt:
        logger.info("Test cancelled by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
    
    logger.info("Test complete")
