"""
Market data tools for accessing Paradex market information.

This module provides tools for retrieving market data from Paradex,
including market listings, details, orderbooks, and historical data.
None of these tools require authentication.
"""

import logging
from enum import Enum
from typing import Annotated, Any, Literal

from mcp.server.fastmcp.server import Context
from pydantic import BaseModel, Field, TypeAdapter

from mcp_paradex import models
from mcp_paradex.models import BBO, FundingData, MarketDetails, MarketSummary, Trade
from mcp_paradex.server.server import server
from mcp_paradex.utils.jmespath_utils import apply_jmespath_filter
from mcp_paradex.utils.paradex_client import api_call, get_paradex_client

logger = logging.getLogger(__name__)


@server.tool(name="paradex_filters_model")
async def get_filters_model(
    tool_name: Annotated[str, Field(description="The name of the tool to get the filters for.")],
) -> dict:
    """
    Get detailed schema information to build precise data filters.

    Use this tool when you need to:
    - Understand exactly what fields are available for filtering
    - Learn the data types and formats for specific fields
    - Build complex JMESPath queries with correct syntax
    - Create sophisticated filtering and sorting expressions

    Knowing the exact schema helps you construct precise filters that
    return exactly the data you need, avoiding trial and error.

    Example use cases:
    - Learning what fields exist in market data responses
    - Finding the correct property names for filtering
    - Understanding data types for numerical comparisons
    - Building complex multi-criteria filters for large datasets
    """
    tool_descriptions = {
        "paradex_markets": models.MarketDetails.model_json_schema(),
        "paradex_market_summaries": models.MarketSummary.model_json_schema(),
        "paradex_open_orders": models.OrderState.model_json_schema(),
        "paradex_orders_history": models.OrderState.model_json_schema(),
        "paradex_vaults": models.Vault.model_json_schema(),
        "paradex_vault_summary": models.VaultSummary.model_json_schema(),
    }
    return tool_descriptions[tool_name]


market_details_adapter = TypeAdapter(list[MarketDetails])


@server.tool(name="paradex_markets")
async def get_markets(
    market_ids: Annotated[
        list[str], Field(description="Market symbols to get details for.", default=["ALL"])
    ],
    jmespath_filter: Annotated[
        str,
        Field(
            description="JMESPath expression to filter, sort, or limit the results.",
            default="",
        ),
    ],
    limit: Annotated[
        int,
        Field(
            default=10,
            gt=0,
            le=100,
            description="Limit the number of results to the specified number.",
        ),
    ],
    offset: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            description="Offset the results to the specified number.",
        ),
    ],
    ctx: Context = None,
) -> dict:
    """
    Find markets that match your trading criteria or get detailed market specifications.

    Use this tool when you need to:
    - Understand exact tick sizes and minimum order sizes before placing trades
    - Find all markets for a specific asset (e.g., all BTC-based markets)
    - Compare contract specifications across different markets
    - Identify markets with specific characteristics for your trading strategy

    Retrieves comprehensive details about specified markets, including
    base and quote assets, tick size, minimum order size, and other
    trading parameters. If "ALL" is specified or no market IDs are provided,
    returns details for all available markets.

    Example use cases:
    - Finding the minimum order size for a new trade
    - Identifying markets with the smallest tick size for precise entries
    - Checking which assets are available for trading

    `asset_kind` is the type of asset in the market. It can be `PERP` or `PERP_OPTION`.

    You can use JMESPath expressions (https://jmespath.org/specification.html) to filter, sort, or limit the results.
    Use the `paradex_filters_model` tool to get the filters for a tool.
    Examples:
    - Filter by base asset: "[?base_asset=='BTC']"
    - Sort by 24h volume: "sort_by([*], &volume_24h)"
    - Limit to top 5 by volume: "[sort_by([*], &to_number(volume_24h))[-5:]]"
    """
    try:
        client = await get_paradex_client()

        response = client.fetch_markets()
        if "error" in response:
            await ctx.error(response)
            raise Exception(response["error"])
        details = market_details_adapter.validate_python(response["results"])
        if market_ids and "ALL" not in market_ids:
            details = [detail for detail in details if detail.symbol in market_ids]

        # Apply JMESPath filter if provided
        if jmespath_filter:
            details = apply_jmespath_filter(
                data=details,
                jmespath_filter=jmespath_filter,
                type_adapter=market_details_adapter,
                error_logger=ctx.error if ctx else None,
            )
        sorted_details = sorted(details, key=lambda x: x.symbol, reverse=True)
        result_details = sorted_details[offset : offset + limit]
        result = {
            "description": MarketDetails.__doc__.strip() if MarketDetails.__doc__ else None,
            "fields": MarketDetails.model_json_schema(),
            "results": result_details,
            "total": len(sorted_details),
            "limit": limit,
            "offset": offset,
        }
        return result
    except Exception as e:
        await ctx.error(f"Error fetching market details: {e!s}")
        raise e


market_summary_adapter = TypeAdapter(list[MarketSummary])


