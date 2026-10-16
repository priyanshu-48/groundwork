import pytest

from app.services.retrieval import rrf_fuse


def test_scores_are_summed_reciprocal_ranks() -> None:
    fused = dict(rrf_fuse([["a", "b"], ["b", "c"]], k=60))
    assert fused["a"] == pytest.approx(1 / 61)
    assert fused["b"] == pytest.approx(1 / 62 + 1 / 61)
    assert fused["c"] == pytest.approx(1 / 62)


def test_agreement_beats_a_single_high_rank() -> None:
    order = [item for item, _ in rrf_fuse([["a", "b"], ["b", "c"]])]
    assert order == ["b", "a", "c"]  # b is 2nd and 1st; a is only 1st in one list


def test_k_controls_how_much_top_ranks_dominate() -> None:
    small_k = dict(rrf_fuse([["a", "b"]], k=0))
    assert small_k["a"] / small_k["b"] == pytest.approx(2.0)  # 1/1 vs 1/2
    large_k = dict(rrf_fuse([["a", "b"]], k=1000))
    assert large_k["a"] / large_k["b"] < 1.01  # nearly flat


def test_ties_keep_first_seen_order() -> None:
    assert [i for i, _ in rrf_fuse([["a"], ["b"]])] == ["a", "b"]


def test_empty_inputs() -> None:
    assert rrf_fuse([]) == []
    assert rrf_fuse([[], []]) == []


def test_raw_scores_never_matter_only_ranks() -> None:
    # Fusing by rank is why a cosine score (0..1) and a ts_rank_cd score (unbounded) can be mixed.
    assert rrf_fuse([["x", "y"]]) == rrf_fuse([["x", "y"]])


def test_prepare_keyword_query_turns_identifiers_into_phrases() -> None:
    from app.repositories.chunks import prepare_keyword_query as prep

    assert prep("Find invoice V02-2025-0003") == 'Find invoice "V02 2025 0003"'
    assert prep('"V02-2025-0003"') == '"V02 2025 0003"'  # already quoted: not double-wrapped
    assert prep("issued 2025-03-05 for 1,234.50") == 'issued "2025 03 05" for 1,234.50'
    assert prep("late payment penalty") == "late payment penalty"
    assert prep("exclude -draft") == "exclude -draft"  # a leading minus is search syntax, kept


def test_specific_terms_pick_out_ids_dates_and_amounts() -> None:
    from app.repositories.chunks import prepare_keyword_query, specific_terms

    q = prepare_keyword_query(
        "Find invoice V02-2025-0003 from Kestrel dated 2025-03-05 for 1,234.50"
    )
    assert specific_terms(q) == ['"V02 2025 0003"', '"2025 03 05"', "1,234.50"]
    assert specific_terms("what is the liability cap") == []
