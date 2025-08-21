"""
Test script to verify NFT event handling in the WebSocket client.
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone

# Sample NFT event data
SAMPLE_EVENTS = [
    {
        "type": "transfer",
        "data": {
            "collection": {
                "name": "Bored Ape Yacht Club",
                "address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
            },
            "token_id": "1234",
            "from": "0x1234567890abcdef1234567890abcdef12345678",
            "to": "0xabcdef1234567890abcdef1234567890abcdef12",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    },
    {
        "type": "sale",
        "data": {
            "collection": {
                "name": "CryptoPunks",
                "address": "0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB"
            },
            "token_id": "5678",
            "seller": "0xabcdef1234567890abcdef1234567890abcdef12",
            "buyer": "0x0987654321abcdef0123456789abcdef01234567",
            "price": {
                "eth": "1.5",
                "usd": "3000.00"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    },
    {
        "type": "listing",
        "data": {
            "collection": {
                "name": "Doodles",
                "address": "0x8a90CAb2b38dba80c64b7734e58Ee1dB38B8992e"
            },
            "token_id": "9012",
            "lister": "0x1234567890abcdef1234567890abcdef12345678",
            "price": {
                "eth": "2.5",
                "usd": "5000.00"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
]

async def test_nft_events():
    """Test NFT event handling with sample data."""
    from services.websocket_service import WebSocketService
    
    # Create a test service instance
    client = WebSocketService()
    
    try:
        print("\n[Test] Starting NFT event handling test...")
        
        # Try to connect to the WebSocket server
        connected = await client.connect()
        if not connected:
            print("[Test] Failed to connect to WebSocket server. Is the server running?")
            return
            
        print("\n[Test] Processing sample NFT events...")
        
        # Process each sample event
        for event in SAMPLE_EVENTS:
            print(f"\n{'='*80}")
            print(f"[Test] Processing {event['type']} event:")
            print("-" * 40)
            
            # Process the event
            try:
                await client._process_message(json.dumps({
                    "type": event["type"],
                    "data": event["data"]
                }))
                print(f"[Test] Successfully processed {event['type']} event")
            except Exception as e:
                print(f"[Test] Error processing {event['type']} event: {e}")
                if client.config.get("debug"):
                    import traceback
                    traceback.print_exc()
            
            # Add a small delay between events
            await asyncio.sleep(0.5)
            
    except websockets.exceptions.InvalidStatusCode as e:
        if e.status_code == 403:
            print("\n[Error] 403 Forbidden - Authentication may be required")
            print("Make sure your API key is properly configured and has the correct permissions.")
        else:
            print(f"\n[Error] WebSocket connection failed with status code {e.status_code}")
    except Exception as e:
        print(f"\n[Error] Test failed: {e}")
        if client.config.get("debug"):
            import traceback
            traceback.print_exc()
    finally:
        # Clean up
        print("\n[Test] Cleaning up...")
        await client.disconnect()
        print("[Test] Test completed")

if __name__ == "__main__":
    asyncio.run(test_nft_events())
