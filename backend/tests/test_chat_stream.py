import os
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
os.environ["AI_PROVIDER"] = "stub"
os.environ["RATELIMIT_ENABLED"] = "false"

from app import create_app


class ChatStreamApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app())

    def tearDown(self):
        self.client.close()

    def test_chat_stream_emits_meta_deltas_and_done(self):
        with self.client.stream("POST", "/api/chat/stream", json={
            "messages": [{"role": "user", "content": "Hello"}],
        }) as response:
            body = "".join(response.iter_text())

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers["content-type"])
        self.assertIn("event: meta", body)
        self.assertIn('"conversation_id"', body)
        self.assertIn("event: delta", body)
        self.assertIn("event: done", body)


if __name__ == "__main__":
    unittest.main()
