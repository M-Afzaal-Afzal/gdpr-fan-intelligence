"""Tiny repository layer keeping ORM details out of route handlers."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import AnalysisResult, AuditEvent, PiiEntity


def create_analysis_result(db: Session, **fields: Any) -> AnalysisResult:
    result = AnalysisResult(**fields)
    db.add(result)
    db.flush()
    return result


def create_pii_entities(db: Session, message_id: uuid.UUID, entities: list[dict[str, Any]]) -> None:
    """Insert PII metadata only — never the original PII value."""

    if not entities:
        return
    rows = [
        PiiEntity(
            message_id=message_id,
            entity_type=e["entity_type"],
            start_char=e["start_char"],
            end_char=e["end_char"],
            replacement_token=e["replacement_token"],
            confidence=e.get("confidence"),
        )
        for e in entities
    ]
    db.add_all(rows)


def create_audit_event(
    db: Session,
    *,
    message_id: uuid.UUID | None,
    step_name: str,
    status: str,
    latency_ms: int | None = None,
    error_message: str | None = None,
) -> None:
    db.add(
        AuditEvent(
            message_id=message_id,
            step_name=step_name,
            status=status,
            latency_ms=latency_ms,
            error_message=error_message,
        )
    )


def get_result_by_id(db: Session, result_id: uuid.UUID) -> AnalysisResult | None:
    stmt = (
        select(AnalysisResult)
        .where(AnalysisResult.id == result_id)
        .options(selectinload(AnalysisResult.pii_entities))
    )
    return db.execute(stmt).scalar_one_or_none()


def get_recent_results(db: Session, limit: int = 25) -> Sequence[AnalysisResult]:
    stmt = select(AnalysisResult).order_by(desc(AnalysisResult.created_at)).limit(limit)
    return db.execute(stmt).scalars().all()


def get_metrics(db: Session) -> dict[str, Any]:
    total = db.execute(select(func.count(AnalysisResult.id))).scalar_one()
    pii_detected = db.execute(
        select(func.count(AnalysisResult.id)).where(AnalysisResult.pii_count > 0)
    ).scalar_one()
    blocked = db.execute(
        select(func.count(AnalysisResult.id)).where(AnalysisResult.privacy_status == "blocked")
    ).scalar_one()
    avg_latency = db.execute(select(func.avg(AnalysisResult.latency_ms))).scalar_one()

    sentiment_rows = db.execute(
        select(AnalysisResult.sentiment, func.count(AnalysisResult.id))
        .where(AnalysisResult.sentiment.is_not(None))
        .group_by(AnalysisResult.sentiment)
    ).all()
    topic_rows = db.execute(
        select(AnalysisResult.topic, func.count(AnalysisResult.id))
        .where(AnalysisResult.topic.is_not(None))
        .group_by(AnalysisResult.topic)
    ).all()
    language_rows = db.execute(
        select(AnalysisResult.language, func.count(AnalysisResult.id)).group_by(
            AnalysisResult.language
        )
    ).all()

    return {
        "total_messages": int(total or 0),
        "pii_detected_count": int(pii_detected or 0),
        "blocked_count": int(blocked or 0),
        "average_latency_ms": float(avg_latency) if avg_latency is not None else None,
        "sentiment_distribution": {k: int(v) for k, v in sentiment_rows},
        "topic_distribution": {k: int(v) for k, v in topic_rows},
        "language_distribution": {k: int(v) for k, v in language_rows},
    }
