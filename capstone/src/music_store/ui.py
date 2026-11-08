"""Gradio presentation boundary; conversation identity stays in server-side State."""

import threading
import time
from dataclasses import dataclass, field
from uuid import uuid4

import gradio as gr


@dataclass
class _View:
    handle: str
    history: list = field(default_factory=list)
    waiting: bool = False
    lock: threading.Lock = field(default_factory=threading.Lock)


class UIController:
    def __init__(self, service):
        self.service = service
        self._views = {}
        self._lock = threading.RLock()

    def open(self):
        token = str(uuid4())
        with self._lock:
            self._views[token] = _View(self.service.new_session())
        return token

    def _view(self, token):
        with self._lock:
            view = self._views.get(token)
        if view is None:
            raise ValueError("Conversation expired; reload this page")
        return view

    def close(self, token):
        with self._lock:
            view = self._views.pop(token, None)
        if view:
            with view.lock:
                self.service.close(view.handle)

    @staticmethod
    def output(view, status, *, busy=False, text=""):
        return (
            list(view.history),
            gr.update(value=text, interactive=not busy),
            gr.update(interactive=not busy),
            gr.update(interactive=not busy),
            status,
            gr.update(visible=view.waiting, interactive=not busy),
            gr.update(visible=view.waiting, interactive=not busy),
        )

    def send(self, text, token, *, action="retry"):
        view = self._view(token)
        if not view.lock.acquire(blocking=False):
            # An in-flight callback owns the UI; do not overwrite its outputs.
            yield (gr.skip(),) * 7
            return
        try:
            if action == "retry" and (not text.strip() or len(text) > 2000):
                yield self.output(view, "Enter 1–2000 characters.", text=text)
                return
            label = (
                text
                if action == "retry"
                else {
                    "cancel": "Cancel verification",
                    "catalog_only": "Continue with catalog only",
                }[action]
            )
            view.history.append({"role": "user", "content": label})
            yield self.output(view, "Working…", busy=True)
            started = time.perf_counter()
            try:
                reply = self.service.send(view.handle, text, action=action)
                view.waiting = reply.waiting
                view.history.append({"role": "assistant", "content": reply.text})
                status = "Verification needed" if reply.waiting else reply.status.replace("_", " ")
                status += f" · {time.perf_counter() - started:.1f}s"
            except Exception:
                view.history.append(
                    {
                        "role": "assistant",
                        "content": (
                            "This request could not finish. Please retry "
                            "or start a new conversation."
                        ),
                    }
                )
                status = "Request unavailable"
            view.history = view.history[-80:]
            yield self.output(view, status)
        finally:
            view.lock.release()

    def cancel(self, text, token):
        yield from self.send("", token, action="cancel")

    def catalog_only(self, text, token):
        yield from self.send("", token, action="catalog_only")

    def reset(self, token):
        view = self._view(token)
        with view.lock:
            view.handle = self.service.reset(view.handle)
            view.history.clear()
            view.waiting = False
            return self.output(view, "New conversation · identity cleared")


def build_ui(service, *, test_banner=None):
    controller = UIController(service)
    with gr.Blocks(title="Music Store Assistant", analytics_enabled=False) as demo:
        gr.Markdown(
            "# Music Store Assistant\nDiscover music, explore purchases, and save your tastes."
        )
        if test_banner:
            gr.Markdown(f"**Browser QA mode — {test_banner}**")
        gr.Markdown(
            "Catalog browsing is public. For account questions, use a Chinook sample customer "
            "ID, email, or phone when prompted. This course demo is not production authentication. "
            "One customer per conversation; use New conversation to switch. Preferences remain "
            "in this running process."
        )
        token = gr.State(None, time_to_live=3600, delete_callback=controller.close)
        chat = gr.Chatbot(
            type="messages",
            height=440,
            render_markdown=False,
            sanitize_html=True,
            allow_tags=False,
            allow_file_downloads=False,
            label="Conversation",
        )
        status = gr.Textbox(value="Ready", label="Status", interactive=False)
        message = gr.Textbox(label="Message", placeholder="Find songs by Queen", max_lines=4)
        with gr.Row():
            send = gr.Button("Send", variant="primary")
            reset = gr.Button("New conversation")
        with gr.Row():
            cancel = gr.Button("Cancel verification", visible=False)
            catalog = gr.Button("Continue with catalog only", visible=False)
        outputs = [chat, message, send, reset, status, cancel, catalog]
        demo.load(controller.open, outputs=token, api_name=False)
        options = dict(
            inputs=[message, token],
            outputs=outputs,
            api_name=False,
            concurrency_limit=16,
            trigger_mode="once",
        )
        send.click(controller.send, **options)
        message.submit(controller.send, **options)
        cancel.click(controller.cancel, **options)
        catalog.click(controller.catalog_only, **options)
        chat.clear(
            controller.reset, inputs=token, outputs=outputs, api_name=False, concurrency_limit=16
        )
        reset.click(
            controller.reset, inputs=token, outputs=outputs, api_name=False, concurrency_limit=16
        )
    demo.queue(default_concurrency_limit=16, max_size=32)
    return demo
