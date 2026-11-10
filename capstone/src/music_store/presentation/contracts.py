"""Immutable view projections, never trusted identity or workflow authority."""

from dataclasses import dataclass
from typing import Protocol

from music_store.application_contracts import ApplicationResult


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ViewState:
    messages: tuple[ChatMessage, ...]
    status: str
    generation: int
    revision: int
    binding_id: str
    busy: bool = False
    waiting: bool = False
    can_catalog_only: bool = False
    draft: str = ""
    result: ApplicationResult | None = None


class ViewPort(Protocol):
    def render(self, state: ViewState) -> None: ...
