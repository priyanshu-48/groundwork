import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocKind, Document
from app.worker import queue


async def get_by_sha(session: AsyncSession, org_id: uuid.UUID, sha256: str) -> Document | None:
    stmt = select(Document).where(Document.org_id == org_id, Document.sha256 == sha256)
    return (await session.execute(stmt)).scalar_one_or_none()


async def create_with_job(
    session: AsyncSession,
    org_id: uuid.UUID,
    filename: str,
    s3_key: str,
    sha256: str,
    kind: DocKind,
) -> Document:
    """Document row and its ingest job are flushed in the caller's single transaction, so a crash
    can never leave a document without a job (or the reverse). A duplicate (org_id, sha256) raises
    IntegrityError at flush/commit."""
    doc = Document(org_id=org_id, filename=filename, s3_key=s3_key, sha256=sha256, kind=kind)
    session.add(doc)
    await session.flush()
    await queue.enqueue(
        session, "ingest", {"document_id": str(doc.id)}, idempotency_key=f"ingest:{doc.id}"
    )
    return doc


async def list_for_org(
    session: AsyncSession, org_id: uuid.UUID, limit: int, offset: int = 0
) -> Sequence[Document]:
    stmt = (
        select(Document)
        .where(Document.org_id == org_id)
        .order_by(Document.created_at.desc(), Document.id)
        .limit(limit)
        .offset(offset)
    )
    return (await session.execute(stmt)).scalars().all()


async def filenames(
    session: AsyncSession, org_id: uuid.UUID, document_ids: list[uuid.UUID]
) -> dict[uuid.UUID, str]:
    """File names of documents in one org (ids from other orgs simply do not appear)."""
    if not document_ids:
        return {}
    stmt = select(Document.id, Document.filename).where(
        Document.org_id == org_id, Document.id.in_(document_ids)
    )
    return {r.id: r.filename for r in (await session.execute(stmt)).all()}
