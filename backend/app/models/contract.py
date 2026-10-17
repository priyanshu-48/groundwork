import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin


class Contract(IdMixin, Base):
    """Structured facts extracted from one contract document. Flagged rows (needs_review) are kept
    as evidence but never reach the agent's SQL tool."""

    __tablename__ = "contracts"
    __table_args__ = (
        Index("ix_contracts_org_terms", "org_id", "payment_terms_days"),
        Index("ix_contracts_org_vendor", "org_id", "vendor"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orgs.id"))
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), unique=True
    )
    vendor: Mapped[str | None]
    payment_terms_days: Mapped[int | None]
    late_fee_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))  # per month
    termination_notice_days: Mapped[int | None]
    auto_renewal: Mapped[bool | None]
    liability_cap_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    liability_cap_currency: Mapped[str | None] = mapped_column(String(3))
    governing_law: Mapped[str | None]
    needs_review: Mapped[bool] = mapped_column(default=False)
    review_reason: Mapped[str | None] = mapped_column(Text)
