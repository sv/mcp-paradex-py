import { McpServer, McpRequest } from "@modelcontextprotocol/sdk/server";
import { z } from "zod";
import { getParadexClient, apiCall } from "../utils/paradex-client"; // Assuming this path
import { Config } from "../utils/config"; // Assuming this path
import {
    MarketDetailsSchema, MarketDetailsArraySchema, MarketDetails,
    MarketSummarySchema, MarketSummaryArraySchema, MarketSummary,
    FundingDataSchema, FundingDataArraySchema, FundingData,
    OrderbookSchema, Orderbook, OrderbookLevelSchema,
    OHLCVSchema, OHLCVArraySchema, OHLCV,
    TradeSchema, TradeArraySchema, Trade,
    BBOSchema, BBO
} from "../models/market"; // Assuming this path
import { OrderStateSchema, VaultSchema, VaultSummarySchema } from "../models/account"; // For get_filters_model

// Helper for JMESPath-like filtering (basic version)
// For full JMESPath, a library like 'jmespath' would be needed.
// This is a simplified placeholder.
function applySimpleFilter<T>(data: T[], filterLogic: (item: T) => boolean): T[] {
    return data.filter(filterLogic);
}

// Placeholder for a more sophisticated JMESPath utility if needed.
// For now, we'll rely on direct array methods or simple filters.
// The Python version used a `jmespath_utils.apply_jmespath_filter`.
// A full JS equivalent might be complex to implement from scratch here.
// We will simplify filtering logic for now.


