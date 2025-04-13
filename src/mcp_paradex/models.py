"""
Pydantic models for the MCP Paradex application.

This module contains all Pydantic models used across the application.
"""

from typing import Literal

from pydantic import BaseModel, Field


# System models
class SystemState(BaseModel):
    """Model representing the current state of the Paradex system."""

    status: str
    timestamp: int = Field(default=0)


# Market models
class BBO(BaseModel):
    """Best Bid and Offer model for a market."""

    market: str
    seq_no: int
    ask: float
    ask_size: float
    bid: float
    bid_size: float
    last_updated_at: int


class Trade(BaseModel):
    """Trade model representing a completed trade on Paradex."""

    id: str
    market: str
    side: str
    size: float
    price: float
    created_at: int
    trade_type: str


# Account models
class Position(BaseModel):
    """Position model representing a trading position on Paradex."""

    id: str = Field(description="Unique string ID for the position")
    account: str = Field(description="Account ID of the position")
    market: str = Field(description="Market for position")
    status: str = Field(description="Status of Position : Open or Closed", enum=["OPEN", "CLOSED"])
    side: str = Field(description="Position Side : Long or Short", enum=["SHORT", "LONG"])
    size: float = Field(
        description="Size of the position with sign (positive if long or negative if short)"
    )
    average_entry_price: float = Field(description="Average entry price")
    average_entry_price_usd: float = Field(description="Average entry price in USD")
    average_exit_price: float = Field(description="Average exit price")
    unrealized_pnl: float = Field(description="Unrealized P&L of the position in the quote asset")
    unrealized_funding_pnl: float = Field(
        description="Unrealized running funding P&L for the position"
    )
    cost: float = Field(description="Position cost")
    cost_usd: float = Field(description="Position cost in USD")
    cached_funding_index: float = Field(description="Position cached funding index")
    last_updated_at: int = Field(description="Position last update time")
    last_fill_id: str = Field(description="Last fill ID to which the position is referring")
    seq_no: int = Field(
        description="Unique increasing number (non-sequential) that is assigned to this position update. Can be used to deduplicate multiple feeds"
    )
    liquidation_price: str = Field(default="", description="Liquidation price of the position")
    leverage: float = Field(default=0, description="Leverage of the position")
    realized_positional_pnl: float = Field(
        default=0,
        description="Realized PnL including both positional PnL and funding payments. Reset to 0 when position is closed or flipped.",
    )
    created_at: int = Field(default=0, description="Position creation time")
    closed_at: int = Field(default=0, description="Position closed time")
    realized_positional_funding_pnl: str = Field(
        default="",
        description="Realized Funding PnL for the position. Reset to 0 when position is closed or flipped.",
    )


class Fill(BaseModel):
    """Fill model representing a trade fill on Paradex."""

    id: str = Field(description="Unique string ID of fill per FillType")
    side: str = Field(description="Taker side")
    liquidity: str = Field(description="Maker or Taker")
    market: str = Field(description="Market name")
    order_id: str = Field(description="Order ID")
    price: float = Field(description="Price at which order was filled")
    size: float = Field(description="Size of the fill")
    fee: float = Field(description="Fee paid by the user")
    fee_currency: str = Field(description="Asset that fee is charged in")
    created_at: int = Field(description="Fill time")
    remaining_size: float = Field(description="Remaining size of the order")
    client_id: str = Field(description="Unique client assigned ID for the order")
    fill_type: str = Field(description="Fill type, can be FILL, LIQUIDATION or TRANSFER")
    realized_pnl: float = Field(description="Realized PnL of the fill")
    realized_funding: float = Field(description="Realized funding of the fill")
    account: str = Field(default="", description="Account that made the fill")
    underlying_price: str = Field(
        default="", description="Underlying asset price of the fill (spot price)"
    )


class Transaction(BaseModel):
    """Transaction model representing an account transaction on Paradex."""

    id: str
    type: str
    hash: str
    state: str
    created_at: int
    completed_at: int


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

    id: str
    account: str
    market: str
    side: str
    type: str
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
    instruction: str
    avg_fill_price: str
    stp: str
    received_at: int
    published_at: int
    flags: list[str]
    trigger_price: str


