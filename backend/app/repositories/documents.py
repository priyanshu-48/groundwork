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


async def list_for_org(session: AsyncSession, org_id: uuid.UUID, limit: int) -> Sequence[Document]:
    stmt = (
        select(Document)
        .where(Document.org_id == org_id)
        .order_by(Document.created_at.desc())
        .limit(limit)
    )
    return (await session.execute(stmt)).scalars().all()
