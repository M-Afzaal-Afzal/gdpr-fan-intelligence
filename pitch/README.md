# Pitch deck — Privacy-First Fan Intelligence

A self-contained, interactive 3-minute pitch deck for the Raumdeuter AI Hackathon.

**Live product:** <https://fan-pulse-guard.vercel.app/> — referenced on slides 1, 5, and 8 (with a scannable QR on the close slide).

## Files

| File                       | What it is                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| `index.html`               | The interactive HTML deck. Single file. Open in any browser. No build step.                 |
| `Raumdeuter-Pitch.pptx`    | The PowerPoint deck (12 slides, same content + brand, multi-step build for the demo).       |
| `build_pptx.py`            | Generator for the `.pptx`. Edit content + colors here, then re-run to rebuild the deck.     |
| `SCRIPT.md`                | The hooky speaker script — what to actually say, slide by slide, timed.                     |
| `README.md`                | This file.                                                                                  |

## How to present

### Option A — HTML (recommended; has the live demo animation, ticker, counter)

```bash
# Just open it.
open pitch/index.html          # macOS
xdg-open pitch/index.html      # Linux
start pitch\index.html         # Windows
```

Then press **F** for fullscreen, and **T** to start the 3-minute timer the moment you start talking.

### Option B — PowerPoint / Keynote (for stages that require a `.pptx`)

```bash
open pitch/Raumdeuter-Pitch.pptx   # macOS — opens in Keynote or PowerPoint
```

The deck has **18 slides** (vs. 8 logical sections) because every HTML animation
is reproduced as a progressive-reveal click-through. The slide counter has been
removed; instead, multi-step sections show a section badge in the top-right
(e.g. `STAGE 03 / 05`, `STEP 02 / 04`, `STEP 1 / 2`) so the speaker knows where
they are within each logical section.

Each click = one beat:

- **Insight** (§3): 2 clicks → "Mask first." → "Analyze second."
- **Pipeline** (§4): 5 clicks → one stage lights up at a time (with a 5-dot
  progress row at the top + a green "● active" pip on the just-lit card).
- **Live demo** (§5): 4 clicks → raw → highlighted → masked → done.
- **Impact** (§7): 2 clicks → stats appear → stakeholder cards appear.

### Rebuilding the `.pptx`

```bash
cd pitch/_build
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python python-pptx pillow
.venv/bin/python ../build_pptx.py
```

The generated file appears at `pitch/Raumdeuter-Pitch.pptx`. The QR code PNG
in `pitch/_build/qr.png` is fetched once and embedded as a real image — the
`.pptx` works fully offline.

## Keyboard

| Key                   | Action                                       |
| --------------------- | -------------------------------------------- |
| `→` `Space` click     | Next slide (or run the live demo on slide 5) |
| `←`                   | Previous slide                               |
| `Home` `End`          | First / last slide                           |
| `T`                   | Start / pause the 3-min timer                |
| `T` (double-click)    | Reset timer back to 3:00                     |
| `S`                   | Show / hide speaker notes overlay            |
| `F`                   | Toggle fullscreen                            |
| `P`                   | Print → save as PDF                          |
| `R`                   | Reset the live demo (slide 5 only)           |
| Click a pipeline stage| Light up stages 1 → 5 (slide 4)              |

## Slide map

The 8 logical sections of the pitch. Multi-step sections in the PPTX
(insight, pipeline, demo, impact) mirror the HTML's JS-driven reveals.

| § | HTML slide | PPTX slides | Clicks | Section        | What it does                                                                |
| - | ---------- | ----------- | ------ | -------------- | --------------------------------------------------------------------------- |
| 1 | 1          | 1           | 1      | Hook           | "What if your ~~AI~~ just leaked your fans to OpenAI?"                      |
| 2 | 2          | 2           | 1      | Problem        | €20M static fine + three pain points.                                       |
| 3 | 3          | **3 → 4**   | 2      | Insight        | "Mask first." → "Analyze second." (green) + lead paragraph.                 |
| 4 | 4          | **5 → 9**   | 5      | How it works   | 5-stage pipeline — one stage lights up per click. Storage footer on 5/5.    |
| 5 | 5          | **10 → 13** | 4      | Live demo      | PII masking on a bilingual complaint — Ready → Detect → Mask → Done.        |
| 6 | 6          | 14          | 1      | The moat       | 4 detection layers, 0 value columns, 2 scans, 77/77 tests + privacy rules.  |
| 7 | 7          | **15 → 16** | 2      | Impact         | €20M → 0, <1 s, 72 h — then stakeholder quotes.                             |
| 8 | 8          | 17          | 1      | Close          | "Raw PII never reaches the LLM. Never stored. By design." + QR code.        |
|   |            | 18          | —      | (Thank you)    | Clean end frame for Q&A.                                                    |

