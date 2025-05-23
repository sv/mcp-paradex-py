"""
Trading prompts module initialization.
"""

# Import all prompts to ensure they're registered
from mcp_paradex.prompts.trader_prompts import (
    create_optimal_order,
    funding_rate_opportunity,
    hedging_strategy,
    liquidation_protection,
    market_analysis,
    market_overview,
    portfolio_risk_assessment,
    position_management,
    trading_consultation,
    vault_analysis,
)

# Export all prompts for convenient importing
__all__ = [
    "create_optimal_order",
    "funding_rate_opportunity",
    "hedging_strategy",
    "liquidation_protection",
    "market_analysis",
    "market_overview",
    "portfolio_risk_assessment",
    "position_management",
    "trading_consultation",
    "vault_analysis",
]
