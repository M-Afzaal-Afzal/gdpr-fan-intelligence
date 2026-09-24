# Antigravity workspace rule — AI handoff

> This file lives in `.agents/rules/`, which Antigravity auto-loads as workspace
> rules (alongside the root `AGENTS.md`). The richer agent/skill/workflow
> definitions are in `.agents/agents.md`, `.agents/skills/`, `.agents/workflows/`.

This repo shares context across multiple AI tools. Always:

1. Read `AGENTS.md` (canonical: stack, commands, the ten privacy rules, style).
2. Read `docs/PROJECT_CONTEXT.md` and `docs/AI_HANDOFF.md` (start from the latter).
3. Skim `docs/DECISIONS.md`.

Continue from "Next Recommended Steps" in `docs/AI_HANDOFF.md` — do not restart
from zero. Before finishing, run the relevant checks (`docs/COMMANDS.md`) and
**update `docs/AI_HANDOFF.md`** so the next tool can continue. Never weaken the
ten privacy rules; never store raw PII; the frontend holds no secrets.

Full workflow + prompts: `docs/AI_WORKFLOW.md`.
