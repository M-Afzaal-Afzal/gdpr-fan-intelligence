# Open Tasks

Lightweight task board shared across AI tools. Move items between sections as
work progresses. Keep it short; detailed status lives in `docs/AI_HANDOFF.md`.

## Todo

- [ ] Update `FIREWORKS_MODEL` in `backend/.env` (deepseek-v4-pro retired → 404).
- [ ] Regression test for the stub LLM fallback path.
- [x] Initialize git at the repo root and push to a public GitHub repo.
- [x] Commit `backend/uv.lock`.
- [ ] (Optional) Wire the OpenAI provider end-to-end and compare vs. stub.
- [ ] (Optional) Extend address detection via TDD (e.g. "Hauptstraße 12, München").
- [ ] (Optional) Dataset evaluation harness (precision/recall/F1, leakage rate).

## In Progress

- [ ] Cross-AI handoff system (this docs + tool-config setup).

## Done

- [x] Portfolio demo video (3:51, motion graphics + live footage) — on Desktop.
- [x] Fix corrupted stub fallback line in `llm_service.py`.
- [x] FastAPI backend with full privacy pipeline (49 tests passing).
- [x] PII detection hardening via TDD (lowercase names, ring-suffix fix).
- [x] Next.js 15 + Tailwind v4 frontend (build + lint + type-check clean).
- [x] PostgreSQL models + Alembic migration + repositories.
- [x] Docker Compose (cloud-DB friendly) + Dockerfiles.
- [x] READMEs, `docs/architecture.md`, `docs/api.md`, sample dataset.

## Blocked

- (none) — see `docs/AI_HANDOFF.md` if anything new gets blocked.
