"""
System management tools for Paradex.

This module provides tools for retrieving system-level information from Paradex,
including configuration, time synchronization, and system state.
These tools help with monitoring the exchange status and retrieving
global parameters that affect trading operations.
"""

import logging

from mcp.server.fastmcp.server import Context
from paradex_py.api.models import SystemConfig, SystemConfigSchema

from mcp_paradex.models import SystemState
from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import api_call, get_paradex_client

logger = logging.getLogger(__name__)


@server.tool(name="paradex_system_config")
async def get_system_config(ctx: Context) -> SystemConfig:
    """
    Understand the exchange's global parameters that affect all trading activity.

    Use this tool when you need to:
    - Check fee schedules before placing trades
    - Verify trading limits and restrictions
    - Understand exchange-wide parameters that affect your trading
    - Keep up with changes to the exchange's configuration

    This information provides important context for making trading decisions and
    understanding how the exchange operates.

    Example use cases:
    - Checking current fee tiers for different markets
    - Verifying maximum leverage available for specific markets
    - Understanding global trading limits or restrictions
    - Checking if any exchange-wide changes might affect your trading strategy
    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "system/config")
        system_config = SystemConfigSchema().load(response, unknown="exclude", partial=True)
        return system_config
    except Exception as e:
        await ctx.error(f"Error fetching system configuration: {e!s}")
        raise e


@server.tool(name="paradex_system_state")
async def get_system_state(ctx: Context) -> SystemState:
    """
    Verify the exchange is fully operational before executing trades.

    Use this tool when you need to:
    - Check if Paradex is functioning normally before placing important orders
    - Verify system status if you encounter unexpected behavior
    - Confirm that maintenance periods are not in effect
    - Check exchange clock synchronization with your own systems

    This is especially important before executing critical trades or when
    experiencing unexpected behavior from other API calls.

    Example use cases:
    - Verifying the exchange is operational before executing a trading strategy
    - Checking if maintenance mode is active when experiencing delays
    - Confirming exchange status during periods of market volatility
    - Diagnosing API issues by checking system health
    """
    try:
        client = await get_paradex_client()
        state = client.fetch_system_state()
        time = client.fetch_system_time()
        return SystemState(status=state["status"], timestamp=time["server_time"])
    except Exception as e:
        await ctx.error(f"Error fetching system state: {e!s}")
        raise e
