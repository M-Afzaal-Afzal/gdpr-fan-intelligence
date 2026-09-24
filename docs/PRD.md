# PRD: Privacy-First Fan Intelligence Pipeline

**Project:** GDPR-Compliant AI Pipeline for Fan Intelligence  
**Context:** Raumdeuter AI Hackathon Challenge  
**Product Name:** Privacy-First Fan Intelligence Pipeline  
**Alternative Name:** GDPR-Safe AI Pipeline for Football Fan Messages  
**Version:** 1.0  
**Date:** 2026-05-19  
**Owner:** Hackathon Team  

---

## 1. Executive Summary

Football clubs receive large volumes of fan messages from support tickets, emails, feedback forms, app reviews, forums, and social media platforms. These messages often contain personally identifiable information (PII), including names, emails, phone numbers, addresses, cities, member IDs, booking IDs, order IDs, and social handles.

The goal of this product is to help clubs extract useful AI-powered insights from fan communication while protecting sensitive personal data. The system detects and masks PII before any LLM processing happens. Only the anonymized message is sent to the LLM for sentiment analysis, topic classification, intent detection, urgency detection, summarization, and recommended action generation.

The MVP will process **one message at a time**, because this is the clearest and safest approach for a two-day hackathon demo. Batch processing can be added later by reusing the same single-message pipeline.

---

## 2. Problem Statement

Football clubs need to understand fan feedback at scale, but raw fan messages contain sensitive data. Sending raw fan messages directly to an LLM creates privacy, GDPR, security, and trust risks.

### Example Raw Message

```text
Hi, I am Lukas Weber from Berlin. My email is lukas.weber@gmail.com.
I waited 45 minutes at Gate C and want a refund for booking BK-92811.
```

This message contains:

- Name: `Lukas Weber`
- City: `Berlin`
- Email: `lukas.weber@gmail.com`
- Booking ID: `BK-92811`

The LLM should **not** see this raw message.

### Safe Masked Message

```text
Hi, I am [NAME_1] from [CITY_1]. My email is [EMAIL_1].
I waited 45 minutes at Gate C and want a refund for booking [BOOKING_ID_1].
```

The masked version preserves enough context for AI analysis while protecting the fan’s private information.

---

## 3. Product Goals

| Goal | Description |
|---|---|
| Protect fan privacy | No raw PII should reach the LLM. |
| Preserve useful context | Masking should keep enough meaning for accurate AI analysis. |
| Analyze one message at a time | User can enter a single fan message and see the full pipeline result. |
| Support multilingual data | English, German, and mixed English-German messages should work. |
| Produce readable insights | Output should include sentiment, topic, intent, urgency, summary, and recommended action. |
| Store safe results only | Database should store masked messages and AI results, not raw PII. |
| Be demo-ready quickly | The system should be reliable, clear, and simple enough to build in two days. |

---

## 4. Non-Goals

These are intentionally out of scope for the MVP:

| Non-goal | Reason |
|---|---|
| Full production GDPR certification | Not realistic in a hackathon. |
| Real fan data ingestion | Synthetic data is safer and enough for the challenge. |
| Large-scale batch processing | One-message processing is clearer and faster for demo. |
| Training a custom NER model | Too time-consuming for MVP. |
| Full authentication and RBAC | Useful later, not needed for demo. |
| Queue-based distributed processing | Future scaling feature, not MVP. |
| Reversible deanonymization | Adds privacy risk and complexity. |
| Direct social media integrations | Not needed for the demo. |

---

## 5. Target Users

### 5.1 Primary User: Fan Insights Manager

A football club employee who wants to understand what fans are complaining about, asking for, or praising without manually reading thousands of messages.

### 5.2 Secondary User: Support Team Lead

A support manager who needs to identify urgent complaints, refund requests, accessibility issues, booking problems, or matchday operations issues.

### 5.3 Technical User: Club Data / AI Team

A technical team that wants to integrate a privacy-safe AI pipeline into existing fan communication systems.

### 5.4 Hackathon Jury

The jury needs to see:

