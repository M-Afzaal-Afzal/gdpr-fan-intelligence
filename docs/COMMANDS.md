# Commands

Only commands that actually exist in this repo. Backend commands run from
`backend/`; frontend commands run from `frontend/`; Docker commands from the
repo root (`gdpr-fan-intelligence/`).

## Backend (uv)

| Purpose      | Command |
|--------------|---------|
| Install      | `uv sync` |
| Dev server   | `uv run uvicorn app.main:app --reload` |
| Test         | `uv run pytest` |
| Lint         | `uv run ruff check .` |
| Format       | `uv run ruff format .` |
| Typecheck    | `uv run mypy app` |
| NLP model    | `uv run python -m spacy download en_core_web_sm` |

### Database (Alembic)

| Purpose            | Command |
|--------------------|---------|
| Apply migrations   | `uv run alembic upgrade head` |
| New migration      | `uv run alembic revision -m "message" --autogenerate` |
| Roll back one      | `uv run alembic downgrade -1` |

## Frontend (pnpm)

| Purpose    | Command |
|------------|---------|
| Install    | `pnpm install` |
| Dev server | `pnpm dev` |
| Build      | `pnpm build` |
| Start      | `pnpm start` |
| Lint       | `pnpm lint` |
| Format     | `pnpm format` |
| Typecheck  | `pnpm type-check` |

## Docker (repo root)

| Purpose          | Command |
|------------------|---------|
| Full stack       | `docker compose up --build` |
| Postgres only    | `docker compose up -d postgres` |
| Stop             | `docker compose down` |

## Privacy leak check (run after touching the pipeline)

This is the guardrail referenced in `AGENTS.md`. Run from `backend/`:

```bash
uv run pytest app/tests/test_pipeline_edge_cases.py app/tests/test_api.py -q
```

These tests assert that no raw PII (emails, phones, IDs, names) survives into
the masked message, the stored row, or the LLM analysis.

## Deployment

No deployment command is defined in the repo yet. The Dockerfiles
(`backend/Dockerfile`, `frontend/Dockerfile`) and `docker-compose.yml` are the
current packaging artifacts.

## Git

Public repo: <https://github.com/M-Afzaal-Afzal/gdpr-fan-intelligence> (default branch `main`).

```bash
git status
git add <path>
git commit -m "message"
git push
```
