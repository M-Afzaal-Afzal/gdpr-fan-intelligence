"""SQLAlchemy 2.0 engine + session factory.

We use the sync engine on purpose: the work per request is small, and
keeping the surface area simple makes the privacy-critical flow easier
to reason about. We still wrap calls with FastAPI dependency injection
so they participate in clean request lifecycle handling.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a request-scoped session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
