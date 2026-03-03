"""
Paradex API client utilities.
"""

import asyncio
import logging
import time
from typing import Any

import httpx
from paradex_py.account.account import ParadexAccount
from paradex_py.api.api_client import ParadexApiClient

from mcp_paradex.utils.config import config

logger = logging.getLogger(__name__)

# Singleton instance of the Paradex client
_paradex_client: ParadexApiClient | None = None
_client_lock = asyncio.Lock()


async def get_paradex_client() -> ParadexApiClient:
    """
    Get or initialize the Paradex client.

    Returns:
        Paradex: The initialized Paradex client.

    Raises:
        ValueError: If the required configuration is not set.
    """
    global _paradex_client

    if _paradex_client is not None:
        return _paradex_client

    async with _client_lock:
        # Double-check in case another task initialized it while waiting
        if _paradex_client is not None:
            return _paradex_client

        logger.info("Initializing Paradex client env=%s", config.ENVIRONMENT)
        # retries=1 on the transport causes httpx to retry automatically on a fresh
        # connection when a pooled connection is stale (e.g. after a Lambda freeze).
        http_client = httpx.Client(
            transport=httpx.HTTPTransport(retries=1),
            timeout=httpx.Timeout(30.0),
        )
        _paradex_client = ParadexApiClient(
            env=config.ENVIRONMENT, logger=logger, http_client=http_client
        )
        logger.info("Paradex client api_url=%s", _paradex_client.api_url)

        if config.PARADEX_ACCOUNT_PRIVATE_KEY:
            logger.info("Authenticating Paradex client")
            response = _paradex_client.fetch_system_config()
            acc = ParadexAccount(
                config=response,
                l1_address="0x0000000000000000000000000000000000000000",
                l2_private_key=config.PARADEX_ACCOUNT_PRIVATE_KEY,
            )
            _paradex_client.init_account(acc)
            logger.info("Paradex client authenticated account=%s", _paradex_client.account)

        return _paradex_client


async def get_authenticated_paradex_client() -> ParadexApiClient:
    """
    Get or initialize the authenticated Paradex client.

    Returns:
        Paradex: The initialized Paradex client.

    Raises:
        ValueError: If the required configuration is not set.
    """
    client = await get_paradex_client()
    if client.account is None:
        raise ValueError("Paradex client is not authenticated")
    return client


async def api_call(
    client: ParadexApiClient, path: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Make a direct API call to Paradex.

    Args:
        client: The Paradex client instance.
        path: The API path to call.
        params: Optional parameters for the API call.

    Returns:
        Dict[str, Any]: The response from the API call.
    """
    url = f"{client.api_url}/{path}"
    logger.info("API call url=%s params=%s", url, params)
    t0 = time.monotonic()
    try:
        response = client.get(client.api_url, path, params)
        logger.info("API call url=%s completed ms=%.0f", url, (time.monotonic() - t0) * 1000)
        return response
    except Exception as exc:
        logger.error(
            "API call url=%s failed ms=%.0f error=%s: %s",
            url,
            (time.monotonic() - t0) * 1000,
            type(exc).__name__,
            exc,
        )
        raise
