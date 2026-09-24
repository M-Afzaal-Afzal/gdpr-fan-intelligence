"""API-level tests using FastAPI's TestClient.

The DB layer is monkeypatched to a no-op session so these tests run anywhere
without a running PostgreSQL. The privacy invariants we care about here are:

- /api/health responds (DB will report down without PG, that's fine).
- /api/analyze-message returns a masked message and never echoes raw PII.
- The detected_pii list contains no field that exposes the original string.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Spin up FastAPI with the DB dependency stubbed out."""

    from app.db import database

    fake_session = MagicMock()
    fake_session.execute.return_value.scalar_one.return_value = 1

    def fake_get_db() -> Iterator[Any]:
        yield fake_session

    # Patch the dependency-injection callable used by every route.
    monkeypatch.setattr(database, "get_db", fake_get_db)

    # Patch the repository to skip real DB writes/reads.
    from app.db import repositories

    class _Result:
        def __init__(self) -> None:
            import uuid

            self.id = uuid.uuid4()

    monkeypatch.setattr(repositories, "create_analysis_result", lambda db, **kw: _Result())
    monkeypatch.setattr(repositories, "create_pii_entities", lambda db, message_id, entities: None)
    monkeypatch.setattr(repositories, "create_audit_event", lambda db, **kw: None)
    monkeypatch.setattr(repositories, "get_recent_results", lambda db, limit=25: [])
    monkeypatch.setattr(
        repositories,
        "get_metrics",
        lambda db: {
            "total_messages": 0,
            "pii_detected_count": 0,
            "blocked_count": 0,
            "average_latency_ms": None,
            "sentiment_distribution": {},
            "topic_distribution": {},
            "language_distribution": {},
        },
    )

    # Late import so monkeypatches apply.
    from app.main import app
    from app.routes import analyze as analyze_route
    from app.routes import health as health_route
    from app.routes import metrics as metrics_route
    from app.routes import results as results_route

    app.dependency_overrides[health_route.get_db] = fake_get_db
    app.dependency_overrides[analyze_route.get_db] = fake_get_db
    app.dependency_overrides[results_route.get_db] = fake_get_db
    app.dependency_overrides[metrics_route.get_db] = fake_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_health_endpoint_responds(client: TestClient):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in {"ok", "degraded"}
    assert "database" in body
    assert "environment" in body


def test_analyze_message_returns_masked_text(client: TestClient):
    raw = "Hi I am John Miller from Berlin, email john.miller@gmail.com booking BK-92811."
    resp = client.post("/api/analyze-message", json={"message": raw, "source": "support_ticket"})
    assert resp.status_code == 200, resp.text
    body = resp.json()

    # No raw PII anywhere in the response payload.
    payload_text = resp.text
    assert "john.miller@gmail.com" not in payload_text
    assert "BK-92811" not in payload_text

    # Masked message includes our placeholders.
    assert body["masked_message"]
    assert "[EMAIL_1]" in body["masked_message"]
    assert "[BOOKING_ID_1]" in body["masked_message"]

    # Detected PII records have no value/original field.
    for entity in body["detected_pii"]:
        assert "value" not in entity
        assert "original" not in entity

    timing = body["pipeline_timing"]
    assert timing["detect_ms"] >= 0
    assert timing["mask_ms"] >= 0
    assert timing["safety_gate_ms"] >= 0
    assert timing["persist_ms"] >= 0
    assert timing["total_ms"] == body["latency_ms"]
    stage_sum = (
        timing["detect_ms"]
        + timing["mask_ms"]
        + timing["safety_gate_ms"]
        + timing["persist_ms"]
    )
    if timing["llm_ms"] is not None:
        stage_sum += timing["llm_ms"]
    assert stage_sum <= timing["total_ms"]


def test_analyze_rejects_too_short_message(client: TestClient):
    resp = client.post("/api/analyze-message", json={"message": "hi"})
    assert resp.status_code == 422


def test_metrics_endpoint_responds(client: TestClient):
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_messages" in body
    assert "sentiment_distribution" in body
    assert "recent_results" in body


def test_llm_providers_endpoint(client: TestClient):
    resp = client.get("/api/llm-providers")
    assert resp.status_code == 200
    body = resp.json()
    assert "default" in body
    assert len(body["providers"]) >= 1
    stub = next(p for p in body["providers"] if p["id"] == "stub")
    assert stub["configured"] is True
    assert stub["model"] == "built-in"


def test_analyze_accepts_llm_provider_override(client: TestClient):
    raw = "Hi I am John Miller from Berlin, email john.miller@gmail.com booking BK-92811."
    resp = client.post(
        "/api/analyze-message",
        json={"message": raw, "source": "support_ticket", "llm_provider": "stub"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["llm_called"] is True
    assert body["llm_provider"] == "stub"
