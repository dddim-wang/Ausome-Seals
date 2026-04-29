from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import re
from datetime import datetime

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")}})

    inquiries = []

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "Ausome Seals Technology API"
        })

    @app.get("/api/products")
    def products():
        return jsonify([
            {
                "id": 1,
                "name": "Hydraulic Gate Seals",
                "category": "Main sealing products",
                "description": "Sealing products for steel production hydraulic gate equipment."
            },
            {
                "id": 2,
                "name": "Cylinder & Rod Seals",
                "category": "Hydraulic cylinder seals",
                "description": "Seals for rods, pistons, cylinders, and heavy-duty hydraulic movement."
            },
            {
                "id": 3,
                "name": "Guide Rings & Wipers",
                "category": "Support components",
                "description": "Support parts for alignment, dust protection, and system reliability."
            }
        ])

    @app.post("/api/contact")
    def contact():
        data = request.get_json(silent=True) or {}

        name = str(data.get("name", "")).strip()
        company = str(data.get("company", "")).strip()
        email = str(data.get("email", "")).strip()
        message = str(data.get("message", "")).strip()

        if not name or not email or not message:
            return jsonify({"error": "name, email, and message are required"}), 400

        if not EMAIL_RE.match(email):
            return jsonify({"error": "invalid email address"}), 400

        inquiry = {
            "id": len(inquiries) + 1,
            "name": name,
            "company": company,
            "email": email,
            "message": message,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        inquiries.append(inquiry)

        # In production, save to database and send notification email here.
        return jsonify({
            "message": "Inquiry received",
            "inquiry": inquiry
        }), 201

    @app.get("/api/admin/inquiries")
    def list_inquiries():
        # Starter endpoint only. Add authentication before production use.
        return jsonify(inquiries)

    return app
