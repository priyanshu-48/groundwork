"""Run the real agent over the eval questions and score the answers.

Run (from backend/, stack up, corpus loaded, invoices extracted with app.worker.backfill_invoices):
    uv run python ../evals/run_agent_evals.py --types contract_lookup --max-llm-calls 25 --label m6

Built for a free tier: finished questions are cached (evals/.cache/agent_runs.jsonl) so a rerun
after the daily quota resets continues where it stopped, errored runs are never cached, and
--max-llm-calls stops before the budget is exceeded. A table row goes into docs/evals.md only when
every question of a type has an answer.
"""

import argparse
import asyncio
import hashlib
import json
import sys
import uuid
from datetime import date
from pathlib import Path
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "backend"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sqlalchemy import text  # noqa: E402

from app.agent.llm import LLM, LLMResponse, Message, ToolSpec  # noqa: E402
from app.agent.loop import run_agent  # noqa: E402
from app.agent.prompts import SYSTEM  # noqa: E402
from app.agent.service import make_context  # noqa: E402
from app.config import model_chain_names  # noqa: E402
from app.worker.deps import Deps, build_deps  # noqa: E402
from evals.metrics import percentile  # noqa: E402
from evals.run_evals import _git_sha, eval_settings  # noqa: E402
from evals.scoring import citation_counts, score_answer  # noqa: E402

CACHE = ROOT / "evals" / ".cache" / "agent_runs.jsonl"
TYPES = ["contract_lookup", "invoice_aggregate", "multi_hop"]
AGENT_HEADER = (
    "\n## Agent answers\n\n"
    "Real agent (tools + model), answers scored by rules in `evals/scoring.py` "
    "(docs/decisions/0008). Citation precision = share of cited chunks that hold the answer, "
    "over answers that cite anything (not defined for multi-hop).\n\n"
    "| Date | Git SHA | Label | Type | Model(s) | Answered | Accuracy | Citation precision "
    "| Avg steps | Avg tokens in/out | p50 s | p95 s |\n"
    "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    "<!-- agent:end -->\n"
)


