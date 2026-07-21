import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from app.extensions import limiter
from app.models import ContactInquiry
from app.services import send_contact_email


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Contact"])


@router.post("/contact", status_code=201)
@limiter.limit("5/hour")
async def contact(request: Request, payload: ContactInquiry):
    # Bots commonly fill hidden website fields. Return success without sending mail.
    if payload.website:
        return {"message": "Inquiry received"}

    inquiry = payload.model_dump(exclude={"website"})
    inquiry["created_at"] = (
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )

    try:
        await run_in_threadpool(send_contact_email, inquiry)
    except Exception:
        logger.exception("Unable to send contact email")
        return JSONResponse(
            status_code=503,
            content={"error": "unable to send contact email"},
        )

    return {"message": "Inquiry received"}
