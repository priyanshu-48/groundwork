"""conversations, messages, agent runs and steps

Revision ID: 0006
Revises: 0005
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0006"
down_revision = "0005"


def _base() -> list[sa.Column]:  # type: ignore[type-arg]
    return [
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "conversations",
        *_base(),
        sa.Column("org_id", sa.Uuid(), sa.ForeignKey("orgs.id"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String()),
    )
    op.create_index("ix_conversations_org", "conversations", ["org_id"])
    op.create_table(
        "messages",
        *_base(),
        sa.Column(
            "conversation_id",
            sa.Uuid(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.Enum("user", "assistant", name="message_role"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations", postgresql.JSONB()),
    )
    op.create_index("ix_messages_conversation", "messages", ["conversation_id", "created_at"])
    op.create_table(
        "agent_runs",
        *_base(),
        sa.Column(
            "message_id",
            sa.Uuid(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("model", sa.String()),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.Enum("ok", "error", "max_steps", name="run_status"), nullable=False),
        sa.Column("error", sa.Text()),
    )
    op.create_table(
        "agent_steps",
        *_base(),
        sa.Column(
            "run_id", sa.Uuid(), sa.ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("step_no", sa.Integer(), nullable=False),
        sa.Column("tool_name", sa.String(), nullable=False),
        sa.Column("args", postgresql.JSONB(), nullable=False),
        sa.Column("result_preview", sa.Text(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_agent_steps_run", "agent_steps", ["run_id", "step_no"])


def downgrade() -> None:
    op.drop_table("agent_steps")
    op.drop_table("agent_runs")
    op.drop_table("messages")
    op.drop_table("conversations")
    for t in ("run_status", "message_role"):
        op.execute(f"DROP TYPE {t}")
