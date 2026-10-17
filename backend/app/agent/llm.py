"""Provider-neutral LLM interface for the agent loop, plus the Gemini adapter and a scripted fake.

The loop only knows Message / ToolCall / LLMResponse. Everything Gemini-specific (Content parts,
thought signatures, JSON-schema cleanup, the model fallback chain) stays in GeminiLLM."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
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


class LLM(Protocol):
    async def generate(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> LLMResponse: ...


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

    async def generate(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> LLMResponse:
        contents = [_to_content(m) for m in messages]
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
