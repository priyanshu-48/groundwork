import uuid
from datetime import date
from typing import Any

from sqlalchemy import delete, desc, func, or_, select
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


def _like(v: str) -> str:
    """Contains-match pattern with LIKE wildcards in the user's text neutralised."""
    esc = "\\"
    escaped = v.strip().replace(esc, esc * 2).replace("%", esc + "%").replace("_", esc + "_")
    return f"%{escaped}%"


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
) -> list[dict[str, Any]]:
    """Parameterised invoice aggregates for the agent. The LLM chooses values, never SQL.

    Only rows that passed validation count (needs_review = false): a doubtful total must not
    leak into a sum. Sums are grouped by currency because adding EUR to USD is meaningless."""
    conds: list[Any] = [Invoice.org_id == org_id, Invoice.needs_review.is_(False)]
    if vendors:
        conds.append(or_(*[Invoice.vendor.ilike(_like(v), escape="\\") for v in vendors]))
    if date_from:
        conds.append(Invoice.issue_date >= date_from)
    if date_to:
        conds.append(Invoice.issue_date <= date_to)

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
            cols.insert(0, Invoice.vendor)
            group.insert(0, Invoice.vendor)
        stmt = select(*cols).where(*conds).group_by(*group).order_by(desc("total")).limit(limit)
    elif aggregate == "count":
        cols = [func.count().label("invoice_count")]
        group = []
        if group_by_vendor:
            cols.insert(0, Invoice.vendor)
            group.append(Invoice.vendor)
        stmt = select(*cols).where(*conds)
        if group:
            stmt = stmt.group_by(*group).order_by(desc("invoice_count")).limit(limit)
    else:
        raise ValueError(f"unknown aggregate {aggregate!r}")
    return [dict(r._mapping) for r in (await session.execute(stmt)).all()]
