"""Gradio presentation boundary; conversation identity stays in server-side State."""

import html

import gradio as gr

from music_store.application_contracts import Action, ActionKind
from music_store.presentation.controller import PresentationController
from music_store.presentation.formatter import render_result, safe_text
from music_store.presentation.suggestions import STARTERS, next_questions

OUTPUT_COUNT = 15


class UIController:
    """Gradio-only mapping of neutral snapshots; no domain/action state lives here."""

    def __init__(self, service):
        self.service = service
        self.presentation = PresentationController(service, formatter=render_result)

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
            return (gr.skip(),) * OUTPUT_COUNT
        questions = next_questions(state)

        def question_update(index):
            if state.busy:
                return gr.update(interactive=False)
            return gr.update(value=questions[index], interactive=not state.waiting)

        return (
            [
                {"role": m.role, "content": safe_text(m.content) if m.role == "user" else m.content}
                for m in state.messages
            ],
            gr.update(
                value=state.draft,
                interactive=not state.busy,
                label="Sample customer ID, email or phone" if state.waiting else "Message",
                placeholder="Enter a Chinook sample identifier"
                if state.waiting
                else "Ask about music or a purchase",
            ),
            gr.update(interactive=not state.busy),
            gr.update(interactive=not state.busy),
            '<div role="status" aria-live="polite" aria-atomic="true">'
            + html.escape(state.status)
            + "</div>",
            gr.update(visible=state.waiting, interactive=not state.busy),
            gr.update(visible=state.can_catalog_only, interactive=not state.busy),
            "**Verified for this conversation**"
            if state.verified
            else "Not verified · public catalog available",
            gr.update(visible=not state.messages),
            gr.update(visible=bool(state.messages)),
            gr.update(visible=False),
            question_update(0),
            gr.update(visible=True),
            question_update(1),
            question_update(2),
        )

    def choose_suggestion(self, question, token):
        try:
            view = self.presentation._view(token)
        except ValueError:
            return gr.skip()
        with view.lock:
            if not view.active or view.busy or view.waiting:
                return gr.skip()
            # This only edits the draft; it never dispatches a tool/account action.
            if not isinstance(question, str) or not 1 <= len(question) <= 2000:
                return gr.skip()
            return gr.update(value=question)

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
            else (gr.skip(),) * OUTPUT_COUNT
        )


STYLE = """
#record-room {max-width:1120px;margin:auto;background:#f5f1e8;color:#202a25;padding:24px;}
#record-room h1,#record-room h2,#record-room h3 {font-family:Georgia,serif;color:#202a25;}
#record-room h1 {font-size:clamp(28px,4vw,42px);line-height:1.15;}
#record-room .rail {border-right:1px solid #8c958b;padding-right:20px;}
#record-room .welcome {padding:26px 0;}
#record-room button {min-height:44px;border-radius:3px;}
#record-room textarea {font-size:16px;}
#record-room :focus-visible {outline:3px solid #245b45;outline-offset:3px;}
#record-room .message {overflow-wrap:anywhere;}
#record-room .prose {overflow-wrap:anywhere;}
#conversation-history {min-height:260px;}
#conversation-history .bot-row .flex-wrap {width:100%;max-width:100%;}
#conversation-history .bot {width:100%;max-width:100%!important;}
#record-room .suggestion-row {gap:8px;}
#record-room .suggestion-row button {font-size:14px;padding:8px 10px;}
#record-room .result-disclosure {border:1px solid #8c958b;border-radius:4px;margin:12px 0;}
#record-room .result-disclosure summary {cursor:pointer;padding:12px;font-weight:600;}
#record-room .result-table {max-width:100%;overflow-x:auto;margin:8px 0;}
#record-room .result-table table {width:100%;border-collapse:collapse;font-size:14px;}
#record-room .result-table caption {position:absolute;width:1px;height:1px;padding:0;
 margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;}
#record-room .result-table th,#record-room .result-table td {text-align:left;padding:10px;
 border-bottom:1px solid #cbd0c8;vertical-align:top;white-space:pre-wrap;min-width:85px;}
#record-room .result-table th {background:#e8eee5;color:#202a25;}
#record-room .result-table tbody tr:nth-child(even) {background:#f5f1e8;}
@media(max-width:650px) {
 #record-room {padding:16px 10px;}
 #record-room .app-header {flex-direction:column;gap:8px;}
 #record-room .app-header > * {width:100%!important;min-width:0!important;flex:none!important;}
 #record-room .rail {display:none;}
 #conversation-history {height:clamp(260px,calc(100dvh - 280px),900px)!important;}
 #record-room .main-column {min-width:0!important;width:100%;}
}
"""


