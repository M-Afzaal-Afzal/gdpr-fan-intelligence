# Workflow: end_task

1. Summarize the work done (what changed and why).
2. List the changed files (actual paths).
3. List the commands run (and their results).
4. List current errors / blockers (or state "none").
5. Run the relevant checks (see `docs/COMMANDS.md`); after pipeline changes, run
   the leak test.
6. **Update `docs/AI_HANDOFF.md`** using the `update_handoff` skill.
7. Log new decisions in `docs/DECISIONS.md`, new errors in
   `docs/ERRORS_AND_FIXES.md`, and move items on `docs/OPEN_TASKS.md`.
8. Recommend concrete next steps for the following tool.
9. Commit with a clear message (see Git guidance in `docs/AI_WORKFLOW.md`).
