/**
 * API Client for Digital Resupplying Tool
 * Connects Next.js frontend with FastAPI backend
 */

// Base URL van de FastAPI backend (localhost tijdens development)
const API_BASE_URL = 'http://localhost:8000';

/**
 * Article interface matching backend model
 */
export interface Article {
  artikelnummer: string;           // Uniek artikelnummer (bijv. "ART-001")
  omschrijving: string;             // Beschrijving/naam van het artikel
  voorraad_per_winkel: Record<string, number>;  // Voorraad per winkel: {"Amsterdam": 15, ...}
}

/**
 * Batch interface matching backend model
 */
export interface Batch {
  id: number;
  name: string;
  status: string;
  pdf_count: number;
  processed_count: number;
  created_at: string;
}

/**
 * Batch with PDFs details
 */
export interface BatchWithPDFs extends Batch {
  pdfs: Array<{
    id: number;
    filename: string;
    status: string;
    uploaded_at: string;
    processed_at: string | null;
    extracted_count: number;
    error: string | null;
  }>;
}

/**
 * Generic API fetch wrapper
 */
async function fetchAPI<T>(endpoint: string): Promise<T> {
  // Bouw de volledige URL
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Voer de fetch request uit naar de backend
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Controleer of de request succesvol was
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  // Parse en return de JSON response
  return response.json();
}

/**
 * API methods
 */
export const api = {
  /**
   * Health check - controleert of de backend bereikbaar is
   */
  async healthCheck() {
    return fetchAPI<{ status: string }>('/health');
  },

  /**
   * Haal alle artikelen op uit de database
   */
  async getArticles() {
    return fetchAPI<Article[]>('/api/articles');
  },

  /**
   * Batch/Reeks endpoints
   */
  batches: {
    /**
     * Haal alle batches op (nieuwste eerst)
     */
    async getAll() {
      return fetchAPI<Batch[]>('/api/batches');
    },

    /**
     * Haal specifieke batch op met PDFs
     */
    async getById(id: number) {
      return fetchAPI<BatchWithPDFs>(`/api/batches/${id}`);
    },
  },
};
