"""
Trading analysis prompts for Paradex.
"""

from mcp.server.fastmcp.prompts import base

from mcp_paradex.server.server import server


@server.prompt()
def market_overview(volume_threshold: float = 1000000, price_change_threshold: float = 5.0) -> str:
    """Get comprehensive overview of the crypto market on Paradex"""
    return f"""Provide a comprehensive analysis of Paradex markets using the following approach:
      1. Check system_state to confirm normal operations
      2. Retrieve market_summaries for all markets, focusing on:
         - Top 5 gainers and losers (24h price change)
         - Top 5 by trading volume
         - Markets with significant funding rate divergence (>0.1% from average)
      3. For high-volume markets (top 10), analyze:
         - Order book depth and imbalances
         - Recent trade flow and size distribution
         - Current vs historical volatility
      4. Identify correlated asset groups and any divergences
      5. Highlight markets with unusual liquidity or spread conditions
      Parameters: volume_threshold={volume_threshold} USD, price_change_threshold={price_change_threshold}%
    """


@server.prompt()
def market_analysis(
    market_id: str, timeframe: str = "1h", risk_percent: float = 1.0, account_balance: float = None
) -> str:
    """Detailed analysis of a specific market for informed trading decisions"""
    account_str = f", account_balance={account_balance}" if account_balance else ""
    return f"""Analyze {market_id} market with the following structured approach:
      1. Price Analysis:
         - Retrieve klines data for {timeframe} timeframe
         - Identify key support/resistance levels using recent price action
         - Calculate and interpret key technical indicators: RSI, MACD, Bollinger Bands
         - Identify chart patterns and trend direction
      2. Market Microstructure:
         - Analyze orderbook for liquidity distribution and potential walls
         - Examine recent trades for large orders or patterns (accumulation/distribution)
         - Calculate bid-ask spread and depth compared to historical average
      3. Market Context:
         - Review funding rate history and current rate vs other markets
         - Compare volume profile to historical patterns
         - Analyze price correlation with market leaders (BTC, ETH)
      4. Position Recommendation:
         - Suggest entry zones with specific price levels
         - Calculate position size based on {risk_percent}% of account{account_str}
         - Provide stop loss placement based on market volatility
         - Identify multiple take profit targets with risk:reward ratios
         - Recommend order types based on current market conditions
    """


@server.prompt()
def position_management(
    target_risk: float = 5.0, max_correlation: float = 0.7, profit_taking_strategy: str = "scaled"
) -> str:
    """Comprehensive analysis and management of existing positions"""
    return f"""Analyze and optimize my current trading positions using these steps:
      1. Portfolio Overview:
         - Retrieve account_positions data and calculate total exposure
         - Analyze cross-position correlation and directional bias
         - Calculate portfolio heat (percentage of account at risk)
         - Determine aggregate leverage and distance to account liquidation
      2. Individual Position Analysis:
         - For each position, calculate:
           * Unrealized PnL (absolute and % of entry)
           * Distance to liquidation price (as % from current price)
           * Funding payment impact (24h projection based on current rates)
           * Position duration and aging analysis
           * Current market momentum relative to position direction
      3. Position Optimization:
         - For profitable positions:
           * Recommend scale-out levels based on technical resistance/support
           * Calculate optimal profit-taking percentages at each level
           * Suggest trailing stop strategies based on market volatility
         - For underwater positions:
           * Evaluate continuation vs exit based on market structure
           * Calculate optimal DCA levels if appropriate
           * Provide specific exit points to minimize losses if trend confirmed against position
      4. Risk Adjustment:
         - Recommend overall portfolio adjustments to maintain {target_risk}% target risk
         - Identify position size imbalances relative to current market conditions
         - Suggest hedge positions if directional exposure exceeds {max_correlation} correlation threshold
         - Apply '{profit_taking_strategy}' profit-taking strategy to profitable positions
    """


