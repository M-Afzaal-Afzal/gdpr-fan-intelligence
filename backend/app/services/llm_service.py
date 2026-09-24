"""LLM service.

Providers: `stub` (default), `openai`, `gemini`, `anthropic`, `ollama`,
`huggingface`. Every provider receives only `masked_message` — raw text never
reaches this module. Each provider falls back to the stub on error.

Privacy invariants:
- Only `masked_message` is ever passed in.
- The raw fan message never reaches this module.
- The prompt instructs the model not to invent personal data.
"""

from __future__ import annotations

import logging
import re
from typing import Any

import httpx

from app.config import settings
from app.schemas import Analysis, Intent, Sentiment, Topic, Urgency
from app.services.output_validator import parse_llm_payload

logger = logging.getLogger(__name__)

ALLOWED_LLM_PROVIDERS = frozenset(
    {"stub", "openai", "gemini", "anthropic", "ollama", "huggingface", "fireworks"}
)


def _provider_configured(provider: str) -> bool:
    if provider == "stub":
        return True
    if provider == "openai":
        return bool(settings.OPENAI_API_KEY)
    if provider == "gemini":
        return bool(settings.GEMINI_API_KEY)
    if provider == "anthropic":
        return bool(settings.ANTHROPIC_API_KEY)
    if provider == "ollama":
        return True
    if provider == "huggingface":
        return bool(settings.HF_API_KEY)
    if provider == "fireworks":
        return bool(settings.FIREWORKS_API_KEY)
    return False


def _provider_model(provider: str) -> str:
    if provider == "stub":
        return "built-in"
    if provider == "openai":
        return settings.OPENAI_MODEL
    if provider == "gemini":
        return settings.GEMINI_MODEL
    if provider == "anthropic":
        return settings.ANTHROPIC_MODEL
    if provider == "ollama":
        return settings.OLLAMA_MODEL
    if provider == "huggingface":
        return settings.HF_MODEL
    if provider == "fireworks":
        return settings.FIREWORKS_MODEL
    return "built-in"


def list_llm_providers() -> list[dict[str, str | bool]]:
    """Return provider metadata for the frontend selector (no secrets)."""
    catalog: list[tuple[str, str]] = [
        ("stub", "Built-in stub"),
        ("openai", "OpenAI"),
        ("gemini", "Google Gemini"),
        ("anthropic", "Anthropic Claude"),
        ("ollama", "Ollama (local)"),
        ("huggingface", "Hugging Face"),
        ("fireworks", "Fireworks AI"),
    ]
    return [
        {
            "id": pid,
            "label": label,
            "model": _provider_model(pid),
            "configured": _provider_configured(pid),
        }
        for pid, label in catalog
    ]


SYSTEM_PROMPT = (
    "You are analyzing anonymized football fan messages.\n"
    "Rules:\n"
    "- The message has already been anonymized.\n"
    "- Do not infer, recreate, or invent names, emails, phone numbers, addresses, "
    "member IDs, order IDs, booking IDs, or social handles.\n"
    "- Analyze only the provided masked message.\n"
    "- Return only valid JSON.\n"
    "- Do not include personal data in the summary or recommended action."
)


def build_user_prompt(masked_message: str) -> str:
    return (
        "Masked message:\n"
        f"{masked_message}\n\n"
        "Return:\n"
        "{\n"
        '  "sentiment": "positive | neutral | negative | mixed",\n'
        '  "topic": "ticket_pricing | ticket_booking | refund | booking_problem | merchandise | '
        "parking | accessibility | stadium_experience | stadium_food | food | security | "
        "streaming | membership | loyalty_points | mobile_app | away_travel | entry_queue | "
        'family_seating | other",\n'
        '  "intent": "complaint | question | refund_request | praise | cancellation | '
        'support_request | feedback",\n'
        '  "urgency": "low | medium | high",\n'
        '  "summary": "One sentence without personal data.",\n'
        '  "recommended_action": "One short operational action."\n'
        "}"
    )


def active_provider_info() -> tuple[str, str]:
    """Return (provider_label, model_name) for the currently configured LLM.

    Used to populate ``llm_provider`` / ``llm_model`` in the API response so
    the frontend can show which model was called.
    """
    provider = settings.LLM_PROVIDER.lower()
    if provider == "openai" and settings.OPENAI_API_KEY:
        return "openai", settings.OPENAI_MODEL
    if provider == "gemini" and settings.GEMINI_API_KEY:
        return "gemini", settings.GEMINI_MODEL
    if provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        return "anthropic", settings.ANTHROPIC_MODEL
    if provider == "ollama":
        return "ollama", settings.OLLAMA_MODEL
    if provider == "huggingface" and settings.HF_API_KEY:
        return "huggingface", settings.HF_MODEL
    if provider == "fireworks" and settings.FIREWORKS_API_KEY:
        return "fireworks", settings.FIREWORKS_MODEL
    return "stub", "built-in"


