import uuid
from typing import Any

import pymupdf
from sqlalchemy import text

from app.models.document import DocKind
from app.repositories import documents, users
from app.services.security import hash_password
from app.services.storage import put_pdf
from app.worker.deps import Deps


def words(n: int, prefix: str = "w") -> str:
    return " ".join(f"{prefix}{i}" for i in range(n))


def make_pdf(pages: list[str]) -> bytes:
    """A real PDF with one text page per entry (PyMuPDF can write them; no extra dependency)."""
    doc = pymupdf.open()
    for body in pages:
        page = doc.new_page()
        rc = page.insert_textbox(pymupdf.Rect(36, 36, 559, 806), body, fontsize=7)
        assert rc >= 0, "test page text did not fit"
    return bytes(doc.tobytes())


def invoice_text(
    vendor: str = "Acme Corp",
    number: str = "INV-1",
    subtotal: str = "100.00",
    tax: str = "10.00",
    total: str = "110.00",
    currency: str = "USD",
    filler: str = "",
) -> str:
    return (
        f"Vendor: {vendor}\nInvoice #: {number}\nIssue Date: 2025-03-05\nDue Date: 2025-04-19\n"
        f"Currency: {currency}\nSubtotal: {subtotal}\nTax: {tax}\nTotal: {total}\n{filler}"
    )


async def new_org(deps: Deps) -> uuid.UUID:
    async with deps.maker.begin() as s:
        user = await users.create_org_with_user(
            s, "Test Org", f"{uuid.uuid4().hex}@example.com", hash_password("x" * 12)
        )
        return user.org_id


async def seed(
    deps: Deps, org_id: uuid.UUID, pdf: bytes, kind: str = "contract", filename: str = "t.pdf"
) -> uuid.UUID:
    """What POST /documents does, minus HTTP: S3 object + document row + ingest job."""
    import hashlib

    sha = hashlib.sha256(pdf).hexdigest()
    key = f"orgs/{org_id}/docs/{sha}.pdf"
    await put_pdf(deps.s3, deps.bucket, key, pdf)
    async with deps.maker.begin() as s:
        doc = await documents.create_with_job(s, org_id, filename, key, sha, DocKind(kind))
        return doc.id


async def scalar(deps: Deps, sql: str, **params: Any) -> Any:
    async with deps.maker() as s:
        return (await s.execute(text(sql), params)).scalar()


async def rows(deps: Deps, sql: str, **params: Any) -> list[Any]:
    async with deps.maker() as s:
        return list((await s.execute(text(sql), params)).mappings().all())


async def make_due(deps: Deps) -> None:
    async with deps.maker.begin() as s:
        await s.execute(text("UPDATE jobs SET run_after = now() WHERE status = 'queued'"))


async def ingest_corpus(deps: Deps, org_id: uuid.UUID, gt: dict[str, Any], out: Any) -> None:
    """Upload every generated PDF under its real filename, then run the worker until idle."""
    from app.worker.runner import process_one

    for v in gt["vendors"]:
        name = v["contract"]["filename"]
        await seed(deps, org_id, (out / "contracts" / name).read_bytes(), "contract", name)
    for inv in gt["invoices"]:
        name = inv["filename"]
        await seed(deps, org_id, (out / "invoices" / name).read_bytes(), "invoice", name)
    while await process_one(deps, "w"):
        pass
