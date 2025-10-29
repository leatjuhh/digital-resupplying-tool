/**
 * API Client for Digital Resupplying Tool
 * Connects Next.js frontend with FastAPI backend
 */

// Base URL van de FastAPI backend (localhost tijdens development)
const API_BASE_URL = 'http://localhost:8000';

/**
 * PDF Batch interface
 */
export interface PDFBatch {
  id: number;
  naam: string;
  status: string;
  pdf_count: number;
  processed_count: number;
  created_at: string;
}

/**
 * Proposal interface
 */
export interface Proposal {
  id: number;
  artikelnummer: string;
  article_name: string;
  total_moves: number;
  total_quantity: number;
  status: 'pending' | 'approved' | 'rejected' | 'edited';
  reason: string;
  applied_rules: string[];
  optimization_applied: string;
  stores_affected: string[];
  created_at: string | null;
  reviewed_at: string | null;
  moves: ProposalMove[];
}

/**
 * Proposal Move interface
 */
export interface ProposalMove {
  size: string;
  from_store: string;
  from_store_name: string;
  to_store: string;
  to_store_name: string;
  qty: number;
  score: number;
  reason: string;
  from_bv: string;
  to_bv: string;
}

/**
 * Batch with proposals
 */
export interface BatchWithProposals extends PDFBatch {
  total_proposals: number;
  status_counts: {
    pending: number;
    approved: number;
    rejected: number;
    edited: number;
  };
  proposals: Proposal[];
}

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
   * Batch/Reeks endpoints (oude systeem)
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

  /**
   * PDF Batch endpoints (nieuw systeem)
   */
  pdf: {
    /**
     * Haal alle PDF batches op
     */
    async getBatches() {
      return fetchAPI<PDFBatch[]>('/api/pdf/batches');
    },

    /**
     * Haal specifieke PDF batch op met details
     */
    async getBatchById(id: number) {
      return fetchAPI<any>(`/api/pdf/batches/${id}`);
    },

    /**
     * Haal alle proposals voor een batch op
     */
    async getBatchProposals(batchId: number) {
      return fetchAPI<BatchWithProposals>(`/api/pdf/batches/${batchId}/proposals`);
    },

    /**
     * Upload PDF files
     */
    async uploadPDFs(files: File[], batchName?: string) {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      if (batchName) {
        formData.append('batch_name', batchName);
      }

      const response = await fetch(`${API_BASE_URL}/api/pdf/ingest`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      return response.json();
    },
  },

  /**
   * Proposal endpoints
   */
  proposals: {
    /**
     * Haal specifieke proposal op
     */
    async getById(proposalId: number) {
      return fetchAPI<Proposal>(`/api/pdf/proposals/${proposalId}`);
    },

    /**
     * Haal specifieke proposal op met volledige voorraad data
     */
    async getByIdFull(proposalId: number) {
      return fetchAPI<any>(`/api/pdf/proposals/${proposalId}/full`);
    },

    /**
     * Keur een proposal goed
     */
    async approve(proposalId: number) {
      const response = await fetch(`${API_BASE_URL}/api/pdf/proposals/${proposalId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Approve failed: ${response.status}`);
      }

      return response.json();
    },

    /**
     * Keur een proposal af
     */
    async reject(proposalId: number, reason?: string) {
      const response = await fetch(`${API_BASE_URL}/api/pdf/proposals/${proposalId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason }),
      });

      if (!response.ok) {
        throw new Error(`Reject failed: ${response.status}`);
      }

      return response.json();
    },

    /**
     * Update een proposal met aangepaste moves
     */
    async update(proposalId: number, moves: ProposalMove[]) {
      const response = await fetch(`${API_BASE_URL}/api/pdf/proposals/${proposalId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ moves }),
      });

      if (!response.ok) {
        throw new Error(`Update failed: ${response.status}`);
      }

      return response.json();
    },
  },
};
