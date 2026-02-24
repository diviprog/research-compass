/**
 * API base URL for backend requests. Set VITE_API_URL in .env.local (local) or Vercel env (production).
 */
const rawBase = (import.meta.env.VITE_API_URL as string | undefined) || 'http://localhost:8000';
const withoutTrailingSlash = rawBase.replace(/\/$/, '');

export const API_BASE_URL =
  !withoutTrailingSlash.includes('localhost') && withoutTrailingSlash.startsWith('http://')
    ? withoutTrailingSlash.replace(/^http:\/\//, 'https://')
    : withoutTrailingSlash;