@server.prompt()
def create_optimal_order(
    market_id: str,
    side: str,
    risk_percent: float = 1.0,
    urgency: str = "normal",
    order_type: str = "",
) -> str:
    """Generate optimized order parameters based on market conditions and risk management"""
    order_type_str = f", order_type={order_type}" if order_type else ""
    return f"""Design an optimal order for {market_id} with these steps:
      1. Market Parameters Analysis:
         - Retrieve market configuration (tick size, min/max size, price precision)
         - Calculate current market volatility (1h, 24h) to inform order parameters
         - Analyze order book depth to estimate potential slippage
         - Check for existing positions in this market
      2. Order Type Determination:
         - Based on '{urgency}' urgency level, recommend market vs. limit order
         - For limit orders, calculate optimal limit price based on:
           * Current bid-ask spread
           * Recent trade execution prices
           * Order book imbalance
           * Historical fill probability at different price levels
         - For conditional orders, determine appropriate trigger prices
      3. Position Sizing:
         - Calculate position size based on:
           * Account balance and {risk_percent}% risk
           * Current market volatility
           * Distance to stop loss
           * Existing exposure to same/correlated assets
         - Adjust for market's minimum and maximum order size constraints
      4. Risk Parameter Configuration:
         - Determine if reduce_only flag should be enabled
         - Set appropriate time-in-force instruction (GTC, IOC, POST_ONLY)
         - For larger orders, evaluate splitting into multiple smaller orders
      5. Order Chain Creation:
         - Generate accompanying stop loss order parameters
         - Calculate take profit level(s) with optimal risk:reward ratio
         - Format all parameters to match Paradex API requirements
      Parameters: side={side}{order_type_str}
    """


@server.prompt()
def hedging_strategy(
    market_id: str,
    position_id: str = None,
    hedge_purpose: str = "full",
    hedge_duration: str = "medium-term",
    hedge_percentage: float = 100.0,
) -> str:
    """Design comprehensive hedging strategy for existing positions"""
    position_str = f", position_id={position_id}" if position_id else ""
    return f"""Develop an effective hedging strategy for my {market_id} position with these steps:
      1. Position Analysis:
         - Retrieve position details (size, direction, entry price, current PnL)
         - Calculate current market value and delta exposure
         - Determine hedging objective: '{hedge_purpose}' (full neutralization, downside protection, volatility reduction)
         - Establish hedge timeframe: '{hedge_duration}' (short-term, medium-term, long-term)
      2. Hedge Instrument Selection:
         - Identify potential hedging instruments on Paradex by:
           * Direct inverse position in same market
           * Correlated/inverse-correlated assets (calculate 30-day correlation coefficients)
           * Sector-related instruments
         - For each potential hedge, analyze:
           * Liquidity and execution costs
           * Funding rate differential compared to original position
           * Historical correlation stability (correlation volatility)
      3. Hedge Ratio Calculation:
         - For each viable hedging instrument, calculate:
           * Optimal hedge ratio based on beta coefficient
           * Required position size to achieve {hedge_percentage}% hedge percentage
           * Expected hedge effectiveness (%)
           * Total execution cost and ongoing carrying cost
      4. Hedge Implementation Strategy:
         - Design order execution plan:
           * Optimal order types and parameters
           * Entry staging if size is significant
           * Specific price levels based on technical analysis
         - Create companion risk management orders:
           * Stop loss if correlation breaks down
           * Take profit if hedge exceeds needed protection
      5. Hedge Monitoring Framework:
         - Define specific conditions to:
           * Adjust hedge ratio (correlation shifts, volatility changes)
           * Exit hedge (original position closed, market regime change)
           * Roll hedge to different instrument
      Parameters:{position_str}
    """


