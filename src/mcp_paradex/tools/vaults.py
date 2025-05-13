"""
Vault management tools for Paradex.

This module provides tools for retrieving information about Paradex vaults,
which are smart contracts that allow users to deposit funds and trade on Paradex
with self-custody. These tools help with monitoring vault status, balances,
positions, and transaction history.
"""

import logging
from datetime import datetime
from typing import Annotated, Any

from pydantic import Field, TypeAdapter

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
from mcp_paradex.utils.jmespath_utils import apply_jmespath_filter
from mcp_paradex.utils.paradex_client import api_call, get_paradex_client

logger = logging.getLogger(__name__)

vault_strategy_adapter = TypeAdapter(list[VaultStrategy])


vault_adapter = TypeAdapter(list[Vault])


@server.tool(name="paradex_vaults")
async def get_vaults(
    vault_address: Annotated[
        str,
        Field(
            default="",
            description="The address of the vault to get details for or empty string to get all vaults.",
        ),
    ],
    jmespath_filter: Annotated[
        str,
        Field(
            default=None, description="JMESPath expression to filter, sort, or limit the results."
        ),
    ],
    limit: Annotated[
        int,
        Field(
            default=10,
            gt=0,
            le=100,
            description="Limit the number of results to the specified number.",
        ),
    ],
    offset: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            description="Offset the results to the specified number.",
        ),
    ],
) -> dict:
    """
    Get detailed information about a specific vault or all vaults if no address is provided.

    Retrieves comprehensive details about a specific vault identified by its address,
    including configuration, permissions, and other vault-specific parameters.

    Use jmespath_filter to reduce the number of results as much as possible as number of vaults can be large.

    You can use JMESPath expressions to filter, sort, or limit the results.
    Examples:
    - Filter by owner: "[?owner_account=='0x123...']"
    - Filter by status: "[?status=='ACTIVE']"
    - Find vaults with specific strategy: "[?contains(strategies, 'strategy_id')]"
    - Sort by creation date: "sort_by([*], &created_at)"
    - Limit to newest vaults: "sort_by([*], &created_at)[-5:]"
    - Select specific fields: "[*].{address: address, name: name, kind: kind, status: status}"
    """
    try:
        client = await get_paradex_client()
        params = {"address": vault_address} if vault_address else None
        response = await api_call(client, "vaults", params=params)
        if "error" in response:
            raise Exception(response["error"])
        results = response["results"]
        vaults = vault_adapter.validate_python(results)

        # Apply JMESPath filter if provided
        if jmespath_filter:
            vaults = apply_jmespath_filter(
                data=vaults,
                jmespath_filter=jmespath_filter,
                type_adapter=vault_adapter,
                error_logger=logger.error,
            )
        sorted_vaults = sorted(vaults, key=lambda x: x.created_at, reverse=True)
        result_vaults = sorted_vaults[offset : offset + limit]
        result = {
            "description": Vault.__doc__.strip() if Vault.__doc__ else None,
            "fields": Vault.model_json_schema(),
            "vaults": result_vaults,
            "total": len(sorted_vaults),
            "limit": limit,
            "offset": offset,
        }
        return result
    except Exception as e:
        logger.error(f"Error fetching vault details: {e!s}")
        raise e


vault_balance_adapter = TypeAdapter(list[VaultBalance])


