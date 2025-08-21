"""
Portfolio Data Models

Defines the core data structures for the Portfolio Management module.
"""
from typing import List, Dict, Optional, Union, Any
from enum import Enum, Enum as StrEnum
from pydantic import BaseModel, Field, field_validator
from pydantic.networks import HttpUrl
from datetime import datetime, timezone
from typing import Literal

class NFTStandard(str, StrEnum):
    """Supported NFT standards"""
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    ERC998 = "erc998"
    OTHER = "other"

class AssetType(str, Enum):
    """Supported asset types in the portfolio"""
    NFT = "nft"
    TOKEN = "token"
    STABLECOIN = "stablecoin"
    DEFI = "defi"

class AssetCreate(BaseModel):
    """Model for creating a new asset"""
    asset_id: str = Field(..., description="Unique identifier for the asset")
    symbol: str = Field(..., description="Asset symbol/ticker")
    name: str = Field(..., description="Asset name")
    type: AssetType = Field(..., description="Type of asset")
    balance: float = Field(0.0, description="Current balance/quantity held")
    avg_buy_price: Optional[float] = Field(None, description="Average purchase price")
    metadata: Dict = Field(default_factory=dict, description="Additional asset metadata")


class Asset(AssetCreate):
    """Base asset model for portfolio items"""
    value_usd: float = Field(0.0, description="Current value in USD")
    pnl: Optional[float] = Field(None, description="Profit/Loss percentage")
    allocation: Optional[float] = Field(None, description="Percentage of total portfolio")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")


class AssetUpdate(BaseModel):
    """Model for updating an existing asset"""
    balance: Optional[float] = Field(None, description="Updated balance/quantity held")
    avg_buy_price: Optional[float] = Field(None, description="Updated average purchase price")
    metadata: Optional[Dict] = Field(None, description="Updated metadata")


class AssetValueHistory(BaseModel):
    """Historical value data points for an asset"""
    timestamp: datetime = Field(..., description="Timestamp of the value record")
    asset_id: str = Field(..., description="ID of the asset")
    price: float = Field(..., description="Price of the asset at the timestamp")
    price_usd: float = Field(..., description="Price in USD at the timestamp")
    market_cap: Optional[float] = Field(None, description="Market capitalization if available")
    total_volume: Optional[float] = Field(None, description="24h trading volume")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AssetPerformance(BaseModel):
    """Performance metrics for an asset over a time period"""
    asset_id: str = Field(..., description="ID of the asset")
    time_period: str = Field(..., description="Time period this performance data covers (e.g., '24h', '7d', '30d', '1y')")
    start_price: float = Field(..., description="Price at the start of the period")
    end_price: float = Field(..., description="Price at the end of the period")
    high_price: float = Field(..., description="Highest price in the period")
    low_price: float = Field(..., description="Lowest price in the period")
    price_change: float = Field(..., description="Absolute price change")
    price_change_pct: float = Field(..., description="Percentage price change")
    volume: float = Field(..., description="Total trading volume in the period")
    start_timestamp: datetime = Field(..., description="Start of the period")
    end_timestamp: datetime = Field(..., description="End of the period")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NFT(BaseModel):
    """Model representing an NFT"""
    id: str = Field(..., description="Unique identifier for the NFT")
    token_id: str = Field(..., description="Token ID on the blockchain")
    contract_address: str = Field(..., description="Smart contract address")
    owner_address: Optional[str] = Field(None, description="Current owner's wallet address")
    name: Optional[str] = Field(None, description="Name of the NFT")
    description: Optional[str] = Field(None, description="Description of the NFT")
    image_url: Optional[str] = Field(None, description="URL to the NFT's image")
    animation_url: Optional[str] = Field(None, description="URL to animation or video")
    external_url: Optional[str] = Field(None, description="External URL for more info")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Complete metadata as a dictionary")
    standard: NFTStandard = Field(NFTStandard.ERC721, description="NFT standard")
    collection_id: Optional[str] = Field(None, description="ID of the collection this NFT belongs to")
    last_sale_price: Optional[float] = Field(None, description="Last sale price in native token")
    last_sale_price_usd: Optional[float] = Field(None, description="Last sale price in USD")
    last_sale_at: Optional[datetime] = Field(None, description="When the last sale occurred")
    is_listed: bool = Field(False, description="Whether the NFT is currently listed for sale")
    is_nsfw: bool = Field(False, description="Whether the NFT contains NSFW content")
    is_verified: bool = Field(False, description="Whether the NFT is verified by the platform")
    rarity_rank: Optional[int] = Field(None, description="Rarity rank in the collection")
    rarity_score: Optional[float] = Field(None, description="Rarity score (0-1)")
    traits: List[Dict[str, Any]] = Field(default_factory=list, description="Traits and attributes")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NFTMetadata(BaseModel):
    """Model for NFT metadata"""
    token_id: str = Field(..., description="Unique token ID")
    contract_address: str = Field(..., description="Smart contract address")
    name: Optional[str] = Field(None, description="NFT name")
    description: Optional[str] = Field(None, description="NFT description")
    image_url: Optional[str] = Field(None, description="URL to the NFT image")
    external_url: Optional[str] = Field(None, description="External URL for more info")
    attributes: List[Dict[str, Any]] = Field(default_factory=list, description="NFT attributes")
    collection_name: Optional[str] = Field(None, description="Name of the NFT collection")
    collection_image_url: Optional[str] = Field(None, description="URL to the collection image")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")


