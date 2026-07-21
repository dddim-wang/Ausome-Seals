import json
import logging
from collections.abc import Iterator

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.ai.providers import AIProviderError
from app.extensions import limiter
from app.models import ChatRequest, ChatResponse


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["AI"])


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    try:
        return request.app.state.ai_service.chat(payload)
    except AIProviderError as exc:
        logger.exception("AI provider request failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is temporarily unavailable",
        ) from exc


@router.post("/chat/stream")
@limiter.limit("20/minute")
def chat_stream(request: Request, payload: ChatRequest) -> StreamingResponse:
    try:
        stream = request.app.state.ai_service.stream(payload)
    except AIProviderError as exc:
        logger.exception("AI provider stream failed to start")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is temporarily unavailable",
        ) from exc

    def event_stream() -> Iterator[str]:
        yield _sse("meta", {
            "conversation_id": payload.conversation_id,
            "model": request.app.state.ai_service.provider.model,
            "knowledge_domain": stream.rag_context.domain if stream.rag_context else None,
            "sources": [source.__dict__ for source in stream.rag_context.sources]
            if stream.rag_context else [],
        })
        try:
            for content in stream.chunks:
                yield _sse("delta", {"content": content})
        except AIProviderError:
            logger.exception("AI provider stream was interrupted")
            yield _sse("error", {"message": "AI service stream was interrupted"})
            return
        yield _sse("done", {})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
