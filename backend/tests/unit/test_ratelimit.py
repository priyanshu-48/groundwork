from app.services.ratelimit import ConcurrencyLimiter, SlidingWindowLimiter


class Clock:
    def __init__(self) -> None:
        self.t = 1000.0

    def __call__(self) -> float:
        return self.t


def test_allows_up_to_the_limit_then_reports_when_to_retry() -> None:
    clock = Clock()
    lim = SlidingWindowLimiter(3, 60, clock)
    for _ in range(3):
        assert lim.check("a") is None
        clock.t += 1
    wait = lim.check("a")
    assert wait is not None and 56.9 < wait < 57.1  # first hit at t=1000 frees up at 1060


def test_window_slides_instead_of_resetting() -> None:
    clock = Clock()
    lim = SlidingWindowLimiter(2, 60, clock)
    assert lim.check("a") is None  # t=1000
    clock.t += 30
    assert lim.check("a") is None  # t=1030
    clock.t += 29.9
    assert lim.check("a") is not None  # t=1059.9: both still inside the window
    clock.t += 0.2
    assert lim.check("a") is None  # t=1060.1: the first hit has aged out
    assert lim.check("a") is not None  # but the second is still in


def test_rejected_calls_are_not_counted() -> None:
    clock = Clock()
    lim = SlidingWindowLimiter(1, 60, clock)
    assert lim.check("a") is None
    for _ in range(50):
        assert lim.check("a") is not None
    clock.t += 60.1
    assert lim.check("a") is None  # hammering while blocked does not extend the block


def test_keys_are_independent() -> None:
    lim = SlidingWindowLimiter(1, 60, Clock())
    assert lim.check("a") is None
    assert lim.check("b") is None
    assert lim.check("a") is not None


def test_idle_keys_are_pruned() -> None:
    clock = Clock()
    lim = SlidingWindowLimiter(5, 60, clock)
    for i in range(255):
        lim.check(f"k{i}")
    clock.t += 120
    lim.check("fresh")  # the 256th call triggers pruning
    assert set(lim._hits) == {"fresh"}


def test_concurrency_cap_release_and_idempotent_release() -> None:
    lim = ConcurrencyLimiter(2)
    t1, t2 = lim.acquire("a"), lim.acquire("a")
    assert t1 and t2 and lim.acquire("a") is None
    assert lim.acquire("b") is not None  # other tenant unaffected
    lim.release("a", t1)
    lim.release("a", t1)  # double release must not free someone else's slot
    assert lim.acquire("a") is not None
    assert lim.acquire("a") is None


def test_a_leaked_slot_is_reclaimed_after_the_max_hold() -> None:
    clock = Clock()
    lim = ConcurrencyLimiter(1, max_hold_s=300, clock=clock)
    assert lim.acquire("a") is not None
    assert lim.acquire("a") is None
    clock.t += 301
    assert lim.acquire("a") is not None
