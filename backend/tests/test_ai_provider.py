import json
import os
import sys
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
os.environ["AI_PROVIDER"] = "stub"
os.environ["RATELIMIT_ENABLED"] = "false"

from app.ai.providers import DeepSeekProvider
from app.models import ChatMessage


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = BytesIO(body)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def __iter__(self):
        return iter(self.body.readlines())

    def read(self):
        return self.body.read()


class DeepSeekProviderTests(unittest.TestCase):
    @patch("app.ai.providers.url_request.urlopen")
    def test_generate_uses_configured_model_and_returns_text(self, urlopen):
        body = {"choices": [{"message": {"content": "Use an NBR oil seal."}}]}
        urlopen.return_value = FakeResponse(json.dumps(body).encode("utf-8"))
        provider = DeepSeekProvider(api_key="test-key")

        result = provider.generate([
            ChatMessage(role="user", content="Which seal should I use?"),
        ])

        self.assertEqual(result, "Use an NBR oil seal.")
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "deepseek-v4-pro")
        self.assertFalse(payload["stream"])

    @patch("app.ai.providers.url_request.urlopen")
    def test_stream_parses_sse_deltas_and_ignores_keep_alive(self, urlopen):
        stream = (
            b": keep-alive\n\n"
            b"data: {\"choices\":[{\"delta\":{\"content\":\"Oil \"}}]}\n\n"
            b"data: {\"choices\":[{\"delta\":{\"content\":\"seal\"}}]}\n\n"
            b"data: [DONE]\n\n"
        )
        urlopen.return_value = FakeResponse(stream)
        provider = DeepSeekProvider(api_key="test-key")

        chunks = list(provider.stream([
            ChatMessage(role="user", content="Tell me about seals"),
        ]))

        self.assertEqual(chunks, ["Oil ", "seal"])
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertTrue(payload["stream"])
        self.assertEqual(request.headers["Accept"], "text/event-stream")


if __name__ == "__main__":
    unittest.main()
