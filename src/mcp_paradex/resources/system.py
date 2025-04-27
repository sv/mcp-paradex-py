"""
System status and health check resources.
"""

from datetime import datetime
from typing import Any

from mcp_paradex.server.server import server
from mcp_paradex.utils.config import config
from mcp_paradex.utils.paradex_client import get_paradex_client


@server.resource("paradex://system/config")
async def get_system_config() -> dict[str, Any]:
    """
    Get general market information and status.

    This endpoint doesn't require authentication and provides basic
    information about the Paradex exchange.

    Returns:
        Dict[str, Any]: Market information.
    """
    client = await get_paradex_client()
    syscfg = client.fetch_system_config()
    base = {
        "exchange": "Paradex",
        "timestamp": datetime.now().isoformat(),
        "environment": config.ENVIRONMENT,
        "status": "operational",
        "features": [
            "perpetual_futures",
            "perpetual_options",
            "vaults",
        ],
        "trading_hours": "24/7",
        "website": "https://paradex.trade/",
        "documentation": "https://github.com/tradeparadex/paradex-docs",
    }
    base.update(syscfg.model_dump())
    return base


@server.resource("paradex://system/time")
async def get_system_time() -> dict[str, Any]:
    """
    Get the current system time.

    This endpoint doesn't require authentication and provides the current
    server time in milliseconds since epoch.

    Returns:
        Dict[str, Any]: System time information.
    """
    client = await get_paradex_client()
    time = client.fetch_system_time()
    return time


@server.resource("paradex://system/state")
async def get_system_state() -> dict[str, Any]:
    """
    Get the current system state.

    This endpoint doesn't require authentication and provides the current
    system state.

    Returns:
        Dict[str, Any]: System state information.
    """
    client = await get_paradex_client()
    state = client.fetch_system_state()
    return state