- A working prototype or live demo
- Architecture explanation
- Technical decision walkthrough
- Privacy strategy overview
- Clear final presentation

---

## 6. MVP Scope

### 6.1 Must Have

- One-message input form
- PII detection
- PII masking/anonymization
- Second PII safety scan before LLM call
- LLM analysis on masked text only
- Human-readable output
- Safe result storage
- Basic dashboard

### 6.2 Should Have

- Dataset demo examples
- Metrics page
- Final PII scan on LLM output
- Hard-negative examples
- Prompt-injection test example
- Clear architecture page

### 6.3 Could Have

- CSV upload
- Batch evaluation
- Export results
- Authentication
- PostgreSQL instead of SQLite
- Docker Compose setup

### 6.4 Won’t Have in MVP

- Real social media connectors
- Queue worker architecture
- Custom model training
- Reversible token mapping
- Multi-tenant club accounts

---

## 7. User Stories and Acceptance Criteria

### User Story 1: Analyze One Fan Message

**As a** club employee,  
**I want to** paste one fan message into the app,  
**so that** I can see whether it contains PII and what the fan is talking about.

#### Acceptance Criteria

- User can enter a message in a textarea.
- User can select source type.
- User clicks “Analyze Safely.”
- System returns detected PII.
- System returns masked message.
- System returns AI insight only after masking.

---

### User Story 2: Detect PII

**As a** privacy-aware club,  
**I want to** detect personal information before AI processing,  
**so that** sensitive data is protected.

#### Acceptance Criteria

The system should detect:

- `NAME`
- `EMAIL`
- `PHONE`
- `CITY`
- `ADDRESS`
- `MEMBER_ID`
- `ORDER_ID`
- `BOOKING_ID`
- `SOCIAL_HANDLE`

Each detected entity should include:

```json
{
  "type": "EMAIL",
  "start": 42,
  "end": 64,
  "replacement": "[EMAIL_1]",
  "confidence": 1.0
}
```

---

### User Story 3: Mask PII

**As a** system user,  
**I want** personal data replaced with readable placeholders,  
**so that** the message remains useful but private.

#### Acceptance Criteria

- `Lukas Weber` becomes `[NAME_1]`
- `Berlin` becomes `[CITY_1]`
- `lukas.weber@gmail.com` becomes `[EMAIL_1]`
- `BK-92811` becomes `[BOOKING_ID_1]`
- Non-PII context like `Gate C`, `Block 12`, `Match Day 12`, or `Berlin derby` should not be masked unless clearly private.

---

### User Story 4: Prevent Unsafe LLM Calls

**As a** privacy officer,  
**I want** the system to block LLM calls if PII remains after masking,  
**so that** raw private data is not exposed.

#### Acceptance Criteria

- System performs a second PII scan after masking.
- If PII remains, the LLM call is blocked.
- Response shows `privacy_status = blocked`.
- If clean, response shows `privacy_status = safe_for_llm`.

---

### User Story 5: Generate Fan Intelligence

**As a** club analyst,  
**I want** AI output from the anonymized message,  
**so that** I can understand the fan issue quickly.

#### Acceptance Criteria

- LLM receives only the masked message.
- LLM returns valid JSON.
- Output contains sentiment, topic, intent, urgency, summary, and recommended action.
- Output is scanned again for PII before display and storage.

---

### User Story 6: Store Safe Results

**As a** product owner,  
**I want** results stored securely,  
**so that** a dashboard can be built without keeping raw personal data.

#### Acceptance Criteria

- Store masked message.
- Store detected PII types, not original PII values.
- Store AI analysis result.
- Do not store raw message by default.
- Store raw message hash only for deduplication.

---

## 8. Functional Requirements

### FR1: One-Message Input

The frontend must provide a textarea where users can enter one fan message.

#### Request Fields

```json
{
  "message": "string",
  "source": "support_ticket | email | social_media | app_review | forum | other"
}
```

#### Validation Rules

- Message cannot be empty.
- Message length should be between 20 and 5,000 characters.
- Source is optional but recommended.

