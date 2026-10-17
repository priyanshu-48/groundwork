import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, StringConstraints
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user, get_session
from app.repositories import conversations
from app.services.security import Principal

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationIn(BaseModel):
    title: Annotated[str, StringConstraints(max_length=200)] | None = None


class ConversationOut(BaseModel):
    id: uuid.UUID
    title: str | None
    created_at: datetime


class MessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    citations: list[dict[str, Any]] | None
    created_at: datetime
    model: str | None = None
    steps: list[dict[str, Any]] | None = None


@router.post("", response_model=ConversationOut, status_code=201)
async def create(
    body: ConversationIn,
    p: Principal = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> object:
    conv = await conversations.create_conversation(session, p.org_id, p.user_id, body.title)
    await session.commit()
    return conv


@router.get("", response_model=list[ConversationOut])
async def list_(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    p: Principal = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> object:
    return await conversations.list_conversations(session, p.org_id, limit)


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def history(
    conversation_id: uuid.UUID,
    p: Principal = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> object:
    if await conversations.get_conversation(session, p.org_id, conversation_id) is None:
        raise HTTPException(404, "Conversation not found")
    msgs = await conversations.history(session, p.org_id, conversation_id, limit=200)
    runs = await conversations.runs_for_messages(session, [m.id for m in msgs])
    return [
        MessageOut(
            id=m.id,
            role=m.role.value,
            content=m.content,
            citations=m.citations,
            created_at=m.created_at,
            model=runs.get(m.id, {}).get("model"),
            steps=runs[m.id]["steps"] if m.id in runs else None,
        )
        for m in msgs
    ]
