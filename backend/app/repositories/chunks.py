import uuid
from dataclasses import dataclass

from sqlalchemy import delete, insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.document import DocKind, Document
from app.services.chunking import TextChunk


@dataclass(frozen=True)
class Hit:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    page: int
    content: str
    score: float  # cosine similarity, higher is better


async def replace_for_document(
    session: AsyncSession,
    org_id: uuid.UUID,
    document_id: uuid.UUID,
    chunks: list[TextChunk],
    vectors: list[list[float]],
) -> None:
    """Delete-then-insert in the caller's transaction: a re-run replaces the document's chunks
    instead of appending, which is what makes ingestion safe to repeat after a crash."""
    await session.execute(
        delete(Chunk).where(Chunk.org_id == org_id, Chunk.document_id == document_id)
    )
    if not chunks:
        return
    await session.execute(
        insert(Chunk),
        [
            {
                "org_id": org_id,
                "document_id": document_id,
                "ord": c.ord,
                "page": c.page,
                "content": c.content,
                "token_count": c.token_count,
                "embedding": v,
            }
            for c, v in zip(chunks, vectors, strict=True)
        ],
    )


async def vector_search(
    session: AsyncSession,
    org_id: uuid.UUID,
    query_vec: list[float],
    kind: DocKind | None,
    limit: int,
) -> list[Hit]:
    """Nearest chunks by cosine distance. The org filter is applied inside the same query as the
    ANN search; iterative_scan makes HNSW keep scanning until enough rows survive that filter
    (without it a selective filter can return fewer than `limit` rows)."""
    await session.execute(text("SET LOCAL hnsw.iterative_scan = relaxed_order"))
    dist = Chunk.embedding.cosine_distance(query_vec).label("distance")
    stmt = (
        select(Chunk.id, Chunk.document_id, Document.filename, Chunk.page, Chunk.content, dist)
        .join(Document, Document.id == Chunk.document_id)
        .where(Chunk.org_id == org_id)
        .order_by(dist)
        .limit(limit)
    )
    if kind is not None:
        stmt = stmt.where(Document.kind == kind)
    rows = list((await session.execute(stmt)).all())
    # relaxed_order may return rows slightly out of order; sorting the final few is cheap.
    rows.sort(key=lambda r: r.distance)
    return [Hit(r.id, r.document_id, r.filename, r.page, r.content, 1 - r.distance) for r in rows]
