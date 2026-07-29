from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


INTERNAL_MESSAGE_MAX_LENGTH = 32_000
CLIENT_MESSAGE_MAX_LENGTH = 8_000


class ChatMessage(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=INTERNAL_MESSAGE_MAX_LENGTH)


class ClientChatMessage(BaseModel):
    """A message accepted from the public chat API."""

    model_config = ConfigDict(str_strip_whitespace=True)

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=CLIENT_MESSAGE_MAX_LENGTH)


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    messages: list[ClientChatMessage] = Field(min_length=1, max_length=50)
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
    language: Literal["zh", "en", "es", "fr", "de", "ja", "id", "ru"]


class ChatResponse(BaseModel):
    id: str
    conversation_id: str
    message: ChatMessage
    model: str
    created_at: str
    knowledge_domain: Literal["ausome", "oilseals"] | None = None
    sources: list[ChatSource] = Field(default_factory=list)
    agent_intent: Literal[
        "general",
        "company_product_qa",
        "technical_qa",
        "product_selection",
        "quotation",
        "human_handoff",
    ]
    agent_stage: Literal[
        "respond",
        "collect_requirements",
        "prepare_inquiry",
    ]

    @classmethod
    def create(
        cls,
        *,
        message: ChatMessage,
        conversation_id: str,
        model: str,
        knowledge_domain: Literal["ausome", "oilseals"] | None = None,
        sources: list[ChatSource] | None = None,
        agent_intent: str,
        agent_stage: str,
    ) -> "ChatResponse":
        return cls(
            id=str(uuid4()),
            conversation_id=conversation_id,
            message=message,
            model=model,
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            knowledge_domain=knowledge_domain,
            sources=sources or [],
            agent_intent=agent_intent,
            agent_stage=agent_stage,
        )
