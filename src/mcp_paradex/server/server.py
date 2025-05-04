"""
MCP server implementation for Paradex integration.
"""

import argparse
import logging
import sys
from http.client import HTTPException
from typing import Any

from exceptions import HTTPException, http_exception
from mcp.server.fastmcp.server import FastMCP
from workers import DurableObject

from mcp_paradex.utils.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("mcp-paradex")


def create_server() -> FastMCP:
    """
    Create and configure the FastMCP server instance.

    Returns:
        FastMCP: The configured server instance.
    """
    # Server metadata
    server_metadata: dict[str, Any] = {
        "name": config.SERVER_NAME,
        "description": "MCP server for Paradex trading platform",
        "vendor": "Model Context Protocol",
        "version": "0.1.0",
    }

    # Create server instance
    server = FastMCP(
        name=config.SERVER_NAME,
    )

    return server


# Singleton instance of the server
server = create_server()

from mcp_paradex.prompts import *
from mcp_paradex.resources import *
from mcp_paradex.tools import *


def run_cli() -> None:
    """
    Run the MCP Paradex server from the command line.
    This function is used as an entry point in pyproject.toml.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP Paradex Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport to use (stdio or sse)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.SERVER_PORT,
        help=f"Port for SSE transport (default: {config.SERVER_PORT})",
    )
    args = parser.parse_args()

    logger.info(f"Starting MCP Paradex server with {args.transport} transport...")

    try:
        server.run(transport=args.transport)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Error running server: {e}")
        sys.exit(1)

    logger.info("Server stopped")


class FastMCPServer(DurableObject):
    def __init__(self, ctx, env, mcp: FastMCP):
        self.ctx = ctx
        self.env = env
        self.mcp = mcp
        self.app = mcp.sse_app()
        from starlette.middleware import Middleware
        from starlette.middleware.cors import CORSMiddleware

        self.app.add_exception_handler(HTTPException, http_exception)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

    async def call(self, request):
        import asgi

        return await asgi.fetch(self.app, request, self.env, self.ctx)


async def on_fetch(request, env):
    id = env.ns.idFromName("example")
    obj = env.ns.get(id)
    return await obj.call(request)
