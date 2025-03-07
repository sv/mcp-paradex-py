"""
Market data tools for accessing Paradex market information.

This module provides tools for retrieving market data from Paradex,
including market listings, details, orderbooks, and historical data.
None of these tools require authentication.
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from enum import Enum

from mcp_paradex.server.server import server
from mcp_paradex.utils.config import config
from mcp_paradex.utils.paradex_client import get_paradex_client, api_call

logger = logging.getLogger(__name__)


@server.tool("paradex-market-names")
async def get_market_names() -> Dict[str, Any]:
    """
    Get a list of available markets from Paradex.
    
    Retrieves all available trading markets/pairs from the Paradex exchange.
    This tool requires no parameters and returns a comprehensive list of
    all markets that can be traded on Paradex.
    
    Returns:
        Dict[str, Any]: List of available markets with the following structure:
            - success (bool): Whether the request was successful
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment (mainnet/testnet)
            - markets (List[str]): List of market symbols
            - count (int): Total number of markets
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
async def get_market_details(market_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific market.
    
    Retrieves comprehensive details about a specific market, including
    base and quote assets, tick size, minimum order size, and other
    trading parameters.
    
    Args:
        market_id (str): The market symbol to get details for (e.g., "ETH-PERP").
        
    Returns:
        Dict[str, Any]: Detailed market information with the following structure:
            - success (bool): Whether the request was successful
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment (mainnet/testnet)
            - details (Dict): Detailed market information including trading parameters
            - error (str, optional): Error message if request failed
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
        logger.error(f"Error fetching market details for {market_id}: {str(e)}")
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
    Get a summary of market statistics and current state.
    
    Retrieves current market summary information including price, volume,
    24h change, and other key market metrics.
    
    Args:
        market_id (str): The market symbol to get summary for (e.g., "ETH-PERP").
        
    Returns:
        Dict[str, Any]: Market summary information including:
            - Current price
            - 24h high/low
            - 24h volume
            - Price change percentage
            - Other market statistics
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
            - summary (None): Null value for summary
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        summary = client.fetch_markets_summary(params={"market": market_id})
        return summary
    except Exception as e:
        logger.error(f"Error fetching market summary for {market_id}: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "summary": None
        }


@server.tool("paradex-funding-data")
async def get_funding_data(
    market_id: str, 
    start_unix_ms: int, 
    end_unix_ms: int
) -> Dict[str, Any]:
    """
    Get historical funding rate data for a perpetual market.
    
    Retrieves funding rate history for a specified time period, which is
    essential for understanding the cost of holding perpetual positions.
    
    Args:
        market_id (str): The market symbol to get funding data for (e.g., "ETH-PERP").
        start_unix_ms (int): The start time in unix milliseconds.
        end_unix_ms (int): The end time in unix milliseconds.
        
    Returns:
        Dict[str, Any]: Historical funding rate data with timestamps.
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
            - funding_data (None): Null value for funding data
    """
    try:
        # Get funding data from Paradex
        client = await get_paradex_client()
        response = client.fetch_funding_data(params={
            "market": market_id, 
            "start_at": start_unix_ms, 
            "end_at": end_unix_ms
        })
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching funding data for {market_id}: {str(e)}")
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
    Get the Best Bid and Offer (BBO) for a market.
    
    Retrieves the current best bid and best offer (ask) prices and sizes
    for a specified market. This represents the tightest spread currently
    available.
    
    Args:
        market_id (str): The market symbol to get BBO for (e.g., "ETH-PERP").
        
    Returns:
        Dict[str, Any]: Best bid and offer information including:
            - bid price and size
            - ask price and size
            - timestamp
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
    """
    try:
        # Get BBO from Paradex
        client = await get_paradex_client()
        response = client.fetch_bbo(market_id)
        return response
    except Exception as e:
        logger.error(f"Error fetching BBO for {market_id}: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "bbo": None
        }


class OrderbookDepth(int, Enum):
    """Valid orderbook depth values."""
    SHALLOW = 5
    MEDIUM = 10
    DEEP = 20
    VERY_DEEP = 50
    FULL = 100


@server.tool("paradex-orderbook")
async def get_orderbook(
    market_id: str, 
    depth: int = OrderbookDepth.MEDIUM
) -> Dict[str, Any]:
    """
    Get the current orderbook for a market.
    
    Retrieves the current state of the orderbook for a specified market,
    showing bid and ask orders up to the requested depth.
    
    Args:
        market_id (str): The market symbol to get orderbook for (e.g., "ETH-PERP").
        depth (int, optional): The depth of the orderbook to retrieve. 
            Defaults to 10. Common values: 5, 10, 20, 50, 100.
    
    Returns:
        Dict[str, Any]: Orderbook data including:
            - bids: List of [price, size] pairs
            - asks: List of [price, size] pairs
            - timestamp
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
            - orderbook (None): Null value for orderbook
    """
    try:
        # Get orderbook from Paradex
        client = await get_paradex_client()
        response = client.fetch_orderbook(market_id, params={"depth": depth})
        return response
    except Exception as e:
        logger.error(f"Error fetching orderbook for {market_id}: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "orderbook": None
        }


class KlineResolution(str, Enum):
    """Valid kline/candlestick resolutions."""
    ONE_MINUTE = "1"
    THREE_MINUTES = "3"
    FIVE_MINUTES = "5"
    FIFTEEN_MINUTES = "15"
    THIRTY_MINUTES = "30"
    ONE_HOUR = "60"
    FOUR_HOURS = "240"
    ONE_DAY = "1D"


@server.tool("paradex-klines")
async def get_klines(
    market_id: str, 
    resolution: KlineResolution = KlineResolution.ONE_MINUTE, 
    start_unix_ms: Optional[int] = None, 
    end_unix_ms: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get candlestick (kline) data for a market.
    
    Retrieves historical price candlestick data for a specified market and time period.
    Each candlestick contains open, high, low, close prices and volume information.
    
    Args:
        market_id (str): The market symbol to get klines for (e.g., "ETH-PERP").
        resolution (str, optional): The time resolution of the klines. 
            Valid values: "1", "3", "5", "15", "30", "60", "240", "1D" (minutes, except 1D = 1 day).
            Defaults to "1" (1 minute).
        start_unix_ms (int, optional): The start time in unix milliseconds.
            If None, defaults to exchange-specific recent timeframe.
        end_unix_ms (int, optional): The end time in unix milliseconds.
            If None, defaults to current time.
    
    Returns:
        Dict[str, Any]: Candlestick data with the following structure for each candle:
            - timestamp
            - open price
            - high price
            - low price
            - close price
            - volume
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
    """
    try:
        # Get klines from Paradex
        client = await get_paradex_client()
        response = await api_call(client, "markets/klines", params={
            "symbol": market_id, 
            "resolution": resolution, 
            "start_at": start_unix_ms, 
            "end_at": end_unix_ms
        })
        return response
    except Exception as e:
        logger.error(f"Error fetching klines for {market_id}: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "klines": None
        }


@server.tool("paradex-trades")
async def get_trades(
    market_id: str, 
    start_unix_ms: Optional[int] = None, 
    end_unix_ms: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get recent trades for a market.
    
    Retrieves historical trade data for a specified market and time period.
    Each trade includes price, size, side (buy/sell), and timestamp information.
    
    Args:
        market_id (str): The market symbol to get trades for (e.g., "ETH-PERP").
        start_unix_ms (int, optional): The start time in unix milliseconds.
            If None, defaults to exchange-specific recent timeframe.
        end_unix_ms (int, optional): The end time in unix milliseconds.
            If None, defaults to current time.
    
    Returns:
        Dict[str, Any]: List of trades with the following structure for each trade:
            - id: Trade ID
            - price: Execution price
            - size: Trade size
            - side: "buy" or "sell"
            - timestamp: Time of execution
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
    """
    try:
        # Get trades from Paradex
        client = await get_paradex_client()
        response = client.fetch_trades(params={
            "market": market_id,
            "start_at": start_unix_ms, 
            "end_at": end_unix_ms
        })
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching trades for {market_id}: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "trades": None
        }