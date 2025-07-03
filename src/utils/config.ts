import { z } from 'zod';

// Define a schema for environment variables for validation and type safety
const envSchema = z.object({
    NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
    SERVER_NAME: z.string().default('mcp-paradex-ts'),
    SERVER_PORT: z.preprocess(
        (val) => (typeof val === 'string' ? parseInt(val, 10) : val),
        z.number().int().positive().default(8080)
    ),
    PARADEX_ENVIRONMENT: z.enum(['testnet', 'mainnet']).default('testnet'),
    // Optional: L1_ADDRESS and L1_PRIVATE_KEY were in Python config but might not be directly used by paradex/sdk
    // PARADEX_L1_ADDRESS: z.string().optional(),
    // PARADEX_L1_PRIVATE_KEY: z.string().optional(), // Be careful with exposing private keys
    PARADEX_ACCOUNT_PRIVATE_KEY: z.string().optional(), // For authenticated endpoints
    LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
});

export type Config = z.infer<typeof envSchema>;

let loadedConfig: Config;

export function loadConfig(): Config {
    if (loadedConfig) {
        return loadedConfig;
    }

    const parsedEnv = envSchema.safeParse(process.env);

    if (!parsedEnv.success) {
        console.error('❌ Invalid environment variables:', parsedEnv.error.format());
        // Output details for each error
        for (const issue of parsedEnv.error.issues) {
            console.error(`  - ${issue.path.join('.')}: ${issue.message}`);
        }
        throw new Error('Invalid environment variables. Check console for details.');
    }

    loadedConfig = parsedEnv.data;

    // Set global log level (simple version)
    // A more sophisticated logger would handle this better
    // console.log(`Log level set to: ${loadedConfig.LOG_LEVEL}`); // Example

    return loadedConfig;
}

// Load config on import to make it available immediately
// This also means it will throw an error on import if config is invalid.
try {
    loadedConfig = loadConfig();
    console.log("Configuration loaded successfully.");
    // console.log("Paradex Environment:", loadedConfig.PARADEX_ENVIRONMENT);
    // console.log("Server Port:", loadedConfig.SERVER_PORT);
} catch (error) {
    console.error("Failed to load configuration during module initialization:", error);
    // Depending on the application's needs, you might want to exit here
    // or allow the application to attempt to run with default/partial config.
    // For a server, exiting is often safer.
    process.exit(1);
}

export const config: Config = loadedConfig;

console.log("src/utils/config.ts loaded");
