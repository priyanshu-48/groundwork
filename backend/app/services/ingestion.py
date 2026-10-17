"""Ingest one document: parse -> chunk -> embed -> (invoice) extract -> store.

Crash safety comes from the shape of this function: every slow or external step (S3, parsing,
Gemini) runs first, holding no database transaction; then ONE short transaction deletes the
document's old rows and writes the new ones. A worker killed at any point has either written
nothing or written everything, and a re-run replaces rather than appends."""

import asyncio
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocKind, DocStatus, Document
from app.models.invoice import Invoice
from app.repositories import chunks as chunks_repo
from app.repositories import invoices as invoices_repo
from app.services.chunking import chunk_pages
from app.services.extraction import InvoiceFields, review_reason
from app.services.parsing import PermanentError, extract_pages
from app.services.storage import get_bytes
from app.worker.deps import Deps


async def ingest_document(deps: Deps, document_id: uuid.UUID) -> None:
    s = deps.settings
    # The job payload only carries the document id (created server-side, not user input); the
    # org_id used for every write below comes from the document row itself.
    async with deps.maker.begin() as session:
        doc = (
            await session.execute(select(Document).where(Document.id == document_id))
        ).scalar_one_or_none()
        if doc is None:
            raise PermanentError(f"Document {document_id} no longer exists")
        doc.status, doc.error = DocStatus.processing, None
        org_id, key, kind = doc.org_id, doc.s3_key, doc.kind

    data = await get_bytes(deps.s3, deps.bucket, key)
    pages = await asyncio.to_thread(extract_pages, data, s.max_pages)
    chunks = chunk_pages(pages)
    if len(chunks) > s.max_chunks:
        raise PermanentError(f"Document produces {len(chunks)} chunks, limit is {s.max_chunks}")
    vectors = await deps.embedder.embed([c.content for c in chunks], "document")

    fields: InvoiceFields | None = None
    if kind == DocKind.invoice and s.extraction_enabled:
        fields = await deps.extractor.extract("\n".join(pages))

    async with deps.maker.begin() as session:  # the only write: all or nothing
        await chunks_repo.replace_for_document(session, org_id, document_id, chunks, vectors)
        if fields is not None:
            await _store_invoice(session, org_id, document_id, fields)
        await session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(status=DocStatus.ready, page_count=len(pages))
        )


async def _store_invoice(
    session: AsyncSession, org_id: uuid.UUID, document_id: uuid.UUID, f: InvoiceFields
) -> None:
    """Replace this document's invoice row. Doubtful or duplicate extractions are kept but
    flagged, so aggregates (which skip flagged rows) never silently include bad numbers."""
    await invoices_repo.delete_for_document(session, org_id, document_id)
    reason = review_reason(f)
    if reason is None:
        assert f.vendor is not None and f.invoice_number is not None
        twin = await invoices_repo.find_trusted(session, org_id, f.vendor, f.invoice_number)
        if twin is not None:
            reason = f"duplicate of invoice {twin.id} (same vendor and number)"
    session.add(
        Invoice(
            org_id=org_id,
            document_id=document_id,
            vendor=f.vendor,
            invoice_number=f.invoice_number,
            issue_date=f.issue_date,
            due_date=f.due_date,
            currency=f.currency,
            subtotal=f.subtotal,
            tax=f.tax,
            total=f.total,
            needs_review=reason is not None,
            review_reason=reason,
        )
    )


async def store_invoice(
    session: AsyncSession, org_id: uuid.UUID, document_id: uuid.UUID, f: InvoiceFields
) -> None:
    """Public entry point (also used by the backfill); resolves _store_invoice at call time."""
    await _store_invoice(session, org_id, document_id, f)


async def mark_failed(deps: Deps, document_id: uuid.UUID, error: str) -> None:
    async with deps.maker.begin() as session:
        await session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(status=DocStatus.failed, error=error[:2000])
        )
