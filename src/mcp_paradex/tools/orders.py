"""
Order management tools.
"""
from decimal import Decimal
from typing import Dict, Any, Literal
from enum import Enum

from pydantic import Field

from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import get_authenticated_paradex_client
from paradex_py.common.order import Order, OrderSide, OrderType
from mcp.server.fastmcp.server import Context

# Define allowed order types
OrderTypeEnum = Literal["MARKET", "LIMIT", "STOP_LIMIT", "STOP_MARKET", "TAKE_PROFIT_LIMIT", "TAKE_PROFIT_MARKET", "STOP_LOSS_MARKET", "STOP_LOSS_LIMIT"]

# Define allowed instruction types
InstructionEnum = Literal["GTC", "IOC", "POST_ONLY"]
OrderSideEnum = Literal["BUY", "SELL"]

@server.tool("paradex-account-open-orders")
async def get_account_open_orders(
    market_id: str = Field(default=None, description="Filter by market."),
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get account open orders.        
    Returns:
        Dict[str, Any]: Account orders.
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_orders(params={"market": market_id})
    return response

@server.tool("paradex-create-order")
async def create_order(
    market_id: str = Field(description="Market identifier."),
    order_side: OrderSideEnum = Field(description="Order side."),
    order_type: OrderTypeEnum = Field(description="Order type."),
    size: float = Field(description="Order size."),
    price: float = Field(default=None, description="Order price (required for LIMIT orders)."),
    trigger_price: float = Field(default=None, description="Trigger price (required for STOP_LIMIT orders)."),
    client_id: str = Field(default=None, description="Client-specified order ID."),
    instruction: InstructionEnum = Field(default="GTC", description="Instruction for order execution."),
    reduce_only: bool = Field(default=False, description="Reduce-only flag."),
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Create a new order.

    Returns:
        Dict[str, Any]: Created order details.
    """
    client = await get_authenticated_paradex_client()
    o = Order(
        market=market_id,
        order_side=OrderSide(order_side),
        order_type=OrderType(order_type),
        size=Decimal(str(size)),
        client_id=client_id,
        limit_price=Decimal(str(price)) if price else Decimal(0),
        reduce_only=reduce_only,
        instruction=instruction,
        trigger_price=Decimal(str(trigger_price)) if trigger_price else None
    )
    response = client.submit_order(o)
    return response

@server.tool("paradex-cancel-order")
async def cancel_order(order_id: str = Field(description="Order identifier."), ctx: Context = None) -> None:
    """
    Cancel an order.
        
    Returns:
        Dict[str, Any]: Cancelled order details.
    """
    client = await get_authenticated_paradex_client()
    client.cancel_order(order_id)
    
@server.tool("paradex-cancel-all-orders")
async def cancel_all_orders(market_id: str = Field(default=None, description="Market identifier to cancel orders for."), ctx: Context = None) -> None:
    """
    Cancel all orders.
    """
    client = await get_authenticated_paradex_client()
    client.cancel_all_orders(market_id)

@server.tool("paradex-get-order-status")
async def get_order_status(order_id: str = Field(description="Order identifier."), ctx: Context = None) -> Dict[str, Any]:
    """
    Get order status.

    Returns:
        Dict[str, Any]: Order details.
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_order(order_id)
    return response 