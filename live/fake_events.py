"""
Fake Event Generator for NFT Analytics Platform

This module provides realistic fake NFT event generation for development and testing.
It simulates various blockchain events that would be processed by the real system.
"""
import random
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from faker import Faker

logger = logging.getLogger(__name__)

# Initialize Faker for realistic test data
fake = Faker()

# Common NFT collections with their attributes
NFT_COLLECTIONS = [
    {
        "name": "Bored Ape Yacht Club",
        "symbol": "BAYC",
        "contract": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
        "floor_price": 30.0,  # In ETH
        "total_supply": 10000,
        "traits": ["Fur", "Hat", "Eyes", "Mouth", "Clothes", "Background"]
    },
    {
        "name": "CryptoPunks",
        "symbol": "PUNK",
        "contract": "0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB",
        "floor_price": 65.0,
        "total_supply": 10000,
        "traits": ["Type", "Accessory", "Hair", "Facial Hair", "Mouth", "Eyes"]
    },
    {
        "name": "Doodles",
        "symbol": "DOODLE",
        "contract": "0x8a90CAb2b38dba80c64b7734e58Ee1dB38B8992e",
        "floor_price": 5.0,
        "total_supply": 10000,
        "traits": ["Face", "Hair", "Body", "Head", "Background"]
    },
    {
        "name": "Azuki",
        "symbol": "AZUKI",
        "contract": "0xED5AF388653567Af2F388E6224dC7C4b3241C544",
        "floor_price": 12.5,
        "total_supply": 10000,
        "traits": ["Type", "Hair", "Clothing", "Eyes", "Mouth", "Off Hand"]
    },
    {
        "name": "CloneX",
        "symbol": "CLONEX",
        "contract": "0x49cF6f5d44E70224e2E23fD2dC2558beEaB6Bf86",
        "floor_price": 8.0,
        "total_supply": 20000,
        "traits": ["Type", "Eyes", "Mouth", "Helmet", "Clothing", "Jewelry"]
    }
]

