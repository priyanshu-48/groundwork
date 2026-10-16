"""Run the retrieval eval against an ingested corpus and record the numbers.

Run (from backend/, stack up and corpus loaded, GEMINI_API_KEY in the environment):
    uv run python ../evals/run_evals.py --sets easy hard --modes vector hybrid hybrid_rerank --label m5

Queries are embedded once, up front, and the vectors reused for every mode. That keeps the Gemini
round trip (identical for all modes) out of the per-mode "search ms", which then measures only
database + fusion + rerank.
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
from typing import Any, get_args

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "backend"):  # make `app.*` and `evals.*` importable when run as a script
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.services.embeddings import EmbeddingProvider, FakeEmbeddingProvider, Task  # noqa: E402
from app.services.rerank import FakeReranker, FlashRankReranker, Reranker  # noqa: E402
from app.services.retrieval import Mode, search_documents  # noqa: E402
from app.worker.deps import build_deps  # noqa: E402
from evals.metrics import mrr_at_k, percentile, recall_at_k  # noqa: E402

MODES = list(get_args(Mode))
SETS = {"easy": "questions.jsonl", "hard": "retrieval_hard.jsonl"}

DOCS_TEMPLATE = """# Evaluation results

Retrieval is scored on questions with a known gold **document and page** from the synthetic corpus
(`evals/ground_truth.json`, seed 42):

- **easy** (35 questions, `evals/questions.jsonl`): contract lookups that name the vendor and echo the clause wording.
- **hard** (60 questions, `evals/retrieval_hard.jsonl`): 20 exact invoice-number lookups, 16 invoice
  lookups by vendor + date + total, and 24 paraphrased contract questions that avoid the clause's words.

- **Hit:** a retrieved chunk from the gold document **and** the gold page.
- **Recall@5:** share of questions with a hit in the top 5. **MRR@10:** mean of 1/rank of the first
  hit within the top 10 (0 if none). **Doc recall@5:** same as recall@5 but only the document must match.
- **Search ms:** database + fusion + rerank, with the query already embedded (the Gemini round trip,
  about the same for every mode, is excluded). Rows from before M5 include that round trip.
- Numbers from a fake embedder or fake reranker are never written here; they only check the harness.

| Date | Git SHA | Label | Set | Mode | Embedder | Reranker | Recall@5 | MRR@10 | Doc recall@5 | search p50 ms | search p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
<!-- evals:end -->
"""


class PrecomputedEmbedder:
    """Returns vectors computed earlier, so a search's timing excludes the embedding API call."""

    def __init__(self, vectors: dict[str, list[float]]) -> None:
        self._vectors = vectors

    async def embed(self, texts: list[str], task: Task) -> list[list[float]]:
        return [self._vectors[t] for t in texts]


async def precompute(
    embedder: EmbeddingProvider, texts: list[str], cache: Path | None = None, cache_key: str = ""
) -> tuple[PrecomputedEmbedder, list[float]]:
    """Embed each distinct query once. With a cache file, vectors computed in earlier runs are
    reused (keyed by model + text), which saves free-tier quota: embeddings are capped at 1000
    requests per day, and a rerun should not spend them again. Latencies cover fresh calls only."""
    stored: dict[str, list[float]] = {}
    if cache is not None and cache.exists():
        stored = json.loads(cache.read_text(encoding="utf8"))
    vectors: dict[str, list[float]] = {}
    latencies: list[float] = []
    try:
        for t in dict.fromkeys(texts):  # unique, order kept
            key = f"{cache_key}|{t}"
            if key in stored:
                vectors[t] = stored[key]
                continue
            t0 = perf_counter()
            (vectors[t],) = await embedder.embed([t], "query")
            latencies.append((perf_counter() - t0) * 1000)
            stored[key] = vectors[t]
    finally:  # keep what we paid for even if a later call fails (e.g. quota)
        if cache is not None:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(stored), encoding="utf8")
    return PrecomputedEmbedder(vectors), latencies


async def evaluate(
    maker: async_sessionmaker[AsyncSession],
    embedder: EmbeddingProvider,
    org_id: uuid.UUID,
    questions: list[dict[str, Any]],
    mode: str = "vector",
    reranker: Reranker | None = None,
) -> dict[str, Any]:
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; available: {MODES}")
    scored = [q for q in questions if q.get("gold")]
    rows: list[dict[str, Any]] = []
    for q in scored:
        t0 = perf_counter()
        async with maker() as session:
            hits = await search_documents(
                session,
                embedder,
                org_id,
                q["question"],
                mode=mode,  # type: ignore[arg-type]
                top_k=10,
                reranker=reranker,
            )
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
                "group": q.get("group") or q.get("fact") or q["type"],
                "page_rank": page_rank,
                "doc_rank": doc_rank,
                "ms": ms,
            }
        )
    ranks = [r["page_rank"] for r in rows]
    lat = [r["ms"] for r in rows] or [0.0]
    by_group: dict[str, dict[str, Any]] = {}
    for g in sorted({r["group"] for r in rows}):
        gr = [r["page_rank"] for r in rows if r["group"] == g]
        by_group[g] = {"n": len(gr), "recall@5": recall_at_k(gr, 5), "mrr@10": mrr_at_k(gr, 10)}
    return {
        "mode": mode,
        "n": len(rows),
        "recall@5": recall_at_k(ranks, 5),
        "mrr@10": mrr_at_k(ranks, 10),
        "doc_recall@5": recall_at_k([r["doc_rank"] for r in rows], 5),
        "p50_ms": percentile(lat, 50),
        "p95_ms": percentile(lat, 95),
        "by_group": by_group,
        "rows": rows,
    }


