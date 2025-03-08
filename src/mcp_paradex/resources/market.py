"""
Market data resources that don't require authentication.
"""
from typing import Dict, Any, List
import logging
from datetime import datetime

from mcp_paradex.server.server import server
from mcp_paradex.utils.config import config
from mcp_paradex.utils.paradex_client import get_paradex_client

logger = logging.getLogger(__name__)

@server.resource("paradex://markets")
async def get_markets() -> Dict[str, Any]:
    """
    Get a list of available markets from Paradex.
    
    This endpoint doesn't require authentication and provides basic
    information about available trading pairs.
    
    Returns:
        Dict[str, Any]: List of available markets.
    """
    try:
        client = await get_paradex_client()
        markets = client.fetch_markets()
        
        # Format the response
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "markets": markets,
            "count": len(markets)
        }
    except Exception as e:
        logger.error(f"Error fetching markets: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "markets": [],
            "count": 0
        }

@server.resource("paradex://market/summary/{market_id}")
async def get_market_summary(market_id: str) -> Dict[str, Any]:
    """
    Get a summary of market information for a specific trading pair.
    
    This endpoint requires authentication and provides detailed
    information about the market, including order book, ticker, and
    market statistics.
    
    Args:
        market_id (str): The ID of the trading pair to get summary for.
        
    Returns:
        Dict[str, Any]: Summary of market information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        summary = client.fetch_markets_summary(params={"market": market_id})
        return summary
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "summary": None
        }
