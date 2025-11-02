/**
 * Enhanced API Client with 401 Detection
 * Wraps fetch with automatic token refresh on 401 responses
 */

import { tokenStorage } from './token-storage';

// Use environment variable for API URL, fallback to localhost
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
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
          });
          
          if (!retryResponse.ok && retryResponse.status !== 401) {
            throw new Error(`API Error: ${retryResponse.status}`);
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

    return response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
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