@server.prompt()
def vault_analysis(
    investment_objective: str = "balanced",
    risk_tolerance: str = "medium",
    time_horizon: str = "medium",
) -> str:
    """Comprehensive analysis of vaults for investment decision-making"""
    return f"""Analyze Paradex vaults using these steps to identify optimal investment opportunities:
      1. Performance Analysis:
         - For all accessible vaults, calculate and compare:
           * Absolute ROI across multiple timeframes (24h, 7d, 30d, inception)
           * Risk-adjusted metrics (Sharpe ratio, Sortino ratio, maximum drawdown)
           * Performance consistency (standard deviation of returns)
           * Performance vs. market benchmarks (BTC, ETH, market index)
      2. Risk Profile Assessment:
         - For each vault, analyze:
           * Trading strategy classification (trend-following, mean-reversion, etc.)
           * Market exposure and concentration
           * Leverage utilization patterns
           * Drawdown history and recovery periods
           * Correlation to major crypto assets
      3. Manager Evaluation:
         - Research vault managers/strategies:
           * Track record length and consistency
           * TVL growth trends
           * Fee structure analysis and impact on returns
           * Trading frequency and activity patterns
      4. Investment Suitability:
         - Match vaults to '{investment_objective}' investment objective:
           * For capital preservation: prioritize low volatility, consistent returns
           * For growth: identify higher risk-adjusted returns with acceptable volatility
           * For diversification: find vaults with low correlation to existing holdings
      5. Liquidity Analysis:
         - Evaluate deposit/withdrawal mechanics:
           * Entry/exit constraints
           * Historical liquidity during market stress
           * Lock-up periods or withdrawal limitations
      6. Recommendation Framework:
         - Generate tiered recommendations:
           * Top 3 vaults matching investment criteria with detailed rationale
           * Vaults to avoid with specific red flags
           * Existing investments that should be reevaluated
      Parameters: risk_tolerance='{risk_tolerance}', time_horizon='{time_horizon}'
    """


@server.prompt()
def portfolio_risk_assessment(
    max_concentration: float = 20.0, target_var: float = 5.0, stress_scenario: str = "medium"
) -> str:
    """Comprehensive risk analysis of trading portfolio with optimization recommendations"""
    return f"""Conduct a thorough risk assessment of my trading portfolio with these steps:
      1. Exposure Analysis:
         - Map total exposure by:
           * Asset (individual cryptocurrencies)
           * Market segment (L1, L2, DeFi, etc.)
           * Market capitalization tiers
           * Long vs. short positioning
         - Identify concentration risks exceeding {max_concentration}% of portfolio
      2. Correlation Assessment:
         - Calculate correlation matrix across all positions
         - Identify highly correlated clusters (>0.7) that amplify risk
         - Determine portfolio beta to major assets (BTC, ETH)
         - Calculate effective diversification ratio
      3. Volatility & Drawdown Metrics:
         - Calculate key risk metrics:
           * Historical and implied volatility by position
           * Value at Risk (VaR) at multiple confidence levels (95%, 99%)
           * Expected Shortfall/Conditional VaR
           * Maximum portfolio drawdown potential
           * Stress test against historical crypto crash scenarios (e.g., May 2021, Nov 2022)
      4. Leverage & Liquidation Analysis:
         - Evaluate account-wide and position-level leverage
         - Calculate cascading liquidation scenarios
         - Identify liquidation clustering risks
         - Determine portfolio breakdown points under various market moves
      5. Temporal Risk Distribution:
         - Analyze risk exposure across time horizons:
           * Immediate (24h) risk from highly volatile positions
           * Medium-term (7-30d) risk from market trends
           * Long-term (30d+) structural risks
      6. Risk Optimization Recommendations:
         - Generate specific risk reduction strategies:
           * Position adjustments with maximum risk reduction per unit of return sacrificed
           * Hedging opportunities with optimal cost/benefit
           * Diversification additions to reduce correlation clusters
           * Leverage optimization to maintain return profile with reduced tail risk
         - Provide implementation plan with priority order
      Parameters: target_var={target_var}% daily 95% VaR, stress_scenario='{stress_scenario}'
    """