def analyze_masked_message(
    masked_message: str,
    provider_override: str | None = None,
) -> tuple[Analysis | None, str, str]:
    """Dispatch to the configured provider; fall back to the stub on errors.

    Returns ``(analysis, provider_used, model_used)`` so the caller always
    knows which model actually produced the result — even if a silent fallback
    to the stub occurred.
    """

    provider = (provider_override or settings.LLM_PROVIDER).lower()
    if provider not in ALLOWED_LLM_PROVIDERS:
        provider = settings.LLM_PROVIDER.lower()

    if provider == "gemini" and settings.GEMINI_API_KEY:
        try:
            return _gemini_call(masked_message), "gemini", settings.GEMINI_MODEL
        except Exception as exc:
            logger.warning("Gemini call failed, falling back to stub: %s", exc)
            return stub_analyze(masked_message), "stub", "built-in"

    if provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        try:
            return _anthropic_call(masked_message), "anthropic", settings.ANTHROPIC_MODEL
        except Exception as exc:
            logger.warning("Anthropic call failed, falling back to stub: %s", exc)
            return stub_analyze(masked_message), "stub", "built-in"

    if provider == "ollama":
        try:
            return _ollama_call(masked_message), "ollama", settings.OLLAMA_MODEL
        except Exception as exc:
            logger.warning("Ollama call failed, falling back to stub: %s", exc)
            return stub_analyze(masked_message), "stub", "built-in"

    if provider == "huggingface" and settings.HF_API_KEY:
        try:
            return _hf_call(masked_message), "huggingface", settings.HF_MODEL
        except Exception as exc:
            logger.warning("HuggingFace call failed, falling back to stub: %s", exc)
            return stub_analyze(masked_message), "stub", "built-in"

    if provider == "openai" and settings.OPENAI_API_KEY:
        try:
            return _openai_call(masked_message), "openai", settings.OPENAI_MODEL
        except Exception as exc:
            logger.warning("OpenAI call failed, falling back to stub: %s", exc)
            return stub_analyze(masked_message), "stub", "built-in"

    if provider == "fireworks" and settings.FIREWORKS_API_KEY:
        try:
            return _fireworks_call(masked_message), "fireworks", settings.FIREWORKS_MODEL
        except Exception as exc:
            logger.warning("Fireworks call failed, falling back to stub: %s", exc)
            return stub_analyze(masked_message), "stub", "built-in"

    return stub_analyze(masked_message), "stub", "built-in"


# ---------------------------------------------------------------------------
# Stub provider — keyword heuristic, deterministic enough for a demo.
# ---------------------------------------------------------------------------


def stub_analyze(masked_message: str) -> Analysis:
    """Lightweight rule-based analysis so the demo runs without an API key."""

    msg = masked_message.lower()

    sentiment = _stub_sentiment(msg)
    topic = _stub_topic(msg)
    intent = _stub_intent(msg)
    urgency = _stub_urgency(msg, sentiment)

    summary = _stub_summary(topic, intent, sentiment)
    action = _stub_action(topic, intent, urgency)

    return Analysis(
        sentiment=sentiment,
        topic=topic,
        intent=intent,
        urgency=urgency,
        summary=summary,
        recommended_action=action,
    )


_NEG_WORDS = {
    "angry",
    "frustrated",
    "bad",
    "worst",
    "terrible",
    "refund",
    "broken",
    "complain",
    "delayed",
    "stolen",
    "rude",
    "unfair",
    "schlimm",
    "schlecht",
    "verärgert",
    "wütend",
    "kaputt",
    "problem",
    "issue",
    "stuck",
    "lost",
    "waited",
    "expensive",
    "overpriced",
    "ripoff",
    "scam",
    "disappointed",
    "ignored",
}
_POS_WORDS = {
    "thanks",
    "thank",
    "great",
    "amazing",
    "love",
    "excellent",
    "fantastic",
    "danke",
    "super",
    "wunderbar",
    "klasse",
}


def _stub_sentiment(msg: str) -> Sentiment:
    neg = sum(1 for w in _NEG_WORDS if w in msg)
    pos = sum(1 for w in _POS_WORDS if w in msg)
    if neg > 0 and pos > 0:
        return Sentiment.mixed
    if neg > pos and neg >= 1:
        return Sentiment.negative
    if pos > neg and pos >= 1:
        return Sentiment.positive
    return Sentiment.neutral


