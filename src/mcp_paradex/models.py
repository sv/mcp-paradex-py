"""
Pydantic models for the MCP Paradex application.

This module contains all Pydantic models used across the application.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# System models
class SystemState(BaseModel):
    """Model representing the current state of the Paradex system."""

    status: str
    timestamp: int = Field(default=0)


# Market models
class BBO(BaseModel):
    """Best Bid and Offer model for a market."""

    market: Annotated[str, Field(description="Symbol of the market")]
    seq_no: Annotated[int, Field(description="Sequence number of the orderbook")]
    ask: Annotated[float, Field(description="Best ask price")]
    ask_size: Annotated[float, Field(description="Best ask size")]
    bid: Annotated[float, Field(description="Best bid price")]
    bid_size: Annotated[float, Field(description="Best bid size")]
    last_updated_at: Annotated[
        int, Field(description="Last update to the orderbook in milliseconds")
    ]


class Trade(BaseModel):
    """Trade model representing a completed trade on Paradex."""

    id: Annotated[str, Field(description="Unique Trade ID per TradeType")]
    market: Annotated[str, Field(description="Market for which trade was done")]
    side: Annotated[str, Field(description="Taker side")]
    size: Annotated[float, Field(description="Trade size")]
    price: Annotated[float, Field(description="Trade price")]
    created_at: Annotated[
        int, Field(description="Unix Millisecond timestamp at which trade was done")
    ]
    trade_type: Annotated[str, Field(description="Trade type, can be FILL or LIQUIDATION")]


# Account models
class Position(BaseModel):
    """Position model representing a trading position on Paradex."""

    id: Annotated[str, Field(description="Unique string ID for the position")]
    account: Annotated[str, Field(description="Account ID of the position")]
    market: Annotated[str, Field(description="Market for position")]
    status: Annotated[
        str, Field(description="Status of Position : Open or Closed", enum=["OPEN", "CLOSED"])
    ]
    side: Annotated[str, Field(description="Position Side : Long or Short", enum=["SHORT", "LONG"])]
    size: Annotated[
        float,
        Field(description="Size of the position with sign (positive if long or negative if short)"),
    ]
    average_entry_price: Annotated[float, Field(description="Average entry price")]
    average_entry_price_usd: Annotated[float, Field(description="Average entry price in USD")]
    average_exit_price: Annotated[float, Field(description="Average exit price")]
    unrealized_pnl: Annotated[
        float, Field(description="Unrealized P&L of the position in the quote asset")
    ]
    unrealized_funding_pnl: Annotated[
        float, Field(description="Unrealized running funding P&L for the position")
    ]
    cost: Annotated[float, Field(description="Position cost")]
    cost_usd: Annotated[float, Field(description="Position cost in USD")]
    cached_funding_index: Annotated[float, Field(description="Position cached funding index")]
    last_updated_at: Annotated[int, Field(description="Position last update time")]
    last_fill_id: Annotated[
        str, Field(description="Last fill ID to which the position is referring")
    ]
    seq_no: Annotated[
        int,
        Field(
            description="Unique increasing number (non-sequential) that is assigned to this position update. Can be used to deduplicate multiple feeds"
        ),
    ]
    liquidation_price: Annotated[
        str, Field(default="", description="Liquidation price of the position")
    ]
    leverage: Annotated[float, Field(default=0, description="Leverage of the position")]
    realized_positional_pnl: Annotated[
        float,
        Field(
            default=0,
            description="Realized PnL including both positional PnL and funding payments. Reset to 0 when position is closed or flipped.",
        ),
    ]
    created_at: Annotated[int, Field(default=0, description="Position creation time")]
    closed_at: Annotated[int, Field(default=0, description="Position closed time")]
    realized_positional_funding_pnl: Annotated[
        str,
        Field(
            default="",
            description="Realized Funding PnL for the position. Reset to 0 when position is closed or flipped.",
        ),
    ]


class Fill(BaseModel):
    """Fill model representing a trade fill on Paradex."""

    id: Annotated[str, Field(description="Unique string ID of fill per FillType")]
    side: Annotated[str, Field(description="Taker side")]
    liquidity: Annotated[str, Field(description="Maker or Taker")]
    market: Annotated[str, Field(description="Market name")]
    order_id: Annotated[str, Field(description="Order ID")]
    price: Annotated[float, Field(description="Price at which order was filled")]
    size: Annotated[float, Field(description="Size of the fill")]
    fee: Annotated[float, Field(description="Fee paid by the user")]
    fee_currency: Annotated[str, Field(description="Asset that fee is charged in")]
    created_at: Annotated[int, Field(description="Fill time")]
    remaining_size: Annotated[float, Field(description="Remaining size of the order")]
    client_id: Annotated[str, Field(description="Unique client assigned ID for the order")]
    fill_type: Annotated[str, Field(description="Fill type, can be FILL, LIQUIDATION or TRANSFER")]
    realized_pnl: Annotated[float, Field(description="Realized PnL of the fill")]
    realized_funding: Annotated[float, Field(description="Realized funding of the fill")]
    account: Annotated[str, Field(default="", description="Account that made the fill")]
    underlying_price: Annotated[
        str, Field(default="", description="Underlying asset price of the fill (spot price)")
    ]


class Transaction(BaseModel):
    """Transaction model representing an account transaction on Paradex."""

    id: Annotated[
        str, Field(description="Unique string ID of the event that triggered the transaction")
    ]
    type: Annotated[str, Field(description="Event that triggered the transaction")]
    hash: Annotated[str, Field(description="Tx Hash of the settled trade")]
    state: Annotated[str, Field(description="Status of the transaction on Starknet")]
    created_at: Annotated[
        int, Field(description="Timestamp from when the transaction was sent to blockchain gateway")
    ]
    completed_at: Annotated[
        int, Field(description="Timestamp from when the transaction was completed")
    ]


# Order models
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


class OrderState(BaseModel):
    """Order state model representing the current state of an order on Paradex."""

    id: Annotated[str, Field(description="Unique order identifier generated by Paradex")]
    account: Annotated[str, Field(description="Paradex Account")]
    market: Annotated[str, Field(description="Market")]
    side: Annotated[str, Field(description="Order side")]
    type: Annotated[str, Field(description="Order type")]
    size: Annotated[float, Field(description="Order size")]
    remaining_size: Annotated[float, Field(description="Remaining size of the order")]
    price: Annotated[float, Field(description="Order price. 0 for MARKET orders")]
    status: Annotated[str, Field(description="Order status")]
    created_at: Annotated[int, Field(description="Order creation time")]
    last_updated_at: Annotated[
        int, Field(description="Order last update time. No changes once status=CLOSED")
    ]
    timestamp: Annotated[int, Field(description="Order signature timestamp")]
    cancel_reason: Annotated[
        str, Field(description="Reason for order cancellation if it was closed by cancel")
    ]
    client_id: Annotated[
        str, Field(description="Client order id provided by the client at order creation")
    ]
    seq_no: Annotated[
        int,
        Field(
            description="Unique increasing number that is assigned to this order update and changes on every order update"
        ),
    ]
    instruction: Annotated[str, Field(description="Execution instruction for order matching")]
    avg_fill_price: Annotated[str, Field(description="Average fill price of the order")]
    stp: Annotated[str, Field(description="Self Trade Prevention mode")]
    received_at: Annotated[
        int, Field(description="Timestamp in milliseconds when order was received by API service")
    ]
    published_at: Annotated[
        int, Field(description="Timestamp in milliseconds when order was sent to the client")
    ]
    flags: Annotated[list[str], Field(description="Order flags, allow flag: REDUCE_ONLY")]
    trigger_price: Annotated[str, Field(description="Trigger price for stop order")]


class VaultStrategy(BaseModel):
    """Vault strategy model representing a strategy for a vault on Paradex."""

    address: Annotated[str, Field(description="Contract address of the sub-operator")]
    name: Annotated[str, Field(description="Strategy name")]


# Vault models
class Vault(BaseModel):
    """Vault model representing a trading vault on Paradex."""

    address: Annotated[str, Field(description="Contract address of the vault")]
    name: Annotated[str, Field(description="Name of the vault")]
    description: Annotated[str, Field(description="Description of the vault")]
    owner_account: Annotated[str, Field(description="Owner account of the vault")]
    operator_account: Annotated[str, Field(description="Operator account of the vault")]
    strategies: Annotated[list[str], Field(description="Strategies of the vault")]
    token_address: Annotated[str, Field(description="LP token address")]
    status: Annotated[str, Field(description="Status of the vault")]
    kind: Annotated[
        str,
        Field(
            description="Kind of the vault: 'user' for user-defined vaults, 'protocol' for vaults controlled by Paradex"
        ),
    ]
    profit_share: Annotated[
        int, Field(description="Profit share of the vault in percentage, i.e. 10 means 10%")
    ]
    lockup_period: Annotated[int, Field(description="Lockup period of the vault in days")]
    max_tvl: Annotated[
        int, Field(description="Maximum amount of assets the vault can hold in USDC")
    ]
    created_at: Annotated[
        int, Field(description="Unix timestamp in milliseconds of when the vault has been created")
    ]
    last_updated_at: Annotated[
        int, Field(description="Unix timestamp in milliseconds of when the vault was last updated")
    ]


class VaultBalance(BaseModel):
    """Model representing the balance of a vault."""

    token: Annotated[str, Field(description="Name of the token")]
    size: Annotated[str, Field(description="Balance amount of settlement token")]
    last_updated_at: Annotated[int, Field(description="Balance last updated time")]


class VaultSummary(BaseModel):
    """Model representing a summary of a vault's performance and statistics."""

    address: Annotated[str, Field(description="Contract address of the vault")]
    owner_equity: Annotated[
        str,
        Field(
            description="Vault equity of the owner (% of ownership) in percentage, i.e. 0.1 means 10%"
        ),
    ]
    vtoken_supply: Annotated[str, Field(description="Total amount of available vault tokens")]
    vtoken_price: Annotated[str, Field(description="Current value of vault token price in USD")]
    tvl: Annotated[
        str,
        Field(
            description="Net deposits of the vault in USDC (deprecated; use net_deposits instead)"
        ),
    ]
    net_deposits: Annotated[str, Field(description="Net deposits of the vault in USDC")]
    total_roi: Annotated[
        str, Field(description="Total ROI of the vault in percentage, i.e. 0.1 means 10%")
    ]
    roi_24h: Annotated[
        str,
        Field(
            description="Return of the vault in the last 24 hours in percentage, i.e. 0.1 means 10%"
        ),
    ]
    roi_7d: Annotated[
        str,
        Field(
            description="Return of the vault in the last 7 days in percentage, i.e. 0.1 means 10%"
        ),
    ]
    roi_30d: Annotated[
        str,
        Field(
            description="Return of the vault in the last 30 days in percentage, i.e. 0.1 means 10%"
        ),
    ]
    last_month_return: Annotated[
        str,
        Field(
            description="APR return of the vault in the last trailing month in percentage, i.e. 0.1 means 10%"
        ),
    ]
    total_pnl: Annotated[str, Field(description="Total P&L of the vault in USD")]
    pnl_24h: Annotated[str, Field(description="P&L of the vault in the last 24 hours in USD")]
    pnl_7d: Annotated[str, Field(description="P&L of the vault in the last 7 days in USD")]
    pnl_30d: Annotated[str, Field(description="P&L of the vault in the last 30 days in USD")]
    max_drawdown: Annotated[
        str,
        Field(
            description="Max all time drawdown realized by the vault in percentage, i.e. 0.1 means 10%"
        ),
    ]
    max_drawdown_24h: Annotated[
        str,
        Field(
            description="Max drawdown realized by the vault in the last 24 hours in percentage, i.e. 0.1 means 10%"
        ),
    ]
    max_drawdown_7d: Annotated[
        str,
        Field(
            description="Max drawdown realized by the vault in the last 7 days in percentage, i.e. 0.1 means 10%"
        ),
    ]
    max_drawdown_30d: Annotated[
        str,
        Field(
            description="Max drawdown realized by the vault in the last 30 days in percentage, i.e. 0.1 means 10%"
        ),
    ]
    volume: Annotated[str, Field(description="All time volume traded by the vault in USD")]
    volume_24h: Annotated[
        str, Field(description="Volume traded by the vault in the last 24 hours in USD")
    ]
    volume_7d: Annotated[
        str, Field(description="Volume traded by the vault in the last 7 days in USD")
    ]
    volume_30d: Annotated[
        str, Field(description="Volume traded by the vault in the last 30 days in USD")
    ]
    num_depositors: Annotated[int, Field(description="Number of depositors on the vault")]


