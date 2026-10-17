import uuid
from pathlib import Path
from typing import Any

import pytest
from evals.build_questions import build_questions
from evals.generate_corpus import build_ground_truth
from evals.run_agent_evals import append_agent_rows, cache_key, evaluate_agent

from app.agent.llm import LLMResponse, Message, ToolSpec, say
from app.services.gemini import LLMUnavailable
from app.worker.deps import Deps

GT = build_ground_truth(seed=42, n_vendors=6, n_invoices=24)
QS = build_questions(GT, seed=42, n_lookup=12, n_aggregate=0, n_hop=0)
RIGHT = {
    "payment_terms": lambda a: f"Net {a.split('-')[1]} [C1]",
    "late_fee": lambda a: f"{a} per month",
    "termination_notice": lambda a: f"{a} written notice",
    "auto_renewal": lambda a: (
        "Yes, it renews automatically." if a == "yes" else "No, it does not renew."
    ),
    "liability_cap": lambda a: f"Capped at {a}",
    "governing_law": lambda a: f"Governed by {a}",
}


class CannedLLM:
    """Answers each question from a dict keyed by question text; counts nothing itself."""

    def __init__(self, right: set[str], fail_on: set[str] = frozenset()) -> None:  # type: ignore[assignment]
        self.right, self.fail_on = right, fail_on

    async def generate(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> LLMResponse:
        q = messages[-1].text
        if q in self.fail_on:
            raise LLMUnavailable("quota")
        item = next(x for x in QS if x["question"] == q)
        if q in self.right:
            return say(RIGHT[item["fact"]](item["answer"]))
        return say("I could not find that.")


def run(deps: Deps, llm: Any, cache: Path | None, **kw: Any):  # type: ignore[no-untyped-def]
    return evaluate_agent(deps, uuid.uuid4(), llm, QS, GT, chain=["m1"], cache_path=cache, **kw)


ALL_RIGHT = {q["question"] for q in QS}


async def test_accuracy_counts_right_and_wrong_answers(deps: Deps) -> None:
    half = {q["question"] for q in QS[:6]}
    r = await run(deps, CannedLLM(half), None)
    s = r["summary"]["contract_lookup"]
    assert (s["answered"], s["total"], s["correct"], s["complete"]) == (12, 12, 6, True)
    assert s["accuracy"] == 0.5 and r["llm_calls"] == 12
    assert s["avg_prompt_tokens"] == 10 and s["models"] == ["fake-model"]


async def test_a_rerun_uses_the_cache_and_makes_no_llm_calls(deps: Deps, tmp_path: Path) -> None:
    cache = tmp_path / "runs.jsonl"
    first = await run(deps, CannedLLM(ALL_RIGHT), cache)
    again = await run(deps, CannedLLM(set()), cache)  # a model that would now get everything wrong
    assert again["llm_calls"] == 0
    assert (
        again["summary"]["contract_lookup"]["accuracy"]
        == first["summary"]["contract_lookup"]["accuracy"]
        == 1.0
    )


async def test_the_call_budget_stops_early_and_the_next_run_resumes(
    deps: Deps, tmp_path: Path
) -> None:
    cache = tmp_path / "runs.jsonl"
    part = await run(deps, CannedLLM(ALL_RIGHT), cache, max_llm_calls=5)
    s = part["summary"]["contract_lookup"]
    assert part["stopped_by_budget"] and (s["answered"], s["complete"]) == (5, False)
    rest = await run(deps, CannedLLM(ALL_RIGHT), cache)
    assert rest["llm_calls"] == 7  # only what was missing
    assert rest["summary"]["contract_lookup"]["complete"]


async def test_failed_runs_are_not_cached_and_are_retried(deps: Deps, tmp_path: Path) -> None:
    cache = tmp_path / "runs.jsonl"
    victim = QS[3]["question"]
    first = await run(deps, CannedLLM(ALL_RIGHT, fail_on={victim}), cache)
    assert first["summary"]["contract_lookup"]["answered"] == 11
    second = await run(deps, CannedLLM(ALL_RIGHT), cache)
    assert second["llm_calls"] == 1 and second["summary"]["contract_lookup"]["answered"] == 12


def test_cache_keys_change_with_the_model_chain_and_search_mode() -> None:
    q = QS[0]
    assert cache_key(["a"], q, "hybrid") != cache_key(["b"], q, "hybrid")
    assert cache_key(["a"], q, "hybrid") != cache_key(["a"], q, "vector")
    assert cache_key(["a"], q, "hybrid") == cache_key(["a"], q, "hybrid")


def test_docs_rows_only_for_complete_types_and_never_for_fakes(tmp_path: Path) -> None:
    done = {
        "total": 2, "answered": 2, "correct": 1, "accuracy": 0.5, "citation_precision": None,
        "cited_chunks": 0, "avg_steps": 2.0, "avg_prompt_tokens": 100.0,
        "avg_completion_tokens": 20.0, "p50_s": 1.5, "p95_s": 2.5, "models": ["m1"],
        "complete": True,
    }  # fmt: skip
    partial = {**done, "answered": 1, "complete": False}
    meta = {"date": "2026-01-01", "git_sha": "abc1234", "label": "t"}
    docs = tmp_path / "evals.md"
    written = append_agent_rows(
        docs, meta, {"contract_lookup": done, "multi_hop": partial}, fake=False
    )
    text = docs.read_text(encoding="utf8")
    assert written == ["contract_lookup"] and "multi_hop" not in text
    assert "| contract_lookup | m1 | 2/2 | 50.0% | n/a |" in text
    with pytest.raises(ValueError, match="fake"):
        append_agent_rows(docs, meta, {"contract_lookup": done}, fake=True)
