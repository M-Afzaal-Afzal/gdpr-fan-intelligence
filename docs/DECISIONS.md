# Architecture Decision Log

Newest first. Use the format below for every new entry.

```md
## YYYY-MM-DD — <decision title>
- **Decision:** what was decided
- **Reason:** why
- **Alternatives considered:** what else, and why not
- **Impact:** what this affects
```

---

## 2026-05-21 — Cross-AI handoff system with one canonical source
- **Decision:** `AGENTS.md` + `docs/*` are the canonical instructions; each tool
  (Kiro, Cursor, Claude, Antigravity, Codex) gets a thin wrapper pointing here.
- **Reason:** avoid drift between five tools; one place to update.
- **Alternatives considered:** per-tool full instructions (duplication, drift).
- **Impact:** all tool configs reference the shared docs; update docs, not copies.

## 2026-05-21 — Intro-name fallback runs on every request
- **Decision:** the self-introduction name heuristic runs always, not only when
  Presidio is unavailable.
- **Reason:** Presidio NER still misses lowercase/uncommon names ("I am afzaal").
- **Alternatives considered:** rely on Presidio only (missed lowercase names).
- **Impact:** `pii_detector.py`; guarded by a stopword list to avoid false
  positives like "I am very angry".

## 2026-05-21 — Dropped `ring` from German street suffixes
- **Decision:** remove `ring` from the address regex.
- **Reason:** with IGNORECASE it matched English words ("during", "spring").
- **Alternatives considered:** keep it (caused over-masking) — rejected.
- **Impact:** `pii_detector.py`; addresses still match straße/str./platz/weg/
  allee/gasse.

## 2026-05-20 — Cloud-DB friendly compose; Node 22 + pinned pnpm
- **Decision:** `DATABASE_URL` is overridable via env in `docker-compose.yml`;
  frontend Docker uses `node:22-alpine` with `pnpm@9.15.4` pinned.
- **Reason:** allow hosted Postgres (Neon/Supabase/etc.); fix a corepack/pnpm
  Node-version crash (`node:sqlite` needs Node ≥ 22.13).
- **Alternatives considered:** local-only DB; unpinned pnpm (non-deterministic).
- **Impact:** `docker-compose.yml`, `frontend/Dockerfile`, `frontend/package.json`.

## 2026-05-20 — `str + Enum` for API enums (ignore Ruff UP042)
- **Decision:** keep `class X(str, Enum)` instead of `StrEnum`.
- **Reason:** clean Pydantic serialization and broad compatibility.
- **Alternatives considered:** `enum.StrEnum` (UP042) — unnecessary churn.
- **Impact:** `backend/app/schemas.py`; `UP042` ignored in Ruff config.

## 2026-05-20 — No `entity_value` column; hash raw message only
- **Decision:** `pii_entities` stores type/offsets/replacement/confidence only;
  `analysis_results.raw_message_hash` is a SHA-256 digest.
- **Reason:** even a full DB dump must not reconstruct PII (privacy rule 4).
- **Alternatives considered:** store values for debugging — rejected (privacy).
- **Impact:** `backend/app/db/models.py`, migration `0001_initial.py`.

## 2026-05-20 — Single Python FastAPI backend for the privacy boundary
- **Decision:** one FastAPI service holds detection, masking, gate, LLM, storage.
- **Reason:** keep raw PII inside one controlled boundary; simpler to reason about.
- **Alternatives considered:** Node gateway + separate Python PII service —
  rejected (more surface area, more places PII could leak).
- **Impact:** whole `backend/` design; frontend is presentation-only.

## 2026-05-20 — Stub LLM provider by default
- **Decision:** default `LLM_PROVIDER=stub` (keyword heuristic); OpenAI optional.
- **Reason:** demo runs free/offline with no key; real model is opt-in.
- **Alternatives considered:** require an API key — rejected (worse demo UX).
- **Impact:** `backend/app/services/llm_service.py`, `config.py`.
