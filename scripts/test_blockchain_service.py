"""
Test script for BlockchainService.

This script tests the BlockchainService with real API calls to Alchemy.
Set the ALCHEMY_API_KEY environment variable before running.
"""
import asyncio
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the blockchain service
from services.blockchain import BlockchainService, BlockchainServiceError

async def test_wallet_nfts():
    """Test fetching NFTs for a wallet."""
    # Test with a known NFT wallet (Vitalik Buterin's wallet)
    wallet_address = "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
    
    try:
        blockchain = BlockchainService()
        
        logger.info(f"Fetching NFTs for wallet: {wallet_address}")
        nfts = await blockchain.get_wallet_nfts(
            wallet_address=wallet_address,
            chain="eth-mainnet",
            page_size=5  # Just get a few for testing
        )
        
        logger.info(f"Found {len(nfts.get('ownedNfts', []))} NFTs")
        
        if nfts.get("ownedNfts"):
            logger.info("Sample NFT:")
            nft = nfts["ownedNfts"][0]
            print(f"  Contract: {nft.get('contract', {}).get('address')}")
            print(f"  Token ID: {nft.get('id', {}).get('tokenId')}")
            print(f"  Title: {nft.get('title')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing wallet NFTs: {str(e)}")
        return False
    finally:
        await blockchain.close()

async def test_token_metadata():
    """Test fetching token metadata."""
    # Test with Bored Ape Yacht Club contract and a token ID
    contract_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
    token_id = "1"  # First BAYC token
    
    try:
        blockchain = BlockchainService()
        
        logger.info(f"Fetching metadata for token {token_id} at {contract_address}")
        metadata = await blockchain.get_token_metadata(
            contract_address=contract_address,
            token_id=token_id,
            chain="eth-mainnet"
        )
        
        logger.info("Token Metadata:")
        print(f"  Title: {metadata.get('title')}")
        print(f"  Description: {metadata.get('description', '')[:100]}...")
        print(f"  Image URL: {metadata.get('image', 'N/A')}")
        
        if 'attributes' in metadata:
            print("  Attributes:")
            for attr in metadata['attributes'][:3]:  # Show first 3 attributes
                print(f"    {attr.get('trait_type')}: {attr.get('value')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing token metadata: {str(e)}")
        return False
    finally:
        await blockchain.close()

async def main():
    """Run all tests."""
    load_dotenv()  # Load environment variables from .env file
    
    if not os.getenv("ALCHEMY_API_KEY"):
        print("Error: ALCHEMY_API_KEY environment variable not set")
        print("Please create a .env file with your Alchemy API key:")
        print("ALCHEMY_API_KEY=your-api-key-here")
        return
    
    print("=== Testing Blockchain Service ===\n")
    
    print("1. Testing Wallet NFTs...")
    success = await test_wallet_nfts()
    print(f"Wallet NFTs test: {'PASSED' if success else 'FAILED'}\n")
    
    print("2. Testing Token Metadata...")
    success = await test_token_metadata()
    print(f"Token Metadata test: {'PASSED' if success else 'FAILED'}\n")

if __name__ == "__main__":
    asyncio.run(main())
