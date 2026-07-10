import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
os.environ["RATELIMIT_ENABLED"] = "false"

from app import create_app


class ContactApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

    def test_health_and_products_match_current_brand(self):
        health = self.client.get("/api/health")
        products = self.client.get("/api/products")

        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.get_json()["service"], "Ausome Seals API")
        self.assertEqual(products.status_code, 200)
        self.assertEqual(len(products.get_json()), 1)
        self.assertEqual(products.get_json()[0]["name"], "Oil Seal")

    def test_admin_inquiries_endpoint_is_not_exposed(self):
        response = self.client.get("/api/admin/inquiries")
        self.assertEqual(response.status_code, 404)

    @patch("app.send_contact_email")
    def test_valid_contact_sends_email_without_echoing_personal_data(self, send_email):
        response = self.client.post("/api/contact", json={
            "name": "Review User",
            "company": "Example",
            "email": "review@example.com",
            "message": "Please quote this seal.",
            "website": "",
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"message": "Inquiry received"})
        send_email.assert_called_once()

    @patch("app.send_contact_email")
    def test_honeypot_submission_is_accepted_without_email(self, send_email):
        response = self.client.post("/api/contact", json={
            "name": "Bot",
            "email": "bot@example.com",
            "message": "Spam",
            "website": "https://spam.example",
        })

        self.assertEqual(response.status_code, 201)
        send_email.assert_not_called()

    def test_rejects_invalid_and_oversized_fields(self):
        invalid_email = self.client.post("/api/contact", json={
            "name": "User",
            "email": "invalid",
            "message": "Hello",
        })
        long_message = self.client.post("/api/contact", json={
            "name": "User",
            "email": "user@example.com",
            "message": "x" * 5001,
        })

        self.assertEqual(invalid_email.status_code, 400)
        self.assertEqual(long_message.status_code, 400)


if __name__ == "__main__":
    unittest.main()