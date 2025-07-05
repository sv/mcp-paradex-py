[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/sv-mcp-paradex-py-badge.png)](https://mseep.ai/app/sv-mcp-paradex-py)

# MCP Paradex Server

[![smithery badge](https://smithery.ai/badge/@sv/mcp-paradex-py)](https://smithery.ai/server/@sv/mcp-paradex-py)

Model Context Protocol (MCP) server implementation for the Paradex trading platform.

<a href="https://glama.ai/mcp/servers/cq4bz5ljqj">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/cq4bz5ljqj/badge" alt="Paradex Server MCP server" />
</a>

## Overview

This project provides a bridge between AI assistants (like Claude) and the
Paradex perpetual futures trading platform. Using the MCP standard,
AI assistants can:

- Retrieve market data from Paradex
- Manage trading accounts and vaults
- Place and manage orders
- Monitor positions and balance

## Prerequisites

- Python 3.10+

## Installation

### Quick Start

#### Cursor IDE

Click to automatically configure this MCP server in Cursor:

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=paradex&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJtY3AtcGFyYWRleCJdLCJlbnYiOnsiUEFSQURFWF9FTlZJUk9OTUVOVCI6InRlc3RuZXQiLCJQQVJBREVYX0FDQ09VTlRfUFJJVkFURV9LRVkiOiJ5b3VyX3ByaXZhdGVfa2V5In19Cg%3D%3D)

#### Claude Code CLI

```bash
claude mcp add paradex uvx mcp-paradex
```

#### Smithery (Claude Desktop)

```bash
npx -y @smithery/cli install @sv/mcp-paradex-py --client claude
```

### Standard Installation

#### PyPI

```bash
pip install mcp-paradex
```

#### uvx (Recommended)

```bash
uvx mcp-paradex
```

### Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/sv/mcp-paradex-py.git
   cd mcp-paradex-py
   ```

2. Install development dependencies:

   ```bash
   uv sync --dev --all-extras
   ```

3. Run locally:

   ```bash
   uv run mcp-paradex
   ```

## Configuration

### Environment Variables

Set these environment variables for authentication:

- `PARADEX_ENVIRONMENT`: Set to `testnet` or `mainnet`
- `PARADEX_ACCOUNT_PRIVATE_KEY`: Your Paradex account private key

### Using .env File

```bash
cp .env.template .env
# Edit .env with your credentials
```

### Client Configuration

#### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paradex": {
      "command": "uvx",
      "args": ["mcp-paradex"],
      "env": {
        "PARADEX_ENVIRONMENT": "testnet",
        "PARADEX_ACCOUNT_PRIVATE_KEY": "your_private_key"
      }
    }
  }
}
```

#### Docker

```bash
# Build image
docker build . -t sv/mcp-paradex-py

# Run (public only)
docker run --rm -i sv/mcp-paradex-py

# Run with trading capabilities
docker run --rm -e PARADEX_ACCOUNT_PRIVATE_KEY=your_key -i sv/mcp-paradex-py
```

## Available Resources and Tools

### Resources

#### System Resources

- `paradex://system/config` - Get Paradex system configuration
- `paradex://system/time` - Get current system time
- `paradex://system/state` - Get system operational state

#### Market Resources

- `paradex://markets` - List of available markets
- `paradex://market/summary/{market_id}` - Detailed market information

#### Vault Resources

- `paradex://vaults` - List all vaults
- `paradex://vaults/config` - Global vault configuration
- `paradex://vaults/balance/{vault_id}` - Vault balance
- `paradex://vaults/summary/{vault_id}` - Comprehensive vault summary
- `paradex://vaults/transfers/{vault_id}` - Deposit/withdrawal history
- `paradex://vaults/positions/{vault_id}` - Current trading positions
- `paradex://vaults/account-summary/{vault_id}` - Trading account information

### Tools

#### System Tools

- `paradex_system_config` - Get global system configuration
- `paradex_system_state` - Get current system state

#### Market Tools

- `paradex_markets` - Get detailed market information
- `paradex_market_summaries` - Get market summaries with metrics
- `paradex_funding_data` - Get historical funding rate data
- `paradex_orderbook` - Get current orderbook with customizable depth
- `paradex_klines` - Get historical candlestick data
- `paradex_trades` - Get recent trades
- `paradex_bbo` - Get best bid and offer

#### Account Tools

- `paradex_account_summary` - Get account summary
- `paradex_account_positions` - Get current positions
- `paradex_account_fills` - Get trade fills
- `paradex_account_funding_payments` - Get funding payments
- `paradex_account_transactions` - Get transaction history

#### Order Tools

- `paradex_open_orders` - Get all open orders
- `paradex_create_order` - Create new order
- `paradex_cancel_orders` - Cancel existing orders
- `paradex_order_status` - Get order status
- `paradex_orders_history` - Get historical orders

#### Vault Tools

- `paradex_vaults` - Get detailed vault information
- `paradex_vaults_config` - Get global vault configuration
- `paradex_vault_balance` - Get vault balance
- `paradex_vault_summary` - Get comprehensive vault summary
- `paradex_vault_transfers` - Get deposit/withdrawal history
- `paradex_vault_positions` - Get current vault positions
- `paradex_vault_account_summary` - Get vault trading account info

## Trading Analysis Prompts

### Market Analysis

- `market_overview` - Comprehensive crypto market overview
- `market_analysis` - Detailed technical and microstructure analysis

### Position and Portfolio Management

- `position_management` - Comprehensive position analysis
- `create_optimal_order` - Design optimal order parameters
- `hedging_strategy` - Develop effective hedging strategies
- `portfolio_risk_assessment` - Thorough portfolio risk analysis
- `liquidation_protection` - Identify and mitigate liquidation risks

### Investment Strategies

- `vault_analysis` - Comprehensive vault analysis for investment decisions
- `funding_rate_opportunity` - Identify funding rate arbitrage opportunities
- `trading_consultation` - Interactive trading advice and consultation

## Documentation MCP

Enhanced results with Paradex documentation access:

```json
"paradex-docs-mcp": {
   "command": "uvx",
   "args": [
      "--from",
      "mcpdoc",
      "mcpdoc",
      "--urls",
      "Paradex:https://docs.paradex.trade/llms.txt",
      "--transport",
      "stdio"
   ]
}
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to
contribute to this project, development setup, and our coding standards.

## License

[MIT License](LICENSE)