@server.tool(name="paradex_vault_balance")
async def get_vault_balance(
    vault_address: Annotated[
        str, Field(description="The address of the vault to get balance for.")
    ],
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


@server.tool(name="paradex_vault_summary")
async def get_vault_summary(
    vault_address: Annotated[
        str,
        Field(
            default=None,
            description="The address of the vault to get summary for or None to get all vaults.",
        ),
    ],
    jmespath_filter: Annotated[
        str,
        Field(default=None, description="JMESPath expression to filter or transform the result."),
    ],
    limit: Annotated[
        int,
        Field(
            default=10,
            gt=0,
            le=100,
            description="Limit the number of results to the specified number.",
        ),
    ],
    offset: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            description="Offset the results to the specified number.",
        ),
    ],
) -> dict:
    """
    Get a comprehensive summary of a specific vault or all vaults if no address is provided.

    Retrieves a summary of all important information about a vault,
    including balance, positions, recent activity, and performance metrics.
    This provides a high-level overview of the vault's current state.

    Use jmespath_filter to reduce the number of results as much as possible as number of vaults can be large.

    You can use JMESPath expressions to filter, sort, or transform the results.
    Examples:
    - Filter by TVL: "[?to_number(tvl) > `10000`]"
    - Filter by performance: "[?to_number(total_roi) > `5.0`]"
    - Sort by TVL (descending): "reverse(sort_by([*], &to_number(tvl)))"
    - Get top performers: "sort_by([*], &to_number(total_roi))[-3:]"
    - Filter by recent returns: "[?to_number(roi_24h) > `0.5`]"
    - Extract specific metrics: "[*].{address: address, tvl: tvl, total_roi: total_roi, volume_24h: volume_24h}"
    """
    try:
        client = await get_paradex_client()
        params = {"address": vault_address} if vault_address else None
        response = await api_call(client, "vaults/summary", params=params)
        if "error" in response:
            raise Exception(response["error"])
        results = response["results"]
        summary = vault_summary_adapter.validate_python(results)

        # Apply JMESPath filter if provided
        if jmespath_filter:
            summary = apply_jmespath_filter(
                data=summary,
                jmespath_filter=jmespath_filter,
                type_adapter=vault_summary_adapter,
                error_logger=logger.error,
            )
        sorted_summary = sorted(summary, key=lambda x: x.address, reverse=True)
        result_summary = sorted_summary[offset : offset + limit]
        result = {
            "description": VaultSummary.__doc__.strip() if VaultSummary.__doc__ else None,
            "fields": VaultSummary.model_json_schema(),
            "vaults": result_summary,
            "total": len(sorted_summary),
            "limit": limit,
            "offset": offset,
        }
        return result
    except Exception as e:
        logger.error(f"Error fetching summary for vault {vault_address}: {e!s}")
        raise e


@server.tool(name="paradex_vault_transfers")
async def get_vault_transfers(
    vault_address: Annotated[
        str, Field(description="The address of the vault to get transfers for.")
    ],
) -> dict[str, Any]:
    """
    Track deposit and withdrawal history for auditing and reconciliation.

    Use this tool when you need to:
    - Verify deposits have completed and are available for trading
    - Track withdrawal status and confirm transaction settlement
    - Audit the complete fund flow history for a vault
    - Reconcile on-chain transactions with platform records
    - Understand historical capital allocation patterns

    Complete transfer history is essential for proper accounting and provides
    a clear audit trail of all capital movements.

    Example use cases:
    - Confirming that a recent deposit was credited to your account
    - Tracking the status of pending withdrawals
    - Creating transaction reports for accounting or tax purposes
    - Verifying the total amount deposited over time
    - Analyzing deposit/withdrawal patterns for strategy insights
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


@server.tool(name="paradex_vault_positions")
async def get_vault_positions(
    vault_address: Annotated[
        str, Field(description="The address of the vault to get positions for.")
    ],
) -> list[Position]:
    """
    Monitor active trading positions to track performance and manage risk.

    Use this tool when you need to:
    - Get a complete view of all open positions for a vault
    - Monitor unrealized P&L across all positions
    - Check liquidation prices and margin requirements
    - Assess position sizing and leverage across markets
    - Track entry prices and position duration

    Position monitoring is fundamental to risk management and provides
    the necessary information for trade management decisions.

    Example use cases:
    - Checking the current status of all open trades
    - Monitoring unrealized profit/loss across positions
    - Assessing liquidation risk during market volatility
    - Comparing performance across different markets
    - Planning adjustments to position sizes or leverage
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


@server.tool(name="paradex_vault_account_summary")
async def get_vault_account_summary(
    vault_address: Annotated[
        str, Field(description="The address of the vault to get account summary for.")
    ],
) -> list[VaultAccountSummary]:
    """
    Get a comprehensive overview of a vault's trading account status.

    Use this tool when you need to:
    - Check account health and available margin
    - Monitor total exposure and leverage
    - Understand risk metrics and account status
    - Assess trading capacity before placing new orders
    - Get a consolidated view of account performance

    This provides essential information about account standing and
    trading capacity to inform risk management decisions.

    Example use cases:
    - Checking available margin before placing new orders
    - Monitoring account health during market volatility
    - Assessing total exposure across all markets
    - Understanding maintenance margin requirements
    - Planning position adjustments based on account metrics
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