@server.prompt()
def funding_rate_opportunity(
    timeframe: str = "7d",
    min_annual_yield: float = 15.0,
    risk_percent: float = 2.0,
    strategy_preference: str = "balanced",
) -> str:
    """Identify and evaluate funding rate arbitrage opportunities"""
    return f"""Analyze funding rate opportunities across Paradex markets with these steps:
      1. Funding Rate Comparison:
         - Retrieve current and historical funding rates for all markets
         - Rank markets by:
           * Current funding rate (absolute value)
           * Funding rate vs. historical average (z-score)
           * Funding rate stability (standard deviation)
           * Predicted funding income over {timeframe}
         - Calculate annualized yield equivalent for each market
      2. Opportunity Qualification:
         - For top funding rate opportunities, analyze:
           * Market liquidity and ease of entry/exit
           * Funding rate history and mean-reversion patterns
           * Historical duration of extreme funding conditions
           * Correlation between funding rate and price movement
         - Filter for opportunities meeting {min_annual_yield}% minimum annual yield threshold
      3. Risk Assessment:
         - For each qualified opportunity, evaluate:
           * Price volatility vs. funding income
           * Maximum adverse excursion calculation
           * Liquidation risk assessment
           * Opportunity cost vs. other strategies
      4. Implementation Strategies:
         - Design position structures:
           * Pure funding capture (directional exposure)
           * Delta-neutral pairs (long/short correlated assets with opposite funding)
           * Cross-exchange arbitrage if applicable
           * Hedged positions with options/futures
         - For each strategy, calculate:
           * Expected return profile
           * Risk-adjusted metrics (Sharpe, Sortino)
           * Required capital and margin efficiency
      5. Execution Framework:
         - Generate specific trade parameters:
           * Optimal position sizing based on account size and {risk_percent}% risk
           * Entry methodology (limit vs. market, staged entry)
           * Recommended hold period
           * Exit triggers (funding normalization, price movement thresholds)
      Parameters: strategy_preference='{strategy_preference}'
    """


@server.prompt()
def liquidation_protection(
    safety_threshold_hours: int = 48,
    max_liquidation_probability: float = 5.0,
    risk_tolerance: str = "moderate",
) -> str:
    """Identify and mitigate liquidation risks for open positions"""
    return f"""Protect against position liquidations with these comprehensive steps:
      1. Liquidation Risk Assessment:
         - Scan all open positions to calculate:
           * Current distance to liquidation (percentage)
           * Estimated Time To Liquidation (TTL) based on:
             - Historical volatility (1h, 4h, 24h)
             - Recent price action and momentum
             - Market-specific volatility characteristics
           * Liquidation probability within various timeframes (24h, 7d)
         - Identify positions with TTL < {safety_threshold_hours} hours or probability > {max_liquidation_probability}%
      2. Risk Severity Classification:
         - Categorize at-risk positions:
           * Critical: Imminent liquidation risk (<24h TTL)
           * High: Near-term risk (24-72h TTL)
           * Moderate: Potential risk under increased volatility
           * Low: Well-collateralized positions
      3. Protection Strategy Selection:
         - For each at-risk position, analyze optimal protection methods:
           * Position Size Reduction:
             - Calculate exact reduction percentage needed to reach safety threshold
             - Determine optimal execution method (market/limit) based on urgency
           * Collateral Addition:
             - Calculate precise additional margin required
             - Identify optimal funding sources with minimal opportunity cost
           * Hedge Implementation:
             - Design correlated asset positions to offset risk
             - Calculate optimal hedge ratio and execution parameters
           * Stop-Loss Placement:
             - Determine ideal stop placement balancing protection vs. avoiding premature execution
             - Calculate optimal order types (market/limit stops)
      4. Cost-Benefit Analysis:
         - For each protection strategy, calculate:
           * Implementation cost (fees, slippage, spreads)
           * Opportunity cost (locked capital, potential upside limitation)
           * Risk reduction effectiveness (% reduction in liquidation probability)
           * Risk-adjusted cost metric (cost per unit of risk reduction)
      5. Implementation Plan:
         - Generate prioritized action list ordered by:
           * Risk severity
           * Cost-efficiency of protection
           * Execution urgency
         - Provide specific execution parameters for each action:
           * Exact order sizes, prices, and types
           * Precise collateral amounts
           * Step-by-step implementation instructions
         - Design contingency plans for rapid market movements
      Parameters: risk_tolerance='{risk_tolerance}'
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
