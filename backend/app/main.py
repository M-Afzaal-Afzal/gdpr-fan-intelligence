"""FastAPI application entrypoint.

Privacy-related design notes
----------------------------
- We log only sanitized fields. The default uvicorn access log is fine; we
  never log request bodies.
- CORS is locked to the configured frontend origin in production.
- Errors are returned as generic 4xx/5xx — never echo back the user message.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import analyze, health, llm_providers, metrics, results

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)

app = FastAPI(
    title="Privacy-First Fan Intelligence API",
    description=(
        "GDPR-safe AI pipeline for football fan messages. Raw PII never reaches "
        "the LLM and is never persisted."
    ),
    version="0.1.0",
)

# CORS — restrict to the configured frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(llm_providers.router, prefix="/api", tags=["llm"])
app.include_router(results.router, prefix="/api", tags=["results"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])
app.include_router(health.router, prefix="/api", tags=["health"])


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "service": "Privacy-First Fan Intelligence",
        "docs": "/docs",
        "health": "/api/health",
    }
