"""
Trading prompts module initialization.
"""

# Always available prompts
from mcp_paradex.prompts.trader_prompts import (
    funding_rate_opportunity,
    getting_started,
    market_analysis,
    market_overview,
    trading_consultation,
    vault_analysis,
)
from mcp_paradex.utils.config import config

# Only register auth-required prompts when authenticated
if config.is_configured():
    from mcp_paradex.prompts.trader_prompts import (
        create_optimal_order,
        hedging_strategy,
        liquidation_protection,
        portfolio_risk_assessment,
        position_management,
    )

# Export all prompts for convenient importing
__all__ = [
    "funding_rate_opportunity",
    "getting_started",
    "market_analysis",
    "market_overview",
    "trading_consultation",
    "vault_analysis",
]

if config.is_configured():
    __all__ += [
        "create_optimal_order",
        "hedging_strategy",
        "liquidation_protection",
        "portfolio_risk_assessment",
        "position_management",
    ]
