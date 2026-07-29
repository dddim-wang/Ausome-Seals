import logging
import os
import re
from collections.abc import Iterator
from dataclasses import dataclass

from app.agent import AgentOrchestrator, AgentPlan
from app.ai.providers import AIProvider, DeepSeekProvider, StubAIProvider
from app.models import ChatMessage, ChatRequest, ChatResponse, ChatSource
from app.rag import RagContext, RagService
from app.rag.service import create_rag_service


logger = logging.getLogger(__name__)

_CITATION_RE = re.compile(
    r"\[[^\]\r\n]*?\.pdf\s+(?:p\.?|page)\s*\d+\]",
    re.IGNORECASE,
)
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+", re.MULTILINE)


def sanitize_assistant_text(content: str) -> str:
    content = content.replace("**", "")
    content = _HEADING_RE.sub("", content)
    content = _CITATION_RE.sub("", content)
    return re.sub(r"\n{3,}", "\n\n", content)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AIStream:
    chunks: Iterator[str]
    rag_context: RagContext | None
    agent_intent: str
    agent_stage: str


class AIService:
    def __init__(
        self,
        provider: AIProvider,
        rag_service: RagService | None = None,
        orchestrator: AgentOrchestrator | None = None,
    ):
        self.provider = provider
        self.orchestrator = orchestrator or AgentOrchestrator(rag_service)

    @staticmethod
    def _provider_messages(plan: AgentPlan) -> list[ChatMessage]:
        system_contents = []
        first_non_system = 0
        for index, message in enumerate(plan.messages):
            if message.role != "system":
                first_non_system = index
                break
            system_contents.append(message.content)
        else:
            first_non_system = len(plan.messages)

        return [
            ChatMessage(role="system", content="\n\n".join(system_contents)),
            *plan.messages[first_non_system:],
        ]

    @staticmethod
    def _sources(rag_context: RagContext | None) -> list[ChatSource]:
        if rag_context is None:
            return []
        return [
            ChatSource(
                source=reference.source,
                page=reference.page,
                domain=reference.domain,
                language=reference.language,
            )
            for reference in rag_context.sources
        ]

    def chat(self, chat_request: ChatRequest) -> ChatResponse:
        plan = self.orchestrator.plan(chat_request)
        messages = self._provider_messages(plan)
        content = sanitize_assistant_text(self.provider.generate(messages))
        return ChatResponse.create(
            message=ChatMessage(role="assistant", content=content),
            conversation_id=chat_request.conversation_id,
            model=self.provider.model,
            knowledge_domain=(
                plan.rag_context.domain if plan.rag_context else None
            ),
            sources=self._sources(plan.rag_context),
            agent_intent=plan.intent,
            agent_stage=plan.stage,
        )

    def stream(self, chat_request: ChatRequest) -> AIStream:
        plan = self.orchestrator.plan(chat_request)
        return AIStream(
            chunks=self.provider.stream(self._provider_messages(plan)),
            rag_context=plan.rag_context,
            agent_intent=plan.intent,
            agent_stage=plan.stage,
        )


def create_ai_service() -> AIService:
    provider_name = os.getenv("AI_PROVIDER", "stub").strip().lower()
    rag_enabled = _env_bool("RAG_ENABLED", provider_name != "stub")
    rag_service = create_rag_service() if rag_enabled else None

    if provider_name == "stub":
        service = AIService(StubAIProvider(), rag_service)
    elif provider_name == "deepseek":
        service = AIService(DeepSeekProvider(
            api_key=os.getenv("DEEPSEEK_API_KEY", "").strip(),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro").strip(),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip(),
            timeout_seconds=float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "60")),
            thinking_enabled=_env_bool("DEEPSEEK_THINKING_ENABLED", False),
            max_retries=int(os.getenv("DEEPSEEK_MAX_RETRIES", "2")),
            retry_base_seconds=float(
                os.getenv("DEEPSEEK_RETRY_BASE_SECONDS", "0.5")
            ),
            retry_max_seconds=float(
                os.getenv("DEEPSEEK_RETRY_MAX_SECONDS", "5")
            ),
        ), rag_service)
    else:
        raise RuntimeError(f"Unsupported AI_PROVIDER: {provider_name}")

    if rag_service is not None and _env_bool("RAG_PRELOAD", True):
        try:
            chunk_count = rag_service.warm_up()
            logger.info("RAG index ready with %s chunks", chunk_count)
        except Exception:
            logger.exception(
                "RAG index preload failed; AI will continue without RAG"
            )
    return service
