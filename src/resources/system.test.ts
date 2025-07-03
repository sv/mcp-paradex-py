import { expect, test, describe, mock } from "bun:test";
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server";
import { Config, config as loadedConfig } from "../utils/config"; // Import the actual loaded config for environment
import * as paradexClientUtils from "../utils/paradex-client";
import { registerSystemResources } from "./system";
import { SystemConfigResourceSchema, SystemTimeSchema, SystemStateSchema } from "./system"; // Import Zod schemas from resource file itself

// Mock the paradex client utility
mock.module("../utils/paradex-client", () => ({
    getParadexClient: mock(async () => ({
        getSystemConfig: mock(async () => ({ // Mock data from Paradex SDK's getSystemConfig
            chain_id: "0x1",
            collateral_asset: "USDC",
            fee_account: "0xFEES",
            // other specific fields returned by the actual SDK
            paradex_specific_key: "paradex_value"
        })),
        getServerTime: mock(async () => ({ // Mock data for getServerTime
            time: Date.now()
        })),
        getSystemState: mock(async () => ({ // Mock data for getSystemState
            state: "OPERATIONAL"
        })),
    })),
    // getAuthenticatedParadexClient is not typically used by system resources
    getAuthenticatedParadexClient: mock(async () => ({})),
}));


describe("System Resources", () => {
    let server: McpServer;
    // Use the actual loaded config for PARADEX_ENVIRONMENT consistency
    const mockConfig: Config = { ...loadedConfig };

    beforeEach(() => {
        // Create a new server for each test to isolate resource registrations
        server = new McpServer({ name: "test-mcp-server-resources", version: "0.1.0" });
        registerSystemResources(server, mockConfig);
    });

    describe("paradex://system/config resource", () => {
        test("should return merged system configuration", async () => {
            const resource = server.resources.find(r => r.name === "paradex_system_config");
            expect(resource).toBeDefined();
            if (!resource) throw new Error("Resource not found");

            const uri = new URL("paradex://system/config");
            const result = await resource.handler(uri, {} /* params */);

            expect(result.contents[0].type).toBe("json");
            const jsonResult = result.contents[0].json as any;

            expect(jsonResult.exchange).toBe("Paradex");
            expect(jsonResult.environment).toBe(mockConfig.PARADEX_ENVIRONMENT);
            expect(jsonResult.status).toBe("operational"); // Default from resource logic
            expect(jsonResult.paradex_specific_key).toBe("paradex_value"); // From mock SDK
            expect(jsonResult.collateral_asset).toBe("USDC"); // From mock SDK
            expect(SystemConfigResourceSchema.safeParse(jsonResult).success).toBe(true);
        });
    });

    describe("paradex://system/time resource", () => {
        test("should return current server time from Paradex", async () => {
            const resource = server.resources.find(r => r.name === "paradex_system_time");
            expect(resource).toBeDefined();
            if (!resource) throw new Error("Resource not found");

            const uri = new URL("paradex://system/time");
            const result = await resource.handler(uri, {});

            expect(result.contents[0].type).toBe("json");
            const jsonResult = result.contents[0].json as any;

            expect(jsonResult.time).toBeGreaterThan(0); // Mock returns Date.now()
            expect(SystemTimeSchema.safeParse(jsonResult).success).toBe(true);
        });
    });

    describe("paradex://system/state resource", () => {
        test("should return current system state from Paradex", async () => {
            const resource = server.resources.find(r => r.name === "paradex_system_state");
            expect(resource).toBeDefined();
            if (!resource) throw new Error("Resource not found");

            const uri = new URL("paradex://system/state");
            const result = await resource.handler(uri, {});

            expect(result.contents[0].type).toBe("json");
            const jsonResult = result.contents[0].json as any;

            expect(jsonResult.state).toBe("OPERATIONAL"); // From mock SDK
            expect(SystemStateSchema.safeParse(jsonResult).success).toBe(true);
        });
    });
});

console.log("src/resources/system.test.ts loaded");