@server.tool(name="paradex_market_summaries")
async def get_market_summaries(
    market_ids: Annotated[
        list[str], Field(description="Market symbols to get summaries for.", default=["ALL"])
    ],
    jmespath_filter: Annotated[
        str,
        Field(
            description="JMESPath expression to filter, sort, or limit the results.",
            default=None,
        ),
    ],
    limit: Annotated[
        int,
        Field(
            default=10,
            gt=0,
            le=100,
            description="Limit the number of results to the specified number.",
        ),
    ],
    offset: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            description="Offset the results to the specified number.",
        ),
    ],
    ctx: Context = None,
) -> dict:
    """
    Identify the most active or volatile markets and get current market conditions.

    Use this tool when you need to:
    - Find the most active markets by volume for liquidity analysis
    - Discover markets with significant price movements for momentum strategies
    - Compare current prices across multiple assets
    - Identify markets with unusual behavior for potential opportunities

    Retrieves current market summary information including price, volume,
    24h change, and other key market metrics. If "ALL" is specified or no market IDs
    are provided, returns summaries for all available markets.

    Example use cases:
    - Finding high-volatility markets for short-term trading
    - Identifying top gainers and losers for the day
    - Comparing volume across different markets to find liquidity
    - Getting the current price and 24-hour range for price analysis

    You can use JMESPath expressions (https://jmespath.org/specification.html) to filter, sort, or limit the results.
    Use the `paradex_filters_model` tool to get the filters for a tool.
    Examples:
    - Filter by high price: "[?high_price > `10000`]"
    - Sort by volume: "sort_by([*], &volume)"
    - Get top 3 by price change: "[sort_by([*], &to_number(price_change_percent))[-3:]]"
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = client.fetch_markets_summary(params={"market": "ALL"})
        if "error" in response:
            await ctx.error(response)
            raise Exception(response["error"])

        # Try to validate directly now that the model is more flexible
        summaries = market_summary_adapter.validate_python(response["results"])

        if market_ids and "ALL" not in market_ids:
            summaries = [summary for summary in summaries if summary.symbol in market_ids]

        # Apply JMESPath filter if provided
        if jmespath_filter:
            summaries = apply_jmespath_filter(
                data=summaries,
                jmespath_filter=jmespath_filter,
                type_adapter=market_summary_adapter,
                error_logger=ctx.error if ctx else None,
            )
        sorted_summaries = sorted(summaries, key=lambda x: x.symbol, reverse=True)
        result_summaries = sorted_summaries[offset : offset + limit]
        result = {
            "description": MarketSummary.__doc__.strip() if MarketSummary.__doc__ else None,
            "fields": MarketSummary.model_json_schema(),
            "results": result_summaries,
            "total": len(sorted_summaries),
            "limit": limit,
            "offset": offset,
        }
        return result
    except Exception as e:
        logger.error(f"Error fetching market summaries: {e!s}")
        await ctx.error(f"Error fetching market summaries: {e!s}")
        raise e


funding_data_adapter = TypeAdapter(list[FundingData])


@server.tool(name="paradex_funding_data")
async def get_funding_data(
    market_id: Annotated[str, Field(description="Market symbol to get funding data for.")],
    start_unix_ms: Annotated[int, Field(description="Start time in unix milliseconds.")],
    end_unix_ms: Annotated[int, Field(description="End time in unix milliseconds.")],
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Analyze funding rates for potential funding arbitrage or to understand holding costs.

    Use this tool when you need to:
    - Calculate expected funding payments for a position
    - Find markets with extreme funding rates for potential arbitrage
    - Understand historical funding patterns for a market
    - Evaluate the cost of holding a position over time

    This data is critical for perpetual futures traders to assess the carrying cost
    of positions and identify potential funding arbitrage opportunities.

    Example use cases:
    - Finding markets with negative funding for "paid to hold" opportunities
    - Calculating the funding component of a trade's P&L
    - Comparing funding rates across different assets for relative value trades
    - Analyzing funding rate volatility to predict potential rate changes
    """
    try:
        # Get funding data from Paradex
        client = await get_paradex_client()
        response = client.fetch_funding_data(
            params={"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
        )
        if "error" in response:
            await ctx.error(response)
            raise Exception(response["error"])
        funding_data = funding_data_adapter.validate_python(response["results"])
        results = {
            "description": FundingData.__doc__.strip() if FundingData.__doc__ else None,
            "fields": FundingData.model_json_schema(),
            "results": funding_data,
        }
        return results
    except Exception as e:
        await ctx.error(f"Error fetching funding data for {market_id}: {e!s}")
        raise e


class OrderbookDepth(int, Enum):
    """Valid orderbook depth values."""

    SHALLOW = 5
    MEDIUM = 10
    DEEP = 20
    VERY_DEEP = 50
    FULL = 100


@server.tool(name="paradex_orderbook")
async def get_orderbook(
    market_id: Annotated[str, Field(description="Market symbol to get orderbook for.")],
    depth: Annotated[
        int,
        Field(default=OrderbookDepth.MEDIUM, description="The depth of the orderbook to retrieve."),
    ],
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Analyze market depth and liquidity to optimize order entry and execution.

    Use this tool when you need to:
    - Assess true liquidity before placing large orders
    - Identify potential support/resistance levels from order clusters
    - Determine optimal limit order prices for higher fill probability
    - Detect order imbalances that might signal price direction

    Understanding the orderbook is essential for effective trade execution,
    especially for larger orders or in less liquid markets.

    Example use cases:
    - Finding the optimal limit price to ensure your order gets filled
    - Estimating potential slippage for market orders of different sizes
    - Identifying large resting orders that might act as support/resistance
    - Detecting order book imbalances that could predict short-term price moves
    """
    try:
        # Get orderbook from Paradex
        client = await get_paradex_client()
        response = client.fetch_orderbook(market_id, params={"depth": depth})
        return response
    except Exception as e:
        await ctx.error(f"Error fetching orderbook for {market_id}: {e!s}")
        raise e


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
    market_id: Annotated[str, Field(description="Market symbol to get klines for.")],
    resolution: Annotated[
        KLinesResolutionEnum, Field(default=1, description="The time resolution of the klines.")
    ],
    start_unix_ms: Annotated[int, Field(description="Start time in unix milliseconds.")],
    end_unix_ms: Annotated[int, Field(description="End time in unix milliseconds.")],
    ctx: Context = None,
) -> list[OHLCV]:
    """
    Analyze historical price patterns for technical analysis and trading decisions.

    Use this tool when you need to:
    - Perform technical analysis on historical price data
    - Identify support and resistance levels from price history
    - Calculate indicators like moving averages, RSI, or MACD
    - Backtest trading strategies on historical data
    - Visualize price action over specific timeframes

    Candlestick data is fundamental for most technical analysis and trading decisions,
    providing structured price and volume information over time.

    Example use cases:
    - Identifying chart patterns for potential entries or exits
    - Calculating technical indicators for trading signals
    - Determining volatility by analyzing price ranges
    - Finding significant price levels from historical support/resistance
    - Measuring volume patterns to confirm price movements
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
        await ctx.error(f"Error fetching klines for {market_id}: {e!s}")
        raise e


trade_adapter = TypeAdapter(list[Trade])


@server.tool(name="paradex_trades")
async def get_trades(
    market_id: Annotated[str, Field(description="Market symbol to get trades for.")],
    start_unix_ms: Annotated[int, Field(description="Start time in unix milliseconds.")],
    end_unix_ms: Annotated[int, Field(description="End time in unix milliseconds.")],
    ctx: Context = None,
) -> dict:
    """
    Analyze actual market transactions to understand market sentiment and liquidity.

    Use this tool when you need to:
    - Detect large trades that might signal institutional activity
    - Calculate average trade size during specific periods
    - Identify buy/sell pressure imbalances
    - Monitor execution prices vs. order book prices
    - Understand market momentum through trade flow

    Trade data provides insights into actual market activity versus just orders,
    helping you understand how other participants are behaving.

    Example use cases:
    - Detecting large "whale" transactions that might influence price
    - Analyzing trade sizes to gauge market participation
    - Identifying periods of aggressive buying or selling
    - Understanding trade frequency as an indicator of market interest
    - Comparing executed prices to orderbook mid-price for market impact analysis
    """
    try:
        # Get trades from Paradex
        client = await get_paradex_client()
        response = client.fetch_trades(
            params={"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
        )
        if "error" in response:
            raise Exception(response["error"])
        trades = trade_adapter.validate_python(response["results"])
        results = {
            "description": Trade.__doc__.strip() if Trade.__doc__ else None,
            "fields": Trade.model_json_schema(),
            "results": trades,
        }
        return results
    except Exception as e:
        await ctx.error(f"Error fetching trades for {market_id}: {e!s}")
        raise e


@server.tool(name="paradex_bbo")
async def get_bbo(
    market_id: Annotated[str, Field(description="Market symbol to get BBO for.")],
    ctx: Context = None,
) -> dict:
    """
    Get the current best available prices for immediate execution decisions.

    Use this tool when you need to:
    - Make quick trading decisions without full orderbook depth
    - Calculate current spread costs before placing orders
    - Monitor real-time price changes efficiently
    - Get a snapshot of current market conditions
    - Determine fair mid-price for calculations

    The BBO provides the most essential price information with minimal data,
    perfect for quick decisions or when full orderbook depth isn't needed.

    Example use cases:
    - Calculating current trading spreads before placing orders
    - Monitoring real-time price movements efficiently
    - Determining execution prices for immediate market orders
    - Calculating mid-price for order placement strategies
    - Setting appropriate limit order prices to improve fill chances
    """
    try:
        # Get BBO from Paradex
        client = await get_paradex_client()
        response = client.fetch_bbo(market_id)
        bbo = BBO(**response)
        results = {
            "description": BBO.__doc__.strip() if BBO.__doc__ else None,
            "fields": BBO.model_json_schema(),
            "results": bbo,
        }
        return results
    except Exception as e:
        await ctx.error(f"Error fetching BBO for {market_id}: {e!s}")
        raise e