class CountingLLM:
    """Counts model calls so --max-llm-calls can stop a run before it spends the day's quota."""

    def __init__(self, inner: LLM) -> None:
        self.inner, self.calls = inner, 0

    async def generate(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> LLMResponse:
        self.calls += 1
        return await self.inner.generate(system, messages, tools)


def prompt_fingerprint() -> str:
    return hashlib.sha256(SYSTEM.encode()).hexdigest()[:12]


def cache_key(chain: list[str], q: dict[str, Any], mode: str) -> str:
    raw = json.dumps([chain, q["id"], q["question"], mode, prompt_fingerprint()])
    return hashlib.sha256(raw.encode()).hexdigest()


def load_cache(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf8").splitlines():
        if line:
            rec = json.loads(line)
            out[rec["key"]] = rec
    return out


def _append_cache(path: Path, rec: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf8") as f:
        f.write(json.dumps(rec) + "\n")


async def ask_once(deps: Deps, org_id: uuid.UUID, llm: LLM, question: str) -> dict[str, Any]:
    ctx = make_context(deps, org_id)
    done: dict[str, Any] = {}
    t0 = perf_counter()
    async for event in run_agent(ctx, llm, question):
        if event.type == "done":
            done = event.data
    done["wall_s"] = perf_counter() - t0
    return done


async def evaluate_agent(
    deps: Deps,
    org_id: uuid.UUID,
    llm: LLM,
    questions: list[dict[str, Any]],
    gt: dict[str, Any],
    *,
    chain: list[str],
    cache_path: Path | None,
    max_llm_calls: int | None = None,
) -> dict[str, Any]:
    counting = CountingLLM(llm)
    cache = load_cache(cache_path) if cache_path else {}
    vendors = [v["name"] for v in gt["vendors"]]
    mode = deps.settings.search_mode
    per_type: dict[str, list[dict[str, Any]]] = {}
    stopped = False
    for q in questions:
        key = cache_key(chain, q, mode)
        rec = cache.get(key)
        if rec is None:
            if max_llm_calls is not None and counting.calls >= max_llm_calls:
                stopped = True
                break
            done = await ask_once(deps, org_id, counting, q["question"])
            if done["status"] == "error":
                continue  # quota or outage: not an answer, never cached, retried next run
            rec = {
                "key": key,
                "id": q["id"],
                "status": done["status"],
                "answer": done["answer"],
                "citations": done["citations"],
                "model": done["model"],
                "steps": len(done["steps"]),
                "prompt_tokens": done["prompt_tokens"],
                "completion_tokens": done["completion_tokens"],
                "latency_s": done["wall_s"],
            }
            if cache_path:
                _append_cache(cache_path, rec)
        correct = rec["status"] == "ok" and score_answer(q, rec["answer"], vendors)
        counts = citation_counts(q, rec["citations"], gt) if rec["citations"] else None
        per_type.setdefault(q["type"], []).append({**rec, "correct": correct, "cites": counts})

    summary: dict[str, Any] = {}
    for t in TYPES:
        total = sum(1 for q in questions if q["type"] == t)
        got = per_type.get(t, [])
        if not total:
            continue
        rel = sum(c[0] for r in got if (c := r["cites"]))
        cited = sum(c[1] for r in got if (c := r["cites"]))
        lat = [r["latency_s"] for r in got] or [0.0]
        summary[t] = {
            "total": total,
            "answered": len(got),
            "correct": sum(r["correct"] for r in got),
            "accuracy": (sum(r["correct"] for r in got) / len(got)) if got else None,
            "citation_precision": (rel / cited) if cited else None,
            "cited_chunks": cited,
            "avg_steps": (sum(r["steps"] for r in got) / len(got)) if got else None,
            "avg_prompt_tokens": (sum(r["prompt_tokens"] for r in got) / len(got)) if got else None,
            "avg_completion_tokens": (sum(r["completion_tokens"] for r in got) / len(got))
            if got
            else None,
            "p50_s": percentile(lat, 50),
            "p95_s": percentile(lat, 95),
            "models": sorted({r["model"] for r in got if r["model"]}),
            "complete": len(got) == total,
            "rows": [
                {"id": r["id"], "correct": r["correct"], "model": r["model"], "steps": r["steps"]}
                for r in got
            ],
        }
    return {"summary": summary, "llm_calls": counting.calls, "stopped_by_budget": stopped}


def append_agent_rows(
    docs: Path, meta: dict[str, Any], summary: dict[str, Any], *, fake: bool
) -> list[str]:
    """Write one docs row per *complete* question type. Fake-LLM runs are refused outright."""
    if fake:
        raise ValueError("refusing to record fake LLM numbers")
    content = docs.read_text(encoding="utf8") if docs.exists() else ""
    if "<!-- agent:end -->" not in content:
        content = content.rstrip("\n") + "\n" + AGENT_HEADER
    written: list[str] = []
    lines = ""
    for t, s in summary.items():
        if not s["complete"]:
            continue
        prec = (
            f"{s['citation_precision'] * 100:.1f}%"
            if s["citation_precision"] is not None
            else "n/a"
        )
        lines += (
            f"| {meta['date']} | {meta['git_sha']} | {meta['label']} | {t} | {', '.join(s['models'])} "
            f"| {s['answered']}/{s['total']} | {s['accuracy'] * 100:.1f}% | {prec} "
            f"| {s['avg_steps']:.1f} | {s['avg_prompt_tokens']:.0f}/{s['avg_completion_tokens']:.0f} "
            f"| {s['p50_s']:.1f} | {s['p95_s']:.1f} |\n"
        )
        written.append(t)
    docs.write_text(
        content.replace("<!-- agent:end -->", lines + "<!-- agent:end -->", 1), encoding="utf8"
    )
    return written


async def _main(args: argparse.Namespace) -> int:
    s = eval_settings()
    deps, engine = build_deps(s)
    try:
        if deps.llm is None:
            raise SystemExit("no real LLM: set AI_PROVIDER=gemini and GEMINI_API_KEY")
        async with deps.maker() as session:
            org_id = (
                await session.execute(
                    text("SELECT org_id FROM users WHERE email = :e"), {"e": args.email}
                )
            ).scalar_one_or_none()
            n_inv = (
                await session.execute(
                    text("SELECT count(*) FROM invoices WHERE org_id = :o AND NOT needs_review"),
                    {"o": org_id},
                )
            ).scalar()
        if org_id is None:
            raise SystemExit(f"no user {args.email}; run load_corpus.py first")
        if not n_inv and any(t != "contract_lookup" for t in args.types):
            raise SystemExit(
                "no extracted invoices: run `python -m app.worker.backfill_invoices` first"
            )
        gt = json.loads((ROOT / "evals" / "ground_truth.json").read_text(encoding="utf8"))
        all_q = [
            json.loads(line)
            for line in (ROOT / "evals" / "questions.jsonl").read_text(encoding="utf8").splitlines()
            if line
        ]
        questions: list[dict[str, Any]] = []
        for t in args.types:
            picked = [q for q in all_q if q["type"] == t]
            questions += picked[: args.limit] if args.limit else picked

        chain = model_chain_names(s)
        result = await evaluate_agent(
            deps,
            org_id,
            deps.llm,
            questions,
            gt,
            chain=chain,
            cache_path=CACHE,
            max_llm_calls=args.max_llm_calls,
        )
        meta = {"date": date.today().isoformat(), "git_sha": _git_sha(), "label": args.label}
        print(f"model chain: {', '.join(chain)}; search mode: {s.search_mode}")
        for t, v in result["summary"].items():
            acc = f"{v['accuracy']:.1%}" if v["accuracy"] is not None else "n/a"
            prec = (
                f"{v['citation_precision']:.1%} of {v['cited_chunks']} cited"
                if v["citation_precision"] is not None
                else "n/a"
            )
            print(
                f"{t:<18} answered {v['answered']}/{v['total']}  accuracy {acc}  "
                f"citation precision {prec}  models {v['models']}"
            )
        if result["stopped_by_budget"]:
            print(
                f"stopped at the --max-llm-calls budget after {result['llm_calls']} calls; rerun to continue"
            )
        elif any(v["answered"] < v["total"] for v in result["summary"].values()):
            print("some questions errored (quota or outage) and will be retried on the next run")
        written = append_agent_rows(args.docs, meta, result["summary"], fake=False)
        print(f"docs/evals.md rows written for: {written or 'none (no type is complete yet)'}")
        args.results.mkdir(parents=True, exist_ok=True)
        path = args.results / f"{meta['date']}_{meta['git_sha']}_agent_{args.label or 'run'}.json"
        path.write_text(
            json.dumps({**meta, "chain": chain, **result}, indent=2) + "\n", encoding="utf8"
        )
        print(f"wrote {path}")
    finally:
        await engine.dispose()
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--types", nargs="+", default=TYPES, choices=TYPES)
    ap.add_argument("--limit", type=int, default=0, help="first N questions of each type")
    ap.add_argument("--max-llm-calls", type=int, default=None)
    ap.add_argument("--label", default="")
    ap.add_argument("--email", default="eval@example.com")
    ap.add_argument("--results", type=Path, default=ROOT / "evals" / "results")
    ap.add_argument("--docs", type=Path, default=ROOT / "docs" / "evals.md")
    raise SystemExit(asyncio.run(_main(ap.parse_args())))


if __name__ == "__main__":
    main()
