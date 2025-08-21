"""
Market Endpoints

Provides endpoints for market data and analysis.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from utils.market import NFTMarketAnalyzer, get_trade_history, get_price_data

router = APIRouter()

# Initialize market analyzer
market_analyzer = NFTMarketAnalyzer(mock_mode=True)  # Set to False for production

@router.get("/summary")
async def market_summary(timeframe: str = "24h"):
    """
    Get overall market summary.
    
    Args:
        timeframe: Time window for summary (1h, 24h, 7d, 30d)
    """
    try:
        # Convert timeframe to days for the API
        timeframe_days = {
            "1h": 1/24,
            "24h": 1,
            "7d": 7,
            "30d": 30
        }.get(timeframe.lower(), 1)  # Default to 1 day if invalid
        
        # Get price data for a default collection (in a real app, you'd aggregate across multiple)
        # This is a simplified example - you'd want to aggregate across multiple collections
        default_collection = "0x0000000000000000000000000000000000000000"  # Replace with actual default
        price_data = get_price_data(default_collection, days=timeframe_days)
        
        # Calculate basic stats
        if price_data and 'prices' in price_data and price_data['prices']:
            prices = price_data['prices']
            volume = sum(trade['price'] * trade['amount'] for trade in price_data.get('trades', []))
            price_change = ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] > 0 else 0
            
            summary = {
                "timeframe": timeframe,
                "floor_price": min(prices) if prices else 0,
                "average_price": sum(prices) / len(prices) if prices else 0,
                "volume": volume,
                "sales_count": len(price_data.get('trades', [])),
                "price_change_percent": price_change,
                "collection_count": 1,  # In a real app, count actual collections
                "unique_traders": len(set(trade['from'] for trade in price_data.get('trades', [])))
            }
            
            return {
                "status": "success",
                "data": summary
            }
        else:
            return {
                "status": "success",
                "data": {
                    "timeframe": timeframe,
                    "message": "No data available for the specified timeframe"
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch market summary: {str(e)}"
        )

@router.get("/collections/trending")
async def trending_collections(
    timeframe: str = "24h",
    limit: int = 10,
    category: Optional[str] = None
):
    """
    Get trending collections.
    
    Args:
        timeframe: Time window for trending (1h, 24h, 7d)
        limit: Maximum number of collections to return
        category: Optional category filter
    """
    try:
        collections = await get_trending_collections(timeframe, limit, category)
        return {
            "timeframe": timeframe,
            "limit": limit,
            "category": category,
            "collections": collections,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/gas")
async def gas_prices():
    """
    Get current gas prices.
    """
    # TODO: Implement actual gas price fetching
    return {
        "fast": 0,
        "standard": 0,
        "slow": 0,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/mints/recent")
async def recent_mints(limit: int = 20):
    """
    Get recent NFT mints across all collections.
    """
    # TODO: Implement actual mint tracking
    return {
        "mints": [],
        "count": 0,
        "limit": limit,
        "timestamp": datetime.utcnow().isoformat()
    }
