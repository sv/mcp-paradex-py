"""
Vault management tools for Paradex.

This module provides tools for retrieving information about Paradex vaults,
which are smart contracts that allow users to deposit funds and trade on Paradex
with self-custody. These tools help with monitoring vault status, balances,
positions, and transaction history.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field

from mcp_paradex.server.server import server
from mcp_paradex.tools.account import Position
from mcp_paradex.utils.config import config
from mcp_paradex.utils.paradex_client import api_call, get_paradex_client

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

        vault_list = [
            {"address": vault["address"], "name": vault["name"]} for vault in response["results"]
        ]
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "vaults": vault_list,
            "count": len(vault_list),
        }
    except Exception as e:
        logger.error(f"Error fetching vaults: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "vaults": [],
            "count": 0,
        }


class Vault(BaseModel):
    address: str
    name: str
    description: str
    owner_account: str
    operator_account: str
    strategies: list[str]
    token_address: str
    status: str
    kind: str
    profit_share: int
    lockup_period: int
    max_tvl: int
    created_at: int
    last_updated_at: int


@server.tool("paradex-vault-details")
async def get_vault_details(
    vault_address: str = Field(description="The address of the vault to get details for."),
) -> Vault:
    """
    Get detailed information about a specific vault.

    Retrieves comprehensive details about a specific vault identified by its address,
    including configuration, permissions, and other vault-specific parameters.

    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults", params={"address": vault_address})
        vault = Vault(**response["results"])
        return vault
    except Exception as e:
        logger.error(f"Error fetching vault details for {vault_address}: {str(e)}")
        raise e


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
            "environment": config.ENVIRONMENT,
            "config": response,
        }
    except Exception as e:
        logger.error(f"Error fetching vaults configuration: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "config": None,
        }


# # {
#             "token": "USDC",
#             "size": "6285318.024264880744",
#             "last_updated_at": 1741934596912
#         }
class VaultBalance(BaseModel):
    token: str
    size: str
    last_updated_at: int


@server.tool("paradex-vault-balance")
async def get_vault_balance(
    vault_address: str = Field(description="The address of the vault to get balance for."),
) -> VaultBalance:
    """
    Get the current balance of a specific vault.

    Retrieves the current balance information for a specific vault,
    including available funds, locked funds, and total balance.
    This is essential for understanding the financial state of a vault
    before executing trades or withdrawals.

    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults/balance", params={"address": vault_address})
        balance = VaultBalance(**response["results"])
        return balance
    except Exception as e:
        logger.error(f"Error fetching balance for vault {vault_address}: {str(e)}")
        raise e


# {
#             "address": "0x5f43c92dbe4e995115f351254407e7e84abf04cbe32a536345b9d6c36bc750f",
#             "owner_equity": "0.03076589",
#             "vtoken_supply": "12078498.10694",
#             "vtoken_price": "1.15894902",
#             "tvl": "13364818.6746007135",
#             "net_deposits": "13364818.6746007135",
#             "total_roi": "0.15905034",
#             "roi_24h": "-0.0004581",
#             "roi_7d": "0.00381278",
#             "roi_30d": "0.01666131",
#             "last_month_return": "0.20271261",
#             "total_pnl": "1012499.53",
#             "pnl_24h": "-6446.71",
#             "pnl_7d": "53575.37",
#             "pnl_30d": "233007.25",
#             "max_drawdown": "0.1880607",
#             "max_drawdown_24h": "0.00066735",
#             "max_drawdown_7d": "0.00131604",
#             "max_drawdown_30d": "0.1880607",
#             "volume": "3288225640.29",
#             "volume_24h": "3.196488724e+07",
#             "volume_7d": "2.6373742904e+08",
#             "volume_30d": "1.83300332466e+09",
#             "num_depositors": 1278
#         }
class VaultSummary(BaseModel):
    address: str
    owner_equity: str
    vtoken_supply: str
    vtoken_price: str
    tvl: str
    net_deposits: str
    total_roi: str
    roi_24h: str
    roi_7d: str
    roi_30d: str
    last_month_return: str
    total_pnl: str
    pnl_24h: str
    pnl_7d: str
    pnl_30d: str
    max_drawdown: str
    max_drawdown_24h: str
    max_drawdown_7d: str
    max_drawdown_30d: str
    volume: str
    volume_24h: str
    volume_7d: str
    volume_30d: str
    num_depositors: int


@server.tool("paradex-vault-summary")
async def get_vault_summary(
    vault_address: str = Field(description="The address of the vault to get summary for."),
) -> VaultSummary:
    """
    Get a comprehensive summary of a specific vault.

    Retrieves a summary of all important information about a vault,
    including balance, positions, recent activity, and performance metrics.
    This provides a high-level overview of the vault's current state.
    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults/summary", params={"address": vault_address})
        summary = VaultSummary(**response["results"])
        return summary
    except Exception as e:
        logger.error(f"Error fetching summary for vault {vault_address}: {str(e)}")
        raise e


@server.tool("paradex-vault-transfers")
async def get_vault_transfers(
    vault_address: str = Field(description="The address of the vault to get transfers for."),
) -> Dict[str, Any]:
    """
    Get a list of deposit and withdrawal transfers for a specific vault.

    Retrieves the history of all transfers (deposits and withdrawals) for a vault,
    including timestamps, amounts, transaction hashes, and status information.
    This is useful for auditing vault activity and tracking fund movements.


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
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "transfers": None,
        }


@server.tool("paradex-vault-positions")
async def get_vault_positions(
    vault_address: str = Field(description="The address of the vault to get positions for."),
) -> list[Position]:
    """
    Get a list of current trading positions for a specific vault.

    Retrieves all open trading positions for a vault, including market,
    size, entry price, liquidation price, unrealized PnL, and other
    position-specific information.
    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults/positions", params={"address": vault_address})
        positions = [Position(**position) for position in response["results"]]
        return positions
    except Exception as e:
        logger.error(f"Error fetching positions for vault {vault_address}: {str(e)}")
        raise e


class VaultAccountSummary(BaseModel):
    address: str
    deposited_amount: str
    vtoken_amount: str
    total_roi: str
    total_pnl: str
    created_at: int


@server.tool("paradex-vault-account-summary")
async def get_vault_account_summary(
    vault_address: str = Field(description="The address of the vault to get account summary for."),
) -> VaultAccountSummary:
    """
    Get a summary of trading account information for a specific vault.

    Retrieves a comprehensive summary of the trading account associated with
    a vault, including margin information, account health, risk metrics,
    and trading statistics.

    """
    try:
        client = await get_paradex_client()
        response = await api_call(
            client, "vaults/account-summary", params={"address": vault_address}
        )
        summary = VaultAccountSummary(**response["results"])
        return summary
    except Exception as e:
        logger.error(f"Error fetching account summary for vault {vault_address}: {str(e)}")
        raise e
