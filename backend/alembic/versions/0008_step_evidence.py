"""evidence rows stored with agent steps

Revision ID: 0008
Revises: 0007
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0008"
down_revision = "0007"


def upgrade() -> None:
    # Nullable and additive: old rows have no evidence, and rolling the app back ignores the column.
    op.add_column("agent_steps", sa.Column("evidence", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("agent_steps", "evidence")
