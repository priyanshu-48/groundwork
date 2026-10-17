import hashlib
import posixpath
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user, get_session
from app.config import get_settings
from app.models.document import DocKind
from app.repositories import documents
from app.schemas.documents import DocumentOut
from app.services.security import Principal
from app.services.storage import put_pdf

router = APIRouter(prefix="/documents", tags=["documents"])
_CHUNK = 1 << 20


async def _read_pdf(file: UploadFile, limit: int) -> bytes:
    """Read at most limit bytes (never buffer an attacker-sized body) and check the PDF magic."""
    buf = bytearray()
    while chunk := await file.read(_CHUNK):
        buf += chunk
        if len(buf) > limit:
            raise HTTPException(413, f"File exceeds {limit // (1024 * 1024)} MB limit")
    if not buf.startswith(b"%PDF-"):
        raise HTTPException(415, "Only PDF files are accepted")
    return bytes(buf)


@router.post("", response_model=DocumentOut, status_code=201)
async def upload(
    request: Request,
    response: Response,
    file: UploadFile,
    kind: Annotated[DocKind, Form()] = DocKind.other,
    p: Principal = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> object:
    if p.demo:
        raise HTTPException(403, "The demo workspace is read-only")
    s = get_settings()
    data = await _read_pdf(file, s.max_upload_bytes)
    sha = hashlib.sha256(data).hexdigest()

    if existing := await documents.get_by_sha(session, p.org_id, sha):
        response.status_code = 200
        return existing

    # S3 first, DB second: the key is deterministic, so a retry after a failed commit simply
    # overwrites the same object (no orphans pile up). The reverse order could commit a document
    # row that points at a missing file.
    key = f"orgs/{p.org_id}/docs/{sha}.pdf"
    await put_pdf(request.app.state.s3, s.s3_bucket, key, data)
    name = posixpath.basename((file.filename or "upload.pdf").replace("\\", "/"))[:255]
    try:
        doc = await documents.create_with_job(session, p.org_id, name, key, sha, kind)
        await session.commit()
    except IntegrityError:
        # Lost a race with a concurrent identical upload: return the winner's document.
        await session.rollback()
        winner = await documents.get_by_sha(session, p.org_id, sha)
        if winner is None:
            raise
        response.status_code = 200
        return winner
    return doc


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    p: Principal = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> object:
    return await documents.list_for_org(session, p.org_id, limit, offset)
