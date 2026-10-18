import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
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
    session: AsyncSession,
    org_id: uuid.UUID,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
) -> Conversation | None:
    """user_id narrows to one user's conversations (demo visitors share an org, not chats)."""
    stmt = select(Conversation).where(
        Conversation.id == conversation_id, Conversation.org_id == org_id
    )
    if user_id is not None:
        stmt = stmt.where(Conversation.user_id == user_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def history(
    session: AsyncSession,
    org_id: uuid.UUID,
    conversation_id: uuid.UUID,
    limit: int = 20,
    user_id: uuid.UUID | None = None,
) -> list[Message]:
    """Oldest-first text history of a conversation; empty if it belongs to another org."""
    stmt = (
        select(Message)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(Conversation.id == conversation_id, Conversation.org_id == org_id)
        .order_by(Message.created_at.desc(), Message.id)
        .limit(limit)
    )
    if user_id is not None:
        stmt = stmt.where(Conversation.user_id == user_id)
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
            evidence=s.get("evidence"),
        )
        for s in steps
    )
    await session.flush()
    return run


async def list_conversations(
    session: AsyncSession, org_id: uuid.UUID, limit: int = 50, user_id: uuid.UUID | None = None
) -> list[Conversation]:
    stmt = (
        select(Conversation)
        .where(Conversation.org_id == org_id)
        .order_by(Conversation.created_at.desc(), Conversation.id)
        .limit(limit)
    )
    if user_id is not None:
        stmt = stmt.where(Conversation.user_id == user_id)
    return list((await session.execute(stmt)).scalars().all())


async def runs_for_messages(
    session: AsyncSession, message_ids: list[uuid.UUID]
) -> dict[uuid.UUID, dict[str, Any]]:
    """Agent run summary and tool steps per assistant message, so history can show what the agent
    did. Callers pass ids of messages they already scoped to an org."""
    if not message_ids:
        return {}
    runs = (
        (await session.execute(select(AgentRun).where(AgentRun.message_id.in_(message_ids))))
        .scalars()
        .all()
    )
    steps = (
        (
            await session.execute(
                select(AgentStep)
                .where(AgentStep.run_id.in_([r.id for r in runs]))
                .order_by(AgentStep.run_id, AgentStep.step_no)
            )
        )
        .scalars()
        .all()
    )
    out: dict[uuid.UUID, dict[str, Any]] = {}
    for r in runs:
        out[r.message_id] = {"model": r.model, "latency_ms": r.latency_ms, "steps": []}
    by_run = {r.id: r.message_id for r in runs}
    for st in steps:
        out[by_run[st.run_id]]["steps"].append(
            {
                "step_no": st.step_no,
                "tool": st.tool_name,
                "args": st.args,
                "status": "ok",  # failed calls are not distinguished in storage; the preview says
                "latency_ms": st.latency_ms,
                "preview": st.result_preview,
                **({"evidence": st.evidence} if st.evidence is not None else {}),
            }
        )
    return out


async def count_questions_since(session: AsyncSession, org_id: uuid.UUID, since: datetime) -> int:
    """User messages in an org since a time: the demo's daily budget, counted from the database
    so it survives restarts and covers every visitor."""
    stmt = (
        select(func.count())
        .select_from(Message)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(
            Conversation.org_id == org_id,
            Message.role == MessageRole.user,
            Message.created_at >= since,
        )
    )
    return int((await session.execute(stmt)).scalar_one())
