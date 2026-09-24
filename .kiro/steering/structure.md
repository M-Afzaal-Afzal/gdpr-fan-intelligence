---
inclusion: always
---

# Structure (Kiro steering)

```text
gdpr-fan-intelligence/
├── backend/app/
│   ├── config.py      settings (pydantic-settings)
│   ├── schemas.py     Pydantic enums + request/response contract
│   ├── routes/        analyze.py (orchestrator), results, metrics, health
│   ├── services/      pii_detector, anonymizer, safety_gate, llm_service,
│   │                  output_validator, language_service, metrics_service
│   ├── db/            database.py, models.py, repositories.py
│   └── tests/         pytest suite
├── backend/migrations/  Alembic (env.py, versions/0001_initial.py)
├── frontend/app/        routes: /, /dashboard, /dataset, /architecture
├── frontend/components/  features + ui/ (shadcn-style primitives)
├── frontend/lib/        api.ts, types.ts, schemas.ts, constants.ts, utils.ts
├── data/                sample_messages.jsonl
└── docs/                cross-AI context system + architecture.md, api.md
```

## Naming / conventions

- Python: snake_case modules; `from __future__ import annotations` + a module
  docstring; small pure functions in `services/`.
- React: PascalCase components; shared primitives in `components/ui/`; the
  `cn()` helper in `lib/utils.ts`; types mirror `backend/app/schemas.py`.

## Where new code goes

- New PII rule → `backend/app/services/pii_detector.py` (+ a test).
- New API field → update `backend/app/schemas.py` **and**
  `frontend/lib/types.ts` together.
- New endpoint → `backend/app/routes/` + register in `app/main.py`.
- New UI primitive → `frontend/components/ui/`; new feature card →
  `frontend/components/`.
- Schema change → new Alembic migration in `backend/migrations/versions/`.