class NFTCollection(BaseModel):
    """Model for an NFT collection"""
    id: str = Field(..., description="Unique identifier for the collection (contract address)")
    name: str = Field(..., description="Name of the collection")
    symbol: str = Field(..., description="Symbol/ticker of the collection")
    contract_address: str = Field(..., description="Contract address of the collection")
    standard: NFTStandard = Field(NFTStandard.ERC721, description="NFT standard of the collection")
    description: Optional[str] = Field(None, description="Description of the collection")
    external_url: Optional[HttpUrl] = Field(None, description="External URL for the collection")
    image_url: Optional[HttpUrl] = Field(None, description="URL of the collection's image/logo")
    banner_image_url: Optional[HttpUrl] = Field(None, description="URL of the collection's banner image")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When the collection was created")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When the collection was last updated")
    
    one_day_volume: Optional[float] = Field(None, description="24h trading volume in native token")
    one_day_volume_usd: Optional[float] = Field(None, description="24h trading volume in USD")
    one_day_change: Optional[float] = Field(None, description="24h price change percentage")
    one_day_sales: Optional[int] = Field(None, description="Number of sales in the last 24h")
    one_day_average_price: Optional[float] = Field(None, description="Average sale price in the last 24h")
    seven_day_volume: Optional[float] = Field(None, description="7d trading volume in native token")
    seven_day_volume_usd: Optional[float] = Field(None, description="7d trading volume in USD")
    seven_day_change: Optional[float] = Field(None, description="7d price change percentage")
    seven_day_sales: Optional[int] = Field(None, description="Number of sales in the last 7d")
    seven_day_average_price: Optional[float] = Field(None, description="Average sale price in the last 7d")
    thirty_day_volume: Optional[float] = Field(None, description="30d trading volume in native token")
    thirty_day_volume_usd: Optional[float] = Field(None, description="30d trading volume in USD")
    thirty_day_change: Optional[float] = Field(None, description="30d price change percentage")
    thirty_day_sales: Optional[int] = Field(None, description="Number of sales in the last 30d")
    total_volume: Optional[float] = Field(None, description="All-time trading volume in native token")
    total_volume_usd: Optional[float] = Field(None, description="All-time trading volume in USD")
    total_sales: Optional[int] = Field(None, description="All-time number of sales")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @property
    def average_price(self) -> Optional[float]:
        """Calculate average price based on total volume and sales"""
        if self.total_volume is not None and self.total_sales and self.total_sales > 0:
            return self.total_volume / self.total_sales
        return None

class WalletCreate(BaseModel):
    """Model for creating a new wallet"""
    address: str = Field(..., description="Wallet address")
    chain: str = Field(..., description="Blockchain network")
    name: Optional[str] = Field(None, description="User-defined name for the wallet")
    is_primary: bool = Field(False, description="Whether this is the user's primary wallet")


class Wallet(WalletCreate):
    """Blockchain wallet model"""
    id: str = Field(..., description="Unique wallet identifier")
    assets: List[Asset] = Field(default_factory=list, description="Assets in this wallet")
    is_connected: bool = Field(False, description="If the wallet is currently connected")
    last_synced: Optional[datetime] = Field(None, description="Last sync timestamp")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WalletUpdate(BaseModel):
    """Model for updating an existing wallet"""
    name: Optional[str] = Field(None, description="Updated name for the wallet")
    is_primary: Optional[bool] = Field(None, description="Whether this is the user's primary wallet")


