/**
 * Authentication Types
 * Type definitions for the authentication system
 */

// User interface matching backend UserResponse
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role_name: string;
  role_display_name: string;
  permissions: string[];
  is_active: boolean;
  last_login: string | null;
}

// Auth state
export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Login credentials
export interface LoginCredentials {
  username: string;
  password: string;
  remember_me?: boolean;
}

// Token response from API
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Auth context type
export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: (showExpiredModal?: boolean) => void;
  refreshToken: () => Promise<boolean>;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
  handle401: () => Promise<void>;
}
