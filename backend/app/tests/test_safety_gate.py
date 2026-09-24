"""Tests for the safety gate (second PII scan)."""

from __future__ import annotations

from app.services.safety_gate import evaluate_masked, sanitize_llm_output


def test_clean_masked_message_is_safe():
    decision = evaluate_masked(
        "Hi I am [NAME_1] from [CITY_1] needing help with booking [BOOKING_ID_1]"
    )
    assert decision.safe is True
    assert decision.residual_spans == []


def test_residual_email_blocks():
    decision = evaluate_masked("Hi I am [NAME_1] contact me at residual@example.com")
    assert decision.safe is False
    assert decision.residual_spans
    assert decision.reason


def test_residual_booking_id_blocks():
    decision = evaluate_masked("Order ORD-12345 still present")
    assert decision.safe is False


def test_sanitize_llm_output_clean_text_unchanged():
    text = "The fan reports a refund issue and asks for support."
    out, was_clean = sanitize_llm_output(text)
    assert was_clean is True
    assert out == text


def test_sanitize_llm_output_redacts_email_if_model_leaks():
    text = "Contact the fan at leak@example.com immediately."
    out, was_clean = sanitize_llm_output(text)
    assert was_clean is False
    assert "leak@example.com" not in out