---

### FR2: Language Detection

System should detect:

- `EN`
- `DE`
- `MIXED`
- `UNKNOWN`

This is important because the dataset includes English, German, and mixed English-German messages.

---

### FR3: PII Detection

The system must detect the following entities:

| Entity | Example |
|---|---|
| NAME | Lukas Weber |
| EMAIL | lukas.weber@gmail.com |
| PHONE | +49 176 12345678 |
| CITY | Berlin |
| ADDRESS | Heinz-Rühmann-Straße 9 |
| MEMBER_ID | MEM-48291 |
| ORDER_ID | ORD-92811 |
| BOOKING_ID | BK-83721 |
| SOCIAL_HANDLE | @lukasfan92 |

#### Recommended Detection Strategy

Use a layered approach:

```text
Microsoft Presidio
+ regex recognizers
+ custom football/fan ID recognizers
+ German address and phone patterns
+ hard-negative protection
```

---

### FR4: PII Masking

Detected PII should be replaced with context-preserving placeholders.

#### Example

```text
Lukas Weber → [NAME_1]
Berlin → [CITY_1]
lukas.weber@gmail.com → [EMAIL_1]
BK-92811 → [BOOKING_ID_1]
```

Good masking:

```text
[NAME_1] from [CITY_1] requested a refund for [BOOKING_ID_1].
```

Bad masking:

```text
[REDACTED] [REDACTED] [REDACTED].
```

---

### FR5: Second PII Safety Gate

Before calling the LLM, the backend must run the PII detector again on the masked message.

#### Logic

```python
if pii_found(masked_message):
    block_llm_call()
else:
    call_llm(masked_message)
```

#### Blocked Response Example

```json
{
  "privacy_status": "blocked",
  "llm_called": false,
  "reason": "PII still detected after masking"
}
```

---

### FR6: LLM Analysis

The LLM must analyze only the masked message.

#### Required Output

```json
{
  "sentiment": "positive | neutral | negative",
  "topic": "ticket_pricing | refund | booking_problem | merchandise | parking | accessibility | stadium_experience | food | security | streaming | membership | other",
  "intent": "complaint | question | refund_request | praise | cancellation | support_request | feedback",
  "urgency": "low | medium | high",
  "summary": "string",
  "recommended_action": "string"
}
```

---

### FR7: Output Validation

The backend must validate the LLM output.

#### Validation Rules

- Output must be valid JSON.
- Output must contain all required fields.
- Sentiment must be one of the allowed values.
- Topic must be one of the allowed values.
- Intent must be one of the allowed values.
- Urgency must be one of the allowed values.
- Summary must not contain PII.
- Recommended action must not contain PII.

---

### FR8: Final PII Scan on LLM Output

The system must run PII detection on:

- `summary`
- `recommended_action`

If PII is found, either:

- replace it with placeholders, or
- block the output and return a safe error.

---

### FR9: Secure Result Storage

The backend should store only safe data:

- `masked_message`
- `language`
- `pii_types_detected`
- `pii_count`
- `sentiment`
- `topic`
- `intent`
- `urgency`
- `summary`
- `recommended_action`
- `latency_ms`
- `privacy_status`
- `created_at`

Raw messages should not be stored by default.

---

### FR10: Dashboard

The dashboard should show:

| Metric | Description |
|---|---|
| Total messages analyzed | Count of processed messages |
| PII detected | Number of messages with PII |
| Blocked messages | Messages blocked before LLM |
| Average latency | Processing speed |
| Sentiment distribution | Positive / neutral / negative |
| Top topics | Most common fan issues |
| Language distribution | EN / DE / MIXED |
| Recent messages | Safe masked messages and insights |

---

### FR11: Dataset Demo Mode

The app should include sample messages from the synthetic dataset.

Required demo examples:

- English message with PII
- German message with PII
- Mixed English-German message with PII
- Hard-negative message without PII
- Prompt-injection style message with PII

---

## 9. Non-Functional Requirements

### NFR1: Privacy

