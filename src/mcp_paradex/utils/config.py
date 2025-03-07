"""
Configuration utilities for the MCP Paradex server.
"""
import os
from enum import Enum
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Environment(Enum):
    """Trading environment options."""
    TESTNET = "testnet"
    PROD = "prod"

class Config:
    """Configuration settings for the MCP Paradex server."""
    
    # Server configuration
    SERVER_NAME: str = os.getenv("SERVER_NAME", "Paradex Trading")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "3000"))
    
    # Paradex configuration
    ENVIRONMENT: Environment = Environment(os.getenv("PARADEX_ENVIRONMENT", "prod"))
    
    # Authentication
    L1_ADDRESS: Optional[str] = os.getenv("PARADEX_L1_ADDRESS")
    L1_PRIVATE_KEY: Optional[str] = os.getenv("PARADEX_L1_PRIVATE_KEY")

    PARADEX_ACCOUNT_ADDRESS: Optional[str] = os.getenv("PARADEX_ACCOUNT_ADDRESS")
    PARADEX_ACCOUNT_PRIVATE_KEY: Optional[str] = os.getenv("PARADEX_ACCOUNT_PRIVATE_KEY")

    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if all required configuration is set."""
        return all([
            cls.L1_ADDRESS is not None,
            cls.L1_PRIVATE_KEY is not None,
        ])

config = Config() 