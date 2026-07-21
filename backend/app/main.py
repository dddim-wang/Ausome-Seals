import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.ai import create_ai_service
from app.api import chat_router, contact_router, system_router
from app.extensions import limiter


def create_app() -> FastAPI:
    load_dotenv()

    app = FastAPI(
        title="Ausome Seals API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    frontend_origins = [
        origin.strip()
        for origin in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=frontend_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    max_request_bytes = int(os.getenv("MAX_API_REQUEST_BYTES", "32768"))

    @app.middleware("http")
    async def reject_oversized_requests(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > max_request_bytes:
            return JSONResponse(
                status_code=413,
                content={"error": "request body is too large"},
            )
        return await call_next(request)

    app.state.limiter = limiter
    app.state.ai_service = create_ai_service()
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.include_router(system_router)
    app.include_router(contact_router)
    app.include_router(chat_router)
    return app


app = create_app()
