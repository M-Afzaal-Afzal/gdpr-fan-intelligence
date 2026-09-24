"""Build Raumdeuter-Pitch.pptx — brand-matched 3-minute pitch deck.

Mirrors the interactive HTML deck in pitch/index.html. Multi-slide progressive
reveal stands in for the HTML's JS animations (PowerPoint's standard idiom).
Slide transition: subtle Push from the right. Push to advance with arrow / click.

Run:
    cd pitch/_build
    uv venv .venv --python 3.12
    uv pip install --python .venv/bin/python python-pptx pillow
    .venv/bin/python ../build_pptx.py
"""
from __future__ import annotations

import copy
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import nsmap, qn
from pptx.util import Emu, Inches, Pt

# ============================================================================
# BRAND
# ============================================================================
# Approximations of the project's oklch tokens from frontend/app/globals.css.
BG = RGBColor(0xF5, 0xF2, 0xEA)        # warm off-white
FG = RGBColor(0x1A, 0x21, 0x32)        # dark slate-blue
CARD = RGBColor(0xFD, 0xFB, 0xF4)
MUTED = RGBColor(0xEC, 0xE8, 0xDD)
MUTED_FG = RGBColor(0x6E, 0x74, 0x82)
BORDER = RGBColor(0xD3, 0xCE, 0xBF)
PRIMARY = RGBColor(0x1F, 0x6B, 0x47)   # brand green
PRIMARY_FG = RGBColor(0xFD, 0xFB, 0xF4)
ACCENT = RGBColor(0xE6, 0xE2, 0xD3)
DESTRUCTIVE = RGBColor(0xB8, 0x2F, 0x21)
DESTRUCTIVE_TINT = RGBColor(0xF6, 0xE6, 0xE2)
WARNING = RGBColor(0xCD, 0x71, 0x1F)
MASK_FG = RGBColor(0x2C, 0x4E, 0x84)
MASK_BG = RGBColor(0xDA, 0xE5, 0xF2)
PIPELINE_BLUE = RGBColor(0x39, 0x66, 0x9E)
# Dimmed / off variants for progressive-reveal sequences
DIM_BORDER = RGBColor(0xE5, 0xE1, 0xD3)
DIM_FG = RGBColor(0xBC, 0xB6, 0xA6)
DIM_BG = RGBColor(0xF7, 0xF4, 0xEA)
ACTIVE_TINT = RGBColor(0xEC, 0xF4, 0xEF)  # very light green for the just-lit card

FONT_SANS = "Calibri"            # widely installed; brand identity carried by color
FONT_MONO = "Consolas"

# ============================================================================
# CANVAS
# ============================================================================
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
PAD_X = Inches(0.9)
PAD_Y = Inches(0.65)
CONTENT_W = SLIDE_W - 2 * PAD_X

QR_PATH = Path(__file__).parent / "_build" / "qr.png"


# ============================================================================
# HELPERS
# ============================================================================
def set_slide_bg(slide, color: RGBColor) -> None:
    """Paint the entire slide background a flat color."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(
    slide, x, y, w, h, *,
    fill=None, line=None, line_w: float | None = None,
    radius: float | None = None,
    shape=MSO_SHAPE.RECTANGLE,
):
    """Add a rectangle (with optional rounded corners) shape."""
    shp = slide.shapes.add_shape(shape, x, y, w, h)
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        if line_w is not None:
            shp.line.width = Pt(line_w)
    # python-pptx doesn't expose corner radius adjustment; if MSO_SHAPE.ROUNDED_RECTANGLE
    # the default radius is fine for our purposes.
    return shp


def add_text(
    slide, x, y, w, h, text, *,
    font=FONT_SANS,
    size=Pt(18),
    color=FG,
    bold=False,
    italic=False,
    align=PP_ALIGN.LEFT,
    anchor=MSO_ANCHOR.TOP,
    spacing: float | None = None,
):
    """Add a text box with one or more runs."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.auto_size = None

    p = tf.paragraphs[0]
    p.alignment = align
    if spacing is not None:
        p.line_spacing = spacing
    r = p.add_run()
    r.text = text
    f = r.font
    f.name = font
    f.size = size
    f.color.rgb = color
    f.bold = bold
    f.italic = italic
    return tb


def add_rich(
    slide, x, y, w, h, runs, *,
    align=PP_ALIGN.LEFT,
    anchor=MSO_ANCHOR.TOP,
    spacing: float | None = None,
    default_font=FONT_SANS,
    default_size=Pt(18),
    default_color=FG,
):
    """Add a text box with multiple runs.

    `runs` is a list of dicts: {text, font?, size?, color?, bold?, italic?}.
    """
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.auto_size = None

    first = True
    for run_data in runs:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            if run_data.get("new_paragraph"):
                p = tf.add_paragraph()
            # otherwise keep adding runs to same paragraph
        p.alignment = align
        if spacing is not None:
            p.line_spacing = spacing
        r = p.add_run()
        r.text = run_data["text"]
        f = r.font
        f.name = run_data.get("font", default_font)
        f.size = run_data.get("size", default_size)
        f.color.rgb = run_data.get("color", default_color)
        f.bold = run_data.get("bold", False)
        f.italic = run_data.get("italic", False)
        if run_data.get("strike"):
            # PowerPoint strike attribute on rPr
            rPr = r._r.get_or_add_rPr()
            rPr.set("strike", "sngStrike")
    return tb


