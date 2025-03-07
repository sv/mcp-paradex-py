"""
System management tools.
"""
from typing import Dict, Any
from datetime import datetime

from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import get_paradex_client, api_call
from mcp_paradex.utils.config import config
from paradex_py.api.models import SystemConfigSchema


@server.tool("paradex-system-config")
async def get_system_config() -> Dict[str, Any]:
    """
    Get global Paradex system configuration.
    
    Returns:
        Dict[str, Any]: Global Paradex system configuration.
    """
    client = await get_paradex_client()
    response = api_call(client, "system/config")
    system_config = SystemConfigSchema().load(response, unknown="exclude", partial=True)
    base = {
        "exchange": "Paradex",
        "timestamp": datetime.now().isoformat(),
        "environment": config.ENVIRONMENT.value,
        "status": "operational",
        "features": [
            "perpetual_futures",
            "perpetual_options",
            "vaults",
        ],
        "trading_hours": "24/7",
        "website": "https://paradex.trade/",
        "documentation": "https://github.com/tradeparadex/paradex-docs"
    } 
    base.update(system_config.model_dump())
    return base

@server.tool("paradex-system-time")
async def get_system_time() -> Dict[str, Any]:
    """
    Get the current system time.

    Returns:
        Dict[str, Any]: Current server time in milliseconds since epoch.
    """
    client = await get_paradex_client()
    time = client.fetch_system_time()
    return time

@server.tool("paradex-system-state")
async def get_system_state() -> Dict[str, Any]:
    """
    Get the current system state.
        
    Returns:
        Dict[str, Any]: Current system state.
    """
    client = await get_paradex_client()
    state = client.fetch_system_state()
    return state
