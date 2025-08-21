"""
Minimal WebSocket test with basic output.
"""
import asyncio
import websockets
import json

def log(msg):
    with open('test_output.log', 'a') as f:
        f.write(f"{msg}\n")

async def test():
    log("Starting test...")
    uri = "ws://localhost:8001/ws/minimal-test"
    
    try:
        log(f"Connecting to {uri}")
        async with websockets.connect(uri) as ws:
            log("Connected successfully")
            
            # Send a test message
            msg = json.dumps({"test": "minimal test"})
            log(f"Sending: {msg}")
            await ws.send(msg)
            
            # Wait for a response
            log("Waiting for response...")
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            log(f"Received: {response}")
            
            log("Test completed successfully")
            return True
            
    except Exception as e:
        log(f"Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    log("="*50)
    log("Starting minimal WebSocket test")
    try:
        result = asyncio.get_event_loop().run_until_complete(test())
        log(f"Test result: {'SUCCESS' if result else 'FAILED'}")
    except Exception as e:
        log(f"Fatal error: {e}")
    log("="*50)
