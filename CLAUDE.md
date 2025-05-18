# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP Paradex Server is a Model Context Protocol (MCP) server implementation for the Paradex perpetual futures trading platform. It provides a bridge between AI assistants (like Claude) and the Paradex platform, allowing the assistants to retrieve market data, manage trading accounts and vaults, place and manage orders, and monitor positions and balances.

## Commands

### Environment Setup

```bash
# Create and activate a virtual environment with uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Install development dependencies
make install-dev
# OR
pip install -e ".[dev]"
pre-commit install
```

### Development Commands

```bash
# Format code with black
make format
# OR
black src tests

# Lint code with ruff
make lint
# OR
ruff check src tests --fix

# Type check with mypy
make typecheck
# OR
mypy src

# Run tests
make test
# OR
pytest

# Run tests with coverage report
make test-cov
# OR
pytest --cov=mcp_paradex --cov-report=html

# Run all checks (format, lint, typecheck, test)
make check

# Run pre-commit hooks on all files
make pre-commit
# OR
pre-commit run --all-files

# Clean up cache files
make clean
```

### Running the Server

```bash
# Run the server using the CLI
python -m mcp_paradex

# Build and run with Docker
docker build . -t sv/mcp-paradex-py
docker run --rm -i sv/mcp-paradex-py  # Public only
docker run --rm -e PARADEX_ACCOUNT_PRIVATE_KEY=0xprivatekey -i sv/mcp-paradex-py  # Allow trading
```

## Architecture

The MCP Paradex Server is structured as follows:

- **Server**: The core server component using FastMCP to handle MCP protocol requests
- **Resources**: Read-only data endpoints structured as URIs
  - System resources: Configuration, time, state
  - Market resources: Lists of markets, market summaries
  - Vault resources: Lists of vaults, vault configurations, balances
- **Tools**: Action-based tools exposed to AI assistants
  - System tools: Configuration, state management
  - Market tools: Market data, order books, trades, etc.
  - Account tools: Balance, positions, transaction history
  - Order tools: Create/cancel orders, monitor order status
  - Vault tools: Balance, transfers, positions
- **Prompts**: Structured prompts for trading analysis and strategy generation
  - Market analysis and trading recommendations
  - Position and portfolio management
  - Investment strategies

The server uses the Paradex Python API client to connect to the Paradex exchange and execute operations. Authentication is handled via a singleton client instance that loads credentials from environment variables.

## Important Files

- **src/mcp_paradex/server/server.py**: Main server implementation
- **src/mcp_paradex/utils/config.py**: Configuration handling
- **src/mcp_paradex/utils/paradex_client.py**: Paradex API client wrapper
- **src/mcp_paradex/resources/**: Resource implementations
- **src/mcp_paradex/tools/**: Tool implementations
- **src/mcp_paradex/prompts/**: Trading prompt templates

## Development Guidelines

1. All code should follow the project's formatting (Black), linting (Ruff), and type checking (Mypy) standards.
2. Pre-commit hooks are set up to run automatically on git commits.
3. New features should include appropriate tests.
4. Always run the type checker before committing changes.
5. The codebase uses Python 3.10+ features, make sure your code is compatible.
