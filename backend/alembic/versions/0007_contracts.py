"""structured contract facts

Revision ID: 0007
Revises: 0006
"""

import sqlalchemy as sa

from alembic import op

revision = "0007"
down_revision = "0006"


def upgrade() -> None:
    op.create_table(
        "contracts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("org_id", sa.Uuid(), sa.ForeignKey("orgs.id"), nullable=False),
        sa.Column(
            "document_id",
            sa.Uuid(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("vendor", sa.String()),
        sa.Column("payment_terms_days", sa.Integer()),
        sa.Column("late_fee_percent", sa.Numeric(5, 2)),
        sa.Column("termination_notice_days", sa.Integer()),
        sa.Column("auto_renewal", sa.Boolean()),
        sa.Column("liability_cap_amount", sa.Numeric(14, 2)),
        sa.Column("liability_cap_currency", sa.String(3)),
        sa.Column("governing_law", sa.String()),
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("review_reason", sa.Text()),
    )
    op.create_index("ix_contracts_org_terms", "contracts", ["org_id", "payment_terms_days"])
    op.create_index("ix_contracts_org_vendor", "contracts", ["org_id", "vendor"])


def downgrade() -> None:
    op.drop_table("contracts")
