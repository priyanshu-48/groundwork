import enum
import uuid
from typing import Any

from sqlalchemy import Enum, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin


class MessageRole(enum.StrEnum):
    user = "user"
    assistant = "assistant"


class RunStatus(enum.StrEnum):
    ok = "ok"
    error = "error"
    max_steps = "max_steps"


class Conversation(IdMixin, Base):
    __tablename__ = "conversations"
    __table_args__ = (Index("ix_conversations_org", "org_id"),)

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orgs.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str | None]


class Message(IdMixin, Base):
    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_conversation", "conversation_id", "created_at"),)

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole, name="message_role"))
    content: Mapped[str] = mapped_column(Text)
    citations: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)


class AgentRun(IdMixin, Base):
    __tablename__ = "agent_runs"

    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"))
    model: Mapped[str | None]  # the model that actually answered (the chain may have fallen over)
    prompt_tokens: Mapped[int] = mapped_column(default=0)
    completion_tokens: Mapped[int] = mapped_column(default=0)
    latency_ms: Mapped[int] = mapped_column(default=0)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus, name="run_status"))
    error: Mapped[str | None] = mapped_column(Text)


class AgentStep(IdMixin, Base):
    __tablename__ = "agent_steps"
    __table_args__ = (Index("ix_agent_steps_run", "run_id", "step_no"),)

    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_runs.id", ondelete="CASCADE"))
    step_no: Mapped[int]
    tool_name: Mapped[str]
    args: Mapped[dict[str, Any]] = mapped_column(JSONB)
    result_preview: Mapped[str] = mapped_column(Text)
    latency_ms: Mapped[int] = mapped_column(default=0)
