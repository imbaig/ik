"""SDK transport fault injection, never live provider quality evidence."""

import httpx
import pytest
from openai import APITimeoutError, RateLimitError

from music_store.config import Settings
from music_store.model import configured_chat_model


def model_with_transport(monkeypatch, handler, attempts=2):
    import music_store.model as module

    constructor = module.ChatOpenAI

    def local_transport(**kwargs):
        return constructor(
            **kwargs, http_client=httpx.Client(transport=httpx.MockTransport(handler))
        )

    monkeypatch.setattr(module, "ChatOpenAI", local_transport)
    return configured_chat_model(Settings(openai_api_key="test-placeholder", max_attempts=attempts))


def test_rate_limit_retries_are_bounded(monkeypatch):
    calls = []

    def handler(request):
        calls.append(request.url.path)
        return httpx.Response(
            429,
            headers={"retry-after": "0"},
            json={"error": {"message": "injected", "type": "rate_limit_error"}},
        )

    model = model_with_transport(monkeypatch, handler)
    with pytest.raises(RateLimitError):
        model.invoke("test only")
    assert len(calls) == 2


def test_timeout_retries_are_bounded(monkeypatch):
    calls = []

    def handler(request):
        calls.append(request.url.path)
        raise httpx.ReadTimeout("injected", request=request)

    model = model_with_transport(monkeypatch, handler, attempts=1)
    with pytest.raises(APITimeoutError):
        model.invoke("test only")
    assert len(calls) == 1


def test_transient_rate_limit_recovers_on_second_attempt(monkeypatch):
    calls = []

    def handler(request):
        calls.append(request.url.path)
        if len(calls) == 1:
            return httpx.Response(
                429, headers={"retry-after": "0"}, json={"error": {"message": "injected"}}
            )
        return httpx.Response(
            200,
            json={
                "id": "mock",
                "object": "chat.completion",
                "created": 0,
                "model": "test-model",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "recovered"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            },
        )

    response = model_with_transport(monkeypatch, handler).invoke("test only")
    assert response.content == "recovered" and len(calls) == 2
