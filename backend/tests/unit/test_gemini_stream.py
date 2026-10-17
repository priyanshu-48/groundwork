from types import SimpleNamespace
from typing import Any

import pytest
from google.genai import errors, types

from app.agent.llm import GeminiLLM, LLMError, LLMResponse, Message, ToolCall
from app.services.gemini import LLMUnavailable, ModelChain

DAILY = "GenerateRequestsPerDayPerProjectPerModel-FreeTier 'retryDelay': '3600s'"


def chunk(*parts: types.Part, usage: tuple[int, int, int] | None = None) -> Any:
    meta = None
    if usage:
        meta = types.GenerateContentResponseUsageMetadata(
            prompt_token_count=usage[0],
            candidates_token_count=usage[1],
            thoughts_token_count=usage[2],
        )
    return SimpleNamespace(
        candidates=[SimpleNamespace(content=types.Content(role="model", parts=list(parts)))],
        usage_metadata=meta,
        prompt_feedback=None,
    )


class StreamModels:
    def __init__(self, plan: dict[str, Any]) -> None:
        self.plan, self.opened = plan, []

    def generate_content_stream(self, *, model: str, contents: Any, config: Any) -> Any:
        self.opened.append((model, config))
        outcome = self.plan[model]
        if isinstance(outcome, Exception):
            raise outcome
        return iter(outcome)


def llm(plan: dict[str, Any], models: list[str]) -> tuple[GeminiLLM, StreamModels]:
    m = StreamModels(plan)
    return GeminiLLM(SimpleNamespace(models=m), ModelChain(models)), m


async def collect(g: Any) -> tuple[list[str], LLMResponse]:
    deltas, final = [], None
    async for item in g:
        if isinstance(item, str):
            deltas.append(item)
        else:
            final = item
    assert final is not None
    return deltas, final


async def test_text_arrives_as_deltas_then_one_assembled_response() -> None:
    chunks = [
        chunk(types.Part(text="Hel")),
        chunk(types.Part(text="lo [C1]"), usage=(11, 4, 3)),
    ]
    g, m = llm({"m1": chunks}, ["m1"])
    deltas, final = await collect(g.generate_stream("sys", [Message("user", "q")], []))
    assert deltas == ["Hel", "lo [C1]"]
    assert final.text == "Hello [C1]" and final.model == "m1"
    assert (final.usage.prompt_tokens, final.usage.completion_tokens) == (11, 7)
    assert m.opened[0][1].automatic_function_calling.disable is True


async def test_thoughts_are_never_streamed_to_the_user() -> None:
    chunks = [chunk(types.Part(text="secret reasoning", thought=True), types.Part(text="Answer"))]
    g, _ = llm({"m1": chunks}, ["m1"])
    deltas, final = await collect(g.generate_stream("s", [Message("user", "q")], []))
    assert deltas == ["Answer"] and final.text == "Answer"


async def test_function_calls_and_thought_signatures_survive_assembly() -> None:
    call_part = types.Part(
        function_call=types.FunctionCall(name="search_documents", args={"query": "q"}, id="7"),
        thought_signature=b"sig",
    )
    chunks = [chunk(types.Part(text="Let me check. ")), chunk(call_part, usage=(5, 2, 0))]
    g, _ = llm({"m1": chunks}, ["m1"])
    deltas, final = await collect(g.generate_stream("s", [Message("user", "q")], []))
    assert deltas == ["Let me check. "]
    assert final.tool_calls == (ToolCall("search_documents", {"query": "q"}, "7"),)
    assert final.raw.role == "model" and final.raw.parts[1].thought_signature == b"sig"


async def test_a_quota_error_when_the_stream_opens_falls_over_to_the_next_model() -> None:
    quota = errors.APIError(429, {"error": {"message": DAILY}})
    g, m = llm({"m1": quota, "m2": [chunk(types.Part(text="from m2"))]}, ["m1", "m2"])
    deltas, final = await collect(g.generate_stream("s", [Message("user", "q")], []))
    assert final.model == "m2" and deltas == ["from m2"]
    assert [model for model, _ in m.opened] == ["m1", "m2"]


async def test_bad_requests_do_not_fall_over_and_exhaustion_is_clear() -> None:
    g, m = llm({"m1": errors.APIError(400, {"error": {"message": "bad"}})}, ["m1", "m2"])
    with pytest.raises(errors.APIError):
        await collect(g.generate_stream("s", [Message("user", "q")], []))
    assert [model for model, _ in m.opened] == ["m1"]
    quota = errors.APIError(429, {"error": {"message": DAILY}})
    g, _ = llm({"m1": quota, "m2": quota}, ["m1", "m2"])
    with pytest.raises(LLMUnavailable):
        await collect(g.generate_stream("s", [Message("user", "q")], []))


async def test_an_empty_stream_is_an_llm_error() -> None:
    g, _ = llm({"m1": []}, ["m1"])
    with pytest.raises(LLMError):
        await collect(g.generate_stream("s", [Message("user", "q")], []))
