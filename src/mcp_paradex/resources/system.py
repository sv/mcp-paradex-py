"""
System status and health check resources.
"""
import os
import sys
from datetime import datetime
from typing import Any

import pkg_resources

from mcp_paradex.server.server import server
from mcp_paradex.utils.config import config
from mcp_paradex.utils.paradex_client import get_paradex_client


@server.resource("system://status")
async def system_status() -> dict[str, Any]:
    """
    Get the current system status.
    
    Returns:
        Dict[str, Any]: System status information.
    """
    return {
        "status": "operational",
        "server": {
            "name": config.SERVER_NAME,
            "version": pkg_resources.get_distribution("mcp-paradex").version,
            "timestamp": datetime.now().isoformat(),
        },
        "paradex": {
            "environment": config.ENVIRONMENT,
            "auth_configured": config.is_configured(),
        }
    }

@server.resource("system://version")
async def version_info() -> dict[str, Any]:
    """
    Get detailed version information about the server and its dependencies.
    
    Returns:
        Dict[str, Any]: Version information.
    """
    # Get MCP SDK version
    try:
        mcp_version = pkg_resources.get_distribution("mcp").version
    except pkg_resources.DistributionNotFound:
        mcp_version = "unknown"

    # Get Paradex SDK version
    try:
        paradex_version = pkg_resources.get_distribution("paradex-py").version
    except pkg_resources.DistributionNotFound:
        paradex_version = "unknown"

    return {
        "dependencies": {
            "mcp_sdk": mcp_version,
            "paradex_sdk": paradex_version,
        },
        "environment": {
            "python_path": sys.executable,
            "working_directory": os.getcwd(),
        }
    }

@server.resource("system://health")
async def health_check() -> dict[str, Any]:
    """
    Perform a basic health check of the server.
    
    This endpoint doesn't require authentication and can be used to verify
    that the server is running correctly.
    
    Returns:
        Dict[str, Any]: Health check results.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "server": "pass",
            "configuration": "pass" if config.SERVER_NAME else "fail",
        }
    }


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
        "documentation": "https://github.com/tradeparadex/paradex-docs"
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