**Total: 18 slides, 16 clicks across 8 logical sections.**

## Brand

Both decks mirror the project's frontend:

- HTML: `DM Sans` (body) + `JetBrains Mono` (data / IDs / timings only).
- PPTX: `Calibri` + `Consolas` — universal fallbacks so it renders identically on
  any Mac/Windows/Linux PowerPoint, Keynote, LibreOffice, or Google Slides install.
- Primary green `oklch(0.45 0.1 155)` (`#1F6B47`), warm off-white background.
- Same triangle BrandMark from `frontend/components/BrandMark.tsx`.
- All tokens copied from `frontend/app/globals.css`.

## Animations (HTML vs. PPTX)

The HTML deck uses JavaScript to drive interactivity. PowerPoint can't run JS, so
the `.pptx` uses **progressive-reveal click-through** — the standard
PowerPoint idiom for the same effect.

| HTML animation                          | PPTX equivalent                                                          |
| --------------------------------------- | ------------------------------------------------------------------------ |
| Slide-in transition (slide → slide)     | Native Push transition from the right (set on every slide).              |
| Strikethrough on "AI" (slide 1)         | Real strikethrough rendered on the run.                                  |
| €20M counter animation (slide 2)        | Final state €20M shown big — no risk of mis-firing on stage.             |
| **Pipeline stages light up (slide 4)**  | **5-slide build: one stage lights up per click. Dimmed cards turn lit; a 5-dot progress row + green ● "active" pip on the just-lit card; storage footer appears on 5/5.** |
| Insight reveal (slide 3)                | 2-slide build: "Mask first." appears, then "Analyze second." (green).    |
| Live demo masking (slide 5)             | 4-slide build: raw → highlighted → masked → done (one click each).       |
| Cycling privacy-rules ticker (slide 6)  | Static "10 / 10 hard privacy rules" pill at the bottom.                  |
| Impact stats reveal (slide 7)           | 2-slide build: stats first, then stakeholder cards.                      |
| QR code on close (slide 8)              | QR PNG embedded directly — works offline.                                |

## Export to PDF

In the deck, press `P` (or `Cmd/Ctrl-P`). Use Chrome for the best result.
The print stylesheet hides the chrome and forces one slide per page.

## Backup plan

If anything weird happens to the deck on stage, fall back to:
1. **The live site:** <https://fan-pulse-guard.vercel.app/>
2. The actual app running locally at `localhost:3000`.
3. The exported PDF.

## Network note

Slide 8 embeds a QR code via `api.qrserver.com`. If the venue blocks it, the QR
gracefully disappears and the URL text stays — the deck still works fully
offline.

## Editing

### HTML deck
Everything lives in `pitch/index.html` (~1100 lines, no dependencies, no build).
- Slide content: search for `<!-- SLIDE N` markers.
- Demo text: search for `const demoText` and `const demoEntities`.
- Brand tokens: top of the `<style>` block under `:root`.
- Speaker notes (in-deck): search for `const speakerNotes`.
- Speaker script (markdown): edit `SCRIPT.md`.

### PPTX deck
Everything lives in `pitch/build_pptx.py` (one Python file, no external assets
beyond `pitch/_build/qr.png`).
- Brand colors: top of the file (`BG`, `FG`, `PRIMARY`, `DIM_BORDER`, etc.).
- Each section has its own `build_slide_*` function.
- Multi-step sections take a parameter (`reveal_second`, `stages_lit`, `step`,
  `reveal_stakeholders`) and are called multiple times from `main()` to
  generate the build slides.
- Re-run `build_pptx.py` to regenerate `Raumdeuter-Pitch.pptx`.
