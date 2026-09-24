---
inclusion: always
---

# Tech (Kiro steering)

## Stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic,
  psycopg v3, Microsoft Presidio (+ spaCy `en_core_web_sm`).
- **Frontend:** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS v4,
  shadcn-style UI, Zod.
- **Database:** PostgreSQL 16. **Orchestration:** Docker Compose.

## Package managers

- Backend: **uv** (deps in `backend/pyproject.toml`; never bare `pip`).
- Frontend: **pnpm** (pinned `pnpm@9.15.4`; never `npm`/`yarn`).

## Commands (run backend cmds from `backend/`, frontend from `frontend/`)

- Backend: `uv sync`, `uv run uvicorn app.main:app --reload`, `uv run pytest`,
  `uv run ruff check .`, `uv run ruff format .`, `uv run mypy app`,
  `uv run alembic upgrade head`, `uv run python -m spacy download en_core_web_sm`.
- Frontend: `pnpm install`, `pnpm dev`, `pnpm build`, `pnpm lint`,
  `pnpm type-check`, `pnpm format`.
- Docker: `docker compose up --build` (root); `docker compose up -d postgres`.

Full list: `docs/COMMANDS.md`.

## Technical constraints

- Tailwind v4 only — **no `tailwind.config.js`**; tokens in
  `frontend/app/globals.css` via `@theme`.
- The ten privacy rules in `AGENTS.md` are non-negotiable. `pii_entities` has no
  `entity_value` column; raw message is only ever hashed.
- Config via `pydantic-settings` from `backend/.env`; secrets never committed;
  the frontend never holds an LLM key.
- Don't add new dependencies unless necessary.
