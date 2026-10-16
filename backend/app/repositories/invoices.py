import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice


async def delete_for_document(
    session: AsyncSession, org_id: uuid.UUID, document_id: uuid.UUID
) -> None:
    await session.execute(
        delete(Invoice).where(Invoice.org_id == org_id, Invoice.document_id == document_id)
    )


async def find_trusted(
    session: AsyncSession, org_id: uuid.UUID, vendor: str, invoice_number: str
) -> Invoice | None:
    stmt = select(Invoice).where(
        Invoice.org_id == org_id,
        Invoice.vendor == vendor,
        Invoice.invoice_number == invoice_number,
        Invoice.needs_review.is_(False),
    )
    return (await session.execute(stmt)).scalar_one_or_none()
