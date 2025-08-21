"""
NFT API Endpoints

Handles NFT-related operations including collection and metadata retrieval.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Path, Depends, Body, Query
from pydantic import BaseModel

from portfolio.services.portfolio_service import PortfolioService
from portfolio.services.analytics_service import AnalyticsService

# Create a router for NFT endpoints
router = APIRouter(tags=["nfts"])

# Initialize services
portfolio_service = PortfolioService()
analytics_service = AnalyticsService()

# Temporary in-memory storage for testing
# Structure: {portfolio_id: {nft_id: nft_data}}
nfts_store = {}
collections_store = {}

# Helper function to get current user (stub for now)
async def get_current_user():
    return {"id": "test-user-1", "email": "test@example.com"}

# Models
class NFTResponse(BaseModel):
    id: str
    name: str
    description: str
    image_url: str
    collection_id: str
    token_id: str
    owner_address: str
    contract_address: str
    metadata: Dict[str, Any] = {}
    created_at: str = "2023-01-01T00:00:00Z"
    updated_at: str = "2023-01-01T00:00:00Z"
    is_verified: bool = False
    is_listed: bool = False

class NFTCreate(BaseModel):
    name: str
    description: str
    image_url: str
    collection_id: str
    token_id: str
    owner_address: str
    contract_address: str
    metadata: Dict[str, Any] = {}
    external_url: Optional[str] = None
    animation_url: Optional[str] = None
    standard: str = "erc721"

class NFTUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    owner_address: Optional[str] = None

class NFTCollection(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    contract_address: str
    chain: str = "ethereum"
    total_supply: Optional[int] = None
    owner_count: Optional[int] = None
    total_volume: Optional[float] = None
    floor_price: Optional[float] = None
    created_at: str = "2023-01-01T00:00:00Z"
    updated_at: str = "2023-01-01T00:00:00Z"
    metadata: Dict[str, Any] = {}

class NFTCollectionResponse(NFTCollection):
    pass

class NFTMetadata(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    animation_url: Optional[str] = None
    external_url: Optional[str] = None
    attributes: List[Dict[str, Any]] = []
    properties: Dict[str, Any] = {}
    contract_address: str
    token_id: str
    chain: str = "ethereum"
    owner_address: Optional[str] = None
    created_at: str = "2023-01-01T00:00:00Z"
    updated_at: str = "2023-01-01T00:00:00Z"
    metadata: Dict[str, Any] = {}

# Test data
test_nft = {
    "id": "test-nft-1",
    "name": "Test NFT",
    "description": "A test NFT",
    "image_url": "https://example.com/test-nft.jpg",
    "collection_id": "test-collection-1",
    "token_id": "1",
    "owner_address": "0x1234567890abcdef1234567890abcdef12345678",
    "contract_address": "0xabcdef1234567890abcdef1234567890abcdef12",
    "metadata": {"test": "data"},
    "is_verified": False,
    "is_listed": False
}

# Initialize test data
if "test-portfolio-1" not in nfts_store:
    nfts_store["test-portfolio-1"] = {"test-nft-1": test_nft}

# NFT Endpoints
@router.get(
    "",
    response_model=List[NFTResponse],
    summary="List all NFTs in a portfolio",
    status_code=status.HTTP_200_OK
)
async def list_nfts(
    portfolio_id: str = Path(..., description="The ID of the portfolio"),
    current_user: dict = Depends(get_current_user)
):
    """List all NFTs in a portfolio"""
    # Return empty list if portfolio doesn't exist or has no NFTs
    if portfolio_id not in nfts_store or not nfts_store[portfolio_id]:
        return []
    return list(nfts_store[portfolio_id].values())

@router.post(
    "",
    response_model=NFTResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new NFT"
)
async def create_nft(
    portfolio_id: str = Path(..., description="The ID of the portfolio"),
    nft: NFTCreate = Body(..., description="NFT data to create"),
    current_user: dict = Depends(get_current_user)
) -> NFTResponse:
    """Create a new NFT"""
    # Initialize portfolio in store if it doesn't exist
    if portfolio_id not in nfts_store:
        nfts_store[portfolio_id] = {}
    
    # Create NFT ID and add to store
    nft_id = f"nft-{str(uuid4())}"
    now = datetime.utcnow().isoformat()
    
    nft_data = {
        "id": nft_id,
        **nft.dict(),
        "created_at": now,
        "updated_at": now,
        "is_verified": False,
        "is_listed": False
    }
    
    nfts_store[portfolio_id][nft_id] = nft_data
    
    return nft_data

@router.get(
    "/{nft_id}",
    response_model=NFTResponse,
    summary="Get NFT details"
)
async def get_nft(
    portfolio_id: str = Path(..., description="The ID of the portfolio"),
    nft_id: str = Path(..., description="The ID of the NFT"),
    current_user: dict = Depends(get_current_user)
) -> NFTResponse:
    """Get details of a specific NFT"""
    if (portfolio_id not in nfts_store or 
        nft_id not in nfts_store[portfolio_id]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NFT not found"
        )
    return nfts_store[portfolio_id][nft_id]

@router.put(
    "/{nft_id}",
    response_model=NFTResponse,
    summary="Update an NFT"
)
async def update_nft(
    portfolio_id: str = Path(..., description="The ID of the portfolio"),
    nft_id: str = Path(..., description="The ID of the NFT"),
    nft_update: NFTUpdate = Body(..., description="NFT data to update"),
    current_user: dict = Depends(get_current_user)
) -> NFTResponse:
    """
    Update an existing NFT
    
    This endpoint updates the specified NFT with the provided data.
    """
    if (portfolio_id not in nfts_store or 
        nft_id not in nfts_store[portfolio_id]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NFT not found"
        )
    
    # Get the existing NFT
    nft = nfts_store[portfolio_id][nft_id]
    
    # Update fields if provided
    update_data = nft_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            nft[field] = value
    
    # Update timestamp
    nft["updated_at"] = datetime.utcnow().isoformat()
    
    # Update the NFT in the store
    nfts_store[portfolio_id][nft_id] = nft
    
    return nft

@router.delete(
    "/{nft_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an NFT"
)
async def delete_nft(
    portfolio_id: str = Path(..., description="The ID of the portfolio"),
    nft_id: str = Path(..., description="The ID of the NFT"),
    current_user: dict = Depends(get_current_user)
):
    """Delete an NFT"""
    if (portfolio_id not in nfts_store or 
        nft_id not in nfts_store[portfolio_id]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NFT not found"
        )
    
    # Remove the NFT from the store
    del nfts_store[portfolio_id][nft_id]
    
    # Clean up empty portfolio entries
    if not nfts_store[portfolio_id]:
        del nfts_store[portfolio_id]
        
    return {"status": "success", "message": "NFT deleted"}

@router.post(
    "/{nft_id}/refresh",
    response_model=NFTResponse,
    summary="Refresh NFT metadata"
)
async def refresh_nft_metadata(
    portfolio_id: str = Path(..., description="The ID of the portfolio"),
    nft_id: str = Path(..., description="The ID of the NFT"),
    current_user: dict = Depends(get_current_user)
) -> NFTResponse:
    """
    Refresh NFT metadata
    
    This endpoint refreshes the metadata for the specified NFT.
    """
    try:
        if nft_id not in nft_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NFT not found"
            )
        
        # In a real app, this would fetch fresh metadata from the blockchain
        nft = nft_store[nft_id]
        nft['updated_at'] = datetime.utcnow().isoformat()
        nft_store[nft_id] = nft
        
        return nft
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing NFT metadata: {str(e)}"
        )

# NFT Collection and Metadata Endpoints
@router.get(
    "/collections",
    response_model=List[NFTCollectionResponse],
    summary="List all NFT collections in a portfolio"
)
async def get_nft_collections(
    portfolio_id: str = Path(..., description="The ID of the portfolio"),
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get all NFT collections in a portfolio
    
    This endpoint returns a list of all NFT collections in the specified portfolio.
    """
    try:
        # In a real app, this would query the database
        collections = [
            {
                "id": col_id,
                "name": col_data.get('name', 'Unnamed Collection'),
                "symbol": col_data.get('symbol', ''),
                "contract_address": col_data.get('contract_address', ''),
                "nft_count": len(col_data.get('nft_ids', [])),
                "created_at": col_data.get('created_at', datetime.utcnow().isoformat()),
                "updated_at": col_data.get('updated_at', datetime.utcnow().isoformat())
            }
            for col_id, col_data in collection_store.items()
        ]
        return collections
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving NFT collections: {str(e)}"
        )

