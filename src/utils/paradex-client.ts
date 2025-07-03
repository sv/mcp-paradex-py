import { ParadexApiClient, ParadexAccount, Environment } from "@paradex/sdk";
import { config } from "./config"; // Assuming your config loader

let paradexApiClient: ParadexApiClient | null = null;
let clientLock = false; // Simple lock mechanism

async function initializeClient(): Promise<ParadexApiClient> {
    if (paradexApiClient) {
        return paradexApiClient;
    }

    if (clientLock) {
        // Wait for the client to be initialized by another concurrent call
        return new Promise((resolve, reject) => {
            const interval = setInterval(() => {
                if (paradexApiClient) {
                    clearInterval(interval);
                    resolve(paradexApiClient);
                }
                // Optional: Add a timeout to prevent infinite waiting
            }, 100);
        });
    }

    clientLock = true;

    try {
        console.log(`Initializing Paradex client for environment: ${config.PARADEX_ENVIRONMENT}`);
        const pdxEnv = config.PARADEX_ENVIRONMENT === 'mainnet' ? Environment.MAINNET : Environment.TESTNET;

        const client = new ParadexApiClient(pdxEnv);

        if (config.PARADEX_ACCOUNT_PRIVATE_KEY) {
            console.log("Authenticating Paradex client...");
            // The @paradex/sdk might handle system config fetching internally or require manual steps.
            // The Python version fetched system_config first, then used it to initialize ParadexAccount.
            // Let's check if ParadexAccount in JS SDK needs similar explicit config or can derive it.
            // Based on typical JS SDK patterns, it might be simpler.
            // If `client.account.login()` or similar exists and takes the private key, that would be it.
            // The v0.6.0 SDK's structure for ParadexAccount isn't immediately obvious from NPM page alone.
            // Assuming a structure like this for now, will need to verify with actual SDK usage/docs if possible.

            // The Python SDK did:
            // response = _paradex_client.fetch_system_config()
            // acc = ParadexAccount(config=response, l1_address="0x0...", l2_private_key=config.PARADEX_ACCOUNT_PRIVATE_KEY)
            // _paradex_client.init_account(acc)

            // Attempting to replicate:
            const systemConfig = await client.getSystemConfig(); // Assumes such a method exists and returns necessary config

            if (!systemConfig) {
                throw new Error("Failed to fetch system config for account initialization.");
            }

            // The JS SDK's ParadexAccount constructor or an init method might differ.
            // Placeholder for L1 address, as it was hardcoded to a zero address in the Python client
            // when only L2 private key was used. The JS SDK might not require it if L2 key is primary.
            const l1Address = "0x0000000000000000000000000000000000000000";

            // This is a guess based on the Python SDK. The actual JS SDK `ParadexAccount`
            // might take different parameters or be initialized differently.
            // For instance, it might take the ParadexApiClient instance and the private key.
            const account = new ParadexAccount(
                client, // Or systemConfig, depending on JS SDK
                l1Address,
                config.PARADEX_ACCOUNT_PRIVATE_KEY
            );
            // Then, associate this account with the client
            client.setAccount(account); // Assuming a method like this exists

            // Or, more simply, the client itself might have a login method:
            // await client.login(config.PARADEX_ACCOUNT_PRIVATE_KEY);

            console.log("Paradex client authenticated (simulated - actual method depends on SDK).");
        } else {
            console.log("Paradex client initialized without authentication (public endpoints only).");
        }

        paradexApiClient = client;
        return paradexApiClient;
    } catch (error) {
        console.error("Error initializing Paradex client:", error);
        throw error;
    } finally {
        clientLock = false;
    }
}

export async function getParadexClient(): Promise<ParadexApiClient> {
    if (!paradexApiClient) {
        return initializeClient();
    }
    return paradexApiClient;
}

export async function getAuthenticatedParadexClient(): Promise<ParadexApiClient> {
    const client = await getParadexClient();
    // The check for authentication needs to align with how @paradex/sdk indicates it.
    // This could be checking if `client.account` is set, or a specific property/method.
    if (!client.account) { // Assuming `client.account` holds the ParadexAccount instance after auth
        throw new Error("Paradex client is not authenticated. PARADEX_ACCOUNT_PRIVATE_KEY might be missing or invalid.");
    }
    return client;
}

/**
 * Make a direct API call to Paradex.
 * This is a generic wrapper. Specific methods on the client should be preferred.
 * @param method HTTP method (e.g., 'GET', 'POST')
 * @param path The API path to call (e.g., '/markets')
 * @param params Optional parameters for the API call. For GET, these are query params. For POST, this is the body.
 * @returns The response from the API call.
 */
export async function apiCall<T = any>(
    client: ParadexApiClient,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE', // Extend as needed
    path: string,
    params?: Record<string, any>
): Promise<T> {
    try {
        console.info(`Calling Paradex API: ${method} ${path} with params:`, params || {});
        // The @paradex/sdk likely has methods like client.get(path, params), client.post(path, body), etc.
        // This generic apiCall is less type-safe than using direct SDK methods if available.
        // Example:
        if (method === 'GET') {
            // Assuming a generic `request` method or specific ones like `get`, `post`.
            // The `client.get(path, params)` was from Python SDK. JS SDK might differ.
            // Let's assume a generic `client.request(method, path, params)` for now if specific ones aren't known.
            // Or, more likely, client.get(path, { params: queryParams })
            // For now, this is a placeholder for how the Python client's generic GET was used.
            // Direct SDK methods like `client.getMarkets()` should be used instead of this generic call if they exist.

            // This is a conceptual placeholder. Actual SDK usage is key.
            // For example, if client has `getPublic`, `getPrivate` methods:
            // return client.getPublic(path, params);

            // If the JS client has a generic `axios-like` interface:
            // return client.request({ method, url: path, params: (method === 'GET' ? params : undefined), data: (method !== 'GET' ? params : undefined) });

            // Given the Python client's `client.get(client.api_url, path, params)`,
            // the JS equivalent might be simpler if paths are relative to a base URL configured in the client.
            // For example: (This is a common pattern, but SDK specific)
            // const response = await (client as any)[method.toLowerCase()](path, params);
            // return response;
            throw new Error(`Generic apiCall for ${method} not fully implemented; use specific client methods or detail SDK's generic request signature.`);

        } else if (method === 'POST') {
            // const response = await client.post(path, params); // Example
            // return response;
            throw new Error(`Generic apiCall for ${method} not fully implemented.`);
        }
        // ... other methods

        // Fallback for unknown or if direct methods are preferred:
        console.warn(`apiCall: Consider using a specific client method for ${method} ${path} if available.`);
        throw new Error(`apiCall for ${method} to ${path} needs specific implementation based on @paradex/sdk capabilities.`);

    } catch (error) {
        console.error(`Error calling Paradex API ${method} ${path}:`, error);
        // Enhance error handling, e.g., parsing Paradex specific error responses
        throw error;
    }
}

console.log("src/utils/paradex-client.ts loaded");

// Note: The authentication and generic `apiCall` parts are highly dependent on the
// actual structure and methods provided by `@paradex/sdk`. The above is an
// adaptation of the Python client's logic and common JS SDK patterns.
// It will likely need adjustments once the precise SDK API is integrated.
// For instance, `ParadexAccount` instantiation and `client.setAccount()` are assumptions.
// The SDK might have `client.loginWithPrivateKey(key)` or similar.
// The generic `apiCall` is also an assumption; the SDK should provide typed methods for specific endpoints.
// For example, instead of `apiCall(client, 'GET', '/markets')`, one would ideally use `client.getMarkets()`.
// This file serves as a starting point for that encapsulation.
