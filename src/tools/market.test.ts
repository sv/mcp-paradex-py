import { expect, test, describe, mock, spyOn } from "bun:test";
import { McpServer, McpRequest } from "@modelcontextprotocol/sdk/server";
import { z } from "zod";
import { Config } from "../utils/config";
import * as paradexClientUtils from "../utils/paradex-client"; // Import all as a namespace
import { registerMarketTools }
    from "./market";
import { MarketDetailsSchema, MarketSummarySchema, MarketDetailsArraySchema, MarketSummaryArraySchema, OrderbookSchema, OHLCVArraySchema, TradeArraySchema, BBOSchema } from "../models/market";

// Mock the paradex client utility
// Option 1: Mock specific functions
mock.module("../utils/paradex-client", () => ({
    getParadexClient: mock(async () => ({
        // Mock the client object and its methods used by market tools
        getMarkets: mock(async () => ([ // Mock implementation for getMarkets
            { symbol: "BTC-PERP", base_asset: "BTC", quote_asset: "USDC", tick_size: "0.1", min_order_size: "0.001", max_order_size: "100", lot_size: "1", contract_type: "PERP", asset_kind: "PERP", is_active: true },
            { symbol: "ETH-PERP", base_asset: "ETH", quote_asset: "USDC", tick_size: "0.01", min_order_size: "0.01", max_order_size: "1000", lot_size: "1", contract_type: "PERP", asset_kind: "PERP", is_active: true },
        ])),
        getMarketSummaries: mock(async () => ([
            { symbol: "BTC-PERP", mark_price: "40000", last_price: "40001", open_interest: "100", high_price_24h: "41000", low_price_24h: "39000", volume_24h: "50000", price_change_percent_24h: "2.5" },
        ])),
        getOrderBook: mock(async (marketId: string, { depth }: { depth?: number }) => ({
            market_id: marketId,
            timestamp: Date.now(),
            bids: [["39990", "1.0"], ["39980", "2.5"]],
            asks: [["40010", "0.5"], ["40020", "3.0"]],
            sequence: 12345,
        })),
        getKlines: mock(async (params: any) => ([ // Assuming params are { symbol, resolution, startTime, endTime }
            { timestamp: params.startTime, open: 100, high: 105, low: 95, close: 102, volume: 1000 },
        ])),
        getTradesHistory: mock(async (symbol: string, params: any) => ([
             { id: "1", market_id: symbol, price: "40000", quantity: "0.1", side: "BUY", timestamp: Date.now() - 1000 },
        ])),
        getBBO: mock(async (marketId: string) => ({
            market_id: marketId, best_bid_price: "39990", best_bid_quantity: "1.0", best_ask_price: "40010", best_ask_quantity: "0.5", timestamp: Date.now()
        })),
        // Mock other methods like getFundingRateHistory if they exist and are used
    })),
    getAuthenticatedParadexClient: mock(async () => ({})), // Not used by market tools usually
    apiCall: mock(async (client: any, method: string, path: string, params?: Record<string, any>) => {
        // Generic fallback for apiCall if used by any market tool
        if (path === 'markets/klines') { // Example from klines tool
             return { results: [[params?.startTime, 100,105,95,102,1000]] };
        }
        return { results: [] };
    }),
}));


