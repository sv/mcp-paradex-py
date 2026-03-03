"""
MCP server implementation for Paradex integration.
"""

import argparse
import logging
import os
import sys
from typing import Any

from mcp.server.fastmcp.server import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

from mcp_paradex import __version__
from mcp_paradex.utils.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("mcp-paradex")


class RejectGetMiddleware:
    """
    Rejects GET requests with 405 in stateless HTTP mode.

    In stateless mode (Lambda), GET /mcp would open a persistent SSE stream that
    Lambda cannot hold open. Returning 405 causes MCP clients to fall back to
    POST-only mode, which works correctly with Lambda's request/response model.
    """

    def __init__(self, app: ASGIApp, mcp_path: str = "/mcp") -> None:
        self.app = app
        self.mcp_path = mcp_path

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["method"] == "GET" and scope["path"] == self.mcp_path:
            response = Response(
                content="Method Not Allowed: GET is not supported in stateless mode",
                status_code=405,
                headers={"Allow": "POST"},
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


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
        "version": __version__,
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
        choices=["stdio", "streamable-http"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="Transport to use (stdio or streamable-http) [env: MCP_TRANSPORT]",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MCP_PORT", str(config.SERVER_PORT))),
        help=f"Port for streamable-http transport (default: {config.SERVER_PORT}) [env: MCP_PORT]",
    )
    parser.add_argument(
        "--stateless",
        action="store_true",
        default=os.environ.get("MCP_STATELESS", "").lower() in ("1", "true", "yes"),
        help="Enable stateless HTTP mode (required for Lambda / serverless deployments) [env: MCP_STATELESS]",
    )
    args = parser.parse_args()

    logger.info(f"Starting MCP Paradex server with {args.transport} transport...")

    try:
        if args.transport == "streamable-http":
            import uvicorn

            server.settings.port = args.port
            server.settings.stateless_http = args.stateless
            server.settings.host = "0.0.0.0"  # bind all interfaces for container deployments
            # Disable DNS rebinding protection: the Host header won't be localhost
            # when running behind Lambda Function URL / CloudFront. Security is
            # handled at the infrastructure layer (TLS, IAM, CloudFront).
            server.settings.transport_security = TransportSecuritySettings(
                enable_dns_rebinding_protection=False
            )
            starlette_app = server.streamable_http_app()
            if args.stateless:
                # Wrap with middleware that rejects GET requests.
                # In stateless mode GET /mcp would open a persistent SSE stream
                # that Lambda cannot hold — 405 makes clients fall back to POST-only.
                starlette_app = RejectGetMiddleware(
                    starlette_app, mcp_path=server.settings.streamable_http_path
                )

            import anyio

            async def _serve() -> None:
                config = uvicorn.Config(
                    starlette_app,
                    host=server.settings.host,
                    port=server.settings.port,
                    log_level=server.settings.log_level.lower(),
                )
                await uvicorn.Server(config).serve()

            anyio.run(_serve)
        else:
            server.run(transport=args.transport)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Error running server: {e}")
        sys.exit(1)

    logger.info("Server stopped")
