import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import delete, desc, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract import Contract
from app.models.invoice import Invoice
from app.repositories.util import like_pattern


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


# Vendors group case- and whitespace-insensitively: an extractor that writes "ACME Labs" on one
# invoice and "Acme Labs " on another must not split one vendor's total in two.
_vendor_key = func.lower(func.trim(Invoice.vendor))


def _conditions(
    org_id: uuid.UUID,
    vendors: list[str],
    date_from: date | None,
    date_to: date | None,
    payment_terms_days: int | None,
) -> list[Any]:
    """The one WHERE clause behind both an answer and the evidence shown with it: sharing it is
    what guarantees the evidence rows are exactly the rows that were counted."""
    conds: list[Any] = [Invoice.org_id == org_id, Invoice.needs_review.is_(False)]
    if vendors:
        conds.append(or_(*[Invoice.vendor.ilike(like_pattern(v), escape="\\") for v in vendors]))
    if payment_terms_days is not None:
        # EXISTS (not JOIN) so a vendor with two contract documents cannot double-count invoices
        conds.append(
            exists().where(
                Contract.org_id == Invoice.org_id,
                func.lower(func.trim(Contract.vendor)) == func.lower(func.trim(Invoice.vendor)),
                Contract.needs_review.is_(False),
                Contract.payment_terms_days == payment_terms_days,
            )
        )
    if date_from:
        conds.append(Invoice.issue_date >= date_from)
    if date_to:
        conds.append(Invoice.issue_date <= date_to)
    return conds


async def contributing(
    session: AsyncSession,
    org_id: uuid.UUID,
    *,
    vendors: list[str],
    date_from: date | None,
    date_to: date | None,
    payment_terms_days: int | None,
    limit: int,
) -> tuple[list[dict[str, Any]], dict[str, Decimal], int]:
    """The invoices behind an aggregate: (rows up to limit, per-currency totals over ALL matching
    rows, number of matching rows). Totals are computed in SQL, so they stay exact when the rows
    shown are cut."""
    conds = _conditions(org_id, vendors, date_from, date_to, payment_terms_days)
    sums = (
        await session.execute(
            select(Invoice.currency, func.sum(Invoice.total), func.count())
            .where(*conds)
            .group_by(Invoice.currency)
        )
    ).all()
    totals = {cur or "unknown": Decimal(total or 0) for cur, total, _ in sums}
    count = sum(n for _, _, n in sums)
    rows = (
        await session.execute(
            select(
                Invoice.document_id,
                Invoice.invoice_number,
                Invoice.vendor,
                Invoice.issue_date,
                Invoice.due_date,
                Invoice.currency,
                Invoice.total,
            )
            .where(*conds)
            .order_by(_vendor_key, Invoice.issue_date, Invoice.invoice_number)
            .limit(limit)
        )
    ).all()
    return [dict(r._mapping) for r in rows], totals, count


async def aggregate(
    session: AsyncSession,
    org_id: uuid.UUID,
    *,
    aggregate: str,
    vendors: list[str],
    date_from: date | None,
    date_to: date | None,
    group_by_vendor: bool,
    limit: int,
    payment_terms_days: int | None = None,
) -> list[dict[str, Any]]:
    """Parameterised invoice aggregates for the agent. The LLM chooses values, never SQL.

    Only rows that passed validation count (needs_review = false): a doubtful total must not
    leak into a sum. Sums are grouped by currency because adding EUR to USD is meaningless."""
    conds = _conditions(org_id, vendors, date_from, date_to, payment_terms_days)

    if aggregate == "list":
        stmt = (
            select(
                Invoice.document_id,
                Invoice.invoice_number,
                Invoice.vendor,
                Invoice.issue_date,
                Invoice.due_date,
                Invoice.currency,
                Invoice.total,
            )
            .where(*conds)
            .order_by(Invoice.issue_date, Invoice.invoice_number)
            .limit(limit)
        )
    elif aggregate == "sum":
        cols: list[Any] = [
            Invoice.currency,
            func.sum(Invoice.total).label("total"),
            func.count().label("invoice_count"),
        ]
        group: list[Any] = [Invoice.currency]
        if group_by_vendor:
            cols.insert(0, func.min(Invoice.vendor).label("vendor"))
            group.insert(0, _vendor_key)
        stmt = select(*cols).where(*conds).group_by(*group).order_by(desc("total")).limit(limit)
    elif aggregate == "count":
        cols = [func.count().label("invoice_count")]
        group = []
        if group_by_vendor:
            cols.insert(0, func.min(Invoice.vendor).label("vendor"))
            group.append(_vendor_key)
        stmt = select(*cols).where(*conds)
        if group:
            stmt = stmt.group_by(*group).order_by(desc("invoice_count")).limit(limit)
    else:
        raise ValueError(f"unknown aggregate {aggregate!r}")
    return [dict(r._mapping) for r in (await session.execute(stmt)).all()]
