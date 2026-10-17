import re
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


_IDENTIFIER = re.compile(r'(?<![\w"-])(\w+(?:-\w+)+)(?![\w"-])')
_INNER_HYPHEN = re.compile(r"(?<=\w)-(?=\w)")


def prepare_keyword_query(q: str) -> str:
    """Make hyphenated identifiers (invoice numbers, dates) match the same way on both sides.

    The default Postgres parser tokenizes 'V02-2025-0003' differently depending on the words around
    it ('-2025' parsed as a signed number, compound token sometimes kept, sometimes not), so exact
    IDs matched in some invoice layouts and not others. The tsv column splits word-internal hyphens
    into spaces (migration 0005); here the query gets the same treatment, with each identifier
    wrapped in quotes so it must match as an adjacent phrase: "v02 2025 0003"."""
    return _INNER_HYPHEN.sub(" ", _IDENTIFIER.sub(lambda m: f'"{m.group(1)}"', q))


def specific_terms(prepared: str) -> list[str]:
    """Query tokens that contain a digit (ids, dates, amounts). They are rare in a corpus, but
    ts_rank_cd has no IDF, so a chunk repeating a common word like 'invoice' would otherwise
    outrank the one chunk holding the exact identifier. Capped to keep the SQL small."""
    tokens = re.findall(r'"[^"]+"|[^\s"]+', prepared)
    return [t for t in tokens if any(c.isdigit() for c in t)][:6]


async def keyword_search(
    session: AsyncSession,
    org_id: uuid.UUID,
    query: str,
    kind: DocKind | None,
    limit: int,
) -> list[Hit]:
    """Full-text search over chunks.tsv (GIN index). websearch_to_tsquery safely parses free text
    but joins terms with AND, which finds nothing for a natural-language question when one word is
    absent from the page; swapping ' & ' for ' | ' gives OR semantics, and ts_rank_cd then ranks
    chunks matching more of the terms first (docs/decisions/0005)."""
    kind_filter = "AND d.kind = CAST(:kind AS doc_kind)" if kind is not None else ""
    prepared = prepare_keyword_query(query)
    specific = specific_terms(prepared)
    # One point per matched identifier-like term, then ts_rank_cd breaks ties (see specific_terms).
    boost = (
        " + ".join(
            f"(c.tsv @@ websearch_to_tsquery('english', :s{i}))::int" for i in range(len(specific))
        )
        or "CAST(0 AS int)"  # a bare 0 would be read as ORDER BY column position 0
    )
    stmt = text(f"""
        SELECT c.id, c.document_id, d.filename, c.page, c.content,
               ts_rank_cd(c.tsv, q.query) AS score
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        CROSS JOIN (
            SELECT replace(
                websearch_to_tsquery('english', :q)::text, ' & ', ' | '
            )::tsquery AS query
        ) q
        WHERE c.org_id = :org AND c.tsv @@ q.query {kind_filter}
        ORDER BY ({boost}) DESC, score DESC, c.id
        LIMIT :lim
    """)  # noqa: S608 - only a constant fragment is interpolated; user input is bound
    params: dict[str, object] = {"q": prepared, "org": org_id, "lim": limit}
    params |= {f"s{i}": t for i, t in enumerate(specific)}
    if kind is not None:
        params["kind"] = kind.value
    rows = (await session.execute(stmt, params)).all()
    return [Hit(r.id, r.document_id, r.filename, r.page, r.content, float(r.score)) for r in rows]


async def fetch_by_ids(
    session: AsyncSession, org_id: uuid.UUID, chunk_ids: list[uuid.UUID]
) -> list[Hit]:
    """Full chunks by id, scoped to the org: an id from another tenant simply is not found."""
    stmt = (
        select(Chunk.id, Chunk.document_id, Document.filename, Chunk.page, Chunk.content)
        .join(Document, Document.id == Chunk.document_id)
        .where(Chunk.org_id == org_id, Chunk.id.in_(chunk_ids))
    )
    return [
        Hit(r.id, r.document_id, r.filename, r.page, r.content, 0.0)
        for r in (await session.execute(stmt)).all()
    ]


async def first_chunks(
    session: AsyncSession, org_id: uuid.UUID, document_ids: list[uuid.UUID]
) -> dict[uuid.UUID, Hit]:
    """The opening chunk of each document (an invoice is one page, so this is its whole text)."""
    stmt = (
        select(Chunk.id, Chunk.document_id, Document.filename, Chunk.page, Chunk.content)
        .join(Document, Document.id == Chunk.document_id)
        .where(Chunk.org_id == org_id, Chunk.document_id.in_(document_ids), Chunk.ord == 0)
    )
    rows = (await session.execute(stmt)).all()
    return {
        r.document_id: Hit(r.id, r.document_id, r.filename, r.page, r.content, 0.0) for r in rows
    }
