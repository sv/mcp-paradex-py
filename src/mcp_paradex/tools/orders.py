"""
Order management tools.
"""
from typing import Dict, Any

from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import get_authenticated_paradex_client

@server.tool("paradex-account-open-orders")
async def get_account_open_orders(
    market_id: str = None,
) -> Dict[str, Any]:
    """
    Get account open orders.
    
    Args:
        market_id (str, optional): Filter by market ID.
        
    Returns:
        Dict[str, Any]: Account orders.
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_orders(market_id)
    return response

@server.tool("paradex-create-order")
async def create_order(
    market_id: str,
    side: str,
    type: str,
    size: str,
    price: str = None,
    client_id: str = None,
    time_in_force: str = None,
    post_only: bool = None,
    reduce_only: bool = None
) -> Dict[str, Any]:
    """
    Create a new order.
    
    Args:
        market_id (str): Market identifier.
        side (str): Order side (BUY/SELL).
        type (str): Order type (LIMIT/MARKET).
        size (str): Order size.
        price (str, optional): Order price (required for LIMIT orders).
        client_id (str, optional): Client-specified order ID.
        time_in_force (str, optional): Time in force (GTC/IOC/FOK).
        post_only (bool, optional): Post-only flag.
        reduce_only (bool, optional): Reduce-only flag.
        
    Returns:
        Dict[str, Any]: Created order details.
    """
    client = await get_authenticated_paradex_client()
    data = {k: v for k, v in locals().items() if v is not None and k != 'client'}
    response = client.submit_order(data)
    return response

@server.tool("paradex-cancel-order")
async def cancel_order(order_id: str) -> Dict[str, Any]:
    """
    Cancel an order.
    
    Args:
        order_id (str): Order identifier.
        
    Returns:
        Dict[str, Any]: Cancelled order details.
    """
    client = await get_authenticated_paradex_client()
    response = client.cancel_order(order_id)
    return response

@server.tool("paradex-cancel-all-orders")
async def cancel_all_orders(market_id: str = None) -> Dict[str, Any]:
    """
    Cancel all orders.
    
    Args:
        market_id (str, optional): Market identifier to cancel orders for.
        
    Returns:
        Dict[str, Any]: Result of cancellation.
    """
    client = await get_authenticated_paradex_client()
    response = client.cancel_all_orders(market_id)
    return response

@server.tool("paradex-get-order-status")
async def get_order_status(order_id: str) -> Dict[str, Any]:
    """
    Get order status.
    
    Args:
        order_id (str): Order identifier.
        
    Returns:
        Dict[str, Any]: Order details.
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_order(order_id)
    return response 