@router.get(
    "/collections/{collection_id}",
    response_model=NFTCollectionResponse,
    summary="Get details of an NFT collection"
)
async def get_nft_collection(
    portfolio_id: str = Path(..., description="The ID of the portfolio"),
    collection_id: str = Path(..., description="The ID of the collection"),
    current_user: dict = Depends(get_current_user)
) -> NFTCollectionResponse:
    """
    Get details of a specific NFT collection
    
    This endpoint returns the details of the specified NFT collection.
    """
    try:
        if collection_id not in collection_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )
        
        col_data = collection_store[collection_id]
        return NFTCollectionResponse(
            id=collection_id,
            name=col_data.get('name', 'Unnamed Collection'),
            symbol=col_data.get('symbol', ''),
            contract_address=col_data.get('contract_address', ''),
            nft_count=len(col_data.get('nft_ids', [])),
            created_at=col_data.get('created_at', datetime.utcnow().isoformat()),
            updated_at=col_data.get('updated_at', datetime.utcnow().isoformat())
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving NFT collection: {str(e)}"
        )

@router.get(
    "/portfolios/{portfolio_id}/nft/{nft_id}/rarity",
    response_model=Dict[str, Any],
    summary="Get NFT rarity information"
)
async def get_nft_rarity(
    portfolio_id: str = Path(..., description="The ID of the portfolio"),
    nft_id: str = Path(..., description="The ID of the NFT"),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get NFT rarity information
    
    This endpoint returns rarity information for the specified NFT.
    """
    try:
        if nft_id not in nft_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NFT not found"
            )
        
        # In a real app, this would calculate actual rarity scores
        return {
            "score": 0.95,
            "rank": 1,
            "total": 100,
            "traits": [
                {"trait_type": "Background", "value": "Blue", "rarity": 0.05},
                {"trait_type": "Rarity", "value": "Legendary", "rarity": 0.01}
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving NFT rarity: {str(e)}"
        )

@router.get(
    "/nfts/collections",
    response_model=List[NFTCollection],
    summary="Get NFT collections by owner"
)
async def get_nft_collections(
    portfolio_id: str,
    owner: str = Query(..., description="Wallet address to query"),
    chain: str = Query('ethereum', description="Blockchain network"),
    with_metadata: bool = Query(True, description="Include collection metadata"),
    current_user: dict = Depends(get_current_user)
) -> List[NFTCollection]:
    """
    Get all NFT collections owned by a wallet address
    """
    try:
        return await nft_service.get_nft_collections(
            owner=owner,
            chain=chain,
            with_metadata=with_metadata
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting NFT collections: {str(e)}"
        )

@router.get(
    "/nfts/collections/{contract_address}",
    response_model=NFTCollection,
    summary="Get NFT collection details"
)
async def get_nft_collection(
    portfolio_id: str,
    contract_address: str,
    chain: str = Query('ethereum', description="Blockchain network"),
    current_user: dict = Depends(get_current_user)
) -> NFTCollection:
    """
    Get details of a specific NFT collection
    """
    try:
        # Get collection metadata
        metadata = await nft_service.get_contract_metadata(
            contract_address=contract_address,
            chain=chain
        )
        
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )
        
        # Get NFTs in the collection
        nfts = await nft_service.get_nfts_for_collection(
            contract_address=contract_address,
            chain=chain,
            with_metadata=True
        )
        
        # Get floor price if available
        floor_price = await price_service.get_nft_floor_price(
            collection_slug=metadata.get('slug', '')
        )
        
        return NFTCollection(
            address=contract_address,
            name=metadata.get('name', 'Unnamed Collection'),
            symbol=metadata.get('symbol', ''),
            description=metadata.get('description', ''),
            image_url=metadata.get('image_url', ''),
            banner_image_url=metadata.get('banner_image_url', ''),
            external_url=metadata.get('external_url', ''),
            twitter_username=metadata.get('twitter_username', ''),
            discord_url=metadata.get('discord_url', ''),
            total_supply=metadata.get('total_supply'),
            nfts=nfts,
            floor_price=floor_price,
            chain=chain,
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting NFT collection: {str(e)}"
        )

@router.get(
    "/nfts/collections/{contract_address}/nfts",
    response_model=List[NFTMetadata],
    summary="Get NFTs in a collection"
)
async def get_nfts_in_collection(
    portfolio_id: str,
    contract_address: str,
    chain: str = Query('ethereum', description="Blockchain network"),
    limit: int = Query(100, description="Maximum number of NFTs to return"),
    current_user: dict = Depends(get_current_user)
) -> List[NFTMetadata]:
    """
    Get all NFTs in a collection
    """
    try:
        return await nft_service.get_nfts_for_collection(
            contract_address=contract_address,
            chain=chain,
            limit=limit,
            with_metadata=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting NFTs in collection: {str(e)}"
        )

@router.get(
    "/nfts/{contract_address}/{token_id}",
    response_model=NFTMetadata,
    summary="Get NFT metadata"
)
async def get_nft_metadata(
    portfolio_id: str,
    contract_address: str,
    token_id: str,
    chain: str = Query('ethereum', description="Blockchain network"),
    current_user: dict = Depends(get_current_user)
) -> NFTMetadata:
    """
    Get metadata for a specific NFT
    """
    try:
        metadata = await nft_service.get_nft_metadata(
            contract_address=contract_address,
            token_id=token_id,
            chain=chain
        )
        
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NFT not found"
            )
            
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting NFT metadata: {str(e)}"
        )

@router.get(
    "/nfts/owners/{contract_address}/{token_id}",
    summary="Get NFT ownership information"
)
async def get_nft_owners(
    portfolio_id: str,
    contract_address: str,
    token_id: Optional[str] = None,
    chain: str = Query('ethereum', description="Blockchain network"),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get ownership information for an NFT or collection
    """
    try:
        # This is a simplified example - in a real app, you'd query the blockchain
        # or an indexer for ownership data
        if token_id:
            # Get single NFT owner
            return {
                "contract_address": contract_address,
                "token_id": token_id,
                "owners": [
                    {
                        "address": "0x...",  # Owner's address
                        "quantity": 1,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                ],
                "chain": chain,
                "last_updated": datetime.utcnow().isoformat()
            }
        else:
            # Get all owners in collection (pagination would be needed in a real app)
            return {
                "contract_address": contract_address,
                "owners": [
                    {
                        "address": "0x...",
                        "tokens_owned": ["1", "2", "3"],
                        "quantity": 3,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                ],
                "chain": chain,
                "total_owners": 1,
                "last_updated": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting NFT owners: {str(e)}"
        )

@router.get(
    "/nfts/search",
    summary="Search for NFTs"
)
async def search_nfts(
    portfolio_id: str,
    query: str = Query(..., description="Search query"),
    chain: str = Query('ethereum', description="Blockchain network"),
    limit: int = Query(10, description="Maximum number of results"),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Search for NFTs by name, description, or attributes
    """
    try:
        # This is a simplified example - in a real app, you'd use a search index
        # or query an NFT API with search capabilities
        return {
            "query": query,
            "results": [
                {
                    "contract_address": "0x...",
                    "token_id": "123",
                    "name": f"Matching NFT for {query}",
                    "description": f"This NFT matches your search for {query}",
                    "image_url": "https://example.com/nft.jpg",
                    "chain": chain
                }
            ],
            "total": 1,
            "chain": chain,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error searching NFTs: {str(e)}"
        )
