import json
import socket
from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from urllib import request as url_request
from urllib.error import HTTPError, URLError

from app.models import ChatMessage


class AIProviderError(RuntimeError):
    """A provider failed to generate a response."""


class AIProvider(ABC):
    name: str
    model: str

    @abstractmethod
    def generate(self, messages: Sequence[ChatMessage]) -> str:
        """Generate complete assistant text for a conversation."""

    def stream(self, messages: Sequence[ChatMessage]) -> Iterator[str]:
        """Stream assistant text; providers may override with native streaming."""
        return iter((self.generate(messages),))


class StubAIProvider(AIProvider):
    """Local provider for tests and development without external API calls."""

    name = "stub"
    model = "ausome-chat-stub-v1"

    def generate(self, messages: Sequence[ChatMessage]) -> str:
        latest_user_message = next(
            (message.content for message in reversed(messages) if message.role == "user"),
            "",
        )
        return (
            "AI service is connected in local test mode. Message received: "
            f"{latest_user_message}"
        )

    def stream(self, messages: Sequence[ChatMessage]) -> Iterator[str]:
        text = self.generate(messages)
        return iter(text[index:index + 12] for index in range(0, len(text), 12))


class DeepSeekProvider(AIProvider):
    name = "deepseek"

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "deepseek-v4-pro",
        base_url: str = "https://api.deepseek.com",
        timeout_seconds: float = 60.0,
        thinking_enabled: bool = False,
    ):
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is required")

        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.thinking_enabled = thinking_enabled

    def _build_request(
        self, messages: Sequence[ChatMessage], *, stream: bool
    ) -> url_request.Request:
        payload = {
            "model": self.model,
            "messages": [message.model_dump() for message in messages],
            "stream": stream,
            "thinking": {
                "type": "enabled" if self.thinking_enabled else "disabled"
            },
        }
        return url_request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "text/event-stream" if stream else "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Ausome-Seals-AI/1.0",
            },
        )

    def _open(self, request: url_request.Request):
        try:
            return url_request.urlopen(request, timeout=self.timeout_seconds)
        except HTTPError as exc:
            raise AIProviderError(f"DeepSeek API returned HTTP {exc.code}") from exc
        except (URLError, socket.timeout, TimeoutError) as exc:
            raise AIProviderError("Unable to reach DeepSeek API") from exc

    def generate(self, messages: Sequence[ChatMessage]) -> str:
        response = self._open(self._build_request(messages, stream=False))
        try:
            with response:
                body = json.loads(response.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"].strip()
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AIProviderError("DeepSeek API returned an invalid response") from exc
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise AIProviderError(
                "DeepSeek API response did not contain assistant text"
            ) from exc

        if not content:
            raise AIProviderError("DeepSeek API returned an empty response")
        return content

    def stream(self, messages: Sequence[ChatMessage]) -> Iterator[str]:
        # Open eagerly so connection/authentication errors can still become HTTP 503.
        response = self._open(self._build_request(messages, stream=True))
        return self._iter_sse(response)

    def _iter_sse(self, response) -> Iterator[str]:
        try:
            with response:
                for raw_line in response:
                    line = raw_line.decode("utf-8").strip()
                    if not line or line.startswith(":") or not line.startswith("data:"):
                        continue

                    data = line[5:].strip()
                    if data == "[DONE]":
                        break

                    chunk = json.loads(data)
                    choices = chunk.get("choices") or []
                    if not choices:
                        continue
                    content = (choices[0].get("delta") or {}).get("content")
                    if content:
                        yield content
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AIProviderError("DeepSeek stream returned invalid data") from exc
        except (URLError, socket.timeout, TimeoutError, OSError) as exc:
            raise AIProviderError("DeepSeek stream was interrupted") from exc
