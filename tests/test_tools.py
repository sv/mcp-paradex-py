"""
Layer 2 integration tests: exercise tools via FastMCP.call_tool() with the
Paradex HTTP client mocked out.

Strategy
--------
All tools call get_paradex_client() or get_authenticated_paradex_client(),
both of which return the module-level `_paradex_client` singleton.  Setting
that variable to a MagicMock bypasses real network calls while still
exercising the full tool logic (arg parsing, Pydantic validation, response
shaping).

call_tool() returns [TextContent(type="text", text="<json>")], so helpers
_text() / _json() extract the payload.
"""

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from mcp.server.fastmcp.exceptions import ToolError

import mcp_paradex.utils.paradex_client as _client_module
from mcp_paradex.server.server import server


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _text(result: Any) -> str:
    """Pull the JSON text from a call_tool result.

    FastMCP call_tool() returns one of:
    - [TextContent(...)]              for tools annotated with plain `dict` / `list`
    - ([TextContent(...)], dict)      for tools annotated with `dict[str, Any]` or
                                      a Pydantic/dataclass model (structured output)
    """
    if isinstance(result, tuple):
        return result[0][0].text
    return result[0].text


def _json(result: Any) -> Any:
    return json.loads(_text(result))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_client():
    """Unauthenticated Paradex client mock (public tools)."""
    client = MagicMock()
    client.account = None
    client.api_url = "https://api.testnet.paradex.trade/v1"
    with patch.object(_client_module, "_paradex_client", client):
        yield client


@pytest.fixture()
def auth_client(mock_client):
    """Authenticated Paradex client mock (account / order tools)."""
    mock_client.account = MagicMock()
    return mock_client


# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

MARKET_RECORD = {
    "symbol": "BTC-USD-PERP",
    "base_currency": "BTC",
    "quote_currency": "USD",
    "settlement_currency": "USDC",
    "order_size_increment": "0.0001",
    "price_tick_size": 0.1,
    "min_notional": 1.0,
    "open_at": 0,
    "expiry_at": 0,
    "asset_kind": "PERP",
    "market_kind": "cross",
    "position_limit": 100.0,
    "price_bands_width": 0.05,
    "max_open_orders": 50,
    "max_funding_rate": 0.0003,
    "delta1_cross_margin_params": {},
    "option_cross_margin_params": {},
    "price_feed_id": "",
    "oracle_ewma_factor": 0.0,
    "max_order_size": 1000.0,
    "max_funding_rate_change": 0.0001,
    "max_tob_spread": 0.01,
    "interest_rate": 0.0,
    "clamp_rate": 0.0,
    "funding_period_hours": 8,
    "tags": [],
    "option_type": "",
    "strike_price": 0.0,
    "iv_bands_width": 0.0,
}

SUMMARY_RECORD = {
    "symbol": "BTC-USD-PERP",
    "mark_price": "95000.0",
    "delta": "1.0",
    "greeks": {"delta": 1.0, "gamma": 0.0, "vega": 0.0, "rho": 0.0, "vanna": 0.0, "volga": 0.0},
    "last_traded_price": "95000.0",
    "bid": "94999.0",
    "ask": "95001.0",
    "volume_24h": "100000000",
    "total_volume": "1000000000",
    "created_at": 1_700_000_000_000,
    "underlying_price": "95000.0",
    "open_interest": "500",
    "funding_rate": "0.0001",
    "price_change_rate_24h": "0.02",
}

ORDER_RECORD = {
    "id": "ord-1",
    "account": "0xabc123",
    "market": "BTC-USD-PERP",
    "side": "BUY",
    "type": "LIMIT",
    "size": 0.1,
    "remaining_size": 0.1,
    "price": 94000.0,
    "status": "OPEN",
    "created_at": 1_700_000_000_000,
    "last_updated_at": 1_700_000_000_000,
    "timestamp": 1_700_000_000_000,
    "cancel_reason": "",
    "client_id": "my-order-1",
    "seq_no": 1,
    "instruction": "GTC",
    "avg_fill_price": "0",
    "stp": "",
    "received_at": 1_700_000_000_000,
    "published_at": 1_700_000_000_000,
    "flags": [],
    "trigger_price": "",
}

