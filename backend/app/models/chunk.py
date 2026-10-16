import uuid
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin


class Chunk(IdMixin, Base):
    __tablename__ = "chunks"
    __table_args__ = (
        Index("ix_chunks_org_document", "org_id", "document_id"),
        Index(
            "ix_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("ix_chunks_tsv", "tsv", postgresql_using="gin"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orgs.id"))
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    ord: Mapped[int]
    page: Mapped[int]
    content: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int]
    embedding: Mapped[Any] = mapped_column(Vector(768))
    tsv: Mapped[Any] = mapped_column(
        TSVECTOR,
        Computed(
            r"to_tsvector('english', regexp_replace(content, '(?<=\w)-(?=\w)', ' ', 'g'))",
            persisted=True,
        ),
    )
