---
inclusion: always
---

# Product (Kiro steering)

**Privacy-First Fan Intelligence Pipeline** — a GDPR-safe AI pipeline for
football fan messages. A user submits one raw fan message; the backend detects
PII, masks it, re-scans in a safety gate, and only then sends the *masked*
message to an LLM for analysis. Raw PII never reaches the LLM and is never
stored.

## Users

- Fan Insights Manager — understand fan sentiment/topics at scale.
- Support Team Lead — spot urgent complaints, refunds, booking/access issues.
- Club Data/AI team — integrate a privacy-safe pipeline.
- Hackathon jury — see a clear, working demo + architecture story.

## Goals

- Protect fan privacy (no raw PII to the LLM or storage).
- Preserve enough context for useful analysis (readable placeholders).
- Analyze one message at a time, reliably, with a clear demo.
- Support English, German, and mixed messages.

## Core features

- `POST /api/analyze-message` one-message pipeline.
- Layered PII detection + anonymization + safety gate + final output scan.
- LLM analysis: sentiment, topic, intent, urgency, summary, recommended action.
- Dashboard metrics, dataset page, architecture page.

> Canonical detail: `docs/PROJECT_CONTEXT.md`. Always also read `AGENTS.md` and
> `docs/AI_HANDOFF.md` (see `.kiro/steering/ai-handoff.md`).
