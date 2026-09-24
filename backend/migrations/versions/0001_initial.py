"""initial schema — analysis_results, pii_entities, audit_events

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-20 12:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "analysis_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("raw_message_hash", sa.String(length=128), nullable=True),
        sa.Column("masked_message", sa.Text(), nullable=False),
        sa.Column("pii_types_detected", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("pii_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sentiment", sa.String(length=32), nullable=True),
        sa.Column("topic", sa.String(length=64), nullable=True),
        sa.Column("intent", sa.String(length=64), nullable=True),
        sa.Column("urgency", sa.String(length=16), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("recommended_action", sa.Text(), nullable=True),
        sa.Column("privacy_status", sa.String(length=32), nullable=False),
        sa.Column("llm_called", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_analysis_results_created_at", "analysis_results", ["created_at"])
    op.create_index("ix_analysis_results_sentiment", "analysis_results", ["sentiment"])
    op.create_index("ix_analysis_results_topic", "analysis_results", ["topic"])
    op.create_index("ix_analysis_results_language", "analysis_results", ["language"])
    op.create_index("ix_analysis_results_privacy_status", "analysis_results", ["privacy_status"])

    op.create_table(
        "pii_entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "message_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analysis_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("start_char", sa.Integer(), nullable=False),
        sa.Column("end_char", sa.Integer(), nullable=False),
        sa.Column("replacement_token", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_pii_entities_message_id", "pii_entities", ["message_id"])

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("step_name", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_audit_events_message_id", "audit_events", ["message_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_events_message_id", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_pii_entities_message_id", table_name="pii_entities")
    op.drop_table("pii_entities")
    for ix in (
        "ix_analysis_results_privacy_status",
        "ix_analysis_results_language",
        "ix_analysis_results_topic",
        "ix_analysis_results_sentiment",
        "ix_analysis_results_created_at",
    ):
        op.drop_index(ix, table_name="analysis_results")
    op.drop_table("analysis_results")
