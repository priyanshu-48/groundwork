"""documents and jobs

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0003"
down_revision = "0002"

_NOW = sa.func.now()


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("org_id", sa.Uuid(), sa.ForeignKey("orgs.id"), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("s3_key", sa.String(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("kind", sa.Enum("invoice", "contract", "other", name="doc_kind"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "ready", "failed", name="doc_status"),
            nullable=False,
        ),
        sa.Column("error", sa.Text()),
        sa.Column("page_count", sa.Integer()),
        sa.UniqueConstraint("org_id", "sha256"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("queued", "running", "done", "failed", name="job_status"),
            nullable=False,
        ),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("run_after", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("locked_at", sa.DateTime(timezone=True)),
        sa.Column("locked_by", sa.String()),
        sa.Column("last_error", sa.Text()),
        sa.Column("idempotency_key", sa.String(), unique=True),
    )
    op.create_index("ix_jobs_status_run_after", "jobs", ["status", "run_after"])


def downgrade() -> None:
    op.drop_table("jobs")
    op.drop_table("documents")
    for t in ("job_status", "doc_status", "doc_kind"):
        op.execute(f"DROP TYPE {t}")