describe("Market Tools", () => {
    let server: McpServer;
    const mockConfig: Config = { // Provide a minimal mock config
        NODE_ENV: "test",
        SERVER_NAME: "test-server",
        SERVER_PORT: 8080,
        PARADEX_ENVIRONMENT: "testnet",
        LOG_LEVEL: "info",
    };

    // Spy on specific client methods if needed for finer-grained assertion
    // let getMarketsSpy: any;

    beforeEach(() => {
        server = new McpServer({ name: "test-mcp-server", version: "0.1.0" });
        registerMarketTools(server, mockConfig);

        // If using the global module mock, spies need to be on the mocked functions.
        // This is tricky with bun:test's current module mocking.
        // An alternative is to pass the mocked client into registration functions,
        // but that changes the main code structure.

        // For now, we rely on the mock implementations above.
    });

    describe("paradex_markets tool", () => {
        test("should return list of markets", async () => {
            const tool = server.tools["paradex_markets"];
            expect(tool).toBeDefined();

            const result = await tool.handler({ limit: 1, offset: 0 });
            expect(result.content[0].type).toBe("json");
            const jsonResult = result.content[0].json as any;
            expect(jsonResult.results.length).toBe(1);
            expect(jsonResult.results[0].symbol).toBe("ETH-PERP"); // Sorted reverse alphabetically by mock
            expect(jsonResult.total).toBe(2);
        });

        test("should filter markets by market_ids", async () => {
            const tool = server.tools["paradex_markets"];
            const result = await tool.handler({ market_ids: ["BTC-PERP"], limit: 10, offset: 0 });
            const jsonResult = result.content[0].json as any;
            expect(jsonResult.results.length).toBe(1);
            expect(jsonResult.results[0].symbol).toBe("BTC-PERP");
        });
    });

    describe("paradex_market_summaries tool", () => {
        test("should return market summaries", async () => {
            const tool = server.tools["paradex_market_summaries"];
            expect(tool).toBeDefined();
            const result = await tool.handler({ limit: 1 });
            const jsonResult = result.content[0].json as any;
            expect(jsonResult.results.length).toBe(1);
            expect(jsonResult.results[0].symbol).toBe("BTC-PERP");
            expect(jsonResult.results[0].mark_price).toBe(40000);
        });
    });

    describe("paradex_orderbook tool", () => {
        test("should return orderbook for a market", async () => {
            const tool = server.tools["paradex_orderbook"];
            expect(tool).toBeDefined();
            const result = await tool.handler({ market_id: "BTC-PERP", depth: 10 });
            const jsonResult = result.content[0].json as any; // The tool returns the orderbook object directly
            expect(jsonResult.market_id).toBe("BTC-PERP");
            expect(jsonResult.bids.length).toBeGreaterThan(0);
            expect(jsonResult.asks.length).toBeGreaterThan(0);
            expect(OrderbookSchema.safeParse(jsonResult).success).toBe(true);
        });
    });

    describe("paradex_klines tool", () => {
        test("should return klines for a market", async () => {
            const tool = server.tools["paradex_klines"];
            expect(tool).toBeDefined();
            const params = { market_id: "BTC-PERP", resolution: "60", start_unix_ms: Date.now() - 3600000, end_unix_ms: Date.now() };
            const result = await tool.handler(params);
            const jsonResult = result.content[0].json as any; // Returns array of klines
            expect(Array.isArray(jsonResult)).toBe(true);
            expect(jsonResult.length).toBeGreaterThan(0);
            expect(jsonResult[0].open).toBe(100); // From mock
            expect(OHLCVArraySchema.safeParse(jsonResult).success).toBe(true);
        });
    });

    describe("paradex_trades tool", () => {
        test("should return trades for a market", async () => {
            const tool = server.tools["paradex_trades"];
            expect(tool).toBeDefined();
            const params = { market_id: "BTC-PERP", start_unix_ms: Date.now() - 3600000, end_unix_ms: Date.now() };
            const result = await tool.handler(params);
            const jsonResult = result.content[0].json as any;
            expect(jsonResult.results.length).toBeGreaterThan(0);
            expect(jsonResult.results[0].market_id).toBe("BTC-PERP");
            expect(TradeArraySchema.safeParse(jsonResult.results).success).toBe(true);
        });
    });

    describe("paradex_bbo tool", () => {
        test("should return BBO for a market", async () => {
            const tool = server.tools["paradex_bbo"];
            expect(tool).toBeDefined();
            const result = await tool.handler({ market_id: "BTC-PERP" });
            const jsonResult = result.content[0].json as any;
            expect(jsonResult.results.market_id).toBe("BTC-PERP");
            expect(jsonResult.results.best_bid_price).toBe(39990);
             expect(BBOSchema.safeParse(jsonResult.results).success).toBe(true);
        });
    });

    describe("paradex_filters_model tool", () => {
        test("should return schema for a given tool name", async () => {
            const tool = server.tools["paradex_filters_model"];
            expect(tool).toBeDefined();
            const result = await tool.handler({ tool_name: "paradex_markets" });
            const jsonResult = result.content[0].json as any;
            expect(jsonResult.title).toBe("MarketDetails"); // ZodSchema.openapi("MarketDetails")
            expect(jsonResult.properties.symbol).toBeDefined();
        });

        test("should throw error for unknown tool name", async () => {
            const tool = server.tools["paradex_filters_model"];
            let errorThrown = false;
            try {
                await tool.handler({ tool_name: "unknown_tool" as any });
            } catch (e: any) {
                errorThrown = true;
                expect(e.message).toContain("No schema found for tool: unknown_tool");
            }
            expect(errorThrown).toBe(true);
        });
    });

});

console.log("src/tools/market.test.ts loaded");
