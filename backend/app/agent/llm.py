"""Provider-neutral LLM interface for the agent loop, plus the Gemini adapter and a scripted fake.

The loop only knows Message / ToolCall / LLMResponse. Everything Gemini-specific (Content parts,
thought signatures, JSON-schema cleanup, the model fallback chain) stays in GeminiLLM."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Literal, Protocol

from google.genai import types

from app.services.gemini import ModelChain, Throttle, call_with_retry


class LLMError(Exception):
    """The model returned nothing usable (blocked, empty candidates)."""


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]
    id: str | None = None


@dataclass(frozen=True)
class ToolResult:
    name: str
    text: str
    call_id: str | None = None
    is_error: bool = False


@dataclass(frozen=True)
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0


@dataclass(frozen=True)
class Message:
    role: Literal["user", "assistant", "tool"]
    text: str = ""
    tool_calls: tuple[ToolCall, ...] = ()
    tool_results: tuple[ToolResult, ...] = ()
    raw: Any = None  # provider-native content to replay verbatim (keeps Gemini thought signatures)


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class LLMResponse:
    text: str = ""
    tool_calls: tuple[ToolCall, ...] = ()
    usage: Usage = field(default_factory=Usage)
    model: str = "fake-model"
    raw: Any = None


StreamItem = str | LLMResponse  # text deltas as they arrive, then exactly one final LLMResponse


class LLM(Protocol):
    async def generate(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> LLMResponse: ...

    # Optional: providers that can stream also provide
    #   generate_stream(system, messages, tools) -> AsyncIterator[StreamItem]


# ------------------------------------------------------------------ fake

Step = LLMResponse | Callable[[list[Message]], LLMResponse]


def say(text: str) -> LLMResponse:
    return LLMResponse(text=text, usage=Usage(10, 5))


def call(name: str, **args: Any) -> LLMResponse:
    return LLMResponse(tool_calls=(ToolCall(name, args, id=f"call-{name}"),), usage=Usage(10, 5))


class FakeLLM:
    """Plays back a script, one entry per generate() call. An entry may be a function of the
    conversation so far, which lets a test cite whatever refs the tools actually returned."""

    def __init__(self, script: list[Step], model: str = "fake-model") -> None:
        self._script = list(script)
        self._model = model
        self.calls: list[list[Message]] = []

    async def generate(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> LLMResponse:
        self.calls.append(list(messages))
        if not self._script:
            raise AssertionError("FakeLLM script exhausted: the loop asked for more calls")
        step = self._script.pop(0)
        resp = step(messages) if callable(step) else step
        return LLMResponse(resp.text, resp.tool_calls, resp.usage, self._model, resp.raw)

    async def generate_stream(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> AsyncIterator[StreamItem]:
        """Same script as generate(), with the text released in small pieces like a real stream."""
        resp = await self.generate(system, messages, tools)
        for i in range(0, len(resp.text), 8):
            yield resp.text[i : i + 8]
        yield resp


# ---------------------------------------------------------------- gemini


def clean_schema(node: Any) -> Any:
    """Drop JSON-schema keys Gemini's function declarations do not accept."""
    if isinstance(node, dict):
        return {
            k: clean_schema(v)
            for k, v in node.items()
            if k not in ("title", "additionalProperties", "$defs")
        }
    if isinstance(node, list):
        return [clean_schema(v) for v in node]
    return node


def _to_content(m: Message) -> types.Content:
    if m.role == "assistant" and m.raw is not None:
        return m.raw  # type: ignore[no-any-return]
    if m.role == "user":
        return types.Content(role="user", parts=[types.Part.from_text(text=m.text)])
    if m.role == "assistant":
        parts = [types.Part.from_text(text=m.text)] if m.text else []
        parts += [
            types.Part(function_call=types.FunctionCall(name=c.name, args=c.args, id=c.id))
            for c in m.tool_calls
        ]
        return types.Content(role="model", parts=parts)
    return types.Content(
        role="user",
        parts=[
            types.Part(
                function_response=types.FunctionResponse(
                    id=r.call_id,
                    name=r.name,
                    response={"error": r.text} if r.is_error else {"result": r.text},
                )
            )
            for r in m.tool_results
        ],
    )


