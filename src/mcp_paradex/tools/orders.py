"""
Order management tools.
"""

from decimal import Decimal
from typing import Any, Literal, Optional

from mcp.server.fastmcp.server import Context
from paradex_py.common.order import Order, OrderSide, OrderType
from pydantic import BaseModel, Field, TypeAdapter

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


# {
#             "id": "1741844800770201709190650000",
#             "account": "0x162a0685d33c626ee6768d309d5bae76d22967ff6f560ff8eb726ee1bef5778",
#             "market": "BTC-USD-PERP",
#             "side": "SELL",
#             "type": "LIMIT",
#             "size": "0.002",
#             "remaining_size": "0",
#             "price": "83170",
#             "status": "CLOSED",
#             "created_at": 1741844800770,
#             "last_updated_at": 1741844825512,
#             "timestamp": 0,
#             "cancel_reason": "",
#             "client_id": "",
#             "seq_no": 1741844825512593648,
#             "instruction": "GTC",
#             "avg_fill_price": "83170",
#             "stp": "EXPIRE_TAKER",
#             "received_at": 1741935870847,
#             "published_at": 1741935870902,
#             "flags": [
#                 "REDUCE_ONLY"
#             ],
#             "trigger_price": "0"
#         }
class OrderState(BaseModel):
    id: str
    account: str
    market: str
    side: OrderSide
    type: OrderType
    size: float
    remaining_size: float
    price: float
    status: str
    created_at: int
    last_updated_at: int
    timestamp: int
    cancel_reason: str
    client_id: str
    seq_no: int
    instruction: InstructionEnum
    avg_fill_price: str
    stp: str
    received_at: int
    published_at: int
    flags: list[str]
    trigger_price: str


order_state_adapter = TypeAdapter(list[OrderState])


@server.tool("paradex-account-open-orders")
async def get_account_open_orders(
    market_id: str = Field(default="ALL", description="Filter by market."),
    ctx: Context = None,
) -> list[OrderState]:
    """
    Get account open orders.
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_orders(params={"market": market_id})
    orders = order_state_adapter.validate_python(response["results"])
    return orders


@server.tool("paradex-create-order")
async def create_order(
    market_id: str = Field(description="Market identifier."),
    order_side: OrderSideEnum = Field(description="Order side."),
    order_type: OrderTypeEnum = Field(description="Order type."),
    size: float = Field(description="Order size."),
    price: float = Field(description="Order price (required for LIMIT orders)."),
    trigger_price: float = Field(description="Trigger price (required for STOP_LIMIT orders)."),
    client_id: str = Field(description="Client-specified order ID."),
    instruction: InstructionEnum = Field(
        default="GTC", description="Instruction for order execution."
    ),
    reduce_only: bool = Field(default=False, description="Reduce-only flag."),
    ctx: Context = None,
) -> OrderState:
    """
    Create a new order.
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


@server.tool("paradex-cancel-order")
async def cancel_order(
    order_id: str = Field(description="Order identifier."), ctx: Context = None
) -> None:
    """
    Cancel an order.
    """
    client = await get_authenticated_paradex_client()
    client.cancel_order(order_id)


@server.tool("paradex-cancel-order-by-client-id")
async def cancel_order_by_client_id(
    client_id: str = Field(description="Client-specified order ID."), ctx: Context = None
) -> None:
    """
    Cancel an order using the client-specified order ID.

    This is useful when you've assigned your own custom IDs to orders and want to cancel
    them using those IDs rather than the exchange-assigned order IDs.

    """
    client = await get_authenticated_paradex_client()
    client.cancel_order_by_client_id(client_id)


@server.tool("paradex-cancel-all-orders")
async def cancel_all_orders(
    market_id: str | None = Field(
        default=None, description="Market identifier to cancel orders for."
    ),
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
) -> OrderState:
    """
    Get order status.
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_order(order_id)
    order: OrderState = OrderState(**response)
    return order


@server.tool("paradex-get-order-by-client-id")
async def get_order_by_client_id(
    client_id: str = Field(description="Client-specified order ID."), ctx: Context = None
) -> OrderState:
    """
    Get order status using client order ID.
    """
    client = await get_authenticated_paradex_client()
    response = client.fetch_order_by_client_id(client_id)
    return OrderState(**response)


@server.tool("paradex-get-orders-history")
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
    orders_raw: list[dict[str, Any]] = response["results"]
    orders: list[OrderState] = [OrderState(**order) for order in orders_raw]
    return orders
