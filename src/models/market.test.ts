import { expect, test, describe } from "bun:test";
import { MarketDetailsSchema, MarketSummarySchema, OHLCVSchema, BBOSchema, OrderbookSchema, TradeSchema, FundingDataSchema } from "./market";

describe("Market Models (Zod Schemas)", () => {
    describe("MarketDetailsSchema", () => {
        test("should validate correct market details", () => {
            const data = {
                symbol: "BTC-PERP",
                base_asset: "BTC",
                quote_asset: "USDC",
                tick_size: "0.1",
                min_order_size: "0.001",
                max_order_size: "100",
                lot_size: "1",
                contract_type: "PERP",
                asset_kind: "PERP",
                is_active: true,
            };
            const parsed = MarketDetailsSchema.safeParse(data);
            expect(parsed.success).toBe(true);
            if (parsed.success) {
                expect(parsed.data.tick_size).toBe(0.1);
                expect(parsed.data.min_order_size).toBe(0.001);
            }
        });

        test("should fail validation for incorrect types", () => {
            const data = {
                symbol: "ETH-PERP",
                base_asset: "ETH",
                quote_asset: "USDC",
                tick_size: "not-a-number", // Invalid
                min_order_size: "0.01",
                max_order_size: "1000",
                lot_size: "1",
                contract_type: "PERP",
                asset_kind: "PERP",
            };
            const parsed = MarketDetailsSchema.safeParse(data);
            expect(parsed.success).toBe(false);
        });

        test("should fail if required fields are missing", () => {
            const data = { base_asset: "SOL" }; // Missing symbol, quote_asset etc.
            const parsed = MarketDetailsSchema.safeParse(data);
            expect(parsed.success).toBe(false);
        });
    });

    describe("MarketSummarySchema", () => {
        test("should validate correct market summary", () => {
            const data = {
                symbol: "BTC-PERP",
                mark_price: "40000.50",
                last_price: "40001.00",
                open_interest: "1000",
                high_price_24h: "41000",
                low_price_24h: "39000",
                volume_24h: "50000000",
                price_change_percent_24h: "2.5",
            };
            const parsed = MarketSummarySchema.safeParse(data);
            expect(parsed.success).toBe(true);
            if (parsed.success) {
                expect(parsed.data.mark_price).toBe(40000.50);
            }
        });
    });

    // Add similar tests for OHLCVSchema, BBOSchema, OrderbookSchema, TradeSchema, FundingDataSchema
    // Example for OHLCVSchema:
    describe("OHLCVSchema", () => {
        test("should validate correct OHLCV data", () => {
            const data = {
                timestamp: 1678886400000,
                open: 30000,
                high: 30500,
                low: 29800,
                close: 30200,
                volume: 100.5,
            };
            const parsed = OHLCVSchema.safeParse(data);
            expect(parsed.success).toBe(true);
        });
    });
});

console.log("src/models/market.test.ts loaded");
