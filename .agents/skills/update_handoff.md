# Skill: update_handoff

Keep `docs/AI_HANDOFF.md` accurate so any tool can continue seamlessly.

## When
After every meaningful task, and always before ending a session.

## How
1. Open `docs/AI_HANDOFF.md`.
2. Refresh the `_Last updated_` line (date + tool name).
3. Rewrite (don't endlessly append) these sections to reflect *now*:
   - Current Goal
   - Current Status
   - Last Completed Work
   - Files Changed Recently (actual paths)
   - Current Errors / Blockers (or "none")
   - Commands Already Run
   - Important Decisions (link to `docs/DECISIONS.md` for detail)
   - Next Recommended Steps (concrete, ordered)
   - Notes for Next AI Tool
4. Put durable history elsewhere: decisions → `docs/DECISIONS.md`, errors →
   `docs/ERRORS_AND_FIXES.md`, task moves → `docs/OPEN_TASKS.md`.
5. Be concise but complete. Never paste secrets or raw PII.
