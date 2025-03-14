"""
Order management tools.
"""

from decimal import Decimal
from typing import Any, Literal

from mcp.server.fastmcp.server import Context
from paradex_py.common.order import Order, OrderSide, OrderType
from pydantic import Field

from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import get_authenticated_paradex_client

# Define allowed order types
OrderTypeEnum = Literal[
    "MARKET",
    "LIMIT",
    "STOP_LIMIT",
    "STOP_MARKET",
    "TAKE_PROFIT_LIMIT",
    "TAKE_PROFIT_MARKET",
    "STOP_LOSS_MARKET",
    "STOP_LOSS_LIMIT",
]

# Define allowed instruction types
InstructionEnum = Literal["GTC", "IOC", "POST_ONLY"]
OrderSideEnum = Literal["BUY", "SELL"]


@server.tool("paradex-account-open-orders")
async def get_account_open_orders(
    market_id: str | None = Field(default=None, description="Filter by market."),
    ctx: Context = None,
) -> dict[str, Any]:
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
    price: float
    | None = Field(default=None, description="Order price (required for LIMIT orders)."),
    trigger_price: float
    | None = Field(default=None, description="Trigger price (required for STOP_LIMIT orders)."),
    client_id: str | None = Field(default=None, description="Client-specified order ID."),
    instruction: InstructionEnum = Field(
        default="GTC", description="Instruction for order execution."
    ),
    reduce_only: bool = Field(default=False, description="Reduce-only flag."),
    ctx: Context = None,
) -> dict[str, Any]:
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
        trigger_price=Decimal(str(trigger_price)) if trigger_price else None,
    )
    response = client.submit_order(o)
    return response


@server.tool("paradex-cancel-order")
async def cancel_order(
    order_id: str = Field(description="Order identifier."), ctx: Context = None
) -> dict[str, Any]:
    """
    Cancel an order.

    Returns:
        Dict[str, Any]: Cancelled order details.
    """
    client = await get_authenticated_paradex_client()
    response = client.cancel_order(order_id)
    return response


@server.tool("paradex-cancel-order-by-client-id")
async def cancel_order_by_client_id(
    client_id: str = Field(description="Client-specified order ID."), ctx: Context = None
) -> dict[str, Any]:
    """
    Cancel an order using the client-specified order ID.

    This is useful when you've assigned your own custom IDs to orders and want to cancel
    them using those IDs rather than the exchange-assigned order IDs.

    Returns:
        Dict[str, Any]: Cancelled order details.
    """
    client = await get_authenticated_paradex_client()
    response = client.cancel_order_by_client_id(client_id)
    return response


@server.tool("paradex-cancel-all-orders")
async def cancel_all_orders(
    market_id: str
    | None = Field(default=None, description="Market identifier to cancel orders for."),
    ctx: Context = None,
) -> None:
    """
    Cancel all orders.
    """
    client = await get_authenticated_paradex_client()
    client.cancel_all_orders(market_id)


@server.tool("paradex-get-order-status")
async def get_order_status(
    order_id: str = Field(description="Order identifier."), ctx: Context = None
) -> dict[str, Any]:
    """
    Get order status.

    Returns:
        Dict[str, Any]: Order details.
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_order(order_id)
    return response


@server.tool("paradex-get-order-by-client-id")
async def get_order_by_client_id(
    client_id: str = Field(description="Client-specified order ID."), ctx: Context = None
) -> dict[str, Any]:
    """
    Get order status using client ID.

    Retrieves order details using the client-specified order ID rather than
    the exchange-assigned order ID. This is useful for systems that track
    orders with their own identifiers.

    Returns:
        Dict[str, Any]: Order details including:
            - order_id: Exchange-assigned order identifier
            - client_id: Client-specified order ID
            - market: Market identifier
            - side: Order side (BUY/SELL)
            - type: Order type
            - size: Order size
            - price: Order price
            - status: Order status
            - created_at: Order creation timestamp
            - updated_at: Last update timestamp
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_order_by_client_id(client_id)
    return response


@server.tool("paradex-get-orders-history")
async def get_orders_history(
    market_id: str = Field(description="Filter by market."),
    start_unix_ms: int = Field(description="Start time in unix milliseconds."),
    end_unix_ms: int = Field(description="End time in unix milliseconds."),
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Get historical orders.

    Retrieves the history of orders for the account, including filled, canceled, and expired orders.
    This is useful for analyzing past trading activity and performance.

    Returns:
        Dict[str, Any]: Historical orders with details including:
            - order_id: Order identifier
            - client_id: Client-specified order ID (if provided)
            - market: Market identifier
            - side: Order side (BUY/SELL)
            - type: Order type
            - size: Order size
            - price: Order price
            - status: Order status (FILLED, CANCELED, EXPIRED, etc.)
            - created_at: Order creation timestamp
            - updated_at: Last update timestamp
    """
    client = await get_authenticated_paradex_client()
    params = {"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms}
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}
    response = client.fetch_orders_history(params=params)
    return response
