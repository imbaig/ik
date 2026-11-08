"""Browser QA only: deterministic model doubles, real graphs/tools/Chinook database.

Run PYTHONPATH=src:tests .venv/bin/python tests/ui_harness.py
This is not the production app or evidence of live model quality.
"""

import re

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from music_store.agents.runtime import AgentRuntime
from music_store.config import load_settings
from music_store.conversation import ConversationService, RouteDecision
from music_store.db import initialize_database
from music_store.identity import UserInput
from music_store.telemetry import EventSink
from music_store.ui import build_ui
from music_store.verification import VerificationService


class QAModel(BaseChatModel):
    role: str
    tool_names: tuple = ()

    @property
    def _llm_type(self):
        return "deterministic-browser-qa"

    def bind_tools(self, tools, **kwargs):
        names = tuple(t.name if hasattr(t, "name") else t["function"]["name"] for t in tools)
        return self.model_copy(update={"tool_names": names})

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if isinstance(messages[-1], ToolMessage) or (
            self.role == "supervisor" and isinstance(messages[-1], AIMessage)
        ):
            response = AIMessage(content="Complete")
        else:
            if self.role == "supervisor":
                name = (
                    "transfer_to_invoice_agent"
                    if "transfer_to_invoice_agent" in self.tool_names
                    else "transfer_to_catalog_agent"
                )
                args = {}
            elif self.role == "invoice":
                identity = " ".join(
                    str(m.content) for m in messages if isinstance(m, SystemMessage)
                )
                match = re.search(r"Verified customer_id: (\d+)", identity)
                name, args = (
                    "get_invoices_by_customer_sorted_by_date",
                    {"customer_id": match[1] if match else "1"},
                )
            else:
                name, args = "get_albums_by_artist", {"artist_name": "Queen"}
            response = AIMessage(
                content="", tool_calls=[{"name": name, "args": args, "id": "qa-call"}]
            )
        return ChatResult(generations=[ChatGeneration(message=response)])


class QARouter:
    def classify(self, messages):
        text = next(m.content for m in reversed(messages) if isinstance(m, HumanMessage)).lower()
        return RouteDecision(
            kind=(
                "mixed"
                if "invoice" in text and "music" in text
                else "invoice"
                if "invoice" in text
                else "catalog"
            )
        )


class QAExtractor:
    def extract(self, message):
        return (
            UserInput(kind="customer_id", identifier=message)
            if message.isdigit()
            else UserInput(kind="none", identifier=None)
        )


def service(database, telemetry=None):
    return ConversationService(
        VerificationService(database, QAExtractor()),
        QARouter(),
        AgentRuntime(
            database,
            supervisor_model=QAModel(role="supervisor"),
            catalog_model=QAModel(role="catalog"),
            invoice_model=QAModel(role="invoice"),
        ),
        telemetry=telemetry,
    )


if __name__ == "__main__":
    database = initialize_database(load_settings().chinook_cache_dir)
    build_ui(
        service(database, EventSink()), test_banner="deterministic models; real database and tools"
    ).launch(
        server_name="127.0.0.1", server_port=7861, share=False, show_api=False, show_error=False
    )
