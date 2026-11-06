/**
 * DisputeShield AI — Official TypeScript SDK Client
 * Generated & formatted for APIMatic and modern TypeScript environments.
 */

export interface Dispute {
  id: number;
  paypal_dispute_id: string;
  paypal_order_id?: string;
  paypal_transaction_id?: string;
  reason: string;
  status: string;
  dispute_amount: number;
  dispute_currency: string;
  dispute_life_cycle_stage?: string;
  buyer_email?: string;
  buyer_message?: string;
  agent_decision: 'AUTO_SUBMITTED' | 'DRAFT_PENDING_REVIEW' | 'ESCALATED' | 'PENDING';
  confidence_score?: number;
  evidence_strength_score?: number;
  agent_reasoning?: string;
  response_deadline?: string;
  created_at?: string;
  updated_at?: string;
}

export interface DisputeQueryParams {
  start_row?: number;
  end_row?: number;
  sort_col?: string;
  sort_dir?: 'asc' | 'desc';
  filter_tab?: 'ALL' | 'REVIEW_NEEDED' | 'AUTO_SUBMITTED' | 'RESOLVED';
  search?: string;
}

export interface DisputeListResponse {
  rows: Dispute[];
  total_count: number;
  start_row: number;
  end_row: number;
}

export interface RiskMetrics {
  current_dispute_ratio: number;
  risk_band: 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED';
  account_health_score: number;
  disputes_90d: number;
  transactions_90d: number;
  recommendations?: string[];
}

export interface AnalyticsSummary {
  total_disputes: number;
  review_needed: number;
  auto_submitted: number;
  resolved: number;
  won: number;
  capital_protected: number;
  average_confidence: number;
}

export interface SimulateWebhookRequest {
  reason?: string;
  amount?: string;
  currency?: string;
  dispute_id?: string;
  scenario_index?: number;
}

export interface SimulateWebhookResponse {
  status: string;
  event_id: string;
  dispute_id: string;
  amount: string;
  reason: string;
  scenario?: string;
  description?: string;
}

export interface ClientConfig {
  baseUrl?: string;
  apiKey?: string;
  timeoutMs?: number;
}

export class DisputeShieldClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeoutMs: number;

  constructor(config: ClientConfig = {}) {
    this.baseUrl = (config.baseUrl || 'http://localhost:8000').replace(/\/$/, '');
    this.apiKey = config.apiKey;
    this.timeoutMs = config.timeoutMs || 15000;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {}),
      ...(options.headers as Record<string, string>),
    };

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });

      if (!response.ok) {
        let errorData: any = {};
        try {
          errorData = await response.json();
        } catch (_) {}
        throw new Error(
          errorData.detail || `DisputeShield API error (${response.status}): ${response.statusText}`
        );
      }

      return (await response.json()) as T;
    } finally {
      clearTimeout(timeout);
    }
  }

  // --- Disputes API ---

  async getDisputes(params: DisputeQueryParams = {}): Promise<DisputeListResponse> {
    const query = new URLSearchParams();
    if (params.start_row !== undefined) query.set('start_row', String(params.start_row));
    if (params.end_row !== undefined) query.set('end_row', String(params.end_row));
    if (params.sort_col) query.set('sort_col', params.sort_col);
    if (params.sort_dir) query.set('sort_dir', params.sort_dir);
    if (params.filter_tab) query.set('filter_tab', params.filter_tab);
    if (params.search) query.set('search', params.search);

    const queryString = query.toString();
    return this.request<DisputeListResponse>(`/api/disputes${queryString ? `?${queryString}` : ''}`);
  }

  async getDispute(disputeId: string | number): Promise<Dispute> {
    return this.request<Dispute>(`/api/disputes/${disputeId}`);
  }

  async submitEvidence(disputeId: string | number, payload: { note?: string } = {}): Promise<{ status: string; dispute_id: string }> {
    return this.request<{ status: string; dispute_id: string }>(`/api/disputes/${disputeId}/submit-evidence`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async overrideDecision(disputeId: string | number, payload: { action: 'AUTO_SUBMIT' | 'ESCALATE' | 'ACCEPT_CLAIM'; note?: string }): Promise<Dispute> {
    return this.request<Dispute>(`/api/disputes/${disputeId}/override`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // --- Webhooks & Simulation API ---

  async simulateWebhook(req: SimulateWebhookRequest = {}): Promise<SimulateWebhookResponse> {
    return this.request<SimulateWebhookResponse>('/api/webhooks/paypal/simulate', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  // --- Analytics & Risk API ---

  async getRiskScore(): Promise<RiskMetrics> {
    return this.request<RiskMetrics>('/api/analytics/risk-score');
  }

  async getAnalyticsSummary(): Promise<AnalyticsSummary> {
    return this.request<AnalyticsSummary>('/api/analytics/summary');
  }

  async getWinRate(): Promise<{ win_rate: number; total_resolved: number; total_won: number }> {
    return this.request<{ win_rate: number; total_resolved: number; total_won: number }>('/api/analytics/win-rate');
  }
}

export default DisputeShieldClient;

