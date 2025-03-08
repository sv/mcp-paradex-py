"""
System management tools for Paradex.

This module provides tools for retrieving system-level information from Paradex,
including configuration, time synchronization, and system state.
These tools help with monitoring the exchange status and retrieving
global parameters that affect trading operations.
"""
from typing import Dict, Any
import logging
from datetime import datetime
from pydantic import Field


from mcp_paradex.server.server import server
from mcp_paradex.utils.paradex_client import get_paradex_client, api_call
from mcp_paradex.utils.config import config
from paradex_py.api.models import SystemConfigSchema
from mcp.server.fastmcp.server import Context

logger = logging.getLogger(__name__)


@server.tool("paradex-system-config")
async def get_system_config(ctx: Context) -> Dict[str, Any]:
    """
    Get global Paradex system configuration.
    
    Retrieves the current system-wide configuration parameters from Paradex,
    including trading limits, fee schedules, and other global settings.
    This information is useful for understanding the current operating
    parameters of the exchange.
    
    Returns:
        Dict[str, Any]: Global Paradex system configuration with the following structure:
            - exchange (str): Exchange name ("Paradex")
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current environment (mainnet/testnet)
            - status (str): Current system status ("operational", "maintenance", etc.)
            - features (List[str]): Available trading features
            - trading_hours (str): Trading availability
            - website (str): Exchange website URL
            - documentation (str): Documentation URL
            - [Additional system parameters from Paradex API]
            
            If an error occurs, returns error information.
    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "system/config")
        system_config = SystemConfigSchema().load(response, unknown="exclude", partial=True)
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
        base.update(system_config.model_dump())
        return base
    except Exception as e:
        logger.error(f"Error fetching system configuration: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "config": None
        }

@server.tool("paradex-system-time")
async def get_system_time(ctx: Context) -> Dict[str, Any]:
    """
    Get the current Paradex server time.
    
    Retrieves the current server time from Paradex. This is important for
    time-sensitive operations like trading, as local time might differ
    from the exchange's server time. Using the exchange time ensures
    accurate timestamp coordination for orders and other time-dependent
    operations.
    
    Returns:
        Dict[str, Any]: Current server time information with the following structure:
            - server_time (int): Current server time in milliseconds since epoch
            - iso_time (str): ISO-formatted timestamp
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
    """
    try:
        client = await get_paradex_client()
        time = client.fetch_system_time()
        return time
    except Exception as e:
        logger.error(f"Error fetching system time: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "server_time": None
        }

@server.tool("paradex-system-state")
async def get_system_state(ctx: Context) -> Dict[str, Any]:
    """
    Get the current Paradex system operational state.
    
    Retrieves the current operational state of the Paradex exchange,
    including information about system health, maintenance status,
    and any active alerts or notices. This is useful for checking
    if the exchange is fully operational before executing trades.
    
    Returns:
        Dict[str, Any]: Current system state information with the following structure:
            - status (str): Overall system status ("operational", "degraded", "maintenance", etc.)
            - components (Dict): Status of individual system components
            - maintenance (Dict, optional): Information about ongoing or scheduled maintenance
            - notices (List, optional): System-wide notices or alerts
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
    """
    try:
        client = await get_paradex_client()
        state = client.fetch_system_state()
        return state
    except Exception as e:
        logger.error(f"Error fetching system state: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "state": None
        }
