"""Server-backed display/action controller. Application services retain all authorization."""

import threading
import time
from dataclasses import dataclass, field
from uuid import uuid4

from music_store.application_contracts import (
    Action,
    ActionKind,
    ApplicationPort,
    DemoLimitReached,
    SessionExpired,
)
from music_store.presentation.contracts import ChatMessage, ViewState


@dataclass
class _Binding:
    handle: str
    delivery_id: str = field(default_factory=lambda: str(uuid4()))
    history: list[ChatMessage] = field(default_factory=list)
    waiting: bool = False
    verified: bool = False
    can_catalog_only: bool = False
    generation: int = 0
    revision: int = 0
    sequence: int = 0
    busy: bool = False
    active: bool = True
    lock: threading.RLock = field(default_factory=threading.RLock)


class PresentationController:
    def __init__(self, service: ApplicationPort, *, formatter=None):
        self.service = service
        self._formatter = formatter or (lambda result: result.text)
        self._views: dict[str, _Binding] = {}
        self._lock = threading.RLock()

    def open(self):
        token = str(uuid4())
        with self._lock:
            self._views[token] = _Binding(self.service.new_session())
        return token

    def _view(self, token):
        with self._lock:
            view = self._views.get(token)
        if view is None or not view.active:
            raise ValueError("Conversation expired; reload this page")
        return view

    @staticmethod
    def _snapshot(view, status, *, draft="", result=None):
        view.revision += 1
        return ViewState(
            tuple(view.history),
            status,
            view.generation,
            view.revision,
            binding_id=view.delivery_id,
            busy=view.busy,
            waiting=view.waiting,
            verified=view.verified,
            can_catalog_only=view.can_catalog_only,
            draft=draft,
            result=result,
        )

    def is_current(self, token, state):
        with self._lock:
            view = self._views.get(token)
        if view is None:
            return False
        with view.lock:
            return (
                view.active
                and state.binding_id == view.delivery_id
                and view.generation == state.generation
                and view.revision == state.revision
            )

    def dispatch(self, token: str, action: Action):
        view = self._view(token)
        with view.lock:
            if not view.active or view.busy:
                return  # No stale/duplicate callback output may overwrite active work.
            if not isinstance(action.kind, ActionKind):
                raise ValueError("Unsupported presentation action")
            invalid = action.kind in {ActionKind.SEND, ActionKind.RESUME_VERIFICATION} and (
                not isinstance(action.text, str)
                or not action.text.strip()
                or len(action.text) > 2000
            )
            if invalid:
                invalid_state = self._snapshot(view, "Enter 1–2000 characters.", draft=action.text)
            else:
                label = {
                    ActionKind.CANCEL_VERIFICATION: "Cancel verification",
                    ActionKind.CATALOG_ONLY: "Continue with catalog only",
                }.get(action.kind, action.text)
                # Identifier input is transient, not retained as a display transcript.
                if action.kind == ActionKind.RESUME_VERIFICATION or view.waiting:
                    label = "[verification response supplied]" if action.text else label
                view.history.append(ChatMessage("user", label))
                view.busy = True
                view.sequence += 1
                sequence = view.sequence
                generation = view.generation
                busy = self._snapshot(view, "Working…")
        if invalid:
            yield invalid_state
            return
        try:
            yield busy  # Never hold a presentation lock across a suspended callback.
            with view.lock:
                if not view.active or view.generation != generation:
                    return
                handle = view.handle
            started = time.perf_counter()
            try:
                reply = self.service.dispatch(handle, action)
                status = (
                    "Verification needed"
                    if reply.session.waiting
                    else reply.status.replace("_", " ")
                )
                status += f" · {time.perf_counter() - started:.1f}s"
                message = self._formatter(reply)
            except DemoLimitReached:
                reply = None
                message = "This public demo has reached its usage limit. Please try later."
                status = "Demo limit reached"
            except SessionExpired:
                reply = None
                message = "Conversation expired; start a new conversation."
                status = "Conversation expired"
            except Exception:
                reply = None
                message = "This request could not finish. Please retry or start a new conversation."
                status = "Request unavailable"
            with view.lock:
                if not view.active or view.generation != generation:
                    return
                if status == "Conversation expired":
                    view.generation += 1
                    view.history.clear()
                    view.waiting = view.can_catalog_only = view.verified = False
                if reply is not None:
                    view.verified = reply.session.verified
                    view.waiting = reply.session.waiting
                    view.can_catalog_only = reply.session.can_catalog_only
                view.history.append(ChatMessage("assistant", message))
                view.history = view.history[-80:]
                view.busy = False
                final = self._snapshot(view, status, result=reply)
            yield final
        finally:
            with view.lock:
                if view.generation == generation and view.sequence == sequence:
                    view.busy = False

    def reset(self, token):
        view = self._view(token)
        with view.lock:
            if not view.active or view.busy:
                return None  # Busy is not a provider abort or optimistic reset.
            try:
                view.handle = self.service.reset(view.handle)
            except SessionExpired:
                view.handle = self.service.new_session()
            view.generation += 1
            view.history.clear()
            view.waiting = view.can_catalog_only = view.verified = False
            return self._snapshot(view, "New conversation · identity cleared")

    def close(self, token):
        with self._lock:
            view = self._views.pop(token, None)
        if view:
            with view.lock:
                view.active = False
                view.generation += 1
                handle = view.handle
            # Existing application serialization may wait for active provider work.
            try:
                self.service.close(handle)
            except SessionExpired:
                pass  # The backend already invalidated this binding.
