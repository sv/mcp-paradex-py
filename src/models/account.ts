import { z } from 'zod';

// Based on models.AccountSummary in Python
export const AccountSummarySchema = z.object({
    account_id: z.string(), // Or number
    username: z.string().optional(), // If available
    total_balance: z.string().transform(parseFloat), // Example: "10000.50"
    available_balance: z.string().transform(parseFloat),
    margin_balance: z.string().transform(parseFloat),
    initial_margin: z.string().transform(parseFloat),
    maintenance_margin: z.string().transform(parseFloat),
    unrealized_pnl: z.string().transform(parseFloat),
    realized_pnl: z.string().transform(parseFloat),
    equity: z.string().transform(parseFloat),
    leverage: z.string().transform(parseFloat).optional(), // Current leverage if applicable
    // Add other fields from Python's AccountSummary model as needed
    // e.g., currency (USDC), account_type, etc.
    currency: z.string().default("USDC"), // Assuming default, make optional if not always present
});
export type AccountSummary = z.infer<typeof AccountSummarySchema>;

// Based on models.Position in Python
export const PositionSchema = z.object({
    market_id: z.string(), // Or symbol
    side: z.enum(['LONG', 'SHORT', 'FLAT']), // Or "BUY"/"SELL", or numerical representation
    size: z.string().transform(parseFloat),
    entry_price: z.string().transform(parseFloat),
    mark_price: z.string().transform(parseFloat),
    liquidation_price: z.string().transform(parseFloat).optional(),
    unrealized_pnl: z.string().transform(parseFloat),
    realized_pnl: z.string().transform(parseFloat).optional(), // PnL for this position if closed partially
    initial_margin: z.string().transform(parseFloat),
    maintenance_margin: z.string().transform(parseFloat),
    leverage: z.string().transform(parseFloat).optional(),
    // Add other fields like timestamp, last_updated_time etc.
    timestamp: z.number().int().optional(), // Creation or last update time
});
export type Position = z.infer<typeof PositionSchema>;
export const PositionArraySchema = z.array(PositionSchema);

// Based on models.Fill in Python
export const FillSchema = z.object({
    id: z.string(), // Fill/Trade ID
    order_id: z.string(),
    market_id: z.string(), // Or symbol
    price: z.string().transform(parseFloat),
    quantity: z.string().transform(parseFloat), // Amount/Size
    side: z.enum(['BUY', 'SELL']), // Or "BID"/"ASK" etc.
    liquidity: z.enum(['MAKER', 'TAKER']).optional(), // Liquidity indicator
    fee: z.string().transform(parseFloat),
    fee_currency: z.string(),
    timestamp: z.number().int(), // Unix timestamp (ms)
    // Add role (maker/taker), trade_type etc. if available
});
export type Fill = z.infer<typeof FillSchema>;
export const FillArraySchema = z.array(FillSchema);

// Based on models.Transaction in Python
export const TransactionSchema = z.object({
    id: z.string(),
    type: z.string(), // e.g., "DEPOSIT", "WITHDRAWAL", "TRADE_FEE", "FUNDING_PAYMENT", "REALIZED_PNL"
    amount: z.string().transform(parseFloat),
    currency: z.string(),
    status: z.string().optional(), // e.g., "COMPLETED", "PENDING", "FAILED"
    timestamp: z.number().int(), // Unix timestamp (ms)
    details: z.record(z.any()).optional(), // For any other specific details, like trade_id, funding_market_id
    // address_from: z.string().optional(), // For deposits/withdrawals
    // address_to: z.string().optional(),   // For deposits/withdrawals
    // transaction_hash: z.string().optional(), // Blockchain transaction hash if applicable
});
export type Transaction = z.infer<typeof TransactionSchema>;
export const TransactionArraySchema = z.array(TransactionSchema);


// Models for Vaults (from Python's mcp_paradex/models.py, assuming structure)
// These were not explicitly requested to be read but are part of the overall structure.

export const VaultSchema = z.object({
  id: z.string(),
  asset: z.string(), // e.g., "USDC"
  total_balance: z.string().transform(parseFloat),
  available_balance: z.string().transform(parseFloat),
  // other vault specific fields
  apy: z.string().transform(parseFloat).optional(),
  strategy: z.string().optional(),
});
export type Vault = z.infer<typeof VaultSchema>;
export const VaultArraySchema = z.array(VaultSchema);

export const VaultSummarySchema = z.object({
  total_value_locked_usd: z.string().transform(parseFloat),
  number_of_vaults: z.number().int(),
  // other summary fields
});
export type VaultSummary = z.infer<typeof VaultSummarySchema>;


// Model for Order (from Python's mcp_paradex/models.py, assuming structure)
export const OrderStateSchema = z.object({
    id: z.string(), // Order ID
    client_order_id: z.string().optional(),
    market_id: z.string(),
    side: z.enum(["BUY", "SELL"]),
    type: z.enum(["LIMIT", "MARKET", "STOP_LOSS", "TAKE_PROFIT"]), // etc.
    status: z.enum(["OPEN", "CLOSED", "CANCELED", "FILLED", "PARTIALLY_FILLED", "EXPIRED"]),
    price: z.string().transform(parseFloat).optional(), // Optional for market orders
    quantity: z.string().transform(parseFloat), // Original quantity
    filled_quantity: z.string().transform(parseFloat),
    remaining_quantity: z.string().transform(parseFloat),
    average_fill_price: z.string().transform(parseFloat).optional(),
    created_at: z.number().int(), // timestamp
    updated_at: z.number().int().optional(), // timestamp
    // time_in_force: z.enum(["GTC", "IOC", "FOK"]).optional(),
    // post_only: z.boolean().optional(),
    // reduce_only: z.boolean().optional(),
});
export type OrderState = z.infer<typeof OrderStateSchema>;
export const OrderStateArraySchema = z.array(OrderStateSchema);


console.log("src/models/account.ts loaded");

// As with market.ts, the actual field names, types (string vs number from API),
// and enum values need to be verified against the @paradex/sdk responses.
// parseFloat transformations assume string numbers from API.
// Optional fields are marked with .optional().
