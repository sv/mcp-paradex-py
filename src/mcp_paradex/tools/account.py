"""
Account management tools.
"""
from typing import Dict, Any

from pydantic import Field


from mcp.server.fastmcp.server import Context
from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import get_authenticated_paradex_client

from paradex_py.api.models import AccountSummary, AccountSummarySchema, AuthSchema, SystemConfig, SystemConfigSchema


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
async def get_account_positions(ctx: Context) -> Dict[str, Any]:
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
    market_id: str = Field(default=None, description="Filter by market ID."),
    start_unix_ms: int = Field(default=None, description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(default=None, description="End time in unix milliseconds."),
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get account fills.
    
    Returns:
        Dict: Account fills.
    """
    client = await get_authenticated_paradex_client()
    params = {
        "market": market_id,
        "start_at": start_unix_ms,
        "end_at": end_unix_ms
    }
    response = client.fetch_fills(params)
    return response

@server.tool("paradex-account-funding-payments")
async def get_account_funding_payments(
    market_id: str = Field(default=None, description="Filter by market ID."),
    start_unix_ms: int = Field(default=None, description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(default=None, description="End time in unix milliseconds."),
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get account funding payments.
        
    Returns:
        Dict[str, Any]: Account funding payments.
    """
    client = await get_authenticated_paradex_client()
    params = {
        "market": market_id,
        "start_at": start_unix_ms,
        "end_at": end_unix_ms
    }
    response = client.fetch_funding_payments(params)
    return response

