"""
Market data resources that don't require authentication.
"""
from typing import Dict, Any, List
import logging
from datetime import datetime

from mcp_paradex.server.server import server
from mcp_paradex.utils.config import config
from mcp_paradex.utils.paradex_client import get_paradex_client, api_call

logger = logging.getLogger(__name__)

@server.resource("paradex://vaults")
async def get_vaults() -> Dict[str, Any]:
    """
    Get a list of available vaults from Paradex.
    
    This endpoint doesn't require authentication and provides basic
    information about available vaults.
    
    Returns:
        Dict[str, Any]: List of available vaults.
    """
    try:        
        client = await get_paradex_client()
        vaults = await api_call(client, "vaults")
        
        # Format the response
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "vaults": vaults,
            "count": len(vaults)
        }
    except Exception as e:
        logger.error(f"Error fetching vaults: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "vaults": [],
            "count": 0
        }


@server.resource("paradex://vaults/config")
async def get_vaults_config() -> Dict[str, Any]:
    """
    Get a list of available vaults from Paradex.
    
    This endpoint doesn't require authentication and provides basic
    information about available vaults.
    
    Returns:
        Dict[str, Any]: List of available vaults.
    """
    try:        
        client = await get_paradex_client()
        config = await api_call(client, "vaults/config")
        
        # Format the response
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "config": config,
        }
    except Exception as e:
        logger.error(f"Error fetching vaults: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "vaults": [],
            "count": 0
        }

@server.resource("paradex://vaults/balance/{vault_id}")
async def get_vault_balance(vault_id: str) -> Dict[str, Any]:
    """
    Get a summary of market information for a specific trading pair.
    
    This endpoint requires authentication and provides detailed
    information about the market, including order book, ticker, and
    market statistics.
    
    Args:
        market_id (str): The ID of the trading pair to get summary for.
        
    Returns:
        Dict[str, Any]: Summary of market information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        summary = await api_call(client, "vaults/balance", params={"address": vault_id})
        return summary
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "summary": None
        }


@server.resource("paradex://vaults/summary/{vault_id}")
async def get_vault_summary(vault_id: str) -> Dict[str, Any]:
    """
    Get a summary of market information for a specific trading pair.
    
    This endpoint requires authentication and provides detailed
    information about the market, including order book, ticker, and
    market statistics.
    
    Args:
        market_id (str): The ID of the trading pair to get summary for.
        
    Returns:
        Dict[str, Any]: Summary of market information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        summary = await api_call(client, "vaults/summary", params={"address": vault_id})
        return summary
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "summary": None
        }
    

@server.resource("paradex://vaults/transfers/{vault_id}")
async def get_vault_transfers(vault_id: str) -> Dict[str, Any]:
    """
    Get a summary of market information for a specific trading pair.
    
    This endpoint requires authentication and provides detailed
    information about the market, including order book, ticker, and
    market statistics.
    
    Args:
        market_id (str): The ID of the trading pair to get summary for.
        
    Returns:
        Dict[str, Any]: Summary of market information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        summary = await api_call(client, "vaults/transfers", params={"address": vault_id})
        return summary
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "summary": None
        }
    

@server.resource("paradex://vaults/positions/{vault_id}")
async def get_vault_positions(vault_id: str) -> Dict[str, Any]:
    """
    Get a summary of market information for a specific trading pair.
    
    This endpoint requires authentication and provides detailed
    information about the market, including order book, ticker, and
    market statistics.
    
    Args:
        market_id (str): The ID of the trading pair to get summary for.
        
    Returns:
        Dict[str, Any]: Summary of market information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        summary = await api_call(client, "vaults/positions", params={"address": vault_id})
        return summary
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "summary": None
        }
    

@server.resource("paradex://vaults/account-summary/{vault_id}")
async def get_vault_account_summary(vault_id: str) -> Dict[str, Any]:
    """
    Get a summary of market information for a specific trading pair.
    
    This endpoint requires authentication and provides detailed
    information about the market, including order book, ticker, and
    market statistics.
    
    Args:
        market_id (str): The ID of the trading pair to get summary for.
        
    Returns:
        Dict[str, Any]: Summary of market information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        summary = await api_call(client, "vaults/account-summary", params={"address": vault_id})
        return summary
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "summary": None
        }
    