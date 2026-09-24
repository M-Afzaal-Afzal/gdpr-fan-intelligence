/**
 * Types matching the FastAPI response models. Keep these in sync with
 * `backend/app/schemas.py`. Frontend NEVER detects or stores PII — it only
 * renders what the backend returned.
 */

export type Source =
  | 'support_ticket'
  | 'email'
  | 'social_media'
  | 'app_review'
  | 'forum'
  | 'other';

export type Language = 'en' | 'de' | 'mixed' | 'unknown';

export type PrivacyStatus = 'safe_for_llm' | 'blocked';

export type PiiType =
  | 'NAME'
  | 'EMAIL'
  | 'PHONE'
  | 'CITY'
  | 'ADDRESS'
  | 'MEMBER_ID'
  | 'ORDER_ID'
  | 'BOOKING_ID'
  | 'SOCIAL_HANDLE';

export type Sentiment = 'positive' | 'neutral' | 'negative' | 'mixed';
export type Urgency = 'low' | 'medium' | 'high';

export type Topic =
  | 'ticket_pricing'
  | 'ticket_booking'
  | 'refund'
  | 'booking_problem'
  | 'merchandise'
  | 'parking'
  | 'accessibility'
  | 'stadium_experience'
  | 'stadium_food'
  | 'food'
  | 'security'
  | 'streaming'
  | 'membership'
  | 'loyalty_points'
  | 'mobile_app'
  | 'away_travel'
  | 'entry_queue'
  | 'family_seating'
  | 'other';

export type Intent =
  | 'complaint'
  | 'question'
  | 'refund_request'
  | 'praise'
  | 'cancellation'
  | 'support_request'
  | 'feedback';

export type LlmProviderId =
  | 'stub'
  | 'openai'
  | 'gemini'
  | 'anthropic'
  | 'ollama'
  | 'huggingface'
  | 'fireworks';

export interface DetectedPii {
  type: PiiType;
  start: number;
  end: number;
  replacement: string;
  confidence: number;
}

export interface Analysis {
  sentiment: Sentiment;
  topic: Topic;
  intent: Intent;
  urgency: Urgency;
  summary: string;
  recommended_action: string;
}

export interface PipelineTiming {
  detect_ms: number;
  mask_ms: number;
  safety_gate_ms: number;
  llm_ms: number | null;
  persist_ms: number;
  total_ms: number;
}

export interface AnalyzeResponse {
  id: string;
  language: Language;
  privacy_status: PrivacyStatus;
  llm_called: boolean;
  llm_provider: string | null;
  llm_model: string | null;
  detected_pii: DetectedPii[];
  masked_message: string;
  analysis: Analysis | null;
  latency_ms: number;
  pipeline_timing: PipelineTiming;
  storage_status: 'stored' | 'failed' | 'skipped';
  reason?: string | null;
}

export interface ResultListItem {
  id: string;
  language: Language;
  privacy_status: PrivacyStatus;
  llm_called: boolean;
  masked_message: string;
  pii_count: number;
  pii_types_detected: string[];
  sentiment: Sentiment | null;
  topic: Topic | null;
  intent: Intent | null;
  urgency: Urgency | null;
  summary: string | null;
  recommended_action: string | null;
  latency_ms: number | null;
  created_at: string;
}

export interface MetricsResponse {
  total_messages: number;
  pii_detected_count: number;
  blocked_count: number;
  average_latency_ms: number | null;
  sentiment_distribution: Record<string, number>;
  topic_distribution: Record<string, number>;
  language_distribution: Record<string, number>;
  recent_results: ResultListItem[];
}

export interface HealthResponse {
  status: 'ok' | 'degraded';
  database: 'ok' | 'down';
  environment: string;
  llm_provider: string;
}

export interface LlmProviderOption {
  id: LlmProviderId;
  label: string;
  model: string;
  configured: boolean;
}

export interface LlmProvidersResponse {
  default: LlmProviderId;
  providers: LlmProviderOption[];
}
