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

- `paradex_system_config` - Get global Paradex system configuration
- `paradex_system_state` - Get current system state

#### Market Tools

- `paradex_markets` - Get detailed information about markets, including base/quote assets, tick size, and other trading parameters
- `paradex_market_summaries` - Get summaries with price, volume, 24h change, and other key market metrics
- `paradex_funding_data` - Get historical funding rate data for perpetual markets
- `paradex_orderbook` - Get the current orderbook for a market with customizable depth
- `paradex_klines` - Get historical candlestick (OHLCV) data for a market
- `paradex_trades` - Get recent trades for a market with price, size, and timestamp information
- `paradex_bbo` - Get best bid and offer (tightest spread) for a market

#### Account Tools

- `paradex_account_summary` - Get account summary information
- `paradex_account_positions` - Get current account positions
- `paradex_account_fills` - Get account trade fills
- `paradex_account_funding_payments` - Get account funding payments
- `paradex_account_transactions` - Get account transaction history

#### Order Tools

- `paradex_open_orders` - Get all open orders for an account
- `paradex_create_order` - Create a new order on Paradex
- `paradex_cancel_orders` - Cancel existing orders
- `paradex_order_status` - Get the status of an order
- `paradex_orders_history` - Get historical orders for an account

#### Vault Tools

- `paradex_vaults` - Get detailed information about specific vaults or all vaults with filtering options
- `paradex_vaults_config` - Get global configuration for vaults including fees, limits, and other settings
- `paradex_vault_balance` - Get the current balance of a vault with available/locked funds information
- `paradex_vault_summary` - Get comprehensive summary of vault performance, balance, and activity
- `paradex_vault_transfers` - Get deposit and withdrawal history for a vault
- `paradex_vault_positions` - Get current trading positions for a vault with market, size, entry price details
- `paradex_vault_account_summary` - Get trading account information for a vault including margin and risk metrics

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to this project, development setup, and our coding standards.

## License

[MIT License](LICENSE)
