"""
Enhanced WebSocket Test Client

Tests the enhanced WebSocket server with:
- Authentication
- Message queuing
- Heartbeats
- Rate limiting
"""
import asyncio
import json
import time
import uuid
import websockets
from typing import Optional, Dict, Any

class WebSocketTestClient:
    def __init__(self, client_id: str = None, api_key: str = "test-api-key"):
        self.client_id = client_id or f"test-client-{str(uuid.uuid4())[:8]}"
        self.api_key = api_key
        self.uri = f"ws://localhost:8001/ws/{self.client_id}"
        self.connected = False
        self.websocket = None
        self.running = False
        self.messages_received = 0
        self.errors = []
        
    async def connect(self):
        """Establish WebSocket connection and authenticate"""
        print(f"Connecting to {self.uri}...")
        self.websocket = await websockets.connect(self.uri)
        
        # Send authentication
        auth = {
            "api_key": self.api_key,
            "client_id": self.client_id,
            "timestamp": time.time()
        }
        await self.websocket.send(json.dumps(auth))
        self.connected = True
        
        # Wait for connection confirmation
        response = await self.websocket.recv()
        print(f"{self.client_id}: {response}")
        return response
    
    async def send_message(self, message: Dict[str, Any]):
        """Send a message to the server"""
        if not self.websocket:
            raise RuntimeError("Not connected to WebSocket server")
            
        message["timestamp"] = time.time()
        await self.websocket.send(json.dumps(message))
        print(f"{self.client_id} sent: {message}")
    
    async def receive_message(self, timeout: float = 5.0) -> Optional[Dict]:
        """Receive a message from the server"""
        if not self.websocket:
            raise RuntimeError("Not connected to WebSocket server")
            
        try:
            response = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
            self.messages_received += 1
            message = json.loads(response)
            
            # Handle different message types
            if message.get("type") == "heartbeat":
                print(f"{self.client_id} received heartbeat")
            elif message.get("type") == "error":
                self.errors.append(message)
                print(f"{self.client_id} error: {message}")
            else:
                print(f"{self.client_id} received: {message}")
                
            return message
            
        except asyncio.TimeoutError:
            print(f"{self.client_id}: No message received in {timeout} seconds")
            return None
        except json.JSONDecodeError:
            print(f"{self.client_id}: Received invalid JSON: {response}")
            return None
    
    async def run_test(self, duration: int = 30, message_interval: float = 1.0):
        """Run a test session"""
        try:
            await self.connect()
            self.running = True
            start_time = time.time()
            
            print(f"{self.client_id}: Starting test for {duration} seconds...")
            
            while time.time() - start_time < duration and self.running:
                # Send a test message
                message = {
                    "type": "test",
                    "message": f"Test message from {self.client_id}",
                    "count": self.messages_received + 1
                }
                await self.send_message(message)
                
                # Wait for responses
                try:
                    await asyncio.wait_for(self.receive_message(), timeout=message_interval)
                except asyncio.TimeoutError:
                    print(f"{self.client_id}: No response received")
                
                await asyncio.sleep(message_interval)
                
        except Exception as e:
            print(f"{self.client_id} error: {str(e)}")
            self.errors.append(str(e))
        finally:
            await self.close()
    
    async def close(self):
        """Close the WebSocket connection"""
        self.running = False
        if self.websocket and self.connected:
            try:
                await self.websocket.close()
                print(f"{self.client_id}: Disconnected")
            except Exception as e:
                print(f"{self.client_id}: Error during close: {e}")
            finally:
                self.websocket = None
                self.connected = False

async def run_multiple_clients(num_clients: int = 3, duration: int = 30):
    """Run multiple WebSocket clients simultaneously"""
    clients = [WebSocketTestClient() for _ in range(num_clients)]
    tasks = [client.run_test(duration) for client in clients]
    
    print(f"🚀 Starting {num_clients} WebSocket clients for {duration} seconds...")
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Print summary
    print("\n📊 Test Results:" + "="*50)
    total_messages = sum(client.messages_received for client in clients)
    total_errors = sum(len(client.errors) for client in clients)
    
    print(f"Total clients: {len(clients)}")
    print(f"Total messages received: {total_messages}")
    print(f"Total errors: {total_errors}")
    
    if total_errors > 0:
        print("\nErrors encountered:")
        for i, client in enumerate(clients):
            if client.errors:
                print(f"Client {client.client_id}:")
                for error in client.errors[:3]:  # Show first 3 errors per client
                    print(f"  - {error}")
                if len(client.errors) > 3:
                    print(f"  - ... and {len(client.errors) - 3} more")

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    num_clients = 1
    duration = 30
    
    if len(sys.argv) > 1:
        try:
            num_clients = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number of clients: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            duration = int(sys.argv[2])
        except ValueError:
            print(f"Invalid duration: {sys.argv[2]}")
            sys.exit(1)
    
    # Run the test
    try:
        asyncio.get_event_loop().run_until_complete(
            run_multiple_clients(num_clients, duration)
        )
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(0)
