import { McpServer, McpRequest } from "@modelcontextprotocol/sdk/server";
import { z } from "zod";
import { getParadexClient, apiCall } from "../utils/paradex-client";
import { Config, config as appConfig } from "../utils/config"; // Import the loaded config

// Zod schema for SystemConfig (based on Python's client.fetch_system_config() and extra fields)
// This will need to be aligned with the actual response from JS SDK client.getSystemConfig()
export const SystemConfigParadexSchema = z.object({
    // Fields from client.fetch_system_config() in Python's Paradex client
    // These are illustrative; actual fields from JS SDK's getSystemConfig() are needed
    chain_id: z.string().optional(), // e.g., "0x..." or number
    collateral_asset: z.string().optional(), // e.g., "USDC"
    fee_account: z.string().optional(), // StarkEx fee account
    // ... other fields from the actual Paradex API response for system config
    // The Python code did `base.update(syscfg.model_dump())`, so we merge.
}).passthrough(); // Allow other fields not explicitly defined

export const SystemConfigResourceSchema = SystemConfigParadexSchema.extend({
    exchange: z.string(),
    timestamp: z.string().datetime(),
    environment: z.string(), // e.g., testnet, mainnet
    status: z.string(), // e.g., operational
    features: z.array(z.string()),
    trading_hours: z.string(),
    website: z.string().url(),
    documentation: z.string().url(),
});
export type SystemConfigResource = z.infer<typeof SystemConfigResourceSchema>;


// Zod schema for SystemTime (illustrative, based on typical time endpoint)
export const SystemTimeSchema = z.object({
    server_time_ms: z.number().int(), // Milliseconds since epoch
    // Paradex Python client's fetch_system_time() returned: {"time": 1678886400000}
    // Adjusting to match that if JS SDK is similar
    time: z.number().int(),
});
export type SystemTime = z.infer<typeof SystemTimeSchema>;

// Zod schema for SystemState (illustrative)
export const SystemStateSchema = z.object({
    status: z.string(), // e.g., "OPERATIONAL", "MAINTENANCE"
    // Paradex Python client's fetch_system_state() returned: {"state": "OPERATIONAL"}
    // Adjusting to match
    state: z.string(),
    message: z.string().optional(), // Optional message during maintenance
});
export type SystemState = z.infer<typeof SystemStateSchema>;


export function registerSystemResources(server: McpServer, config: Config) {

    server.registerResource(
        "paradex_system_config", // Resource name
        "paradex://system/config", // URI template
        { // Metadata
            title: "System Configuration",
            description: "Get general market information, status, and configuration of the Paradex exchange.",
            // No input schema for simple GET resource
        },
        async (uri: URL, params: Record<string, string>, mcpRequest?: McpRequest) => {
            try {
                const client = await getParadexClient();
                // Assumed JS SDK method, e.g., client.getSystemConfig()
                const paradexSysConfig = await client.getSystemConfig?.();

                if (!paradexSysConfig) {
                    throw new Error("Failed to fetch system config from Paradex SDK.");
                }

                const baseInfo = {
                    exchange: "Paradex",
                    timestamp: new Date().toISOString(),
                    environment: appConfig.PARADEX_ENVIRONMENT,
                    status: "operational", // This might come from paradexSysConfig.status or similar
                    features: ["perpetual_futures", "perpetual_options", "vaults"],
                    trading_hours: "24/7",
                    website: "https://paradex.trade/",
                    documentation: "https://docs.paradex.com/", // Updated URL
                };

                // Merge Paradex specific config with base info
                // The passthrough() in Zod schema allows this merging if fields are not predefined.
                const fullConfigData = { ...baseInfo, ...paradexSysConfig };
                const validatedConfig = SystemConfigResourceSchema.parse(fullConfigData);

                return {
                    contents: [{
                        uri: uri.href,
                        // text: JSON.stringify(validatedConfig, null, 2), // For text type
                        // mimeType: "application/json"
                        json: validatedConfig, // For json type (preferred by MCP for structured data)
                        type: "json",
                    }]
                };
            } catch (error: any) {
                console.error("Error in paradex://system/config resource:", error);
                // Return an MCP error structure if possible, or let server handle
                // This might involve creating an McpError object
                throw error;
            }
        }
    );

    server.registerResource(
        "paradex_system_time",
        "paradex://system/time",
        {
            title: "System Time",
            description: "Get the current Paradex server time.",
        },
        async (uri: URL, params: Record<string, string>, mcpRequest?: McpRequest) => {
            try {
                const client = await getParadexClient();
                // Assumed JS SDK method: client.getServerTime()
                // Python used client.fetch_system_time()
                const systemTimeResponse = await client.getServerTime?.() ?? await (client as any).getSystemTime?.();

                if (!systemTimeResponse) {
                    throw new Error("Failed to fetch system time from Paradex SDK.");
                }

                const validatedTime = SystemTimeSchema.parse(systemTimeResponse);

                return {
                    contents: [{
                        uri: uri.href,
                        json: validatedTime,
                        type: "json",
                    }]
                };
            } catch (error: any) {
                console.error("Error in paradex://system/time resource:", error);
                throw error;
            }
        }
    );

    server.registerResource(
        "paradex_system_state",
        "paradex://system/state",
        {
            title: "System State",
            description: "Get the current operational state of the Paradex system.",
        },
        async (uri: URL, params: Record<string, string>, mcpRequest?: McpRequest) => {
            try {
                const client = await getParadexClient();
                // Assumed JS SDK method: client.getSystemState()
                // Python used client.fetch_system_state()
                const systemStateResponse = await client.getSystemState?.();

                if (!systemStateResponse) {
                    throw new Error("Failed to fetch system state from Paradex SDK.");
                }

                const validatedState = SystemStateSchema.parse(systemStateResponse);

                return {
                    contents: [{
                        uri: uri.href,
                        json: validatedState,
                        type: "json",
                    }]
                };
            } catch (error: any) {
                console.error("Error in paradex://system/state resource:", error);
                throw error;
            }
        }
    );

    console.log("System resources registered.");
}

console.log("src/resources/system.ts loaded");

// Notes:
// - SDK Method Names: `client.getSystemConfig()`, `client.getServerTime()`, `client.getSystemState()` are assumed.
//   Actual names from `@paradex/sdk` must be used.
// - Response Structures: Zod schemas are based on Python client's responses. These need to match actual JS SDK responses.
// - Error Handling: Throwing errors which McpServer should catch. Specific McpError types could be used.
// - URI parameters (`params` in handler): Not used in these system resources as URIs are static.
// - `appConfig.PARADEX_ENVIRONMENT` is used from the global config.
// - Content type: Using `type: "json"` for structured data, which is generally preferred by MCP clients.
//   The `json` property of the content part should contain the JS object.
/* Integration into src/server/server.ts:
import { registerSystemResources } from "../resources/system";
// ...
export function createServer(config: Config): McpServer {
    // ...
    registerMarketTools(server, config);
    registerAccountTools(server, config);
    registerSystemResources(server, config); // Add this
    // ...
    return server;
}
*/
/* And the import at the top of src/server/server.ts:
import { registerSystemResources } from "../resources/system"; // Add this
*/
