/**
 * API base URL for backend requests. Set VITE_API_URL in .env.local (local) or Vercel env (production).
 */
export const API_BASE_URL =
  (import.meta.env.VITE_API_URL as string | undefined) || 'http://localhost:8000';
