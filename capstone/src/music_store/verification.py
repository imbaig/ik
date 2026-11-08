"""Real LangGraph interrupts behind a server-owned session and tool-access boundary.

This is the identity slice, not yet the supervisor/chat app. A future UI owns session
handles and passes text/actions here; it must never accept thread IDs supplied by clients.
"""

import threading
from dataclasses import dataclass, field
from typing import Literal, TypedDict
from uuid import uuid4

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from music_store.db import Database, DatabaseQueryError
from music_store.identity import IdentifierExtractor, UserInput, match_customer
from music_store.tools import build_tools

ACCOUNT_TOOLS = frozenset(
    {
        "get_invoices_by_customer_sorted_by_date",
        "get_purchased_tracks",
        "get_support_rep_by_invoice",
        "get_invoice_line_items",
    }
)


class VerificationState(TypedDict, total=False):
    customer_id: int | None
    identifier_input: str
    pending_request: str
    messages: list
    status: str
    message: str
    attempts: int
    action: str
    verification_outcome: str


@dataclass
class _Session:
    lock: threading.RLock = field(default_factory=threading.RLock)
    active: bool = True


@dataclass(frozen=True)
class VerificationResult:
    status: str
    message: str
    waiting: bool
    pending_request: str
    outcome: str = "not_attempted"


