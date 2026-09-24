"""Tests for the LLM output validator."""

from __future__ import annotations

import json

from app.services.output_validator import parse_llm_payload


def _good_payload() -> str:
    return json.dumps(
        {
            "sentiment": "negative",
            "topic": "refund",
            "intent": "refund_request",
            "urgency": "medium",
            "summary": "A fan reports a matchday issue and requests support.",
            "recommended_action": "Review the issue and respond with refund options.",
        }
    )


def test_accepts_valid_json():
    analysis = parse_llm_payload(_good_payload())
    assert analysis is not None
    assert analysis.sentiment.value == "negative"


def test_accepts_code_fenced_json():
    fenced = "```json\n" + _good_payload() + "\n```"
    analysis = parse_llm_payload(fenced)
    assert analysis is not None


def test_rejects_invalid_json():
    assert parse_llm_payload("not json at all") is None
    assert parse_llm_payload("") is None


def test_rejects_missing_field():
    bad = json.dumps({"sentiment": "negative", "topic": "refund"})
    assert parse_llm_payload(bad) is None


def test_rejects_bad_enum_value():
    bad = json.dumps(
        {
            "sentiment": "incandescent",
            "topic": "refund",
            "intent": "refund_request",
            "urgency": "medium",
            "summary": "ok",
            "recommended_action": "ok",
        }
    )
    assert parse_llm_payload(bad) is None


def test_sanitizes_pii_inside_summary():
    payload = json.dumps(
        {
            "sentiment": "negative",
            "topic": "refund",
            "intent": "refund_request",
            "urgency": "medium",
            "summary": "Fan john.smith@example.com asked for a refund.",
            "recommended_action": "Reach out to fan.",
        }
    )
    analysis = parse_llm_payload(payload)
    assert analysis is not None
    assert "john.smith@example.com" not in analysis.summary
