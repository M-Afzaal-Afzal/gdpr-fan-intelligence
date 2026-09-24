---
inclusion: always
---

# AI Handoff (Kiro steering)

This project shares context across multiple AI tools through canonical docs.

## Always read first

1. `AGENTS.md` — canonical instructions (stack, commands, privacy rules, style).
2. `docs/PROJECT_CONTEXT.md` — what the project is.
3. `docs/AI_HANDOFF.md` — current goal, status, next steps. **Start here.**
4. `docs/DECISIONS.md` — why things are the way they are.

## Always do before finishing

- Run the relevant checks (`docs/COMMANDS.md`).
- **Update `docs/AI_HANDOFF.md` after every meaningful task** so the next tool
  (Cursor, Antigravity, Claude Code, Codex) can continue without restarting.
- Log new decisions in `docs/DECISIONS.md`, new errors in
  `docs/ERRORS_AND_FIXES.md`, and update `docs/OPEN_TASKS.md`.

Do not restart from zero — continue from "Next Recommended Steps" in the handoff.
Preserve the ten privacy rules in `AGENTS.md`.
