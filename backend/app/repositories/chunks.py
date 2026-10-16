import uuid

from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.services.chunking import TextChunk


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
