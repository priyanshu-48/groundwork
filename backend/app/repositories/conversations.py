import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import AgentRun, AgentStep, Conversation, Message, MessageRole, RunStatus


async def create_conversation(
    session: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, title: str | None = None
) -> Conversation:
    conv = Conversation(org_id=org_id, user_id=user_id, title=title)
    session.add(conv)
    await session.flush()
    return conv


async def get_conversation(
    session: AsyncSession, org_id: uuid.UUID, conversation_id: uuid.UUID
) -> Conversation | None:
    stmt = select(Conversation).where(
        Conversation.id == conversation_id, Conversation.org_id == org_id
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def history(
    session: AsyncSession, org_id: uuid.UUID, conversation_id: uuid.UUID, limit: int = 20
) -> list[Message]:
    """Oldest-first text history of a conversation; empty if it belongs to another org."""
    stmt = (
        select(Message)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(Conversation.id == conversation_id, Conversation.org_id == org_id)
        .order_by(Message.created_at.desc(), Message.id)
        .limit(limit)
    )
    return list(reversed((await session.execute(stmt)).scalars().all()))


async def add_message(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    role: MessageRole,
    content: str,
    citations: list[dict[str, Any]] | None = None,
) -> Message:
    msg = Message(conversation_id=conversation_id, role=role, content=content, citations=citations)
    session.add(msg)
    await session.flush()
    return msg


async def record_run(
    session: AsyncSession,
    message_id: uuid.UUID,
    *,
    model: str | None,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: int,
    status: RunStatus,
    error: str | None,
    steps: list[dict[str, Any]],
) -> AgentRun:
    run = AgentRun(
        message_id=message_id,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        status=status,
        error=error,
    )
    session.add(run)
    await session.flush()
    session.add_all(
        AgentStep(
            run_id=run.id,
            step_no=s["step_no"],
            tool_name=s["tool"],
            args=s["args"],
            result_preview=s["preview"],
            latency_ms=s["latency_ms"],
        )
        for s in steps
    )
    await session.flush()
    return run