def build_ui(service, *, test_banner=None):
    controller = UIController(service)
    theme = gr.themes.Base(
        primary_hue="green",
        neutral_hue="stone",
        font=["system-ui", "sans-serif"],
    ).set(
        body_background_fill="#f5f1e8",
        block_background_fill="#fffdf8",
        body_text_color="#202a25",
        body_text_color_subdued="#4c5a51",
        border_color_primary="#8c958b",
        button_primary_background_fill="#245b45",
        button_primary_text_color="#ffffff",
    )
    with gr.Blocks(
        title="Record Room · Music Store v1", analytics_enabled=False, css=STYLE, theme=theme
    ) as demo:
        token = gr.State(None, time_to_live=3600, delete_callback=controller.close)
        with gr.Column(elem_id="record-room"):
            with gr.Row(elem_classes="app-header"):
                gr.Markdown("## Music Store\nRecord Room · v1 preview")
                identity = gr.Markdown("Not verified · public catalog available")
                reset = gr.Button("New conversation")
            if test_banner:
                gr.Markdown("**Test-only mode:** " + safe_text(test_banner))
            with gr.Row():
                with gr.Column(scale=1, min_width=170, elem_classes="rail"):
                    gr.Markdown(
                        "### Music & purchases\nFind something to explore.\n\n"
                        "Understand what you bought.\n\n"
                        "**Your conversation**\nOne verified customer per conversation. "
                        "To switch, choose New conversation and verify again."
                    )
                with gr.Column(scale=4, min_width=280, elem_classes="main-column"):
                    with gr.Column(elem_classes="welcome") as welcome:
                        gr.Markdown(
                            "# What would you like to explore?\n"
                            "Find albums and tracks, or revisit a purchase."
                        )
                    with gr.Column(visible=False) as conversation_panel:
                        chat = gr.Chatbot(
                            type="messages",
                            height="clamp(260px, calc(100dvh - 340px), 1400px)",
                            elem_id="conversation-history",
                            render_markdown=True,
                            sanitize_html=True,
                            allow_tags=False,
                            allow_file_downloads=False,
                            label="Conversation",
                            show_copy_button=False,
                        )
                    status = gr.HTML(
                        '<div role="status" aria-live="polite" aria-atomic="true">'
                        "Ready · ask a question to begin</div>",
                        elem_id="request-status",
                    )
                    with gr.Row(elem_classes="suggestion-row") as suggestions:
                        discover = gr.Button(STARTERS[0], size="sm", min_width=140)
                        purchases = gr.Button(STARTERS[1], size="sm", min_width=140)
                        taste = gr.Button(STARTERS[2], size="sm", min_width=140)
                    message = gr.Textbox(
                        label="Message", placeholder="Ask about music or a purchase", max_lines=5
                    )
                    send = gr.Button("Send", variant="primary")
                    with gr.Row():
                        cancel = gr.Button("Cancel verification", visible=False)
                        catalog = gr.Button("Continue with catalog only", visible=False)
                    with gr.Column(visible=False) as confirmation:
                        gr.Markdown(
                            "### Start a new conversation?\n"
                            "This clears this chat and verified identity. You will need to verify "
                            "again for account questions. Saved music preferences stay in this "
                            "running process; they are not deleted."
                        )
                        with gr.Row():
                            confirm = gr.Button("Start new conversation", variant="primary")
                            keep = gr.Button("Keep this conversation")
                    gr.Markdown(
                        "Catalog browsing is public. Account questions use a Chinook sample "
                        "customer ID, email or phone when prompted. **This demo is not production "
                        "authentication.** One customer per conversation; "
                        "New conversation requires "
                        "fresh verification. Preferences exist only in this running process and "
                        "are lost on restart. Cancel verification abandons the pending account "
                        "request; it does not stop a provider call."
                    )
        outputs = [
            chat,
            message,
            send,
            reset,
            status,
            cancel,
            catalog,
            identity,
            welcome,
            conversation_panel,
            confirmation,
            discover,
            suggestions,
            purchases,
            taste,
        ]

        def request_reset(binding):
            view = controller.presentation._view(binding)
            with view.lock:
                return gr.update(visible=True) if not view.busy else gr.skip()

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
        reset.click(request_reset, inputs=token, outputs=confirmation, api_name=False)
        keep.click(lambda: gr.update(visible=False), outputs=confirmation, api_name=False)
        confirm.click(
            controller.reset,
            inputs=token,
            outputs=outputs,
            api_name=False,
            concurrency_limit=16,
        )
        for button in (discover, purchases, taste):
            button.click(
                controller.choose_suggestion,
                inputs=[button, token],
                outputs=message,
                api_name=False,
            )
    demo.queue(default_concurrency_limit=16, max_size=32)
    return demo