ACCOUNT_RESPONSE = {
    "account": "0xabc123",
    "account_value": "10000.0",
    "free_collateral": "8000.0",
    "initial_margin_requirement": "1000.0",
    "maintenance_margin_requirement": "500.0",
    "margin_cushion": "9500.0",
    "seq_no": 1,
    "settlement_asset": "USDC",
    "status": "ACTIVE",
    "total_collateral": "10000.0",
    "updated_at": 1_700_000_000_000,
}

POSITION_RECORD = {
    "id": "pos-1",
    "account": "0xabc123",
    "market": "BTC-USD-PERP",
    "status": "OPEN",
    "side": "LONG",
    "size": 0.1,
    "average_entry_price": 95000.0,
    "average_entry_price_usd": 95000.0,
    "average_exit_price": 0.0,
    "unrealized_pnl": 500.0,
    "unrealized_funding_pnl": -10.0,
    "cost": 9500.0,
    "cost_usd": 9500.0,
    "cached_funding_index": 0.0,
    "last_updated_at": 1_700_000_000_000,
    "last_fill_id": "fill-1",
    "seq_no": 1,
}


# ---------------------------------------------------------------------------
# System tools
# ---------------------------------------------------------------------------


async def test_system_state_returns_status_and_timestamp(mock_client):
    mock_client.fetch_system_state.return_value = {"status": "ok"}
    mock_client.fetch_system_time.return_value = {"server_time": 1_700_000_000_000}

    result = await server.call_tool("paradex_system_state", {})
    data = _json(result)

    assert data["status"] == "ok"
    assert data["timestamp"] == 1_700_000_000_000
    mock_client.fetch_system_state.assert_called_once()
    mock_client.fetch_system_time.assert_called_once()


SYSTEM_CONFIG_RESPONSE = {
    "starknet_gateway_url": "https://alpha-mainnet.starknet.io",
    "starknet_fullnode_rpc_url": "https://rpc.mainnet.starknet.io",
    "starknet_fullnode_rpc_base_url": "https://rpc.mainnet.starknet.io",
    "starknet_chain_id": "0x534e5f4d41494e",
    "block_explorer_url": "https://starkscan.co",
    "paraclear_address": "0xabc",
    "paraclear_decimals": 8,
    "paraclear_account_proxy_hash": "0xdef",
    "paraclear_account_hash": "0x123",
    "oracle_address": "0x456",
    "bridged_tokens": [],
    "l1_core_contract_address": "0x789",
    "l1_operator_address": "0xabc",
    "l1_chain_id": "1",
    "liquidation_fee": "0.005",
}


async def test_system_config_calls_correct_api_path(mock_client):
    mock_client.get.return_value = SYSTEM_CONFIG_RESPONSE

    await server.call_tool("paradex_system_config", {})

    mock_client.get.assert_called_once_with(mock_client.api_url, "system/config", None)


# ---------------------------------------------------------------------------
# Market tools
# ---------------------------------------------------------------------------


async def test_markets_returns_results(mock_client):
    mock_client.fetch_markets.return_value = {"results": [MARKET_RECORD]}

    result = await server.call_tool("paradex_markets", {"market_ids": ["ALL"]})
    data = _json(result)

    assert data["total"] == 1
    assert data["results"][0]["symbol"] == "BTC-USD-PERP"
    mock_client.fetch_markets.assert_called_once()


async def test_markets_filters_by_symbol(mock_client):
    eth_record = {**MARKET_RECORD, "symbol": "ETH-USD-PERP", "base_currency": "ETH"}
    mock_client.fetch_markets.return_value = {"results": [MARKET_RECORD, eth_record]}

    result = await server.call_tool("paradex_markets", {"market_ids": ["ETH-USD-PERP"]})
    data = _json(result)

    assert data["total"] == 1
    assert data["results"][0]["symbol"] == "ETH-USD-PERP"


async def test_markets_pagination(mock_client):
    records = [{**MARKET_RECORD, "symbol": f"MKT{i}-USD-PERP"} for i in range(5)]
    mock_client.fetch_markets.return_value = {"results": records}

    result = await server.call_tool("paradex_markets", {"market_ids": ["ALL"], "limit": 2, "offset": 0})
    data = _json(result)

    assert data["total"] == 5
    assert len(data["results"]) == 2


