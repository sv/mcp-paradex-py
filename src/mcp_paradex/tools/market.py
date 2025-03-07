"""
Market data resources that don't require authentication.
"""
from typing import Dict, Any, List
import logging
from datetime import datetime

from mcp_paradex.server.server import server
from mcp_paradex.utils.config import config
from mcp_paradex.utils.paradex_client import get_paradex_client, api_call

logger = logging.getLogger(__name__)


@server.tool("paradex-market-names")
async def get_market_names() -> Dict[str, Any]:
    """
    Get a list of available markets from Paradex.
    
    Returns:
        Dict[str, Any]: List of available markets.
    """
    try:
        client = await get_paradex_client()
        response = client.fetch_markets()
        markets = [market["symbol"] for market in response["results"]]
        # Format the response
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "markets": markets,
            "count": len(markets)
        }
    except Exception as e:
        logger.error(f"Error fetching markets: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "markets": [],
            "count": 0
        }
    
@server.tool("paradex-market-details")
async def get_market_details(market_id: str ) -> Dict[str, Any]:
    """
    Get details of a market.
    
    Args:
        market_id (str): The ID of the market to get details for.
        
    Returns:
        Dict[str, Any]: Details of the market.
    """
    try:
        client = await get_paradex_client()
        details = client.fetch_markets(params={"market": market_id})
        
        # Format the response
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "details": details["results"],
        }
    except Exception as e:
        logger.error(f"Error fetching markets: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "details": None,
        }

@server.tool("paradex-market-summary")
async def get_market_summary(market_id: str) -> Dict[str, Any]:
    """
    Get a summary of market.
    
    
    Args:
        market_id (str): The ID of the market to get summary for.
        
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
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "summary": None
        }


@server.tool("paradex-funding-data")
async def get_funding_data(market_id: str, start_unix_ms: int, end_unix_ms: int) -> Dict[str, Any]:
    """
    Get a summary of market.
    
    
    Args:
        market_id (str): The ID of the market to get funding data for.
        start_unix_ms (int): The start time in unix milliseconds.
        end_unix_ms (int): The end time in unix milliseconds.
        
    Returns:
        Dict[str, Any]: Summary of market information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = client.fetch_funding_data(params={"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms})
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "funding_data": None
        }


@server.tool("paradex-bbo")
async def get_bbo(market_id: str) -> Dict[str, Any]:
    """
    Get a summary of market.
    
    
    Args:
        market_id (str): The ID of the market to get BBO for.
        
    Returns:
        Dict[str, Any]: Summary of market information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = client.fetch_bbo(market_id)
        return response
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "funding_data": None
        }


@server.tool("paradex-orderbook")
async def get_orderbook(market_id: str, depth: int = 10) -> Dict[str, Any]:
    """
    Get a summary of market.
    
    
    Args:
        market_id (str): The ID of the market to get orderbook for.
        depth (int): The depth of the orderbook.
    Returns:
        Dict[str, Any]: Summary of market information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = client.fetch_orderbook(market_id, params={"depth": depth})
        return response
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "orderbook": None
        }

@server.tool("paradex-klines")
async def get_klines(market_id: str, resolution: str = "1", start_unix_ms: int = None, end_unix_ms: int = None) -> Dict[str, Any]:
    """
    Klines for a symbol    
    
    Args:
        market_id (str): The ID of the market to get klines for.
        resolution (str): The resolution of the klines in minutes: 1, 3, 5, 15, 30, 60
        start_unix_ms (int): The start time in unix milliseconds.
        end_unix_ms (int): The end time in unix milliseconds.
    Returns:
        Dict[str, Any]: Summary of market information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = await api_call(client, "markets/klines", params={
            "symbol": market_id, "resolution": resolution, 
            "start_at": start_unix_ms, "end_at": end_unix_ms})
        return response
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "orderbook": None
        }
    

@server.tool("paradex-trades")
async def get_trades(market_id: str, start_unix_ms: int = None, end_unix_ms: int = None) -> Dict[str, Any]:
    """
    Trades for a symbol    
    
    Args:
        market_id (str): The ID of the market to get klines for.
        start_unix_ms (int): The start time in unix milliseconds.
        end_unix_ms (int): The end time in unix milliseconds.
    Returns:
        Dict[str, Any]: Summary of market information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = client.fetch_trades(params={
            "market": market_id,
            "start_at": start_unix_ms, "end_at": end_unix_ms})
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "orderbook": None
        }