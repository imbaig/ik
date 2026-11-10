"""TEST TARGET ONLY: real services with deterministic models, never the default app."""

from langchain_core.messages import HumanMessage, ToolMessage
from ui_harness import QAExtractor, QAModel, QARouter

from music_store.agents.runtime import AgentRuntime
from music_store.conversation import ConversationService
from music_store.deployment import serve
from music_store.verification import VerificationService


class ContainerModel(QAModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        # A supervisor handoff is not a completed domain tool. The older browser
        # harness stops at this ToolMessage; explicitly exercise the real specialist.
        if isinstance(messages[-1], ToolMessage) and messages[-1].name.startswith("transfer_to_"):
            messages = [*messages, HumanMessage(content="Run the assigned domain tool")]
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


def service(database):
    return ConversationService(
        VerificationService(database, QAExtractor()),
        QARouter(),
        AgentRuntime(
            database,
            supervisor_model=ContainerModel(role="supervisor"),
            catalog_model=ContainerModel(role="catalog"),
            invoice_model=ContainerModel(role="invoice"),
        ),
    )


if __name__ == "__main__":
    serve(service_factory=service, smoke_test=True)
