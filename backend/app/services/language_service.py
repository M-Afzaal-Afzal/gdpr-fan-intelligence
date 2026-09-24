"""Lightweight language detection for EN / DE / mixed.

We intentionally avoid bringing in a heavy language model. The signal we
need is coarse: pick the spaCy NER model and tell the dashboard whether
the message is English, German, or a mix. A keyword-frequency heuristic
is plenty for the hackathon corpus and is deterministic in tests.
"""

from __future__ import annotations

import re

from app.schemas import Language

_DE_TOKENS: set[str] = {
    "ich",
    "und",
    "nicht",
    "ist",
    "habe",
    "haben",
    "mein",
    "meine",
    "der",
    "die",
    "das",
    "ein",
    "eine",
    "aus",
    "auf",
    "mit",
    "für",
    "warum",
    "wie",
    "wer",
    "wo",
    "was",
    "wann",
    "kein",
    "keine",
    "hallo",
    "danke",
    "bitte",
    "leider",
    "schon",
    "noch",
    "über",
    "kann",
    "könnte",
    "möchte",
    "muss",
    "sollte",
    "wegen",
    "wenn",
    "telefonnummer",
    "bestellung",
    "buchung",
    "stadion",
    "spiel",
    "straße",
    "platz",
    "weg",
    "allee",
    "hausnummer",
}

_EN_TOKENS: set[str] = {
    "the",
    "and",
    "is",
    "are",
    "was",
    "were",
    "i",
    "my",
    "you",
    "your",
    "we",
    "they",
    "their",
    "have",
    "has",
    "from",
    "with",
    "for",
    "this",
    "that",
    "want",
    "need",
    "please",
    "thanks",
    "thank",
    "hello",
    "hi",
    "refund",
    "booking",
    "ticket",
    "order",
    "match",
    "stadium",
    "game",
    "team",
    "club",
    "support",
    "help",
}


_TOKEN_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+")


def detect_language(text: str) -> Language:
    """Return the dominant language for a fan message."""

    if not text or not text.strip():
        return Language.unknown

    tokens = [tok.lower() for tok in _TOKEN_RE.findall(text)]
    if not tokens:
        return Language.unknown

    de_hits = sum(1 for t in tokens if t in _DE_TOKENS)
    en_hits = sum(1 for t in tokens if t in _EN_TOKENS)

    # Umlaut/ß is a strong DE signal
    if re.search(r"[äöüÄÖÜß]", text):
        de_hits += 2

    if de_hits == 0 and en_hits == 0:
        return Language.unknown
    if de_hits > 0 and en_hits > 0:
        ratio = min(de_hits, en_hits) / max(de_hits, en_hits)
        if ratio >= 0.35:
            return Language.mixed
    if de_hits > en_hits:
        return Language.de
    return Language.en
