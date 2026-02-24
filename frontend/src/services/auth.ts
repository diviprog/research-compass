/**
 * Authentication service for API calls and token management.
 */

import axios, { AxiosError } from 'axios';
import { API_BASE_URL } from '../lib/apiBase';

export interface SignUpData {
  email: string;
  password: string;
  name: string;
}

export interface SignInData {
  email: string;
  password: string;
}

export interface UserData {
  user_id: number;
  email: string;
  name: string;
  created_at: string;
}

export interface AuthResponse {
  user: UserData;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthError {
  detail: string;
}

/**
 * Token storage utilities
 */
export const TokenStorage = {
  setAccessToken: (token: string) => {
    localStorage.setItem('access_token', token);
  },
  
  getAccessToken: (): string | null => {
    return localStorage.getItem('access_token');
  },
  
  setRefreshToken: (token: string) => {
    localStorage.setItem('refresh_token', token);
  },
  
  getRefreshToken: (): string | null => {
    return localStorage.getItem('refresh_token');
  },
  
  setUser: (user: UserData) => {
    localStorage.setItem('user', JSON.stringify(user));
  },
  
  getUser: (): UserData | null => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
  
  clearAll: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }
};

/**
 * Create axios instance with interceptors for automatic token refresh
 */
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: add auth token; for FormData, drop Content-Type so browser sets multipart boundary
api.interceptors.request.use(
  (config) => {
    const token = TokenStorage.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<AuthError>) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && originalRequest && !originalRequest.headers['X-Retry']) {
      const refreshToken = TokenStorage.getRefreshToken();
      
      if (refreshToken) {
        try {
          // Try to refresh the token
          const response = await axios.post<TokenPair>(
            `${API_BASE_URL}/api/auth/refresh`,
            { refresh_token: refreshToken }
          );
          
          const { access_token, refresh_token } = response.data;
          
          // Store new tokens
          TokenStorage.setAccessToken(access_token);
          TokenStorage.setRefreshToken(refresh_token);
          
          // Retry the original request with new token
          originalRequest.headers['X-Retry'] = 'true';
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect to login
          TokenStorage.clearAll();
          window.location.href = '/signin';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        TokenStorage.clearAll();
        window.location.href = '/signin';
      }
    }
    
    return Promise.reject(error);
  }
);

/**
 * Auth API service
 */
export const AuthService = {
  /**
   * Sign up a new user
   */
  async signUp(data: SignUpData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/signup', data);
    const authData = response.data;
    
    // Store tokens and user data
    TokenStorage.setAccessToken(authData.access_token);
    TokenStorage.setRefreshToken(authData.refresh_token);
    TokenStorage.setUser(authData.user);
    
    return authData;
  },
  
  /**
   * Sign in an existing user
   */
  async signIn(data: SignInData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/signin', data);
    const authData = response.data;
    
    // Store tokens and user data
    TokenStorage.setAccessToken(authData.access_token);
    TokenStorage.setRefreshToken(authData.refresh_token);
    TokenStorage.setUser(authData.user);
    
    return authData;
  },
  
  /**
   * Refresh access token
   */
  async refreshToken(): Promise<TokenPair> {
    const refreshToken = TokenStorage.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    const response = await api.post<TokenPair>('/auth/refresh', {
      refresh_token: refreshToken
    });
    
    const tokens = response.data;
    TokenStorage.setAccessToken(tokens.access_token);
    TokenStorage.setRefreshToken(tokens.refresh_token);
    
    return tokens;
  },
  
  /**
   * Log out the current user
   */
  async logout(): Promise<void> {
    const refreshToken = TokenStorage.getRefreshToken();
    if (refreshToken) {
      try {
        await api.post('/auth/logout', { refresh_token: refreshToken });
      } catch (error) {
        console.error('Logout API call failed:', error);
      }
    }
    TokenStorage.clearAll();
  },
  
  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<UserData> {
    const response = await api.get<UserData>('/auth/me');
    TokenStorage.setUser(response.data);
    return response.data;
  },
  
  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!TokenStorage.getAccessToken();
  }
};

export default api;

