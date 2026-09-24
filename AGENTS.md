# AGENTS.md — Shared instructions for all AI coding tools

This is the **canonical instruction file** for every AI agent working in this
repo (Codex, Cursor, Kiro, Antigravity, Claude Code, and any other tool).
Read this first, then read `docs/AI_HANDOFF.md` to see where work stands.

## Project overview

**Privacy-First Fan Intelligence Pipeline** — a GDPR-safe AI pipeline for
football fan messages. A user submits one raw fan message; the backend detects
PII, masks it, re-scans for safety, and only then sends the *masked* message to
an LLM for analysis (sentiment, topic, intent, urgency, summary, recommended
action). Raw PII never reaches the LLM and is never stored.

Full detail: `docs/PROJECT_CONTEXT.md`. Architecture: `docs/architecture.md`.

## Tech stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic,
  psycopg v3, Microsoft Presidio (+ spaCy `en_core_web_sm`). Managed by **uv**.
  Lint/format: **Ruff**. Types: **mypy**. Tests: **pytest**.
- **Frontend:** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS v4,
  shadcn-style UI. Managed by **pnpm** (pinned `pnpm@9.15.4`). Lint: ESLint
  (flat config). Format: Prettier.
- **Database:** PostgreSQL 16 (local via Docker, or any hosted Postgres).
- **Orchestration:** `docker-compose.yml` (postgres + backend + frontend).

## Folder structure (summary)

```text
gdpr-fan-intelligence/
├── backend/        FastAPI service (app/, migrations/, pyproject.toml)
│   └── app/        config, schemas, routes/, services/ (PII pipeline), db/, tests/
├── frontend/       Next.js app (app/, components/, lib/)
├── data/           sample_messages.jsonl
├── docs/           canonical context + handoff docs (this system)
├── docker-compose.yml
├── AGENTS.md       ← you are here
└── CLAUDE.md
```

The privacy pipeline lives in `backend/app/services/`:
`pii_detector.py` → `anonymizer.py` → `safety_gate.py` → `llm_service.py` →
`output_validator.py`, orchestrated by `backend/app/routes/analyze.py`.

## Package managers

- Backend: **uv** (do not use bare `pip`; deps live in `backend/pyproject.toml`).
- Frontend: **pnpm** (do not use `npm`/`yarn`; respect the pinned version).

## Commands (canonical list: `docs/COMMANDS.md`)

Backend — run from `backend/`:

| Action      | Command |
|-------------|---------|
| Install     | `uv sync` |
| Dev server  | `uv run uvicorn app.main:app --reload` |
| Test        | `uv run pytest` |
| Lint        | `uv run ruff check .` |
| Format      | `uv run ruff format .` |
| Typecheck   | `uv run mypy app` |
| Migrate     | `uv run alembic upgrade head` |
| NLP model   | `uv run python -m spacy download en_core_web_sm` |

Frontend — run from `frontend/`:

| Action      | Command |
|-------------|---------|
| Install     | `pnpm install` |
| Dev server  | `pnpm dev` |
| Build       | `pnpm build` |
| Lint        | `pnpm lint` |
| Format      | `pnpm format` |
| Typecheck   | `pnpm type-check` |

Full stack: `docker compose up --build` (from repo root). DB only:
`docker compose up -d postgres`. No deployment command is defined in the repo.

## Environment rules

- Backend config is read via `pydantic-settings` from `backend/.env`
  (template: `backend/.env.example`). Frontend uses `frontend/.env.local`
  (template: `frontend/.env.example`, only `NEXT_PUBLIC_API_BASE_URL`).
- **Never commit secrets.** `.env` files are gitignored; only `.env.example`
  is tracked. The frontend must never hold an LLM key.
- The only required runtime secret is `OPENAI_API_KEY` (optional — the default
  `LLM_PROVIDER=stub` runs with no key).

## Code style rules

- **Python:** Ruff (line length 100, `py312`). Type hints on public functions.
  Keep services pure and small. Follow the existing `from __future__ import
  annotations` + module-docstring pattern.
- **TypeScript/React:** Prettier (printWidth 100, single quotes, semicolons,
  trailing commas, 2-space). Tailwind v4 only — **no `tailwind.config.js`**;
  tokens live in `frontend/app/globals.css` via `@theme`. Reuse the shadcn-style
  primitives in `frontend/components/ui/` and the `cn()` helper in `lib/utils.ts`.
- Reuse existing helpers/components; do not introduce duplicate patterns.
- Do not add new dependencies unless necessary; prefer what's already installed.

## Privacy rules (NON-NEGOTIABLE — this is the product)

1. Raw PII never reaches the LLM.
2. Raw PII is never stored in PostgreSQL.
3. Logs never contain raw PII.
4. PII entity *values* are never persisted (no `entity_value` column).
5. Store only masked messages, PII metadata, analysis, latency, status, timestamps.
6. A second PII scan runs on the masked message before any LLM call.
7. A final PII scan runs on LLM output before display/storage.
8. If masking is incomplete, block the LLM call.
9. The frontend never runs PII detection.
10. The frontend never holds LLM secrets.

Any change touching `backend/app/services/` or `backend/app/db/models.py` must
preserve all ten rules. The leak test in `docs/COMMANDS.md` must still pass.

## Git workflow rules

- The repo is on GitHub (public): <https://github.com/M-Afzaal-Afzal/gdpr-fan-intelligence>.
  Default branch is `main`. Never commit `.env` files — the repo is public.
- Branch off `main` for non-trivial work; keep commits small and descriptive.
- Stage specific files (`git add <path>`), not `git add -A` blindly.
- Never commit `.env`, secrets, `node_modules/`, `.next/`, or `.venv/`.
- Never force-push or run destructive git commands without explicit instruction.

## Safety rules

- Do not change application logic unless the task requires it.
- Do not weaken any of the ten privacy rules.
- Do not add fake/placeholder commands — only commands that exist in this repo.
- Run the relevant checks (tests, lint, typecheck) before declaring work done.

## Before starting work (checklist)

1. Read this file (`AGENTS.md`).
2. Read `docs/PROJECT_CONTEXT.md` and `docs/AI_HANDOFF.md`.
3. Skim `docs/DECISIONS.md` and `docs/OPEN_TASKS.md`.
4. Run `git status` (once git is initialized) to see uncommitted work.
5. Continue from "Next Recommended Steps" in `docs/AI_HANDOFF.md` — do **not**
   restart from zero.

## Before finishing work (checklist)

1. Run the relevant checks (backend: `uv run pytest` + `uv run ruff check .`;
   frontend: `pnpm lint` + `pnpm type-check` + `pnpm build`).
2. Update **`docs/AI_HANDOFF.md`** (mandatory after every meaningful task).
3. Log any new architecture decision in `docs/DECISIONS.md`.
4. Log any new error+fix in `docs/ERRORS_AND_FIXES.md`.
5. Move tasks on `docs/OPEN_TASKS.md`.
6. Commit with a clear message.

## Mandatory rule

**After every meaningful task, update `docs/AI_HANDOFF.md`** so the next tool (or
the next session of this tool) can continue without losing context.
