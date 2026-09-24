"""GET /api/metrics — aggregates for the dashboard."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import MetricsResponse
from app.services.metrics_service import build_metrics

router = APIRouter()


@router.get("/metrics", response_model=MetricsResponse)
def metrics(db: Session = Depends(get_db)) -> MetricsResponse:
    return build_metrics(db)
