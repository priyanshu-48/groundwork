from pathlib import Path

import pytest
from evals.build_questions import build_questions, build_retrieval_questions
from evals.run_evals import MODES, append_docs_row, evaluate, precompute

from app.services.rerank import FakeReranker
from app.worker.deps import Deps
from tests.helpers import ingest_corpus, new_org


async def test_every_mode_and_set_reports_all_metrics(deps: Deps, small: tuple[dict, Path]) -> None:
    gt, out = small
    org = await new_org(deps)
    await ingest_corpus(deps, org, gt, out)
    sets = {
        "easy": build_questions(gt, seed=42, n_lookup=12, n_aggregate=0, n_hop=0),
        "hard": build_retrieval_questions(gt, seed=42, n_id=6, n_paraphrase=12, n_fields=4),
    }
    for questions in sets.values():
        for mode in MODES:
            result = await evaluate(deps.maker, deps.embedder, org, questions, mode, FakeReranker())
            assert result["mode"] == mode and result["n"] == len(questions)
            for key in ("recall@5", "mrr@10", "doc_recall@5"):
                assert 0.0 <= result[key] <= 1.0
            assert 0 < result["p50_ms"] <= result["p95_ms"]
            assert sum(g["n"] for g in result["by_group"].values()) == len(questions)


async def test_hard_set_exact_ids_are_found_by_keyword_modes(
    deps: Deps, small: tuple[dict, Path]
) -> None:
    gt, out = small
    org = await new_org(deps)
    await ingest_corpus(deps, org, gt, out)
    ids = [
        q
        for q in build_retrieval_questions(gt, seed=42, n_id=6, n_paraphrase=0, n_fields=0)
        if q["type"] == "retrieval_invoice_id"
    ]
    res = await evaluate(deps.maker, deps.embedder, org, ids, "hybrid")
    assert res["recall@5"] == 1.0  # an exact identifier is the keyword side's home turf


async def test_precomputed_embedder_returns_the_stored_vectors(deps: Deps) -> None:
    emb, ms = await precompute(deps.embedder, ["a b", "c d", "a b"])
    assert len(ms) == 2  # duplicates are embedded once
    assert await emb.embed(["c d"], "query") == await deps.embedder.embed(["c d"], "query")


def test_fake_embedder_numbers_never_reach_docs_without_opt_in(tmp_path: Path) -> None:
    docs = tmp_path / "evals.md"
    row = {
        "date": "2026-01-01",
        "git_sha": "abc1234",
        "label": "x",
        "mode": "vector",
        "embedder": "fake",
        "set": "easy",
        "reranker": "-",
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


def test_eval_queries_are_never_throttled(monkeypatch: pytest.MonkeyPatch) -> None:
    from evals.run_evals import eval_settings

    from app.config import get_settings

    monkeypatch.setenv("EMBEDDING_MIN_INTERVAL_S", "2")
    get_settings.cache_clear()
    try:
        assert get_settings().embedding_min_interval_s == 2
        assert eval_settings().embedding_min_interval_s == 0
    finally:
        get_settings.cache_clear()


def test_fake_reranker_numbers_are_refused_too(tmp_path: Path) -> None:
    row = {
        "date": "2026-01-01",
        "git_sha": "abc1234",
        "label": "x",
        "set": "hard",
        "mode": "hybrid_rerank",
        "embedder": "gemini",
        "reranker": "fake",
        "recall@5": 0.5,
        "mrr@10": 0.4,
        "doc_recall@5": 0.9,
        "p50_ms": 5.0,
        "p95_ms": 9.0,
    }
    with pytest.raises(ValueError, match="fake"):
        append_docs_row(tmp_path / "evals.md", row, allow_fake=False)
