"""
Tests for the run_cli argument parsing and transport wiring in server.py.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Import the module explicitly so patch() can resolve the dotted path.
import mcp_paradex.server.server as server_module
from mcp_paradex.utils.config import config


class TestTransportChoices:
    """Argparse-level validation of --transport choices."""

    def test_stdio_is_accepted(self) -> None:
        mock_server = MagicMock()
        with (
            patch.object(server_module, "server", mock_server),
            patch("sys.argv", ["mcp-paradex", "--transport", "stdio"]),
        ):
            server_module.run_cli()

        mock_server.run.assert_called_once_with(transport="stdio")

    def test_streamable_http_is_accepted(self) -> None:
        mock_server = MagicMock()
        mock_server.settings = MagicMock()
        with (
            patch.object(server_module, "server", mock_server),
            patch("sys.argv", ["mcp-paradex", "--transport", "streamable-http"]),
            patch("anyio.run"),
        ):
            server_module.run_cli()

        mock_server.streamable_http_app.assert_called_once()

    def test_sse_is_rejected(self) -> None:
        with (
            patch("sys.argv", ["mcp-paradex", "--transport", "sse"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            server_module.run_cli()

        assert exc_info.value.code == 2  # argparse exits with code 2 on bad args

    def test_default_transport_is_stdio(self) -> None:
        mock_server = MagicMock()
        with (
            patch.object(server_module, "server", mock_server),
            patch("sys.argv", ["mcp-paradex"]),
        ):
            server_module.run_cli()

        mock_server.run.assert_called_once_with(transport="stdio")


class TestPortWiring:
    """Verify that --port is applied to server.settings only for streamable-http."""

    def test_port_set_for_streamable_http(self) -> None:
        mock_server = MagicMock()
        mock_server.settings = MagicMock()
        with (
            patch.object(server_module, "server", mock_server),
            patch(
                "sys.argv",
                ["mcp-paradex", "--transport", "streamable-http", "--port", "4242"],
            ),
            patch("anyio.run"),
        ):
            server_module.run_cli()

        assert mock_server.settings.port == 4242

    def test_port_not_set_for_stdio(self) -> None:
        mock_server = MagicMock()
        mock_server.settings = MagicMock()
        # Read the auto-generated child mock before the call; if port is never
        # assigned it will still be this same object afterward.
        original_port = mock_server.settings.port
        with (
            patch.object(server_module, "server", mock_server),
            patch("sys.argv", ["mcp-paradex", "--transport", "stdio", "--port", "4242"]),
        ):
            server_module.run_cli()

        # settings.port must NOT have been written for stdio
        assert mock_server.settings.port is original_port

    def test_default_port_equals_config(self) -> None:
        mock_server = MagicMock()
        mock_server.settings = MagicMock()
        with (
            patch.object(server_module, "server", mock_server),
            patch("sys.argv", ["mcp-paradex", "--transport", "streamable-http"]),
            patch("anyio.run"),
        ):
            server_module.run_cli()

        assert mock_server.settings.port == config.SERVER_PORT

    def test_host_set_to_all_interfaces_for_streamable_http(self) -> None:
        mock_server = MagicMock()
        mock_server.settings = MagicMock()
        with (
            patch.object(server_module, "server", mock_server),
            patch("sys.argv", ["mcp-paradex", "--transport", "streamable-http"]),
            patch("anyio.run"),
        ):
            server_module.run_cli()

        assert mock_server.settings.host == "0.0.0.0"


class TestStatelessFlag:
    """Verify --stateless wires into server.settings.stateless_http."""

    def test_stateless_enabled(self) -> None:
        mock_server = MagicMock()
        mock_server.settings = MagicMock()
        with (
            patch.object(server_module, "server", mock_server),
            patch(
                "sys.argv",
                ["mcp-paradex", "--transport", "streamable-http", "--stateless"],
            ),
            patch("anyio.run"),
        ):
            server_module.run_cli()

        assert mock_server.settings.stateless_http is True

    def test_stateless_defaults_to_false(self) -> None:
        mock_server = MagicMock()
        mock_server.settings = MagicMock()
        with (
            patch.object(server_module, "server", mock_server),
            patch("sys.argv", ["mcp-paradex", "--transport", "streamable-http"]),
            patch("anyio.run"),
        ):
            server_module.run_cli()

        assert mock_server.settings.stateless_http is False
