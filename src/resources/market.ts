import { McpServer, McpRequest, ResourceTemplate } from "@modelcontextprotocol/sdk/server";
import { z } from "zod";
import { getParadexClient } from "../utils/paradex-client";
import { Config, config as appConfig } from "../utils/config";
import { MarketDetailsArraySchema, MarketSummarySchema, MarketDetails } from "../models/market"; // Zod schemas

export function registerMarketResources(server: McpServer, config: Config) {

    server.registerResource(
        "paradex_markets_list", // Resource name
        "paradex://markets",    // URI template (static for list)
        { // Metadata
            title: "Available Markets List",
            description: "Get a list of all available markets on Paradex.",
            // No input schema for a static list resource
        },
        async (uri: URL, params: Record<string, string>, mcpRequest?: McpRequest) => {
            try {
                const client = await getParadexClient();
                // Assumed JS SDK method: client.getMarkets()
                // Python used: client.fetch_markets()
                const response = await client.getMarkets?.();

                if (!response) {
                    throw new Error("Failed to fetch markets list from Paradex SDK.");
                }

                // Assuming response is an array of market objects or { results: [...] }
                let marketsData: any;
                if (Array.isArray(response)) {
                    marketsData = response;
                } else if (response && Array.isArray((response as any).results)) {
                    marketsData = (response as any).results;
                } else {
                    throw new Error("Unexpected response structure for markets list.");
                }

                // We can validate against MarketDetailsArraySchema if the structure matches
                const validatedMarkets = MarketDetailsArraySchema.parse(marketsData);

                // The Python version returned a custom structure with success, timestamp, env, markets, count.
                // MCP resources should return ContentPart[]
                return {
                    contents: [{
                        uri: uri.href,
                        type: "json",
                        json: { // Replicating Python's structure within the JSON content part
                            success: true,
                            timestamp: new Date().toISOString(),
                            environment: appConfig.PARADEX_ENVIRONMENT,
                            markets: validatedMarkets, // The array of market details
                            count: validatedMarkets.length,
                        }
                    }]
                };
            } catch (error: any) {
                console.error("Error in paradex://markets resource:", error);
                throw error;
            }
        }
    );

    server.registerResource(
        "paradex_market_summary_item", // Resource name
        new ResourceTemplate("paradex://market/summary/{market_id}", { list: undefined }), // Dynamic URI
        { // Metadata
            title: "Market Summary",
            description: "Get a summary of market information for a specific trading pair.",
            // Path parameters are defined in ResourceTemplate, not here.
            // If there were query params, they could be in an argsSchema.
        },
        async (uri: URL, params: { market_id: string }, mcpRequest?: McpRequest) => {
            // `params` will contain resolved path parameters, e.g., { market_id: "BTC-PERP" }
            const { market_id } = params;
            if (!market_id) {
                throw new Error("market_id path parameter is required.");
            }

            try {
                const client = await getParadexClient();
                // Python used: client.fetch_markets_summary(params={"market": market_id})
                // Assumed JS SDK: client.getMarketSummary(market_id) or client.getTicker(market_id)
                const summaryResponse = await client.getMarketSummary?.(market_id) ?? await client.getTicker?.(market_id);


                if (!summaryResponse) {
                    throw new Error(`Failed to fetch market summary for ${market_id} from Paradex SDK.`);
                }

                // The Python code returned the raw summary. We should validate it.
                const validatedSummary = MarketSummarySchema.parse(summaryResponse);

                return {
                    contents: [{
                        uri: uri.href,
                        type: "json",
                        json: validatedSummary // Python returned the direct response, assuming it's the summary object
                    }]
                };
            } catch (error: any) {
                console.error(`Error in paradex://market/summary/${market_id} resource:`, error);
                // If error is due to "not found", a specific MCP error could be raised.
                throw error;
            }
        }
    );

    console.log("Market resources registered.");
}

console.log("src/resources/market.ts loaded");

// Notes:
// - `paradex://markets`: Returns a list of all markets.
// - `paradex://market/summary/{market_id}`: Uses ResourceTemplate for dynamic segment `{market_id}`.
//   The handler receives `params` object with `market_id` property.
// - SDK Methods: `client.getMarkets()`, `client.getMarketSummary(market_id)` are assumed.
// - Response Validation: Zod schemas are used to parse and validate responses from the SDK.
// - Content Structure: The Python `get_markets` resource returned a custom dict. This is replicated inside the `json`
//   part of the MCP content. The `get_market_summary` directly returns the summary object as JSON.
/* Integration into src/server/server.ts:
import { registerMarketResources } from "../resources/market";
// ...
export function createServer(config: Config): McpServer {
    // ...
    registerSystemResources(server, config);
    registerMarketResources(server, config); // Add this
    // ...
    return server;
}
*/
/* And the import at the top of src/server/server.ts:
import { registerMarketResources } from "../resources/market"; // Add this
*/
