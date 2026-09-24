"""Pydantic schemas — the single source of truth for the public API contract."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.config import settings

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Source(str, Enum):
    support_ticket = "support_ticket"
    email = "email"
    social_media = "social_media"
    app_review = "app_review"
    forum = "forum"
    other = "other"


class Language(str, Enum):
    en = "en"
    de = "de"
    mixed = "mixed"
    unknown = "unknown"


class PrivacyStatus(str, Enum):
    safe_for_llm = "safe_for_llm"
    blocked = "blocked"


class PiiType(str, Enum):
    NAME = "NAME"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    CITY = "CITY"
    ADDRESS = "ADDRESS"
    MEMBER_ID = "MEMBER_ID"
    ORDER_ID = "ORDER_ID"
    BOOKING_ID = "BOOKING_ID"
    SOCIAL_HANDLE = "SOCIAL_HANDLE"


class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"
    mixed = "mixed"


class Topic(str, Enum):
    ticket_pricing = "ticket_pricing"
    ticket_booking = "ticket_booking"
    refund = "refund"
    booking_problem = "booking_problem"
    merchandise = "merchandise"
    parking = "parking"
    accessibility = "accessibility"
    stadium_experience = "stadium_experience"
    stadium_food = "stadium_food"
    food = "food"
    security = "security"
    streaming = "streaming"
    membership = "membership"
    loyalty_points = "loyalty_points"
    mobile_app = "mobile_app"
    away_travel = "away_travel"
    entry_queue = "entry_queue"
    family_seating = "family_seating"
    other = "other"


class Intent(str, Enum):
    complaint = "complaint"
    question = "question"
    refund_request = "refund_request"
    praise = "praise"
    cancellation = "cancellation"
    support_request = "support_request"
    feedback = "feedback"


class Urgency(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class LlmProvider(str, Enum):
    stub = "stub"
    openai = "openai"
    gemini = "gemini"
    anthropic = "anthropic"
    ollama = "ollama"
    huggingface = "huggingface"
    fireworks = "fireworks"


StorageStatus = Literal["stored", "failed", "skipped"]


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    """The only thing the frontend sends — never raw secrets, never PII rules."""

    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(
        ...,
        min_length=settings.MIN_MESSAGE_LENGTH,
        max_length=settings.MAX_MESSAGE_LENGTH,
        description="Raw fan message — processed in-memory only.",
    )
    source: Source = Field(default=Source.other)
    llm_provider: LlmProvider | None = Field(
        default=None,
        description="Optional per-request LLM override. Keys stay on the server.",
    )


class DetectedPii(BaseModel):
    """A single PII span. NOTE: no `value` field — original PII is never returned."""

    type: PiiType
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)
    replacement: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class Analysis(BaseModel):
    sentiment: Sentiment
    topic: Topic
    intent: Intent
    urgency: Urgency
    summary: str
    recommended_action: str


class PipelineTiming(BaseModel):
    """Per-stage wall-clock timings for the privacy pipeline (milliseconds)."""

    detect_ms: int = Field(..., ge=0, description="Language detection + PII detection.")
    mask_ms: int = Field(..., ge=0, description="Anonymization / masking.")
    safety_gate_ms: int = Field(..., ge=0, description="Second PII scan on masked text.")
    llm_ms: int | None = Field(
        default=None,
        ge=0,
        description="LLM call duration; null when blocked or not invoked.",
    )
    persist_ms: int = Field(..., ge=0, description="Database persist.")
    total_ms: int = Field(..., ge=0, description="End-to-end server time (matches latency_ms).")


class AnalyzeResponse(BaseModel):
    id: UUID
    language: Language
    privacy_status: PrivacyStatus
    llm_called: bool
    llm_provider: str | None = None
    llm_model: str | None = None
    detected_pii: list[DetectedPii]
    masked_message: str
    analysis: Analysis | None = None
    latency_ms: int
    pipeline_timing: PipelineTiming
    storage_status: StorageStatus
    reason: str | None = None


class ResultListItem(BaseModel):
    id: UUID
    language: Language
    privacy_status: PrivacyStatus
    llm_called: bool
    masked_message: str
    pii_count: int
    pii_types_detected: list[str]
    sentiment: Sentiment | None = None
    topic: Topic | None = None
    intent: Intent | None = None
    urgency: Urgency | None = None
    summary: str | None = None
    recommended_action: str | None = None
    latency_ms: int | None = None
    created_at: datetime


class MetricsResponse(BaseModel):
    total_messages: int
    pii_detected_count: int
    blocked_count: int
    average_latency_ms: float | None
    sentiment_distribution: dict[str, int]
    topic_distribution: dict[str, int]
    language_distribution: dict[str, int]
    recent_results: list[ResultListItem]


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    database: Literal["ok", "down"]
    environment: str
    llm_provider: str


class LlmProviderOption(BaseModel):
    id: LlmProvider
    label: str
    model: str
    configured: bool


class LlmProvidersResponse(BaseModel):
    default: LlmProvider
    providers: list[LlmProviderOption]
