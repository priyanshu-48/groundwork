from types import SimpleNamespace
from typing import Any

import pytest
from google.genai import errors, types

from app.agent.llm import (
    GeminiLLM,
    LLMError,
    Message,
    ToolCall,
    ToolResult,
    ToolSpec,
    _to_content,
    clean_schema,
    parse_response,
)
from app.agent.tools import TOOLS, specs
from app.services.gemini import LLMUnavailable, ModelChain

DAILY = "GenerateRequestsPerDayPerProjectPerModel-FreeTier 'retryDelay': '3600s'"


def response(parts: list[types.Part], prompt: int = 11, out: int = 4, thoughts: int = 3) -> Any:
    return SimpleNamespace(
        candidates=[SimpleNamespace(content=types.Content(role="model", parts=parts))],
        # the real SDK class, so a wrong field name here fails the test (it did, once, live)
        usage_metadata=types.GenerateContentResponseUsageMetadata(
            prompt_token_count=prompt, candidates_token_count=out, thoughts_token_count=thoughts
        ),
    )


class StubModels:
    def __init__(self, plan: dict[str, Any]) -> None:
        self.plan, self.seen = plan, []

    def generate_content(self, *, model: str, contents: Any, config: Any) -> Any:
        self.seen.append((model, contents, config))
        outcome = self.plan[model]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def llm_with(plan: dict[str, Any], models: list[str]) -> tuple[GeminiLLM, StubModels]:
    stub = StubModels(plan)
    return GeminiLLM(SimpleNamespace(models=stub), ModelChain(models)), stub


def test_schema_cleaner_drops_keys_gemini_rejects() -> None:
    raw = {
        "title": "X",
        "type": "object",
        "additionalProperties": False,
        "properties": {"a": {"title": "A", "type": "string"}},
        "$defs": {"y": {}},
    }
    assert clean_schema(raw) == {"type": "object", "properties": {"a": {"type": "string"}}}


def test_every_tool_schema_survives_cleaning_with_its_fields() -> None:
    names = {s.name for s in specs()}
    assert names == set(TOOLS) == {"search_documents", "read_chunks", "query_invoices"}
    for s in specs():
        cleaned = clean_schema(s.parameters)
        assert "additionalProperties" not in str(cleaned) and "title" not in str(cleaned)
        assert cleaned["properties"], s.name
    assert "org_id" not in str(specs())  # the model is never even told the field exists


def test_messages_become_gemini_contents() -> None:
    user = _to_content(Message("user", "hello"))
    assert user.role == "user" and user.parts[0].text == "hello"
    calls = _to_content(
        Message("assistant", "", (ToolCall("search_documents", {"query": "q"}, "c1"),))
    )
    assert calls.role == "model" and calls.parts[0].function_call.name == "search_documents"
    result = _to_content(
        Message("tool", tool_results=(ToolResult("search_documents", "found", "c1"),))
    )
    fr = result.parts[0].function_response
    assert (
        result.role == "user"
        and fr.name == "search_documents"
        and fr.response == {"result": "found"}
    )
    err = _to_content(Message("tool", tool_results=(ToolResult("x", "bad", None, True),)))
    assert err.parts[0].function_response.response == {"error": "bad"}


def test_raw_model_content_is_replayed_verbatim() -> None:
    raw = types.Content(role="model", parts=[types.Part(text="hi", thought_signature=b"sig")])
    assert _to_content(Message("assistant", "hi", raw=raw)) is raw  # keeps thought signatures


def test_parse_separates_text_calls_thoughts_and_counts_tokens() -> None:
    parts = [
        types.Part(text="private reasoning", thought=True),
        types.Part(text="Answer [C1]"),
        types.Part(
            function_call=types.FunctionCall(name="read_chunks", args={"refs": ["C1"]}, id="9")
        ),
    ]
    r = parse_response(response(parts), "m1")
    assert r.text == "Answer [C1]"  # the model's thoughts are not shown to users
    assert r.tool_calls == (ToolCall("read_chunks", {"refs": ["C1"]}, "9"),)
    assert (r.usage.prompt_tokens, r.usage.completion_tokens) == (11, 7)  # output + thinking
    assert r.model == "m1" and r.raw is not None


def test_parse_rejects_blocked_or_empty_responses() -> None:
    with pytest.raises(LLMError):
        parse_response(SimpleNamespace(candidates=[], prompt_feedback="blocked"), "m")


async def test_generate_disables_auto_function_calling_and_declares_tools() -> None:
    llm, stub = llm_with({"m1": response([types.Part(text="ok")])}, ["m1"])
    spec = ToolSpec("t", "d", {"type": "object", "properties": {}, "title": "T"})
    await llm.generate("sys", [Message("user", "q")], [spec])
    _, contents, cfg = stub.seen[0]
    assert cfg.automatic_function_calling.disable is True
    assert cfg.temperature == 0 and cfg.system_instruction == "sys"
    decl = cfg.tools[0].function_declarations[0]
    assert decl.name == "t" and "title" not in str(decl.parameters_json_schema)
    assert contents[0].parts[0].text == "q"


async def test_generate_falls_over_to_the_next_model_and_reports_it() -> None:
    quota = errors.APIError(429, {"error": {"message": DAILY}})
    llm, stub = llm_with({"m1": quota, "m2": response([types.Part(text="from m2")])}, ["m1", "m2"])
    r = await llm.generate("s", [Message("user", "q")], [])
    assert r.model == "m2" and r.text == "from m2"
    assert [m for m, *_ in stub.seen] == ["m1", "m2"]
    await llm.generate("s", [Message("user", "q")], [])
    assert [m for m, *_ in stub.seen][2:] == ["m2"]  # m1 is not retried while exhausted


async def test_generate_raises_clearly_when_every_model_is_exhausted() -> None:
    quota = errors.APIError(429, {"error": {"message": DAILY}})
    llm, _ = llm_with({"m1": quota, "m2": quota}, ["m1", "m2"])
    with pytest.raises(LLMUnavailable):
        await llm.generate("s", [Message("user", "q")], [])
