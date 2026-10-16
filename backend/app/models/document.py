import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin


class DocKind(enum.StrEnum):
    invoice = "invoice"
    contract = "contract"
    other = "other"


class DocStatus(enum.StrEnum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    failed = "failed"


class Document(IdMixin, Base):
    __tablename__ = "documents"
    # Makes uploads idempotent per tenant; its index also serves "documents of this org" lookups.
    __table_args__ = (UniqueConstraint("org_id", "sha256"),)

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orgs.id"))
    filename: Mapped[str]
    s3_key: Mapped[str]
    sha256: Mapped[str] = mapped_column(String(64))
    kind: Mapped[DocKind] = mapped_column(Enum(DocKind, name="doc_kind"))
    status: Mapped[DocStatus] = mapped_column(
        Enum(DocStatus, name="doc_status"), default=DocStatus.pending
    )
    error: Mapped[str | None] = mapped_column(Text)
    page_count: Mapped[int | None]