class NFTEventGenerator:
    """Generates realistic fake NFT events for development and testing."""
    
    def __init__(self):
        self.collections = NFT_COLLECTIONS
        self.wallets = set()
        self._initialize_wallets(100)  # Start with 100 random wallets
        self.last_event_time = datetime.utcnow()
        self.event_id = 0
        
    def _initialize_wallets(self, count: int):
        """Initialize a set of random wallet addresses."""
        for _ in range(count):
            self.wallets.add(f"0x{fake.sha256()[:40]}")
    
    def _get_random_collection(self) -> Dict[str, Any]:
        """Get a random NFT collection with some randomization."""
        collection = random.choice(self.collections).copy()
        # Add some randomness to floor price (±20%)
        collection["floor_price"] = round(
            collection["floor_price"] * random.uniform(0.8, 1.2),
            2
        )
        return collection
    
    def _get_random_traits(self, collection: Dict[str, Any]) -> Dict[str, str]:
        """Generate random traits for an NFT based on collection."""
        traits = {}
        for trait_type in collection.get("traits", []):
            # Simple trait generation - in a real app, this would use the actual trait distribution
            traits[trait_type] = fake.word()
        return traits
    
    def _get_random_wallet(self) -> str:
        """Get a random wallet, with a small chance to generate a new one."""
        if random.random() < 0.1 and len(self.wallets) < 1000:  # 10% chance to add a new wallet
            new_wallet = f"0x{fake.sha256()[:40]}"
            self.wallets.add(new_wallet)
            return new_wallet
        return random.choice(list(self.wallets))
    
    def _get_event_timestamp(self) -> str:
        """Generate a realistic timestamp for the event."""
        # Move time forward by a random amount (0-30 seconds)
        self.last_event_time += timedelta(seconds=random.uniform(0, 30))
        return self.last_event_time.isoformat() + "Z"
    
    def generate_mint_event(self) -> Dict[str, Any]:
        """Generate a fake NFT mint event."""
        collection = self._get_random_collection()
        token_id = random.randint(1, collection["total_supply"])
        
        return {
            "event_id": f"evt_{self._next_event_id()}",
            "event_type": "MINT",
            "timestamp": self._get_event_timestamp(),
            "collection": {
                "address": collection["contract"],
                "name": collection["name"],
                "symbol": collection["symbol"]
            },
            "token_id": str(token_id),
            "token_uri": f"ipfs://QmXp/.../{token_id}",
            "minter": self._get_random_wallet(),
            "price_eth": round(random.uniform(0.05, 0.2), 4),  # Mint price
            "traits": self._get_random_traits(collection),
            "rarity_score": round(random.uniform(0, 1), 4),
            "rarity_rank": random.randint(1, collection["total_supply"])
        }
    
    def generate_sale_event(self) -> Dict[str, Any]:
        """Generate a fake NFT sale event."""
        collection = self._get_random_collection()
        token_id = random.randint(1, collection["total_supply"])
        seller = self._get_random_wallet()
        buyer = self._get_random_wallet()
        
        # Ensure buyer and seller are different
        while buyer == seller and len(self.wallets) > 1:
            buyer = self._get_random_wallet()
        
        price = round(random.uniform(
            collection["floor_price"] * 0.8,  
            collection["floor_price"] * 3.0    
        ), 2)
        
        return {
            "event_id": f"evt_{self._next_event_id()}",
            "event_type": "SALE",
            "timestamp": self._get_event_timestamp(),
            "collection": {
                "address": collection["contract"],
                "name": collection["name"],
                "symbol": collection["symbol"]
            },
            "token_id": str(token_id),
            "seller": seller,
            "buyer": buyer,
            "price_eth": price,
            "marketplace": random.choice(["OpenSea", "LooksRare", "X2Y2", "Blur"]),
            "tx_hash": f"0x{fake.sha256()}"
        }
    
    def generate_transfer_event(self) -> Dict[str, Any]:
        """Generate a fake NFT transfer event."""
        collection = self._get_random_collection()
        token_id = random.randint(1, collection["total_supply"])
        from_addr = self._get_random_wallet()
        to_addr = self._get_random_wallet()
        
        # Ensure from and to are different
        while to_addr == from_addr and len(self.wallets) > 1:
            to_addr = self._get_random_wallet()
        
        return {
            "event_id": f"evt_{self._next_event_id()}",
            "event_type": "TRANSFER",
            "timestamp": self._get_event_timestamp(),
            "collection": {
                "address": collection["contract"],
                "name": collection["name"],
                "symbol": collection["symbol"]
            },
            "token_id": str(token_id),
            "from": from_addr,
            "to": to_addr,
            "tx_hash": f"0x{fake.sha256()}"
        }
    
    def generate_listing_event(self) -> Dict[str, Any]:
        """Generate a fake NFT listing event."""
        collection = self._get_random_collection()
        token_id = random.randint(1, collection["total_supply"])
        
        price = round(random.uniform(
            collection["floor_price"] * 0.9,  
            collection["floor_price"] * 2.0    
        ), 2)
        
        return {
            "event_id": f"evt_{self._next_event_id()}",
            "event_type": "LISTING",
            "timestamp": self._get_event_timestamp(),
            "collection": {
                "address": collection["contract"],
                "name": collection["name"],
                "symbol": collection["symbol"]
            },
            "token_id": str(token_id),
            "seller": self._get_random_wallet(),
            "price_eth": price,
            "marketplace": random.choice(["OpenSea", "LooksRare", "X2Y2", "Blur"]),
            "expiration_days": random.choice([1, 3, 7, 30])
        }
    
    def generate_rarity_update(self) -> Dict[str, Any]:
        """Generate a fake rarity update event."""
        collection = self._get_random_collection()
        token_id = random.randint(1, collection["total_supply"])
        
        return {
            "event_id": f"evt_{self._next_event_id()}",
            "event_type": "RARITY_UPDATE",
            "timestamp": self._get_event_timestamp(),
            "collection": {
                "address": collection["contract"],
                "name": collection["name"],
                "symbol": collection["symbol"]
            },
            "token_id": str(token_id),
            "rarity_score": round(random.uniform(0, 1), 4),
            "rarity_rank": random.randint(1, collection["total_supply"]),
            "traits": self._get_random_traits(collection)
        }
    
    def _next_event_id(self) -> str:
        """Generate the next sequential event ID."""
        self.event_id += 1
        return f"{int(time.time())}_{self.event_id}"
    
    def generate_random_event(self) -> Dict[str, Any]:
        """Generate a random type of NFT event."""
        event_type = random.choices(
            ["MINT", "SALE", "TRANSFER", "LISTING", "RARITY_UPDATE"],
            weights=[0.1, 0.3, 0.3, 0.2, 0.1],  # Relative frequencies
            k=1
        )[0]
        
        if event_type == "MINT":
            return self.generate_mint_event()
        elif event_type == "SALE":
            return self.generate_sale_event()
        elif event_type == "TRANSFER":
            return self.generate_transfer_event()
        elif event_type == "LISTING":
            return self.generate_listing_event()
        else:  # RARITY_UPDATE
            return self.generate_rarity_update()

# Global instance
event_generator = NFTEventGenerator()

async def generate_events_forever(interval: float = 1.0, callback=None):
    """Continuously generate fake NFT events and pass them to a callback."""
    while True:
        try:
            # Randomize interval slightly (0.5x to 1.5x of requested interval)
            actual_interval = interval * random.uniform(0.5, 1.5)
            await asyncio.sleep(actual_interval)
            
            # Generate 1-3 events at a time
            num_events = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
            events = [event_generator.generate_random_event() for _ in range(num_events)]
            
            if callback:
                for event in events:
                    await callback(event)
                    
        except Exception as e:
            logger.error(f"Error in event generation loop: {e}")
            await asyncio.sleep(5)  # Wait before retrying on error
