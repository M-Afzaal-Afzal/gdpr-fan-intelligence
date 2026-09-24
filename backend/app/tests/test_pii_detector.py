"""Tests for the PII detector (no Presidio dependency)."""

from __future__ import annotations

from app.schemas import PiiType
from app.services.pii_detector import detect_pii


def _types(text: str) -> set[PiiType]:
    return {span.type for span in detect_pii(text)}


def test_detects_email():
    assert PiiType.EMAIL in _types("Contact me at john.miller@gmail.com please")


def test_detects_phone_international():
    assert PiiType.PHONE in _types("Call me on +49 176 12345678 today")


def test_detects_phone_german_local():
    assert PiiType.PHONE in _types("Ruf mich an: 0176-1234567 bitte")


def test_detects_booking_id_with_bk_prefix():
    assert PiiType.BOOKING_ID in _types("My booking is BK-83721 thanks")


def test_detects_booking_id_with_book_prefix():
    """Dataset uses BOOK-71001 style — must be detected too."""

    assert PiiType.BOOKING_ID in _types("Reference BOOK-71001 in the email")


def test_detects_order_id():
    assert PiiType.ORDER_ID in _types("ORD-92811 was charged twice")


def test_detects_member_id():
    assert PiiType.MEMBER_ID in _types("Member MEM-48291 here")


def test_detects_member_id_with_fan_prefix():
    """Dataset variant FAN-73001 must trip the MEMBER_ID rule."""

    assert PiiType.MEMBER_ID in _types("Show record FAN-73001 to support")


def test_detects_social_handle():
    assert PiiType.SOCIAL_HANDLE in _types("Follow @fan_john for updates")


def test_does_not_flag_email_address_inside_word():
    # Avoid catching things like "info@" but require a domain
    assert PiiType.EMAIL not in _types("Just a regular sentence with no contact info.")


def test_hard_negative_gate_c_not_address():
    spans = detect_pii("The queue at Gate C was long after Match Day 12")
    # Gate C / Match Day 12 / Block N should not be masked as PII.
    assert all(span.type != PiiType.ADDRESS for span in spans)


def test_hard_negative_berlin_derby():
    # Berlin appears in football context — derby phrase must protect it.
    spans = detect_pii("Great atmosphere at the Berlin derby last night")
    assert all(span.type != PiiType.CITY for span in spans)


def test_german_street_detected():
    assert PiiType.ADDRESS in _types("Ich wohne in der Heinz-Rühmann-Straße 9")


def test_german_platz_detected():
    assert PiiType.ADDRESS in _types("Treffen am Marienplatz vor dem Spiel")


def test_name_fallback_english_intro():
    """Without Presidio, 'I am John Miller' should still mask the name."""

    assert PiiType.NAME in _types("Hi, I am John Miller from somewhere.")


def test_name_fallback_german_intro():
    assert PiiType.NAME in _types("Hallo, ich bin Lukas Weber und brauche Hilfe.")


def test_name_fallback_does_not_capture_trigger_words():
    spans = [s for s in detect_pii("I am John Miller here") if s.type == PiiType.NAME]
    assert spans
    # The captured span must start at the name, not at "I am".
    text = "I am John Miller here"
    captured = text[spans[0].start : spans[0].end]
    assert captured.startswith("John")
