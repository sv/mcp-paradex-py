"""
Order management tools.
"""

from decimal import Decimal
from typing import Annotated, Any

from mcp.server.fastmcp.server import Context
from mcp.types import ToolAnnotations
from paradex_py.common.order import Order, OrderSide, OrderType
from pydantic import Field, TypeAdapter

from mcp_paradex.models import InstructionEnum, OrderSideEnum, OrderState, OrderTypeEnum
from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import get_authenticated_paradex_client

order_state_adapter = TypeAdapter(list[OrderState])


@server.tool(name="paradex_open_orders", annotations=ToolAnnotations(readOnlyHint=True))
async def get_open_orders(
    market_id: Annotated[str, Field(default="ALL", description="Filter by market.")],
    ctx: Context = None,
) -> list[OrderState]:
    """
    Monitor your active orders to track execution status and manage your trading strategy.

    Use this tool when you need to:
    - Check which of your orders are still pending execution
    - Verify limit order prices and remaining quantities
    - Determine which orders might need cancellation or modification
    - Get a complete picture of your current market exposure

    Keeping track of your open orders is essential for effective order management
    and avoiding duplicate or conflicting trades.

    Example use cases:
    - Checking if your limit orders have been partially filled
    - Verifying that a recently placed order was accepted by the exchange
    - Identifying stale orders that should be canceled or modified
    - Getting a consolidated view of all pending orders across markets
    """
    client = await get_authenticated_paradex_client()
    params = {"market": market_id} if market_id != "" and market_id != "ALL" else None
    response = client.fetch_orders(params=params)
    if "error" in response:
        ctx.error(f"Error fetching open orders: {response['error']}")
        raise Exception(response["error"])
    orders = order_state_adapter.validate_python(response["results"])
    return orders


@server.tool(name="paradex_create_order")
async def create_order(
    market_id: Annotated[str, Field(description="Market identifier.")],
    order_side: Annotated[OrderSideEnum, Field(description="Order side.")],
    order_type: Annotated[OrderTypeEnum, Field(description="Order type.")],
    size: Annotated[float, Field(description="Order size.")],
    price: Annotated[float, Field(description="Order price (required for LIMIT orders).")],
    trigger_price: Annotated[
        float, Field(description="Trigger price (required for STOP_LIMIT orders).")
    ],
    instruction: Annotated[
        InstructionEnum, Field(default="GTC", description="Instruction for order execution.")
    ],
    reduce_only: Annotated[bool, Field(default=False, description="Reduce-only flag.")],
    client_id: Annotated[str, Field(description="Client-specified order ID.")],
    ctx: Context = None,
) -> OrderState:
    """
    Execute trades on Paradex with precise control over all order parameters.

    Use this tool when you need to:
    - Enter a new position based on your trading strategy
    - Set limit orders at specific price levels
    - Create stop-loss or take-profit orders for risk management
    - Implement complex trading strategies with conditional orders

    This is the primary tool for executing your trading decisions on Paradex,
    with full control over order type, size, price, and execution parameters.

    Example use cases:
    - Setting limit orders at key support/resistance levels
    - Placing stop-limit orders to manage risk on existing positions
    - Executing market orders for immediate entry or exit
    - Creating reduce-only orders to ensure you don't flip position direction
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
    order_id: Annotated[
        str, Field(default="", description="Order id (received from create_order)")
    ],
    client_id: Annotated[
        str, Field(default="", description="Client id (provided by you on create_order)")
    ],
    market_id: Annotated[
        str, Field(default="ALL", description="Market is the market to cancel orders for")
    ],
    ctx: Context = None,
) -> OrderState:
    """
    Cancel pending orders to manage exposure or adjust your trading strategy.

    Use this tool when you need to:
    - Remove stale limit orders that are no longer desirable
    - Quickly reduce market exposure during volatility
    - Update your order strategy by removing existing orders
    - Clear your order book before implementing a new strategy
    - React to changing market conditions by canceling pending orders

    Order cancellation is a critical risk management function and allows you
    to quickly adapt to changing market conditions.

    Example use cases:
    - Canceling limit orders when your outlook changes
    - Removing all orders during unexpected market volatility
    - Canceling a specific order identified by order ID
    - Clearing all orders for a specific market
    - Removing stale orders before placing new ones

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
        response = client.cancel_all_orders(market_id)
    else:
        raise Exception("Either order_id or client_id must be provided.")
    order = OrderState(**response)
    return order


@server.tool(name="paradex_order_status")
async def get_order_status(
    order_id: Annotated[str, Field(description="Order identifier.")],
    client_id: Annotated[str, Field(description="Client-specified order ID.")],
    ctx: Context = None,
) -> OrderState:
    """
    Check the detailed status of a specific order for execution monitoring.

    Use this tool when you need to:
    - Confirm if a particular order was accepted and is active
    - Check if an order has been filled, partially filled, or canceled
    - Get execution details for a specific order
    - Diagnose issues with order placement
    - Track the status of important orders individually

    Order status tracking is essential for verifying execution status
    and troubleshooting any issues with specific orders.

    Example use cases:
    - Checking if a recently placed limit order is active in the book
    - Verifying fill details of a specific order
    - Determining why an order might have been rejected
    - Confirming cancellation status of an order you attempted to cancel
    - Getting execution timestamps for order lifecycle analysis
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
    market_id: Annotated[str, Field(description="Filter by market.")],
    start_unix_ms: Annotated[int, Field(description="Start time in unix milliseconds.")],
    end_unix_ms: Annotated[int, Field(description="End time in unix milliseconds.")],
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
        await ctx.error(response)
        raise Exception(response["error"])
    orders_raw: list[dict[str, Any]] = response["results"]
    orders: list[OrderState] = [OrderState(**order) for order in orders_raw]
    return orders
