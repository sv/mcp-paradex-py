"""
Account management tools.
"""

from mcp.server.fastmcp.server import Context
from paradex_py.api.models import AccountSummary
from pydantic import Field, TypeAdapter

from mcp_paradex.models import Fill, Position, Transaction
from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import get_authenticated_paradex_client


@server.tool("paradex-account-summary")
async def get_account_summary(ctx: Context) -> AccountSummary:
    """
    Get account summary.

    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_account_summary()
    return response


position_adapter = TypeAdapter(list[Position])


@server.tool("paradex-account-positions")
async def get_account_positions(ctx: Context) -> list[Position]:
    """
    Get account positions.
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_positions()
    positions = position_adapter.validate_python(response["results"])
    return positions


fill_adapter = TypeAdapter(list[Fill])


@server.tool("paradex-account-fills")
async def get_account_fills(
    market_id: str = Field(description="Filter by market ID."),
    start_unix_ms: int = Field(description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(description="End time in unix milliseconds."),
    ctx: Context = None,
) -> list[Fill]:
    """
    Get account fills.
    """
    client = await get_authenticated_paradex_client()
    params = {"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
    response = client.fetch_fills(params)
    fills = [Fill(**fill) for fill in response["results"]]
    return fills


@server.tool("paradex-account-funding-payments")
async def get_account_funding_payments(
    market_id: str | None = Field(default=None, description="Filter by market ID."),
    start_unix_ms: int = Field(description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(description="End time in unix milliseconds."),
    ctx: Context = None,
) -> dict:
    """
    Get account funding payments.

    Returns:
        Dict[str, Any]: Account funding payments.
    """
    client = await get_authenticated_paradex_client()
    params = {"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}
    response = client.fetch_funding_payments(params)
    return response


transaction_adapter = TypeAdapter(list[Transaction])


@server.tool("paradex-account-transactions")
async def get_account_transactions(
    transaction_type: str | None = Field(default=None, description="Filter by transaction type."),
    start_unix_ms: int = Field(description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(description="End time in unix milliseconds."),
    limit: int = Field(default=50, description="Maximum number of transactions to return."),
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
    transactions = transaction_adapter.validate_python(response["results"])
    return transactions
