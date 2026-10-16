"""Run the retrieval eval against an ingested corpus and record the numbers.

Run (from backend/, stack up and corpus loaded):
    uv run python ../evals/run_evals.py --modes vector --label baseline
"""

import argparse
import asyncio
import json
import subprocess
import sys
import uuid
from datetime import date
from pathlib import Path
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "backend"):  # make `app.*` and `evals.*` importable when run as a script
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.services.embeddings import EmbeddingProvider, FakeEmbeddingProvider  # noqa: E402
from app.services.retrieval import search_documents  # noqa: E402
from app.worker.deps import build_deps  # noqa: E402
from evals.metrics import mrr_at_k, percentile, recall_at_k  # noqa: E402

MODES = ["vector"]  # hybrid and hybrid_rerank arrive in M5

DOCS_TEMPLATE = """# Evaluation results

Retrieval is scored on the 35 contract-lookup questions of the synthetic eval set
(`evals/questions.jsonl`, built from `evals/ground_truth.json`, seed 42).

- **Hit:** a retrieved chunk from the gold contract **and** the gold page.
- **Recall@5:** share of questions with a hit in the top 5. **MRR@10:** mean of 1/rank of the
  first hit within the top 10 (0 if none). **Doc recall@5:** same as recall@5 but only the
  contract must match (looser).
- Latency is the whole search call: query embedding plus the SQL.
- Numbers from the fake embedder are never written here; they only check the harness.

| Date | Git SHA | Label | Mode | Embedder | Recall@5 | MRR@10 | Doc recall@5 | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|---|
<!-- evals:end -->
"""


async def evaluate(
    maker: async_sessionmaker[AsyncSession],
    embedder: EmbeddingProvider,
    org_id: uuid.UUID,
    questions: list[dict[str, Any]],
    mode: str = "vector",
) -> dict[str, Any]:
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; available: {MODES}")
    lookups = [q for q in questions if q["type"] == "contract_lookup"]
    rows: list[dict[str, Any]] = []
    for q in lookups:
        t0 = perf_counter()
        async with maker() as session:
            hits = await search_documents(session, embedder, org_id, q["question"], top_k=10)
        ms = (perf_counter() - t0) * 1000
        gold = q["gold"]
        page_rank = next(
            (
                i
                for i, h in enumerate(hits, 1)
                if h.filename == gold["document"] and h.page == gold["page"]
            ),
            None,
        )
        doc_rank = next((i for i, h in enumerate(hits, 1) if h.filename == gold["document"]), None)
        rows.append(
            {
                "id": q["id"],
                "fact": q["fact"],
                "page_rank": page_rank,
                "doc_rank": doc_rank,
                "ms": ms,
            }
        )
    ranks = [r["page_rank"] for r in rows]
    lat = [r["ms"] for r in rows] or [0.0]
    by_fact: dict[str, dict[str, Any]] = {}
    for fact in sorted({r["fact"] for r in rows}):
        fr = [r["page_rank"] for r in rows if r["fact"] == fact]
        by_fact[fact] = {"n": len(fr), "recall@5": recall_at_k(fr, 5)}
    return {
        "mode": mode,
        "n": len(rows),
        "recall@5": recall_at_k(ranks, 5),
        "mrr@10": mrr_at_k(ranks, 10),
        "doc_recall@5": recall_at_k([r["doc_rank"] for r in rows], 5),
        "p50_ms": percentile(lat, 50),
        "p95_ms": percentile(lat, 95),
        "by_fact": by_fact,
        "rows": rows,
    }


