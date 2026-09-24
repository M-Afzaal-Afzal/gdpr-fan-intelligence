"""SQLAlchemy 2.0 ORM models.

PRIVACY NOTE
------------
- `analysis_results.raw_message_hash` stores a salted/hash digest only — never the message.
- `pii_entities` has NO `entity_value` column on purpose. We store only `entity_type`,
  offsets, replacement token, and confidence so that even a full DB dump cannot
  reconstruct the original PII.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str] = mapped_column(String(16), nullable=False)
    raw_message_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    masked_message: Mapped[str] = mapped_column(Text, nullable=False)
    pii_types_detected: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    pii_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    sentiment: Mapped[str | None] = mapped_column(String(32), nullable=True)
    topic: Mapped[str | None] = mapped_column(String(64), nullable=True)
    intent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)

    privacy_status: Mapped[str] = mapped_column(String(32), nullable=False)
    llm_called: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    pii_entities: Mapped[list[PiiEntity]] = relationship(
        back_populates="analysis_result",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_analysis_results_created_at", "created_at"),
        Index("ix_analysis_results_sentiment", "sentiment"),
        Index("ix_analysis_results_topic", "topic"),
        Index("ix_analysis_results_language", "language"),
        Index("ix_analysis_results_privacy_status", "privacy_status"),
    )


class PiiEntity(Base):
    __tablename__ = "pii_entities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    start_char: Mapped[int] = mapped_column(Integer, nullable=False)
    end_char: Mapped[int] = mapped_column(Integer, nullable=False)
    replacement_token: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    analysis_result: Mapped[AnalysisResult] = relationship(back_populates="pii_entities")

    __table_args__ = (Index("ix_pii_entities_message_id", "message_id"),)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    step_name: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (Index("ix_audit_events_message_id", "message_id"),)
