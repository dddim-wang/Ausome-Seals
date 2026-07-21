import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
os.environ["RATELIMIT_ENABLED"] = "false"
os.environ["AI_PROVIDER"] = "stub"

from app import create_app


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        self.client.close()


class ContactApiTests(ApiTestCase):
    def test_health_and_products_match_current_brand(self):
        health = self.client.get("/api/health")
        products = self.client.get("/api/products")

        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["service"], "Ausome Seals API")
        self.assertEqual(products.status_code, 200)
        self.assertEqual(len(products.json()), 1)
        self.assertEqual(products.json()[0]["name"], "Oil Seal")

    def test_admin_inquiries_endpoint_is_not_exposed(self):
        response = self.client.get("/api/admin/inquiries")
        self.assertEqual(response.status_code, 404)

    @patch("app.api.contact.send_contact_email")
    def test_valid_contact_sends_email_without_echoing_personal_data(self, send_email):
        response = self.client.post("/api/contact", json={
            "name": "Review User",
            "company": "Example",
            "email": "review@example.com",
            "message": "Please quote this seal.",
            "website": "",
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "Inquiry received"})
        send_email.assert_called_once()

    @patch("app.api.contact.send_contact_email")
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

        self.assertEqual(invalid_email.status_code, 422)
        self.assertEqual(long_message.status_code, 422)


class ChatApiTests(ApiTestCase):
    def test_chat_returns_assistant_message_and_conversation_id(self):
        response = self.client.post("/api/chat", json={
            "messages": [{"role": "user", "content": "如何选择油封？"}],
        })

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["message"]["role"], "assistant")
        self.assertIn("如何选择油封？", body["message"]["content"])
        self.assertTrue(body["conversation_id"])
        self.assertEqual(body["model"], "ausome-chat-stub-v1")

    def test_chat_preserves_supplied_conversation_id(self):
        response = self.client.post("/api/chat", json={
            "conversation_id": "conversation-123",
            "messages": [{"role": "user", "content": "Hello"}],
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["conversation_id"], "conversation-123")

    def test_chat_rejects_invalid_payloads(self):
        not_json = self.client.post(
            "/api/chat", content="hello", headers={"Content-Type": "text/plain"}
        )
        empty_messages = self.client.post("/api/chat", json={"messages": []})
        invalid_role = self.client.post("/api/chat", json={
            "messages": [{"role": "tool", "content": "Hello"}],
        })

        self.assertEqual(not_json.status_code, 422)
        self.assertEqual(empty_messages.status_code, 422)
        self.assertEqual(invalid_role.status_code, 422)

    def test_openapi_docs_include_chat_endpoint(self):
        schema = self.client.get("/openapi.json")

        self.assertEqual(schema.status_code, 200)
        self.assertIn("/api/chat", schema.json()["paths"])


if __name__ == "__main__":
    unittest.main()