def append_docs_row(docs: Path, row: dict[str, Any], allow_fake: bool) -> None:
    """Add one result row to docs/evals.md. Fake-embedder or fake-reranker numbers are refused by
    default so a harness check can never end up as a headline number."""
    fake = row["embedder"] == "fake" or row.get("reranker") == "fake"
    if fake and not allow_fake:
        raise ValueError("refusing to record fake embedder/reranker numbers (use --allow-fake)")
    if not docs.exists():
        docs.write_text(DOCS_TEMPLATE, encoding="utf8")

    def label(v: str) -> str:
        return "fake (harness check only)" if v == "fake" else v

    line = (
        f"| {row['date']} | {row['git_sha']} | {row['label']} | {row.get('set', 'easy')} "
        f"| {row['mode']} | {label(row['embedder'])} | {label(row.get('reranker', '-'))} "
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
        # graphify-out/ is regenerated by hooks and says nothing about the code under test
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", ".", ":(exclude)graphify-out"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        ).stdout
        return sha + ("-dirty" if dirty.strip() else "")
    except Exception:
        return "unknown"


def eval_settings() -> Any:
    """The min-interval throttle exists for bulk ingestion. Left on, every query would wait 2 s and
    the latency numbers would just measure the throttle (a few dozen queries is far below any quota)."""
    return get_settings().model_copy(update={"embedding_min_interval_s": 0.0})


def _load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf8").splitlines() if line]


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

        sets = {name: _load(ROOT / "evals" / SETS[name]) for name in args.sets}
        texts = [q["question"] for qs in sets.values() for q in qs if q.get("gold")]
        fake_embedder = isinstance(deps.embedder, FakeEmbeddingProvider)
        print(f"embedding {len(set(texts))} queries once (cached ones are reused) ...")
        embedder, embed_ms = await precompute(
            deps.embedder,
            texts,
            None if fake_embedder else ROOT / "evals" / ".cache" / "query_vectors.json",
            s.embedding_model,
        )
        if embed_ms:
            print(
                f"  fresh query embeddings: p50={percentile(embed_ms, 50):.0f}ms "
                f"p95={percentile(embed_ms, 95):.0f}ms"
            )
        else:
            print("  all query vectors came from the cache")
        reranker: Reranker | None = None
        reranker_name = "-"
        if "hybrid_rerank" in args.modes:
            if args.fake_reranker:
                reranker, reranker_name = FakeReranker(), "fake"
            else:
                print(f"loading reranker {s.rerank_model} (first run downloads it) ...")
                reranker = FlashRankReranker(s.rerank_model, s.rerank_cache_dir)
                reranker_name = f"flashrank:{s.rerank_model}"

        out: dict[str, Any] = {
            "date": date.today().isoformat(),
            "git_sha": _git_sha(),
            "label": args.label,
            "embedder": "fake" if fake_embedder else "gemini",
            "embedding_model": None if fake_embedder else s.embedding_model,
            "reranker": reranker_name,
            "query_embed_ms": (
                {"p50": percentile(embed_ms, 50), "p95": percentile(embed_ms, 95)}
                if embed_ms
                else None
            ),
            "sets": {},
        }
        for set_name, questions in sets.items():
            out["sets"][set_name] = {}
            print(f"\n== {set_name} ({sum(1 for q in questions if q.get('gold'))} questions)")
            for mode in args.modes:
                res = await evaluate(
                    deps.maker,
                    embedder,
                    org_id,
                    questions,
                    mode,
                    reranker if mode == "hybrid_rerank" else None,
                )
                out["sets"][set_name][mode] = res
                print(
                    f"{mode:<14} recall@5={res['recall@5']:.1%} mrr@10={res['mrr@10']:.3f} "
                    f"doc@5={res['doc_recall@5']:.1%} search p50={res['p50_ms']:.0f}ms p95={res['p95_ms']:.0f}ms"
                )
                for g, v in res["by_group"].items():
                    print(
                        f"    {g:<30} n={v['n']:<3} recall@5={v['recall@5']:.0%} mrr@10={v['mrr@10']:.3f}"
                    )
                row = {
                    **out,
                    "set": set_name,
                    "mode": mode,
                    "reranker": reranker_name if mode == "hybrid_rerank" else "-",
                    **{
                        k: res[k]
                        for k in ("recall@5", "mrr@10", "doc_recall@5", "p50_ms", "p95_ms")
                    },
                }
                if (fake_embedder or row["reranker"] == "fake") and not args.allow_fake:
                    continue
                append_docs_row(args.docs, row, args.allow_fake)
        if fake_embedder or reranker_name == "fake":
            if not args.allow_fake:
                print("\n(fake embedder or reranker: docs/evals.md not updated)")
        suffix = f"_{args.label}" if args.label else ""
        path = args.results / f"{out['date']}_{out['git_sha']}{suffix}.json"
        args.results.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf8")
        print(f"\nwrote {path}")
    finally:
        await engine.dispose()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sets", nargs="+", default=["easy", "hard"], choices=list(SETS))
    ap.add_argument("--modes", nargs="+", default=MODES, choices=MODES)
    ap.add_argument("--label", default="")
    ap.add_argument("--email", default="eval@example.com")
    ap.add_argument("--results", type=Path, default=ROOT / "evals" / "results")
    ap.add_argument("--docs", type=Path, default=ROOT / "docs" / "evals.md")
    ap.add_argument("--allow-fake", action="store_true")
    ap.add_argument("--fake-reranker", action="store_true", help="harness check without a model")
    asyncio.run(_main(ap.parse_args()))


if __name__ == "__main__":
    main()
