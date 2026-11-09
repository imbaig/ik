"""Neutral in-process application port. No widgets, model clients or presentation imports."""

import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class SessionExpired(ValueError):
    """The application no longer owns this conversation handle."""


class ActionKind(StrEnum):
    SEND = "send"
    RESUME_VERIFICATION = "resume_verification"
    CANCEL_VERIFICATION = "cancel_verification"
    CATALOG_ONLY = "catalog_only"


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    text: str = ""


@dataclass(frozen=True)
class SessionInfo:
    """Display hints only. The application rechecks authoritative state on every action."""

    waiting: bool
    verified: bool
    can_catalog_only: bool


@dataclass(frozen=True)
class FactSection:
    """Detached immutable JSON envelope; decoding returns a fresh structured copy.

    Exact JSON strings, numeric types, insertion order and metadata survive projection.
    This is observed tool data, never JSON extracted from customer-facing prose.
    """

    tool: str
    envelope_json: str
    elapsed_ms: float

    @classmethod
    def from_record(cls, record):
        return cls(
            record["tool"],
            json.dumps(record["result"], ensure_ascii=False, allow_nan=False),
            record["elapsed_ms"],
        )

    @property
    def envelope(self):
        return json.loads(self.envelope_json)

    def to_record(self):
        return {"tool": self.tool, "result": self.envelope, "elapsed_ms": self.elapsed_ms}


@dataclass(frozen=True)
class ApplicationResult:
    # Staged compatibility text is still produced only by the existing grounded service.
    # FactSections/status remain separate; no adapter parses this text to obtain facts.
    text: str
    status: str
    session: SessionInfo
    facts: tuple[FactSection, ...] = ()
    branch: str = "unknown"
    verification_outcome: str = "not_attempted"
    memory_status: str = "not_attempted"
    request_id: str = ""


class ApplicationPort(Protocol):
    def new_session(self) -> str: ...

    def dispatch(self, handle: str, action: Action) -> ApplicationResult: ...

    def reset(self, handle: str) -> str: ...

    def close(self, handle: str) -> None: ...
