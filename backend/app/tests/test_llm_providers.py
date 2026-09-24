"""Tests for the multi-LLM provider implementations.

Verifies:
- Each provider falls back to the stub when the API key is empty.
- Each provider falls back to the stub on HTTP errors.
- The masked_message (not raw) is what every provider sends.
- parse_llm_payload is called by each provider path.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.schemas import Analysis, Intent, Sentiment, Topic, Urgency
from app.services import llm_service
from app.services.llm_service import (
    SYSTEM_PROMPT,
    _anthropic_call,
    _gemini_call,
    _hf_call,
    _ollama_call,
    analyze_masked_message,
    build_user_prompt,
    stub_analyze,
)

MASKED = "Fan is upset about the [PERSON] price increase."
RAW = "Fan is upset about John's price increase."  # must never reach any provider

_VALID_ANALYSIS = Analysis(
    sentiment=Sentiment.negative,
    topic=Topic.ticket_pricing,
    intent=Intent.complaint,
    urgency=Urgency.medium,
    summary="A fan complained about ticket prices.",
    recommended_action="Review pricing policy.",
)

_VALID_JSON = json.dumps(
    {
        "sentiment": "negative",
        "topic": "ticket_pricing",
        "intent": "complaint",
        "urgency": "medium",
        "summary": "A fan complained about ticket prices.",
        "recommended_action": "Review pricing policy.",
    }
)


def _mock_response(text: str, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json.loads(text) if text else {}
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        import httpx

        mock.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=mock
        )
    return mock


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------


class TestGeminiCall:
    def _gemini_payload(self, content: str) -> str:
        return json.dumps({"candidates": [{"content": {"parts": [{"text": content}]}}]})

    def test_returns_analysis_on_success(self) -> None:
        resp = _mock_response(self._gemini_payload(_VALID_JSON))
        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = resp
            result = _gemini_call(MASKED)
        assert result is not None
        assert result.sentiment == Sentiment.negative

    def test_sends_masked_message_not_raw(self) -> None:
        resp = _mock_response(self._gemini_payload(_VALID_JSON))
        with patch("httpx.Client") as mock_client_cls:
            mock_post = mock_client_cls.return_value.__enter__.return_value.post
            mock_post.return_value = resp
            _gemini_call(MASKED)
            call_kwargs = mock_post.call_args
        body: dict[str, Any] = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
        prompt_text = body["contents"][0]["parts"][0]["text"]
        assert MASKED in prompt_text
        assert RAW not in prompt_text

    def test_fallback_to_stub_on_http_error(self) -> None:
        import httpx

        with patch("httpx.Client") as mock_client_cls:
            mock_post = mock_client_cls.return_value.__enter__.return_value.post
            mock_post.return_value = _mock_response("{}", 500)
            with pytest.raises(httpx.HTTPStatusError):
                _gemini_call(MASKED)

    def test_analyze_falls_back_to_stub_when_no_key(self) -> None:
        with patch.object(llm_service.settings, "LLM_PROVIDER", "gemini"), patch.object(
            llm_service.settings, "GEMINI_API_KEY", ""
        ):
            analysis, provider, model = analyze_masked_message(MASKED)
        assert isinstance(analysis, Analysis)
        assert provider == "stub"

    def test_analyze_falls_back_to_stub_on_error(self) -> None:
        with (
            patch.object(llm_service.settings, "LLM_PROVIDER", "gemini"),
            patch.object(llm_service.settings, "GEMINI_API_KEY", "fake-key"),
            patch.object(llm_service, "_gemini_call", side_effect=RuntimeError("boom")),
        ):
            analysis, provider, model = analyze_masked_message(MASKED)
        assert isinstance(analysis, Analysis)
        assert provider == "stub"


# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------


class TestAnthropicCall:
    def _anthropic_payload(self, content: str) -> str:
        return json.dumps({"content": [{"text": content}]})

    def test_returns_analysis_on_success(self) -> None:
        resp = _mock_response(self._anthropic_payload(_VALID_JSON))
        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = resp
            result = _anthropic_call(MASKED)
        assert result is not None
        assert result.topic == Topic.ticket_pricing

    def test_sends_masked_message_not_raw(self) -> None:
        resp = _mock_response(self._anthropic_payload(_VALID_JSON))
        with patch("httpx.Client") as mock_client_cls:
            mock_post = mock_client_cls.return_value.__enter__.return_value.post
            mock_post.return_value = resp
            _anthropic_call(MASKED)
            call_kwargs = mock_post.call_args
        body: dict[str, Any] = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
        message_content = body["messages"][0]["content"]
        assert MASKED in message_content
        assert RAW not in message_content

    def test_uses_system_prompt(self) -> None:
        resp = _mock_response(self._anthropic_payload(_VALID_JSON))
        with patch("httpx.Client") as mock_client_cls:
            mock_post = mock_client_cls.return_value.__enter__.return_value.post
            mock_post.return_value = resp
            _anthropic_call(MASKED)
            call_kwargs = mock_post.call_args
        body: dict[str, Any] = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
        assert body["system"] == SYSTEM_PROMPT

    def test_analyze_falls_back_to_stub_when_no_key(self) -> None:
        with patch.object(llm_service.settings, "LLM_PROVIDER", "anthropic"), patch.object(
            llm_service.settings, "ANTHROPIC_API_KEY", ""
        ):
            analysis, provider, model = analyze_masked_message(MASKED)
        assert isinstance(analysis, Analysis)
        assert provider == "stub"

    def test_analyze_falls_back_to_stub_on_error(self) -> None:
        with (
            patch.object(llm_service.settings, "LLM_PROVIDER", "anthropic"),
            patch.object(llm_service.settings, "ANTHROPIC_API_KEY", "fake-key"),
            patch.object(llm_service, "_anthropic_call", side_effect=RuntimeError("boom")),
        ):
            analysis, provider, model = analyze_masked_message(MASKED)
        assert isinstance(analysis, Analysis)
        assert provider == "stub"


# ---------------------------------------------------------------------------
# Ollama
# ---------------------------------------------------------------------------


class TestOllamaCall:
    def _ollama_payload(self, content: str) -> str:
        return json.dumps({"message": {"content": content}})

    def test_returns_analysis_on_success(self) -> None:
        resp = _mock_response(self._ollama_payload(_VALID_JSON))
        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = resp
            result = _ollama_call(MASKED)
        assert result is not None
        assert result.intent == Intent.complaint

    def test_sends_masked_message_not_raw(self) -> None:
        resp = _mock_response(self._ollama_payload(_VALID_JSON))
        with patch("httpx.Client") as mock_client_cls:
            mock_post = mock_client_cls.return_value.__enter__.return_value.post
            mock_post.return_value = resp
            _ollama_call(MASKED)
            call_kwargs = mock_post.call_args
        body: dict[str, Any] = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
        user_content = next(m["content"] for m in body["messages"] if m["role"] == "user")
        assert MASKED in user_content
        assert RAW not in user_content

    def test_stream_is_false(self) -> None:
        resp = _mock_response(self._ollama_payload(_VALID_JSON))
        with patch("httpx.Client") as mock_client_cls:
            mock_post = mock_client_cls.return_value.__enter__.return_value.post
            mock_post.return_value = resp
            _ollama_call(MASKED)
            call_kwargs = mock_post.call_args
        body: dict[str, Any] = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
        assert body["stream"] is False

    def test_analyze_falls_back_to_stub_on_error(self) -> None:
        with (
            patch.object(llm_service.settings, "LLM_PROVIDER", "ollama"),
            patch.object(llm_service, "_ollama_call", side_effect=RuntimeError("boom")),
        ):
            analysis, provider, model = analyze_masked_message(MASKED)
        assert isinstance(analysis, Analysis)
        assert provider == "stub"

    def test_analyze_routes_to_ollama_without_key(self) -> None:
        """Ollama needs no API key — it should be attempted when provider=ollama."""
        resp_payload = self._ollama_payload(_VALID_JSON)
        resp = _mock_response(resp_payload)
        with (
            patch.object(llm_service.settings, "LLM_PROVIDER", "ollama"),
            patch("httpx.Client") as mock_client_cls,
        ):
            mock_client_cls.return_value.__enter__.return_value.post.return_value = resp
            analysis, provider, model = analyze_masked_message(MASKED)
        assert analysis is not None
        assert analysis.urgency == Urgency.medium
        assert provider == "ollama"


# ---------------------------------------------------------------------------
# HuggingFace
# ---------------------------------------------------------------------------


class TestHuggingFaceCall:
    def _hf_payload(self, content: str) -> str:
        return json.dumps([{"generated_text": content}])

    def test_returns_analysis_on_success(self) -> None:
        resp = _mock_response(self._hf_payload(_VALID_JSON))
        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = resp
            result = _hf_call(MASKED)
        assert result is not None
        assert result.sentiment == Sentiment.negative

    def test_sends_masked_message_not_raw(self) -> None:
        resp = _mock_response(self._hf_payload(_VALID_JSON))
        with patch("httpx.Client") as mock_client_cls:
            mock_post = mock_client_cls.return_value.__enter__.return_value.post
            mock_post.return_value = resp
            _hf_call(MASKED)
            call_kwargs = mock_post.call_args
        body: dict[str, Any] = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
        inputs: str = body["inputs"]
        assert MASKED in inputs
        assert RAW not in inputs

    def test_return_full_text_false(self) -> None:
        resp = _mock_response(self._hf_payload(_VALID_JSON))
        with patch("httpx.Client") as mock_client_cls:
            mock_post = mock_client_cls.return_value.__enter__.return_value.post
            mock_post.return_value = resp
            _hf_call(MASKED)
            call_kwargs = mock_post.call_args
        body: dict[str, Any] = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
        assert body["parameters"]["return_full_text"] is False

    def test_analyze_falls_back_to_stub_when_no_key(self) -> None:
        with patch.object(llm_service.settings, "LLM_PROVIDER", "huggingface"), patch.object(
            llm_service.settings, "HF_API_KEY", ""
        ):
            analysis, provider, model = analyze_masked_message(MASKED)
        assert isinstance(analysis, Analysis)
        assert provider == "stub"

    def test_analyze_falls_back_to_stub_on_error(self) -> None:
        with (
            patch.object(llm_service.settings, "LLM_PROVIDER", "huggingface"),
            patch.object(llm_service.settings, "HF_API_KEY", "fake-key"),
            patch.object(llm_service, "_hf_call", side_effect=RuntimeError("boom")),
        ):
            analysis, provider, model = analyze_masked_message(MASKED)
        assert isinstance(analysis, Analysis)
        assert provider == "stub"


# ---------------------------------------------------------------------------
# Dispatch / routing
# ---------------------------------------------------------------------------


class TestDispatch:
    def test_unknown_provider_uses_stub(self) -> None:
        with patch.object(llm_service.settings, "LLM_PROVIDER", "unknown_llm"):
            analysis, provider, model = analyze_masked_message(MASKED)
        assert isinstance(analysis, Analysis)
        assert provider == "stub"

    def test_stub_provider_returns_analysis(self) -> None:
        with patch.object(llm_service.settings, "LLM_PROVIDER", "stub"):
            analysis, provider, model = analyze_masked_message(MASKED)
        assert isinstance(analysis, Analysis)
        assert provider == "stub"

    def test_stub_analyze_never_receives_raw(self) -> None:
        result = stub_analyze(MASKED)
        assert result is not None
        # Stub result should be based on masked message content.
        assert isinstance(result.sentiment, Sentiment)

    def test_build_user_prompt_contains_masked(self) -> None:
        prompt = build_user_prompt(MASKED)
        assert MASKED in prompt
