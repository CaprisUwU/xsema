"""
Test Minimal WebSocket Server

A simple script to test the minimal WebSocket server.
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8001/ws"
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")
            
            # Send a test message
            message = {"text": "Hello from test client!"}
            print(f"Sending: {message}")
            await websocket.send(json.dumps(message))
            
            # Wait for a response
            print("Waiting for response...")
            response = await websocket.recv()
            print(f"Received: {response}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting WebSocket test...")
    asyncio.get_event_loop().run_until_complete(test_websocket())
