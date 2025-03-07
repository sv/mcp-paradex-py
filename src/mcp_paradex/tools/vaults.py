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

@server.tool("paradex-vault-list")
async def get_vault_list() -> Dict[str, Any]:
    """
    Get a list of available vaults from Paradex.
    
    Returns:
        Dict[str, Any]: List of available vaults.
    """
    try:        
        client = await get_paradex_client()
        response = await api_call(client, "vaults")
        
        vault_list = [{"address": vault["address"], "name": vault["name"]} for vault in response["results"]]
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "vaults": vault_list,
            "count": len(vault_list)
        }
    except Exception as e:
        logger.error(f"Error fetching vaults: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "vaults": [],
            "count": 0
        }

@server.tool("paradex-vault-details")
async def get_vault_details(vault_address: str) -> Dict[str, Any]:
    """
    Get details of a vault.
    
    Returns:
        Dict[str, Any]: List of available vaults.
    """
    try:        
        client = await get_paradex_client()
        response = await api_call(client, "vaults", params={"address": vault_address})
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "vaults": response["results"],
            "count": len(response["results"])
        }
    except Exception as e:
        logger.error(f"Error fetching vaults: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "vaults": [],
            "count": 0
        }


@server.tool("paradex-vaults-config")
async def get_vaults_config() -> Dict[str, Any]:
    """
    Get global configuration for vaults from Paradex.
    """
    try:        
        client = await get_paradex_client()
        response = await api_call(client, "vaults/config")
        
        # Format the response
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "config": response,
        }
    except Exception as e:
        logger.error(f"Error fetching vaults: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "vaults": [],
            "count": 0
        }

@server.tool("paradex-vault-balance")
async def get_vault_balance(vault_address: str) -> Dict[str, Any]:
    """
    Get the balance of a specific vault from Paradex.

    Args:
        vault_address (str): The address of the vault to get balance for.
        
    Returns:
        Dict[str, Any]: Balance of the vault.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = await api_call(client, "vaults/balance", params={"address": vault_address})
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "balance": None
        }


@server.tool("paradex-vault-summary")
async def get_vault_summary(vault_address: str) -> Dict[str, Any]:
    """
    Get a summary of vault information for a specific vault.
    
    Args:
        vault_address (str): The address of the vault to get summary for.
        
    Returns:
        Dict[str, Any]: Summary of vault information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = await api_call(client, "vaults/summary", params={"address": vault_address})
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching vault summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "summary": None
        }
    

@server.tool("paradex-vault-transfers")
async def get_vault_transfers(vault_address: str) -> Dict[str, Any]:
    """
    Get a list of transfers for a specific vault.

    Args:
        vault_address (str): The address of the vault to get transfers for.
        
    Returns:
        Dict[str, Any]: List of transfers for the vault.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = await api_call(client, "vaults/transfers", params={"address": vault_address})
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "transfers": None
        }
    

@server.tool("paradex-vault-positions")
async def get_vault_positions(vault_address: str) -> Dict[str, Any]:
    """
    Get a list of positions for a specific vault.
    
    Args:
        vault_address (str): The address of the vault to get positions for.
        
    Returns:
        Dict[str, Any]: List of positions for the vault.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = await api_call(client, "vaults/positions", params={"address": vault_address})
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "positions": None
        }
    

@server.tool("paradex-vault-account-summary")
async def get_vault_account_summary(vault_address: str) -> Dict[str, Any]:
    """
    Get a summary of account information for a specific vault.
    
    Args:
        vault_address (str): The address of the vault to get account summary for.
        
    Returns:
        Dict[str, Any]: Summary of account information.
    """
    try:
        # Get market summary from Paradex
        client = await get_paradex_client()
        response = await api_call(client, "vaults/account-summary", params={"address": vault_address})
        return response
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "account_summary": None
        }
    