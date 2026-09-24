# Backend — Privacy-First Fan Intelligence API

FastAPI service that runs the full GDPR-safe pipeline:
`language detection → layered PII detection → masking → safety gate → LLM
(stub or OpenAI) → output validation → secure storage`.

## Stack

- Python 3.12, FastAPI, Pydantic v2
- SQLAlchemy 2.0 + Alembic + psycopg v3
- Microsoft Presidio Analyzer + Anonymizer + spaCy (`en_core_web_sm`)
- Ruff + pytest + mypy
- `uv` for dependency / project management

## Quickstart with uv

```bash
cd backend
uv sync
cp .env.example .env

# Bring up PostgreSQL (run from repo root)
docker compose up -d postgres

# Run database migrations
uv run alembic upgrade head

# Download the spaCy model used by Presidio (one-time)
uv run python -m spacy download en_core_web_sm

# Start the API
uv run uvicorn app.main:app --reload
```

API docs: <http://localhost:8000/docs>.

## Environment variables

| Name              | Default                                                                  | Notes |
|-------------------|--------------------------------------------------------------------------|-------|
| `DATABASE_URL`    | `postgresql+psycopg://postgres:postgres@localhost:5432/fan_intelligence` | psycopg v3 driver |
| `LLM_PROVIDER`    | `stub`                                                                   | `stub` or `openai` |
| `OPENAI_API_KEY`  | empty                                                                    | required if provider is `openai` |
| `OPENAI_MODEL`    | `gpt-4o-mini`                                                            | overridable |
| `FRONTEND_ORIGIN` | `http://localhost:3000`                                                  | CORS allow-list |
| `ENVIRONMENT`     | `development`                                                            | shown on /api/health |

## Using a cloud database (Neon / Supabase / Railway / Prisma Postgres)

There is no local-database lock-in: the backend only needs a Postgres
`DATABASE_URL`. To use a hosted database, set that one variable — no code
changes.

1. Create a Postgres database with any provider and copy its connection string.
2. Convert it to the psycopg v3 driver form and require SSL:

   ```text
   # Provider gives you:
   postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
   # Use this in backend/.env (note the +psycopg):
   DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
   ```

3. Run migrations against it, then start the API:

   ```bash
   uv run alembic upgrade head
   uv run uvicorn app.main:app --reload
   ```

Notes per provider:

- **Neon / Supabase / Railway / Aiven** — give a standard `postgresql://` URL.
  Just add the `+psycopg` driver and `?sslmode=require`. These are the
  smoothest fit for this Python/SQLAlchemy stack.
- **Prisma Postgres** — use the **direct TCP connection string** (a normal
  `postgresql://...`). Do **not** use the `prisma+postgres://...` Accelerate
  string; that speaks Prisma's proxy protocol, which psycopg cannot connect to.
  Prisma itself is a Node ORM and is not used here — only its hosted database.
- With Docker Compose, export `DATABASE_URL` in your shell before
  `docker compose up`; you can then stop the bundled local `postgres` service.

## Migrations (Alembic)

```bash
uv run alembic upgrade head          # apply
uv run alembic revision -m "msg" --autogenerate
uv run alembic downgrade -1
```

## Tests

```bash
uv run pytest
```

The test suite covers the regex detector, anonymizer, safety gate, output
validator, and a TestClient-driven API test. It runs without a live
PostgreSQL because the API tests monkeypatch the DB session.

## Lint / format / types

```bash
uv run ruff check .
uv run ruff format .
uv run mypy app
```

## Privacy implementation notes

- `app/services/pii_detector.py` runs four layers: regex, Presidio NER,
  German address heuristics, and football hard-negatives. Returns spans —
  never values.
- `app/services/anonymizer.py` replaces from right-to-left, with stable
  per-type numbering, so offsets stay valid and the masked message remains
  human-readable.
- `app/services/safety_gate.py` re-runs detection on the masked message
  (ignoring our own placeholders) **before** the LLM call. Any residual
  span means `privacy_status = blocked` and `llm_called = false`.
- `app/services/output_validator.py` parses JSON, validates the enum
  contract, and runs a final PII scan on `summary` / `recommended_action`.
- `app/db/models.py`: `pii_entities` has **no** `entity_value` column.
  `analysis_results.raw_message_hash` stores a SHA-256 digest only.
