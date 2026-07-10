import os
import re
import smtplib
import json
from datetime import datetime, timezone
from email.message import EmailMessage
from urllib import request as url_request
from urllib.error import HTTPError, URLError

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DEFAULT_CONTACT_TO_EMAIL = "ausomeseals@gmail.com"
RESEND_API_URL = "https://api.resend.com/emails"
limiter = Limiter(key_func=get_remote_address, default_limits=[])


def _env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def build_contact_email(inquiry):
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


def send_contact_email_with_resend(inquiry):
    resend_api_key = os.getenv("RESEND_API_KEY", "").strip()
    resend_from_email = os.getenv("RESEND_FROM_EMAIL", "Ausome Seals <onboarding@resend.dev>").strip()
    contact_to_email = os.getenv("CONTACT_TO_EMAIL", DEFAULT_CONTACT_TO_EMAIL).strip()

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

    data = json.dumps(payload).encode("utf-8")
    req = url_request.Request(
        RESEND_API_URL,
        data=data,
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


def send_contact_email_with_smtp(inquiry):
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username).strip()
    smtp_use_tls = _env_bool("SMTP_USE_TLS", True)
    smtp_use_ssl = _env_bool("SMTP_USE_SSL", False)
    contact_to_email = os.getenv("CONTACT_TO_EMAIL", DEFAULT_CONTACT_TO_EMAIL).strip()

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


def send_contact_email(inquiry):
    if os.getenv("RESEND_API_KEY", "").strip():
        return send_contact_email_with_resend(inquiry)

    return send_contact_email_with_smtp(inquiry)

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTACT_REQUEST_BYTES", "32768"))
    app.config["RATELIMIT_ENABLED"] = _env_bool("RATELIMIT_ENABLED", True)
    app.config["RATELIMIT_STORAGE_URI"] = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").strip()
    CORS(app, resources={r"/api/*": {"origins": frontend_origin}})

    limiter.init_app(app)

    @app.errorhandler(429)
    def rate_limit_exceeded(_error):
        return jsonify({"error": "too many requests; please try again later"}), 429

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "Ausome Seals API"
        })

    @app.get("/api/products")
    def products():
        return jsonify([{
            "id": 1,
            "name": "Oil Seal",
            "category": "Heavy machinery sealing products",
            "description": "Large custom oil seals for rolling mill roll bearing areas and demanding industrial equipment."
        }])

    @app.post("/api/contact")
    @limiter.limit("5 per hour")
    def contact():
        if not request.is_json:
            return jsonify({"error": "application/json request required"}), 415

        data = request.get_json(silent=True) or {}

        name = str(data.get("name", "")).strip()
        company = str(data.get("company", "")).strip()
        email = str(data.get("email", "")).strip()
        message = str(data.get("message", "")).strip()
        website = str(data.get("website", "")).strip()

        # Bots commonly fill hidden website fields. Return success without sending mail.
        if website:
            return jsonify({"message": "Inquiry received"}), 201

        if not name or not email or not message:
            return jsonify({"error": "name, email, and message are required"}), 400

        if not EMAIL_RE.match(email):
            return jsonify({"error": "invalid email address"}), 400

        field_limits = {
            "name": (name, 120),
            "company": (company, 200),
            "email": (email, 254),
            "message": (message, 5000),
        }
        for field_name, (value, maximum) in field_limits.items():
            if len(value) > maximum:
                return jsonify({"error": f"{field_name} is too long"}), 400

        inquiry = {
            "name": name,
            "company": company,
            "email": email,
            "message": message,
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        try:
            send_contact_email(inquiry)
        except Exception as exc:
            app.logger.exception("Unable to send contact email")
            return jsonify({
                "error": "unable to send contact email",
                "details": str(exc) if app.debug else "email delivery failed"
            }), 503

        return jsonify({"message": "Inquiry received"}), 201

    return app
