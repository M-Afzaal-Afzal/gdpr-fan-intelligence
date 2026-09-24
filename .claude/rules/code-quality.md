# Claude rule — code quality

- Follow the code style and the ten privacy rules in `AGENTS.md`.
- Reuse existing patterns: backend services are small pure functions; frontend
  reuses `components/ui/` primitives and `lib/utils.ts` `cn()`.
- Keep `backend/app/schemas.py` and `frontend/lib/types.ts` in sync.
- Don't add dependencies unless necessary. Tailwind v4 only (no config file).
- Prefer TDD for pipeline/detector changes.
- Run checks before finishing — backend: `uv run pytest`, `uv run ruff check .`,
  `uv run mypy app`; frontend: `pnpm lint`, `pnpm type-check`, `pnpm build`.
  After touching the pipeline, run the leak test in `docs/COMMANDS.md`.
- Never store raw PII or `entity_value`; the frontend holds no secrets.
