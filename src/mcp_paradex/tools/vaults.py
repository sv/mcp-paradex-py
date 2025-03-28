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

from pydantic import BaseModel, Field, TypeAdapter

from mcp_paradex.models import (
    Position,
    Vault,
    VaultAccountSummary,
    VaultBalance,
    VaultStrategy,
    VaultSummary,
)
from mcp_paradex.server.server import server
from mcp_paradex.utils.config import config
from mcp_paradex.utils.paradex_client import api_call, get_paradex_client

logger = logging.getLogger(__name__)

vault_strategy_adapter = TypeAdapter(list[VaultStrategy])


@server.tool("paradex-vault-list")
async def get_vault_list() -> list[VaultStrategy]:
    """
    Get a list of available vaults from Paradex.

    Retrieves all available vaults on Paradex, including their addresses and names.
    This tool requires no parameters and returns a comprehensive list of
    all vaults that can be accessed on Paradex.

    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults")
        if "error" in response:
            raise Exception(response["error"])
        results = response["results"]
        vault_list = vault_strategy_adapter.validate_python(results)
        return vault_list
    except Exception as e:
        logger.error(f"Error fetching vaults: {e!s}")
        raise e


vault_adapter = TypeAdapter(list[Vault])


@server.tool("paradex-vault-details")
async def get_vault_details(
    vault_address: str = Field(description="The address of the vault to get details for."),
) -> list[Vault]:
    """
    Get detailed information about a specific vault.

    Retrieves comprehensive details about a specific vault identified by its address,
    including configuration, permissions, and other vault-specific parameters.

    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults", params={"address": vault_address})
        if "error" in response:
            raise Exception(response["error"])
        results = response["results"]
        vaults = vault_adapter.validate_python(results)
        return vaults
    except Exception as e:
        logger.error(f"Error fetching vault details for {vault_address}: {e!s}")
        raise e


class VaultConfig(BaseModel):
    """Vault configuration model."""

    vault_factory_address: str
    max_profit_share_percentage: str
    min_lockup_period_days: str
    max_lockup_period_days: str
    min_initial_deposit: str
    min_owner_share_percentage: str


@server.tool("paradex-vaults-config")
async def get_vaults_config() -> VaultConfig:
    """
    Get global configuration for vaults from Paradex.

    Retrieves system-wide configuration parameters for vaults on Paradex,
    including fee structures, limits, and other global settings that apply
    to all vaults on the platform.
    """
    try:
        client = await get_paradex_client()
        response = await api_call(client, "vaults/config")
        config = VaultConfig.validate_python(response)
        return config

    except Exception as e:
        logger.error(f"Error fetching vaults configuration: {e!s}")
        raise e


vault_balance_adapter = TypeAdapter(list[VaultBalance])


@server.tool("paradex-vault-balance")
async def get_vault_balance(
    vault_address: str = Field(description="The address of the vault to get balance for."),
) -> list[VaultBalance]:
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
        if "error" in response:
            raise Exception(response["error"])
        results = response["results"]
        balances = vault_balance_adapter.validate_python(results)
        return balances
    except Exception as e:
        logger.error(f"Error fetching balance for vault {vault_address}: {e!s}")
        raise e


vault_summary_adapter = TypeAdapter(list[VaultSummary])


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
        if "error" in response:
            raise Exception(response["error"])
        results = response["results"]
        summary = vault_summary_adapter.validate_python(results)
        return summary
    except Exception as e:
        logger.error(f"Error fetching summary for vault {vault_address}: {e!s}")
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
        logger.error(f"Error fetching transfers for vault {vault_address}: {e!s}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "environment": config.ENVIRONMENT,
            "error": str(e),
            "transfers": None,
        }


position_adapter = TypeAdapter(list[Position])


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
        positions = position_adapter.validate_python(response["results"])
        return positions
    except Exception as e:
        logger.error(f"Error fetching positions for vault {vault_address}: {e!s}")
        raise e


vault_account_summary_adapter = TypeAdapter(list[VaultAccountSummary])


@server.tool("paradex-vault-account-summary")
async def get_vault_account_summary(
    vault_address: str = Field(description="The address of the vault to get account summary for."),
) -> list[VaultAccountSummary]:
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
        if "error" in response:
            raise Exception(response["error"])
        results = response["results"]
        summary = vault_account_summary_adapter.validate_python(results)
        return summary
    except Exception as e:
        logger.error(f"Error fetching account summary for vault {vault_address}: {e!s}")
        raise e
