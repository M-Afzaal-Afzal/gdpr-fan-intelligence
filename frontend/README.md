# Frontend — Privacy-First Fan Intelligence

Next.js 15 (App Router) + React 19 + Tailwind CSS v4 + shadcn-style UI.

> **Tailwind v4 note:** there is **no** `tailwind.config.js`. Styling is configured
> through `postcss.config.mjs` (`@tailwindcss/postcss`) and `app/globals.css`
> (`@import "tailwindcss";` + `@theme` design tokens). Do not add a legacy config.

## Setup

```bash
cd frontend
pnpm install
cp .env.example .env.local   # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
pnpm dev                     # http://localhost:3000
```

## Scripts

| Script            | Purpose                       |
|-------------------|-------------------------------|
| `pnpm dev`        | Dev server (Turbopack)        |
| `pnpm build`      | Production build              |
| `pnpm start`      | Serve production build        |
| `pnpm lint`       | ESLint (flat config)          |
| `pnpm format`     | Prettier write                |
| `pnpm type-check` | `tsc --noEmit`                |

## Pages

- `/` — one-message demo: input, source dropdown, sample buttons, and five result
  cards (raw input, detected PII, masked message, AI insight, privacy status).
- `/dashboard` — totals, blocked count, latency, sentiment / topic / language
  distributions, and a recent-results table (from `GET /api/metrics`).
- `/dataset` — the canonical sample messages.
- `/architecture` — the pipeline diagram and the ten hard privacy rules.

## Components

`components/` holds the feature components (`MessageInput`, `PiiEntityTable`,
`MaskedMessageCard`, `AiInsightCard`, `PrivacyStatusBadge`, `MetricsDashboard`,
`SampleMessageButtons`, `SiteNav`). `components/ui/` holds the shadcn-style
primitives. `lib/` holds `api.ts`, `types.ts`, `schemas.ts`, and `constants.ts`.

## API configuration

The single env var `NEXT_PUBLIC_API_BASE_URL` points at the FastAPI backend.
All calls go through `lib/api.ts` (`analyzeMessage`, `getResults`, `getMetrics`,
`healthCheck`). The frontend never performs PII detection and never stores any
LLM secret.
