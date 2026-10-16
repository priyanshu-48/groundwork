import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin


class User(IdMixin, Base):
    __tablename__ = "users"

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orgs.id"), index=True)
    # Always stored lower-cased (see schemas.auth), so the plain UNIQUE is case-insensitive.
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
