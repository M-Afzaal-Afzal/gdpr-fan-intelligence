# Antigravity agents

A small AI team for this repo. **Every agent** reads the canonical docs before
acting: `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/AI_HANDOFF.md`,
`docs/DECISIONS.md`. Shared workflow: `docs/AI_WORKFLOW.md`.

## Project Context Agent
- Purpose: build/refresh understanding of the repo before any change.
- Reads: `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/architecture.md`, the
  relevant `backend/app/` or `frontend/` code.
- Output: a short, accurate summary of current state and the target task.
- Skill: `.agents/skills/repo_context.md`.

## Implementation Agent
- Purpose: make the change using existing patterns.
- Rules: reuse `services/` functions and `components/ui/` primitives; keep
  `schemas.py` and `lib/types.ts` in sync; no new deps unless necessary; never
  weaken the ten privacy rules in `AGENTS.md`. Prefer TDD for pipeline changes.
- Starts via `.agents/workflows/start_task.md`.

## QA / Review Agent
- Purpose: verify before handoff.
- Runs: backend `uv run pytest` + `uv run ruff check .` + `uv run mypy app`;
  frontend `pnpm lint` + `pnpm type-check` + `pnpm build`; the leak test in
  `docs/COMMANDS.md` after pipeline changes.
- Output: pass/fail per check and a list of changed files with rationale.

## Handoff Agent
- Purpose: preserve continuity for the next tool.
- Updates `docs/AI_HANDOFF.md`, and `docs/DECISIONS.md` /
  `docs/ERRORS_AND_FIXES.md` / `docs/OPEN_TASKS.md` as needed.
- Skill: `.agents/skills/update_handoff.md`. Ends via
  `.agents/workflows/end_task.md`.
