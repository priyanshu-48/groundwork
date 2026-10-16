import pytest
from evals.metrics import mrr_at_k, percentile, recall_at_k

# 1-based rank of the first relevant hit per question; None = never retrieved
RANKS = [1, 3, None, 7, 12]


def test_recall_at_k_counts_hits_within_k() -> None:
    assert recall_at_k(RANKS, 5) == pytest.approx(2 / 5)  # ranks 1 and 3
    assert recall_at_k(RANKS, 10) == pytest.approx(3 / 5)  # + rank 7
    assert recall_at_k(RANKS, 1) == pytest.approx(1 / 5)


def test_mrr_at_k_ignores_hits_beyond_k_and_misses() -> None:
    # 1/1 + 1/3 + 0 + 1/7 + 0 (rank 12 is past k=10), averaged over 5 questions
    assert mrr_at_k(RANKS, 10) == pytest.approx((1 + 1 / 3 + 1 / 7) / 5)


def test_empty_input_is_zero_not_a_crash() -> None:
    assert recall_at_k([], 5) == 0.0
    assert mrr_at_k([], 10) == 0.0


def test_percentile_interpolates() -> None:
    assert percentile([10.0, 20.0, 30.0, 40.0], 50) == pytest.approx(25.0)
    assert percentile([10.0, 20.0, 30.0, 40.0], 100) == 40.0
    assert percentile([10.0, 20.0, 30.0, 40.0], 0) == 10.0
    assert percentile([7.0], 95) == 7.0
