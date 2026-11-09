"""Gradio presentation boundary; conversation identity stays in server-side State."""

import gradio as gr

from music_store.application_contracts import Action, ActionKind
from music_store.presentation.controller import PresentationController


class UIController:
    """Gradio-only mapping of neutral snapshots; no domain/action state lives here."""

    def __init__(self, service):
        self.service = service
        self.presentation = PresentationController(service)

    def open(self):
        return self.presentation.open()

    def close(self, token):
        self.presentation.close(token)

    def _view(self, token):
        # Compatibility for existing diagnostics; the server binding never enters outputs.
        return self.presentation._view(token)

    @staticmethod
    def output(state):
        if state is None:
            return (gr.skip(),) * 7
        return (
            [{"role": m.role, "content": m.content} for m in state.messages],
            gr.update(value=state.draft, interactive=not state.busy),
            gr.update(interactive=not state.busy),
            gr.update(interactive=not state.busy),
            state.status,
            gr.update(visible=state.waiting, interactive=not state.busy),
            gr.update(visible=state.can_catalog_only, interactive=not state.busy),
        )

    def send(self, text, token, *, action="retry"):
        kind = {
            "retry": ActionKind.SEND,
            "cancel": ActionKind.CANCEL_VERIFICATION,
            "catalog_only": ActionKind.CATALOG_ONLY,
        }[action]
        for state in self.presentation.dispatch(token, Action(kind, text)):
            if self.presentation.is_current(token, state):
                yield self.output(state)

    def cancel(self, text, token):
        yield from self.send("", token, action="cancel")

    def catalog_only(self, text, token):
        yield from self.send("", token, action="catalog_only")

    def reset(self, token):
        state = self.presentation.reset(token)
        return (
            self.output(state)
            if state is None or self.presentation.is_current(token, state)
            else (gr.skip(),) * 7
        )


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