def append_docs_row(docs: Path, row: dict[str, Any], allow_fake: bool) -> None:
    """Add one result row to docs/evals.md. Fake-embedder numbers are refused by default so a
    harness check can never end up as a headline number."""
    if row["embedder"] == "fake" and not allow_fake:
        raise ValueError("refusing to record fake-embedder numbers (use --allow-fake to override)")
    if not docs.exists():
        docs.write_text(DOCS_TEMPLATE, encoding="utf8")
    embedder = "fake (harness check only)" if row["embedder"] == "fake" else row["embedder"]
    line = (
        f"| {row['date']} | {row['git_sha']} | {row['label']} | {row['mode']} | {embedder} "
        f"| {row['recall@5'] * 100:.1f}% | {row['mrr@10']:.3f} | {row['doc_recall@5'] * 100:.1f}% "
        f"| {row['p50_ms']:.0f} | {row['p95_ms']:.0f} |\n"
    )
    content = docs.read_text(encoding="utf8")
    docs.write_text(
        content.replace("<!-- evals:end -->", line + "<!-- evals:end -->", 1), encoding="utf8"
    )


def _git_sha() -> str:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=ROOT
        ).stdout
        return sha + ("-dirty" if dirty.strip() else "")
    except Exception:
        return "unknown"


def eval_settings() -> Any:
    """The min-interval throttle exists for bulk ingestion. Left on, every query would wait 2 s and
    the latency numbers would just measure the throttle (35 queries is far below any quota)."""
    return get_settings().model_copy(update={"embedding_min_interval_s": 0.0})


async def _main(args: argparse.Namespace) -> None:
    s = eval_settings()
    deps, engine = build_deps(s)
    try:
        async with deps.maker() as session:
            org_id = (
                await session.execute(
                    text("SELECT org_id FROM users WHERE email = :e"), {"e": args.email}
                )
            ).scalar_one_or_none()
        if org_id is None:
            raise SystemExit(f"no user {args.email}; run load_corpus.py first")
        questions = [
            json.loads(line)
            for line in args.questions.read_text(encoding="utf8").splitlines()
            if line
        ]
        fake = isinstance(deps.embedder, FakeEmbeddingProvider)
        out: dict[str, Any] = {
            "date": date.today().isoformat(),
            "git_sha": _git_sha(),
            "label": args.label,
            "embedder": "fake" if fake else "gemini",
            "embedding_model": None if fake else s.embedding_model,
            "modes": {},
        }
        for mode in args.modes:
            res = await evaluate(deps.maker, deps.embedder, org_id, questions, mode)
            out["modes"][mode] = res
            print(
                f"{mode}: recall@5={res['recall@5']:.1%} mrr@10={res['mrr@10']:.3f} "
                f"doc_recall@5={res['doc_recall@5']:.1%} p50={res['p50_ms']:.0f}ms p95={res['p95_ms']:.0f}ms"
            )
            for fact, v in res["by_fact"].items():
                print(f"    {fact:<20} n={v['n']:<3} recall@5={v['recall@5']:.0%}")
            if fake and not args.allow_fake:
                print("    (fake embedder: docs/evals.md not updated)")
            else:
                append_docs_row(
                    args.docs,
                    {
                        **out,
                        **{
                            k: res[k]
                            for k in ("recall@5", "mrr@10", "doc_recall@5", "p50_ms", "p95_ms")
                        },
                        "mode": mode,
                    },
                    args.allow_fake,
                )
        suffix = f"_{args.label}" if args.label else ""
        path = args.results / f"{out['date']}_{out['git_sha']}{suffix}.json"
        args.results.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf8")
        print(f"wrote {path}")
    finally:
        await engine.dispose()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--modes", nargs="+", default=["vector"], choices=MODES)
    ap.add_argument("--label", default="")
    ap.add_argument("--email", default="eval@example.com")
    ap.add_argument("--questions", type=Path, default=ROOT / "evals" / "questions.jsonl")
    ap.add_argument("--results", type=Path, default=ROOT / "evals" / "results")
    ap.add_argument("--docs", type=Path, default=ROOT / "docs" / "evals.md")
    ap.add_argument("--allow-fake", action="store_true")
    asyncio.run(_main(ap.parse_args()))


if __name__ == "__main__":
    main()
