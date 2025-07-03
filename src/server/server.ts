import { McpServer, StdioServerTransport, StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/index.js";
import { randomUUID } from "node:crypto";
import { Config, config as appConfigInstance } from "../utils/config"; // Import loaded config instance
import { registerMarketTools } from "../tools/market";
import { registerAccountTools } from "../tools/account";
import { registerSystemResources } from "../resources/system";
import { registerMarketResources } from "../resources/market";

// Configure logging - Bun typically uses console.log, .error, etc.
// For more advanced logging, a library could be added, but for now, console will be used.

let appConfig: Config;

export function createServer(config: Config): McpServer {
    appConfig = config;
    const server = new McpServer({
        name: config.SERVER_NAME,
        version: "0.1.0", // Version can be dynamic if needed
        // description, vendor, etc. can be added from config if available in JS SDK
    });

    // Import and register tools, resources, and prompts

    // Import and call tool registration functions
    // Using static imports for immediate registration
    // Note: Ensure that the tool files (e.g., market.ts) only define the registration function
    // and don't have side effects that depend on the server instance being fully ready,
    // or ensure server instance is passed correctly.

    // market.ts should export registerMarketTools
    registerMarketTools(server, config);

    // Register account tools
    registerAccountTools(server, config);

    // Placeholder for future tool modules
    // import { registerOrderTools } from "../tools/orders";
    // registerOrderTools(server, config);

    // import { registerSystemTools } from "../tools/system";
    // registerSystemTools(server, config);

    // import { registerVaultTools } from "../tools/vaults";
    // registerVaultTools(server, config);


    // Similarly for resources and prompts
    registerMarketResources(server, config); // Register market resources
    registerSystemResources(server, config); // Register system resources

    // import { registerTraderPrompts } from "../prompts/trader_prompts";
    // registerTraderPrompts(server, config);


    return server;
}

export async function runServer(server: McpServer, transportChoice: string, port?: number) {
    console.info(`Starting MCP Paradex server with ${transportChoice} transport...`);

    try {
        if (transportChoice === "stdio") {
            const transport = new StdioServerTransport();
            await server.connect(transport);
            console.info("MCP Server connected via stdio.");
        } else if (transportChoice === "sse") {
            // This is a simplified SSE setup. For production, you'd use a proper HTTP server like Express or Bun.serve
            // The MCP SDK's StreamableHTTPServerTransport is more robust for HTTP-based comms.
            // For Bun, you'd typically use Bun.serve:
            if (!port) {
                console.error("Port is required for SSE transport.");
                process.exit(1);
            }
            console.info(`Attempting to start HTTP server on port ${port} for SSE-like transport.`);

            // Example using StreamableHTTPServerTransport with Bun.serve
            // This part will be refined when we set up the main index.ts
            // For now, this illustrates the intent.
            const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};

            Bun.serve({
                port: port,
                async fetch(req) {
                    const url = new URL(req.url);
                    if (url.pathname === "/mcp") {
                        const sessionIdHeader = req.headers.get('mcp-session-id');
                        let transport: StreamableHTTPServerTransport;

                        if (sessionIdHeader && transports[sessionIdHeader]) {
                            transport = transports[sessionIdHeader];
                        } else {
                            // A real client would send an initialize request first.
                            // This is a simplified example.
                            transport = new StreamableHTTPServerTransport({
                                sessionIdGenerator: () => randomUUID(),
                                onsessioninitialized: (newSessionId) => {
                                    transports[newSessionId] = transport;
                                    console.log(`MCP session ${newSessionId} initialized.`);
                                },
                            });
                            transport.onclose = () => {
                                if (transport.sessionId) {
                                    delete transports[transport.sessionId];
                                    console.log(`MCP session ${transport.sessionId} closed.`);
                                }
                            };
                            // Connect this new transport to the main MCP server instance
                            // This is a conceptual link; actual McpServer.connect might need one transport per server
                            // or the transport itself handles multiplexing if designed for it.
                            // The typical pattern is one McpServer instance connects to one transport instance.
                            // For multiple HTTP clients, each would ideally get its own McpServer pipeline.
                            // Or, a more complex transport layer is needed.
                            // For now, let's assume a single server instance for simplicity in this file.
                            // This part needs careful thought based on JS SDK patterns.
                            // await server.connect(transport); // This might be problematic if server is already connected.
                        }
                        // return transport.handleRequest(req); // handleRequest expects specific parameters
                        // A more complete implementation is needed here based on how StreamableHTTPServerTransport integrates.
                        return new Response("MCP Endpoint. Correct handling pending.", { status: 200 });
                    }
                    return new Response("Not Found", { status: 404 });
                },
                error(error) {
                    console.error("Bun server error:", error);
                    return new Response("Internal Server Error", { status: 500 });
                },
            });
            console.info(`MCP Server potentially available via HTTP on port ${port}/mcp`);
            // Note: McpServer.connect for SSE might need a different approach or a dedicated SSE transport if not using StreamableHTTP.
            // The Python server's "sse" likely used a specific MCP library feature for it.
            // The JS SDK focuses on StdioServerTransport and StreamableHTTPServerTransport.
            // For a true SSE (not full StreamableHTTP), custom logic or a simpler transport would be needed.
        } else {
            console.error(`Unsupported transport: ${transportChoice}`);
            process.exit(1);
        }
    } catch (error) {
        if (error instanceof Error && error.message.includes("EADDRINUSE")) {
            console.error(`Port ${port} is already in use.`);
        } else if (error instanceof Error) {
            console.error(`Error running server: ${error.message}`);
            console.error(error.stack);
        } else {
            console.error(`An unknown error occurred: ${error}`);
        }
        process.exit(1);
    }
}

// Placeholder for where tools, resources, prompts would be registered
// function importAndRegisterTools(server: McpServer, config: Config) { /* ... */ }
// function importAndRegisterResources(server: McpServer, config: Config) { /* ... */ }
// function importAndRegisterPrompts(server: McpServer, config: Config) { /* ... */ }

// This file exports createServer and runServer.
// The main entry point (e.g., src/index.ts) will use these.
// It doesn't run the server directly.
// Example of how it might be used in index.ts:
//
// import { createServer, runServer } from './server/server';
// import { loadConfig } from './utils/config';
//
// async function main() {
//   const config = loadConfig(); // Load environment variables or other config sources
//   const server = createServer(config);
//
//   const transport = process.env.MCP_TRANSPORT || "stdio";
//   const port = process.env.MCP_PORT ? parseInt(process.env.MCP_PORT) : 8080;
//
//   await runServer(server, transport, port);
// }
//
// main().catch(error => {
//   console.error("Failed to start server:", error);
//   process.exit(1);
// });
//
// process.on('SIGINT', () => {
//   console.info("Server shutting down...");
//   // Perform any cleanup here
//   process.exit(0);
// });
//
console.log("src/server/server.ts loaded");