class GeminiLLM:
    """Function calling with automatic execution switched off: our loop decides what runs, with
    validated arguments and the server's org_id."""

    def __init__(
        self,
        client: Any,
        chain: ModelChain,
        throttle: Throttle | None = None,
        max_tries: int = 3,
    ) -> None:
        self._client, self._chain, self._throttle, self._max_tries = (
            client,
            chain,
            throttle,
            max_tries,
        )

    def _request(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> tuple[list[types.Content], types.GenerateContentConfig]:
        decls = [
            types.FunctionDeclaration(
                name=t.name,
                description=t.description,
                parameters_json_schema=clean_schema(t.parameters),
            )
            for t in tools
        ]
        cfg = types.GenerateContentConfig(
            system_instruction=system,
            tools=[types.Tool(function_declarations=decls)],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            temperature=0,
        )
        return [_to_content(m) for m in messages], cfg

    async def generate(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> LLMResponse:
        contents, cfg = self._request(system, messages, tools)
        if self._throttle:
            await self._throttle.wait()
        model, resp = await self._chain.run(
            lambda m: call_with_retry(
                lambda: self._client.models.generate_content(
                    model=m, contents=contents, config=cfg
                ),
                max_tries=self._max_tries,
            )
        )
        return parse_response(resp, model)

    async def generate_stream(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> AsyncIterator[StreamItem]:
        """Yield text deltas as the model produces them, then the assembled LLMResponse.

        The stream is opened (first chunk fetched) inside the model chain, so a quota or overload
        error at the start still falls over to the next model. An error after text has started
        propagates: switching models mid-answer would splice two answers together."""
        contents, cfg = self._request(system, messages, tools)
        if self._throttle:
            await self._throttle.wait()

        def open_stream(model: str) -> tuple[Any, Any]:
            it = iter(
                self._client.models.generate_content_stream(
                    model=model, contents=contents, config=cfg
                )
            )
            return it, next(it, None)  # the HTTP request happens on the first next()

        model, (it, first) = await self._chain.run(
            lambda m: call_with_retry(lambda: open_stream(m), max_tries=self._max_tries)
        )
        chunks: list[Any] = []
        chunk = first
        while chunk is not None:
            chunks.append(chunk)
            for cand in chunk.candidates or []:
                for part in (cand.content.parts if cand.content else None) or []:
                    if part.text and not part.thought:
                        yield part.text
            chunk = await asyncio.to_thread(next, it, None)
        yield assemble_stream(chunks, model)


def assemble_stream(chunks: list[Any], model: str) -> LLMResponse:
    """One response from many chunks. Parts are kept in arrival order (function calls and thought
    signatures included) so the next turn can replay the model's own content verbatim."""
    parts = [
        p
        for c in chunks
        for cand in (c.candidates or [])[:1]
        for p in (cand.content.parts if cand.content else None) or []
    ]
    usage = next((c.usage_metadata for c in reversed(chunks) if c.usage_metadata), None)
    merged = SimpleNamespace(
        candidates=[SimpleNamespace(content=types.Content(role="model", parts=parts))]
        if parts
        else [],
        usage_metadata=usage,
        prompt_feedback=chunks[-1].prompt_feedback if chunks else None,
    )
    return parse_response(merged, model)


def parse_response(resp: Any, model: str) -> LLMResponse:
    candidates = resp.candidates or []
    if not candidates or candidates[0].content is None:
        reason = (
            candidates[0].finish_reason if candidates else getattr(resp, "prompt_feedback", None)
        )
        raise LLMError(f"model returned no content ({reason})")
    content = candidates[0].content
    text = "".join(p.text for p in content.parts or [] if p.text and not p.thought)
    calls = tuple(
        ToolCall(p.function_call.name, dict(p.function_call.args or {}), p.function_call.id)
        for p in content.parts or []
        if p.function_call
    )
    u = resp.usage_metadata
    usage = Usage(
        (u.prompt_token_count or 0) if u else 0,
        ((u.candidates_token_count or 0) + (u.thoughts_token_count or 0)) if u else 0,
    )
    return LLMResponse(text=text, tool_calls=calls, usage=usage, model=model, raw=content)
