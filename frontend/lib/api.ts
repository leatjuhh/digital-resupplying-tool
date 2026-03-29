/**
 * API Client for Digital Resupplying Tool
 * Connects Next.js frontend with FastAPI backend
 */

import { User, LoginCredentials, TokenResponse } from '@/types/auth';
import { apiClient } from '@/lib/api-client';

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

export interface AssignmentSizeQuantity {
  size: string;
  qty: number;
}

export interface AssignmentSeriesSummary {
  id: number;
  batch_id: number;
  batch_name: string;
  store_code: string;
  store_name: string;
  description: string;
  count: number;
  completed: number;
  failed: number;
  pending: number;
  status: 'open' | 'in_progress' | 'attention' | 'completed';
  created_at: string | null;
  updated_at: string | null;
}

export interface AssignmentItemSummary {
  id: number;
  proposal_id: number;
  artikelnummer: string;
  article_name: string;
  from_store_code: string;
  from_store_name: string;
  to_store_code: string;
  to_store_name: string;
  size_quantities: AssignmentSizeQuantity[];
  total_quantity: number;
  status: 'open' | 'completed' | 'failed';
  failure_reason?: string | null;
  failure_size?: string | null;
  failure_notes?: string | null;
  completed_at?: string | null;
}

export interface AssignmentSeriesDetail extends AssignmentSeriesSummary {
  items: AssignmentItemSummary[];
}

export interface AssignmentItemDetail {
  assignment_id: number;
  proposal_id: number;
  batch_id: number;
  artikelnummer: string;
  article_name: string;
  status: 'open' | 'completed' | 'failed';
  size_quantities: AssignmentSizeQuantity[];
  total_quantity: number;
  failure_reason?: string | null;
  failure_size?: string | null;
  failure_notes?: string | null;
  metadata: Record<string, string>;
  sizes: string[];
  stores: Array<{
    id: string;
    name: string;
    inventory_current: number[];
    inventory_proposed: number[];
    sold: number;
  }>;
  from_store_code: string;
  from_store_name: string;
  to_store_code: string;
  to_store_name: string;
  completed_at?: string | null;
}

export interface DashboardStatsSummary {
  total_proposals: number;
  pending_proposals: number;
  approved_proposals: number;
  rejected_proposals: number;
  edited_proposals: number;
  open_assignment_items: number;
  completed_assignment_items: number;
  failed_assignment_items: number;
  active_store_count: number;
  total_batches: number;
  assignment_series_count: number;
}

export interface DashboardPendingBatch {
  batch_id: number;
  batch_name: string;
  created_at: string | null;
  total_proposals: number;
  pending_proposals: number;
  reviewed_proposals: number;
  next_proposal_id: number | null;
}

export interface DashboardEvent {
  id: string;
  kind: "proposal" | "batch" | "assignment" | "parse_log";
  title: string;
  description: string;
  created_at: string | null;
  href: string | null;
}

export interface DashboardAttentionItem {
  id: string;
  severity: "info" | "warning";
  title: string;
  description: string;
  href: string | null;
}

export interface DashboardSummary {
  generated_at: string | null;
  period_note: string;
  stats: DashboardStatsSummary;
  pending_batches: DashboardPendingBatch[];
  recent_activity: DashboardEvent[];
  attention_items: DashboardAttentionItem[];
}

export interface GeneralSettings {
  app_name: string;
  language: string;
  timezone: string;
  email_notifications: boolean;
}

export interface RulesSettings {
  min_stock_per_store: number;
  max_stock_per_store: number;
  min_stores_per_article: number;
  sales_period_days: number;
}

export interface ApiKeyStatus {
  configured: boolean;
  masked_key: string | null;
  updated_at: string | null;
}

export interface SettingsUpdateResponse {
  message: string;
  updated_count: number;
  errors?: string[] | null;
}

export interface ManagedUser {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role_id: number;
  role_name: string;
  role_display_name: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
  store_code?: string | null;
  store_name?: string | null;
}

export interface UserRoleOption {
  id: number;
  name: string;
  display_name: string;
  description?: string | null;
  is_system_role: boolean;
}

export interface ManagedUserCreateInput {
  username: string;
  email: string;
  full_name: string;
  password: string;
  role_id: number;
  is_active: boolean;
  store_code?: string | null;
  store_name?: string | null;
}

export interface ManagedUserUpdateInput {
  username?: string;
  email?: string;
  full_name?: string;
  role_id?: number;
  is_active?: boolean;
  store_code?: string | null;
  store_name?: string | null;
}

