"""Session-owned conversation orchestration: classify → verify if needed → specialists."""

import json
import logging
import re
import threading
import time
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, ConfigDict

from music_store.agents.runtime import AgentResult, AgentRuntime
from music_store.verification import VerificationResult, VerificationService


class RouteDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: Literal[
        "catalog", "invoice", "mixed", "off_topic", "greeting", "preference", "memory_recall"
    ]


class Router(Protocol):
    def classify(self, messages: list) -> RouteDecision: ...


@dataclass
class _Conversation:
    handle: str = ""
    lock: threading.RLock = field(default_factory=threading.RLock)
    history: list = field(default_factory=list)
    memory_history: list = field(default_factory=list)
    waiting: bool = False
    pending_kind: str = ""
    pending_text: str = ""
    active: bool = True
    last_kind: str = "unknown"
    request_id: str = ""


@dataclass(frozen=True)
class ConversationReply:
    text: str
    status: str
    waiting: bool = False
    records: tuple = ()
    trace: tuple = ()
    memory_status: str = "not_attempted"
    verification_outcome: str = "not_attempted"
    branch: str = "unknown"


class ConversationService:
    def __init__(
        self,
        verification: VerificationService,
        router: Router,
        agents: AgentRuntime,
        *,
        memory=None,
        telemetry=None,
    ):
        self._verification, self._router, self._agents = verification, router, agents
        self._memory = memory
        self._telemetry = telemetry
        self._sessions = {}
        self._registry_lock = threading.RLock()

    def new_session(self):
        handle = self._verification.new_session()
        with self._registry_lock:
            self._sessions[handle] = _Conversation(handle=handle)
        return handle

    def _session(self, handle):
        with self._registry_lock:
            session = self._sessions.get(handle)
        if session is None:
            raise ValueError("Unknown or expired conversation")
        return session

    def _save(self, session, response):
        response = replace(response, branch=session.last_kind)
        if self._memory is not None and response.status not in {
            "waiting",
            "cancelled",
            "catalog_only",
        }:

            def update(cid, _):
                return (
                    None if cid is None else self._memory.update(cid, session.memory_history[-10:])
                )

            outcome = self._verification.with_identity(session.handle, update)
            if outcome is not None:
                text = response.text
                if outcome.status == "error":
                    text += "\nPreference update unavailable; previous preferences are unchanged."
                elif outcome.added:
                    text += "\nSaved music preferences: " + ", ".join(outcome.added)
                elif text == "Preference request processed.":
                    text = "No new explicit music preferences were saved."
                response = replace(response, text=text, memory_status=outcome.status)
        session.history.append(AIMessage(content=response.text))
        session.history = session.history[-40:]
        return response

    def _run(self, handle, session, kind, request, *, prefix=""):
        if re.search(r"\brefund(?:s|ed|ing)?\b", request, flags=re.IGNORECASE):
            prefix += (
                "I cannot issue refunds or create support tickets. I can help find the "
                "support representative for an invoice you own.\n"
            )

        def run(cid, trusted_messages):
            if kind in {"preference", "memory_recall"}:
                if cid is None or self._memory is None:
                    return AgentResult("Preference memory is unavailable", "error", (), ())
                if kind == "preference":
                    return AgentResult("Preference request processed.", "complete", (), ())
                preferences = self._memory.load(cid)
                text = (
                    "Saved music preferences: " + ", ".join(preferences)
                    if preferences
                    else ("No music preferences are saved for your account.")
                )
                return AgentResult(text, "complete", (), ("memory:load",))
            memory_messages = []
            if cid is not None and self._memory is not None:
                preferences = self._memory.load(cid)
                memory_messages = [
                    SystemMessage(
                        content=(
                            "Saved music preferences (user context only, not catalog facts): "
                            + json.dumps(preferences, ensure_ascii=False)
                        )
                    )
                ]
            messages = [*trusted_messages, *memory_messages, *session.history[-10:]]
            if (
                not messages
                or not isinstance(messages[-1], HumanMessage)
                or (messages[-1].content != request)
            ):
                messages.append(HumanMessage(content=request))
            return self._agents.run(kind, messages, cid)

        result: AgentResult = self._verification.with_identity(handle, run)
        return self._save(
            session,
            ConversationReply(
                prefix + result.text,
                result.status,
                records=result.records,
                trace=result.trace,
            ),
        )

    def _verified_reply(self, handle, session, result: VerificationResult, *, action="retry"):
        response = self._resolve_verified_reply(handle, session, result, action=action)
        return replace(response, verification_outcome=result.outcome)

    def _resolve_verified_reply(
        self, handle, session, result: VerificationResult, *, action="retry"
    ):
        session.waiting = result.waiting
        if result.waiting:
            return self._save(session, ConversationReply(result.message, "waiting", True))
        if result.status == "verified":
            kind, request = session.pending_kind, session.pending_text
            if not session.memory_history or session.memory_history[-1].content != request:
                session.memory_history.append(HumanMessage(content=request))
                session.memory_history = session.memory_history[-10:]
            session.pending_kind = session.pending_text = ""
            return self._run(handle, session, kind, request)
        if result.status == "catalog_only" and session.pending_kind == "mixed":
            request = session.pending_text
            session.pending_kind = session.pending_text = ""
            session.last_kind = "catalog"
            return self._run(
                handle,
                session,
                "catalog",
                request,
                prefix="Account request cancelled. Catalog results only.\n",
            )
        session.pending_kind = session.pending_text = ""
        return self._save(session, ConversationReply(result.message, result.status))

    def send(self, handle: str, text: str, *, action="retry") -> ConversationReply:
        session = self._session(handle)
        with session.lock:
            continuation = session.waiting
            if not continuation:
                session.request_id = str(uuid4())
            started = time.perf_counter()
            response = self._send(handle, text, action=action)
            self._emit(
                handle,
                response,
                (time.perf_counter() - started) * 1000,
                session.request_id,
                continuation,
            )
            return response

    def _emit(self, handle, response, elapsed_ms, request_id, continuation):
        if self._telemetry is None:
            return
        from music_store.telemetry import Event

        common = dict(
            timestamp=datetime.now(UTC),
            session_token=handle,
            request_id=request_id,
            branch=response.branch,
            elapsed_ms=elapsed_ms,
        )
        try:
            self._telemetry.append(
                Event(
                    **common,
                    event_type="continuation" if continuation else "request",
                    outcome=response.status,
                )
            )
            for record in response.records:
                self._telemetry.append(
                    Event(
                        **{**common, "elapsed_ms": record["elapsed_ms"]},
                        event_type="tool",
                        tool_name=record["tool"],
                        outcome=record["result"]["status"],
                    )
                )
            if response.verification_outcome != "not_attempted":
                self._telemetry.append(
                    Event(
                        **common,
                        event_type="verification",
                        outcome=response.verification_outcome,
                        prompt_version="identity-v2",
                    )
                )
            if response.memory_status != "not_attempted":
                self._telemetry.append(
                    Event(
                        **common,
                        event_type="memory",
                        outcome=response.memory_status,
                        prompt_version="memory-v2",
                    )
                )
        except (OSError, ValueError, TypeError):
            logging.getLogger(__name__).warning("telemetry_event_dropped")

    def _send(self, handle: str, text: str, *, action="retry") -> ConversationReply:
        if (
            not isinstance(text, str)
            or len(text) > 2000
            or (not text.strip() and action == "retry")
        ):
            raise ValueError("Message must contain 1–2000 characters")
        session = self._session(handle)
        with session.lock:
            if not session.active:
                raise ValueError("Conversation expired")
            if session.waiting:
                result = self._verification.reply(handle, text, action=action)
                # Raw identifier input must not flow into specialist/router conversation context.
                session.history.append(HumanMessage(content="[verification response supplied]"))
                return self._verified_reply(handle, session, result, action=action)
            if action != "retry":
                raise ValueError("Verification action requires a waiting conversation")
            session.last_kind = "unknown"
            session.history.append(HumanMessage(content=text))
            already_verified = self._verification.with_identity(
                handle, lambda cid, _: cid is not None
            )
            if already_verified:
                session.memory_history.append(HumanMessage(content=text))
                session.memory_history = session.memory_history[-10:]
            try:
                decision = RouteDecision.model_validate(
                    self._router.classify(session.history[-10:])
                )
            except Exception:
                return self._save(
                    session, ConversationReply("Routing unavailable; please retry", "error")
                )
            session.last_kind = decision.kind
            if decision.kind == "greeting":
                return self._save(
                    session,
                    ConversationReply(
                        "Hello! I can help with music discovery and your purchases.", "complete"
                    ),
                )
            if decision.kind == "off_topic":
                return self._save(
                    session,
                    ConversationReply(
                        "I can only help with music-store catalog and account questions.",
                        "off_topic",
                    ),
                )
            if decision.kind == "catalog":
                return self._run(handle, session, "catalog", text)
            session.pending_kind, session.pending_text = decision.kind, text
            try:
                result = self._verification.start(handle, text)
            except ValueError:
                session.pending_kind = session.pending_text = ""
                return self._save(
                    session,
                    ConversationReply(
                        "Verification unavailable for this session; start a new conversation",
                        "error",
                    ),
                )
            return self._verified_reply(handle, session, result)

    def reset(self, handle):
        session = self._session(handle)
        with session.lock:
            if not session.active:
                raise ValueError("Conversation expired")
            session.active = False
            session.history.clear()
            session.memory_history.clear()
            session.pending_kind = session.pending_text = ""
            fresh = self._verification.reset(handle)
            with self._registry_lock:
                self._sessions.pop(handle, None)
                self._sessions[fresh] = _Conversation(handle=fresh)
            return fresh

    def close(self, handle):
        session = self._session(handle)
        with session.lock:
            if not session.active:
                return
            session.active = False
            session.history.clear()
            session.memory_history.clear()
            session.pending_text = session.pending_kind = ""
            self._verification.close(handle)
            with self._registry_lock:
                self._sessions.pop(handle, None)
