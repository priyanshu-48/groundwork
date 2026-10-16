import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocKind, DocStatus


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    sha256: str
    kind: DocKind
    status: DocStatus
    error: str | None
    page_count: int | None
    created_at: datetime
