const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export interface Business {
  msme_id: string;
  business_name: string;
  gstin: string;
  pan: string;
  sector: string;
  state: string;
  incorporation_date: string;
  credit_status: "NTC" | "NTB";
}

export interface SubScores {
  compliance_consistency: number;
  cash_flow_stability: number;
  digital_footprint: number;
  workforce_stability: number;
  [key: string]: number;
}

export interface ScoreResponse {
  msme_id: string;
  business_name: string;
  sub_scores: SubScores;
  composite_score: number;
  learned_weights: SubScores;
  traditional_outcome: string;
  health_card_outcome: string;
  last_updated: string;
}

export interface NarrativeResponse {
  msme_id: string;
  narrative: string;
}

export interface PortfolioRow {
  msme_id: string;
  business_name: string;
  sector: string;
  state: string;
  credit_status: "NTC" | "NTB";
  composite_score: number;
  last_updated: string | null;
}

export interface PortfolioResponse {
  businesses: PortfolioRow[];
  portfolio_stats: {
    average_health_score: number;
    high_risk_flagged_pct: number;
    total_msmes: number;
  };
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  searchMsme: (identifier: string) =>
    request<Business>(`/msme/${encodeURIComponent(identifier)}`),

  grantConsent: (msmeId: string, sources: string[]) =>
    request<{ msme_id: string; consented_sources: string[]; aggregated_data: unknown }>(
      `/consent`,
      { method: "POST", body: JSON.stringify({ msme_id: msmeId, sources }) }
    ),

  getScore: (msmeId: string) => request<ScoreResponse>(`/score/${msmeId}`),

  getNarrative: (msmeId: string) =>
    request<NarrativeResponse>(`/narrative/${msmeId}`),

  getPortfolio: () => request<PortfolioResponse>(`/portfolio`),

  refreshScore: (msmeId: string) =>
    request<ScoreResponse>(`/portfolio/${msmeId}/refresh`, { method: "POST" }),
};
