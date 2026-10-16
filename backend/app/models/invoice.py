import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin


class Invoice(IdMixin, Base):
    __tablename__ = "invoices"
    __table_args__ = (
        # Only trusted rows must be unique: a duplicate or doubtful extraction is stored flagged
        # instead of failing the whole ingest (docs/decisions/0003).
        Index(
            "uq_invoices_org_vendor_number",
            "org_id",
            "vendor",
            "invoice_number",
            unique=True,
            postgresql_where=text("NOT needs_review"),
        ),
        Index("ix_invoices_document_id", "document_id"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orgs.id"))
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    vendor: Mapped[str | None]
    invoice_number: Mapped[str | None]
    issue_date: Mapped[date | None]
    due_date: Mapped[date | None]
    currency: Mapped[str | None] = mapped_column(String(3))
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    tax: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    needs_review: Mapped[bool] = mapped_column(default=False)
    review_reason: Mapped[str | None] = mapped_column(Text)
