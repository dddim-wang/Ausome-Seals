import os
from collections.abc import Iterator
from dataclasses import dataclass

from app.ai.providers import AIProvider, DeepSeekProvider, StubAIProvider
from app.models import ChatMessage, ChatRequest, ChatResponse, ChatSource
from app.rag import RagContext, RagService
from app.rag.service import create_rag_service


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AIStream:
    chunks: Iterator[str]
    rag_context: RagContext | None


class AIService:
    def __init__(self, provider: AIProvider, rag_service: RagService | None = None):
        self.provider = provider
        self.rag_service = rag_service

    def _prepare(self, chat_request: ChatRequest) -> tuple[list[ChatMessage], RagContext | None]:
        messages = list(chat_request.messages)
        if self.rag_service is None:
            return messages, None
        user_messages = [message.content for message in messages if message.role == "user"]
        if not user_messages:
            return messages, None
        latest_question = user_messages[-1]
        conversation_context = "\n".join(user_messages[-3:-1])
        rag_context = self.rag_service.retrieve(latest_question, conversation_context)
        if rag_context is None:
            return messages, None
        return [ChatMessage(role="system", content=rag_context.prompt), *messages], rag_context

    @staticmethod
    def _sources(rag_context: RagContext | None) -> list[ChatSource]:
        if rag_context is None:
            return []
        return [ChatSource(**source.__dict__) for source in rag_context.sources]

    def chat(self, chat_request: ChatRequest) -> ChatResponse:
        messages, rag_context = self._prepare(chat_request)
        content = self.provider.generate(messages)
        return ChatResponse.create(
            message=ChatMessage(role="assistant", content=content),
            conversation_id=chat_request.conversation_id,
            model=self.provider.model,
            knowledge_domain=rag_context.domain if rag_context else None,
            sources=self._sources(rag_context),
        )

    def stream(self, chat_request: ChatRequest) -> AIStream:
        messages, rag_context = self._prepare(chat_request)
        return AIStream(self.provider.stream(messages), rag_context)


def create_ai_service() -> AIService:
    provider_name = os.getenv("AI_PROVIDER", "stub").strip().lower()
    rag_enabled = _env_bool("RAG_ENABLED", provider_name != "stub")
    rag_service = create_rag_service() if rag_enabled else None

    if provider_name == "stub":
        return AIService(StubAIProvider(), rag_service)
    if provider_name == "deepseek":
        return AIService(DeepSeekProvider(
            api_key=os.getenv("DEEPSEEK_API_KEY", "").strip(),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro").strip(),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip(),
            timeout_seconds=float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "60")),
            thinking_enabled=_env_bool("DEEPSEEK_THINKING_ENABLED", False),
        ), rag_service)

    raise RuntimeError(f"Unsupported AI_PROVIDER: {provider_name}")
