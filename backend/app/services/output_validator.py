"""LLM output validator — pure functions, no I/O.

Validates the JSON shape and enum membership of the LLM analysis payload.
If anything looks off, callers should fall back to a safe default rather
than show garbage to the user.
"""

from __future__ import annotations

import json
import logging
import re

from pydantic import ValidationError

from app.schemas import Analysis
from app.services.safety_gate import sanitize_llm_output

logger = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


def parse_llm_payload(raw: str) -> Analysis | None:
    """Best-effort: parse JSON, validate schema, scrub any leaked PII."""

    if not raw or not raw.strip():
        return None

    cleaned = _FENCE_RE.sub("", raw.strip()).strip()
    # Some models prefix with `{` after metadata — trim to first JSON object.
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace == -1 or last_brace == -1 or last_brace <= first_brace:
        return None
    candidate = cleaned[first_brace : last_brace + 1]

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as exc:
        logger.warning("LLM output not valid JSON: %s", exc)
        return None

    if not isinstance(data, dict):
        return None

    # Scrub summary / recommended_action through the final PII gate.
    for field in ("summary", "recommended_action"):
        value = data.get(field)
        if isinstance(value, str):
            sanitized, was_clean = sanitize_llm_output(value)
            if not was_clean:
                logger.warning("LLM output contained PII in %s — sanitized", field)
            data[field] = sanitized

    try:
        return Analysis.model_validate(data)
    except ValidationError as exc:
        logger.warning("LLM output failed schema validation: %s", exc)
        return None
