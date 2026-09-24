"""POST /api/analyze-message — orchestrates the privacy pipeline.

Order of operations (do not reorder without privacy review):

1. Validate request (Pydantic).
2. Detect language.
3. Layered PII detection on the raw message.
4. Anonymize → masked message + PII metadata.
5. Safety gate: second PII scan on the masked message.
6. If safe → LLM with masked message ONLY.
7. Validate LLM JSON output; final PII scan on summary + action.
8. Persist masked message + metadata + analysis (never raw PII).
9. Return structured response.
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import repositories
from app.db.database import get_db
from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    DetectedPii,
    PipelineTiming,
    PrivacyStatus,
)
from app.services import (
    anonymizer,
    language_service,
    llm_service,
    pii_detector,
    safety_gate,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze-message", response_model=AnalyzeResponse)
def analyze_message(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
) -> AnalyzeResponse:
    start = time.perf_counter()
    t0 = start

    # 1. Language detection (cheap, helps the dashboard)
    language = language_service.detect_language(payload.message)

    # 2. Layered PII detection
    spans = pii_detector.detect_pii(payload.message)
    detect_ms = int((time.perf_counter() - t0) * 1000)
    t0 = time.perf_counter()

    # 3. Anonymization
    anonymized = anonymizer.anonymize(payload.message, spans)
    mask_ms = int((time.perf_counter() - t0) * 1000)
    t0 = time.perf_counter()

    # 4. Second safety gate
    gate = safety_gate.evaluate_masked(anonymized.masked_message)
    safety_gate_ms = int((time.perf_counter() - t0) * 1000)
    t0 = time.perf_counter()

    analysis = None
    llm_called = False
    llm_provider: str | None = None
    llm_model: str | None = None
    privacy_status = PrivacyStatus.blocked
    reason: str | None = gate.reason
    llm_ms: int | None = None

    if gate.safe:
        privacy_status = PrivacyStatus.safe_for_llm
        try:
            analysis, llm_provider, llm_model = llm_service.analyze_masked_message(
                anonymized.masked_message,
                provider_override=(
                    payload.llm_provider.value if payload.llm_provider is not None else None
                ),
            )
            llm_called = True
        except Exception as exc:
            logger.warning("LLM call failed: %s", exc)
            analysis = None
            llm_called = False
            reason = "LLM call failed"
        llm_ms = int((time.perf_counter() - t0) * 1000)
        t0 = time.perf_counter()

    # 7. Final scrub of any text the LLM might have generated already happens
    #    inside the validator. Belt-and-braces: do it once more here for the
    #    fields we surface in the API response.
    if analysis is not None:
        clean_summary, _ = safety_gate.sanitize_llm_output(analysis.summary)
        clean_action, _ = safety_gate.sanitize_llm_output(analysis.recommended_action)
        analysis = analysis.model_copy(
            update={"summary": clean_summary, "recommended_action": clean_action}
        )

    # 8. Persist
    pre_persist_latency = int((time.perf_counter() - start) * 1000)
    persist_start = time.perf_counter()
    record_id, storage_status = _store_result(
        db=db,
        request=payload,
        language=language,
        detected=anonymized.detected,
        masked_message=anonymized.masked_message,
        analysis=analysis,
        privacy_status=privacy_status,
        llm_called=llm_called,
        latency_ms=pre_persist_latency,
    )
    persist_ms = int((time.perf_counter() - persist_start) * 1000)

    latency_ms = pre_persist_latency + persist_ms
    pipeline_timing = PipelineTiming(
        detect_ms=detect_ms,
        mask_ms=mask_ms,
        safety_gate_ms=safety_gate_ms,
        llm_ms=llm_ms,
        persist_ms=persist_ms,
        total_ms=latency_ms,
    )

    return AnalyzeResponse(
        id=record_id,
        language=language,
        privacy_status=privacy_status,
        llm_called=llm_called,
        llm_provider=llm_provider,
        llm_model=llm_model,
        detected_pii=anonymized.detected,
        masked_message=anonymized.masked_message,
        analysis=analysis,
        latency_ms=latency_ms,
        pipeline_timing=pipeline_timing,
        storage_status=storage_status,
        reason=reason if privacy_status == PrivacyStatus.blocked else None,
    )


def _hash_raw(message: str) -> str:
    return hashlib.sha256(message.encode("utf-8")).hexdigest()


def _store_result(
    *,
    db: Session,
    request: AnalyzeRequest,
    language: Any,
    detected: list[DetectedPii],
    masked_message: str,
    analysis: Any,
    privacy_status: PrivacyStatus,
    llm_called: bool,
    latency_ms: int,
) -> tuple[uuid.UUID, str]:
    pii_types_detected = sorted({d.type.value for d in detected})
    fields: dict[str, Any] = {
        "source": request.source.value,
        "language": language.value,
        "raw_message_hash": _hash_raw(request.message),
        "masked_message": masked_message,
        "pii_types_detected": pii_types_detected,
        "pii_count": len(detected),
        "privacy_status": privacy_status.value,
        "llm_called": llm_called,
        "latency_ms": latency_ms,
    }
    if analysis is not None:
        fields.update(
            sentiment=analysis.sentiment.value,
            topic=analysis.topic.value,
            intent=analysis.intent.value,
            urgency=analysis.urgency.value,
            summary=analysis.summary,
            recommended_action=analysis.recommended_action,
        )

    try:
        result = repositories.create_analysis_result(db, **fields)
        repositories.create_pii_entities(
            db,
            message_id=result.id,
            entities=[
                {
                    "entity_type": d.type.value,
                    "start_char": d.start,
                    "end_char": d.end,
                    "replacement_token": d.replacement,
                    "confidence": d.confidence,
                }
                for d in detected
            ],
        )
        repositories.create_audit_event(
            db,
            message_id=result.id,
            step_name="analyze",
            status=privacy_status.value,
            latency_ms=latency_ms,
        )
        db.commit()
        return result.id, "stored"
    except SQLAlchemyError as exc:
        db.rollback()
        logger.warning("DB write failed: %s", exc)
        return uuid.uuid4(), "failed"
