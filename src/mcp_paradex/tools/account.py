"""
Account management tools.
"""

from typing import Any

from mcp.server.fastmcp.server import Context
from paradex_py.api.models import AccountSummary
from pydantic import Field

from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import get_authenticated_paradex_client


@server.tool("paradex-account-summary")
async def get_account_summary(ctx: Context) -> AccountSummary:
    """
    Get account summary.

    Returns:
        Dict[str, Any]: Account summary.
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_account_summary()
    return response


@server.tool("paradex-account-positions")
async def get_account_positions(ctx: Context) -> dict[str, Any]:
    """
    Get account positions.

    Returns:
        Dict[str, Any]: Account positions.
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_positions()
    return response


@server.tool("paradex-account-fills")
async def get_account_fills(
    market_id: str = Field(description="Filter by market ID."),
    start_unix_ms: int = Field(description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(description="End time in unix milliseconds."),
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Get account fills.

    Returns:
        Dict: Account fills.
    """
    client = await get_authenticated_paradex_client()
    params = {"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
    response = client.fetch_fills(params)
    return response


@server.tool("paradex-account-funding-payments")
async def get_account_funding_payments(
    market_id: str | None = Field(default=None, description="Filter by market ID."),
    start_unix_ms: int = Field(description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(description="End time in unix milliseconds."),
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Get account funding payments.

    Returns:
        Dict[str, Any]: Account funding payments.
    """
    client = await get_authenticated_paradex_client()
    params = {"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
    response = client.fetch_funding_payments(params)
    return response


@server.tool("paradex-account-transactions")
async def get_account_transactions(
    transaction_type: str | None = Field(default=None, description="Filter by transaction type."),
    start_unix_ms: int = Field(description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(description="End time in unix milliseconds."),
    limit: int = Field(default=50, description="Maximum number of transactions to return."),
    ctx: Context = None,
) -> dict[str, Any]:
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

    Returns:
        Dict[str, Any]: Transaction history with details including:
            - transaction_id: Transaction identifier
            - type: Transaction type
            - amount: Transaction amount
            - currency: Currency of the transaction
            - timestamp: When the transaction occurred
            - status: Status of the transaction
            - details: Additional transaction-specific details
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
    return response