class WalletBalance(BaseModel):
    """Model representing a wallet's balance information"""
    wallet_id: str = Field(..., description="Unique identifier for the wallet")
    address: str = Field(..., description="Wallet address")
    chain: str = Field(..., description="Blockchain network the wallet is on")
    native_balance: float = Field(..., description="Native token balance (e.g., ETH, MATIC)")
    native_balance_usd: float = Field(..., description="Value of native token balance in USD")
    token_balances: Dict[str, float] = Field(
        default_factory=dict,
        description="Dictionary of token addresses to their respective balances"
    )
    nft_count: int = Field(0, description="Number of NFTs in the wallet")
    total_value_usd: float = Field(..., description="Total value of all assets in USD")
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of when the balance was last updated"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PortfolioCreate(BaseModel):
    """Model for creating a new portfolio"""
    user_id: str = Field(..., description="Owner of the portfolio")
    name: str = Field(..., description="Name of the portfolio")
    description: Optional[str] = Field(None, description="Optional portfolio description")
    risk_tolerance: float = Field(0.5, ge=0.0, le=1.0, description="User's risk tolerance (0-1)")


class Portfolio(PortfolioCreate):
    """User portfolio model"""
    id: str = Field(..., description="Unique portfolio identifier")
    wallets: List[Wallet] = Field(default_factory=list, description="Connected wallets")
    total_value: float = Field(0.0, description="Total portfolio value in USD")
    risk_score: Optional[float] = Field(None, description="Overall portfolio risk score (0-1)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioUpdate(BaseModel):
    """Model for updating an existing portfolio"""
    name: Optional[str] = Field(None, description="Updated portfolio name")
    description: Optional[str] = Field(None, description="Updated portfolio description")
    risk_tolerance: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0, 
        description="Updated risk tolerance (0-1)"
    )
    
    def add_wallet(self, wallet: Wallet):
        """Add a wallet to the portfolio"""
        self.wallets.append(wallet)
        self.updated_at = datetime.now(timezone.utc)
    
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Get an asset by ID across all wallets"""
        for wallet in self.wallets:
            for asset in wallet.assets:
                if asset.asset_id == asset_id:
                    return asset
        return None

class RecommendationType(str, Enum):
    """Types of AI-generated recommendations"""
    REBALANCE = "rebalance"
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    RISK = "risk"

class Recommendation(BaseModel):
    """AI-generated recommendation model"""
    type: RecommendationType
    asset_id: str
    current_value: Optional[float] = None
    suggested_value: Optional[float] = None
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score (0-1)")
    reasons: List[str] = Field(default_factory=list, description="Explanation for the recommendation")
    priority: int = Field(1, ge=1, le=5, description="Priority level (1-5)")
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TransactionType(StrEnum):
    """Types of transactions that can be performed on assets"""
    BUY = "buy"
    SELL = "sell"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    AIRDROP = "airdrop"
    REWARD = "reward"
    STAKING = "staking"
    MINT = "mint"
    BURN = "burn"
    LIST = "list"
    UNLIST = "unlist"
    BID = "bid"
    CANCEL_BID = "cancel_bid"
    ACCEPT_BID = "accept_bid"
    OTHER = "other"


class TransactionStatus(str, StrEnum):
    """Possible statuses for a transaction"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Transaction(BaseModel):
    """Model representing a single transaction of an asset"""
    id: str = Field(..., description="Unique transaction identifier")
    wallet_id: str = Field(..., description="ID of the wallet this transaction belongs to")
    asset_id: str = Field(..., description="ID of the asset being transacted")
    type: TransactionType = Field(..., description="Type of transaction")
    status: TransactionStatus = Field(default=TransactionStatus.COMPLETED, description="Current status of the transaction")
    
    # Transaction details
    quantity: float = Field(..., description="Amount of the asset transacted")
    price_per_unit: Optional[float] = Field(None, description="Price per unit at time of transaction (in USD)")
    total_value: Optional[float] = Field(None, description="Total value of the transaction (in USD)")
    fee: float = Field(0.0, description="Transaction fee (in USD)")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When the transaction occurred")
    processed_at: Optional[datetime] = Field(None, description="When the transaction was processed")
    
    # Additional metadata
    tx_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    source: Optional[str] = Field(None, description="Source of the transaction (e.g., exchange name, wallet address)")
    destination: Optional[str] = Field(None, description="Destination of the transaction")
    notes: Optional[str] = Field(None, description="Any additional notes about the transaction")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional transaction metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @field_validator('total_value', mode='before')
    @classmethod
    def calculate_total_value(cls, v, info):
        """Calculate total value if not provided"""
        if v is None and hasattr(info, 'data'):
            data = info.data
            if 'quantity' in data and 'price_per_unit' in data:
                if data['quantity'] is not None and data['price_per_unit'] is not None:
                    return data['quantity'] * data['price_per_unit']
        return v


