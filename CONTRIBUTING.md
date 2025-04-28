# Contributing to MCP Paradex Server

Thank you for your interest in contributing to the MCP Paradex Server project!

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

Generate models.py

Convert paradex swagger to openapi using https://converter.swagger.io/#/Converter/convertByUrl

```
https://api.prod.paradex.trade/swagger/doc.json
```

```bash
pip install datamodel-code-generator
datamodel-codegen  --input prompts/paradex-openapi.json --use-annotated --use-default-kwarg --keep-model-order --output src/mcp_paradex/models/
```

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure your code follows the existing style and passes all tests and linters before submitting a PR.

## Evals

[MCP Testing Framework](https://github.com/L-Qun/mcp-testing-framework)
