"""Extract invoice rows for documents that have none, many invoices per LLM request.

Why batches: free-tier generate_content quotas are tiny (tens of requests a day), and one
invoice is one page. Ten per request turns 300 calls into 30. Also the recovery path for documents
ingested while extraction was off. Safe to re-run: documents that already have a row are skipped.

Run (from backend/):  uv run python -m app.worker.backfill_invoices [--batch 10] [--limit N]
"""

import argparse
import asyncio
import logging
import uuid
from dataclasses import dataclass

from sqlalchemy import exists, select

from app.config import get_settings
from app.models.chunk import Chunk
from app.models.document import DocKind, DocStatus, Document
from app.models.invoice import Invoice
from app.services.extraction import review_reason
from app.services.ingestion import store_invoice
from app.worker.deps import Deps, build_deps

log = logging.getLogger(__name__)


@dataclass
class BackfillResult:
    documents: int = 0
    flagged: int = 0
    llm_calls: int = 0


async def _next_batch(deps: Deps, size: int) -> list[tuple[uuid.UUID, uuid.UUID, str]]:
    """(document_id, org_id, full text) for invoice documents still without an invoice row."""
    async with deps.maker() as session:
        docs = (
            await session.execute(
                select(Document.id, Document.org_id)
                .where(
                    Document.kind == DocKind.invoice,
                    Document.status == DocStatus.ready,
                    ~exists().where(Invoice.document_id == Document.id),
                )
                .order_by(Document.created_at, Document.id)
                .limit(size)
            )
        ).all()
        if not docs:
            return []
        rows = (
            await session.execute(
                select(Chunk.document_id, Chunk.content)
                .where(Chunk.document_id.in_([d.id for d in docs]))
                .order_by(Chunk.document_id, Chunk.ord)
            )
        ).all()
    text: dict[uuid.UUID, list[str]] = {}
    for r in rows:
        text.setdefault(r.document_id, []).append(r.content)
    return [(d.id, d.org_id, "\n".join(text.get(d.id, []))) for d in docs]


async def backfill(deps: Deps, batch_size: int = 10, limit: int | None = None) -> BackfillResult:
    result = BackfillResult()
    while limit is None or result.documents < limit:
        size = batch_size if limit is None else min(batch_size, limit - result.documents)
        batch = await _next_batch(deps, size)
        if not batch:
            break
        fields = await deps.extractor.extract_many([t for _, _, t in batch])
        result.llm_calls += 1
        async with deps.maker.begin() as session:  # one transaction per batch
            for (doc_id, org_id, _), f in zip(batch, fields, strict=True):
                await store_invoice(session, org_id, doc_id, f)
        result.documents += len(batch)
        result.flagged += sum(1 for f in fields if review_reason(f) is not None)
        log.info("backfilled %d invoices (%d calls so far)", result.documents, result.llm_calls)
    return result


async def _main(args: argparse.Namespace) -> int:
    deps, engine = build_deps(get_settings())
    try:
        result = await backfill(deps, args.batch, args.limit)
    except Exception as e:  # quota or outage: progress so far is already committed
        print(f"stopped early: {type(e).__name__}: {e}")
        return 1
    finally:
        await engine.dispose()
    print(
        f"extracted {result.documents} invoices in {result.llm_calls} LLM calls; "
        f"{result.flagged} flagged for review"
    )
    return 0


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--limit", type=int, default=None, help="stop after this many documents")
    raise SystemExit(asyncio.run(_main(ap.parse_args())))


if __name__ == "__main__":
    main()
