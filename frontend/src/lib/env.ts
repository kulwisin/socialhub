const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const META_APP_ID = process.env.NEXT_PUBLIC_META_APP_ID ?? "";

export const env = {
  API_URL,
  META_APP_ID,
} as const;