async def test_market_summaries_fetches_all(mock_client):
    mock_client.fetch_markets_summary.return_value = {"results": [SUMMARY_RECORD]}

    result = await server.call_tool("paradex_market_summaries", {"market_ids": ["ALL"]})
    data = _json(result)

    assert data["total"] == 1
    assert data["results"][0]["symbol"] == "BTC-USD-PERP"
    mock_client.fetch_markets_summary.assert_called_once_with(params={"market": "ALL"})


async def test_bbo_returns_bid_ask(mock_client):
    mock_client.fetch_bbo.return_value = {
        "market": "BTC-USD-PERP",
        "seq_no": 42,
        "ask": 95001.0,
        "ask_size": 0.5,
        "bid": 94999.0,
        "bid_size": 1.0,
        "last_updated_at": 1_700_000_000_000,
    }

    result = await server.call_tool("paradex_bbo", {"market_id": "BTC-USD-PERP"})
    data = _json(result)

    assert data["results"]["market"] == "BTC-USD-PERP"
    assert data["results"]["ask"] == 95001.0
    mock_client.fetch_bbo.assert_called_once_with("BTC-USD-PERP")


async def test_orderbook_passes_depth_param(mock_client):
    mock_client.fetch_orderbook.return_value = {
        "market": "BTC-USD-PERP",
        "asks": [["95001.0", "0.1"]],
        "bids": [["94999.0", "0.2"]],
    }

    result = await server.call_tool(
        "paradex_orderbook", {"market_id": "BTC-USD-PERP", "depth": 20}
    )
    data = _json(result)

    assert data["market"] == "BTC-USD-PERP"
    mock_client.fetch_orderbook.assert_called_once_with("BTC-USD-PERP", params={"depth": 20})


async def test_trades_passes_time_params(mock_client):
    mock_client.fetch_trades.return_value = {
        "results": [
            {
                "id": "trade-1",
                "market": "BTC-USD-PERP",
                "side": "BUY",
                "size": 0.1,
                "price": 95000.0,
                "created_at": 1_700_000_000_000,
                "trade_type": "FILL",
            }
        ]
    }

    result = await server.call_tool(
        "paradex_trades",
        {"market_id": "BTC-USD-PERP", "start_unix_ms": 1_000, "end_unix_ms": 2_000},
    )
    data = _json(result)

    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == "trade-1"
    mock_client.fetch_trades.assert_called_once_with(
        params={"market": "BTC-USD-PERP", "start_at": 1_000, "end_at": 2_000}
    )


async def test_klines_passes_params_and_shapes_ohlcv(mock_client):
    mock_client.get.return_value = {
        "results": [[1_700_000_000_000, 95000.0, 95500.0, 94500.0, 95200.0, 100.0]]
    }

    result = await server.call_tool(
        "paradex_klines",
        {
            "market_id": "BTC-USD-PERP",
            "resolution": 1,
            "start_unix_ms": 1_000,
            "end_unix_ms": 2_000,
        },
    )
    # list[OHLCV] → structured output: (content_list, {'result': [...]})
    candles = result[1]["result"]

    assert len(candles) == 1
    assert candles[0]["open"] == 95000.0
    assert candles[0]["high"] == 95500.0
    assert candles[0]["close"] == 95200.0
    mock_client.get.assert_called_once_with(
        mock_client.api_url,
        "markets/klines",
        {"symbol": "BTC-USD-PERP", "resolution": "1", "start_at": 1_000, "end_at": 2_000},
    )


async def test_funding_data_passes_params(mock_client):
    mock_client.fetch_funding_data.return_value = {
        "results": [
            {
                "market": "BTC-USD-PERP",
                "created_at": 1_700_000_000_000,
                "funding_index": "0.001",
                "funding_premium": "0.0002",
                "funding_rate": "0.0001",
            }
        ]
    }

    result = await server.call_tool(
        "paradex_funding_data",
        {"market_id": "BTC-USD-PERP", "start_unix_ms": 1_000, "end_unix_ms": 2_000},
    )
    data = _json(result)

    assert data["results"][0]["market"] == "BTC-USD-PERP"
    mock_client.fetch_funding_data.assert_called_once_with(
        params={"market": "BTC-USD-PERP", "start_at": 1_000, "end_at": 2_000}
    )