- Raw messages must never be sent to the LLM.
- Raw messages should not be stored by default.
- Logs must not contain raw PII.
- PII entity values should not be stored.
- Only masked messages should be persisted.

---

### NFR2: Security

- API keys must be stored in backend `.env`.
- No API keys in frontend.
- CORS should be restricted to the frontend origin.
- Input validation should use Pydantic.
- Output validation should use strict schemas.
- Rate limiting is recommended for production.
- Final PII scan must happen before display and storage.
- Errors must not expose raw user input.

---

### NFR3: Performance

MVP target:

| Operation | Target |
|---|---:|
| PII detection + masking | < 1 second |
| LLM analysis | < 5 seconds |
| Total response time | < 7 seconds |
| One-message demo reliability | 95%+ successful runs |

---

### NFR4: Reliability

- If LLM fails, still return masked message and PII detection result.
- If PII safety gate fails, block LLM call.
- If database fails, still show the result in frontend but mark storage as failed.
- If JSON parsing fails, retry once with a stricter prompt or return a safe fallback.

---

### NFR5: Maintainability

- Clear separation between detection, masking, safety, LLM, and storage.
- Typed request and response schemas.
- Simple folder structure.
- Small functions.
- Unit tests for regex recognizers, masking, safety gate, and API responses.

---

## 10. Recommended System Architecture

### 10.1 High-Level Architecture

```text
Next.js / React Frontend
        ↓
FastAPI Python Backend
        ↓
Pydantic Input Validation
        ↓
Language Detection
        ↓
PII Detection
  - Microsoft Presidio
  - Regex Rules
  - German Custom Rules
  - Football-Specific ID Rules
        ↓
Masking / Anonymization
        ↓
Second PII Safety Gate
        ↓
LLM Analysis on Masked Text Only
        ↓
LLM Output Validation
        ↓
Final PII Scan on AI Output
        ↓
Secure Database Storage
        ↓
Dashboard / Results UI
```

---

### 10.2 Architecture Decision: Why FastAPI Backend

Because the core privacy engine is Python-based, the whole backend should be Python FastAPI instead of Express/Fastify plus a separate Python service.

Not recommended for MVP:

```text
Next.js → Node backend → Python Presidio service → Node backend → LLM → DB
```

Recommended:

```text
Next.js → FastAPI backend → Presidio → LLM → DB
```

#### Reasons

1. **Less complexity**  
   One backend is easier to build, test, debug, and explain.

2. **Better privacy control**  
   Raw PII stays inside one controlled backend service.

3. **Faster development**  
   Presidio, Pydantic, FastAPI, and Python LLM clients can live in the same backend.

4. **Cleaner demo story**  
   “The privacy pipeline runs in one Python backend before any LLM call.”

---

## 11. Technical Stack

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui optional

### Backend

- Python
- FastAPI
- Pydantic
- Microsoft Presidio Analyzer
- Microsoft Presidio Anonymizer
- Custom regex recognizers
- SQLite for MVP
- PostgreSQL later
- SQLAlchemy or SQLModel
- python-dotenv

### AI

- OpenAI / Gemini / Claude API
- Only masked messages sent to LLM

### Security

- `.env` for secrets
- No frontend API keys
- CORS restriction
- Sanitized logs
- PII safety gate
- Final output scan

---

## 12. Frontend Requirements

### 12.1 Pages

```text
/
Main one-message demo

/dashboard
Analytics and stored results

/dataset
Sample dataset examples

/architecture
Visual explanation of privacy pipeline
```

### 12.2 Main Page UI

The main page should include:

- Textarea: fan message input
- Dropdown: source type
- Button: Analyze Safely
- Result cards:
  1. Raw Input
  2. Detected PII
  3. Masked Safe Message
  4. AI Insight
  5. Privacy Status

### 12.3 Important Frontend Rule

The frontend should **not** do PII detection. It should only send the message to the backend.

Bad:

```text
React frontend detects and masks PII
```

Good:

```text
React frontend sends message to FastAPI backend
FastAPI backend detects and masks PII
```

