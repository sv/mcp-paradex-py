"""
Tools module for MCP Paradex.
"""

from mcp_paradex.utils.config import config

# Import tools modules to register them with the server
from . import market, system, vaults

# Only register auth-required tools when authenticated
if config.is_configured():
    from . import account, orders
