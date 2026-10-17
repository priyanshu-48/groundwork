"""The hand-written agent loop (SPEC 6.5): ask the model, run the tools it requests, repeat.

run_agent() is an async generator of events so a streaming API (M7) can forward them as they
happen. The last event is always "done" and carries everything needed to persist the run."""

import re
import time
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass, field
from typing import Any

from app.agent.llm import LLM, LLMError, Message, ToolResult, Usage
from app.agent.prompts import SYSTEM
from app.agent.tools import AgentContext, execute, specs
from app.services.gemini import LLMUnavailable

_BRACKET = re.compile(r"\[([^\[\]]*)\]")
_REF = re.compile(r"^C\d+$")


@dataclass(frozen=True)
class AgentEvent:
    type: str  # step | answer | citations | done
    data: dict[str, Any] = field(default_factory=dict)


def snippet(text: str, n: int = 200) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= n else flat[:n] + "..."


def validate_citations(answer: str, ctx: AgentContext) -> tuple[str, list[dict[str, Any]], int]:
    """Keep only citations that point at chunks this run really retrieved.

    The model writes refs like [C1] or [C1, C2]. Anything else it invents (C99, a UUID, a filename
    in brackets that looks like a ref) is removed from the text and counted, so a hallucinated
    source can never be shown to the user as if it were real."""
    seen: list[str] = []
    dropped = 0

    def fix(m: re.Match[str]) -> str:
        nonlocal dropped
        tokens = [t for t in re.split(r"[,\s]+", m.group(1).strip()) if t]
        if not tokens or not all(_REF.match(t) for t in tokens):
            return m.group(0)  # ordinary brackets, not a citation
        good = [t for t in tokens if t in ctx.refs]
        dropped += len(tokens) - len(good)
        seen.extend(t for t in good if t not in seen)
        return f"[{', '.join(good)}]" if good else ""

    cleaned = re.sub(r"\s+([.,;:])", r"\1", _BRACKET.sub(fix, answer)).strip()
    citations = [
        {
            "ref": r,
            "chunk_id": str(ctx.refs[r].chunk_id),
            "document_id": str(ctx.refs[r].document_id),
            "filename": ctx.refs[r].filename,
            "page": ctx.refs[r].page,
            "snippet": snippet(ctx.refs[r].content),
        }
        for r in seen
    ]
    return cleaned, citations, dropped


def _step_limit_answer(ctx: AgentContext) -> tuple[str, list[dict[str, Any]]]:
    shown = list(ctx.refs)[:5]
    lines = [
        f"- [{r}] {ctx.refs[r].filename} p.{ctx.refs[r].page}: {snippet(ctx.refs[r].content, 150)}"
        for r in shown
    ]
    text = (
        "I couldn't complete this within the step limit. Here is what I found so far:\n"
        + "\n".join(lines)
    )
    return validate_citations(text, ctx)[:2]


async def run_agent(
    ctx: AgentContext,
    llm: LLM,
    question: str,
    history: Sequence[Message] = (),
    *,
    max_steps: int | None = None,
) -> AsyncIterator[AgentEvent]:
    limit = max_steps or ctx.settings.agent_max_steps
    messages: list[Message] = [*history, Message("user", question)]
    started = time.perf_counter()
    usage = Usage()
    model: str | None = None
    steps: list[dict[str, Any]] = []
    status, error, answer = "ok", None, ""
    citations: list[dict[str, Any]] = []
    dropped = 0

    try:
        for _ in range(limit):
            resp = await llm.generate(SYSTEM, messages, specs())
            usage = Usage(
                usage.prompt_tokens + resp.usage.prompt_tokens,
                usage.completion_tokens + resp.usage.completion_tokens,
            )
            model = resp.model
            if resp.tool_calls:
                messages.append(Message("assistant", resp.text, resp.tool_calls, raw=resp.raw))
                results: list[ToolResult] = []
                for tc in resp.tool_calls:
                    n = len(steps) + 1
                    yield AgentEvent(
                        "step",
                        {"step_no": n, "tool": tc.name, "args": tc.args, "status": "running"},
                    )
                    t0 = time.perf_counter()
                    out = await execute(ctx, tc.name, tc.args)
                    ms = int((time.perf_counter() - t0) * 1000)
                    steps.append(
                        {
                            "step_no": n,
                            "tool": tc.name,
                            "args": tc.args,
                            "preview": out.preview[:500],
                            "latency_ms": ms,
                        }
                    )
                    yield AgentEvent(
                        "step",
                        {
                            "step_no": n,
                            "tool": tc.name,
                            "args": tc.args,
                            "status": "error" if out.is_error else "ok",
                            "latency_ms": ms,
                            "preview": out.preview[:500],
                        },
                    )
                    results.append(ToolResult(tc.name, out.text, tc.id, out.is_error))
                messages.append(Message("tool", tool_results=tuple(results)))
                continue
            if not resp.text.strip():
                raise LLMError("model returned an empty answer")
            answer, citations, dropped = validate_citations(resp.text, ctx)
            break
        else:
            status = "max_steps"
            answer, citations = _step_limit_answer(ctx)
    except (LLMUnavailable, LLMError) as e:
        status, error = "error", f"{type(e).__name__}: {e}"
        answer = (
            "I couldn't get an answer from the language model right now. Please try again later."
        )
        citations = []

    yield AgentEvent("answer", {"text": answer})
    yield AgentEvent("citations", {"items": citations})
    yield AgentEvent(
        "done",
        {
            "status": status,
            "error": error,
            "model": model,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "answer": answer,
            "citations": citations,
            "dropped_citations": dropped,
            "steps": steps,
        },
    )
