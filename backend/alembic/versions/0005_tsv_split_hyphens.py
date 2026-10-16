"""split word-internal hyphens before building the full-text vector

Revision ID: 0005
Revises: 0004
"""

from alembic import op

revision = "0005"
down_revision = "0004"

_OLD = "to_tsvector('english', content)"
_NEW = r"to_tsvector('english', regexp_replace(content, '(?<=\w)-(?=\w)', ' ', 'g'))"


def _rebuild(expr: str) -> None:
    # A generated column's expression cannot be altered in place, so drop and re-add it.
    op.execute("DROP INDEX IF EXISTS ix_chunks_tsv")
    op.execute("ALTER TABLE chunks DROP COLUMN tsv")
    op.execute(f"ALTER TABLE chunks ADD COLUMN tsv tsvector GENERATED ALWAYS AS ({expr}) STORED")
    op.execute("CREATE INDEX ix_chunks_tsv ON chunks USING gin (tsv)")


def upgrade() -> None:
    _rebuild(_NEW)


def downgrade() -> None:
    _rebuild(_OLD)
