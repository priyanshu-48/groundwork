from sqlalchemy.orm import Mapped

from app.models.base import Base, IdMixin


class Org(IdMixin, Base):
    __tablename__ = "orgs"

    name: Mapped[str]