def add_brand_header(slide, badge: str | None = None) -> None:
    """Top brand mark on every slide.

    Optional `badge` (top-right) is used by multi-step sections to show
    progress, e.g. "STAGE 03 / 05" on the pipeline build slides.
    """
    icon_size = Inches(0.34)
    icon_x = PAD_X
    icon_y = PAD_Y - Inches(0.05)
    icon = add_rect(
        slide, icon_x, icon_y, icon_size, icon_size,
        fill=PRIMARY, line=None,
        shape=MSO_SHAPE.ROUNDED_RECTANGLE,
    )
    # Triangle inside the icon (BrandMark)
    tri = slide.shapes.add_shape(
        MSO_SHAPE.ISOSCELES_TRIANGLE,
        icon_x + Inches(0.07), icon_y + Inches(0.07),
        Inches(0.2), Inches(0.2),
    )
    tri.fill.background()
    tri.line.color.rgb = PRIMARY_FG
    tri.line.width = Pt(1.25)
    tri.shadow.inherit = False

    add_text(
        slide, icon_x + Inches(0.45), icon_y + Inches(-0.03),
        Inches(2.5), Inches(0.25),
        "Raumdeuter", size=Pt(11), bold=True, color=FG,
    )
    add_text(
        slide, icon_x + Inches(0.45), icon_y + Inches(0.16),
        Inches(2.5), Inches(0.25),
        "Fan Intelligence", size=Pt(9), color=MUTED_FG,
    )

    if badge:
        badge_w = Inches(1.7)
        badge_x = SLIDE_W - PAD_X - badge_w
        badge_y = PAD_Y - Inches(0.05)
        add_rect(
            slide, badge_x, badge_y, badge_w, Inches(0.32),
            fill=CARD, line=PRIMARY, line_w=1.0,
            shape=MSO_SHAPE.ROUNDED_RECTANGLE,
        )
        add_text(
            slide, badge_x, badge_y + Inches(0.05),
            badge_w, Inches(0.22),
            badge,
            font=FONT_MONO, size=Pt(9), color=PRIMARY,
            align=PP_ALIGN.CENTER, bold=True,
            anchor=MSO_ANCHOR.MIDDLE,
        )


def add_eyebrow(slide, text: str, y=Inches(2.0)) -> None:
    add_text(
        slide, PAD_X, y, CONTENT_W, Inches(0.3),
        text.upper(),
        size=Pt(10), bold=True, color=PRIMARY,
    )


def add_h1(slide, text: str, y=Inches(2.4), color=FG, size=Pt(54),
           w=None, align=PP_ALIGN.LEFT) -> None:
    add_text(
        slide, PAD_X, y, w or CONTENT_W, Inches(2.0),
        text, size=size, bold=True, color=color, align=align,
        spacing=1.05,
    )


def add_h2(slide, text: str, y=Inches(2.4), color=FG, size=Pt(36),
           w=None, align=PP_ALIGN.LEFT) -> None:
    add_text(
        slide, PAD_X, y, w or CONTENT_W, Inches(1.5),
        text, size=size, bold=True, color=color, align=align,
        spacing=1.1,
    )


def add_h3(slide, text: str, y=Inches(2.4), color=FG, size=Pt(24),
           w=None, align=PP_ALIGN.LEFT) -> None:
    add_text(
        slide, PAD_X, y, w or CONTENT_W, Inches(0.9),
        text, size=size, bold=True, color=color, align=align,
        spacing=1.15,
    )


def add_lead(slide, text: str, y, color=MUTED_FG, size=Pt(16),
             w=None, align=PP_ALIGN.LEFT) -> None:
    add_text(
        slide, PAD_X, y, w or Inches(8.5), Inches(2.0),
        text, size=size, color=color, align=align, spacing=1.3,
    )


def add_pill(slide, x, y, text: str, *, dot=False, color_text=MUTED_FG,
             font=FONT_SANS, w=Inches(1.8), h=Inches(0.32)):
    add_rect(
        slide, x, y, w, h,
        fill=CARD, line=BORDER, line_w=0.75,
        shape=MSO_SHAPE.ROUNDED_RECTANGLE,
    )
    text_x = x + (Inches(0.3) if dot else Inches(0.15))
    if dot:
        d_size = Inches(0.08)
        d = add_rect(
            slide, x + Inches(0.15), y + Inches(0.12),
            d_size, d_size,
            fill=PRIMARY,
            shape=MSO_SHAPE.OVAL,
        )
    add_text(
        slide, text_x, y + Inches(0.04),
        w - (text_x - x) - Inches(0.05), Inches(0.25),
        text, size=Pt(10), color=color_text, font=font,
        anchor=MSO_ANCHOR.MIDDLE,
    )


def set_push_transition(slide) -> None:
    """Add a 'Push' transition from the right (matches HTML slide animation)."""
    sld = slide._element
    nsmap_p = sld.nsmap.get("p")
    if nsmap_p is None:
        nsmap_p = "http://schemas.openxmlformats.org/presentationml/2006/main"
    transition_xml = (
        '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'spd="med" advClick="1">'
        '<p:push dir="r"/>'
        '</p:transition>'
    )
    transition = etree.fromstring(transition_xml)
    sld.append(transition)


