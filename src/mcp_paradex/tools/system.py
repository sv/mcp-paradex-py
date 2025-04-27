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
    Get global Paradex system configuration.

    Retrieves the current system-wide configuration parameters from Paradex,
    including trading limits, fee schedules, and other global settings.
    This information is useful for understanding the current operating
    parameters of the exchange.

    Returns:
        SystemConfig: Global Paradex system configuration
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
    Get the current Paradex system operational state.

    Retrieves the current operational state of the Paradex exchange,
    including information about system health, maintenance status,
    and any active alerts or notices. This is useful for checking
    if the exchange is fully operational before executing trades.
    """
    try:
        client = await get_paradex_client()
        state = client.fetch_system_state()
        time = client.fetch_system_time()
        return SystemState(status=state["status"], timestamp=time["server_time"])
    except Exception as e:
        await ctx.error(f"Error fetching system state: {e!s}")
        raise e