def _stub_topic(msg: str) -> Topic:
    candidates: list[tuple[Topic, list[str]]] = [
        (Topic.refund, ["refund", "rückerstattung", "money back", "charged twice"]),
        (Topic.ticket_booking, ["[booking_id", "buchung", "ticket booking", "buy ticket"]),
        (Topic.booking_problem, ["booking problem", "booking error", "booking issue"]),
        (Topic.ticket_pricing, ["price", "preis", "expensive", "cost", "kosten", "ticket price"]),
        (Topic.merchandise, ["jersey", "shirt", "trikot", "scarf", "shop", "store"]),
        (Topic.parking, ["parking", "parken", "park"]),
        (Topic.accessibility, ["wheelchair", "rollstuhl", "accessib", "barriere"]),
        (Topic.stadium_food, ["bratwurst", "stadium food", "food stall", "kiosk"]),
        (Topic.food, ["food", "essen", "drink", "beer"]),
        (Topic.security, ["security", "steward", "fight", "sicherheit"]),
        (Topic.streaming, ["stream", "broadcast", "tv", "übertragung"]),
        (Topic.loyalty_points, ["loyalty", "points", "reward", "treuepunkte"]),
        (Topic.mobile_app, ["app", "mobile", "smartphone", "push notification"]),
        (Topic.away_travel, ["away", "auswärts", "travel", "coach", "train to"]),
        (Topic.entry_queue, ["entry", "entrance", "turnstile", "eingang", "queue"]),
        (Topic.family_seating, ["family", "familien", "child", "kids", "seating"]),
        (Topic.membership, ["member", "mitglied", "[member_id"]),
        (Topic.stadium_experience, ["gate", "block", "stand", "stadium", "stadion"]),
    ]
    for topic, keywords in candidates:
        if any(k in msg for k in keywords):
            return topic
    return Topic.other


def _stub_intent(msg: str) -> Intent:
    if "refund" in msg or "rückerstattung" in msg:
        return Intent.refund_request
    if any(w in msg for w in ("cancel", "stornieren", "kündigen")):
        return Intent.cancellation
    if any(w in msg for w in ("?", "how do", "wie kann", "warum", "why")):
        return Intent.question
    if any(w in msg for w in ("thanks", "great", "love", "danke", "super")):
        return Intent.praise
    if any(w in msg for w in ("help", "support", "hilfe")):
        return Intent.support_request
    if any(w in msg for w in ("complain", "issue", "problem", "broken", "kaputt")):
        return Intent.complaint
    return Intent.feedback


def _stub_urgency(msg: str, sentiment: Sentiment) -> Urgency:
    if any(w in msg for w in ("urgent", "asap", "today", "tonight", "sofort", "dringend")):
        return Urgency.high
    if sentiment == Sentiment.negative:
        return Urgency.medium
    return Urgency.low


def _stub_summary(topic: Topic, intent: Intent, sentiment: Sentiment) -> str:
    return (
        f"A fan submitted a {sentiment.value} message about {topic.value.replace('_', ' ')} "
        f"with intent {intent.value.replace('_', ' ')}."
    )


def _stub_action(topic: Topic, intent: Intent, urgency: Urgency) -> str:
    if intent == Intent.refund_request:
        return "Review the booking or order and follow the refund policy."
    if intent == Intent.cancellation:
        return "Confirm cancellation eligibility and notify the fan in writing."
    if intent == Intent.complaint and urgency == Urgency.high:
        return "Escalate to on-duty operations lead within one hour."
    if intent == Intent.support_request:
        return "Route to the relevant support queue with topic context."
    if intent == Intent.praise:
        return "Acknowledge and forward to the team responsible."
    return f"Acknowledge the message and tag it under {topic.value.replace('_', ' ')}."


# ---------------------------------------------------------------------------
# OpenAI provider — masked message only, never the raw text.
# ---------------------------------------------------------------------------


def _openai_call(masked_message: str) -> Analysis | None:
    """Call OpenAI's chat-completions API with strict JSON expectations."""

    url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(masked_message)},
    ]
    body: dict[str, Any] = {
        "model": settings.OPENAI_MODEL,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": messages,
    }

    with httpx.Client(timeout=20.0) as client:
        resp = client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        payload = resp.json()

    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        logger.warning("OpenAI response missing content")
        return None

    analysis = parse_llm_payload(content)
    if analysis is not None:
        return analysis

    # One retry with a stricter instruction.
    messages.append({"role": "user", "content": "Return ONLY valid JSON, no prose."})
    with httpx.Client(timeout=20.0) as client:
        resp = client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        payload = resp.json()
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None
    return parse_llm_payload(content)


