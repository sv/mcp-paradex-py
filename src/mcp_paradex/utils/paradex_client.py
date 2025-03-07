"""
Paradex API client utilities.
"""
import asyncio
import logging
from typing import Optional, Dict, Any

from paradex_py.api.api_client import ParadexApiClient
from paradex_py.account.account import ParadexAccount


from paradex_py.api.models import  SystemConfigSchema
from mcp_paradex.utils.config import config

logger = logging.getLogger(__name__)

# Singleton instance of the Paradex client
_paradex_client: Optional[ParadexApiClient] = None
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
        
        # if not config.is_configured():
            # raise ValueError(
            #     "Paradex client configuration is incomplete. "
            #     "Make sure L1_ADDRESS and L1_PRIVATE_KEY are set."
            # )
            
        
        # _paradex_client = Paradex(
        #     env=config.ENVIRONMENT,
        #     logger=logger,
        #     l1_address=config.L1_ADDRESS,
        #     l1_private_key=config.L1_PRIVATE_KEY
        # )
        _paradex_client = ParadexApiClient(
            env=config.ENVIRONMENT.value,
            logger=logger
        )

        if config.PARADEX_ACCOUNT_PRIVATE_KEY:
            logger.info("Authenticating Paradex client")
            response = _paradex_client.fetch_system_config()
            acc = ParadexAccount(
                config=response,
                l1_address="0x0000000000000000000000000000000000000000",
                l2_private_key=config.PARADEX_ACCOUNT_PRIVATE_KEY,
            )
            _paradex_client.init_account(acc)
    
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


async def api_call(client: ParadexApiClient, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Make a direct API call to Paradex.
    
    Args:
        client: The Paradex client instance.
        path: The API path to call.
        params: Optional parameters for the API call.
        
    Returns:
        Dict[str, Any]: The response from the API call.
    """
    try:
        logger.info(f"Calling {path} with params: {params}")
        response = client.get(client.api_url, path, params)
        return response
    except Exception as e:
        logger.exception(f"Error calling {path}")
        raise 