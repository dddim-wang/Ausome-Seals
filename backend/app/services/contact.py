import json
import os
import smtplib
from email.message import EmailMessage
from urllib import request as url_request
from urllib.error import HTTPError, URLError


DEFAULT_CONTACT_TO_EMAIL = "support@ausomeseals.com"
RESEND_API_URL = "https://api.resend.com/emails"


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def build_contact_email(inquiry: dict[str, str]) -> tuple[str, str]:
    subject = f"New Ausome Seals inquiry from {inquiry['name']}"
    if inquiry["company"]:
        subject += f" ({inquiry['company']})"

    body = "\n".join([
        "A customer submitted the Ausome Seals contact form.",
        "",
        f"Name: {inquiry['name']}",
        f"Company: {inquiry['company'] or '-'}",
        f"Email: {inquiry['email']}",
        f"Submitted at: {inquiry['created_at']}",
        "",
        "Message:",
        inquiry["message"],
    ])
    return subject, body


def send_contact_email_with_resend(inquiry: dict[str, str]) -> dict:
    resend_api_key = os.getenv("RESEND_API_KEY", "").strip()
    resend_from_email = os.getenv(
        "RESEND_FROM_EMAIL", "Ausome Seals <onboarding@resend.dev>"
    ).strip()
    contact_to_email = os.getenv(
        "CONTACT_TO_EMAIL", DEFAULT_CONTACT_TO_EMAIL
    ).strip()

    if not resend_api_key:
        raise RuntimeError("RESEND_API_KEY is required")

    subject, body = build_contact_email(inquiry)
    payload = {
        "from": resend_from_email,
        "to": [contact_to_email],
        "subject": subject,
        "text": body,
        "reply_to": inquiry["email"],
    }
    req = url_request.Request(
        RESEND_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {resend_api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Ausome-Seals-Contact/1.0",
        },
    )

    try:
        with url_request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Resend API error {exc.code}: {details}") from exc
    except URLError as exc:
        raise RuntimeError(f"Unable to connect to Resend API: {exc.reason}") from exc


def send_contact_email_with_smtp(inquiry: dict[str, str]) -> None:
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username).strip()
    smtp_use_tls = _env_bool("SMTP_USE_TLS", True)
    smtp_use_ssl = _env_bool("SMTP_USE_SSL", False)
    contact_to_email = os.getenv(
        "CONTACT_TO_EMAIL", DEFAULT_CONTACT_TO_EMAIL
    ).strip()

    if not smtp_host or not smtp_from_email:
        raise RuntimeError("SMTP_HOST and SMTP_FROM_EMAIL or SMTP_USERNAME are required")

    subject, body = build_contact_email(inquiry)
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = smtp_from_email
    message["To"] = contact_to_email
    message["Reply-To"] = inquiry["email"]
    message.set_content(body)

    smtp_class = smtplib.SMTP_SSL if smtp_use_ssl else smtplib.SMTP
    with smtp_class(smtp_host, smtp_port, timeout=15) as smtp:
        if smtp_use_tls and not smtp_use_ssl:
            smtp.starttls()
        if smtp_username and smtp_password:
            smtp.login(smtp_username, smtp_password)
        smtp.send_message(message)


def send_contact_email(inquiry: dict[str, str]):
    if os.getenv("RESEND_API_KEY", "").strip():
        return send_contact_email_with_resend(inquiry)
    return send_contact_email_with_smtp(inquiry)
