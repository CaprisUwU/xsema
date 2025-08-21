"""
NFT Models

Defines Pydantic models for NFT-related data structures.
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl, field_validator
from datetime import datetime
from enum import Enum

class NFTStandard(str, Enum):
    """Supported NFT standards"""
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    ERC998 = "erc998"
    OTHER = "other"

class NFTAttribute(BaseModel):
    """Represents an attribute of an NFT."""
    trait_type: str
    value: Union[str, int, float, bool]
    display_type: Optional[str] = None
    max_value: Optional[Union[int, float]] = None
    trait_count: Optional[int] = None
    order: Optional[int] = None

class NFTMetadata(BaseModel):
    """Represents the metadata of an NFT."""
    token_id: str = Field(..., alias="tokenId")
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = Field(None, alias="imageUrl")
    external_url: Optional[HttpUrl] = Field(None, alias="externalUrl")
    animation_url: Optional[HttpUrl] = Field(None, alias="animationUrl")
    attributes: List[NFTAttribute] = []
    background_color: Optional[str] = Field(None, alias="backgroundColor")
    collection: Optional[Dict[str, Any]] = None
    contract: Optional[Dict[str, Any]] = None
    token_standard: Optional[str] = Field(None, alias="tokenStandard")
    owner: Optional[str] = None
    last_updated: Optional[datetime] = Field(None, alias="lastUpdated")

class NFTCreate(BaseModel):
    """Model for creating a new NFT"""
    token_id: str = Field(..., description="Token ID of the NFT")
    contract_address: str = Field(..., description="Smart contract address")
    name: Optional[str] = Field(None, description="Name of the NFT")
    description: Optional[str] = Field(None, description="Description of the NFT")
    image_url: Optional[str] = Field(None, description="URL to the NFT's image")
    external_url: Optional[str] = Field(None, description="External URL for more info")
    animation_url: Optional[str] = Field(None, description="URL to animation or video")
    standard: NFTStandard = Field(NFTStandard.ERC721, description="NFT standard")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Raw metadata as JSON")
    owner_address: Optional[str] = Field(None, description="Current owner's wallet address")
    collection_id: Optional[str] = Field(None, description="ID of the collection this NFT belongs to")

    @field_validator('contract_address')
    @classmethod
    def validate_contract_address(cls, v):
        """Validate contract address format"""
        if not v.startswith('0x') or len(v) != 42:
            raise ValueError("Invalid contract address format")
        return v.lower()

class NFTUpdate(BaseModel):
    """Model for updating an existing NFT"""
    name: Optional[str] = Field(None, description="Updated name of the NFT")
    description: Optional[str] = Field(None, description="Updated description")
    image_url: Optional[str] = Field(None, description="Updated image URL")
    external_url: Optional[str] = Field(None, description="Updated external URL")
    animation_url: Optional[str] = Field(None, description="Updated animation URL")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    owner_address: Optional[str] = Field(None, description="New owner's wallet address")
    is_listed: Optional[bool] = Field(None, description="Whether the NFT is listed for sale")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

class NFTResponse(NFTMetadata):
    """Response model for NFT data"""
    id: str = Field(..., description="Internal ID of the NFT")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    is_verified: bool = Field(False, description="If the NFT has been verified")
    is_listed: bool = Field(False, description="If the NFT is currently listed for sale")

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        },
        "json_schema_extra": {
            "example": {
                "id": "nft_123",
                "token_id": "123",
                "contract_address": "0x1234...",
                "name": "My Awesome NFT",
                "description": "A very special NFT",
                "image_url": "https://example.com/nft.jpg",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "is_verified": True,
                "is_listed": False
            }
        }
    }

class NFTCollection(BaseModel):
    """Represents an NFT collection."""
    address: str
    name: Optional[str] = None
    symbol: Optional[str] = None
    total_supply: Optional[int] = Field(None, alias="totalSupply")
    owner: Optional[str] = None
    description: Optional[str] = None
    external_url: Optional[HttpUrl] = Field(None, alias="externalUrl")
    image_url: Optional[HttpUrl] = Field(None, alias="imageUrl")
    banner_image_url: Optional[HttpUrl] = Field(None, alias="bannerImageUrl")
    created_date: Optional[datetime] = Field(None, alias="createdDate")
    is_verified: Optional[bool] = Field(None, alias="isVerified")
    stats: Optional[Dict[str, Any]] = None
    traits: Optional[Dict[str, List[Dict[str, Any]]]] = None