class TransactionCreate(BaseModel):
    """Model for creating a new transaction"""
    wallet_id: str = Field(..., description="ID of the wallet this transaction belongs to")
    asset_id: str = Field(..., description="ID of the asset being transacted")
    type: TransactionType = Field(..., description="Type of transaction")
    quantity: float = Field(..., description="Amount of the asset transacted")
    price_per_unit: Optional[float] = Field(None, description="Price per unit at time of transaction (in USD)")
    fee: float = Field(0.0, description="Transaction fee (in USD)")
    tx_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    source: Optional[str] = Field(None, description="Source of the transaction")
    destination: Optional[str] = Field(None, description="Destination of the transaction")
    notes: Optional[str] = Field(None, description="Any additional notes about the transaction")


class TransactionUpdate(BaseModel):
    """Model for updating an existing transaction"""
    status: Optional[TransactionStatus] = Field(None, description="Updated transaction status")
    price_per_unit: Optional[float] = Field(None, description="Updated price per unit (in USD)")
    fee: Optional[float] = Field(None, description="Updated transaction fee (in USD)")
    notes: Optional[str] = Field(None, description="Updated notes about the transaction")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated transaction metadata")


class NFTTransfer(BaseModel):
    """Model representing an NFT transfer event"""
    id: str = Field(..., description="Unique identifier for the transfer")
    token_id: str = Field(..., description="Token ID of the NFT")
    contract_address: str = Field(..., description="Smart contract address of the NFT")
    from_address: str = Field(..., description="Sender's wallet address")
    to_address: str = Field(..., description="Recipient's wallet address")
    transaction_hash: str = Field(..., description="Blockchain transaction hash")
    block_number: int = Field(..., description="Block number of the transfer")
    block_timestamp: datetime = Field(..., description="Timestamp of the block")
    value: Optional[float] = Field(None, description="Value transferred in native token")
    value_usd: Optional[float] = Field(None, description="Value transferred in USD")
    log_index: int = Field(..., description="Index of the log in the transaction")
    confirmed: bool = Field(True, description="Whether the transfer is confirmed on-chain")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NFTAttribute(BaseModel):
    """Model for NFT attributes (alias for NFTTrait for compatibility)"""
    trait_type: str = Field(..., description="Type of the attribute")
    value: Union[str, int, float, bool] = Field(..., description="Value of the attribute")
    display_type: Optional[str] = Field(None, description="How the attribute should be displayed")
    max_value: Optional[float] = Field(None, description="Maximum value for numerical attributes")
    trait_count: Optional[int] = Field(None, description="Number of items with this attribute")
    rarity: Optional[float] = Field(None, description="Rarity score of this attribute (0-1)")
    frequency: Optional[float] = Field(None, description="Frequency of this attribute in the collection")

# Alias for backward compatibility
NFTTrait = NFTAttribute

class NFTCreate(BaseModel):
    """Model for creating a new NFT"""
    token_id: str = Field(..., description="Token ID on the blockchain")
    contract_address: str = Field(..., description="Smart contract address")
    owner_address: Optional[str] = Field(None, description="Current owner's wallet address")
    name: Optional[str] = Field(None, description="Name of the NFT")
    description: Optional[str] = Field(None, description="Description of the NFT")
    image_url: Optional[str] = Field(None, description="URL to the NFT's image")
    animation_url: Optional[str] = Field(None, description="URL to animation or video")
    external_url: Optional[str] = Field(None, description="External URL for more info")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Complete metadata as a dictionary")
    standard: NFTStandard = Field(NFTStandard.ERC721, description="NFT standard")
    collection_id: Optional[str] = Field(None, description="ID of the collection this NFT belongs to")
    last_sale_price: Optional[float] = Field(None, description="Last sale price in native token")
    last_sale_price_usd: Optional[float] = Field(None, description="Last sale price in USD")
    last_sale_at: Optional[datetime] = Field(None, description="When the last sale occurred")
    is_listed: bool = Field(False, description="Whether the NFT is currently listed for sale")
    is_nsfw: bool = Field(False, description="Whether the NFT contains NSFW content")
    is_verified: bool = Field(False, description="Whether the NFT is verified by the platform")
    rarity_rank: Optional[int] = Field(None, description="Rarity rank in the collection")
    rarity_score: Optional[float] = Field(None, description="Rarity score (0-1)")
    traits: List[Dict[str, Any]] = Field(default_factory=list, description="Traits and attributes")