class VaultStrategy(BaseModel):
    """Vault strategy model representing a strategy for a vault on Paradex."""

    address: str
    name: str


# Vault models
class Vault(BaseModel):
    """Vault model representing a trading vault on Paradex."""

    address: str
    name: str
    description: str
    owner_account: str
    operator_account: str
    strategies: list[str]
    token_address: str
    status: str
    kind: str
    profit_share: int
    lockup_period: int
    max_tvl: int
    created_at: int
    last_updated_at: int


class VaultBalance(BaseModel):
    """Model representing the balance of a vault."""

    token: str
    size: str
    last_updated_at: int


class VaultSummary(BaseModel):
    """Model representing a summary of a vault's performance and statistics."""

    address: str
    owner_equity: str
    vtoken_supply: str
    vtoken_price: str
    tvl: str
    net_deposits: str
    total_roi: str
    roi_24h: str
    roi_7d: str
    roi_30d: str
    last_month_return: str
    total_pnl: str
    pnl_24h: str
    pnl_7d: str
    pnl_30d: str
    max_drawdown: str
    max_drawdown_24h: str
    max_drawdown_7d: str
    max_drawdown_30d: str
    volume: str
    volume_24h: str
    volume_7d: str
    volume_30d: str
    num_depositors: int


class VaultAccountSummary(BaseModel):
    """Model representing an account summary for a vault."""

    address: str
    deposited_amount: str
    vtoken_amount: str
    total_roi: str
    total_pnl: str
    created_at: int


class Greeks(BaseModel):
    """Model representing the Greeks of a market."""

    delta: float
    gamma: float
    vega: float


class MarketSummary(BaseModel):
    """Model representing a summary of a market."""

    symbol: str
    mark_price: str
    delta: str = Field(default="")
    greeks: Greeks
    last_traded_price: str
    bid: str
    ask: str
    volume_24h: str
    total_volume: str
    created_at: int
    underlying_price: str
    open_interest: str
    funding_rate: str
    price_change_rate_24h: str


class MarketDetails(BaseModel):
    """Model representing the details of a market."""

    symbol: str
    base_currency: str
    quote_currency: str
    settlement_currency: str
    order_size_increment: str
    price_tick_size: float
    min_notional: float
    open_at: int
    expiry_at: int
    asset_kind: str
    market_kind: str
    position_limit: float
    price_bands_width: float
    max_open_orders: int
    max_funding_rate: float
    delta1_cross_margin_params: dict[str, float] = Field(default_factory=dict)
    option_cross_margin_params: dict[str, dict[str, float]] = Field(default_factory=dict)
    price_feed_id: str
    oracle_ewma_factor: float
    max_order_size: float
    max_funding_rate_change: float
    max_tob_spread: float
    interest_rate: float
    clamp_rate: float
    funding_period_hours: int
    tags: list[str]
    option_type: str = Field(default="")
    strike_price: float = Field(default=0.0)
    iv_bands_width: float = Field(default=0.0)


class AccountSummary(BaseModel):
    """Model representing an account summary response from Paradex."""

    account: str = Field(description="User's starknet account")
    account_value: str = Field(description="Current account value [with unrealized P&Ls]")
    free_collateral: str = Field(
        description="Free collateral available (Account value in excess of Initial Margin required)"
    )
    initial_margin_requirement: str = Field(
        description="Amount required to open trade for the existing positions"
    )
    maintenance_margin_requirement: str = Field(
        description="Amount required to maintain exisiting positions"
    )
    margin_cushion: str = Field(description="Acc value in excess of maintenance margin required")
    seq_no: int = Field(
        description="Unique increasing number (non-sequential) that is assigned to this account update. Can be used to deduplicate multiple feeds"
    )
    settlement_asset: str = Field(description="Settlement asset for the account")
    status: str = Field(description="Status of the acc - like ACTIVE, LIQUIDATION")
    total_collateral: str = Field(description="User's total collateral")
    updated_at: int = Field(description="Account last updated time")
