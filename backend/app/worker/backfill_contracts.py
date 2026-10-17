"""Extract structured contract facts for contract documents that have none, 3 per LLM request.

Mirror of backfill_invoices (see there for why batching matters on a free tier). Contracts are
longer than invoices, so batches are smaller. Safe to re-run: documents that already have a
contract row are skipped. An org-agnostic operator tool, like the invoice backfill.

Run (from backend/):  uv run python -m app.worker.backfill_contracts [--batch 3] [--retry-flagged]
"""

import argparse
import asyncio
import logging
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import exists, or_, select

from app.config import get_settings
from app.models.chunk import Chunk
from app.models.contract import Contract
from app.models.document import DocKind, DocStatus, Document
from app.services.contract_extraction import review_contract
from app.services.ingestion import store_contract
from app.worker.deps import Deps, build_deps

log = logging.getLogger(__name__)


@dataclass
class BackfillResult:
    documents: int = 0
    flagged: int = 0
    llm_calls: int = 0


async def _next_batch(
    deps: Deps, size: int, retry_flagged: bool, seen: set[uuid.UUID]
) -> list[tuple[uuid.UUID, uuid.UUID, str]]:
    missing = ~exists().where(Contract.document_id == Document.id)
    flagged = exists().where(Contract.document_id == Document.id, Contract.needs_review.is_(True))
    conds: list[Any] = [
        Document.kind == DocKind.contract,
        Document.status == DocStatus.ready,
        or_(missing, flagged) if retry_flagged else missing,
    ]
    if seen:
        conds.append(Document.id.not_in(seen))
    async with deps.maker() as session:
        docs = (
            await session.execute(
                select(Document.id, Document.org_id)
                .where(*conds)
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


async def backfill(
    deps: Deps, batch_size: int = 3, limit: int | None = None, retry_flagged: bool = False
) -> BackfillResult:
    result = BackfillResult()
    seen: set[uuid.UUID] = set()
    while limit is None or result.documents < limit:
        size = batch_size if limit is None else min(batch_size, limit - result.documents)
        batch = await _next_batch(deps, size, retry_flagged, seen)
        if not batch:
            break
        seen.update(doc_id for doc_id, _, _ in batch)
        fields = await deps.extractor.extract_contracts_many([t for _, _, t in batch])
        result.llm_calls += 1
        async with deps.maker.begin() as session:  # one transaction per batch
            for (doc_id, org_id, _), f in zip(batch, fields, strict=True):
                await store_contract(session, org_id, doc_id, f)
        result.documents += len(batch)
        result.flagged += sum(1 for f in fields if review_contract(f) is not None)
        log.info("backfilled %d contracts (%d calls so far)", result.documents, result.llm_calls)
    return result


async def _main(args: argparse.Namespace) -> int:
    deps, engine = build_deps(get_settings())
    try:
        result = await backfill(deps, args.batch, args.limit, args.retry_flagged)
    except Exception as e:  # quota or outage: progress so far is already committed
        print(f"stopped early: {type(e).__name__}: {e}")
        return 1
    finally:
        await engine.dispose()
    print(
        f"extracted {result.documents} contracts in {result.llm_calls} LLM calls; "
        f"{result.flagged} flagged for review"
    )
    return 0


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--batch", type=int, default=3)
    ap.add_argument("--limit", type=int, default=None, help="stop after this many documents")
    ap.add_argument("--retry-flagged", action="store_true")
    raise SystemExit(asyncio.run(_main(ap.parse_args())))


if __name__ == "__main__":
    main()