class NFTUpdate(BaseModel):
    """Model for updating an existing NFT"""
    owner_address: Optional[str] = Field(None, description="Updated owner's wallet address")
    name: Optional[str] = Field(None, description="Updated name of the NFT")
    description: Optional[str] = Field(None, description="Updated description of the NFT")
    image_url: Optional[str] = Field(None, description="Updated URL to the NFT's image")
    animation_url: Optional[str] = Field(None, description="Updated URL to animation or video")
    external_url: Optional[str] = Field(None, description="Updated external URL for more info")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata as a dictionary")
    last_sale_price: Optional[float] = Field(None, description="Updated last sale price in native token")
    last_sale_price_usd: Optional[float] = Field(None, description="Updated last sale price in USD")
    last_sale_at: Optional[datetime] = Field(None, description="Updated timestamp of the last sale")
    is_listed: Optional[bool] = Field(None, description="Whether the NFT is currently listed for sale")
    is_nsfw: Optional[bool] = Field(None, description="Whether the NFT contains NSFW content")
    is_verified: Optional[bool] = Field(None, description="Whether the NFT is verified by the platform")
    rarity_rank: Optional[int] = Field(None, description="Updated rarity rank in the collection")
    rarity_score: Optional[float] = Field(None, description="Updated rarity score (0-1)")
    traits: Optional[List[Dict[str, Any]]] = Field(None, description="Updated traits and attributes")

class NFTResponse(NFT):
    """Response model for NFT with additional fields"""
    collection: Optional[NFTCollection] = Field(None, description="Collection details")
    attributes: List[NFTAttribute] = Field(default_factory=list, description="Detailed attributes")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    is_favorite: bool = Field(False, description="Whether the NFT is marked as favorite by the user")


class NFTCollectionResponse(BaseModel):
    """Response model for NFT collection information"""
    id: str = Field(..., description="Unique identifier for the collection")
    name: str = Field(..., description="Name of the collection")
    symbol: str = Field(..., description="Symbol/ticker of the collection")
    contract_address: str = Field(..., description="Contract address of the collection")
    nft_count: int = Field(0, description="Number of NFTs in the collection")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When the collection was created")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When the collection was last updated")


class NFTMetadata(BaseModel):
    """Model for NFT metadata"""
    name: Optional[str] = Field(None, description="Name of the NFT")
    description: Optional[str] = Field(None, description="Description of the NFT")
    image: Optional[str] = Field(None, description="URL to the NFT's image")
    image_url: Optional[str] = Field(None, alias="image_url", description="URL to the NFT's image (alternative field)")
    image_data: Optional[str] = Field(None, description="Raw image data (base64)")
    external_url: Optional[str] = Field(None, description="External URL for more information")
    animation_url: Optional[str] = Field(None, description="URL to an animation or video")
    youtube_url: Optional[str] = Field(None, description="URL to a YouTube video")
    background_color: Optional[str] = Field(None, description="Background color as a hex code")
    attributes: List[NFTTrait] = Field(default_factory=list, description="Traits and attributes")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    token_id: Optional[str] = Field(None, description="Token ID as a string")
    collection: Optional[Dict[str, Any]] = Field(None, description="Collection information")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PortfolioInsights(BaseModel):
    """AI-generated insights about a portfolio"""
    portfolio_id: str
    risk_assessment: Dict
    opportunities: List[Recommendation]
    warnings: List[Recommendation]
    market_conditions: Dict
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "portfolio_id": self.portfolio_id,
            "risk_assessment": self.risk_assessment,
            "opportunities": [rec.dict() for rec in self.opportunities],
            "warnings": [rec.dict() for rec in self.warnings],
            "market_conditions": self.market_conditions,
            "generated_at": self.generated_at.isoformat()
        }
