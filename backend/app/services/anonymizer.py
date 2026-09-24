"""Anonymizer — replaces detected spans with stable readable placeholders.

Rules implemented from the PRD:
- `Lukas Weber → [NAME_1]`, `Berlin → [CITY_1]`, etc.
- Stable numbering per message: the same entity type increments per detection
  in document order.
- Replace from end to start so character offsets remain valid.
- Overlapping detections are already deduped by `pii_detector.detect_pii`,
  but the algorithm is robust if they reappear.
- Returns both the masked message and a list of `DetectedPii` records that
  carry only metadata (no original value).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.schemas import DetectedPii, PiiType
from app.services.pii_detector import PiiSpan


@dataclass
class AnonymizationResult:
    masked_message: str
    detected: list[DetectedPii]


def anonymize(text: str, spans: list[PiiSpan]) -> AnonymizationResult:
    """Replace each span with `[TYPE_N]` and return the masked message + records."""

    if not spans:
        return AnonymizationResult(masked_message=text, detected=[])

    # Sort spans by start position for stable numbering, then replace from end -> start.
    ordered = sorted(spans, key=lambda s: s.start)

    counters: dict[PiiType, int] = {}
    placeholders: list[tuple[PiiSpan, str]] = []
    for span in ordered:
        counters[span.type] = counters.get(span.type, 0) + 1
        placeholders.append((span, f"[{span.type.value}_{counters[span.type]}]"))

    # Apply replacements from rightmost to leftmost.
    masked = text
    for span, replacement in reversed(placeholders):
        masked = masked[: span.start] + replacement + masked[span.end :]

    detected = [
        DetectedPii(
            type=span.type,
            start=span.start,
            end=span.end,
            replacement=replacement,
            confidence=span.confidence,
        )
        for span, replacement in placeholders
    ]
    return AnonymizationResult(masked_message=masked, detected=detected)
