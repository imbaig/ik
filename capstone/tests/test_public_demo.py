"""Public demo admission is persistent and cannot overshoot under concurrent requests."""

from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest

from music_store.application_contracts import Action, ActionKind, DemoLimitReached
from music_store.config import ConfigurationError
from music_store.deployment import access_gate, deployment_settings
from music_store.public_demo import DemoQuota, LimitedApplication


def test_public_access_requires_explicit_sample_data_acknowledgement():
    for ack in (None, "true", ""):
        with pytest.raises(ConfigurationError):
            access_gate({"APP_ACCESS_MODE": "public-demo", "PUBLIC_DEMO_ACK": ack}, "0.0.0.0")
    assert (
        access_gate(
            {"APP_ACCESS_MODE": "public-demo", "PUBLIC_DEMO_ACK": "PUBLIC_SAMPLE_DATA_ONLY"},
            "0.0.0.0",
        )
        is None
    )


def test_concurrent_admission_and_restart_share_same_limit(tmp_path):
    path = tmp_path / "quota.sqlite"
    quota = DemoQuota(path, daily=7, total=10)
    with ThreadPoolExecutor(max_workers=12) as pool:
        accepted = list(pool.map(lambda _: quota.reserve(), range(30)))
    assert sum(accepted) == 7
    assert not DemoQuota(path, daily=7, total=10).reserve()


def test_lifetime_limit_includes_prior_days(tmp_path):
    import sqlite3

    path = tmp_path / "quota.sqlite"
    quota = DemoQuota(path, daily=2, total=3)
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO usage VALUES (?,?)", ("2000-01-01", 2))
    assert quota.reserve()
    assert not quota.reserve()


@pytest.mark.parametrize("daily,total", [(0, 5), (6, 5), (1, 1001)])
def test_invalid_limits_fail_closed(tmp_path, daily, total):
    with pytest.raises(ValueError):
        DemoQuota(tmp_path / "quota.sqlite", daily=daily, total=total)


def test_public_startup_bounds_tokens_even_when_omitted():
    assert deployment_settings({"APP_ACCESS_MODE": "public-demo"}).model_max_tokens == 600
    assert deployment_settings({}).model_max_tokens is None
    with pytest.raises(ConfigurationError):
        deployment_settings({"APP_ACCESS_MODE": "public-demo", "MODEL_MAX_TOKENS": "601"})


@pytest.mark.parametrize("cap,expected", [(None, 350), (128, 128), (600, 350)])
def test_narration_models_respect_smaller_configured_cap(monkeypatch, cap, expected):
    from music_store import model
    from music_store.config import Settings

    seen = []

    class Chat:
        max_tokens = None

        def with_structured_output(self, *args, **kwargs):
            seen.append(self.max_tokens)
            return self

    monkeypatch.setattr(model, "configured_chat_model", lambda settings: Chat())
    model.build_response_writer(Settings(model_max_tokens=cap))
    assert seen == [expected, expected]


def test_limit_prevents_service_call_but_keeps_cancellation_available(tmp_path):
    calls = []
    service = SimpleNamespace(dispatch=lambda handle, action: calls.append(action.kind))
    limited = LimitedApplication(service, DemoQuota(tmp_path / "quota.sqlite", daily=1, total=1))
    limited.dispatch("session", Action(ActionKind.SEND, "hello"))
    with pytest.raises(DemoLimitReached):
        limited.dispatch("session", Action(ActionKind.SEND, "hello again"))
    limited.dispatch("session", Action(ActionKind.CANCEL_VERIFICATION))
    assert calls == [ActionKind.SEND, ActionKind.CANCEL_VERIFICATION]
