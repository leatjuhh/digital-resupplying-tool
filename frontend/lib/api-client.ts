/**
 * Enhanced API Client with 401 Detection
 * Wraps fetch with automatic token refresh on 401 responses
 */

import { tokenStorage } from './token-storage';

// Use environment variable for API URL, fallback to localhost
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Standaard-timeout voor API-aanroepen (PR-017): voorkomt dat een hangende
// backend-request de UI oneindig laat wachten.
const DEFAULT_TIMEOUT_MS = 30000;

// Store handle401 callback globally
let handle401Callback: (() => Promise<void>) | null = null;

/**
 * Register the handle401 callback from AuthContext
 * This should be called when AuthProvider mounts
 */
export function registerHandle401(callback: () => Promise<void>) {
  handle401Callback = callback;
}

/**
 * Enhanced fetch that handles 401 responses
 */
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const accessToken = tokenStorage.getAccessToken();
  
  // Add authorization header if token exists
  const headers = new Headers(options.headers);
  if (accessToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const url = `${API_BASE_URL}${endpoint}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });

    // Handle 401 Unauthorized
    if (response.status === 401) {
      console.log('401 detected in API call, triggering handle401...');
      
      if (handle401Callback) {
        await handle401Callback();
        
        // Retry the request with new token
        const newToken = tokenStorage.getAccessToken();
        if (newToken) {
          headers.set('Authorization', `Bearer ${newToken}`);
          const retryResponse = await fetch(url, {
            ...options,
            headers,
            signal: controller.signal,
          });
          
          if (!retryResponse.ok && retryResponse.status !== 401) {
            throw new Error(`API Error: ${retryResponse.status}`);
          }

          if (retryResponse.status === 204) {
            return undefined as T;
          }

          return retryResponse.json();
        }
      }
      
      throw new Error('Unauthorized');
    }

    // Handle other errors
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API Error: ${response.status}`);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      console.error(`API call timed out na ${DEFAULT_TIMEOUT_MS}ms:`, url);
      throw new Error('De aanvraag duurde te lang (timeout).');
    }
    console.error('API call failed:', error);
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * API methods using enhanced fetch
 */
export const apiClient = {
  get: <T>(endpoint: string) => apiFetch<T>(endpoint, { method: 'GET' }),
  
  post: <T>(endpoint: string, data?: any) => 
    apiFetch<T>(endpoint, {
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data),
    }),
  
  put: <T>(endpoint: string, data: any) =>
    apiFetch<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  delete: <T>(endpoint: string) => apiFetch<T>(endpoint, { method: 'DELETE' }),
};
