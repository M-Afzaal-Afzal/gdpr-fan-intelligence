# Architecture

## Pipeline

```text
User
  → Next.js (frontend, sends raw text only)
    → FastAPI (validates request with Pydantic)
      → Language detection (en / de / mixed / unknown)
        → PII detection (regex + Presidio NER + German rules + hard negatives)
          → Anonymization (readable placeholders, stable numbering)
            → Safety gate (second PII scan on the masked message)
              → LLM (stub or OpenAI — masked message ONLY)
                → Output validation + final PII scan
                  → PostgreSQL (masked message + metadata + analysis only)
                    → Dashboard (privacy-safe aggregates)
```

## Components

### Frontend (`frontend/`)
Next.js 15 App Router + Tailwind v4 + shadcn-style UI. It only sends the raw
message and renders the structured response. It performs **no** PII detection
and holds **no** LLM secrets.

### Backend (`backend/`)
A single FastAPI service. Keeping the entire privacy engine in one Python
process means raw PII never crosses a service boundary.

| Module | Responsibility |
|--------|----------------|
| `services/language_service.py` | Coarse EN/DE/mixed detection |
| `services/pii_detector.py` | Four detection layers, returns spans only |
| `services/anonymizer.py` | Right-to-left replacement, stable `[TYPE_N]` tokens |
| `services/safety_gate.py` | Second scan + final output scrub |
| `services/llm_service.py` | Stub + OpenAI providers, masked input only |
| `services/output_validator.py` | JSON + enum validation + PII scrub |
| `db/models.py` | `analysis_results`, `pii_entities` (no value column), `audit_events` |
| `routes/analyze.py` | Orchestrates the whole flow |

## Detection layers

1. **Regex** — EMAIL, PHONE, MEMBER_ID, ORDER_ID, BOOKING_ID, SOCIAL_HANDLE.
   ID rules accept dataset variants (`BK-`, `BOOK-`, `MEM-`, `FAN-`, `ORD-`).
2. **Presidio NER** — PERSON → NAME, LOCATION/GPE → CITY (when the spaCy model
   is installed). A self-introduction name heuristic and a city list act as a
   fallback when Presidio is unavailable, so the demo still masks names offline.
3. **German rules** — street suffixes (`straße`, `str.`, `platz`, `weg`,
   `allee`, `gasse`, `ring`) and `Hausnummer N`.
4. **Hard negatives** — `Gate C`, `Block 12`, `Match Day 12`, `Berlin derby`,
   `Family Stand`, `South Stand`, `Bayern away game`, `Dortmund match`, etc. are
   protected from masking.

## Data model & privacy

- `analysis_results.raw_message_hash` is a SHA-256 digest, used only for
  deduplication — never the message.
- `pii_entities` stores `entity_type`, `start_char`, `end_char`,
  `replacement_token`, `confidence`. There is **no** `entity_value` column.
- `audit_events` records each pipeline step's status and latency.

## Failure handling

- LLM error → return masked message + PII, `llm_called=false`.
- PII after masking → `privacy_status=blocked`, LLM never called.
- Invalid LLM JSON → one stricter retry, else safe fallback (no storage of
  unsafe output).
- DB write failure → result still returned, `storage_status=failed`.
