# Antigravity workspace rule — code quality

- Reuse existing patterns: backend small pure functions in `app/services/`;
  frontend shadcn-style primitives in `components/ui/` + `cn()` in `lib/utils.ts`.
- Keep `backend/app/schemas.py` and `frontend/lib/types.ts` in sync.
- Don't add dependencies unless necessary. Tailwind v4 only (no config file).
- Prefer TDD for pipeline/detector changes
  (`backend/app/tests/test_pipeline_edge_cases.py`).
- Run checks before finishing — backend: `uv run pytest`, `uv run ruff check .`,
  `uv run mypy app`; frontend: `pnpm lint`, `pnpm type-check`, `pnpm build`.
  After touching the pipeline, run the leak test in `docs/COMMANDS.md`.
- Privacy first: never store raw PII or `entity_value`; the frontend never holds
  secrets and never runs PII detection.
