'use client';

/**
 * Authentication Context
 * Provides authentication state and methods throughout the application
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { User, AuthState, AuthContextType, LoginCredentials, TokenResponse } from '@/types/auth';
import { tokenStorage } from '@/lib/token-storage';
import { SessionExpiredModal } from '@/components/auth/session-expired-modal';
import { registerHandle401 } from '@/lib/api-client';

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// API base URL
const API_BASE_URL = 'http://localhost:8000';

/**
 * Auth Provider Component
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: true, // Start as true for initial auth check
    error: null
  });
  const [showSessionExpired, setShowSessionExpired] = useState(false);

  /**
   * Initialize authentication state from storage
   */
  const initializeAuth = useCallback(async () => {
    try {
      const accessToken = tokenStorage.getAccessToken();
      const refreshToken = tokenStorage.getRefreshToken();
      const user = tokenStorage.getUser();

      if (accessToken && user) {
        // Verify token is still valid by calling /me endpoint
        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const userData = await response.json();
            setState({
              user: userData,
              accessToken,
              refreshToken,
              isAuthenticated: true,
              isLoading: false,
              error: null
            });
            return;
          }
        } catch (error) {
          console.error('Token validation failed:', error);
        }
      }

      // No valid session found
      setState(prev => ({
        ...prev,
        isAuthenticated: false,
        isLoading: false
      }));
    } catch (error) {
      console.error('Auth initialization failed:', error);
      setState(prev => ({
        ...prev,
        isAuthenticated: false,
        isLoading: false,
        error: 'Failed to initialize authentication'
      }));
    }
  }, []);

  /**
   * Login function
   */
  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      // Prepare form data for OAuth2PasswordRequestForm
      const formData = new URLSearchParams();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await fetch(
        `${API_BASE_URL}/api/auth/login?remember_me=${credentials.remember_me || false}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: formData,
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const tokenData: TokenResponse = await response.json();

      // Get user info
      const userResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${tokenData.access_token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!userResponse.ok) {
        throw new Error('Failed to get user info');
      }

      const userData: User = await userResponse.json();

      // Store tokens and user data
      tokenStorage.setTokens(
        tokenData.access_token,
        tokenData.refresh_token,
        credentials.remember_me || false
      );
      tokenStorage.setUser(userData);

      // Update state
      setState({
        user: userData,
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });

      // Redirect to dashboard
      router.push('/');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      throw error;
    }
  }, [router]);

  /**
   * Logout function
   */
  const logout = useCallback((showExpiredModal: boolean = false) => {
    // Call logout endpoint (optional, for logging purposes)
    if (state.accessToken) {
      fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${state.accessToken}`,
          'Content-Type': 'application/json'
        }
      }).catch(() => {
        // Ignore errors, we're logging out anyway
      });
    }

    // Clear storage
    tokenStorage.clear();

    // Reset state
    setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null
    });

    // Show session expired modal if requested
    if (showExpiredModal) {
      setShowSessionExpired(true);
    } else {
      // Redirect to login
      router.push('/login');
    }
  }, [state.accessToken, router]);

  /**
   * Refresh access token
   */
  const refreshTokenFn = useCallback(async () => {
    try {
      const refreshToken = tokenStorage.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const tokenData: TokenResponse = await response.json();

      // Update tokens in storage
      const rememberMe = tokenStorage.isRememberMe();
      tokenStorage.setTokens(
        tokenData.access_token,
        tokenData.refresh_token,
        rememberMe
      );

      // Update state
      setState(prev => ({
        ...prev,
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token
      }));

      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // If refresh fails, logout user with session expired modal
      logout(true);
      return false;
    }
  }, [logout]);

  /**
   * Check if user has a specific permission
   */
  const hasPermission = useCallback((permission: string): boolean => {
    if (!state.user) return false;
    return state.user.permissions.includes(permission);
  }, [state.user]);

  /**
   * Check if user has a specific role
   */
  const hasRole = useCallback((role: string): boolean => {
    if (!state.user) return false;
    return state.user.role_name === role;
  }, [state.user]);

  /**
   * Handle 401 Unauthorized responses
   * This can be called from anywhere in the app when a 401 is detected
   */
  const handle401 = useCallback(async () => {
    console.log('401 Unauthorized detected, attempting token refresh...');
    
    // Try to refresh the token
    const refreshSuccess = await refreshTokenFn();
    
    if (!refreshSuccess) {
      // Refresh failed, show session expired modal
      logout(true);
    }
  }, [refreshTokenFn, logout]);

  /**
   * Initialize auth on mount
   */
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  /**
   * Register handle401 callback for API client
   */
  useEffect(() => {
    registerHandle401(handle401);
  }, [handle401]);

  /**
   * Set up auto token refresh (every 10 minutes)
   * Access tokens expire in 15 minutes, so refresh at 10 minutes
   */
  useEffect(() => {
    if (!state.isAuthenticated || !state.refreshToken) return;

    const refreshInterval = setInterval(() => {
      refreshTokenFn();
    }, 10 * 60 * 1000); // 10 minutes

    return () => clearInterval(refreshInterval);
  }, [state.isAuthenticated, state.refreshToken, refreshTokenFn]);

  const value: AuthContextType = {
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    error: state.error,
    login,
    logout,
    refreshToken: refreshTokenFn,
    hasPermission,
    hasRole,
    handle401
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
      <SessionExpiredModal 
        isOpen={showSessionExpired} 
        onClose={() => setShowSessionExpired(false)} 
      />
    </AuthContext.Provider>
  );
}

/**
 * Hook to use auth context
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
