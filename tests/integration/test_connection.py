"""
Test WebSocket server connection with minimal output.
"""
import asyncio
import websockets
import json
import sys

async def test():
    uri = "ws://localhost:8001/ws/test-client"
    print(f"Testing connection to {uri}")
    
    try:
        async with websockets.connect(uri) as ws:
            print("✅ Connected to WebSocket server")
            
            # Send a test message
            msg = {"type": "test", "message": "Hello, WebSocket server!"}
            print(f"Sending: {json.dumps(msg, indent=2)}")
            await ws.send(json.dumps(msg))
            
            # Wait for a response
            print("Waiting for response...")
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"✅ Received: {response}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.get_event_loop().run_until_complete(test())
        print("\nTest", "PASSED" if success else "FAILED")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
