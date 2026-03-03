"""
Trading analysis prompts for Paradex.
"""

from mcp.server.fastmcp.prompts import base

from mcp_paradex.server.server import server
from mcp_paradex.utils.config import config


@server.prompt()
def getting_started() -> str:
    """Welcome prompt showing auth status and available capabilities"""
    auth_status = "✓ Authenticated" if config.is_configured() else "✗ Not authenticated (read-only)"
    public_note = (
        ""
        if config.is_configured()
        else "\nTo enable trading tools, set PARADEX_ACCOUNT_PRIVATE_KEY."
    )
    auth_prompts = (
        "- Account & trading: position_management, create_optimal_order, hedging_strategy, portfolio_risk_assessment, liquidation_protection"
        if config.is_configured()
        else ""
    )
    return f"""Welcome to the Paradex MCP server ({auth_status}).{public_note}

Available capabilities:
- Market data: market_overview, market_analysis, vault_analysis, funding_rate_opportunity
{auth_prompts}
Start with market_overview for a snapshot, or pick a specific prompt.
"""


@server.prompt()
def market_overview(volume_threshold: float = 1000000, price_change_threshold: float = 5.0) -> str:
    """Get a brief overview of the crypto market on Paradex"""
    return f"""Fetch market summaries. List top 5 gainers/losers, top 5 by volume, and any markets with unusual funding rates (>{price_change_threshold}% price change or >{volume_threshold} USD volume). Be brief.
"""


@server.prompt()
def market_analysis(
    market_id: str, timeframe: str = "1h", risk_percent: float = 1.0, account_balance: float = None
) -> str:
    """Concise analysis of a specific market with a position recommendation"""
    account_str = f", account_balance={account_balance}" if account_balance else ""
    return f"""Analyze {market_id} ({timeframe}). Cover: trend direction, key support/resistance, funding rate, order book imbalance, and a position recommendation with entry/SL/TP for {risk_percent}% risk{account_str}. Be concise.
"""


@server.prompt()
def position_management(
    target_risk: float = 5.0, max_correlation: float = 0.7, profit_taking_strategy: str = "scaled"
) -> str:
    """Review open positions and recommend actions"""
    return f"""Review all open positions. For each: show PnL%, distance to liquidation, funding impact. Recommend hold/reduce/exit based on '{profit_taking_strategy}' strategy. Total portfolio risk vs {target_risk}% target.
"""


@server.prompt()
def create_optimal_order(
    market_id: str,
    side: str,
    risk_percent: float = 1.0,
    urgency: str = "normal",
    order_type: str = "",
) -> str:
    """Generate optimized order parameters for a trade"""
    order_type_str = f", order_type={order_type}" if order_type else ""
    return f"""Design an order for {market_id} {side}. Pick order type for '{urgency}' urgency. Size for {risk_percent}% risk. Include stop loss and take profit. Output ready-to-use parameters.{order_type_str}
"""


@server.prompt()
def hedging_strategy(
    market_id: str,
    position_id: str = None,
    hedge_purpose: str = "full",
    hedge_duration: str = "medium-term",
    hedge_percentage: float = 100.0,
) -> str:
    """Design a hedge for an existing position"""
    position_str = f", position_id={position_id}" if position_id else ""
    return f"""Design a {hedge_percentage}% '{hedge_purpose}' hedge for {market_id} ({hedge_duration}). Pick best instrument, calculate ratio, provide execution params. Keep it actionable.{position_str}
"""


@server.prompt()
def vault_analysis(
    investment_objective: str = "balanced",
    risk_tolerance: str = "medium",
    time_horizon: str = "medium",
) -> str:
    """Compare vaults and recommend top picks"""
    return f"""Compare all vaults. Rank by risk-adjusted returns. Match to '{investment_objective}' objective and '{risk_tolerance}' risk tolerance (time_horizon={time_horizon}). Give top 3 picks with brief rationale.
"""


@server.prompt()
def portfolio_risk_assessment(
    max_concentration: float = 20.0, target_var: float = 5.0, stress_scenario: str = "medium"
) -> str:
    """Assess portfolio risk and flag top issues"""
    return f"""Assess portfolio risk. Flag concentration >{max_concentration}%, high correlations, liquidation risks (stress_scenario='{stress_scenario}', target_var={target_var}%). Give top 3 priority actions.
"""


@server.prompt()
def funding_rate_opportunity(
    timeframe: str = "7d",
    min_annual_yield: float = 15.0,
    risk_percent: float = 2.0,
    strategy_preference: str = "balanced",
) -> str:
    """Find funding rate opportunities above a yield threshold"""
    return f"""Find funding rate opportunities >{min_annual_yield}% annual yield ({timeframe} lookback). Rank by yield vs risk. Show position structure (directional or delta-neutral) and sizing for {risk_percent}% risk. Strategy preference: '{strategy_preference}'.
"""


@server.prompt()
def liquidation_protection(
    safety_threshold_hours: int = 48,
    max_liquidation_probability: float = 5.0,
    risk_tolerance: str = "moderate",
) -> str:
    """Check positions for liquidation risk and provide protective actions"""
    return f"""Check all positions for liquidation risk (risk_tolerance='{risk_tolerance}'). Flag critical (<24h) and high (24-72h TTL or >{max_liquidation_probability}% probability within {safety_threshold_hours}h) risk positions. Give specific protective actions with sizes/prices.
"""


# For more complex prompt interactions that require a sequence of messages, we can use the list[base.Message] format:
@server.prompt()
def trading_consultation() -> list[base.Message]:
    """Interactive trading consultation prompt sequence"""
    return [
        base.SystemMessage(
            "You are an expert cryptocurrency trading advisor specialized in Paradex perpetual markets."
        ),
        base.UserMessage("I want help with my trading on Paradex."),
        base.AssistantMessage(
            """I'd be happy to help with your Paradex trading. To provide the most relevant advice, I'll need to understand more about:

1. Your trading objectives (income, growth, hedging)
2. Your risk tolerance (conservative, moderate, aggressive)
3. Your preferred trading timeframes
4. Any specific markets you're interested in

I can help with market analysis, position management, risk assessment, or specific trading strategies. What area would you like to focus on first?"""
        ),
    ]
