"""
Simple test to verify the WebSocket server is running and responding.
"""
import asyncio
import websockets
import json

def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text} ")
    print("=" * 60)

async def test_websocket():
    uri = "ws://localhost:8001/ws/test-client"
    print(f"Testing WebSocket connection to {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            
            # Send a test message
            test_msg = {"type": "test", "message": "Hello from test script!"}
            print(f"\nSending test message: {test_msg}")
            await websocket.send(json.dumps(test_msg))
            
            # Wait for a response
            print("\nWaiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"✅ Received response: {response}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print_header("WebSocket Server Test")
    print("This script will test the WebSocket server's basic functionality.")
    
    try:
        success = asyncio.get_event_loop().run_until_complete(test_websocket())
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETED SUCCESSFULLY" if success else "❌ TEST FAILED")
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        exit(1)
