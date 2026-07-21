from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChatMessage(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=8_000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    messages: list[ChatMessage] = Field(min_length=1, max_length=50)
    conversation_id: str = Field(
        default_factory=lambda: str(uuid4()), min_length=1, max_length=128
    )

    @model_validator(mode="after")
    def require_user_message(self) -> "ChatRequest":
        if not any(message.role == "user" for message in self.messages):
            raise ValueError("at least one user message is required")
        return self


class ChatSource(BaseModel):
    source: str
    page: int
    domain: Literal["ausome", "oilseals"]
    language: Literal["zh", "en"]


class ChatResponse(BaseModel):
    id: str
    conversation_id: str
    message: ChatMessage
    model: str
    created_at: str
    knowledge_domain: Literal["ausome", "oilseals"] | None = None
    sources: list[ChatSource] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        *,
        message: ChatMessage,
        conversation_id: str,
        model: str,
        knowledge_domain: Literal["ausome", "oilseals"] | None = None,
        sources: list[ChatSource] | None = None,
    ) -> "ChatResponse":
        return cls(
            id=str(uuid4()),
            conversation_id=conversation_id,
            message=message,
            model=model,
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            knowledge_domain=knowledge_domain,
            sources=sources or [],
        )