# ============================================================================
# SLIDE BUILDERS
# ============================================================================
def build_slide_hook(prs):
    """Slide 1 — Hook."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(s, BG)
    add_brand_header(s)
    set_push_transition(s)

    add_eyebrow(s, "Raumdeuter AI Hackathon · Privacy-First Fan Intelligence",
                y=Inches(1.6))

    # Hook headline with strikethrough on "AI"
    add_rich(
        s, PAD_X, Inches(2.0), CONTENT_W, Inches(2.8),
        [
            {"text": "What if your "},
            {"text": "AI", "strike": True, "color": DESTRUCTIVE},
            {"text": " just leaked your"},
        ],
        default_size=Pt(60), default_color=FG, spacing=1.0,
    )
    # python-pptx doesn't reliably wrap long rich-text — split into two paragraphs.
    add_text(
        s, PAD_X, Inches(3.05), CONTENT_W, Inches(1.0),
        "fans to OpenAI?",
        size=Pt(60), bold=True, color=FG, spacing=1.0,
    )

    add_lead(
        s,
        "Every club wants AI on fan messages. Every fan message is full of "
        "names, emails, booking IDs, addresses. Most pipelines just forward it.",
        y=Inches(4.5),
        w=Inches(10.5),
    )

    # Bottom meta pills
    bottom_y = SLIDE_H - PAD_Y - Inches(0.6)
    add_pill(s, PAD_X, bottom_y, "Live now", dot=True, w=Inches(1.3))
    add_pill(s, PAD_X + Inches(1.4), bottom_y,
             "fan-pulse-guard.vercel.app", font=FONT_MONO, w=Inches(2.7))
    add_pill(s, PAD_X + Inches(4.2), bottom_y, "3 min", font=FONT_MONO,
             w=Inches(0.9))
    add_text(
        s, SLIDE_W - PAD_X - Inches(4.0), bottom_y + Inches(0.05),
        Inches(4.0), Inches(0.25),
        "Raumdeuter AI Hackathon · 2026",
        size=Pt(10), color=MUTED_FG, font=FONT_MONO,
        align=PP_ALIGN.RIGHT,
    )


def build_slide_problem(prs):
    """Slide 2 — Problem (€20M static + 3 pain points)."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(s, BG)
    add_brand_header(s)
    set_push_transition(s)

    add_eyebrow(s, "The problem", y=Inches(1.4))
    add_h2(
        s,
        "Football clubs are sitting on millions of fan messages — and they can't use them.",
        y=Inches(1.75),
        w=Inches(10.5),
    )

    # Left: pain points
    points = [
        ("01", "Fans send everything.",
         "Names, emails, phones, addresses, booking IDs — in one breath, in two languages."),
        ("02", "Clubs want insight.",
         "What are fans angry about? Who needs a refund? What's the matchday issue today?"),
        ("03", "Sending raw text to GPT = GDPR breach.",
         "Personal data leaves the EU. Stored on third-party servers. Never deletable."),
    ]
    py = Inches(3.55)
    for num, head, body in points:
        # left red accent bar
        add_rect(s, PAD_X, py, Inches(0.06), Inches(0.95), fill=DESTRUCTIVE)
        add_rect(
            s, PAD_X + Inches(0.06), py, Inches(5.5), Inches(0.95),
            fill=CARD, line=BORDER, line_w=0.6,
        )
        add_text(
            s, PAD_X + Inches(0.22), py + Inches(0.13),
            Inches(0.5), Inches(0.3),
            num, size=Pt(11), color=DESTRUCTIVE, font=FONT_MONO, bold=True,
        )
        add_rich(
            s, PAD_X + Inches(0.7), py + Inches(0.1),
            Inches(4.7), Inches(0.85),
            [
                {"text": head, "bold": True, "color": FG, "size": Pt(13)},
                {"text": " " + body, "color": MUTED_FG, "size": Pt(11)},
            ],
            spacing=1.35,
        )
        py += Inches(1.05)

    # Right: €20M fine counter (static final state)
    rx = Inches(7.4)
    rw = SLIDE_W - PAD_X - rx
    ry = Inches(3.55)
    rh = Inches(3.1)
    add_rect(
        s, rx, ry, rw, rh,
        fill=CARD, line=BORDER, line_w=0.6,
        shape=MSO_SHAPE.ROUNDED_RECTANGLE,
    )
    add_text(
        s, rx, ry + Inches(0.4),
        rw, Inches(0.3),
        "MAX GDPR FINE (ART. 83)",
        size=Pt(10), color=MUTED_FG, align=PP_ALIGN.CENTER, bold=True,
    )
    add_text(
        s, rx, ry + Inches(0.85),
        rw, Inches(1.3),
        "€20M",
        size=Pt(78), bold=True, color=DESTRUCTIVE,
        align=PP_ALIGN.CENTER, font=FONT_MONO,
    )
    add_text(
        s, rx, ry + Inches(2.2),
        rw, Inches(0.3),
        "or 4% of global turnover — whichever is higher",
        size=Pt(10), color=MUTED_FG, align=PP_ALIGN.CENTER, font=FONT_MONO,
    )
    add_text(
        s, rx, ry + Inches(2.55),
        rw, Inches(0.3),
        "This is the wall every club hits before they ship.",
        size=Pt(9), color=MUTED_FG, align=PP_ALIGN.CENTER,
    )


def build_slide_insight(prs, *, reveal_second: bool):
    """Slide 3 — Insight (2-step build).

    Step 1: only "Mask first." is shown.
    Step 2: + "Analyze second." (green) + the lead paragraph appear.
    """
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(s, BG)
    add_brand_header(s, badge="STEP 2 / 2" if reveal_second else "STEP 1 / 2")
    set_push_transition(s)

    add_eyebrow(s, "Our insight", y=Inches(2.0))
    add_text(
        s, PAD_X, Inches(2.5), CONTENT_W, Inches(1.4),
        "Mask first.",
        size=Pt(96), bold=True, color=FG, spacing=1.0,
    )
    if reveal_second:
        add_text(
            s, PAD_X, Inches(3.85), CONTENT_W, Inches(1.4),
            "Analyze second.",
            size=Pt(96), bold=True, color=PRIMARY, spacing=1.0,
        )
        add_lead(
            s,
            "Privacy is step 1 of the pipeline, not a final check. "
            "Raw PII never crosses a service boundary, never reaches the LLM, "
            "never lands in the database — by architecture, not by promise.",
            y=Inches(5.35),
            w=Inches(10.5),
        )


