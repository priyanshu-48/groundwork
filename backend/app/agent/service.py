"""Run the agent for a conversation and persist the outcome (message, run, steps)."""

import uuid
from collections.abc import AsyncIterator

from app.agent.llm import LLM, Message
from app.agent.loop import AgentEvent, run_agent
from app.agent.tools import AgentContext
from app.models.agent import MessageRole, RunStatus
from app.repositories import conversations
from app.worker.deps import Deps

HISTORY_LIMIT = 20


class ConversationNotFound(Exception):
    pass


def make_context(deps: Deps, org_id: uuid.UUID) -> AgentContext:
    return AgentContext(
        org_id=org_id,
        maker=deps.maker,
        embedder=deps.embedder,
        settings=deps.settings,
        reranker=deps.reranker,
    )


async def ask(
    deps: Deps,
    org_id: uuid.UUID,
    conversation_id: uuid.UUID,
    question: str,
    llm: LLM | None = None,
    *,
    stream: bool = False,
) -> AsyncIterator[AgentEvent]:
    """Yield the loop's events; after the last one, the run is stored and 'done' carries its ids.

    org_id must come from the verified token (never from the request body or the model)."""
    llm = llm or deps.llm
    if llm is None:
        raise RuntimeError("no LLM configured (AI_PROVIDER=fake needs an explicit FakeLLM)")
    async with deps.maker.begin() as session:
        conv = await conversations.get_conversation(session, org_id, conversation_id)
        if conv is None:
            raise ConversationNotFound(str(conversation_id))
        past = await conversations.history(session, org_id, conversation_id, HISTORY_LIMIT)
        history = [Message(m.role.value, m.content) for m in past]  # plain text, no tool traffic
        await conversations.add_message(session, conversation_id, MessageRole.user, question)
        if conv.title is None:  # the sidebar needs something to show
            conv.title = " ".join(question.split())[:60]

    done: AgentEvent | None = None
    async for event in run_agent(make_context(deps, org_id), llm, question, history, stream=stream):
        if event.type == "done":
            done = event
        else:
            yield event
    assert done is not None
    d = done.data

    async with deps.maker.begin() as session:
        msg = await conversations.add_message(
            session, conversation_id, MessageRole.assistant, d["answer"], d["citations"]
        )
        run = await conversations.record_run(
            session,
            msg.id,
            model=d["model"],
            prompt_tokens=d["prompt_tokens"],
            completion_tokens=d["completion_tokens"],
            latency_ms=d["latency_ms"],
            status=RunStatus(d["status"]),
            error=d["error"],
            steps=d["steps"],
        )
    yield AgentEvent("done", {**d, "message_id": str(msg.id), "run_id": str(run.id)})
