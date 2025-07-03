import { createServer, runServer } from './server/server';
import { config, loadConfig } from './utils/config';
import { McpServer } from '@modelcontextprotocol/sdk/server';

// Import tools and resources to ensure they are registered
// This will be done by importing their respective modules which should call server.registerTool/Resource
// For example:
// import './tools/account';
// import './tools/market';
// import './resources/market';
// import './resources/system';
// etc.

// These imports will be added as we create the tool/resource files.
// For now, the registration will happen inside createServer or dedicated functions called by it.

async function main() {
  // Configuration is loaded when config.ts is imported, but explicitly calling it ensures clarity.
  const appConfig = loadConfig(); // or just use the exported 'config' object

  const serverInstance: McpServer = createServer(appConfig);

  // Register tools and resources by importing their modules
  // This is a common pattern: module side effects register things.
  // Ensure these files exist and correctly register with the serverInstance passed or a global one.
  // For now, assuming createServer handles initial registration or we'll do it explicitly.
  // Example (if createServer doesn't handle it, and assuming a way to pass serverInstance or use a global singleton):
  // await import('./tools/accountTools').then(module => module.register(serverInstance, appConfig));
  // await import('./tools/marketTools').then(module => module.register(serverInstance, appConfig));
  // await import('./resources/marketResources').then(module => module.register(serverInstance, appConfig));
  // await import('./resources/systemResources').then(module => module.register(serverInstance, appConfig));

  // The actual registration of tools/resources will be handled in their respective files
  // or a central registration function called within `createServer`.
  // For now, let's assume `createServer` wires up the basics or we will iterate.

  const transport = appConfig.NODE_ENV === 'production' ? 'sse' : (process.env.MCP_TRANSPORT || "stdio");
  const port = appConfig.SERVER_PORT;

  console.log(`Using transport: ${transport}, Port: ${port} (if applicable)`);

  await runServer(serverInstance, transport, port);
}

main().catch(error => {
  console.error("Failed to start server:", error);
  process.exit(1);
});

process.on('SIGINT', () => {
  console.info("\nSIGINT received. Shutting down MCP Paradex server...");
  // Perform any cleanup here if necessary
  // e.g., server.close();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.info("\nSIGTERM received. Shutting down MCP Paradex server...");
  // Perform any cleanup here if necessary
  process.exit(0);
});

console.log("src/index.ts loaded");
