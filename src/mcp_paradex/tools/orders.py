"""
Order management tools.
"""

from decimal import Decimal
from typing import Any, Optional

from mcp.server.fastmcp.server import Context
from paradex_py.common.order import Order, OrderSide, OrderType
from pydantic import Field, TypeAdapter

from mcp_paradex.models import InstructionEnum, OrderSideEnum, OrderState, OrderTypeEnum
from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import get_authenticated_paradex_client

order_state_adapter = TypeAdapter(list[OrderState])


@server.tool(name="paradex_open_orders")
async def get_open_orders(
    market_id: str = Field(default="ALL", description="Filter by market."),
    ctx: Context = None,
) -> list[OrderState]:
    """
    Get open orders for a market or all markets if market_id is not provided.
    """
    client = await get_authenticated_paradex_client()
    params = {"market": market_id} if market_id != "" and market_id != "ALL" else None
    response = client.fetch_orders(params=params)
    if "error" in response:
        ctx.logger.error(f"Error fetching open orders: {response['error']}")
        raise Exception(response["error"])
    orders = order_state_adapter.validate_python(response["results"])
    return orders


@server.tool(name="paradex_create_order")
async def create_order(
    market_id: str = Field(description="Market identifier."),
    order_side: OrderSideEnum = Field(description="Order side."),
    order_type: OrderTypeEnum = Field(description="Order type."),
    size: float = Field(description="Order size."),
    price: float = Field(description="Order price (required for LIMIT orders)."),
    trigger_price: float = Field(description="Trigger price (required for STOP_LIMIT orders)."),
    instruction: InstructionEnum = Field(
        default="GTC", description="Instruction for order execution."
    ),
    reduce_only: bool = Field(default=False, description="Reduce-only flag."),
    client_id: str = Field(description="Client-specified order ID."),
    ctx: Context = None,
) -> OrderState:
    """
    Create a new order.
    Response indicates that the order was accepted for processing. Check order status using order id.
    Order parameters must follow requirements for the market.
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
        trigger_price=Decimal(str(trigger_price)) if trigger_price else None,
    )
    response = client.submit_order(o)
    order: OrderState = OrderState(**response)
    return order


@server.tool(name="paradex_cancel_orders")
async def cancel_orders(
    order_id: str = Field(default="", description="Order identifier."),
    client_id: str = Field(default="", description="Client-specified order ID."),
    market_id: str = Field(default="ALL", description="Market identifier."),
    ctx: Context = None,
) -> OrderState:
    """
    Cancel an order by order id (received from create_order) or client id (provided by you on create_order).
    If only market_id is provided, cancels all orders for the market. market_id defaults to ALL.
    Calling without any parameters will cancel all orders.

    Succesful response indicates that orders were queued for cancellation.
    Check order status using order id.
    """
    client = await get_authenticated_paradex_client()
    if order_id:
        response = client.cancel_order(order_id)
    elif client_id:
        response = client.cancel_order_by_client_id(client_id)
    elif market_id:
        response = client.cancel_orders(market_id)
    else:
        raise Exception("Either order_id or client_id must be provided.")
    order = OrderState(**response)
    return order


@server.tool(name="paradex_order_status")
async def get_order_status(
    order_id: str = Field(description="Order identifier."),
    client_id: str = Field(description="Client-specified order ID."),
    ctx: Context = None,
) -> OrderState:
    """
    Get order status by order id (received from create_order) or client id (provided by you on create_order).
    """
    client = await get_authenticated_paradex_client()
    if order_id:
        response = client.fetch_order(order_id)
    elif client_id:
        response = client.fetch_order_by_client_id(client_id)
    else:
        raise Exception("Either order_id or client_id must be provided.")
    order: OrderState = OrderState.model_validate(response)
    return order


@server.tool(name="paradex_orders_history")
async def get_orders_history(
    market_id: str = Field(description="Filter by market."),
    start_unix_ms: int = Field(description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(description="End time in unix milliseconds."),
    ctx: Context = None,
) -> list[OrderState]:
    """
    Get historical orders.

    Retrieves the history of orders for the account, including filled, canceled, and expired orders.
    This is useful for analyzing past trading activity and performance.
    """
    client = await get_authenticated_paradex_client()
    params = {"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}
    response = client.fetch_orders_history(params=params)
    if "error" in response:
        ctx.logger.error(f"Error fetching orders history: {response['error']}")
        raise Exception(response["error"])
    orders_raw: list[dict[str, Any]] = response["results"]
    orders: list[OrderState] = [OrderState(**order) for order in orders_raw]
    return orders