# ---------------------------------------------------------------------------
# Fireworks AI provider — OpenAI-compatible, masked message only.
# ---------------------------------------------------------------------------


def _fireworks_call(masked_message: str) -> Analysis | None:
    """Call Fireworks AI via its OpenAI-compatible chat/completions endpoint."""

    url = f"{settings.FIREWORKS_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.FIREWORKS_API_KEY}",
        "Content-Type": "application/json",
    }
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(masked_message)},
    ]
    body: dict[str, Any] = {
        "model": settings.FIREWORKS_MODEL,
        "temperature": 0.1,
        "max_tokens": 1024,
        "response_format": {"type": "json_object"},
        "messages": messages,
    }

    with httpx.Client(timeout=20.0) as client:
        resp = client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        payload = resp.json()

    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        logger.warning("Fireworks response missing content")
        return None

    return parse_llm_payload(content)


# ---------------------------------------------------------------------------
# Gemini provider — masked message only, never the raw text.
# ---------------------------------------------------------------------------


def _gemini_call(masked_message: str) -> Analysis | None:
    """Call Google Gemini's generateContent API."""

    url = (
        f"{settings.GEMINI_BASE_URL.rstrip('/')}/models/"
        f"{settings.GEMINI_MODEL}:generateContent"
        f"?key={settings.GEMINI_API_KEY}"
    )
    body = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": build_user_prompt(masked_message)}]}],
        "generationConfig": {"temperature": 0.1, "response_mime_type": "application/json"},
    }

    with httpx.Client(timeout=20.0) as client:
        resp = client.post(url, json=body)
        resp.raise_for_status()
        payload = resp.json()

    try:
        content = payload["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        logger.warning("Gemini response missing content")
        return None

    return parse_llm_payload(content)


# ---------------------------------------------------------------------------
# Anthropic/Claude provider — masked message only, never the raw text.
# ---------------------------------------------------------------------------


def _anthropic_call(masked_message: str) -> Analysis | None:
    """Call Anthropic's Messages API."""

    url = f"{settings.ANTHROPIC_BASE_URL.rstrip('/')}/messages"
    headers = {
        "x-api-key": settings.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": settings.ANTHROPIC_MODEL,
        "max_tokens": 512,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": build_user_prompt(masked_message)}],
    }

    with httpx.Client(timeout=20.0) as client:
        resp = client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        payload = resp.json()

    try:
        content = payload["content"][0]["text"]
    except (KeyError, IndexError, TypeError):
        logger.warning("Anthropic response missing content")
        return None

    return parse_llm_payload(content)


# ---------------------------------------------------------------------------
# Ollama provider — local open-source LLMs, masked message only.
# ---------------------------------------------------------------------------


def _ollama_call(masked_message: str) -> Analysis | None:
    """Call a local Ollama instance."""

    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    body = {
        "model": settings.OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(masked_message)},
        ],
    }

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, json=body)
        resp.raise_for_status()
        payload = resp.json()

    try:
        content = payload["message"]["content"]
    except (KeyError, TypeError):
        logger.warning("Ollama response missing content")
        return None

    return parse_llm_payload(content)


# ---------------------------------------------------------------------------
# HuggingFace Inference API — masked message only, never the raw text.
# ---------------------------------------------------------------------------


def _hf_call(masked_message: str) -> Analysis | None:
    """Call the HuggingFace Inference API."""

    url = f"{settings.HF_BASE_URL.rstrip('/')}/{settings.HF_MODEL}"
    headers = {
        "Authorization": f"Bearer {settings.HF_API_KEY}",
    }
    body = {
        "inputs": f"{SYSTEM_PROMPT}\n\n{build_user_prompt(masked_message)}",
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.1,
            "return_full_text": False,
        },
    }

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        payload = resp.json()

    try:
        content = payload[0]["generated_text"]
    except (KeyError, IndexError, TypeError):
        logger.warning("HuggingFace response missing content")
        return None

    return parse_llm_payload(content)


# Re-export so callers can mock easily in tests.
__all__ = [
    "SYSTEM_PROMPT",
    "ALLOWED_LLM_PROVIDERS",
    "analyze_masked_message",
    "build_user_prompt",
    "list_llm_providers",
    "stub_analyze",
    "_gemini_call",
    "_anthropic_call",
    "_ollama_call",
    "_hf_call",
]


# Suppress unused-import warning for re used in tests.
_ = re
