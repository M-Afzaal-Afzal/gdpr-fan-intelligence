# Project Context

## What this project does

**Privacy-First Fan Intelligence Pipeline** is a GDPR-safe AI pipeline for
football fan messages. A user submits one raw fan message; the backend detects
personally identifiable information (PII), masks it with readable placeholders,
re-scans the masked text in a safety gate, and only then sends the *masked*
message to an LLM for analysis. The LLM output is validated and scanned once
more before anything is displayed or stored. Raw PII never reaches the LLM and
is never stored.

Built for the Raumdeuter AI Hackathon. The full product spec lives in the
workspace as `privacy_first_fan_intelligence_prd.md`.

## Main users

- **Fan Insights Manager** — wants to understand what fans complain about,
  ask for, or praise without reading thousands of messages.
- **Support Team Lead** — needs to spot urgent complaints, refund requests,
  accessibility/booking/matchday issues.
- **Club Data / AI team** — wants a privacy-safe pipeline they can integrate.
- **Hackathon jury** — needs a clear, working demo and architecture story.

## Core features

- One-message analysis endpoint (`POST /api/analyze-message`).
- Layered PII detection (regex, Presidio NER, German address rules, football
  hard-negative protection, intro-name fallback).
- Anonymization with stable `[TYPE_N]` placeholders.
- Second safety gate before the LLM; final PII scan on LLM output.
- LLM analysis: sentiment, topic, intent, urgency, summary, recommended action
  (stub provider by default; OpenAI optional).
- Secure storage of masked results + PII metadata + audit events.
- Dashboard metrics, dataset page, architecture page.

## Tech stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic,
  psycopg v3, Microsoft Presidio (+ spaCy `en_core_web_sm`). Tooling: uv, Ruff,
  mypy, pytest.
- **Frontend:** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS v4,
  shadcn-style UI, Zod. Tooling: pnpm (`pnpm@9.15.4`), ESLint, Prettier.
- **Database:** PostgreSQL 16.
- **Orchestration:** Docker Compose.

## Main directories

```text
backend/app/
  config.py        pydantic-settings config (reads backend/.env)
  schemas.py       Pydantic API contract (enums + request/response models)
  routes/          analyze.py (orchestrator), results.py, metrics.py, health.py
  services/        language_service, pii_detector, anonymizer, safety_gate,
                   llm_service, output_validator, metrics_service
  db/              database.py (engine), models.py (ORM), repositories.py
  tests/           pytest suite (detector, anonymizer, gate, validator, api,
                   pipeline edge cases)
backend/migrations/  Alembic env + versions/0001_initial.py
frontend/app/        Next.js routes: / , /dashboard, /dataset, /architecture
frontend/components/ feature components + ui/ (shadcn-style primitives)
frontend/lib/        api.ts, types.ts, schemas.ts, constants.ts, utils.ts
data/                sample_messages.jsonl
docs/                this cross-AI context system + architecture.md, api.md
```

## Important architecture notes

- The whole privacy engine is in **one** FastAPI backend, so raw PII stays in a
  single controlled boundary. The frontend only sends raw text and renders the
  structured response — it never runs PII detection and holds no secrets.
- Pipeline order (do not reorder): language detection → PII detection →
  anonymization → safety gate → LLM (masked only) → output validation + final
  PII scan → storage.
- DB privacy: `pii_entities` has **no** `entity_value` column;
  `analysis_results.raw_message_hash` is a SHA-256 digest only.
- The intro-name fallback in `pii_detector.py` runs always (not only when
  Presidio is missing), because NER still misses lowercase/uncommon names.

## External services

- **OpenAI** (optional) — only when `LLM_PROVIDER=openai` and `OPENAI_API_KEY`
  are set; receives the masked message only. Default is the offline `stub`.
- **PostgreSQL** — local (Docker) or any hosted provider (Neon/Supabase/Railway/
  Prisma Postgres direct connection) via `DATABASE_URL`.

## Current limitations / unknowns

- The repo is public on GitHub: <https://github.com/M-Afzaal-Afzal/gdpr-fan-intelligence>.
- Offline name detection only fires on self-introductions; free-floating names
  rely on the Presidio spaCy model being installed.
- The `stub` LLM is a keyword heuristic — fine for the demo, not production NLP.
- No auth, rate limiting, or batch processing yet (intentionally out of scope).
