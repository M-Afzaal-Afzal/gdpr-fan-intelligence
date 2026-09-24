"""GET /api/results and GET /api/results/{id}."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import repositories
from app.db.database import get_db
from app.schemas import ResultListItem

router = APIRouter()


def _to_item(row) -> ResultListItem:
    return ResultListItem(
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


@router.get("/results", response_model=list[ResultListItem])
def list_results(limit: int = 25, db: Session = Depends(get_db)) -> list[ResultListItem]:
    limit = max(1, min(limit, 100))
    rows = repositories.get_recent_results(db, limit=limit)
    return [_to_item(r) for r in rows]


@router.get("/results/{result_id}", response_model=ResultListItem)
def get_result(result_id: uuid.UUID, db: Session = Depends(get_db)) -> ResultListItem:
    row = repositories.get_result_by_id(db, result_id)
    if row is None:
        raise HTTPException(status_code=404, detail="result not found")
    return _to_item(row)
