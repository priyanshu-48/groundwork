from typing import Any

import pymupdf


class PermanentError(Exception):
    """Retrying cannot help (corrupt file, no text, over limits): fail the job immediately."""


def extract_pages(data: bytes, max_pages: int) -> list[str]:
    """Text of each page, in order. CPU-bound: call via asyncio.to_thread."""
    try:
        doc: Any = pymupdf.open(stream=data, filetype="pdf")  # type: ignore[no-untyped-call]  # PyMuPDF has no type hints
    except Exception as e:
        raise PermanentError(f"Unreadable PDF: {e}") from e
    with doc:
        if doc.needs_pass:
            raise PermanentError("PDF is password-protected")
        if doc.page_count > max_pages:
            raise PermanentError(f"PDF has {doc.page_count} pages, limit is {max_pages}")
        try:
            pages = [page.get_text() for page in doc]
        except Exception as e:
            raise PermanentError(f"Unreadable PDF: {e}") from e
    if not any(p.strip() for p in pages):
        raise PermanentError("PDF has no extractable text (scanned images are not supported)")
    return pages