class VaultAccountSummary(BaseModel):
    """Model representing an account summary for a vault."""

    address: Annotated[str, Field(description="Contract address of the vault")]
    deposited_amount: Annotated[
        str, Field(description="Amount deposited on the vault by the user in USDC")
    ]
    vtoken_amount: Annotated[str, Field(description="Amount of vault tokens owned by the user")]
    total_roi: Annotated[
        str, Field(description="Total ROI realized by the user in percentage, i.e. 0.1 means 10%")
    ]
    total_pnl: Annotated[str, Field(description="Total P&L realized by the user in USD")]
    created_at: Annotated[
        int, Field(description="Unix timestamp in milliseconds of when the user joined the vault")
    ]


class Greeks(BaseModel):
    """Model representing the Greeks of a market."""

    delta: Annotated[float, Field(default=0.0, description="Market Delta")]
    gamma: Annotated[float, Field(default=0.0, description="Market Gamma")]
    vega: Annotated[float, Field(default=0.0, description="Market Vega")]
    rho: Annotated[float, Field(default=0.0, description="Market Rho")]
    vanna: Annotated[float, Field(default=0.0, description="Market Vanna")]
    volga: Annotated[float, Field(default=0.0, description="Market Volga")]

    # Allow additional fields beyond the defined ones
    model_config = {"extra": "allow"}