async def test_filters_model_returns_schema(mock_client):
    result = await server.call_tool("paradex_filters_model", {"tool_name": "paradex_markets"})
    data = _json(result)

    # Should be a JSON Schema with at least a 'properties' key
    assert "properties" in data
    assert "symbol" in data["properties"]


# ---------------------------------------------------------------------------
# Account tools — require authentication
# ---------------------------------------------------------------------------


async def test_account_summary_raises_when_unauthenticated(mock_client):
    mock_client.account = None

    with pytest.raises(ToolError, match="not authenticated"):
        await server.call_tool("paradex_account_summary", {})


async def test_account_summary_returns_data(auth_client):
    auth_client.get.return_value = ACCOUNT_RESPONSE

    result = await server.call_tool("paradex_account_summary", {})
    data = _json(result)

    assert data["results"]["account"] == "0xabc123"
    assert data["results"]["status"] == "ACTIVE"
    auth_client.get.assert_called_once_with(auth_client.api_url, "account", None)


async def test_account_positions_returns_list(auth_client):
    auth_client.fetch_positions.return_value = {"results": [POSITION_RECORD]}

    result = await server.call_tool("paradex_account_positions", {})
    data = _json(result)

    assert len(data["results"]) == 1
    assert data["results"][0]["market"] == "BTC-USD-PERP"
    assert data["results"][0]["side"] == "LONG"
    auth_client.fetch_positions.assert_called_once()


# ---------------------------------------------------------------------------
# Order tools — require authentication
# ---------------------------------------------------------------------------


async def test_open_orders_no_market_filter(auth_client):
    auth_client.fetch_orders.return_value = {"results": [ORDER_RECORD]}

    result = await server.call_tool("paradex_open_orders", {"market_id": "ALL", "limit": 10})
    data = _json(result)

    assert data["total"] == 1
    assert data["results"][0]["id"] == "ord-1"
    # market_id=ALL → params=None
    auth_client.fetch_orders.assert_called_once_with(params=None)


async def test_open_orders_passes_market_filter(auth_client):
    auth_client.fetch_orders.return_value = {"results": []}

    await server.call_tool("paradex_open_orders", {"market_id": "ETH-USD-PERP"})

    auth_client.fetch_orders.assert_called_once_with(params={"market": "ETH-USD-PERP"})


async def test_cancel_order_by_order_id(auth_client):
    auth_client.cancel_order.return_value = {**ORDER_RECORD, "status": "CANCELLED"}

    result = await server.call_tool(
        "paradex_cancel_orders", {"order_id": "ord-1", "client_id": "", "market_id": ""}
    )
    data = _json(result)

    assert data["status"] == "CANCELLED"
    auth_client.cancel_order.assert_called_once_with("ord-1")
    auth_client.cancel_order_by_client_id.assert_not_called()


async def test_cancel_order_by_client_id(auth_client):
    auth_client.cancel_order_by_client_id.return_value = {**ORDER_RECORD, "status": "CANCELLED"}

    result = await server.call_tool(
        "paradex_cancel_orders", {"order_id": "", "client_id": "my-order-1", "market_id": ""}
    )
    data = _json(result)

    assert data["status"] == "CANCELLED"
    auth_client.cancel_order_by_client_id.assert_called_once_with("my-order-1")
    auth_client.cancel_order.assert_not_called()


async def test_order_status_by_order_id(auth_client):
    auth_client.fetch_order.return_value = ORDER_RECORD

    result = await server.call_tool(
        "paradex_order_status", {"order_id": "ord-1", "client_id": ""}
    )
    data = _json(result)

    assert data["results"]["id"] == "ord-1"
    assert data["results"]["market"] == "BTC-USD-PERP"
    auth_client.fetch_order.assert_called_once_with("ord-1")


async def test_order_status_by_client_id(auth_client):
    auth_client.fetch_order_by_client_id.return_value = ORDER_RECORD

    result = await server.call_tool(
        "paradex_order_status", {"order_id": "", "client_id": "my-order-1"}
    )
    data = _json(result)

    assert data["results"]["client_id"] == "my-order-1"
    auth_client.fetch_order_by_client_id.assert_called_once_with("my-order-1")
