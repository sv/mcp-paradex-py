"""
Vault management tools for Paradex.

This module provides tools for retrieving information about Paradex vaults,
which are smart contracts that allow users to deposit funds and trade on Paradex
with self-custody. These tools help with monitoring vault status, balances,
positions, and transaction history.
"""
from typing import Dict, Any
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
    
    Retrieves all available vaults on Paradex, including their addresses and names.
    This tool requires no parameters and returns a comprehensive list of
    all vaults that can be accessed on Paradex.
    
    Returns:
        Dict[str, Any]: List of available vaults with the following structure:
            - success (bool): Whether the request was successful
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment (mainnet/testnet)
            - vaults (List[Dict]): List of vault objects with address and name
            - count (int): Total number of vaults
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
            - vaults (List): Empty list
            - count (int): 0
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
    Get detailed information about a specific vault.
    
    Retrieves comprehensive details about a specific vault identified by its address,
    including configuration, permissions, and other vault-specific parameters.
    
    Args:
        vault_address (str): The blockchain address of the vault to get details for.
                            Example: "0x1234...abcd"
        
    Returns:
        Dict[str, Any]: Detailed vault information with the following structure:
            - success (bool): Whether the request was successful
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment (mainnet/testnet)
            - vaults (List[Dict]): List containing the vault details
            - count (int): Number of vaults returned (should be 1)
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
            - vaults (List): Empty list
            - count (int): 0
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
        logger.error(f"Error fetching vault details for {vault_address}: {str(e)}")
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
    
    Retrieves system-wide configuration parameters for vaults on Paradex,
    including fee structures, limits, and other global settings that apply
    to all vaults on the platform.
    
    Returns:
        Dict[str, Any]: Global vault configuration with the following structure:
            - success (bool): Whether the request was successful
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment (mainnet/testnet)
            - config (Dict): Global vault configuration parameters
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
            - config (None): Null value for config
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
        logger.error(f"Error fetching vaults configuration: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "config": None
        }

@server.tool("paradex-vault-balance")
async def get_vault_balance(vault_address: str) -> Dict[str, Any]:
    """
    Get the current balance of a specific vault.

    Retrieves the current balance information for a specific vault,
    including available funds, locked funds, and total balance.
    This is essential for understanding the financial state of a vault
    before executing trades or withdrawals.

    Args:
        vault_address (str): The blockchain address of the vault to get balance for.
                            Example: "0x1234...abcd"
        
    Returns:
        Dict[str, Any]: Balance information for the vault, including:
            - available (float): Available balance that can be used for trading
            - locked (float): Balance locked in open orders or positions
            - total (float): Total balance (available + locked)
            - currency (str): Currency of the balance (e.g., "USDC")
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
            - balance (None): Null value for balance
    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults/balance", params={"address": vault_address})
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching balance for vault {vault_address}: {str(e)}")
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
    Get a comprehensive summary of a specific vault.
    
    Retrieves a summary of all important information about a vault,
    including balance, positions, recent activity, and performance metrics.
    This provides a high-level overview of the vault's current state.
    
    Args:
        vault_address (str): The blockchain address of the vault to get summary for.
                            Example: "0x1234...abcd"
        
    Returns:
        Dict[str, Any]: Summary information for the vault, including:
            - balance (Dict): Current balance information
            - positions (List): Current open positions
            - performance (Dict): Performance metrics
            - recent_activity (List): Recent transactions or trades
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
            - summary (None): Null value for summary
    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults/summary", params={"address": vault_address})
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching summary for vault {vault_address}: {str(e)}")
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
    Get a list of deposit and withdrawal transfers for a specific vault.

    Retrieves the history of all transfers (deposits and withdrawals) for a vault,
    including timestamps, amounts, transaction hashes, and status information.
    This is useful for auditing vault activity and tracking fund movements.

    Args:
        vault_address (str): The blockchain address of the vault to get transfers for.
                            Example: "0x1234...abcd"
        
    Returns:
        Dict[str, Any]: List of transfers for the vault, each containing:
            - id (str): Transfer ID
            - type (str): "DEPOSIT" or "WITHDRAWAL"
            - amount (float): Transfer amount
            - currency (str): Currency of the transfer
            - timestamp (str): When the transfer occurred
            - status (str): Status of the transfer (e.g., "COMPLETED", "PENDING")
            - transaction_hash (str): Blockchain transaction hash
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
            - transfers (None): Null value for transfers
    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults/transfers", params={"address": vault_address})
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching transfers for vault {vault_address}: {str(e)}")
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
    Get a list of current trading positions for a specific vault.
    
    Retrieves all open trading positions for a vault, including market,
    size, entry price, liquidation price, unrealized PnL, and other
    position-specific information.
    
    Args:
        vault_address (str): The blockchain address of the vault to get positions for.
                            Example: "0x1234...abcd"
        
    Returns:
        Dict[str, Any]: List of positions for the vault, each containing:
            - market_id (str): Market identifier (e.g., "ETH-PERP")
            - side (str): Position side ("LONG" or "SHORT")
            - size (float): Position size
            - entry_price (float): Average entry price
            - mark_price (float): Current mark price
            - liquidation_price (float): Price at which position would be liquidated
            - unrealized_pnl (float): Unrealized profit/loss
            - leverage (float): Current leverage
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
            - positions (None): Null value for positions
    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults/positions", params={"address": vault_address})
        return response["results"]
    except Exception as e:
        logger.error(f"Error fetching positions for vault {vault_address}: {str(e)}")
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
    Get a summary of trading account information for a specific vault.
    
    Retrieves a comprehensive summary of the trading account associated with
    a vault, including margin information, account health, risk metrics,
    and trading statistics.
    
    Args:
        vault_address (str): The blockchain address of the vault to get account summary for.
                            Example: "0x1234...abcd"
        
    Returns:
        Dict[str, Any]: Account summary information, including:
            - margin_ratio (float): Current margin ratio
            - account_health (float): Account health percentage
            - total_equity (float): Total account equity
            - available_margin (float): Available margin for new positions
            - used_margin (float): Margin currently in use
            - unrealized_pnl (float): Total unrealized profit/loss
            - realized_pnl_24h (float): Realized profit/loss in the last 24 hours
            - open_orders_count (int): Number of open orders
            - positions_count (int): Number of open positions
            
            If an error occurs, returns:
            - success (bool): False
            - timestamp (str): ISO-formatted timestamp of the request
            - environment (str): Current Paradex environment
            - error (str): Error message
            - account_summary (None): Null value for account summary
    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults/account-summary", params={"address": vault_address})
        return response
    except Exception as e:
        logger.error(f"Error fetching account summary for vault {vault_address}: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT.value,
            "error": str(e),
            "account_summary": None
        }
    