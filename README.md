# MCP Paradex Server

[![smithery badge](https://smithery.ai/badge/@sv/mcp-paradex-py)](https://smithery.ai/server/@sv/mcp-paradex-py)

Model Context Protocol (MCP) server implementation for the Paradex trading platform.

## Overview

This project provides a bridge between AI assistants (like Claude) and the Paradex perpetual futures trading platform. Using the MCP standard, AI assistants can:

- Retrieve market data from Paradex
- Manage trading accounts and vaults
- Place and manage orders
- Monitor positions and balance

## Prerequisites

- Python 3.10+

## Installation

### Installing via Smithery

To install mcp-paradex-py for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@sv/mcp-paradex-py):

```bash
npx -y @smithery/cli install @sv/mcp-paradex-py --client claude
```

### Using pip

1. Clone this repository:

   ```bash
   git clone https://github.com/sv/mcp-paradex-py.git
   cd mcp-paradex-py
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
   git clone https://github.com/sv/mcp-paradex-py.git
   cd mcp-paradex-py
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

### Docker (recommended)

```
docker build . -t sv/mcp-paradex-py
```

### In Cursor add MCP as command

Public only

```
docker run --rm -i sv/mcp-paradex-py
```

Allow trading

```
docker run --rm -e PARADEX_ACCOUNT_PRIVATE_KEY=0xprivatekey -i sv/mcp-paradex-py
```

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
        "PARADEX_ACCOUNT_PRIVATE_KEY": "your_private_key"
      }
    }
  }
}
```

4. Replace `your_ethereum_private_key` with your actual Paradex private key
5. Save the file and restart Claude Desktop

### Smithery.ai Registry

The server includes a `smithery.yaml` file with metadata for the Smithery.ai registry. If you want to publish this server to Smithery.ai, you can use the Smithery CLI:

```bash
# Install Smithery CLI
npm install -g @smithery/cli

# Login to Smithery
smithery login

# Publish the server
smithery publish
```

For more information about publishing to Smithery.ai, see the [Smithery documentation](https://smithery.ai/docs).

## Available Resources and Tools

### Resources

#### System Resources

- `system://status` - Get the current status of the system and Paradex connection
- `system://version` - Get detailed version information about the server and dependencies
- `system://health` - Perform a basic health check of the server

#### Market Resources

- `market://public/markets` - Get a list of available markets from Paradex
- `market://public/info` - Get general market information and status

#### Vault Resources

- `vaults://list` - List all vaults associated with the account
- `vaults://balance` - Get the balance of a specific vault
- `vaults://details` - Get detailed information about a vault

### Tools

#### System Tools

- `check_public_api` - Check the connection to Paradex public API without authentication
- `check_paradex_connection` - Verify connectivity with Paradex API using authentication

#### Market Tools

- `get_market_data` - Retrieve detailed market data for a specific market
- `get_orderbook` - Get the current orderbook for a market
- `get_recent_trades` - Retrieve recent trades for a market

#### Account Tools

- `get_account_info` - Get information about the connected account
- `get_account_balance` - Retrieve the account balance

#### Order Tools

- `place_order` - Place a new order on Paradex
- `cancel_order` - Cancel an existing order
- `get_order_status` - Check the status of an order

#### Vault Tools

- `create_vault` - Create a new vault
- `deposit_to_vault` - Deposit funds into a vault
- `withdraw_from_vault` - Withdraw funds from a vault

## Development

### Project Structure

- `src/mcp_paradex/` - Main package
  - `server/` - MCP server implementation
    - `server.py` - FastMCP server configuration
  - `resources/` - Read-only data resources
    - `system.py` - System status resource
    - `market.py` - Market data resources
    - `vaults.py` - Vault management resources
  - `tools/` - Action tools for operations
    - `system.py` - System management tools
    - `market.py` - Market data tools
    - `account.py` - Account management tools
    - `orders.py` - Order management tools
    - `vaults.py` - Vault management tools
  - `utils/` - Utility functions and helpers
    - `config.py` - Configuration handling
    - `paradex_client.py` - Paradex API client

### Development Progress

- [x] **Step 1:** Create Basic Project Structure

  - Set up package configuration and dependencies
  - Create initial FastMCP server configuration
  - Implement basic system health checks

- [x] **Step 2:** Implement Authentication Layer

  - Design secure API key management system
  - Create authentication flow for Paradex API

- [x] **Step 3:** Deploy Basic Server with Health Check

  - Implement system status resource
  - Create connectivity verification tool
  - Add public API endpoints that don't require authentication

- [x] **Step 4:** Market Data Integration

  - Implement market data resources
  - Create market data tools
  - Add orderbook and trade history functionality

- [x] **Step 5:** Account and Order Management

  - Implement account information resources
  - Create order management tools
  - Add vault management capabilities

- [x] **Step 6:** Add Smithery.ai Support
  - Create Smithery.ai configuration file
  - Add Claude Desktop configuration example
  - Document Smithery.ai integration

### Code Quality Tools

This project uses several tools to maintain code quality:

- **Black**: Code formatter that enforces a consistent style
- **Ruff**: Fast Python linter that combines functionality from multiple linting tools
- **Mypy**: Static type checker for Python
- **Pre-commit**: Git hook scripts to automate checks before commits

### Setup Development Environment

1. Install development dependencies:

   ```bash
   make install-dev
   ```

2. Format code:

   ```bash
   make format
   ```

3. Lint code:

   ```bash
   make lint
   ```

4. Type check:

   ```bash
   make typecheck
   ```

5. Run all checks:

   ```bash
   make check
   ```

6. Run pre-commit on all files:

   ```bash
   make pre-commit
   ```

7. Run tests:

   ```bash
   make test
   ```

8. Run tests with coverage report:
   ```bash
   make test-cov
   ```

### Testing

This project uses pytest for testing. Tests are located in the `tests` directory.

To run tests:

```bash
pytest
```

To run tests with coverage report:

```bash
pytest --cov=mcp_paradex --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov` directory.

### Pre-commit Hooks

Pre-commit hooks are configured to run automatically on git commit. They include:

- Trailing whitespace removal
- End-of-file fixer
- YAML/TOML syntax checking
- Black formatting
- Ruff linting
- Mypy type checking

To manually run all pre-commit hooks on all files:

```bash
pre-commit run --all-files
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
