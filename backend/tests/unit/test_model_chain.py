import pytest
from google.genai import errors

from app.services.gemini import LLMUnavailable, ModelChain, retry_delay_s


def api_error(code: int, msg: str = "boom") -> errors.APIError:
    return errors.APIError(code, {"error": {"message": msg}})


DAILY = "Quota exceeded: GenerateRequestsPerDayPerProjectPerModel-FreeTier. 'retryDelay': '17928s'"


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def make(models: list[str], clock: Clock | None = None) -> tuple[ModelChain, Clock]:
    c = clock or Clock()
    return ModelChain(models, clock=c), c


async def test_first_model_answers_when_healthy() -> None:
    chain, _ = make(["a", "b"])

    async def call(m: str) -> str:
        return f"ok-{m}"

    assert await chain.run(call) == ("a", "ok-a")


async def test_daily_quota_moves_to_the_next_model_and_remembers() -> None:
    chain, _ = make(["a", "b"])
    tried: list[str] = []

    async def call(m: str) -> str:
        tried.append(m)
        if m == "a":
            raise api_error(429, DAILY)
        return "ok"

    assert (await chain.run(call))[0] == "b"
    tried.clear()
    assert (await chain.run(call))[0] == "b"
    assert tried == ["b"]  # "a" is not even attempted again: no wasted request


async def test_exhausted_model_comes_back_after_its_retry_delay() -> None:
    chain, clock = make(["a", "b"])
    calls: list[str] = []

    async def call(m: str) -> str:
        calls.append(m)
        if m == "a" and clock.now < 17928:
            raise api_error(429, DAILY)
        return "ok"

    await chain.run(call)
    clock.now = 17929
    calls.clear()
    assert (await chain.run(call))[0] == "a"


@pytest.mark.parametrize("code", [500, 503, 404])
async def test_server_errors_and_missing_models_fall_over(code: int) -> None:
    chain, _ = make(["a", "b"])

    async def call(m: str) -> str:
        if m == "a":
            raise api_error(code)
        return "ok"

    assert (await chain.run(call))[0] == "b"


@pytest.mark.parametrize("code", [400, 401, 403])
async def test_client_errors_never_fall_over(code: int) -> None:
    chain, _ = make(["a", "b"])
    tried: list[str] = []

    async def call(m: str) -> str:
        tried.append(m)
        raise api_error(code)

    with pytest.raises(errors.APIError):
        await chain.run(call)
    assert tried == ["a"]  # a different model would not fix a bad request


async def test_all_models_exhausted_is_a_clear_error() -> None:
    chain, _ = make(["a", "b"])

    async def call(m: str) -> str:
        raise api_error(429, DAILY)

    with pytest.raises(LLMUnavailable, match="a, b"):
        await chain.run(call)
    with pytest.raises(LLMUnavailable):  # and stays unavailable without calling anything
        await chain.run(call)


def test_retry_delay_is_read_from_the_error() -> None:
    assert retry_delay_s(api_error(429, DAILY)) == 17928
    assert retry_delay_s(api_error(429, "no hint here")) is None
    assert retry_delay_s(api_error(429, "'retryDelay': '2.5s'")) == 2.5


def test_empty_chain_is_rejected() -> None:
    with pytest.raises(ValueError):
        ModelChain([])
