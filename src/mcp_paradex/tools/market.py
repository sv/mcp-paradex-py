"""
Market data tools for accessing Paradex market information.

This module provides tools for retrieving market data from Paradex,
including market listings, details, orderbooks, and historical data.
None of these tools require authentication.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from mcp.server.fastmcp.server import Context
from pydantic import BaseModel, Field, TypeAdapter

from mcp_paradex.models import BBO, MarketDetails, MarketSummary, Trade
from mcp_paradex.server.server import server
from mcp_paradex.utils.config import config
from mcp_paradex.utils.paradex_client import api_call, get_paradex_client

logger = logging.getLogger(__name__)


@server.tool(name="paradex_market_names")
async def get_market_names(ctx: Context) -> list[str]:
    """
    Get a list of available markets from Paradex.

    Retrieves all available trading markets/pairs from the Paradex exchange.
    This tool requires no parameters and returns a comprehensive list of
    all markets that can be traded on Paradex.

    Returns:
        List[str]: List of available markets.
    """
    try:
        client = await get_paradex_client()
        response = client.fetch_markets()
        if "error" in response:
            raise Exception(response["error"])
        markets = [market["symbol"] for market in response["results"]]
        return markets
    except Exception as e:
        ctx.error(f"Error fetching markets: {e!s}")
        return e


market_details_adapter = TypeAdapter(list[MarketDetails])


@server.tool(name="paradex_market_details")
async def get_market_details(
    market_ids: list[str] = Field(
        description="Market symbols to get details for.", default=["ALL"]
    ),
    ctx: Context = None,
) -> list[MarketDetails]:
    """
    Get detailed information about specific markets.

    Retrieves comprehensive details about specified markets, including
    base and quote assets, tick size, minimum order size, and other
    trading parameters. If "ALL" is specified or no market IDs are provided,
    returns details for all available markets.

    Args:
        market_ids: List of market symbols to get details for. Use ["ALL"] for all markets.
        ctx: Optional context object for logging.

    Returns:
        List of MarketDetails objects containing comprehensive information about each market.
    """
    try:
        client = await get_paradex_client()

        response = client.fetch_markets()
        if "error" in response:
            raise Exception(response["error"])
        details = market_details_adapter.validate_python(response["results"])
        if market_ids and "ALL" not in market_ids:
            details = [detail for detail in details if detail.symbol in market_ids]
        else:
            details = details
        return details
    except Exception as e:
        ctx.error(f"Error fetching market details: {e!s}")
        raise e


market_summary_adapter = TypeAdapter(list[MarketSummary])


@server.tool(name="paradex_market_summaries")
async def get_market_summaries(
    market_ids: list[str] = Field(
        description="Market symbols to get summaries for.", default=["ALL"]
    ),
    ctx: Context = None,
) -> list[MarketSummary]:
    """
    Get a summary of market statistics and current state for specific markets.

    Retrieves current market summary information including price, volume,
    24h change, and other key market metrics. If "ALL" is specified or no market IDs
    are provided, returns summaries for all available markets.

    Args:
        market_ids: List of market symbols to get summaries for. Use ["ALL"] for all markets.
        ctx: Optional context object for logging.

    Returns:
        List of MarketSummary objects containing current statistics for each market.

    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = client.fetch_markets_summary(params={"market": "ALL"})
        if "error" in response:
            raise Exception(response["error"])
        summaries = market_summary_adapter.validate_python(response["results"])
        if market_ids and "ALL" not in market_ids:
            summaries = [summary for summary in summaries if summary.symbol in market_ids]
        else:
            summaries = summaries
        return summaries
    except Exception as e:
        ctx.error(f"Error fetching market summaries: {e!s}")
        raise e


