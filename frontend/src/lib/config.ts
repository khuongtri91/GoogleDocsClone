const requiredEnv = (name: string): string => {
  const value = import.meta.env[name];

  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }

  return value;
};

export const config = {
  apiBaseUrl: requiredEnv("VITE_API_BASE_URL"),
  supabaseUrl: requiredEnv("VITE_SUPABASE_URL"),
  supabasePublishableKey: requiredEnv("VITE_SUPABASE_PUBLISHABLE_KEY"),
};
