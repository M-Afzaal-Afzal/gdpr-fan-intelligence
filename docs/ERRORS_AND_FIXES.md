# Errors and Fixes

A running log of problems hit and how they were resolved, so no AI tool wastes
time re-debugging a known issue. Newest first. Use the format below.

```md
## YYYY-MM-DD — <short error title>
- **Error:** the message / symptom
- **Cause:** root cause
- **Fix:** what resolved it
- **Files involved:** paths
```

---

## 2026-05-21 — Lowercase intro name not masked
- **Error:** "Hi, I am afzaal…" left "afzaal" unmasked (0 entities detected).
- **Cause:** the intro-name regex only matched capitalized names, and Presidio
  NER also misses lowercase names.
- **Fix:** allow lowercase tokens after intro triggers, run the fallback on
  every request, and add a stopword guard to avoid masking "I am very/from…".
- **Files involved:** `backend/app/services/pii_detector.py`,
  `backend/app/tests/test_pipeline_edge_cases.py`.

## 2026-05-21 — "during" masked as a German address
- **Error:** "Bayern away game during the…" masked "during" as `[ADDRESS_1]`.
- **Cause:** the `ring` street suffix matched "Du**ring**" under IGNORECASE.
- **Fix:** removed `ring` from the German street regex.
- **Files involved:** `backend/app/services/pii_detector.py`.

## 2026-05-20 — `docker compose up --build` frontend build failed
- **Error:** `ERR_UNKNOWN_BUILTIN_MODULE: No such built-in module: node:sqlite`
  during `pnpm install` in the frontend image.
- **Cause:** `node:20-alpine` + corepack pulled pnpm 11, which requires Node
  ≥ 22.13 and the `node:sqlite` builtin.
- **Fix:** bumped the image to `node:22-alpine` and pinned `pnpm@9.15.4` via the
  `packageManager` field.
- **Files involved:** `frontend/Dockerfile`, `frontend/package.json`.

## 2026-05-20 — `next build` failed on unused import
- **Error:** ESLint `@typescript-eslint/no-unused-vars` for `Badge`.
- **Cause:** leftover import after refactor in `MetricsDashboard.tsx`.
- **Fix:** removed the unused import; build passes.
- **Files involved:** `frontend/components/MetricsDashboard.tsx`.

## 2026-09-24 — stub LLM fallback crashed
- **Error:** `'str' object has no attribute 'value'` on every stub fallback.
- **Cause:** corrupted line in `_stub_analysis`: `sentiment =  (msg)` assigned the
  raw message string instead of calling the classifier.
- **Fix:** `sentiment = _stub_sentiment(msg)`; 77 tests pass.
- **Files involved:** `backend/app/services/llm_service.py`.

## 2026-09-24 — Fireworks model 404
- **Error:** 404 from Fireworks for `accounts/fireworks/models/deepseek-v4-pro`.
- **Cause:** model retired upstream.
- **Workaround:** env override `FIREWORKS_MODEL=accounts/fireworks/models/deepseek-v4p1-flash`
  (works). `backend/.env` itself not edited — update it.
