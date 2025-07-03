import { z } from 'zod';

// Based on models.MarketDetails in Python
export const MarketDetailsSchema = z.object({
    symbol: z.string(),
    base_asset: z.string(),
    quote_asset: z.string(),
    tick_size: z.string().transform(parseFloat), // Assuming string from API, convert to number
    min_order_size: z.string().transform(parseFloat),
    max_order_size: z.string().transform(parseFloat),
    lot_size: z.string().transform(parseFloat),
    contract_type: z.string(), // e.g., "PERP", "PERP_OPTION"
    asset_kind: z.string(), // e.g., "PERP", "PERP_OPTION" (might be same as contract_type or more specific)
    // Add other fields from Python's MarketDetails model as needed
    // e.g., created_at, updated_at, status, etc.
    // For now, keeping it aligned with what's explicitly used or mentioned.
    is_active: z.boolean().optional(), // Assuming this might exist
    underlying_asset: z.string().optional(), // For derivatives like options/futures
});
export type MarketDetails = z.infer<typeof MarketDetailsSchema>;
export const MarketDetailsArraySchema = z.array(MarketDetailsSchema);

// Based on models.MarketSummary in Python
export const MarketSummarySchema = z.object({
    symbol: z.string(),
    mark_price: z.string().transform(parseFloat),
    last_price: z.string().transform(parseFloat),
    open_interest: z.string().transform(parseFloat),
    high_price_24h: z.string().transform(parseFloat), // Python had high_price
    low_price_24h: z.string().transform(parseFloat),  // Python had low_price
    volume_24h: z.string().transform(parseFloat),     // Python had volume
    price_change_percent_24h: z.string().transform(parseFloat), // Python had price_change_percent
    // Paradex API might return these as strings, so parsing them
    // Ensure the field names match the JS SDK or direct API response
    // The Python model was: symbol, mark_price, last_price, open_interest, high_price, low_price, volume, price_change_percent
    // Adjusted here to likely 24h versions if that's standard.
});
export type MarketSummary = z.infer<typeof MarketSummarySchema>;
export const MarketSummaryArraySchema = z.array(MarketSummarySchema);


// Based on models.FundingData in Python
export const FundingDataSchema = z.object({
    market_id: z.string(), // Or symbol
    funding_rate: z.string().transform(parseFloat),
    funding_time: z.number().int(), // Assuming Unix timestamp (ms or s)
    // Add other relevant fields if any
});
export type FundingData = z.infer<typeof FundingDataSchema>;
export const FundingDataArraySchema = z.array(FundingDataSchema);

// For Orderbook (based on common orderbook structures and Python's implicit use)
export const OrderbookLevelSchema = z.tuple([z.string().transform(parseFloat), z.string().transform(parseFloat)]); // [price, quantity]
export type OrderbookLevel = z.infer<typeof OrderbookLevelSchema>;

export const OrderbookSchema = z.object({
    market_id: z.string(), // Or symbol
    timestamp: z.number().int(), // Unix timestamp
    bids: z.array(OrderbookLevelSchema),
    asks: z.array(OrderbookLevelSchema),
    // Optional sequence number or last update ID if provided by API
    sequence: z.number().int().optional(),
});
export type Orderbook = z.infer<typeof OrderbookSchema>;

// Based on OHLCV model in Python (for klines)
export const OHLCVSchema = z.object({
    timestamp: z.number().int(), // Typically Unix timestamp (ms) for start of interval
    open: z.number(), // In Python these were float, direct number is fine in Zod
    high: z.number(),
    low: z.number(),
    close: z.number(),
    volume: z.number(),
});
export type OHLCV = z.infer<typeof OHLCVSchema>;
export const OHLCVArraySchema = z.array(OHLCVSchema);


// Based on models.Trade in Python
export const TradeSchema = z.object({
    id: z.string(), // Or number, depending on API
    market_id: z.string(), // Or symbol
    price: z.string().transform(parseFloat),
    quantity: z.string().transform(parseFloat),
    side: z.enum(['BUY', 'SELL']), // Or "BID"/"ASK", "Bid"/"Ask", "b"/"s" etc. - check API
    timestamp: z.number().int(), // Unix timestamp (ms)
    liquidation: z.boolean().optional(), // If API provides this
    // fee: z.string().transform(parseFloat).optional(), // If applicable and provided
    // fee_currency: z.string().optional(),
});
export type Trade = z.infer<typeof TradeSchema>;
export const TradeArraySchema = z.array(TradeSchema);

// Based on models.BBO in Python
export const BBOSchema = z.object({
    market_id: z.string(), // Or symbol
    best_bid_price: z.string().transform(parseFloat),
    best_bid_quantity: z.string().transform(parseFloat),
    best_ask_price: z.string().transform(parseFloat),
    best_ask_quantity: z.string().transform(parseFloat),
    timestamp: z.number().int(), // Unix timestamp (ms)
});
export type BBO = z.infer<typeof BBOSchema>;

console.log("src/models/market.ts loaded");

// Note: The actual field names and types must match the responses from the @paradex/sdk.
// The .transform(parseFloat) assumes the API returns numbers as strings. If they are already numbers,
// then z.number() would be used directly. This is a common pattern for financial APIs.
// Enum values (like trade side) also need to match the API's exact string values.
// Optional fields should be marked with .optional().
// This initial version is a direct translation of the Python models' structure.
// It will need verification against the actual data from the Paradex JS SDK.
