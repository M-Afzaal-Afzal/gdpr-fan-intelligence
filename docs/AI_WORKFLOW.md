# AI Workflow — moving work between Kiro, Antigravity, Cursor, Claude Code, Codex

This repo uses **one canonical source of truth** (`AGENTS.md` + `docs/*`) and
thin per-tool wrappers. The goal: pick up in any tool without restarting.

## The golden rule

`docs/AI_HANDOFF.md` is the baton. **Read it when you start; update it before
you stop.** Everything else (decisions, errors, tasks) supports it.

## Before leaving one tool

1. Make sure your changes are coherent and the relevant checks pass
   (see `docs/COMMANDS.md`).
2. Update `docs/AI_HANDOFF.md` (goal, status, files changed, commands run,
   errors, decisions, next steps).
3. Log any new decision in `docs/DECISIONS.md` and any new error in
   `docs/ERRORS_AND_FIXES.md`; update `docs/OPEN_TASKS.md`.
4. Commit (see Git flow below).

## When starting in a new tool

1. Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/AI_HANDOFF.md`,
   `docs/DECISIONS.md`, `docs/COMMANDS.md`.
2. Run `git status` / `git diff` to see uncommitted work.
3. Summarize what you understand, then continue from "Next Recommended Steps"
   in `docs/AI_HANDOFF.md`. Do **not** restart from zero.

## How to avoid losing context

- Treat `docs/AI_HANDOFF.md` as mandatory, not optional.
- Commit at every handoff so the next tool sees a clean, described state.
- Keep the handoff concise — link to decisions/errors instead of pasting them.

## How to avoid duplicate / repeated work

- Check `docs/OPEN_TASKS.md` (Done / In Progress) before starting.
- Check `docs/ERRORS_AND_FIXES.md` before debugging — the fix may exist.
- Reuse existing components/services; don't recreate patterns (see
  `.cursor/rules/code-quality.mdc`).

## Copy-paste prompts

**Before leaving any AI tool:**

> Before we stop, update docs/AI_HANDOFF.md. Include what was done, files
> changed, commands run, current errors, important decisions, and exact next
> steps for another AI coding tool. Be concise but complete.

**When starting in a new AI tool:**

> Read AGENTS.md, docs/PROJECT_CONTEXT.md, docs/AI_HANDOFF.md, docs/DECISIONS.md,
> and docs/COMMANDS.md first. Continue from the current handoff. Do not restart
> from zero. First summarize what you understand, then continue the next
> recommended step.

**For bug fixing:**

> Read docs/ERRORS_AND_FIXES.md and docs/AI_HANDOFF.md first. Check whether this
> error already happened before. Reuse existing fixes if relevant. After fixing,
> update both docs/ERRORS_AND_FIXES.md and docs/AI_HANDOFF.md.

**For feature work:**

> Read AGENTS.md, docs/PROJECT_CONTEXT.md, docs/DECISIONS.md, and
> docs/AI_HANDOFF.md. Implement the feature using existing project patterns. Do
> not introduce new libraries unless necessary. Run available checks. Update
> docs/AI_HANDOFF.md before finishing.

## Git safety guidance

Recommended handoff flow:

1. Start task (read the handoff).
2. Let the AI tool work.
3. Review the changes.
4. Run the relevant checks (`docs/COMMANDS.md`).
5. Update `docs/AI_HANDOFF.md`.
6. Commit with a clear message.
7. Continue in another tool if needed.

Safe example commands:

```bash
git status
git diff
git add .
git commit -m "Update AI handoff and project context"
```

Do **not** use destructive git commands (`reset --hard`, `push --force`,
`clean -f`, `checkout .`) unless you explicitly intend to and understand the
consequences. The shared rule in `AGENTS.md` forbids them without explicit
instruction.

> The repo is public on GitHub — double-check that no secrets or real PII are staged
> before every push.
