#!/usr/bin/env python3
"""
NFT Event Listener

This script initializes and runs the blockchain event listener to monitor NFT transfers
and broadcast them to connected WebSocket clients.
"""
import asyncio
import logging
import signal
import sys
from typing import List, Optional

from dotenv import load_dotenv

from .event_listener import BlockchainEventListener
from .ws_manager import manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('event_listener.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class NFTEventListener:
    """Main class to manage the NFT event listener lifecycle."""
    
    def __init__(self, rpc_url: Optional[str] = None, 
                contract_addresses: Optional[List[str]] = None):
        """Initialize the NFT event listener.
        
        Args:
            rpc_url: Optional custom RPC URL. Uses WEB3_PROVIDER_URI env var if not provided.
            contract_addresses: Optional list of contract addresses to monitor.
        """
        self.listener = BlockchainEventListener(
            rpc_url=rpc_url,
            contract_addresses=contract_addresses
        )
        self.running = False
        
    async def start(self, from_block: Optional[int] = None):
        """Start the event listener."""
        if self.running:
            logger.warning("Listener is already running")
            return
            
        self.running = True
        logger.info("Starting NFT event listener")
        
        # Register signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(s))
            )
        
        try:
            # Initialize Web3 connection
            await self.listener._initialize_web3()
            
            # Start the event listener
            await self.listener.start(from_block=from_block)
            
        except Exception as e:
            logger.error(f"Error in event listener: {e}", exc_info=True)
            await self.shutdown()
    
    async def shutdown(self, sig: Optional[int] = None):
        """Gracefully shut down the event listener."""
        if not self.running:
            return
            
        logger.info(f"Shutting down NFT event listener (signal: {sig or 'manual'})")
        self.running = False
        
        # Stop the blockchain listener
        await self.listener.stop()
        
        # Close WebSocket connections
        await manager.disconnect_all()
        
        logger.info("NFT event listener stopped")
        
        # Exit the application
        sys.exit(0 if sig is None else 128 + sig)

def parse_args():
    """Parse command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description='NFT Event Listener')
    parser.add_argument('--rpc', type=str, help='Ethereum RPC URL')
    parser.add_argument('--from-block', type=int, help='Block number to start from')
    parser.add_argument('--contracts', nargs='+', help='Contract addresses to monitor')
    
    return parser.parse_args()

async def main():
    """Main entry point."""
    args = parse_args()
    
    # Initialize the event listener
    listener = NFTEventListener(
        rpc_url=args.rpc,
        contract_addresses=args.contracts
    )
    
    try:
        # Start the event listener
        await listener.start(from_block=args.from_block)
        
        # Keep the event loop running
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        logger.info("Shutting down due to cancellation")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        await listener.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested, exiting...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