export function registerMarketTools(server: McpServer, config: Config) {

    server.registerTool(
        "paradex_filters_model",
        {
            title: "Get Filters Model",
            description: "Get detailed schema information to build precise data filters for other tools.",
            inputSchema: {
                tool_name: z.enum([
                    "paradex_markets",
                    "paradex_market_summaries",
                    "paradex_open_orders",
                    "paradex_orders_history",
                    "paradex_vaults",
                    "paradex_vault_summary",
                    // Add other tools that support filtering if any
                ]).describe("The name of the tool to get the filters for.")
            }
        },
        async ({ tool_name } : { tool_name: string }) => {
            const toolSchemas: Record<string, any> = {
                "paradex_markets": MarketDetailsSchema.openapi("MarketDetails"),
                "paradex_market_summaries": MarketSummarySchema.openapi("MarketSummary"),
                "paradex_open_orders": OrderStateSchema.openapi("OrderState"), // Assuming OrderStateSchema is defined in account models
                "paradex_orders_history": OrderStateSchema.openapi("OrderState"),
                "paradex_vaults": VaultSchema.openapi("Vault"), // Assuming VaultSchema is defined
                "paradex_vault_summary": VaultSummarySchema.openapi("VaultSummary"), // Assuming VaultSummarySchema is defined
            };
            if (tool_name in toolSchemas) {
                return { content: [{ type: "json", json: toolSchemas[tool_name] }] };
            } else {
                // MCP error handling:
                // throw new McpError({ code: ErrorCode.InvalidParams, message: `No schema found for tool: ${tool_name}` });
                // For now, simple throw:
                throw new Error(`No schema found for tool: ${tool_name}`);
            }
        }
    );

    server.registerTool(
        "paradex_markets",
        {
            title: "Get Markets",
            description: "Find markets that match your trading criteria or get detailed market specifications. Retrieves comprehensive details about specified markets. If 'ALL' is specified or no market IDs are provided, returns details for all available markets.",
            inputSchema: {
                market_ids: z.array(z.string()).default(["ALL"]).describe("Market symbols to get details for (e.g., ['BTC-PERP', 'ETH-PERP']). Default is ['ALL']."),
                // JMESPath support is complex. For now, we'll simplify or omit.
                // jmespath_filter: z.string().optional().describe("JMESPath expression to filter, sort, or limit the results."),
                limit: z.number().int().positive().max(100).default(10).describe("Limit the number of results."),
                offset: z.number().int().nonnegative().default(0).describe("Offset the results."),
            }
        },
        async (params: { market_ids?: string[], limit?: number, offset?: number }, mcpContext?: McpRequest) => {
            try {
                const client = await getParadexClient();
                // In @paradex/sdk, fetching markets is likely:
                const response = await client.getMarkets(); // This is an assumed method based on common SDK patterns

                // The actual response structure from client.getMarkets() needs to be known.
                // Assuming it returns an array of market detail objects.
                // If it's structured like { results: [...] }, then:
                // let details: MarketDetails[] = MarketDetailsArraySchema.parse(response.results);
                // For now, let's assume `response` is directly the array or has a known structure

                // This is a placeholder parse, actual parsing depends on SDK's response shape
                let details: MarketDetails[];
                if (Array.isArray(response)) {
                    details = MarketDetailsArraySchema.parse(response);
                } else if (response && Array.isArray((response as any).results)) { // Common API pattern
                    details = MarketDetailsArraySchema.parse((response as any).results);
                } else {
                    console.error("Unexpected response structure from client.getMarkets():", response);
                    throw new Error("Failed to parse market details from Paradex API.");
                }

                const marketIds = params.market_ids || ["ALL"];
                if (!(marketIds.includes("ALL"))) {
                    details = details.filter(detail => marketIds.includes(detail.symbol));
                }

                // JMESPath filtering was here. Simplified:
                // if (params.jmespath_filter) {
                //     mcpContext?.notify({ type: "info", message: "JMESPath filtering is not fully supported in this version. Basic filtering applied." });
                //     // Basic filtering example (e.g., filter by base_asset if filter was "[?base_asset=='BTC']")
                //     // This would need a proper JMESPath parser or simplified query language.
                // }

                const sortedDetails = details.sort((a, b) => b.symbol.localeCompare(a.symbol)); // reverse: True in Python

                const offset = params.offset ?? 0;
                const limit = params.limit ?? 10;
                const paginatedDetails = sortedDetails.slice(offset, offset + limit);

                return {
                    content: [{
                        type: "json", // Using JSON content type for structured data
                        json: {
                            description: MarketDetailsSchema.description || "Details for specified markets.",
                            fields: MarketDetailsSchema.openapi("MarketDetails"), // Or a simplified schema representation
                            results: paginatedDetails,
                            total: sortedDetails.length,
                            limit: limit,
                            offset: offset,
                        }
                    }]
                };
            } catch (error: any) {
                console.error("Error in paradex_markets tool:", error);
                // Propagate error to MCP client
                // This requires knowing how McpServer expects errors to be thrown or returned.
                // throw new McpError({ code: ErrorCode.InternalError, message: error.message || "Failed to fetch market details" });
                throw error; // Let McpServer handle it or wrap it
            }
        }
    );

    server.registerTool(
        "paradex_market_summaries",
        {
            title: "Get Market Summaries",
            description: "Identify the most active or volatile markets and get current market conditions. Retrieves current market summary information. If 'ALL' is specified or no market IDs are provided, returns summaries for all available markets.",
            inputSchema: {
                market_ids: z.array(z.string()).default(["ALL"]).describe("Market symbols to get summaries for. Default ['ALL']."),
                // jmespath_filter: z.string().optional().describe("JMESPath expression to filter, sort, or limit the results."),
                limit: z.number().int().positive().max(100).default(10).describe("Limit the number of results."),
                offset: z.number().int().nonnegative().default(0).describe("Offset the results."),
            }
        },
        async (params: { market_ids?: string[], limit?: number, offset?: number }, mcpContext?: McpRequest) => {
            try {
                const client = await getParadexClient();
                // Assumed SDK method: client.getMarketSummaries() or client.getTickers()
                // Python used: client.fetch_markets_summary(params={"market": "ALL"})
                // The `market: "ALL"` suggests it might fetch all and then filter, or the API supports "ALL".
                // Let's assume the JS SDK has a method that can fetch all or specific summaries.
                // For now, client.getMarketSummaries() is a placeholder for such a method.
                const response = await client.getMarketSummaries ? await client.getMarketSummaries() : await client.getTickers(); // Or similar method

                let summaries: MarketSummary[];
                if (Array.isArray(response)) {
                    summaries = MarketSummaryArraySchema.parse(response);
                } else if (response && Array.isArray((response as any).results)) {
                    summaries = MarketSummaryArraySchema.parse((response as any).results);
                } else if (response && typeof response === 'object' && !Array.isArray(response)) {
                    // If it returns an object where keys are symbols and values are summaries
                    summaries = MarketSummaryArraySchema.parse(Object.values(response));
                }
                else {
                    console.error("Unexpected response structure from client.getMarketSummaries():", response);
                    throw new Error("Failed to parse market summaries from Paradex API.");
                }

                const marketIds = params.market_ids || ["ALL"];
                if (!(marketIds.includes("ALL"))) {
                    summaries = summaries.filter(summary => marketIds.includes(summary.symbol));
                }

                // JMESPath filtering simplified/omitted for now

                const sortedSummaries = summaries.sort((a, b) => b.symbol.localeCompare(a.symbol)); // reverse: True

                const offset = params.offset ?? 0;
                const limit = params.limit ?? 10;
                const paginatedSummaries = sortedSummaries.slice(offset, offset + limit);

                return {
                    content: [{
                        type: "json",
                        json: {
                            description: MarketSummarySchema.description || "Summary information for specified markets.",
                            fields: MarketSummarySchema.openapi("MarketSummary"),
                            results: paginatedSummaries,
                            total: sortedSummaries.length,
                            limit: limit,
                            offset: offset,
                        }
                    }]
                };
            } catch (error: any) {
                console.error("Error in paradex_market_summaries tool:", error);
                throw error;
            }
        }
    );

    server.registerTool(
        "paradex_funding_data",
        {
            title: "Get Funding Data",
            description: "Analyze funding rates for potential funding arbitrage or to understand holding costs. This data is critical for perpetual futures traders.",
            inputSchema: {
                market_id: z.string().describe("Market symbol to get funding data for (e.g., 'BTC-PERP')."),
                start_unix_ms: z.number().int().describe("Start time in Unix milliseconds."),
                end_unix_ms: z.number().int().describe("End time in Unix milliseconds."),
            }
        },
        async (params: { market_id: string, start_unix_ms: number, end_unix_ms: number }, mcpContext?: McpRequest) => {
            try {
                const client = await getParadexClient();
                // Assumed SDK method: client.getFundingRatesHistory(marketId, { startTime, endTime }) or similar
                // Python used: client.fetch_funding_data(params={"market": market_id, "start_at": start_unix_ms, "end_at": end_unix_ms})
                const apiParams = {
                    symbol: params.market_id, // SDK might use 'symbol' or 'market'
                    startTime: params.start_unix_ms,
                    endTime: params.end_unix_ms
                };
                // This is a highly assumed method name and parameter structure
                const response = await client.getFundingRateHistory?.(params.market_id, apiParams) ?? await (client as any).getFundingData?.(apiParams);


                let fundingDataList: FundingData[];
                if (Array.isArray(response)) {
                    fundingDataList = FundingDataArraySchema.parse(response);
                } else if (response && Array.isArray((response as any).results)) {
                    fundingDataList = FundingDataArraySchema.parse((response as any).results);
                } else {
                    console.error("Unexpected response structure from client.getFundingData():", response);
                    throw new Error("Failed to parse funding data from Paradex API.");
                }

                return {
                    content: [{
                        type: "json",
                        json: {
                            description: FundingDataSchema.description || `Funding data for ${params.market_id}.`,
                            fields: FundingDataSchema.openapi("FundingData"),
                            results: fundingDataList,
                        }
                    }]
                };
            } catch (error: any) {
                console.error(`Error in paradex_funding_data tool for ${params.market_id}:`, error);
                throw error;
            }
        }
    );

    // Valid orderbook depth values, similar to Python's OrderbookDepth Enum
    const OrderbookDepthEnum = z.enum(["5", "10", "20", "50", "100"]).transform(Number).pipe(z.number().int());
    // Or more directly if the API takes numbers:
    // const OrderbookDepthEnum = z.nativeEnum({ SHALLOW: 5, MEDIUM: 10, DEEP: 20, VERY_DEEP: 50, FULL: 100 });
    // For now, let's use specific numbers as per Python example.

    server.registerTool(
        "paradex_orderbook",
        {
            title: "Get Orderbook",
            description: "Analyze market depth and liquidity to optimize order entry and execution. Understanding the orderbook is essential for effective trade execution.",
            inputSchema: {
                market_id: z.string().describe("Market symbol to get orderbook for (e.g., 'BTC-PERP')."),
                depth: z.number().int().pipe(z.enum([5, 10, 20, 50, 100])).default(10).describe("The depth of the orderbook to retrieve (e.g., 5, 10, 20, 50, 100). Default 10.")
            }
        },
        async (params: { market_id: string, depth?: 5 | 10 | 20 | 50 | 100 }, mcpContext?: McpRequest) => {
            try {
                const client = await getParadexClient();
                // Assumed SDK method: client.getOrderbook(marketId, { depth })
                // Python used: client.fetch_orderbook(market_id, params={"depth": depth})
                const response = await client.getOrderBook?.(params.market_id, { depth: params.depth }); // More likely: client.getOrderBook(symbol, depth)

                if (!response) { // Ensure response is not undefined if SDK method is optional a la `?.`
                     throw new Error("Failed to fetch orderbook: SDK method not found or returned undefined.");
                }

                // The response from `fetch_orderbook` in Python was returned directly.
                // We should parse it against our OrderbookSchema for validation and typing.
                const orderbook = OrderbookSchema.parse(response);

                return {
                    content: [{
                        type: "json",
                        // The Python version returned the direct response.
                        // Here we return the parsed and validated object.
                        // It might be useful to also include schema/description if that was the Python server's pattern.
                        json: orderbook // Python version returned the raw response, assuming it matched the implicit structure.
                    }]
                };
            } catch (error: any) {
                console.error(`Error in paradex_orderbook tool for ${params.market_id}:`, error);
                throw error;
            }
        }
    );

    // KLinesResolutionEnum from Python
    const KLinesResolutionEnum = z.enum(["1", "3", "5", "15", "30", "60"]).describe("Time resolution of klines/candlesticks.");
    // If the API expects numbers:
    // const KLinesResolutionNumberEnum = z.enum([1, 3, 5, 15, 30, 60]);

    server.registerTool(
        "paradex_klines",
        {
            title: "Get Klines (Candlestick Data)",
            description: "Analyze historical price patterns for technical analysis and trading decisions. Candlestick data is fundamental for most technical analysis.",
            inputSchema: {
                market_id: z.string().describe("Market symbol to get klines for (e.g., 'BTC-PERP')."),
                resolution: KLinesResolutionEnum.describe("The time resolution of the klines (e.g., '1', '5', '60' for 1m, 5m, 1h)."),
                start_unix_ms: z.number().int().describe("Start time in Unix milliseconds."),
                end_unix_ms: z.number().int().describe("End time in Unix milliseconds."),
            }
        },
        async (params: { market_id: string, resolution: string, start_unix_ms: number, end_unix_ms: number }, mcpContext?: McpRequest) => {
            try {
                const client = await getParadexClient();
                // Python used: api_call(client, "markets/klines", params={...})
                // This suggests a direct API call rather than a dedicated SDK method in Python's case,
                // or the SDK method was a thin wrapper.
                // Let's assume the JS SDK might have a dedicated method:
                const apiParams = {
                    symbol: params.market_id,
                    resolution: params.resolution, // JS SDK might expect number or string
                    startTime: params.start_unix_ms, // or start_at
                    endTime: params.end_unix_ms,   // or end_at
                };

                // Assumed SDK method: client.getKlines(apiParams) or client.getOHLCV(apiParams)
                const response = await client.getKlines?.(apiParams) ?? await client.getOHLCV?.(apiParams)
                                 ?? await apiCall(client, 'GET', `markets/klines`, apiParams); // Fallback to generic if specific not found

                let klines: OHLCV[];
                // Python constructed OHLCV objects from a list of lists.
                // The JS SDK might return objects directly or a similar structure.
                if (response && Array.isArray((response as any).results) && Array.isArray((response as any).results[0])) {
                    // Matches Python's structure: results: [[ts, o, h, l, c, v], ...]
                    const rawKlines = (response as any).results as number[][];
                    klines = OHLCVArraySchema.parse(
                        rawKlines.map(k => ({
                            timestamp: k[0],
                            open: k[1],
                            high: k[2],
                            low: k[3],
                            close: k[4],
                            volume: k[5],
                        }))
                    );
                } else if (Array.isArray(response)) { // If SDK returns array of OHLCV objects
                    klines = OHLCVArraySchema.parse(response);
                } else if (response && Array.isArray((response as any).results)) { // if SDK returns { results: [OHLCVObject, ...] }
                     klines = OHLCVArraySchema.parse((response as any).results);
                }
                else {
                    console.error("Unexpected response structure from klines endpoint:", response);
                    throw new Error("Failed to parse klines data from Paradex API.");
                }

                return {
                    content: [{
                        type: "json", // Python returned a list of OHLCV objects
                        json: klines
                    }]
                };
            } catch (error: any) {
                console.error(`Error in paradex_klines tool for ${params.market_id}:`, error);
                throw error;
            }
        }
    );

    server.registerTool(
        "paradex_trades",
        {
            title: "Get Trades",
            description: "Analyze actual market transactions to understand market sentiment and liquidity. Trade data provides insights into actual market activity.",
            inputSchema: {
                market_id: z.string().describe("Market symbol to get trades for (e.g., 'BTC-PERP')."),
                start_unix_ms: z.number().int().describe("Start time in Unix milliseconds."),
                end_unix_ms: z.number().int().describe("End time in Unix milliseconds."),
            }
        },
        async (params: { market_id: string, start_unix_ms: number, end_unix_ms: number }, mcpContext?: McpRequest) => {
            try {
                const client = await getParadexClient();
                // Python used: client.fetch_trades(params={...})
                // Assumed JS SDK method: client.getTrades(marketId, { startTime, endTime }) or similar
                const apiParams = {
                    symbol: params.market_id,
                    startTime: params.start_unix_ms,
                    endTime: params.end_unix_ms,
                };
                const response = await client.getTradesHistory?.(params.market_id, apiParams) ?? await (client as any).getTrades?.(apiParams);


                let trades: Trade[];
                if (Array.isArray(response)) {
                    trades = TradeArraySchema.parse(response);
                } else if (response && Array.isArray((response as any).results)) {
                    trades = TradeArraySchema.parse((response as any).results);
                } else {
                    console.error("Unexpected response structure from trades endpoint:", response);
                    throw new Error("Failed to parse trades data from Paradex API.");
                }

                return {
                    content: [{
                        type: "json",
                        json: {
                            description: TradeSchema.description || `Trade history for ${params.market_id}.`,
                            fields: TradeSchema.openapi("Trade"),
                            results: trades,
                        }
                    }]
                };
            } catch (error: any) {
                console.error(`Error in paradex_trades tool for ${params.market_id}:`, error);
                throw error;
            }
        }
    );

    server.registerTool(
        "paradex_bbo",
        {
            title: "Get BBO (Best Bid and Offer)",
            description: "Get the current best available prices for immediate execution decisions. The BBO provides the most essential price information with minimal data.",
            inputSchema: {
                market_id: z.string().describe("Market symbol to get BBO for (e.g., 'BTC-PERP')."),
            }
        },
        async (params: { market_id: string }, mcpContext?: McpRequest) => {
            try {
                const client = await getParadexClient();
                // Python used: client.fetch_bbo(market_id)
                // Assumed JS SDK method: client.getBBO(marketId) or client.getTicker(marketId) if BBO is part of ticker
                const response = await client.getBBO?.(params.market_id) ?? await client.getBestBidOffer?.(params.market_id);

                if (!response) {
                    throw new Error("Failed to fetch BBO: SDK method not found or returned undefined.");
                }

                const bbo = BBOSchema.parse(response);

                return {
                    content: [{
                        type: "json",
                        json: {
                            description: BBOSchema.description || `Best Bid and Offer for ${params.market_id}.`,
                            fields: BBOSchema.openapi("BBO"), // Or a simplified schema
                            results: bbo, // Python returned a dict with BBO model + description/fields
                        }
                    }]
                };
            } catch (error: any) {
                console.error(`Error in paradex_bbo tool for ${params.market_id}:`, error);
                throw error;
            }
        }
    );

    console.log("All market tools registered.");
}

