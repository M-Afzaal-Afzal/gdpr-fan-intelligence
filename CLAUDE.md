# CLAUDE.md — for Claude Code

@AGENTS.md

This project uses a shared, tool-agnostic instruction system. The line above
auto-imports the canonical `AGENTS.md` into context. **Do not rely on this file
alone.** Before doing anything:

1. Read **`AGENTS.md`** (the canonical instructions — stack, commands, privacy
   rules, code style, git workflow, safety rules, start/finish checklists).
2. Read **`docs/PROJECT_CONTEXT.md`** (what the project is and how it's built).
3. Read **`docs/AI_HANDOFF.md`** (current goal, status, and next steps — start
   from here, do not restart from zero).
4. Skim **`docs/DECISIONS.md`** (why things are the way they are) and
   **`docs/OPEN_TASKS.md`**.

Then follow the shared workflow in **`docs/AI_WORKFLOW.md`**.

## The one rule you must not forget

The product is **privacy-first**: raw PII must never reach the LLM and must
never be stored. The ten hard privacy rules are in `AGENTS.md`. Any change to
`backend/app/services/` or `backend/app/db/models.py` must preserve them, and
the leak test in `docs/COMMANDS.md` must still pass.

## Before ending a session

Update **`docs/AI_HANDOFF.md`** with what you did, files changed, commands run,
errors/blockers, decisions, and exact next steps — so the next tool (Cursor,
Kiro, Antigravity, Codex, or a fresh Claude session) can continue seamlessly.

> Detailed Claude-specific rules: `.claude/rules/ai-handoff.md` and
> `.claude/rules/code-quality.md`.
