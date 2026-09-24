"""Health endpoint — verifies API and database connectivity."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.schemas import HealthResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    db_status: str = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("DB health check failed: %s", exc)
        db_status = "down"

    overall = "ok" if db_status == "ok" else "degraded"
    return HealthResponse(
        status=overall,  # type: ignore[arg-type]
        database=db_status,  # type: ignore[arg-type]
        environment=settings.ENVIRONMENT,
        llm_provider=settings.LLM_PROVIDER,
    )