class VerificationService:
    def __init__(
        self, database: Database, extractor: IdentifierExtractor, *, max_attempts: int = 5
    ):
        if not 1 <= max_attempts <= 10:
            raise ValueError("Verification attempt limit must be between 1 and 10")
        self._database = database
        self._extractor = extractor
        self._sessions: dict[str, _Session] = {}
        self._registry_lock = threading.RLock()
        self._checkpointer = InMemorySaver()

        def verify(state):
            if state.get("customer_id") is not None:
                return {
                    "status": "verified",
                    "message": "Account verified",
                    "verification_outcome": "not_attempted",
                }
            if state.get("action") in {"cancel", "catalog_only"}:
                return {
                    "status": "cancelled" if state["action"] == "cancel" else "catalog_only",
                    "verification_outcome": "not_attempted",
                    "message": "Account request cancelled; no invoices accessed",
                    "customer_id": None,
                    "pending_request": "",
                    "identifier_input": "",
                    "messages": [],
                }
            attempts = state.get("attempts", 0)
            if attempts >= max_attempts:
                return {
                    "customer_id": None,
                    "status": "retry_limit",
                    "verification_outcome": "not_attempted",
                    "attempts": attempts,
                    "message": "Verification retry limit reached; start a new conversation",
                    "pending_request": "",
                    "identifier_input": "",
                    "messages": [],
                }
            message = "Please provide your customer ID, registered email or phone"
            identity = None
            outcome = "not_attempted"
            source = state.get("identifier_input", "")
            if source.strip():
                attempts += 1
                outcome = "not_found"
                try:
                    candidate = UserInput.model_validate(self._extractor.extract(source))
                    identity = match_customer(self._database, candidate, source)
                    message = (
                        "I couldn't find one account with those details. Check them or try "
                        "your registered email or phone. No invoices were accessed."
                    )
                except DatabaseQueryError:
                    outcome = "database_error"
                    message = (
                        "Verification lookup is unavailable; retry later. No invoices accessed."
                    )
                except Exception:
                    outcome = "provider_error"
                    # The provider/extractor is a fault boundary; never emit credential/raw input.
                    message = (
                        "Verification could not be completed; please retry. No invoices accessed."
                    )
            if identity is not None:
                return {
                    "customer_id": identity,
                    "verification_outcome": "verified",
                    "status": "verified",
                    "message": "Account verified",
                    "identifier_input": "",
                    "attempts": attempts,
                    "messages": [SystemMessage(content="Verified customer_id: " + str(identity))],
                }
            if attempts >= max_attempts:
                return {
                    "customer_id": None,
                    "status": "retry_limit",
                    "verification_outcome": outcome,
                    "attempts": attempts,
                    "message": "Verification retry limit reached; start a new conversation",
                    "pending_request": "",
                    "identifier_input": "",
                    "messages": [],
                }
            return {
                "customer_id": None,
                "status": "waiting",
                "verification_outcome": outcome,
                "message": message,
                "attempts": attempts,
                "identifier_input": "",
                "messages": [],
            }

        def wait_for_user(state):
            reply = interrupt(
                {
                    "message": state["message"],
                    "actions": ["retry", "cancel", "catalog_only", "reset"],
                }
            )
            return {"identifier_input": reply["text"], "action": reply["action"]}

        graph = StateGraph(VerificationState)
        graph.add_node("verify", verify)
        graph.add_node("human_input", wait_for_user)
        graph.add_edge(START, "verify")
        graph.add_conditional_edges(
            "verify", lambda state: "human_input" if state["status"] == "waiting" else END
        )
        graph.add_edge("human_input", "verify")
        self._graph = graph.compile(checkpointer=self._checkpointer)

    def new_session(self) -> str:
        with self._registry_lock:
            handle = str(uuid4())
            self._sessions[handle] = _Session()
            return handle

    def _session(self, handle):
        with self._registry_lock:
            session = self._sessions.get(handle)
        if session is None:
            raise ValueError("Unknown or expired session")
        return session

    @staticmethod
    def _config(handle):
        return {"configurable": {"thread_id": handle}, "recursion_limit": 12}

    @staticmethod
    def _text(value):
        if not isinstance(value, str) or len(value) > 2000:
            raise ValueError("Verification input must be text of at most 2000 characters")
        return value

    def _result(self, handle):
        snapshot = self._graph.get_state(self._config(handle))
        values = snapshot.values
        return VerificationResult(
            status=values["status"],
            message=values["message"],
            waiting=bool(snapshot.next),
            pending_request=values.get("pending_request", ""),
            outcome=values.get("verification_outcome", "not_attempted"),
        )

    def start(self, handle: str, request: str, identifier_text: str = "") -> VerificationResult:
        request, identifier_text = self._text(request), self._text(identifier_text)
        session = self._session(handle)
        with session.lock:
            if not session.active:
                raise ValueError("Session expired")
            snapshot = self._graph.get_state(self._config(handle))
            if snapshot.values.get("status") == "retry_limit":
                raise ValueError("Verification retry limit reached; reset the conversation")
            if snapshot.next:
                raise ValueError("Verification is waiting; use reply, cancel, or reset")
            self._graph.invoke(
                {
                    "identifier_input": identifier_text,
                    "pending_request": request,
                    "action": "retry",
                },
                self._config(handle),
            )
            return self._result(handle)

    def reply(
        self,
        handle: str,
        text: str = "",
        *,
        action: Literal["retry", "cancel", "catalog_only"] = "retry",
    ) -> VerificationResult:
        text = self._text(text)
        if action not in {"retry", "cancel", "catalog_only"}:
            raise ValueError("Unsupported verification action")
        session = self._session(handle)
        with session.lock:
            if not session.active:
                raise ValueError("Session expired")
            if not self._graph.get_state(self._config(handle)).next:
                raise ValueError("No pending verification")
            self._graph.invoke(
                Command(resume={"text": text, "action": action}), self._config(handle)
            )
            return self._result(handle)

    def reset(self, handle: str) -> str:
        session = self._session(handle)
        with session.lock:
            session.active = False
            self._checkpointer.delete_thread(handle)
            with self._registry_lock:
                self._sessions.pop(handle, None)
            return self.new_session()

    def call_account_tool(self, handle: str, name: str, arguments: dict) -> str:
        """Resolve identity server-side at execution time; no exported stale bound tools."""
        if name not in ACCOUNT_TOOLS:
            raise ValueError("Unsupported account tool")
        session = self._session(handle)
        with session.lock:
            if not session.active:
                raise ValueError("Session expired")
            state = self._graph.get_state(self._config(handle)).values
            customer_id = state.get("customer_id") if state.get("status") == "verified" else None
            return build_tools(self._database, verified_customer_id=customer_id)[name].invoke(
                arguments
            )

    def with_identity(self, handle: str, callback):
        """Execute application work under session lock with current verified identity.

        Internal integration API, never exposed as a model tool. Reset cannot race this
        callback. Trusted SystemMessage is derived from state, not provided by the caller.
        """
        session = self._session(handle)
        with session.lock:
            if not session.active:
                raise ValueError("Session expired")
            state = self._graph.get_state(self._config(handle)).values
            cid = state.get("customer_id") if state.get("status") == "verified" else None
            messages = (
                [] if cid is None else [SystemMessage(content="Verified customer_id: " + str(cid))]
            )
            return callback(cid, messages)

    def close(self, handle: str):
        session = self._session(handle)
        with session.lock:
            session.active = False
            self._checkpointer.delete_thread(handle)
            with self._registry_lock:
                self._sessions.pop(handle, None)
