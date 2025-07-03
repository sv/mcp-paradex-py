import { McpServer, McpRequest } from "@modelcontextprotocol/sdk/server";
import { z } from "zod";
import { getAuthenticatedParadexClient, apiCall } from "../utils/paradex-client";
import { Config } from "../utils/config";
import {
    AccountSummarySchema, AccountSummary,
    PositionSchema, PositionArraySchema, Position,
    FillSchema, FillArraySchema, Fill,
    TransactionSchema, TransactionArraySchema, Transaction
} from "../models/account"; // Zod schemas

export function registerAccountTools(server: McpServer, config: Config) {

    server.registerTool(
        "paradex_account_summary",
        {
            title: "Get Account Summary",
            description: "Get a snapshot of your account's current financial status and trading capacity. Use to check balance, margin, account health, and P&L.",
            inputSchema: {}, // No input parameters
        },
        async (_params: {}, mcpContext?: McpRequest) => {
            try {
                const client = await getAuthenticatedParadexClient();
                // Python used: await api_call(client, "account")
                // The JS SDK might have a dedicated method like `client.getAccountSummary()` or `client.account.getSummary()`
                // Or it might indeed be a generic call to an "/account" endpoint.

                // Assuming a dedicated method or a well-defined response from a generic GET /account
                const response = await client.getAccount?.() ?? await (client as any).getAccountSummary?.() ?? await apiCall(client, 'GET', 'account');

                if (!response) {
                    throw new Error("Failed to fetch account summary: SDK method returned no response.");
                }

                const accountSummary = AccountSummarySchema.parse(response); // Assuming response is the summary object

                return {
                    content: [{
                        type: "json",
                        json: {
                            description: AccountSummarySchema.description || "Account financial status and trading capacity.",
                            fields: AccountSummarySchema.openapi("AccountSummary"),
                            results: accountSummary,
                        }
                    }]
                };
            } catch (error: any) {
                console.error("Error in paradex_account_summary tool:", error);
                // mcpContext?.error(error.message || "Failed to get account summary"); // If MCP context supports error reporting
                throw error; // Let McpServer handle/wrap
            }
        }
    );

    server.registerTool(
        "paradex_account_positions",
        {
            title: "Get Account Positions",
            description: "Analyze your open positions to monitor exposure, profitability, and risk. Use to check P&L, liquidation prices, and margin requirements.",
            inputSchema: {}, // No input parameters
        },
        async (_params: {}, mcpContext?: McpRequest) => {
            try {
                const client = await getAuthenticatedParadexClient();
                // Python used: client.fetch_positions()
                // JS SDK equivalent: client.getPositions() or client.account.getPositions()
                const response = await client.getPositions?.() ?? await (client as any).account?.getPositions?.();

                if (!response) {
                    throw new Error("Failed to fetch account positions: SDK method returned no response.");
                }

                let positions: Position[];
                if (Array.isArray(response)) {
                    positions = PositionArraySchema.parse(response);
                } else if (response && Array.isArray((response as any).results)) { // Common API pattern
                    positions = PositionArraySchema.parse((response as any).results);
                } else {
                    console.error("Unexpected response structure from positions endpoint:", response);
                    throw new Error("Failed to parse account positions.");
                }

                return {
                    content: [{
                        type: "json",
                        json: {
                            description: PositionSchema.description || "Current open positions.",
                            fields: PositionSchema.openapi("Position"), // Schema for a single position
                            results: positions, // Array of positions
                        }
                    }]
                };
            } catch (error: any) {
                console.error("Error in paradex_account_positions tool:", error);
                throw error;
            }
        }
    );

    server.registerTool(
        "paradex_account_fills",
        {
            title: "Get Account Fills (Trade History)",
            description: "Analyze your executed trades (fills) to evaluate performance and execution quality. Use to review trading history, calculate average entry prices, and track P&L.",
            inputSchema: {
                market_id: z.string().describe("Filter by market ID (e.g., 'BTC-PERP')."),
                start_unix_ms: z.number().int().describe("Start time in Unix milliseconds."),
                end_unix_ms: z.number().int().describe("End time in Unix milliseconds."),
                // Optional: Add limit, order_id, etc. if supported by API/SDK
            }
        },
        async (params: { market_id: string, start_unix_ms: number, end_unix_ms: number }, mcpContext?: McpRequest) => {
            try {
                const client = await getAuthenticatedParadexClient();
                // Python used: client.fetch_fills(params)
                // JS SDK: client.getFills({ market, startTime, endTime }) or client.account.getFills(...)
                const apiParams = {
                    symbol: params.market_id, // Or 'market'
                    startTime: params.start_unix_ms,
                    endTime: params.end_unix_ms,
                };
                const response = await client.getFills?.(apiParams) ?? await (client as any).account?.getFills?.(apiParams);

                if (!response) {
                    throw new Error("Failed to fetch account fills: SDK method returned no response.");
                }

                let fills: Fill[];
                 if (Array.isArray(response)) {
                    fills = FillArraySchema.parse(response);
                } else if (response && Array.isArray((response as any).results)) {
                    fills = FillArraySchema.parse((response as any).results);
                } else {
                    console.error("Unexpected response structure from fills endpoint:", response);
                    throw new Error("Failed to parse account fills.");
                }

                return {
                    content: [{
                        type: "json",
                        json: {
                            description: FillSchema.description || "Executed trades (fills).",
                            fields: FillSchema.openapi("Fill"),
                            results: fills,
                        }
                    }]
                };
            } catch (error: any) {
                console.error(`Error in paradex_account_fills tool for market ${params.market_id}:`, error);
                throw error;
            }
        }
    );

    server.registerTool(
        "paradex_account_funding_payments",
        {
            title: "Get Account Funding Payments",
            description: "Track your funding payment history to understand its impact on P&L. Funding payments can significantly impact perpetual futures trading P&L.",
            inputSchema: {
                market_id: z.string().optional().describe("Filter by market ID (e.g., 'BTC-PERP'). If omitted, might fetch for all markets or require one."),
                start_unix_ms: z.number().int().describe("Start time in Unix milliseconds."),
                end_unix_ms: z.number().int().describe("End time in Unix milliseconds."),
            }
        },
        async (params: { market_id?: string, start_unix_ms: number, end_unix_ms: number }, mcpContext?: McpRequest) => {
            try {
                const client = await getAuthenticatedParadexClient();
                // Python used: client.fetch_funding_payments(params)
                // JS SDK: client.getFundingPayments({ market, startTime, endTime })
                const apiParams: Record<string, any> = {
                    startTime: params.start_unix_ms,
                    endTime: params.end_unix_ms,
                };
                if (params.market_id) {
                    apiParams.symbol = params.market_id; // or 'market'
                }

                const response = await client.getFundingPayments?.(apiParams) ?? await (client as any).account?.getFundingPayments?.(apiParams);

                if (!response) {
                    throw new Error("Failed to fetch funding payments: SDK method returned no response.");
                }

                // Funding payments data structure needs to be defined, assuming it's an array of objects.
                // Let's assume it might return a generic list of transactions or specific funding payment objects.
                // For now, returning raw response if no specific Zod schema is defined for it yet.
                // If TransactionSchema is applicable:
                // const fundingPayments = TransactionArraySchema.parse(response.results || response);

                // The Python response was returned directly. Let's assume the response is an array of suitable objects.
                // If not, a specific Zod schema for FundingPayment would be needed.
                // For now, let's assume it's parseable by a generic array schema or we return it as raw json.
                // If `TransactionSchema` is suitable (e.g. funding payments are a type of transaction):
                let fundingPayments;
                if (Array.isArray(response)) {
                    fundingPayments = z.array(z.any()).parse(response); // General array
                } else if (response && Array.isArray((response as any).results)) {
                    fundingPayments = z.array(z.any()).parse((response as any).results);
                } else {
                     throw new Error("Unexpected funding payments response structure.");
                }


                return {
                    content: [{
                        type: "json",
                        json: {
                            description: "History of funding payments.",
                            // fields: FundingPaymentSchema.openapi("FundingPayment"), // If a specific schema exists
                            results: fundingPayments, // This might need a specific Zod schema
                        }
                    }]
                };
            } catch (error: any) {
                console.error(`Error in paradex_account_funding_payments tool:`, error);
                throw error;
            }
        }
    );

    server.registerTool(
        "paradex_account_transactions",
        {
            title: "Get Account Transactions",
            description: "Get account transaction history, including deposits, withdrawals, trades, funding, etc. Filter by type and time.",
            inputSchema: {
                transaction_type: z.string().optional().describe("Filter by transaction type (e.g., 'DEPOSIT', 'WITHDRAWAL')."),
                start_unix_ms: z.number().int().describe("Start time in Unix milliseconds."),
                end_unix_ms: z.number().int().describe("End time in Unix milliseconds."),
                limit: z.number().int().positive().max(1000).default(50).describe("Maximum number of transactions to return (e.g., 50). Max 1000."), // Max based on Python, adjust if different
            }
        },
        async (params: { transaction_type?: string, start_unix_ms: number, end_unix_ms: number, limit?: number }, mcpContext?: McpRequest) => {
            try {
                const client = await getAuthenticatedParadexClient();
                // Python used: client.fetch_transactions(params)
                // JS SDK: client.getTransactions({ type, startTime, endTime, limit })
                const apiParams: Record<string, any> = {
                    startTime: params.start_unix_ms,
                    endTime: params.end_unix_ms,
                    limit: params.limit || 50,
                };
                if (params.transaction_type) {
                    apiParams.type = params.transaction_type;
                }

                const response = await client.getTransactions?.(apiParams) ?? await (client as any).account?.getTransactions?.(apiParams);

                if (!response) {
                    throw new Error("Failed to fetch account transactions: SDK method returned no response.");
                }

                let transactions: Transaction[];
                if (Array.isArray(response)) {
                    transactions = TransactionArraySchema.parse(response);
                } else if (response && Array.isArray((response as any).results)) {
                    transactions = TransactionArraySchema.parse((response as any).results);
                } else {
                    console.error("Unexpected response structure from transactions endpoint:", response);
                    throw new Error("Failed to parse account transactions.");
                }

                return {
                    content: [{
                        type: "json",
                        json: {
                            description: TransactionSchema.description || "Account transaction history.",
                            fields: TransactionSchema.openapi("Transaction"),
                            results: transactions,
                        }
                    }]
                };
            } catch (error: any) {
                console.error(`Error in paradex_account_transactions tool:`, error);
                throw error;
            }
        }
    );

    console.log("All account tools registered.");
}

