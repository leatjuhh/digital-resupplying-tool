/**
 * Token Storage Utility
 * Manages secure storage of authentication tokens and user data
 */

import { User } from '@/types/auth';

// Storage keys
const ACCESS_TOKEN_KEY = 'drt_access_token';
const REFRESH_TOKEN_KEY = 'drt_refresh_token';
const USER_KEY = 'drt_user';
const REMEMBER_ME_KEY = 'drt_remember_me';

/**
 * Token Storage Interface
 * Provides methods for storing and retrieving authentication data
 */
export const tokenStorage = {
  /**
   * Get storage type based on remember me preference
   * Returns localStorage if remember me is true, sessionStorage otherwise
   */
  getStorage: (rememberMe: boolean = false): Storage => {
    // Check if we're in a browser environment
    if (typeof window === 'undefined') {
      // Return a mock storage for SSR
      return {
        getItem: () => null,
        setItem: () => {},
        removeItem: () => {},
        clear: () => {},
        key: () => null,
        length: 0
      } as Storage;
    }

    const remembered = rememberMe || localStorage.getItem(REMEMBER_ME_KEY) === 'true';
    return remembered ? localStorage : sessionStorage;
  },

  /**
   * Save authentication tokens
   */
  setTokens: (accessToken: string, refreshToken: string, rememberMe: boolean = false): void => {
    if (typeof window === 'undefined') return;

    try {
      const storage = tokenStorage.getStorage(rememberMe);
      storage.setItem(ACCESS_TOKEN_KEY, accessToken);
      storage.setItem(REFRESH_TOKEN_KEY, refreshToken);
      localStorage.setItem(REMEMBER_ME_KEY, rememberMe.toString());
    } catch (error) {
      console.error('Failed to save tokens:', error);
    }
  },

  /**
   * Get access token from storage
   */
  getAccessToken: (): string | null => {
    if (typeof window === 'undefined') return null;

    try {
      return localStorage.getItem(ACCESS_TOKEN_KEY) || sessionStorage.getItem(ACCESS_TOKEN_KEY);
    } catch (error) {
      console.error('Failed to get access token:', error);
      return null;
    }
  },

  /**
   * Get refresh token from storage
   */
  getRefreshToken: (): string | null => {
    if (typeof window === 'undefined') return null;

    try {
      return localStorage.getItem(REFRESH_TOKEN_KEY) || sessionStorage.getItem(REFRESH_TOKEN_KEY);
    } catch (error) {
      console.error('Failed to get refresh token:', error);
      return null;
    }
  },

  /**
   * Save user data
   */
  setUser: (user: User): void => {
    if (typeof window === 'undefined') return;

    try {
      const storage = tokenStorage.getStorage();
      storage.setItem(USER_KEY, JSON.stringify(user));
    } catch (error) {
      console.error('Failed to save user:', error);
    }
  },

  /**
   * Get user data from storage
   */
  getUser: (): User | null => {
    if (typeof window === 'undefined') return null;

    try {
      const userStr = localStorage.getItem(USER_KEY) || sessionStorage.getItem(USER_KEY);
      if (!userStr) return null;
      return JSON.parse(userStr) as User;
    } catch (error) {
      console.error('Failed to get user:', error);
      return null;
    }
  },

  /**
   * Check if remember me is enabled
   */
  isRememberMe: (): boolean => {
    if (typeof window === 'undefined') return false;
    return localStorage.getItem(REMEMBER_ME_KEY) === 'true';
  },

  /**
   * Clear all authentication data
   */
  clear: (): void => {
    if (typeof window === 'undefined') return;

    try {
      // Clear from both storages to be sure
      [localStorage, sessionStorage].forEach(storage => {
        storage.removeItem(ACCESS_TOKEN_KEY);
        storage.removeItem(REFRESH_TOKEN_KEY);
        storage.removeItem(USER_KEY);
      });
      localStorage.removeItem(REMEMBER_ME_KEY);
    } catch (error) {
      console.error('Failed to clear tokens:', error);
    }
  }
};
