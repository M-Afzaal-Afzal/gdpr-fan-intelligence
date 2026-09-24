"""Layered PII detector.

Layers
------
1. Regex — structured entities (email, phone, member/order/booking IDs, handles).
2. Presidio NER — names, locations, addresses (when the model is available).
3. German custom rules — street-name suffixes (Straße, Str., Platz, Weg, Allee...).
4. Hard-negative protection — never mask "Gate C", "Block 12", "Berlin derby" etc.

The detector is deliberately stateless and pure: it takes a string and returns a
list of *spans*. Anonymization is a separate concern (see anonymizer.py).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.schemas import PiiType

logger = logging.getLogger(__name__)

# Try to load Presidio. If the model is missing in dev, we degrade gracefully —
# regex + German rules still cover the structured cases.
try:
    from presidio_analyzer import AnalyzerEngine  # type: ignore
    from presidio_analyzer.nlp_engine import NlpEngineProvider  # type: ignore

    _PRESIDIO_AVAILABLE = True
except Exception:  # pragma: no cover
    AnalyzerEngine = None  # type: ignore
    NlpEngineProvider = None  # type: ignore
    _PRESIDIO_AVAILABLE = False


# ---------------------------------------------------------------------------
# Span objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PiiSpan:
    """A single detected PII span (no original value carried around)."""

    type: PiiType
    start: int
    end: int
    confidence: float

    def overlaps(self, other: PiiSpan) -> bool:
        return self.start < other.end and other.start < self.end


# ---------------------------------------------------------------------------
# Layer 1 — Regex
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")

# Phones: international (+49), DE with leading 0, generic with country code,
# and dashed formats. We require >=7 digits to avoid catching scores like "3-1".
_PHONE_RE = re.compile(
    r"""
    (?<!\w)
    (?:
        \+?\d{1,3}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,5}
      | 0\d{2,4}[\s\-]?\d{3,5}[\s\-]?\d{2,5}
      | \(?\d{3,4}\)?[\s\-]\d{3,4}[\s\-]\d{3,5}
    )
    (?!\w)
    """,
    re.VERBOSE,
)

# Domain IDs — covers EN and DE variants found in real datasets.
# MEMBER_ID: MEM-, MEMBER-, FAN-, MITGLIED- (German)
_MEMBER_ID_RE = re.compile(r"\b(?:MEM|MEMBER|FAN|MITGLIED)[-_]?\d{3,10}\b", re.IGNORECASE)
# ORDER_ID: ORD-, ORDER-, SHOP-, BEST- (common e-commerce/ticketing prefixes)
_ORDER_ID_RE = re.compile(
    r"\b(?:ORD|ORDER|SHOP|BEST)[-_]?\d{3,10}(?:[-_][A-Z]{2})?\b", re.IGNORECASE
)
# BOOKING_ID: BK-, BOOK-, BOOKING-, TKT- (ticketing) — optional alphanumeric suffix
_BOOKING_ID_RE = re.compile(
    r"\b(?:BK|BOOK|BOOKING|TKT)[-_]?\d{3,10}(?:[-_][A-Z0-9]{1,6})?\b", re.IGNORECASE
)
_SOCIAL_HANDLE_RE = re.compile(r"(?<![A-Za-z0-9_])@[A-Za-z0-9_]{3,30}\b")

# Layer 3 — German address-like rules
_GERMAN_STREET_RE = re.compile(
    # NOTE: 'ring' is intentionally excluded — with IGNORECASE it matched common
    # English words ("during", "spring", "bring") and over-masked them as ADDRESS.
    r"\b[A-ZÄÖÜ][A-Za-zÄÖÜäöüß\-]+(?:straße|strasse|str\.|platz|weg|allee|gasse)\b"
    r"(?:\s+\d{1,4}[a-z]?)?",
    re.IGNORECASE,
)
_GERMAN_HOUSENUMBER_RE = re.compile(r"\bHausnummer\s+\d{1,4}[a-z]?\b", re.IGNORECASE)

# Common DE/EN city anchor list. Presidio NER is the main detector for cities;
# this fallback only kicks in for messages where Presidio is unavailable.
_KNOWN_CITIES: set[str] = {
    "berlin",
    "münchen",
    "munich",
    "hamburg",
    "köln",
    "cologne",
    "frankfurt",
    "stuttgart",
    "düsseldorf",
    "duesseldorf",
    "leipzig",
    "dortmund",
    "essen",
    "bremen",
    "hannover",
    "nürnberg",
    "nuremberg",
    "dresden",
    "bochum",
    "bonn",
    "mainz",
    "wolfsburg",
    "augsburg",
    "freiburg",
    "münster",
    "karlsruhe",
    "leverkusen",
    "schalke",
    "gelsenkirchen",
    "mönchengladbach",
    "kiel",
    "rostock",
}
_CITY_FALLBACK_RE = re.compile(
    r"\b(" + "|".join(sorted(_KNOWN_CITIES, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)

# Name fallback: catches self-introduction names even when Presidio/spaCy is
# unavailable or misses an uncommon/lowercase name (e.g. "I am afzaal").
# We fire on explicit introduction triggers, capture up to three following
# tokens (any case), then trim with a stopword guard so we never mask things
# like "I am very angry" or "I am from Hamburg".
_NAME_INTRO_RE = re.compile(
    r"\b(?:I\s+am|I'm|this\s+is|my\s+name\s+is|ich\s+bin|mein\s+Name\s+ist)\s+"
    r"([A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß'\-]+(?:\s+[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß'\-]+){0,2})",
    re.IGNORECASE,
)
# Referral phrasing: "i want bilal to be my friend" — Presidio misses lowercase names.
_NAME_WANT_TO_BE_RE = re.compile(
    r"\bwant\s+"
    r"([A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß'\-]+(?:\s+[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß'\-]+){0,2})"
    r"\s+to\s+be\b",
    re.IGNORECASE,
)
_NAME_TRIGGER_PATTERNS: tuple[re.Pattern[str], ...] = (_NAME_INTRO_RE, _NAME_WANT_TO_BE_RE)
_NAME_TOKEN_RE = re.compile(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß'\-]*")

# Words that commonly follow an intro trigger but are NOT names. If the first
# captured token is one of these we skip; otherwise we trim at the first one.
_NAME_STOPWORDS: set[str] = {
    # English articles / prepositions / conjunctions / pronouns
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "so",
    "to",
    "of",
    "for",
    "with",
    "from",
    "in",
    "on",
    "at",
    "here",
    "there",
    "about",
    "my",
    "your",
    "his",
    "her",
    "their",
    "our",
    "this",
    "that",
    # English aux / fillers / verbs
    "not",
    "no",
    "very",
    "really",
    "quite",
    "too",
    "just",
    "still",
    "also",
    "currently",
    "now",
    "writing",
    "contacting",
    "reaching",
    "trying",
    "looking",
    "asking",
    "wondering",
    "having",
    "getting",
    "going",
    "unable",
    "able",
    "done",
    "new",
    "old",
    # English feelings / adjectives
    "sorry",
    "happy",
    "glad",
    "sad",
    "angry",
    "upset",
    "mad",
    "furious",
    "frustrated",
    "annoyed",
    "disappointed",
    "unhappy",
    "fine",
    "ok",
    "okay",
    "good",
    "bad",
    "great",
    "sure",
    "afraid",
    "confused",
    "concerned",
    "worried",
    "interested",
    "waiting",
    "fed",
    "tired",
    "sick",
    "unacceptable",
    "ridiculous",
    "frustrating",
    "terrible",
    "awful",
    "disgusted",
    "livid",
    # German equivalents
    "sehr",
    "nicht",
    "aus",
    "hier",
    "froh",
    "traurig",
    "sauer",
    "wütend",
    "enttäuscht",
    "verärgert",
    "ein",
    "eine",
    "der",
    "die",
    "das",
    "kein",
    "keine",
    "noch",
    "schon",
    "gerade",
    "immer",
    "mir",
    "mich",
    "nur",
    "total",
    "ziemlich",
    "echt",
    "wirklich",
    "und",
    "oder",
    "aber",
    "müde",
    "krank",
    "fertig",
    "böse",
    "glücklich",
    "unzufrieden",
}


# ---------------------------------------------------------------------------
# Layer 4 — Hard-negative football vocabulary
# ---------------------------------------------------------------------------

_FOOTBALL_HARD_NEGATIVES: list[re.Pattern[str]] = [
    re.compile(r"\bGate\s+[A-Z0-9]+\b", re.IGNORECASE),
    re.compile(r"\bBlock\s+\d+[A-Z]?\b", re.IGNORECASE),
    re.compile(r"\bMatch\s*Day\s+\d+\b", re.IGNORECASE),
    re.compile(r"\b(?:Family|South|North|East|West)\s+Stand\b", re.IGNORECASE),
    re.compile(
        r"\b(?:Berlin|Munich|Dortmund|Hamburg|Köln|Cologne|Leipzig)\s+derby\b", re.IGNORECASE
    ),
    re.compile(
        r"\b(?:Bayern|Dortmund|Schalke|Leipzig|Hamburg|Köln|Cologne)\s+"
        r"(?:home|away)\s+game\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:Bayern|Dortmund|Schalke|Leipzig|Hertha|Werder)\s+match\b", re.IGNORECASE),
    re.compile(r"\bFamily\s+Stand\b", re.IGNORECASE),
    re.compile(r"\bmember[-_\s]?only\b", re.IGNORECASE),
]


def _is_in_hard_negative(text: str, start: int, end: int) -> bool:
    """Return True if [start,end) overlaps with a protected football phrase."""

    for pat in _FOOTBALL_HARD_NEGATIVES:
        for m in pat.finditer(text):
            if m.start() < end and start < m.end():
                return True
    return False


# ---------------------------------------------------------------------------
# Presidio singleton — lazy load
# ---------------------------------------------------------------------------

_analyzer: AnalyzerEngine | None = None


def _get_analyzer() -> AnalyzerEngine | None:
    """Return a memoised Presidio analyzer, or None if unavailable."""

    global _analyzer
    if not _PRESIDIO_AVAILABLE:
        return None
    if _analyzer is not None:
        return _analyzer
    try:
        provider = NlpEngineProvider(
            nlp_configuration={
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
            }
        )
        _analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["en"])
    except Exception as exc:  # pragma: no cover
        logger.warning("Presidio unavailable, falling back to regex-only: %s", exc)
        _analyzer = None
    return _analyzer


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_pii(text: str) -> list[PiiSpan]:
    """Run all layers and return a merged, non-overlapping span list.

    The returned spans are sorted by `start`. Overlapping spans are deduped,
    keeping the highest-confidence span (preferring structured/regex hits).
    """

    if not text:
        return []

    spans: list[PiiSpan] = []
    spans.extend(_regex_layer(text))
    spans.extend(_presidio_layer(text))
    spans.extend(_german_layer(text))
    # Intro-name fallback runs ALWAYS — Presidio NER still misses lowercase or
    # uncommon names, so this is a defence-in-depth layer, not just a stand-in.
    spans.extend(_name_fallback(text))

    # Filter hard-negatives before dedup so we don't drop valid PII by accident.
    spans = [s for s in spans if not _is_in_hard_negative(text, s.start, s.end)]

    # Remove over-broad Presidio NAME spans that wholly contain a German ADDRESS
    # match (e.g. Presidio tags "Treffen am Marienplatz" as PERSON while the
    # German-rule layer correctly identifies "Marienplatz" as ADDRESS).
    address_spans = [s for s in spans if s.type == PiiType.ADDRESS]
    if address_spans:
        spans = [
            s
            for s in spans
            if not (
                s.type == PiiType.NAME
                and any(s.start <= a.start and s.end >= a.end for a in address_spans)
            )
        ]

    # Sort + dedup overlaps. Prefer structured > NAME/CITY/ADDRESS, then higher confidence.
    spans.sort(key=lambda s: (s.start, -_type_priority(s.type), -s.confidence))
    deduped: list[PiiSpan] = []
    for span in spans:
        if any(span.overlaps(kept) for kept in deduped):
            continue
        deduped.append(span)
    deduped.sort(key=lambda s: s.start)
    return deduped


def has_pii(text: str) -> bool:
    """Convenience wrapper used by the safety gate."""

    return bool(detect_pii(text))


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


_STRUCTURED_TYPES: set[PiiType] = {
    PiiType.EMAIL,
    PiiType.PHONE,
    PiiType.MEMBER_ID,
    PiiType.ORDER_ID,
    PiiType.BOOKING_ID,
    PiiType.SOCIAL_HANDLE,
}


def _type_priority(t: PiiType) -> int:
    if t in _STRUCTURED_TYPES:
        return 3
    if t == PiiType.ADDRESS:
        # German-rule regex hits are highly precise; ADDRESS beats NAME in dedup.
        return 2
    if t == PiiType.NAME:
        return 1
    return 0


def _regex_layer(text: str) -> list[PiiSpan]:
    spans: list[PiiSpan] = []
    for pat, ptype, conf in (
        (_EMAIL_RE, PiiType.EMAIL, 1.0),
        (_PHONE_RE, PiiType.PHONE, 0.95),
        (_MEMBER_ID_RE, PiiType.MEMBER_ID, 1.0),
        (_ORDER_ID_RE, PiiType.ORDER_ID, 1.0),
        (_BOOKING_ID_RE, PiiType.BOOKING_ID, 1.0),
        (_SOCIAL_HANDLE_RE, PiiType.SOCIAL_HANDLE, 0.97),
    ):
        for m in pat.finditer(text):
            spans.append(PiiSpan(type=ptype, start=m.start(), end=m.end(), confidence=conf))
    return spans


def _german_layer(text: str) -> list[PiiSpan]:
    spans: list[PiiSpan] = []
    for m in _GERMAN_STREET_RE.finditer(text):
        spans.append(PiiSpan(type=PiiType.ADDRESS, start=m.start(), end=m.end(), confidence=0.9))
    for m in _GERMAN_HOUSENUMBER_RE.finditer(text):
        spans.append(PiiSpan(type=PiiType.ADDRESS, start=m.start(), end=m.end(), confidence=0.9))
    return spans


# Minimum Presidio confidence thresholds per entity type.
# NAME: raised to 0.75 to cut football-venue false positives (stadium names,
# club names, stand names all score ~0.5–0.7 as PERSON).
# GPE/LOCATION: raised to 0.80 to avoid tagging country/venue references.
_PRESIDIO_SCORE_THRESHOLD: dict[str, float] = {
    "PERSON": 0.75,
    "LOCATION": 0.80,
    "GPE": 0.80,
}


def _presidio_layer(text: str) -> list[PiiSpan]:
    analyzer = _get_analyzer()
    if analyzer is None:
        # Name fallback is added centrally in detect_pii; here we only need the
        # offline city fallback since Presidio NER is unavailable.
        return _city_fallback(text)

    try:
        results = analyzer.analyze(
            text=text,
            language="en",
            entities=["PERSON", "LOCATION", "GPE", "NRP", "ORGANIZATION"],
        )
    except Exception as exc:  # pragma: no cover
        logger.warning("Presidio analyze failed, using fallback: %s", exc)
        return _city_fallback(text)

    spans: list[PiiSpan] = []
    for r in results:
        ptype = _map_presidio_entity(r.entity_type)
        if ptype is None:
            continue
        score = float(getattr(r, "score", 0.6))
        threshold = _PRESIDIO_SCORE_THRESHOLD.get(r.entity_type, 0.5)
        if score < threshold:
            continue
        spans.append(
            PiiSpan(
                type=ptype,
                start=int(r.start),
                end=int(r.end),
                confidence=score,
            )
        )
    spans.extend(_city_fallback(text))
    return spans


def _map_presidio_entity(entity: str) -> PiiType | None:
    if entity == "PERSON":
        return PiiType.NAME
    if entity in {"LOCATION", "GPE"}:
        return PiiType.CITY
    return None


def _city_fallback(text: str) -> list[PiiSpan]:
    """Catch obvious DE/EN city names without a NER model loaded."""

    spans: list[PiiSpan] = []
    for m in _CITY_FALLBACK_RE.finditer(text):
        spans.append(PiiSpan(type=PiiType.CITY, start=m.start(), end=m.end(), confidence=0.85))
    return spans


def _name_span_from_capture(match: re.Match[str]) -> PiiSpan | None:
    """Turn trigger-regex group 1 into a NAME span, or None if stopwords reject it."""

    group = match.group(1)
    base = match.start(1)
    tokens = list(_NAME_TOKEN_RE.finditer(group))
    if not tokens:
        return None
    # If the very first token is a stopword, this is not a name.
    if tokens[0].group(0).lower() in _NAME_STOPWORDS:
        return None
    # Keep the leading run of non-stopword tokens.
    kept = []
    for tok in tokens:
        if tok.group(0).lower() in _NAME_STOPWORDS:
            break
        kept.append(tok)
    if not kept:
        return None
    start = base + kept[0].start()
    end = base + kept[-1].end()
    return PiiSpan(type=PiiType.NAME, start=start, end=end, confidence=0.7)


def _name_fallback(text: str) -> list[PiiSpan]:
    """Heuristic NAME detection via introduction and referral triggers.

    Catches names Presidio may miss (lowercase or uncommon). The captured group
    is the candidate name; we trim it with a stopword guard so phrases like
    "I am very angry" or "I want to be happy" do not get masked as names.
    """

    spans: list[PiiSpan] = []
    for pattern in _NAME_TRIGGER_PATTERNS:
        for m in pattern.finditer(text):
            span = _name_span_from_capture(m)
            if span is not None:
                spans.append(span)
    return spans
