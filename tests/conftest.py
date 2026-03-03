"""
Pytest configuration for mcp-paradex tests.
"""

import os

# Set a fake private key before any server module is imported so that
# config.is_configured() returns True and auth-required tools get registered
# on the FastMCP server.  Actual network calls are mocked in each test.
os.environ.setdefault("PARADEX_ACCOUNT_PRIVATE_KEY", "0xtest")
