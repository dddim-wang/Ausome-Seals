import json
import os
import sys
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
os.environ["AI_PROVIDER"] = "stub"
os.environ["RATELIMIT_ENABLED"] = "false"

from app.ai.providers import AIProviderError, DeepSeekProvider
from app.ai.service import AIService, create_ai_service
from app.agent import AgentPlan
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


class InterruptedResponse(FakeResponse):
    def __iter__(self):
        yield b'data: {"choices":[{"delta":{"content":"Oil "}}]}\n\n'
        raise OSError("stream disconnected")


class BrokenRagService:
    def warm_up(self):
        raise OSError("cache directory is read-only")


class AIServiceResilienceTests(unittest.TestCase):
    @patch("app.ai.service.create_rag_service")
    def test_unexpected_rag_preload_error_does_not_break_ai_startup(self, create_rag):
        create_rag.return_value = BrokenRagService()

        with patch.dict(os.environ, {
            "AI_PROVIDER": "stub",
            "RAG_ENABLED": "true",
            "RAG_PRELOAD": "true",
        }), self.assertLogs("app.ai.service", level="ERROR"):
            service = create_ai_service()

        self.assertIsInstance(service, AIService)


class DeepSeekProviderTests(unittest.TestCase):
    def test_combined_rag_system_prompt_can_exceed_client_message_limit(self):
        plan = AgentPlan(
            messages=[
                ChatMessage(role="system", content="a" * 4_000),
                ChatMessage(role="system", content="b" * 5_000),
                ChatMessage(role="user", content="What is an oil seal?"),
            ],
            intent="technical_qa",
            stage="respond",
            rag_context=None,
        )

        messages = AIService._provider_messages(plan)

        self.assertEqual(messages[0].role, "system")
        self.assertEqual(len(messages[0].content), 9_002)
        self.assertEqual(messages[1].role, "user")

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

    @patch("app.ai.providers.time.sleep")
    @patch("app.ai.providers.url_request.urlopen")
    def test_retries_retryable_http_error_before_stream_starts(self, urlopen, sleep):
        urlopen.side_effect = [
            HTTPError("https://api.deepseek.com", 503, "unavailable", {}, None),
            FakeResponse(
                b'data: {"choices":[{"delta":{"content":"Oil seal"}}]}\n\n'
            ),
        ]
        provider = DeepSeekProvider(api_key="test-key")

        chunks = list(provider.stream([
            ChatMessage(role="user", content="Tell me about seals"),
        ]))

        self.assertEqual(chunks, ["Oil seal"])
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(0.5)

    @patch("app.ai.providers.time.sleep")
    @patch("app.ai.providers.url_request.urlopen")
    def test_retries_timeout_before_request_starts(self, urlopen, sleep):
        urlopen.side_effect = [
            TimeoutError("connection timed out"),
            FakeResponse(
                b'{"choices":[{"message":{"content":"Recovered"}}]}'
            ),
        ]
        provider = DeepSeekProvider(api_key="test-key")

        result = provider.generate([
            ChatMessage(role="user", content="Tell me about seals"),
        ])

        self.assertEqual(result, "Recovered")
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(0.5)

    @patch("app.ai.providers.time.sleep")
    @patch("app.ai.providers.url_request.urlopen")
    def test_does_not_retry_authentication_error(self, urlopen, sleep):
        urlopen.side_effect = HTTPError(
            "https://api.deepseek.com", 401, "unauthorized", {}, None
        )
        provider = DeepSeekProvider(api_key="test-key")

        with self.assertRaisesRegex(AIProviderError, "HTTP 401"):
            provider.stream([
                ChatMessage(role="user", content="Tell me about seals"),
            ])

        self.assertEqual(urlopen.call_count, 1)
        sleep.assert_not_called()

    @patch("app.ai.providers.url_request.urlopen")
    def test_does_not_reopen_interrupted_stream(self, urlopen):
        urlopen.return_value = InterruptedResponse(b"")
        provider = DeepSeekProvider(api_key="test-key")

        stream = provider.stream([
            ChatMessage(role="user", content="Tell me about seals"),
        ])
        self.assertEqual(next(stream), "Oil ")
        with self.assertRaisesRegex(AIProviderError, "stream was interrupted"):
            next(stream)

        self.assertEqual(urlopen.call_count, 1)


if __name__ == "__main__":
    unittest.main()
