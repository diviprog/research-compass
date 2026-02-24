/**
 * API base URL for backend requests. Set VITE_API_URL in .env.local (local) or Vercel env (production).
 */
const rawUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_BASE_URL = rawUrl.replace(/^http:\/\/(?!localhost)/, 'https://');
