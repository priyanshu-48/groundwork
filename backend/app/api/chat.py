"""POST /chat/{conversation_id}/messages: the agent's run as a Server-Sent Events stream.

Errors that can be known up front (auth, unknown conversation, bad body, chat not configured) are
ordinary HTTP errors. Once streaming starts the stream always ends with a "done" event (the loop
turns model outages into done/status=error), or an "error" event if something unexpected breaks."""

import json
import logging
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agent.service import ConversationNotFound, ask
from app.api.deps import current_user
from app.repositories import conversations
from app.services.ratelimit import Limits, get_limits, too_many
from app.services.security import Principal
from app.worker.deps import Deps

log = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])

# The final 'done' event also carries these for persistence; clients already received them as
# their own events, so they are not sent twice.
_DONE_OMIT = {"answer", "citations", "steps"}


class MessageIn(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


def sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@router.post("/chat/{conversation_id}/messages")
async def send(
    conversation_id: uuid.UUID,
    body: MessageIn,
    request: Request,
    p: Principal = Depends(current_user),
    limits: Limits = Depends(get_limits),
) -> StreamingResponse:
    deps: Deps | None = getattr(request.app.state, "agent_deps", None)
    if deps is None or deps.llm is None:
        raise HTTPException(503, "Chat is not configured on this server")
    async with deps.maker() as session:
        only = p.user_id if p.demo else None  # demo visitors only reach their own conversations
        if await conversations.get_conversation(session, p.org_id, conversation_id, only) is None:
            raise HTTPException(404, "Conversation not found")
        if p.demo:
            cap = deps.settings.demo_daily_chat_cap
            since = datetime.now(UTC) - timedelta(hours=24)
            if await conversations.count_questions_since(session, p.org_id, since) >= cap:
                raise HTTPException(
                    429,
                    "The demo has reached its daily question limit. Try again tomorrow, "
                    "or ask for an invite code to use your own workspace.",
                    headers={"Retry-After": "3600"},
                )

    key = str(p.org_id)
    if (wait := limits.chat.check(key)) is not None:
        raise too_many(wait, "questions")
    slot = limits.chat_concurrent.acquire(key)
    if slot is None:
        raise too_many(2, "questions at once")

    async def stream() -> AsyncIterator[str]:
        try:
            async for ev in ask(deps, p.org_id, conversation_id, body.content, stream=True):
                data = ev.data
                if ev.type == "done":
                    data = {k: v for k, v in data.items() if k not in _DONE_OMIT}
                yield sse(ev.type, data)
        except ConversationNotFound:
            yield sse("error", {"message": "Conversation not found"})
        except Exception:
            log.exception("chat stream failed")
            yield sse("error", {"message": "Something went wrong while answering"})
        finally:
            limits.chat_concurrent.release(key, slot)  # also runs when the client disconnects

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