export interface RolePermission {
  id: number;
  name: string;
  display_name: string;
  description?: string | null;
  category: string;
}

export interface ManagedRole {
  id: number;
  name: string;
  display_name: string;
  description?: string | null;
  is_system_role: boolean;
  permissions: RolePermission[];
  user_count: number;
  created_at: string;
}

export interface ExternalAlgorithmLineage {
  source_path: string;
  size_bytes: number;
  modified_at: string | null;
  sha256: string;
}

export interface ExternalAlgorithmWeekSummary {
  year: number;
  week: number;
  proposal_count: number;
  observed_move_count: number;
  model_opportunity_count: number;
  overlap_move_count: number;
  observed_opportunity_recall: number;
  model_overlap_ratio: number;
  lineage?: ExternalAlgorithmLineage | null;
}

export interface ExternalAlgorithmModelSummary {
  data_available: boolean;
  average_precision_test?: number | null;
  top_k_recall_test?: number | null;
  top_k_precision_test?: number | null;
  binary_precision_test?: number | null;
  binary_recall_test?: number | null;
  feature_importance: Array<{
    feature: string;
    weight: number;
    abs_weight: number;
  }>;
  lineage?: ExternalAlgorithmLineage | null;
}

export interface ExternalAlgorithmDatasetStatus {
  data_available: boolean;
  assist_mode: "off" | "shadow" | "rank_assist" | string;
  dataset_root: string;
  latest_year?: number | null;
  latest_week?: number | null;
  processed_week_count: number;
  weeks_available: ExternalAlgorithmWeekSummary[];
  aggregate_training_summary?: {
    total_example_count: number;
    total_positive_count: number;
    total_negative_count: number;
    positive_rate: number;
    weeks_included: number[];
  } | null;
  aggregate_model_summary: ExternalAlgorithmModelSummary;
  refresh_state_lineage?: ExternalAlgorithmLineage | null;
  errors: string[];
}

export interface ExternalAlgorithmMove {
  article_id: string;
  from_store: string;
  to_store: string;
  size: string;
  qty: number;
  score?: number;
}

export interface ExternalAlgorithmProposalComparison {
  available: boolean;
  proposal_id: number;
  artikelnummer: string;
  article_name: string;
  current_proposal: {
    move_count: number;
    moves: ExternalAlgorithmMove[];
  };
  matched_weeks: Array<{
    year: number;
    week: number;
  }>;
  latest_matching_week?: {
    year: number;
    week: number;
  } | null;
  comparison?: {
    year: number;
    week: number;
    article_context: {
      size_count: number;
      store_count: number;
      total_inventory: number;
      total_sales: number;
    };
    manual_observed: {
      move_count: number;
      moves: ExternalAlgorithmMove[];
    };
    baseline: {
      available: boolean;
      move_count: number;
      moves: ExternalAlgorithmMove[];
    };
    model: {
      available: boolean;
      selection_size: number;
      total_candidate_count: number;
      selected_moves: ExternalAlgorithmMove[];
      top_candidates: ExternalAlgorithmMove[];
      average_precision_test?: number | null;
      top_k_recall_test?: number | null;
    };
    drt_vs_manual: {
      overlap_count: number;
      left_only_count: number;
      right_only_count: number;
      overlap_moves: ExternalAlgorithmMove[];
      left_only_moves: ExternalAlgorithmMove[];
      right_only_moves: ExternalAlgorithmMove[];
    };
    drt_vs_baseline?: {
      overlap_count: number;
      left_only_count: number;
      right_only_count: number;
      overlap_moves: ExternalAlgorithmMove[];
      left_only_moves: ExternalAlgorithmMove[];
      right_only_moves: ExternalAlgorithmMove[];
    } | null;
    drt_vs_model?: {
      overlap_count: number;
      left_only_count: number;
      right_only_count: number;
      overlap_moves: ExternalAlgorithmMove[];
      left_only_moves: ExternalAlgorithmMove[];
      right_only_moves: ExternalAlgorithmMove[];
    } | null;
    manual_vs_model?: {
      overlap_count: number;
      left_only_count: number;
      right_only_count: number;
      overlap_moves: ExternalAlgorithmMove[];
      left_only_moves: ExternalAlgorithmMove[];
      right_only_moves: ExternalAlgorithmMove[];
    } | null;
    lineage: {
      combined?: ExternalAlgorithmLineage | null;
      baseline_proposals?: ExternalAlgorithmLineage | null;
      model_artifacts?: ExternalAlgorithmLineage | null;
    };
  } | null;
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