@server.tool(name="paradex_funding_data")
async def get_funding_data(
    market_id: str = Field(description="Market symbol to get funding data for."),
    start_unix_ms: int = Field(description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(description="End time in unix milliseconds."),
) -> dict[str, Any]:
    """
    Get historical funding rate data for a perpetual market.

    Retrieves funding rate history for a specified time period, which is
    essential for understanding the cost of holding perpetual positions.


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
        response = client.fetch_funding_data(
            params={"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
        )
        if "error" in response:
            raise Exception(response["error"])
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching funding data for {market_id}: {e!s}")
        return e


class OrderbookDepth(int, Enum):
    """Valid orderbook depth values."""

    SHALLOW = 5
    MEDIUM = 10
    DEEP = 20
    VERY_DEEP = 50
    FULL = 100


@server.tool(name="paradex_orderbook")
async def get_orderbook(
    market_id: str = Field(description="Market symbol to get orderbook for."),
    depth: int = Field(
        default=OrderbookDepth.MEDIUM, description="The depth of the orderbook to retrieve."
    ),
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Get the current orderbook for a market.

    Retrieves the current state of the orderbook for a specified market,
    showing bid and ask orders up to the requested depth.


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
        ctx.error(f"Error fetching orderbook for {market_id}: {e!s}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "orderbook": None,
        }


KLinesResolutionEnum = Literal[1, 3, 5, 15, 30, 60]


class OHLCV(BaseModel):
    """OHLCV data for a market."""

    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


ohlcv_adapter = TypeAdapter(list[OHLCV])


@server.tool(name="paradex_klines")
async def get_klines(
    market_id: str = Field(description="Market symbol to get klines for."),
    resolution: KLinesResolutionEnum = Field(
        default=1, description="The time resolution of the klines."
    ),
    start_unix_ms: int = Field(description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(description="End time in unix milliseconds."),
    ctx: Context = None,
) -> list[OHLCV]:
    """
    Get candlestick (kline) data for a market.

    Retrieves historical price candlestick data for a specified market and time period.
    Each candlestick contains open, high, low, close prices and volume information.

    Returns:
        List[OHLCV]: Candlestick data with the following structure for each candle:
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
        response = await api_call(
            client,
            "markets/klines",
            params={
                "symbol": market_id,
                "resolution": str(resolution),
                "start_at": start_unix_ms,
                "end_at": end_unix_ms,
            },
        )
        if "error" in response:
            raise Exception(response["error"])
        results = response["results"]
        list_of_ohlcv = [
            OHLCV(
                timestamp=result[0],
                open=result[1],
                high=result[2],
                low=result[3],
                close=result[4],
                volume=result[5],
            )
            for result in results
        ]
        return list_of_ohlcv
    except Exception as e:
        ctx.error(f"Error fetching klines for {market_id}: {e!s}")
        raise e


trade_adapter = TypeAdapter(list[Trade])


@server.tool(name="paradex_trades")
async def get_trades(
    market_id: str = Field(description="Market symbol to get trades for."),
    start_unix_ms: int = Field(description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(description="End time in unix milliseconds."),
    ctx: Context = None,
) -> list[Trade]:
    """
    Get recent trades for a market.

    Retrieves historical trade data for a specified market and time period.
    Each trade includes price, size, side (buy/sell), and timestamp information.
    """
    try:
        # Get trades from Paradex
        client = await get_paradex_client()
        response = client.fetch_trades(
            params={"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
        )
        trades = trade_adapter.validate_python(response["results"])
        return trades
    except Exception as e:
        ctx.error(f"Error fetching trades for {market_id}: {e!s}")
        raise e


@server.tool(name="paradex_bbo")
async def get_bbo(
    market_id: str = Field(description="Market symbol to get BBO for."),
    ctx: Context = None,
) -> BBO:
    """
    Get the Best Bid and Offer (BBO) for a market.

    Retrieves the current best bid and best offer (ask) prices and sizes
    for a specified market. This represents the tightest spread currently
    available.
    """
    try:
        # Get BBO from Paradex
        client = await get_paradex_client()
        response = client.fetch_bbo(market_id)
        bbo = BBO(**response)
        return bbo
    except Exception as e:
        ctx.error(f"Error fetching BBO for {market_id}: {e!s}")
        raise e
