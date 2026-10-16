import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocKind
from app.repositories import chunks as chunks_repo
from app.repositories.chunks import Hit
from app.services.embeddings import EmbeddingProvider


async def search_documents(
    session: AsyncSession,
    embedder: EmbeddingProvider,
    org_id: uuid.UUID,
    query: str,
    *,
    kind: DocKind | None = None,
    top_k: int = 5,
) -> list[Hit]:
    """Vector-only retrieval (the baseline). The query is embedded with the query task type, which
    Gemini optimizes differently from document text. Hybrid search and reranking come in M5."""
    (vector,) = await embedder.embed([query], "query")
    return await chunks_repo.vector_search(session, org_id, vector, kind, top_k)


__all__ = ["Hit", "search_documents"]