  assignments: {
    async list() {
      return apiClient.get<{ series: AssignmentSeriesSummary[] }>('/api/assignments');
    },

    async getSeries(seriesId: number) {
      return apiClient.get<AssignmentSeriesDetail>(`/api/assignments/${seriesId}`);
    },

    async getItem(seriesId: number, itemId: number) {
      return apiClient.get<{ series: AssignmentSeriesSummary; item: AssignmentItemDetail }>(
        `/api/assignments/${seriesId}/items/${itemId}`
      );
    },

    async complete(itemId: number, notes?: string) {
      return apiClient.post(`/api/assignments/items/${itemId}/complete`, { notes });
    },

    async fail(itemId: number, reason: string, size: string, notes?: string) {
      return apiClient.post(`/api/assignments/items/${itemId}/fail`, { reason, size, notes });
    },
  },

  dashboard: {
    async getSummary() {
      return apiClient.get<DashboardSummary>("/api/dashboard/summary");
    },
  },

  externalAlgorithm: {
    async getStatus() {
      return apiClient.get<ExternalAlgorithmDatasetStatus>("/api/algorithm-import/status");
    },

    async getWeekEvaluation(year: number, week: number) {
      return apiClient.get(`/api/algorithm-import/weeks/${year}/${week}`);
    },

    async getProposalComparison(proposalId: number) {
      return apiClient.get<ExternalAlgorithmProposalComparison>(
        `/api/algorithm-import/proposals/${proposalId}/comparison`
      );
    },
  },

  settings: {
    async getGeneral() {
      return apiClient.get<GeneralSettings>("/api/settings/general/all");
    },

    async updateGeneral(settings: GeneralSettings) {
      return apiClient.put<SettingsUpdateResponse>("/api/settings", {
        settings,
      });
    },

    async getRules() {
      return apiClient.get<RulesSettings>("/api/settings/rules/all");
    },

    async updateRules(settings: RulesSettings) {
      return apiClient.put<SettingsUpdateResponse>("/api/settings", {
        settings,
      });
    },

    async getApiKeyStatus() {
      return apiClient.get<ApiKeyStatus>("/api/settings/api/openai-key/status");
    },

    async validateApiKey(apiKey: string) {
      return apiClient.post<{ valid: boolean; message: string }>("/api/settings/validate-api-key", {
        api_key: apiKey,
      });
    },

    async updateOpenAiKey(apiKey: string) {
      return apiClient.put<{ message: string; masked_key: string }>("/api/settings/api/openai-key", {
        api_key: apiKey,
      });
    },
  },

  users: {
    async list() {
      return apiClient.get<ManagedUser[]>("/api/users");
    },

    async getRoleOptions() {
      return apiClient.get<UserRoleOption[]>("/api/users/role-options");
    },

    async create(data: ManagedUserCreateInput) {
      return apiClient.post<ManagedUser>("/api/users", data);
    },

    async update(userId: number, data: ManagedUserUpdateInput) {
      return apiClient.put<ManagedUser>(`/api/users/${userId}`, data);
    },

    async delete(userId: number) {
      return apiClient.delete<void>(`/api/users/${userId}`);
    },
  },

  roles: {
    async list() {
      return apiClient.get<ManagedRole[]>("/api/roles");
    },

    async getAllPermissions() {
      return apiClient.get<RolePermission[]>("/api/roles/permissions/all");
    },

    async updatePermissions(roleId: number, permissionIds: number[]) {
      return apiClient.put<{ message: string; role_id: number; permission_count: number }>(
        `/api/roles/${roleId}/permissions`,
        { permission_ids: permissionIds }
      );
    },
  },

  /**
   * Authentication endpoints
   */
  auth: {
    /**
     * Login met username en password
     */
    async login(credentials: LoginCredentials): Promise<TokenResponse> {
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

      return response.json();
    },

    /**
     * Refresh access token
     */
    async refresh(refreshToken: string): Promise<TokenResponse> {
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

      return response.json();
    },

    /**
     * Get current user info
     */
    async me(accessToken: string): Promise<User> {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to get user info');
      }

      return response.json();
    },

    /**
     * Logout (client-side cleanup)
     */
    async logout(accessToken: string): Promise<void> {
      try {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        });
      } catch {
        // Ignore errors, cleanup locally anyway
      }
    }
  },
};