console.log("src/tools/account.ts loaded");

// Note:
// - Authentication is critical here: `getAuthenticatedParadexClient()` is used.
// - SDK method names like `client.getAccount()`, `client.getPositions()` are assumptions.
//   These need to be verified against the actual `@paradex/sdk` documentation or typings.
// - The structure of the response from these SDK methods is also assumed to align with Zod schemas.
//   Adjust parsing (e.g., `response.results`) as needed.
// - Error handling: Similar to market tools, throwing errors for McpServer to handle.
// - Return structure for MCP: `content: [{ type: "json", json: { description, fields, results } }]`
//   is kept consistent with the pattern established for market tools.
// - `openapi("SchemaName")` on Zod schemas is used to provide schema metadata.
//   The actual "SchemaName" might need to be adjusted based on how it's consumed or displayed.
/* Example of how this might be integrated into src/server/server.ts:
import { registerAccountTools } from "../tools/account";
// ...
export function createServer(config: Config): McpServer {
    // ... server creation ...
    registerMarketTools(server, config);
    registerAccountTools(server, config); // Add this line
    // ... register other tools ...
    return server;
}
*/
/* And ensure the import is at the top of src/server/server.ts:
import { registerMarketTools } from "../tools/market";
import { registerAccountTools } from "../tools/account"; // Add this line
*/