---

## 13. Backend Requirements

### 13.1 Endpoints

```http
POST /api/analyze-message
GET  /api/results
GET  /api/results/{id}
GET  /api/metrics
GET  /api/health
```

---

### 13.2 POST `/api/analyze-message`

#### Request

```json
{
  "message": "Hallo, ich bin Lukas Weber from Berlin. My email is lukas.weber@gmail.com and I want a refund for booking BK-92811.",
  "source": "support_ticket"
}
```

#### Success Response

```json
{
  "id": "msg_001",
  "language": "mixed",
  "privacy_status": "safe_for_llm",
  "llm_called": true,
  "detected_pii": [
    {
      "type": "NAME",
      "start": 15,
      "end": 27,
      "replacement": "[NAME_1]",
      "confidence": 0.91
    },
    {
      "type": "CITY",
      "start": 33,
      "end": 39,
      "replacement": "[CITY_1]",
      "confidence": 0.88
    },
    {
      "type": "EMAIL",
      "start": 53,
      "end": 76,
      "replacement": "[EMAIL_1]",
      "confidence": 1.0
    },
    {
      "type": "BOOKING_ID",
      "start": 111,
      "end": 119,
      "replacement": "[BOOKING_ID_1]",
      "confidence": 1.0
    }
  ],
  "masked_message": "Hallo, ich bin [NAME_1] from [CITY_1]. My email is [EMAIL_1] and I want a refund for booking [BOOKING_ID_1].",
  "analysis": {
    "sentiment": "negative",
    "topic": "refund",
    "intent": "refund_request",
    "urgency": "medium",
    "summary": "A fan requests a refund related to a booking issue.",
    "recommended_action": "Review the booking issue and respond with refund options."
  },
  "latency_ms": 2840
}
```

#### Blocked Response

```json
{
  "id": "msg_002",
  "language": "de",
  "privacy_status": "blocked",
  "llm_called": false,
  "reason": "PII still detected after masking",
  "masked_message": "Partial masked message here",
  "detected_pii": []
}
```

---

## 14. Database Design

For MVP, use SQLite. For a stronger production-ready version, use PostgreSQL.

### 14.1 Table: `analysis_results`

