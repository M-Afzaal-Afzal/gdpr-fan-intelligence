"""Second PII scan — the gate that decides whether the LLM is allowed to run.

This module is intentionally minimal. The real defence-in-depth comes from:
1. Running the same `detect_pii` function on the masked message.
2. Ignoring our own placeholders (`[NAME_1]`, `[EMAIL_2]`...).
3. Returning a structured decision the orchestrator can audit-log.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.services.pii_detector import PiiSpan, detect_pii

_PLACEHOLDER_RE = re.compile(
    r"\[(NAME|EMAIL|PHONE|CITY|ADDRESS|MEMBER_ID|ORDER_ID|"
    r"BOOKING_ID|SOCIAL_HANDLE)_\d+\]"
)


@dataclass(frozen=True)
class GateDecision:
    """Outcome of the safety gate."""

    safe: bool
    residual_spans: list[PiiSpan]
    reason: str | None = None


def evaluate_masked(masked_message: str) -> GateDecision:
    """Decide whether `masked_message` may be sent to the LLM."""

    if not masked_message.strip():
        return GateDecision(safe=False, residual_spans=[], reason="Empty masked message")

    # Detect PII *ignoring* our own placeholders. We do this by blanking them
    # out with same-length spaces so offsets in downstream messages stay sane.
    scrubbed = _PLACEHOLDER_RE.sub(lambda m: " " * (m.end() - m.start()), masked_message)
    spans = detect_pii(scrubbed)

    if spans:
        return GateDecision(
            safe=False,
            residual_spans=spans,
            reason="PII still detected after masking",
        )
    return GateDecision(safe=True, residual_spans=[], reason=None)


def sanitize_llm_output(text: str) -> tuple[str, bool]:
    """Final PII scan for LLM-generated text.

    Returns (sanitized_text, was_clean). If PII is found we replace it inline
    so the user never sees raw PII even if the model invented some.
    """

    if not text:
        return text, True

    spans = detect_pii(text)
    if not spans:
        return text, True

    # Replace from right to left to preserve offsets.
    out = text
    for span in sorted(spans, key=lambda s: s.start, reverse=True):
        out = out[: span.start] + f"[{span.type.value}_REDACTED]" + out[span.end :]
    return out, False
