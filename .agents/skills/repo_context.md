# Skill: repo_context

Understand the repo before editing anything.

## Steps
1. Read `AGENTS.md` (stack, commands, privacy rules, style, safety).
2. Read `docs/PROJECT_CONTEXT.md` (purpose, directories, architecture notes).
3. Read `docs/AI_HANDOFF.md` (where work stands; the baton).
4. Skim `docs/DECISIONS.md` and `docs/OPEN_TASKS.md`.
5. For deeper context: `docs/architecture.md`, `docs/api.md`, and the relevant
   code under `backend/app/` or `frontend/`.
6. Run `git status` / `git diff` (once git is initialized) to see uncommitted
   work.

## Key facts to internalize
- Pipeline order is fixed: language → PII detect → mask → safety gate → LLM
  (masked only) → output validation + final scan → storage.
- The ten privacy rules in `AGENTS.md` are non-negotiable.
- Backend = uv; Frontend = pnpm; Tailwind v4 (no config file).
- Keep `backend/app/schemas.py` and `frontend/lib/types.ts` in sync.

Produce a short summary of the current state and the target task before editing.
