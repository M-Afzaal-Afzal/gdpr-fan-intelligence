/** Thin fetch wrapper for the FastAPI backend.
 *
 * Privacy: this client only sends the raw message to the backend, and never
 * applies any PII rules locally. It also never reads or stores any LLM keys.
 */

import type {
  AnalyzeResponse,
  HealthResponse,
  LlmProviderId,
  LlmProvidersResponse,
  MetricsResponse,
  ResultListItem,
  Source,
} from './types';
import { API_BASE_URL } from './constants';

class ApiError extends Error {
  status: number;
  body?: unknown;

  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(init?.headers ?? {}),
    },
  });

  if (!res.ok) {
    let body: unknown;
    try {
      body = await res.json();
    } catch {
      body = await res.text();
    }
    throw new ApiError(`Request failed (${res.status})`, res.status, body);
  }

  return res.json() as Promise<T>;
}

export async function analyzeMessage(
  message: string,
  source: Source = 'other',
  llmProvider?: LlmProviderId,
): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>('/api/analyze-message', {
    method: 'POST',
    body: JSON.stringify({
      message,
      source,
      ...(llmProvider ? { llm_provider: llmProvider } : {}),
    }),
  });
}

export async function getLlmProviders(): Promise<LlmProvidersResponse> {
  return request<LlmProvidersResponse>('/api/llm-providers');
}

export async function getResults(limit = 25): Promise<ResultListItem[]> {
  return request<ResultListItem[]>(`/api/results?limit=${limit}`);
}

export async function getResultById(id: string): Promise<ResultListItem> {
  return request<ResultListItem>(`/api/results/${encodeURIComponent(id)}`);
}

export async function getMetrics(): Promise<MetricsResponse> {
  return request<MetricsResponse>('/api/metrics');
}

export async function healthCheck(): Promise<HealthResponse> {
  return request<HealthResponse>('/api/health');
}

export { ApiError };
