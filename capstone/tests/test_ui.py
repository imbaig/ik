from types import SimpleNamespace

import pytest

from music_store.application_contracts import ApplicationResult, SessionInfo
from music_store.ui import UIController, build_ui


class Service:
    def __init__(self):
        self.next = 0
        self.calls = []
        self.closed = []

    def new_session(self):
        self.next += 1
        return str(self.next)

    def send(self, handle, text, *, action):
        self.calls.append((handle, text, action))
        if text == "failure":
            raise RuntimeError("secret-provider-detail")
        return SimpleNamespace(
            text="Response " + handle, waiting=text == "account", status="complete"
        )

    def dispatch(self, handle, action):
        name = {
            "send": "retry",
            "resume_verification": "retry",
            "cancel_verification": "cancel",
            "catalog_only": "catalog_only",
        }[action.kind]
        reply = self.send(handle, action.text, action=name)
        return ApplicationResult(
            reply.text, reply.status, SessionInfo(reply.waiting, False, reply.waiting)
        )

    def reset(self, handle):
        self.closed.append(handle)
        return self.new_session()

    def close(self, handle):
        self.closed.append(handle)


@pytest.fixture
def controller():
    return UIController(Service())


def test_immediate_message_and_busy_then_answer(controller):
    token = controller.open()
    stream = controller.send("hello", token)
    first = next(stream)
    assert first[0] == [{"role": "user", "content": "hello"}]
    assert first[2]["interactive"] is False
    assert 'role="status"' in first[4] and "Working…" in first[4]
    assert controller.service.calls == []
    final = next(stream)
    assert final[0][-1]["content"] == "Response 1"
    assert final[2]["interactive"] is True
    list(stream)


def test_duplicate_send_rejected_while_in_flight(controller):
    token = controller.open()
    stream = controller.send("first", token)
    next(stream)
    list(controller.send("duplicate", token))
    list(stream)
    assert len(controller.service.calls) == 1


def test_distinct_sessions_and_reset(controller):
    one, two = controller.open(), controller.open()
    list(controller.send("account", one))
    assert controller._view(one).waiting
    assert controller._view(two).history == []
    result = controller.reset(one)
    assert result[0] == [] and not controller._view(one).waiting
    assert controller._view(one).handle == "3"
    list(controller.send("hello", two))
    assert controller.service.calls[-1][0] == "2"


@pytest.mark.parametrize("action", ["cancel", "catalog_only"])
def test_explicit_verification_actions(controller, action):
    token = controller.open()
    list(controller.send("account", token))
    list(getattr(controller, action)("untrusted textbox", token))
    assert controller.service.calls[-1] == ("1", "", action)


@pytest.mark.parametrize("text", ["", "   ", "x" * 2001])
def test_bad_input_never_calls_service(controller, text):
    list(controller.send(text, controller.open()))
    assert not controller.service.calls


def test_errors_sanitized_and_buttons_restored(controller):
    result = list(controller.send("failure", controller.open()))[-1]
    assert "secret" not in str(result)
    assert result[2]["interactive"] is True


def test_cleanup_closes_service_session(controller):
    token = controller.open()
    controller.close(token)
    controller.close(token)
    assert controller.service.closed == ["1"]
    with pytest.raises(ValueError, match="expired"):
        list(controller.send("hello", token))


def test_gradio_blocks_constructs_without_provider(controller):
    demo = build_ui(controller.service)
    assert demo.enable_queue
    assert not demo.analytics_enabled


def test_readable_adapter_preserves_sanitization_and_disallows_tags_downloads(controller):
    demo = build_ui(controller.service)
    chat = next(c for c in demo.config["components"] if c["type"] == "chatbot")["props"]
    assert chat["render_markdown"] is True and chat["sanitize_html"] is True
    assert chat["allow_tags"] is False and chat["allow_file_downloads"] is False
