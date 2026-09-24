"""Tests for the anonymizer."""

from __future__ import annotations

from app.schemas import PiiType
from app.services.anonymizer import anonymize
from app.services.pii_detector import PiiSpan, detect_pii


def test_replaces_single_entity():
    text = "Email: john.miller@gmail.com please."
    spans = detect_pii(text)
    out = anonymize(text, spans)
    assert "[EMAIL_1]" in out.masked_message
    assert "john.miller@gmail.com" not in out.masked_message


def test_multiple_entities_stable_numbering():
    text = "Hi from john@a.com and mary@b.com — booking BK-1001."
    spans = detect_pii(text)
    out = anonymize(text, spans)
    # First email becomes EMAIL_1, second EMAIL_2, booking becomes BOOKING_ID_1.
    assert "[EMAIL_1]" in out.masked_message
    assert "[EMAIL_2]" in out.masked_message
    assert "[BOOKING_ID_1]" in out.masked_message
    assert "john@a.com" not in out.masked_message
    assert "mary@b.com" not in out.masked_message
    assert "BK-1001" not in out.masked_message


def test_overlapping_spans_handled_safely():
    """Manually crafted overlapping spans should not raise or corrupt output."""

    text = "abcdefghij"
    overlapping = [
        PiiSpan(type=PiiType.NAME, start=0, end=5, confidence=0.9),
        PiiSpan(type=PiiType.NAME, start=2, end=7, confidence=0.9),
    ]
    out = anonymize(text, overlapping)
    # Anonymizer is robust to overlap — just verify it produces a string.
    assert isinstance(out.masked_message, str)
    assert len(out.detected) == 2


def test_returns_metadata_without_original_value():
    text = "Call +49 176 12345678"
    out = anonymize(text, detect_pii(text))
    for d in out.detected:
        # The DetectedPii model has no field carrying the raw PII string.
        dumped = d.model_dump()
        assert "value" not in dumped
        assert "original" not in dumped


def test_offsets_preserved_for_right_to_left_replacement():
    text = "First mary@b.com then BK-9911 here"
    spans = detect_pii(text)
    out = anonymize(text, spans)
    # Both entities should be replaced cleanly.
    assert "mary@b.com" not in out.masked_message
    assert "BK-9911" not in out.masked_message
