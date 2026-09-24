# AI Handoff

> **The single most important file for cross-tool continuity.** Every AI tool
> reads this at the start of a session and updates it before finishing. Keep it
> current, concise, and honest. Overwrite the sections below each session
> (don't append endlessly) — history belongs in `docs/DECISIONS.md` and
> `docs/ERRORS_AND_FIXES.md`.

_Last updated: 2026-09-24 · by: Claude Code (Opus 5.5)_

## Current Goal

Portfolio demo videos (motion graphics + live product footage) — **done**:
a 60-second interview cut and a full 3:51 walkthrough. Pitch decks unchanged.

## Current Status

- **Git:** published as a **public** repo — <https://github.com/M-Afzaal-Afzal/gdpr-fan-intelligence>
  (`main`). README rewritten as a portfolio page (live demo link, real masking example,
  pipeline image in `docs/assets/`, PRD copied to `docs/PRD.md`). `pitch/_build/` is gitignored.
  The repo is public: never commit `.env` files or real PII.
- **Naming:** the product is **Privacy-First Fan Intelligence**, built *for
  Raumdeuter* (the company that set the hackathon challenge). Raumdeuter is not
  the product name; the videos now say "Built for Raumdeuter".
- **Done (Desktop, not in repo):**
  - `~/Desktop/fan-intelligence-60s.mp4` — 59.8 s interview cut (1080p50,
    narrated, captioned for mute viewing).
  - `~/Desktop/fan-intelligence-full-demo.mp4` — 3:51 full walkthrough (61 MB).
  - Video source (edit lists, recorder scenes, motion-graphics lib) in
    `~/Desktop/fan-intelligence-video-source/` (`short/edit.py` = 60 s cut).
  - Old wrongly-branded `raumdeuter-privacy-first-fan-intelligence*.mp4` and
    `raumdeuter-video-source/` still on Desktop — delete once the user confirms.
- **Bug fixed:** `backend/app/services/llm_service.py` stub fallback line was
  corrupted (`sentiment =  (msg)`) → `_stub_sentiment(msg)`. 77/77 tests pass.
- **Known config issue (not changed):** `backend/.env` `FIREWORKS_MODEL=
  accounts/fireworks/models/deepseek-v4-pro` returns 404 (retired). Videos were
  recorded with env override `deepseek-v4p1-flash`. Update `.env`.
- Demo recording added ~5 masked analysis rows to local Postgres (no raw PII).

## Last Completed Work

**60 s interview cut (2026-09-24):** built on retention research (Wistia
engagement data, short-form 3-second hook research, mute-viewing/caption stats,
Murch's Rule of Six, Made to Stick). Structure: 5.8 s question hook ("Would you
send this to an AI?") with the leak animation → core idea card "Mask first.
Analyze second." → "Now, live." slam → John Miller end-to-end → "One more
thing." slam → prompt injection flagged → stats outro (3 scans, 10 rules, 77
tests, 0 PII stored). New motion-graphics card kind `slam` + hook timing
overrides in `lib/mg.mjs`.

**Full walkthrough (2026-09-24):** hook → idea → John Miller → mixed EN/DE +
no-PII control → prompt injection → what gets stored → dashboard →
architecture → stats outro. `product-demo-video` skill + custom card kinds.

**Pitch deck — PPTX iteration 2 (2026-05-22, second pass):**
- **Pipeline now matches HTML stage-by-stage click-through** (per user request):
  - 5 build slides — one stage lights up per click.
  - Dimmed cards turn lit with brand-green border, lighter green tint on the
    just-lit "active" card, plus a small green ● pip in the top-right corner.
  - 5-dot progress row at the top + connecting lines that fill in as stages
    advance.
  - "What gets stored" footer revealed only on the final stage (5/5).
- **Slide counter removed** (per user request) — replaced with section-specific
  badges in the top-right (`STAGE 03 / 05`, `STEP 02 / 04`, `STEP 1 / 2`).
- **Insight slide now 2-step build** — "Mask first." → "Analyze second." +
  lead paragraph appears on click.
- **Impact slide now 2-step build** — stats first, stakeholder cards on click.
- **Close slide overflow fixed** — wider URL/QR box, smaller fonts, brand-green
  border, "or `docker compose up` from the repo" now fits clearly on one line.
- **Thank you slide overflow fixed** — taller "Thank you." box, "Questions?"
  and URL repositioned with proper spacing.
- Total deck went from 12 → 18 slides (8 logical sections, 16 clicks).

**Pitch deck — PPTX iteration 1 (earlier 2026-05-22):**
- Wrote `pitch/build_pptx.py` (`python-pptx` + `lxml`) — generates the
  brand-matched deck with Push transitions on every slide.
- Embedded the live-site QR code as a real PNG (765 B) — works offline.
- Brand: warm off-white background, primary green `#1F6B47`, Calibri + Consolas
  for universal compatibility.
- Verified visually by rendering via Keynote → PDF → per-slide PNGs.

**Prior:** Interactive HTML deck + live-site/QR integration; UI polish; LLM
provider dropdown; timings in seconds; pipeline staged reveal.

## Files Changed Recently

**Pitch deck (this session):**
- `pitch/build_pptx.py` (new) — PowerPoint generator (~700 lines).
- `pitch/Raumdeuter-Pitch.pptx` (new, generated) — 12-slide deck.
- `pitch/_build/qr.png` (fetched once) — QR code PNG embedded into the .pptx.
- `pitch/README.md` — added PPTX section, animation comparison table, build steps.
- `pitch/SCRIPT.md` — added PPTX 4-step demo cues + dual-deck rehearsal checklist.
- `.gitignore` — added `pitch/_build/.venv/`, `preview.pdf`, `slide-*.png`.

**Prior session (UI / API changes — unchanged this session):**
- `backend/app/schemas.py`, `routes/llm_providers.py`, `services/llm_service.py`,
  `routes/analyze.py`, `tests/test_api.py`.
- `frontend/app/globals.css`, `layout.tsx`, `page.tsx`, `BrandMark.tsx`,
  `SiteNav.tsx`, `MessageInput.tsx`, `TimingBadges.tsx`, `PipelineStepper.tsx`,
  `lib/format.ts`, `lib/types.ts`, `lib/api.ts`.

## Current Errors / Blockers

- 4 pre-existing mypy `unused-ignore` warnings (unchanged).
- `backend/.env` points at a retired Fireworks model (404) — see Current Status.

## Commands Already Run

```bash
# 2026-09-24 (video session):
cd backend && uv run pytest -q                 # 77/77 passed after llm_service fix
docker compose up -d postgres && cd backend && uv run alembic upgrade head
# backend on :8010 (FIREWORKS_MODEL=accounts/fireworks/models/deepseek-v4p1-flash), frontend on :3010

# Earlier session (pitch deck PPTX):
cd pitch/_build && uv venv .venv --python 3.12
uv pip install --python .venv/bin/python python-pptx pillow
cd pitch && _build/.venv/bin/python build_pptx.py   # → Raumdeuter-Pitch.pptx (12 slides)

# Verified via Keynote → PDF → pdftoppm PNGs per slide.

# Prior session (unchanged this session):
cd backend && uv run pytest -q                 # 77/77 passed
cd backend && uv run ruff check .
cd frontend && pnpm lint && pnpm type-check && pnpm build
```

## Important Decisions

- **Pitch PPTX uses progressive-reveal multi-slide builds, not embedded animations.**
  PowerPoint XML animation timing is fragile across PowerPoint / Keynote /
  LibreOffice / Google Slides. Multi-slide reveal works identically everywhere
  and matches the HTML's slide-by-slide pacing.
- **PPTX uses Calibri + Consolas, not DM Sans / JetBrains Mono.** Universal
  fallback fonts mean the deck renders the same on any stage laptop without
  needing font installation. Brand identity carried by color + layout.
- Frontend selects provider; API keys remain server-side only (privacy rule 10).
- Unconfigured providers shown disabled; backend falls back to stub if called anyway.
- Timings stay in ms on API; frontend converts to seconds for display.

## Next Recommended Steps

1. Fix `FIREWORKS_MODEL` in `backend/.env` (retired model → 404).
2. Add a regression test for the stub fallback path in `llm_service.py`.
3. Rehearse the pitch end-to-end with each deck variant on the actual stage laptop.
4. Manual smoke: switch LLM provider on demo page with keys in `backend/.env`.
5. Optional: sync architecture page styling with new brand.
6. Continue backlog: PHONE FNs, German spaCy.

## Notes for Next AI Tool

- Start from "Next Recommended Steps" above; do not rebuild from scratch.
- Preserve the ten privacy rules in `AGENTS.md`.
- Update this file before you stop.
