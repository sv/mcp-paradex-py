"""
MCP Paradex server entry point.
"""
from mcp_paradex.resources import *
from mcp_paradex.tools import *

from mcp_paradex.server.server import run_cli

if __name__ == "__main__":
    run_cli()
