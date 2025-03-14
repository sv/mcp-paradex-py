"""
MCP Paradex server entry point for module execution.
"""

import os
import sys

# Add the parent directory to sys.path to allow imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import and run the main function
from mcp_paradex.resources import *
from mcp_paradex.server.server import run_cli

if __name__ == "__main__":
    run_cli()
