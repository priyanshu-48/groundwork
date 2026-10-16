from pathlib import Path

import pytest
from evals.build_questions import build_questions
from evals.generate_corpus import build_ground_truth, render_corpus
from evals.run_evals import append_docs_row, evaluate

from app.worker.deps import Deps
from app.worker.runner import process_one
from tests.helpers import new_org, seed


async def test_evaluate_reports_all_metrics_for_a_small_corpus(deps: Deps, tmp_path: Path) -> None:
    gt = build_ground_truth(seed=42, n_vendors=6, n_invoices=12)
    render_corpus(gt, tmp_path, seed=42)
    org = await new_org(deps)
    for v in gt["vendors"]:
        name = v["contract"]["filename"]
        await seed(deps, org, (tmp_path / "contracts" / name).read_bytes(), "contract", name)
    while await process_one(deps, "w"):
        pass
    qs = build_questions(gt, seed=42, n_lookup=12, n_aggregate=0, n_hop=0)
    assert len(qs) == 12

    result = await evaluate(deps.maker, deps.embedder, org, qs, mode="vector")  # type: ignore[arg-type]

    assert result["n"] == 12 and result["mode"] == "vector"
    for key in ("recall@5", "mrr@10", "doc_recall@5"):
        assert 0.0 <= result[key] <= 1.0
    assert 0 < result["p50_ms"] <= result["p95_ms"]
    assert set(result["by_fact"]) == {
        "payment_terms",
        "late_fee",
        "termination_notice",
        "auto_renewal",
        "liability_cap",
        "governing_law",
    }
    assert len(result["rows"]) == 12


def test_fake_embedder_numbers_never_reach_docs_without_opt_in(tmp_path: Path) -> None:
    docs = tmp_path / "evals.md"
    row = {
        "date": "2026-01-01",
        "git_sha": "abc1234",
        "label": "x",
        "mode": "vector",
        "embedder": "fake",
        "recall@5": 0.5,
        "mrr@10": 0.4,
        "doc_recall@5": 0.9,
        "p50_ms": 5.0,
        "p95_ms": 9.0,
    }
    with pytest.raises(ValueError, match="fake"):
        append_docs_row(docs, row, allow_fake=False)
    append_docs_row(docs, {**row, "embedder": "gemini"}, allow_fake=False)
    text = docs.read_text(encoding="utf8")
    assert "abc1234" in text and "50.0%" in text and "<!-- evals:end -->" in text
    append_docs_row(docs, row, allow_fake=True)
    assert "fake (harness check only)" in docs.read_text(encoding="utf8")
