"""Translates repository metric rows into API response shapes."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db import repositories
from app.schemas import MetricsResponse, ResultListItem


def build_metrics(db: Session, *, recent_limit: int = 20) -> MetricsResponse:
    metrics = repositories.get_metrics(db)
    recent_rows = repositories.get_recent_results(db, limit=recent_limit)

    recent_items = [
        ResultListItem(
            id=row.id,
            language=row.language,
            privacy_status=row.privacy_status,
            llm_called=row.llm_called,
            masked_message=row.masked_message,
            pii_count=row.pii_count,
            pii_types_detected=row.pii_types_detected or [],
            sentiment=row.sentiment,
            topic=row.topic,
            intent=row.intent,
            urgency=row.urgency,
            summary=row.summary,
            recommended_action=row.recommended_action,
            latency_ms=row.latency_ms,
            created_at=row.created_at,
        )
        for row in recent_rows
    ]

    return MetricsResponse(**metrics, recent_results=recent_items)
