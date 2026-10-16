from app.services.gemini import Throttle


async def test_throttle_spaces_calls_by_the_interval() -> None:
    sleeps: list[float] = []

    async def fake_sleep(s: float) -> None:
        sleeps.append(s)

    t = Throttle(2.0, clock=lambda: 0.0, sleep=fake_sleep)  # clock frozen: worst case burst
    for _ in range(3):
        await t.wait()
    assert sleeps == [2.0, 4.0]  # first call free, then 2 s and 4 s after the start


async def test_zero_interval_never_sleeps() -> None:
    sleeps: list[float] = []

    async def fake_sleep(s: float) -> None:
        sleeps.append(s)

    t = Throttle(0, clock=lambda: 0.0, sleep=fake_sleep)
    for _ in range(5):
        await t.wait()
    assert sleeps == []
