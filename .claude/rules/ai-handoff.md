# Claude rule — AI handoff

This repo shares context across AI tools through canonical docs. At the start of
a session read, in order: `AGENTS.md`, `docs/PROJECT_CONTEXT.md`,
`docs/AI_HANDOFF.md`, `docs/DECISIONS.md`.

Start from "Next Recommended Steps" in `docs/AI_HANDOFF.md` — do not restart
from zero. Before ending the session, update `docs/AI_HANDOFF.md` (work done,
files changed, commands run, errors, decisions, next steps), and log new
decisions/errors in `docs/DECISIONS.md` / `docs/ERRORS_AND_FIXES.md`.

Full workflow + prompts: `docs/AI_WORKFLOW.md`.
