# MCP Paradex Server

[![smithery badge](https://smithery.ai/badge/@sv/mcp-paradex-py)](https://smithery.ai/server/@sv/mcp-paradex-py)

Model Context Protocol (MCP) server implementation for the Paradex trading platform.

## Overview

This project provides a bridge between AI assistants (like Claude) and the Paradex perpetual futures trading platform. Using the MCP standard, AI assistants can:

- Retrieve market data from Paradex
- Manage trading accounts
- Place and manage orders
- Monitor positions and balance

## Prerequisites

- Python 3.10+
- Paradex account with API keys
- Ethereum L1 wallet address and private key

## Installation

### Installing via Smithery

To install mcp-paradex-py for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@sv/mcp-paradex-py):

```bash
npx -y @smithery/cli install @sv/mcp-paradex-py --client claude
```

### Using pip

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/mcp-paradex.git
   cd mcp-paradex
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

### Using uv (faster alternative)

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/mcp-paradex.git
   cd mcp-paradex
   ```

2. Create a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

### Configuration

Set up your configuration:
```bash
cp .env.template .env
```
Then edit the `.env` file with your Paradex credentials.

## Running the Server

### Standard Mode (stdio transport)

This is the default mode, suitable for use with CLI tools like the MCP CLI:

```bash
python main.py
```

### Web Server Mode (SSE transport)

This mode starts a web server, suitable for integration with web applications:

```bash
python main.py --transport sse
```

The server will be available at http://0.0.0.0:8000 by default.

Note: The port is currently fixed at 8000 for the SSE transport.

## Smithery.ai Integration

This MCP server is compatible with [Smithery.ai](https://smithery.ai/), a platform for discovering and deploying MCP servers.

### Claude Desktop Configuration

To use this server with Claude Desktop via Smithery.ai:

1. Open Claude Desktop and enable Developer Mode from the menu
2. Go to Settings > Developer and click "Edit Config"
3. Add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paradex": {
      "command": "uvx",
      "args": ["--with-editable", ".", "mcp-paradex"],
      "env": {
        "PARADEX_ENVIRONMENT": "testnet",
        "PARADEX_L1_ADDRESS": "your_ethereum_address",
        "PARADEX_L1_PRIVATE_KEY": "your_ethereum_private_key"
      }
    }
  }
}
```

4. Replace `your_ethereum_address` and `your_ethereum_private_key` with your actual Ethereum address and private key
5. Save the file and restart Claude Desktop

### Smithery.ai Registry

The server includes a `smithery.json` file with metadata for the Smithery.ai registry. If you want to publish this server to Smithery.ai, you can use the Smithery CLI:

```bash
# Install Smithery CLI
npm install -g @smithery/cli

# Login to Smithery
smithery login

# Publish the server
smithery publish
```

For more information about publishing to Smithery.ai, see the [Smithery documentation](https://smithery.ai/docs).

## Development

### Project Structure

- `src/mcp_paradex/` - Main package
  - `server/` - MCP server implementation
    - `server.py` - FastMCP server configuration
  - `resources/` - Read-only data resources
    - `system.py` - System status resource
    - `market.py` - Market data resources
  - `tools/` - Action tools for operations
    - `system.py` - System management tools
  - `utils/` - Utility functions and helpers
    - `config.py` - Configuration handling
    - `paradex_client.py` - Paradex API client

### Available Resources and Tools

#### Resources (No Authentication Required)

- `system://status` - Get the current status of the system and Paradex connection
- `system://version` - Get detailed version information about the server and dependencies
- `system://health` - Perform a basic health check of the server
- `market://public/markets` - Get a list of available markets from Paradex
- `market://public/info` - Get general market information and status

#### Tools (No Authentication Required)

- `check_public_api` - Check the connection to Paradex public API without authentication

#### Tools (Authentication Required)

- `check_paradex_connection` - Verify connectivity with Paradex API using authentication

### Development Progress

- [x] **Step 1:** Create Basic Project Structure
  - Set up package configuration and dependencies
  - Create initial FastMCP server configuration
  - Implement basic system health checks

- [x] **Step 3:** Deploy Basic Server with Health Check
  - Implement system status resource
  - Create connectivity verification tool
  - Add public API endpoints that don't require authentication

- [x] **Step 6:** Add Smithery.ai Support
  - Create Smithery.ai configuration file
  - Add Claude Desktop configuration example
  - Document Smithery.ai integration

- [ ] **Step 2:** Implement Authentication Layer
  - Design secure API key management system
  - Create authentication flow for Paradex API

- [ ] **Step 4:** Begin Market Data Integration
  - Implement market data resources
  - Create caching layer

- [ ] **Step 5:** Advanced Features and Integration

### Adding New Capabilities

- Resources: Add new resources in `resources/` directory
- Tools: Add new tools in `tools/` directory

## License

[MIT License](LICENSE)
