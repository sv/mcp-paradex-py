"""
Account management tools.
"""
from typing import Dict, Any

from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import get_authenticated_paradex_client, api_call

@server.tool("paradex-account-info")
async def get_account_summary() -> Dict[str, Any]:
    """
    Get account summary.
    
    Returns:
        Dict[str, Any]: Account summary.
    """
    client = await get_authenticated_paradex_client()
    response = await client.fetch_account_summary()
    return response

@server.tool("paradex-account-positions")
async def get_account_positions() -> Dict[str, Any]:
    """
    Get account positions.
    
    Returns:
        Dict[str, Any]: Account positions.
    """
    client = await get_authenticated_paradex_client()
    response = await client.fetch_positions()
    return response

@server.tool("paradex-account-fills")
async def get_account_fills(
    market_id: str = None,
    start_unix_ms: int = None,
    end_unix_ms: int = None
) -> Dict[str, Any]:
    """
    Get account fills.
    
    Args:
        market_id (str, optional): Filter by market ID.
        start_unix_ms (int, optional): Start time in unix milliseconds.
        end_unix_ms (int, optional): End time in unix milliseconds.
        
    Returns:
        Dict[str, Any]: Account fills.
    """
    client = await get_authenticated_paradex_client()
    params = {
        "market": market_id,
        "start_at": start_unix_ms,
        "end_at": end_unix_ms
    }
    response = await client.fetch_fills(params)
    return response

@server.tool("paradex-account-funding-payments")
async def get_account_funding_payments(
    market_id: str = None,
    start_unix_ms: int = None,
    end_unix_ms: int = None
) -> Dict[str, Any]:
    """
    Get account funding payments.
    
    Args:
        market_id (str, optional): Filter by market ID.
        start_unix_ms (int, optional): Start time in unix milliseconds.
        end_unix_ms (int, optional): End time in unix milliseconds.
        
    Returns:
        Dict[str, Any]: Account funding payments.
    """
    client = await get_authenticated_paradex_client()
    params = {
        "market": market_id,
        "start_at": start_unix_ms,
        "end_at": end_unix_ms
    }
    response = await client.fetch_funding_payments(params)
    return response

