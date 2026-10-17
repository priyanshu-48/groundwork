import json
from decimal import Decimal

from app.services.metrics import HttpMetrics, parse_prices, percentile


def test_percentile_interpolates() -> None:
    assert percentile([], 50) == 0.0
    assert percentile([10], 99) == 10
    assert percentile([1, 2, 3, 4], 50) == 2.5
    assert abs(percentile(list(range(1, 101)), 95) - 95.05) < 1e-9


def test_summary_groups_by_route_and_counts_5xx_as_errors() -> None:
    m = HttpMetrics()
    for ms in (10, 20, 30, 40):
        m.record("/search", 200, ms)
    m.record("/search", 500, 100)
    m.record("/health", 200, 1)
    s = m.summary()
    assert s["overall"]["count"] == 6
    assert s["routes"]["/search"]["count"] == 5
    assert s["routes"]["/search"]["error_rate"] == 0.2
    assert s["routes"]["/health"]["p95_ms"] == 1


def test_ring_buffer_is_bounded() -> None:
    m = HttpMetrics(size=3)
    for i in range(10):
        m.record("/x", 200, i)
    assert m.summary()["overall"]["count"] == 3


def test_prices_parse_to_decimal_and_empty_means_none() -> None:
    assert parse_prices("") == {}
    p = parse_prices(json.dumps({"m": [0.3, 2.5]}))
    assert p["m"] == (Decimal("0.3"), Decimal("2.5"))
