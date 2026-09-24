# API Reference

Base URL: `http://localhost:8000`. All endpoints are under `/api`.
Interactive docs: `/docs` (Swagger) and `/redoc`.

## POST `/api/analyze-message`

Runs the full privacy pipeline on one message.

### Request

```json
{
  "message": "string (5–5000 chars, required)",
  "source": "support_ticket | email | social_media | app_review | forum | other"
}
```

`source` is optional and defaults to `other`.

### Success response (`200`)

```json
{
  "id": "uuid-string",
  "language": "en | de | mixed | unknown",
  "privacy_status": "safe_for_llm",
  "llm_called": true,
  "detected_pii": [
    { "type": "EMAIL", "start": 42, "end": 64, "replacement": "[EMAIL_1]", "confidence": 1.0 }
  ],
  "masked_message": "Hi, I am [NAME_1] from [CITY_1]. My email is [EMAIL_1] ...",
  "analysis": {
    "sentiment": "negative",
    "topic": "refund",
    "intent": "refund_request",
    "urgency": "medium",
    "summary": "One sentence without personal data.",
    "recommended_action": "One short operational action."
  },
  "latency_ms": 1234,
  "storage_status": "stored"
}
```

### Blocked response (`200`)

When PII remains after masking, the LLM is never called:

```json
{
  "id": "uuid-string",
  "language": "de",
  "privacy_status": "blocked",
  "llm_called": false,
  "reason": "PII still detected after masking",
  "detected_pii": [],
  "masked_message": "partial masked message",
  "analysis": null,
  "latency_ms": 800,
  "storage_status": "stored"
}
```

### Validation errors (`422`)

Message shorter than 5 or longer than 5000 characters.

## GET `/api/results`

Query param `limit` (1–100, default 25). Returns recent stored results
(masked message + metadata + analysis). Never returns raw PII.

## GET `/api/results/{id}`

Returns a single result by UUID, or `404`.

## GET `/api/metrics`

```json
{
  "total_messages": 12,
  "pii_detected_count": 9,
  "blocked_count": 1,
  "average_latency_ms": 142.5,
  "sentiment_distribution": { "negative": 7, "neutral": 4, "positive": 1 },
  "topic_distribution": { "refund": 5, "stadium_experience": 3 },
  "language_distribution": { "en": 6, "de": 4, "mixed": 2 },
  "recent_results": [ /* ResultListItem[] */ ]
}
```

## GET `/api/health`

```json
{ "status": "ok", "database": "ok", "environment": "development", "llm_provider": "stub" }
```

`status` is `degraded` and `database` is `down` if the DB is unreachable.