PIPELINE_STAGES = [
    ("01 · DETECT", "PII Scan",
     "Regex + Presidio NER + German rules + hard negatives"),
    ("02 · MASK", "Anonymize",
     "Stable [NAME_1], [EMAIL_1] placeholders"),
    ("03 · GATE", "Safety Gate",
     "Second PII scan on masked text — blocks if any leak"),
    ("04 · LLM", "Analyze",
     "Stub or OpenAI — only masked text leaves the box"),
    ("05 · VALIDATE", "Final Scrub",
     "Output re-scanned + JSON validated before storage"),
]


def build_slide_pipeline_step(prs, *, stages_lit: int):
    """Slide 4 — Pipeline (5-step progressive reveal).

    Cards 1..stages_lit are fully lit (green border, brand colors).
    Cards stages_lit+1..5 are dimmed (gray border, muted text).
    Connecting arrows light up only when *both* adjacent stages are lit.
    The "What gets stored" footer appears only on the final reveal (5/5).
    """
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(s, BG)
    add_brand_header(s, badge=f"STAGE {stages_lit:02d} / 05")
    set_push_transition(s)

    add_eyebrow(s, "How it works", y=Inches(1.4))
    add_h3(
        s,
        "One Python boundary. Five stages. Raw PII dies at stage 2.",
        y=Inches(1.75),
        w=Inches(11),
    )

    # Progress dot row at the top of the card area
    dot_row_y = Inches(2.85)
    dot_d = Inches(0.16)
    dot_gap = Inches(0.18)
    dot_total_w = dot_d * 5 + dot_gap * 4
    dot_x0 = (SLIDE_W - dot_total_w) / 2
    for i in range(5):
        dx = dot_x0 + i * (dot_d + dot_gap)
        is_lit = (i + 1) <= stages_lit
        add_rect(
            s, dx, dot_row_y, dot_d, dot_d,
            fill=PRIMARY if is_lit else DIM_BORDER,
            shape=MSO_SHAPE.OVAL,
        )
        # connecting line between dots
        if i < 4:
            line_y = dot_row_y + dot_d / 2 - Emu(7000)
            line_x = dx + dot_d
            line_lit = (i + 2) <= stages_lit
            add_rect(
                s, line_x, line_y, dot_gap, Emu(14000),
                fill=PRIMARY if line_lit else DIM_BORDER,
            )

    # Stage cards
    gap = Inches(0.18)
    total_gap = gap * (len(PIPELINE_STAGES) - 1)
    card_w = (CONTENT_W - total_gap) / len(PIPELINE_STAGES)
    card_h = Inches(2.05)
    card_y = Inches(3.35)
    arrow_y = card_y + card_h / 2 - Inches(0.15)

    for i, (num, name, desc) in enumerate(PIPELINE_STAGES):
        cx = PAD_X + (card_w + gap) * i
        is_lit = (i + 1) <= stages_lit
        is_active = (i + 1) == stages_lit  # the one that *just* lit up

        if is_lit:
            border_color = PRIMARY
            border_w = 2.0 if is_active else 1.25
            fill_color = ACTIVE_TINT if is_active else CARD
            num_color = PRIMARY
            name_color = FG
            desc_color = MUTED_FG
        else:
            border_color = DIM_BORDER
            border_w = 0.75
            fill_color = DIM_BG
            num_color = DIM_FG
            name_color = DIM_FG
            desc_color = DIM_FG

        add_rect(
            s, cx, card_y, card_w, card_h,
            fill=fill_color, line=border_color, line_w=border_w,
            shape=MSO_SHAPE.ROUNDED_RECTANGLE,
        )
        # Small "● ACTIVE" pip on the just-lit card (top-right of card)
        if is_active:
            pip_size = Inches(0.13)
            add_rect(
                s, cx + card_w - pip_size - Inches(0.15),
                card_y + Inches(0.15),
                pip_size, pip_size,
                fill=PRIMARY, shape=MSO_SHAPE.OVAL,
            )
        add_text(
            s, cx + Inches(0.1), card_y + Inches(0.2),
            card_w - Inches(0.2), Inches(0.25),
            num, size=Pt(9), color=num_color, font=FONT_MONO,
            align=PP_ALIGN.CENTER, bold=True,
        )
        add_text(
            s, cx + Inches(0.1), card_y + Inches(0.55),
            card_w - Inches(0.2), Inches(0.4),
            name, size=Pt(14), color=name_color, bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(
            s, cx + Inches(0.1), card_y + Inches(1.0),
            card_w - Inches(0.2), Inches(1.0),
            desc, size=Pt(9), color=desc_color, align=PP_ALIGN.CENTER,
            spacing=1.3,
        )
        # Arrow to next card (lit only if both adjacent stages are lit)
        if i < len(PIPELINE_STAGES) - 1:
            ax = cx + card_w + Inches(0.01)
            arrow_lit = (i + 2) <= stages_lit
            add_text(
                s, ax, arrow_y, gap, Inches(0.3),
                "→", size=Pt(16),
                color=PRIMARY if arrow_lit else DIM_BORDER,
                bold=True,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
            )

    # Bottom note about storage — only on the final reveal (5/5)
    note_y = card_y + card_h + Inches(0.45)
    note_h = Inches(0.9)
    if stages_lit == 5:
        add_rect(
            s, PAD_X, note_y, CONTENT_W, note_h,
            fill=MASK_BG, line=None,
            shape=MSO_SHAPE.ROUNDED_RECTANGLE,
        )
        add_rich(
            s, PAD_X + Inches(0.3), note_y + Inches(0.15),
            CONTENT_W - Inches(0.6), note_h - Inches(0.3),
            [
                {"text": "What gets stored: ", "bold": True, "color": MASK_FG, "size": Pt(13)},
                {"text": "masked message + PII metadata (type, offset — ", "color": MASK_FG, "size": Pt(12)},
                {"text": "no entity_value column", "font": FONT_MONO, "color": MASK_FG, "bold": True, "size": Pt(11)},
                {"text": ") + analysis + a SHA-256 of the raw input. ", "color": MASK_FG, "size": Pt(12)},
                {"text": "That's it.", "color": MASK_FG, "bold": True, "size": Pt(12)},
            ],
            spacing=1.3, anchor=MSO_ANCHOR.MIDDLE,
        )
    else:
        # Helpful hint while building
        hint = f"Stage {stages_lit} of 5 lit · click to advance"
        add_text(
            s, PAD_X, note_y + Inches(0.3), CONTENT_W, Inches(0.3),
            hint, font=FONT_MONO, size=Pt(10), color=MUTED_FG,
            align=PP_ALIGN.CENTER,
        )


def _demo_panels(s, *, highlights: bool, masked_filled: bool, status_kind: str):
    """Render the two demo panels (used by the 4 demo build slides)."""
    # Headline + try-on-phone pill
    add_eyebrow(s, "Live · A real fan complaint", y=Inches(1.4))
    add_h3(
        s,
        "Watch personal data turn into placeholders in milliseconds.",
        y=Inches(1.75),
        w=Inches(7.4),
    )
    # Try on phone pill (top right)
    pill_w = Inches(4.2)
    pill_x = SLIDE_W - PAD_X - pill_w
    pill_y = Inches(1.8)
    add_rect(
        s, pill_x, pill_y, pill_w, Inches(0.7),
        fill=CARD, line=PRIMARY, line_w=1.5,
        shape=MSO_SHAPE.ROUNDED_RECTANGLE,
    )
    # green dot
    add_rect(
        s, pill_x + Inches(0.22), pill_y + Inches(0.29),
        Inches(0.13), Inches(0.13),
        fill=PRIMARY, shape=MSO_SHAPE.OVAL,
    )
    add_text(
        s, pill_x + Inches(0.5), pill_y + Inches(0.1),
        pill_w - Inches(0.55), Inches(0.22),
        "TRY IT ON YOUR PHONE",
        size=Pt(8), bold=True, color=PRIMARY,
    )
    add_text(
        s, pill_x + Inches(0.5), pill_y + Inches(0.33),
        pill_w - Inches(0.55), Inches(0.3),
        "fan-pulse-guard.vercel.app",
        size=Pt(14), color=FG, font=FONT_MONO, bold=True,
    )

    # Panels
    panel_y = Inches(2.85)
    panel_h = Inches(3.5)
    panel_gap = Inches(0.3)
    panel_w = (CONTENT_W - panel_gap) / 2

    # ---------------- LEFT PANEL (raw) ----------------
    add_rect(
        s, PAD_X, panel_y, Inches(0.06), panel_h, fill=DESTRUCTIVE,
    )
    add_rect(
        s, PAD_X + Inches(0.06), panel_y, panel_w - Inches(0.06), panel_h,
        fill=CARD, line=BORDER, line_w=0.5,
    )
    # Red dot + label
    add_rect(
        s, PAD_X + Inches(0.3), panel_y + Inches(0.3),
        Inches(0.13), Inches(0.13),
        fill=DESTRUCTIVE, shape=MSO_SHAPE.OVAL,
    )
    add_text(
        s, PAD_X + Inches(0.5), panel_y + Inches(0.27),
        panel_w - Inches(0.6), Inches(0.25),
        "RAW FAN MESSAGE", size=Pt(9), bold=True, color=DESTRUCTIVE,
    )

    # Raw text body
    raw_body_y = panel_y + Inches(0.75)
    if highlights:
        # PII highlighted in red boxes
        add_rich(
            s, PAD_X + Inches(0.3), raw_body_y,
            panel_w - Inches(0.6), panel_h - Inches(0.95),
            [
                {"text": "Hallo team, ich bin "},
                {"text": "Lukas Weber", "color": DESTRUCTIVE, "bold": True},
                {"text": " from "},
                {"text": "München", "color": DESTRUCTIVE, "bold": True},
                {"text": ". Email: "},
                {"text": "lukas.weber@gmail.com", "color": DESTRUCTIVE, "bold": True},
                {"text": ", phone "},
                {"text": "+49 176 12345678", "color": DESTRUCTIVE, "bold": True},
                {"text": ". My booking "},
                {"text": "BK-92811", "color": DESTRUCTIVE, "bold": True},
                {"text": " was charged twice after Match Day 12 — please refund. "
                         "Gate C was chaos too."},
            ],
            default_font=FONT_MONO, default_size=Pt(13), default_color=FG,
            spacing=1.55,
        )
    else:
        add_text(
            s, PAD_X + Inches(0.3), raw_body_y,
            panel_w - Inches(0.6), panel_h - Inches(0.95),
            "Hallo team, ich bin Lukas Weber from München. "
            "Email: lukas.weber@gmail.com, phone +49 176 12345678. "
            "My booking BK-92811 was charged twice after Match Day 12 — "
            "please refund. Gate C was chaos too.",
            font=FONT_MONO, size=Pt(13), color=FG, spacing=1.55,
        )

    # ---------------- RIGHT PANEL (masked) ----------------
    rpx = PAD_X + panel_w + panel_gap
    add_rect(
        s, rpx, panel_y, Inches(0.06), panel_h, fill=PRIMARY,
    )
    add_rect(
        s, rpx + Inches(0.06), panel_y, panel_w - Inches(0.06), panel_h,
        fill=CARD, line=BORDER, line_w=0.5,
    )
    add_rect(
        s, rpx + Inches(0.3), panel_y + Inches(0.3),
        Inches(0.13), Inches(0.13),
        fill=PRIMARY, shape=MSO_SHAPE.OVAL,
    )
    add_text(
        s, rpx + Inches(0.5), panel_y + Inches(0.27),
        panel_w - Inches(0.6), Inches(0.25),
        "WHAT THE LLM SEES", size=Pt(9), bold=True, color=PRIMARY,
    )

    if masked_filled:
        add_rich(
            s, rpx + Inches(0.3), panel_y + Inches(0.75),
            panel_w - Inches(0.6), panel_h - Inches(0.95),
            [
                {"text": "Hallo team, ich bin "},
                {"text": "[NAME_1]", "color": MASK_FG, "bold": True},
                {"text": " from "},
                {"text": "[CITY_1]", "color": MASK_FG, "bold": True},
                {"text": ". Email: "},
                {"text": "[EMAIL_1]", "color": MASK_FG, "bold": True},
                {"text": ", phone "},
                {"text": "[PHONE_1]", "color": MASK_FG, "bold": True},
                {"text": ". My booking "},
                {"text": "[BOOKING_ID_1]", "color": MASK_FG, "bold": True},
                {"text": " was charged twice after Match Day 12 — please refund. "
                         "Gate C was chaos too."},
            ],
            default_font=FONT_MONO, default_size=Pt(13), default_color=FG,
            spacing=1.55,
        )
    else:
        add_text(
            s, rpx + Inches(0.3), panel_y + Inches(0.75),
            panel_w - Inches(0.6), panel_h - Inches(0.95),
            "(LLM hasn't seen anything yet)",
            font=FONT_MONO, size=Pt(12), color=MUTED_FG, italic=True,
        )

    # Status bar at bottom
    status_y = panel_y + panel_h + Inches(0.3)
    if status_kind == "ready":
        add_rich(
            s, PAD_X, status_y, CONTENT_W, Inches(0.3),
            [
                {"text": "Ready. ", "bold": True, "color": FG, "size": Pt(11),
                 "font": FONT_MONO},
                {"text": "Press Space or click to run the masking.",
                 "color": MUTED_FG, "size": Pt(11), "font": FONT_MONO},
            ],
        )
    elif status_kind == "detect":
        add_rich(
            s, PAD_X, status_y, CONTENT_W, Inches(0.3),
            [
                {"text": "Stage 1/5 · Detect ", "bold": True, "color": FG,
                 "size": Pt(11), "font": FONT_MONO},
                {"text": "— scanning for PII…", "color": MUTED_FG,
                 "size": Pt(11), "font": FONT_MONO},
            ],
        )
    elif status_kind == "mask":
        add_rich(
            s, PAD_X, status_y, CONTENT_W, Inches(0.3),
            [
                {"text": "Stage 2/5 · Mask ", "bold": True, "color": FG,
                 "size": Pt(11), "font": FONT_MONO},
                {"text": "— replacing with stable placeholders…",
                 "color": MUTED_FG, "size": Pt(11), "font": FONT_MONO},
            ],
        )
    elif status_kind == "done":
        add_rich(
            s, PAD_X, status_y, CONTENT_W, Inches(0.3),
            [
                {"text": "✓ Done. ", "bold": True, "color": PRIMARY,
                 "size": Pt(11), "font": FONT_MONO},
                {"text": "5 entities masked · 0 leaked · 612ms total",
                 "color": FG, "size": Pt(11), "font": FONT_MONO},
            ],
        )


def build_slide_demo_step(prs, *, highlights, masked_filled, status_kind, step):
    """Slide 5 sub-steps — demo progressive reveal."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(s, BG)
    add_brand_header(s, badge=f"STEP {step:02d} / 04")
    set_push_transition(s)
    _demo_panels(
        s,
        highlights=highlights,
        masked_filled=masked_filled,
        status_kind=status_kind,
    )


def build_slide_moat(prs):
    """Slide 6 — The moat."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(s, BG)
    add_brand_header(s)
    set_push_transition(s)

    add_eyebrow(s, "Why this is hard · Our moat", y=Inches(1.4))
    add_h3(
        s,
        "Anyone can call an LLM. Almost nobody gets the masking layer right.",
        y=Inches(1.75),
        w=Inches(11.5),
    )

    cards = [
        ("4×", "Detection layers",
         "Regex + Presidio NER + German address rules + football hard negatives so "
         "“Gate C”, “Match Day 12”, “Block 14” stay unmasked.", PRIMARY),
        ("0", "entity_value columns",
         "PII values are not just hashed — they are never persisted. "
         "Even a full DB dump can't reconstruct them.", PIPELINE_BLUE),
        ("2×", "Safety scans",
         "One on the input after masking (blocks the LLM if any leak survives), "
         "one on the LLM's output before storage.", PRIMARY),
        ("77 / 77", "Tests passing · 0% leakage",
         "Hostile prompts, prompt-injection, mixed EN/DE, lowercase names, "
         "intro-only names — all covered.", PIPELINE_BLUE),
    ]
    cy0 = Inches(2.85)
    ch = Inches(1.55)
    cw = (CONTENT_W - Inches(0.3)) / 2
    for i, (big, head, body, accent) in enumerate(cards):
        col = i % 2
        row = i // 2
        cx = PAD_X + col * (cw + Inches(0.3))
        cy = cy0 + row * (ch + Inches(0.25))
        add_rect(s, cx, cy, Inches(0.06), ch, fill=accent)
        add_rect(
            s, cx + Inches(0.06), cy, cw - Inches(0.06), ch,
            fill=CARD, line=BORDER, line_w=0.5,
        )
        add_text(
            s, cx + Inches(0.3), cy + Inches(0.15),
            cw - Inches(0.5), Inches(0.4),
            big, size=Pt(22), bold=True, color=accent, font=FONT_MONO,
        )
        add_text(
            s, cx + Inches(0.3), cy + Inches(0.55),
            cw - Inches(0.5), Inches(0.3),
            head, size=Pt(13), bold=True, color=FG,
        )
        add_text(
            s, cx + Inches(0.3), cy + Inches(0.9),
            cw - Inches(0.5), Inches(0.65),
            body, size=Pt(10), color=MUTED_FG, spacing=1.35,
        )

    # Bottom rules summary
    rules_y = Inches(6.45)
    add_rect(
        s, PAD_X, rules_y, CONTENT_W, Inches(0.55),
        fill=ACCENT, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
    )
    add_rich(
        s, PAD_X + Inches(0.3), rules_y + Inches(0.13),
        CONTENT_W - Inches(0.6), Inches(0.3),
        [
            {"text": "10 / 10 ", "color": PRIMARY, "bold": True,
             "font": FONT_MONO, "size": Pt(12)},
            {"text": "hard privacy rules baked into the architecture · ",
             "color": FG, "size": Pt(11)},
            {"text": "raw PII never reaches the LLM · never stored · "
                     "blocked at the gate if any leak survives",
             "color": MUTED_FG, "size": Pt(11), "italic": True},
        ],
        anchor=MSO_ANCHOR.MIDDLE,
    )


def build_slide_impact(prs, *, reveal_stakeholders: bool):
    """Slide 7 — Impact (2-step build).

    Step 1: headline + three big stats.
    Step 2: + stakeholder cards at the bottom.
    """
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(s, BG)
    add_brand_header(
        s,
        badge="STEP 2 / 2" if reveal_stakeholders else "STEP 1 / 2",
    )
    set_push_transition(s)

    add_eyebrow(s, "Why this matters", y=Inches(1.4))
    add_h3(
        s,
        "Any club, any league, can now read every fan — without ever touching a fan.",
        y=Inches(1.75),
        w=Inches(11.5),
    )

    # Three big numbers
    stats = [
        ("€20M → 0", "GDPR exposure removed at the architecture level, "
         "not added on at the end.", WARNING),
        ("< 1s", "End-to-end latency on the stub provider — drop in any LLM, "
         "the pipeline doesn't change.", PRIMARY),
        ("72h", "Built in one hackathon weekend. 77 tests, 10 hard privacy rules, "
         "EN + DE, ready to demo.", PRIMARY),
    ]
    sw = CONTENT_W / 3
    sy = Inches(2.95)
    for i, (val, label, color) in enumerate(stats):
        sx = PAD_X + i * sw
        add_text(
            s, sx, sy, sw - Inches(0.3), Inches(1.4),
            val, size=Pt(44), bold=True, color=color, font=FONT_MONO,
        )
        add_text(
            s, sx, sy + Inches(1.5), sw - Inches(0.3), Inches(1.2),
            label, size=Pt(11), color=MUTED_FG, spacing=1.4,
        )

    # Three stakeholder cards at bottom (only on step 2)
    if reveal_stakeholders:
        stake = [
            ("FAN INSIGHTS MANAGER",
             "“What are fans complaining about today?” — answered without reading one PII byte."),
            ("SUPPORT TEAM LEAD",
             "Urgent refund requests surface in seconds — not after 800 inbox scrolls."),
            ("DATA / LEGAL",
             "One controlled boundary, audit log, no PII in DB. The compliance review writes itself."),
        ]
        by = Inches(5.6)
        bh = Inches(1.3)
        bw = (CONTENT_W - Inches(0.4)) / 3
        for i, (who, what) in enumerate(stake):
            bx = PAD_X + i * (bw + Inches(0.2))
            add_rect(
                s, bx, by, bw, bh,
                fill=CARD, line=BORDER, line_w=0.5,
                shape=MSO_SHAPE.ROUNDED_RECTANGLE,
            )
            add_text(
                s, bx + Inches(0.2), by + Inches(0.2),
                bw - Inches(0.4), Inches(0.25),
                who, size=Pt(9), bold=True, color=PRIMARY,
            )
            add_text(
                s, bx + Inches(0.2), by + Inches(0.5),
                bw - Inches(0.4), Inches(0.75),
                what, size=Pt(11), color=FG, spacing=1.35,
            )
    else:
        # While stats are reveal step 1, leave a quiet hint at the bottom
        add_text(
            s, PAD_X, Inches(6.1), CONTENT_W, Inches(0.3),
            "click to see who this is for →",
            font=FONT_MONO, size=Pt(10), color=MUTED_FG,
            align=PP_ALIGN.CENTER,
        )


def build_slide_close(prs):
    """Slide 8 — Close (tagline + QR + URL)."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(s, BG)
    add_brand_header(s)
    set_push_transition(s)

    # Centered eyebrow
    add_text(
        s, PAD_X, Inches(1.2), CONTENT_W, Inches(0.3),
        "RAUMDEUTER · FAN INTELLIGENCE",
        size=Pt(10), bold=True, color=PRIMARY, align=PP_ALIGN.CENTER,
    )

    # Build the close tagline (centered, 3 lines)
    add_text(
        s, PAD_X, Inches(1.7), CONTENT_W, Inches(0.75),
        "Raw PII never reaches the LLM.",
        size=Pt(40), bold=True, color=FG, align=PP_ALIGN.CENTER, spacing=1.0,
    )
    add_text(
        s, PAD_X, Inches(2.4), CONTENT_W, Inches(0.75),
        "Never stored.",
        size=Pt(40), bold=True, color=FG, align=PP_ALIGN.CENTER, spacing=1.0,
    )
    add_text(
        s, PAD_X, Inches(3.1), CONTENT_W, Inches(0.75),
        "By design.",
        size=Pt(40), bold=True, color=PRIMARY, align=PP_ALIGN.CENTER, spacing=1.0,
    )

    # Three checkmarks (centered)
    checks = [
        "10 hard privacy rules baked into the architecture",
        "Works offline (stub LLM) — drop-in OpenAI optional",
        "Open-source, EN + DE, ready to ship for any club",
    ]
    cy = Inches(4.0)
    for line in checks:
        add_rich(
            s, PAD_X, cy, CONTENT_W, Inches(0.3),
            [
                {"text": "✓  ", "color": PRIMARY, "bold": True, "size": Pt(12),
                 "font": FONT_MONO},
                {"text": line, "color": MUTED_FG, "size": Pt(12),
                 "font": FONT_MONO},
            ],
            align=PP_ALIGN.CENTER,
        )
        cy += Inches(0.32)

    # QR code + URL box at the bottom (centered, more generous sizing)
    ask_w = Inches(8.2)
    ask_h = Inches(1.9)
    ask_x = (SLIDE_W - ask_w) / 2
    ask_y = Inches(5.3)
    add_rect(
        s, ask_x, ask_y, ask_w, ask_h,
        fill=CARD, line=PRIMARY, line_w=1.0,
        shape=MSO_SHAPE.ROUNDED_RECTANGLE,
    )

    # QR image (left side of the box)
    qr_size = Inches(1.5)
    qr_x = ask_x + Inches(0.2)
    qr_y = ask_y + Inches(0.2)
    if QR_PATH.exists():
        s.shapes.add_picture(
            str(QR_PATH), qr_x, qr_y, height=qr_size, width=qr_size,
        )

    # URL text on the right of the QR
    text_x = qr_x + qr_size + Inches(0.4)
    text_w = ask_w - (text_x - ask_x) - Inches(0.25)
    add_text(
        s, text_x, ask_y + Inches(0.25),
        text_w, Inches(0.25),
        "TRY IT LIVE · RIGHT NOW",
        size=Pt(10), bold=True, color=PRIMARY,
    )
    add_text(
        s, text_x, ask_y + Inches(0.6),
        text_w, Inches(0.55),
        "fan-pulse-guard.vercel.app",
        size=Pt(22), bold=True, color=FG, font=FONT_MONO,
    )
    add_rich(
        s, text_x, ask_y + Inches(1.25),
        text_w, Inches(0.4),
        [
            {"text": "or ", "color": MUTED_FG, "size": Pt(11)},
            {"text": "docker compose up", "color": FG, "size": Pt(11),
             "font": FONT_MONO, "bold": True},
            {"text": " from the repo", "color": MUTED_FG, "size": Pt(11)},
        ],
    )


# ============================================================================
# MAIN
# ============================================================================
def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    # 8 logical sections, expanded into multi-step builds where the HTML deck
    # animates. The slide counter is removed; section-specific badges (e.g.
    # "STAGE 03 / 05", "STEP 02 / 04") appear top-right on the build slides.

    build_slide_hook(prs)                          # § 1 — Hook
    build_slide_problem(prs)                       # § 2 — Problem

    # § 3 — Insight (2-step reveal: "Mask first." → "Analyze second.")
    build_slide_insight(prs, reveal_second=False)
    build_slide_insight(prs, reveal_second=True)

    # § 4 — Pipeline (5-step reveal — one stage lights up per click)
    for stages_lit in range(1, 6):
        build_slide_pipeline_step(prs, stages_lit=stages_lit)

    # § 5 — Live demo (4-step reveal — Ready → Detect → Mask → Done)
    build_slide_demo_step(prs, highlights=False, masked_filled=False,
                          status_kind="ready", step=1)
    build_slide_demo_step(prs, highlights=True, masked_filled=False,
                          status_kind="detect", step=2)
    build_slide_demo_step(prs, highlights=True, masked_filled=True,
                          status_kind="mask", step=3)
    build_slide_demo_step(prs, highlights=True, masked_filled=True,
                          status_kind="done", step=4)

    build_slide_moat(prs)                          # § 6 — Moat

    # § 7 — Impact (2-step reveal: stats → stakeholders)
    build_slide_impact(prs, reveal_stakeholders=False)
    build_slide_impact(prs, reveal_stakeholders=True)

    build_slide_close(prs)                         # § 8 — Close

    # Final "Thank you" frame for Q&A
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(s, BG)
    add_brand_header(s)
    set_push_transition(s)
    add_text(
        s, PAD_X, Inches(2.7), CONTENT_W, Inches(1.6),
        "Thank you.",
        size=Pt(88), bold=True, color=FG, align=PP_ALIGN.CENTER, spacing=1.0,
    )
    add_text(
        s, PAD_X, Inches(4.55), CONTENT_W, Inches(0.55),
        "Questions?",
        size=Pt(26), color=PRIMARY, align=PP_ALIGN.CENTER,
    )
    add_text(
        s, PAD_X, Inches(5.4), CONTENT_W, Inches(0.4),
        "fan-pulse-guard.vercel.app",
        font=FONT_MONO, size=Pt(13), color=MUTED_FG, align=PP_ALIGN.CENTER,
    )

    out = Path(__file__).parent / "Raumdeuter-Pitch.pptx"
    prs.save(str(out))
    print(f"Wrote {out} · {len(prs.slides)} slides")


if __name__ == "__main__":
    main()
