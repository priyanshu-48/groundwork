import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract import Contract
from app.repositories.util import like_pattern


async def delete_for_document(
    session: AsyncSession, org_id: uuid.UUID, document_id: uuid.UUID
) -> None:
    await session.execute(
        delete(Contract).where(Contract.org_id == org_id, Contract.document_id == document_id)
    )


async def query(
    session: AsyncSession,
    org_id: uuid.UUID,
    *,
    vendor: str | None,
    payment_terms_days: int | None,
    auto_renewal: bool | None,
    governing_law: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    """Contracts matching exact filters. Parameterised; the model supplies values only. Rows
    flagged for review are excluded, like flagged invoices."""
    conds: list[Any] = [Contract.org_id == org_id, Contract.needs_review.is_(False)]
    if vendor:
        conds.append(Contract.vendor.ilike(like_pattern(vendor), escape="\\"))
    if payment_terms_days is not None:
        conds.append(Contract.payment_terms_days == payment_terms_days)
    if auto_renewal is not None:
        conds.append(Contract.auto_renewal.is_(auto_renewal))
    if governing_law:
        conds.append(Contract.governing_law.ilike(like_pattern(governing_law), escape="\\"))
    stmt = (
        select(
            Contract.document_id,
            Contract.vendor,
            Contract.payment_terms_days,
            Contract.late_fee_percent,
            Contract.termination_notice_days,
            Contract.auto_renewal,
            Contract.liability_cap_amount,
            Contract.liability_cap_currency,
            Contract.governing_law,
        )
        .where(*conds)
        .order_by(Contract.vendor)
        .limit(limit)
    )
    return [dict(r._mapping) for r in (await session.execute(stmt)).all()]