console.log("src/tools/market.ts loaded");

// Note:
// - The actual method `client.getMarkets()` and its response structure are assumptions.
//   This will need to be validated against the `@paradex/sdk`.
// - JMESPath filtering is complex; a full JS implementation is out of scope for this direct translation.
//   Simplified filtering or using a library would be needed. For now, it's mostly omitted.
// - Error handling: Throwing errors directly might be okay, or MCP might have specific error types/formats.
// - The `fields` in the response: Python used `model_json_schema()`. Zod's `.openapi()` can generate
//   OpenAPI-compatible schemas, or a custom schema representation might be needed if MCP expects a specific format.
// - Context (`ctx` in Python tools for `ctx.error`) is available as the second argument in MCP tool handlers.
//   It can be used for notifications (`mcpContext?.notify(...)`) or other context-aware actions.
// - The `apiCall` utility might be used if direct SDK methods are not available for some specific data points,
//   but typed SDK methods are always preferred.
// - `parseFloat` was used in Zod schemas assuming string numbers from API. If numbers, adjust schema.
// - `content: [{ type: "json", json: ... }]` is one way to return structured data.
//   MCP also supports `text` and other types. For complex objects, `json` is suitable.
//   The Python server often returned a dict that was implicitly JSON-serialized.
//   The JS SDK might expect a specific structure for tool results (e.g., direct object or `{ content: [...] }`).
//   The example `({ content: [{ type: "text", text: String(a + b) }] })` from MCP SDK docs suggests this structure.
//   The Python server's return dict with "description", "fields", "results" needs to be mapped to this.
//   A common pattern for complex data is to put the whole structure inside a single `json` content part.
/* Example of how this might be integrated into src/server/server.ts:
import { registerMarketTools } from "../tools/market";

export function createServer(config: Config): McpServer {
    // ... server creation ...
    registerMarketTools(server, config);
    // ... register other tools ...
    return server;
}
*/
/* And in src/index.ts, ensure server/server.ts is imported, which in turn imports and registers tools:
import { createServer, runServer } from './server/server'; // This should trigger registrations
// ... rest of main function ...
*/