```sql
CREATE TABLE analysis_results (
    id TEXT PRIMARY KEY,
    source TEXT,
    language TEXT,
    raw_message_hash TEXT,
    masked_message TEXT NOT NULL,
    pii_types_detected TEXT,
    pii_count INTEGER,
    sentiment TEXT,
    topic TEXT,
    intent TEXT,
    urgency TEXT,
    summary TEXT,
    recommended_action TEXT,
    privacy_status TEXT NOT NULL,
    llm_called BOOLEAN NOT NULL,
    latency_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 14.2 Table: `pii_entities`

```sql
CREATE TABLE pii_entities (
    id TEXT PRIMARY KEY,
    message_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    start_char INTEGER,
    end_char INTEGER,
    replacement_token TEXT NOT NULL,
    confidence REAL,
    FOREIGN KEY (message_id) REFERENCES analysis_results(id)
);
```

Important: do **not** store original PII values.

Bad:

```sql
entity_value = 'lukas.weber@gmail.com'
```

Good:

```sql
entity_type = 'EMAIL'
replacement_token = '[EMAIL_1]'
```

---

### 14.3 Table: `audit_events`

```sql
CREATE TABLE audit_events (
    id TEXT PRIMARY KEY,
    message_id TEXT,
    step_name TEXT NOT NULL,
    status TEXT NOT NULL,
    latency_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 15. Backend Folder Structure

```text
backend/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── routes/
│   │   ├── analyze.py
│   │   ├── results.py
│   │   └── metrics.py
│   │
│   ├── services/
│   │   ├── language_service.py
│   │   ├── pii_detector.py
│   │   ├── anonymizer.py
│   │   ├── safety_gate.py
│   │   ├── llm_service.py
│   │   ├── output_validator.py
│   │   └── metrics_service.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repositories.py
│   │
│   └── tests/
│       ├── test_pii_detector.py
│       ├── test_anonymizer.py
│       ├── test_safety_gate.py
│       └── test_api.py
│
├── requirements.txt
└── .env.example
```

---

## 16. Frontend Folder Structure

```text
frontend/
│
├── app/
│   ├── page.tsx
│   ├── dashboard/page.tsx
│   ├── dataset/page.tsx
│   └── architecture/page.tsx
│
├── components/
│   ├── MessageInput.tsx
│   ├── PiiEntityTable.tsx
│   ├── MaskedMessageCard.tsx
│   ├── AiInsightCard.tsx
│   ├── PrivacyStatusBadge.tsx
│   └── MetricsDashboard.tsx
│
├── lib/
│   ├── api.ts
│   └── types.ts
│
└── .env.local
```

---

## 17. Core Processing Sequence

```text
1. User enters message in Next.js UI
2. Frontend sends POST request to FastAPI
3. FastAPI validates request with Pydantic
4. Backend detects language
5. Backend runs PII detection
6. Backend masks PII
7. Backend runs second PII scan on masked message
8. If PII remains, block LLM call
9. If safe, send only masked message to LLM
10. Backend validates LLM JSON
11. Backend scans LLM output for PII
12. Backend stores safe result
13. Frontend displays full pipeline result
```

---

## 18. PII Detection Strategy

Use layered detection.

### Layer 1: Regex

Best for structured entities:

- `EMAIL`
- `PHONE`
- `MEMBER_ID`
- `ORDER_ID`
- `BOOKING_ID`
- `SOCIAL_HANDLE`

Example categories:

```text
Email: standard email regex
Phone: German and international phone formats
Booking ID: BK-[0-9]{4,8}
Order ID: ORD-[0-9]{4,8}
Member ID: MEM-[0-9]{4,8}
Social handle: @[A-Za-z0-9_]{3,30}
```

---

### Layer 2: Presidio NER

Best for:

- `PERSON`
- `LOCATION`
- `ADDRESS-like entities`

---

### Layer 3: Custom German Rules

Add patterns for:

- `Straße`
- `Str.`
- `Platz`
- `Weg`
- `Allee`
- `Hausnummer`
- German phone formats
- German city references

---

### Layer 4: Hard-Negative Protection

Avoid masking normal football context:

- Gate C
- Block 12
- Match Day 12
- Berlin derby
- Family Stand
- South Stand
- Bayern away game
- Dortmund match

---

## 19. LLM Prompt Design

### System Prompt

```text
You are analyzing anonymized football fan messages.

Rules:
- The message has already been anonymized.
- Do not infer, recreate, or invent names, emails, phone numbers, addresses, member IDs, order IDs, booking IDs, or social handles.
- Analyze only the provided masked message.
- Return only valid JSON.
- Do not include personal data in the summary or recommended action.
```

### User Message

```text
Masked message:
{masked_message}
```

### Required JSON Output

```json
{
  "sentiment": "positive | neutral | negative",
  "topic": "ticket_pricing | refund | booking_problem | merchandise | parking | accessibility | stadium_experience | food | security | streaming | membership | other",
  "intent": "complaint | question | refund_request | praise | cancellation | support_request | feedback",
  "urgency": "low | medium | high",
  "summary": "One sentence summary without PII.",
  "recommended_action": "One short operational action."
}
```

---

## 20. Success Metrics

| Metric | Target |
|---|---:|
| PII leakage rate before LLM | 0% for demo set |
| Email masking recall | 100% |
| Phone masking recall | 95%+ |
| ID masking recall | 95%+ |
| Name/city detection recall | 80%+ MVP target |
| False positive rate on hard negatives | Low enough to explain clearly |
| Average total latency | < 7 seconds |
| LLM JSON validity | 95%+ |
| Demo success rate | 95%+ |
| Raw PII stored | 0 values |

Most important metric:

```text
PII leakage rate before LLM = 0
```

---

## 21. Evaluation Plan

Use the synthetic dataset.

### Evaluation Steps

```text
1. Load test examples from JSONL.
2. Run PII detector on raw_message.
3. Compare detected entities with gold labels.
4. Calculate precision, recall, and F1.
5. Generate masked message.
6. Check if any gold PII value remains in masked message.
7. Run LLM task on masked message.
8. Validate JSON output.
9. Scan output for PII leakage.
10. Store metrics.
```

### Metrics to Calculate

- PII precision
- PII recall
- PII F1
- PII leakage rate
- False positive count
- Latency per message
- LLM cost estimate
- Topic distribution
- Sentiment distribution

---

## 22. Privacy and Security Requirements

| Area | Requirement |
|---|---|
| Raw message handling | Process in memory only by default |
| LLM input | Only masked message |
| Logs | Never log raw message |
| Database | Store masked message and AI result only |
| PII entity table | Store type and position, not value |
| API keys | Backend `.env` only |
| Frontend | No LLM or API secrets |
| Retention | For demo, no raw retention |
| Output | Final PII scan before display |
| Error messages | Do not expose raw input |

---

## 23. Error Handling

### 23.1 LLM Failure

If the LLM call fails:

- Return masked message and detected PII.
- Set `analysis_status = failed`.
- Do not expose internal errors.
- Allow the user to retry.

### 23.2 PII Still Detected After Masking

If PII remains after masking:

- Do not call the LLM.
- Return `privacy_status = blocked`.
- Show detected issue safely.
- Ask user to review or use stricter masking.

### 23.3 Invalid LLM JSON

If the LLM returns invalid JSON:

- Retry once with stricter prompt.
- If still invalid, return fallback error.
- Do not store unsafe output.

### 23.4 Database Failure

If database save fails:

- Show the result to the user.
- Mark `storage_status = failed`.
- Do not lose the demo flow.

---

## 24. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Presidio misses German names/cities | PII leakage risk | Add custom rules and curated examples |
| False positives on football context | Bad UX | Add hard-negative patterns |
| LLM returns invalid JSON | App breaks | Strict prompt, schema validation, retry once |
| LLM output contains PII | Privacy risk | Final PII scan |
| App too complex for two days | Demo failure | Keep one-message MVP first |
| Raw PII appears in logs | Privacy failure | Disable raw logging and sanitize errors |
| LLM API slow/fails | Poor demo | Return masked result even if AI fails |

---

## 25. Key Trade-Offs

| Decision | Chosen Option | Reason |
|---|---|---|
| Backend | FastAPI Python | Best because Presidio is Python-native |
| Frontend | Next.js React | Matches team skillset |
| Processing | One message at a time | Best for demo clarity and debugging |
| Storage | SQLite first | Fastest for MVP |
| PII masking | Placeholder replacement | Best balance of privacy and context |
| LLM | External API after masking | Fast to implement and safe after anonymization |
| Queue | Not in MVP | Too much complexity for two days |

---

## 26. Two-Day Development Roadmap

### Day 1: Build Privacy Pipeline

Goal:

```text
Raw message → PII detection → masking → safety gate → UI display
```

| Time | Task |
|---|---|
| 09:00–10:00 | Setup Next.js frontend and FastAPI backend |
| 10:00–11:00 | Create `/api/analyze-message` endpoint |
| 11:00–13:00 | Add Presidio + regex PII detection |
| 13:00–15:00 | Add masking with placeholders |
| 15:00–16:00 | Add second PII safety scan |
| 16:00–18:00 | Build Next.js input + result cards |
| 18:00–20:00 | Test English, German, mixed, and hard-negative examples |

Day 1 is done when:

```text
A mixed German-English message with email, name, city, phone, and booking ID is correctly masked and shown in the UI.
```

---

### Day 2: Add LLM, Storage, Dashboard, Demo Polish

Goal:

```text
Masked message → LLM analysis → validated output → safe storage → dashboard
```

| Time | Task |
|---|---|
| 09:00–10:30 | Add LLM service |
| 10:30–11:30 | Add strict JSON validation |
| 11:30–12:30 | Add final PII scan on LLM output |
| 12:30–14:00 | Add SQLite storage |
| 14:00–16:00 | Build dashboard |
| 16:00–17:00 | Add sample dataset examples |
| 17:00–18:30 | Test prompt-injection and leakage cases |
| 18:30–20:00 | Polish UI and prepare demo story |

Day 2 is done when:

```text
The app can process one realistic fan message, mask PII, block unsafe cases, call the LLM only with safe text, store the result, and show dashboard metrics.
```

---

## 27. Definition of Done

The MVP is complete when:

```text
1. User can enter one fan message.
2. Backend detects PII.
3. Backend masks PII with placeholders.
4. Backend performs second safety scan.
5. LLM is called only if the message is safe.
6. LLM returns sentiment, topic, intent, urgency, summary, and action.
7. LLM output is validated and scanned for PII.
8. Safe result is stored.
9. Dashboard shows basic metrics.
10. Demo can show English, German, mixed, no-PII, and prompt-injection examples.
```

---

## 28. Future Production Architecture

For the hackathon, use synchronous one-message processing.

For real club scale, evolve to:

```text
API Gateway
        ↓
Message Queue
        ↓
PII Worker Pool
        ↓
Masked Message Queue
        ↓
LLM Worker Pool
        ↓
PostgreSQL / Data Warehouse
        ↓
Dashboard / BI Layer
```

### Future Improvements

- PostgreSQL instead of SQLite
- Redis queue or Celery workers
- User authentication
- Role-based access control
- Audit log dashboard
- Batch upload
- API rate limiting
- Multi-club tenancy
- Automated PII evaluation report
- Cost tracking per 1,000 messages
- Deployment using Docker Compose
- Monitoring and alerting

---

## 29. Final Recommended Architecture Summary

```text
User enters message
        ↓
Next.js frontend sends message to FastAPI
        ↓
FastAPI validates request
        ↓
Language detection
        ↓
Presidio + regex + custom rules detect PII
        ↓
Masking service replaces PII with placeholders
        ↓
Second safety gate scans masked message
        ↓
If unsafe: block LLM
If safe: send masked message to LLM
        ↓
LLM returns structured JSON insight
        ↓
Backend validates JSON
        ↓
Final PII scan on summary/action
        ↓
Store only safe result
        ↓
Show result and dashboard
```

---

## 30. Final Demo Story

Use this explanation in your presentation:

> Our system treats privacy as the first step, not the final check. A fan message is processed locally in the backend, where PII such as names, emails, phones, addresses, cities, booking IDs, order IDs, member IDs, and social handles is detected and masked. Then a second safety gate checks that no PII remains. Only after this step does the LLM receive the anonymized message. The LLM returns sentiment, topic, intent, urgency, summary, and recommended action. We store only the safe masked message and analysis result, allowing clubs to understand fans without exposing personal data.

---

## 31. Development Priority Checklist

### Highest Priority

- [ ] FastAPI project setup
- [ ] Next.js project setup
- [ ] `/api/analyze-message` endpoint
- [ ] PII detection with Presidio
- [ ] Regex detection for emails, phones, IDs, handles
- [ ] Masking with placeholders
- [ ] Second safety gate
- [ ] Frontend input page

### Medium Priority

- [ ] LLM analysis service
- [ ] Output schema validation
- [ ] Final PII scan on LLM output
- [ ] SQLite storage
- [ ] Dashboard metrics

### Lower Priority

- [ ] Dataset sample page
- [ ] Architecture page
- [ ] Batch CSV upload
- [ ] Export results
- [ ] Docker Compose

---

## 32. Final Notes for Implementation

The best practical implementation is:

```text
Frontend:
Next.js + React + TypeScript + Tailwind

Backend:
FastAPI + Pydantic + Presidio + custom regex

Storage:
SQLite for hackathon, PostgreSQL later

AI:
External LLM API only after masking

Privacy:
No raw message storage, no raw PII logs, no raw PII to LLM
```

This system is simple enough to build quickly, strong enough to explain technically, and directly aligned with the hackathon requirements.