class MarketSummary(BaseModel):
    """Model representing a summary of a market."""

    symbol: Annotated[str, Field(description="Market symbol")]
    mark_price: Annotated[str, Field(description="Mark price")]
    delta: Annotated[str, Field(default="", description="Deprecated: Use greeks.delta instead")]
    greeks: Annotated[
        Greeks,
        Field(
            default=None, description="Greeks (delta, gamma, vega). Partial for perpetual futures"
        ),
    ]
    last_traded_price: Annotated[str, Field(description="Last traded price")]
    bid: Annotated[str, Field(description="Best bid price")]
    ask: Annotated[str, Field(description="Best ask price")]
    volume_24h: Annotated[str, Field(description="24 hour volume in USD")]
    total_volume: Annotated[str, Field(description="Lifetime total traded volume in USD")]
    created_at: Annotated[int, Field(description="Market summary creation time")]
    underlying_price: Annotated[str, Field(description="Underlying asset price (spot price)")]
    open_interest: Annotated[str, Field(description="Open interest in base currency")]
    funding_rate: Annotated[str, Field(description="8 hour funding rate")]
    price_change_rate_24h: Annotated[
        str, Field(description="Price change rate in the last 24 hours")
    ]


class MarketDetails(BaseModel):
    """Model representing the details of a market."""

    symbol: Annotated[str, Field(description="Market symbol")]
    base_currency: Annotated[str, Field(description="Base currency of the market")]
    quote_currency: Annotated[str, Field(description="Quote currency of the market")]
    settlement_currency: Annotated[str, Field(description="Settlement currency of the market")]
    order_size_increment: Annotated[
        str, Field(description="Minimum size increment for base currency")
    ]
    price_tick_size: Annotated[
        float, Field(description="Minimum price increment of the market in USD")
    ]
    min_notional: Annotated[float, Field(description="Minimum order size in USD")]
    open_at: Annotated[int, Field(description="Market open time in milliseconds")]
    expiry_at: Annotated[int, Field(description="Market expiry time")]
    asset_kind: Annotated[str, Field(description="Type of asset")]
    market_kind: Annotated[str, Field(description="Type of market - always 'cross'")]
    position_limit: Annotated[float, Field(description="Position limit")]
    price_bands_width: Annotated[
        float,
        Field(
            description="Price Bands Width, 0.05 means 5% price deviation allowed from mark price"
        ),
    ]
    max_open_orders: Annotated[int, Field(description="Max open orders")]
    max_funding_rate: Annotated[float, Field(description="Max funding rate")]
    delta1_cross_margin_params: Annotated[
        dict[str, float], Field(default_factory=dict, description="Delta1 Cross margin parameters")
    ]
    option_cross_margin_params: Annotated[
        dict[str, dict[str, float]],
        Field(default_factory=dict, description="Option Cross margin parameters"),
    ]
    price_feed_id: Annotated[
        str, Field(description="Price feed id. Pyth price account used to price underlying asset")
    ]
    oracle_ewma_factor: Annotated[float, Field(description="Oracle EWMA factor")]
    max_order_size: Annotated[float, Field(description="Maximum order size in base currency")]
    max_funding_rate_change: Annotated[float, Field(description="Max funding rate change")]
    max_tob_spread: Annotated[
        float, Field(description="The maximum TOB spread allowed to apply funding rate changes")
    ]
    interest_rate: Annotated[float, Field(description="Interest rate")]
    clamp_rate: Annotated[float, Field(description="Clamp rate")]
    funding_period_hours: Annotated[int, Field(description="Funding period in hours")]
    tags: Annotated[list[str], Field(description="Market tags")]
    option_type: Annotated[str, Field(default="", description="Type of option (PUT or CALL)")]
    strike_price: Annotated[float, Field(default=0.0, description="Strike price for option market")]
    iv_bands_width: Annotated[float, Field(default=0.0, description="IV Bands Width")]


class AccountSummary(BaseModel):
    """Model representing an account summary response from Paradex."""

    account: Annotated[str, Field(description="User's starknet account")]
    account_value: Annotated[str, Field(description="Current account value [with unrealized P&Ls]")]
    free_collateral: Annotated[
        str,
        Field(
            description="Free collateral available (Account value in excess of Initial Margin required)"
        ),
    ]
    initial_margin_requirement: Annotated[
        str, Field(description="Amount required to open trade for the existing positions")
    ]
    maintenance_margin_requirement: Annotated[
        str, Field(description="Amount required to maintain exisiting positions")
    ]
    margin_cushion: Annotated[
        str, Field(description="Acc value in excess of maintenance margin required")
    ]
    seq_no: Annotated[
        int,
        Field(
            description="Unique increasing number (non-sequential) that is assigned to this account update. Can be used to deduplicate multiple feeds"
        ),
    ]
    settlement_asset: Annotated[str, Field(description="Settlement asset for the account")]
    status: Annotated[str, Field(description="Status of the acc - like ACTIVE, LIQUIDATION")]
    total_collateral: Annotated[str, Field(description="User's total collateral")]
    updated_at: Annotated[int, Field(description="Account last updated time")]
