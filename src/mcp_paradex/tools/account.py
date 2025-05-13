"""
Account management tools.
"""

from typing import Annotated

from mcp.server.fastmcp.server import Context
from pydantic import Field, TypeAdapter

from mcp_paradex.models import AccountSummary, Fill, Position, Transaction
from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import api_call, get_authenticated_paradex_client


@server.tool(name="paradex_account_summary")
async def get_account_summary(ctx: Context) -> AccountSummary:
    """
    Get a snapshot of your account's current financial status and trading capacity.

    Use this tool when you need to:
    - Check your current available and total balance
    - Understand your margin utilization and remaining trading capacity
    - Verify your account health and distance from liquidation
    - Get an overview of realized and unrealized P&L

    This provides the essential financial information needed to make informed
    trading decisions and manage risk appropriately.

    Example use cases:
    - Checking available balance before placing new orders
    - Monitoring account health during volatile market conditions
    - Assessing realized and unrealized P&L for performance tracking
    - Verifying margin requirements and utilization
    """
    client = await get_authenticated_paradex_client()
    response = await api_call(client, "account")
    return AccountSummary.model_validate(response)


position_adapter = TypeAdapter(list[Position])


@server.tool(name="paradex_account_positions")
async def get_account_positions(ctx: Context) -> dict:
    """
    Analyze your open positions to monitor exposure, profitability, and risk.

    Use this tool when you need to:
    - Check the status and P&L of all your open positions
    - Monitor your liquidation prices and margin requirements
    - Assess your exposure across different markets
    - Make decisions about position management (scaling, hedging, closing)

    Understanding your current positions is fundamental to proper risk management
    and is the starting point for many trading decisions.

    Example use cases:
    - Checking the unrealized P&L of your positions
    - Monitoring liquidation prices during market volatility
    - Assessing total exposure across related assets
    - Verifying entry prices and position sizes
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_positions()
    if "error" in response:
        await ctx.error(response)
        raise Exception(response["error"])
    positions = position_adapter.validate_python(response["results"])

    results = {
        "description": Position.__doc__.strip() if Position.__doc__ else None,
        "fields": Position.model_json_schema(),
        "results": positions,
    }
    return results


fill_adapter = TypeAdapter(list[Fill])


@server.tool(name="paradex_account_fills")
async def get_account_fills(
    market_id: Annotated[str, Field(description="Filter by market ID.")],
    start_unix_ms: Annotated[int, Field(description="Start time in unix milliseconds.")],
    end_unix_ms: Annotated[int, Field(description="End time in unix milliseconds.")],
    ctx: Context = None,
) -> dict:
    """
    Analyze your executed trades to evaluate performance and execution quality.

    Use this tool when you need to:
    - Review your trading history across specific markets
    - Calculate your average entry price for multi-fill positions
    - Analyze execution quality compared to intended prices
    - Track realized PnL from completed trades
    - Verify order execution details for reconciliation

    Detailed fill information is essential for performance analysis and
    understanding how your orders were actually executed.

    Example use cases:
    - Calculating volume-weighted average price (VWAP) of your entries
    - Analyzing execution slippage from your intended prices
    - Reviewing trade history for tax or accounting purposes
    - Tracking commission costs across different markets
    - Identifying which of your strategies produced the best execution
    """
    client = await get_authenticated_paradex_client()
    params = {"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
    response = client.fetch_fills(params)
    if "error" in response:
        await ctx.error(response)
        raise Exception(response["error"])
    fills = fill_adapter.validate_python(response["results"])
    results = {
        "description": Fill.__doc__.strip() if Fill.__doc__ else None,
        "fields": Fill.model_json_schema(),
        "results": fills,
    }
    return results


@server.tool(name="paradex_account_funding_payments")
async def get_account_funding_payments(
    market_id: Annotated[str | None, Field(default=None, description="Filter by market ID.")],
    start_unix_ms: Annotated[int, Field(description="Start time in unix milliseconds.")],
    end_unix_ms: Annotated[int, Field(description="End time in unix milliseconds.")],
    ctx: Context = None,
) -> dict:
    """
    Track your funding payment history to understand its impact on P&L.

    Use this tool when you need to:
    - Calculate total funding costs or gains for a position
    - Analyze how funding has affected your overall performance
    - Plan position timing around funding payment schedules
    - Compare funding costs across different markets
    - Account for funding in your trading strategy profitability

    Funding payments can significantly impact perpetual futures trading P&L,
    especially for longer-term positions or in markets with volatile funding rates.

    Example use cases:
    - Calculating the total funding component of your P&L
    - Comparing funding costs against trading profits
    - Planning position entries/exits around funding payment times
    - Identifying markets where funding has been consistently favorable
    - Reconciling funding payments for accounting purposes
    """
    client = await get_authenticated_paradex_client()
    params = {"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}
    response = client.fetch_funding_payments(params)
    return response


transaction_adapter = TypeAdapter(list[Transaction])


@server.tool(name="paradex_account_transactions")
async def get_account_transactions(
    transaction_type: Annotated[
        str | None, Field(default=None, description="Filter by transaction type.")
    ],
    start_unix_ms: Annotated[int, Field(description="Start time in unix milliseconds.")],
    end_unix_ms: Annotated[int, Field(description="End time in unix milliseconds.")],
    limit: Annotated[
        int, Field(default=50, description="Maximum number of transactions to return.")
    ],
    ctx: Context = None,
) -> list[Transaction]:
    """
    Get account transaction history.

    Retrieves a filtered history of account transactions, including deposits,
    withdrawals, trades, funding payments, and other account activities.
    Use transaction_type and time filters to limit the results and avoid
    overwhelming the client.

    This tool is valuable for:
    - Reconciliation of account activity
    - Auditing trading history
    - Tracking deposits and withdrawals
    - Analyzing funding payments over time

    """
    client = await get_authenticated_paradex_client()
    params = {
        "type": transaction_type,
        "start_at": start_unix_ms,
        "end_at": end_unix_ms,
        "limit": limit,
    }
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}
    response = client.fetch_transactions(params)
    if "error" in response:
        await ctx.error(response)
        raise Exception(response["error"])
    transactions = transaction_adapter.validate_python(response["results"])
    results = {
        "description": Transaction.__doc__.strip() if Transaction.__doc__ else None,
        "fields": Transaction.model_json_schema(),
        "results": transactions,
    }
    return results
