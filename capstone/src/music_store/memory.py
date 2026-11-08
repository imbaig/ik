"""Process-local preference memory with trusted customer scope and conservative evidence checks."""

import re
import threading
from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from langchain_core.messages import HumanMessage
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, ConfigDict, Field

from music_store.db import DATASET_REVISION

EVIDENCE_FILTER_VERSION = "evidence-v3"


class UserProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    customer_id: str | None
    music_preferences: list[str] = Field(max_length=32)


class PreferenceExtractor(Protocol):
    def extract(self, user_messages: list[str]) -> UserProfile: ...


def _customer_id(value):
    if type(value) is not int or not 0 < value < 10**18:
        raise ValueError("Memory requires a verified positive customer ID")
    return str(value)


def supported_preferences(candidates: list[str], user_messages: list[str]) -> tuple[str, ...]:
    """Reject unsupported model candidates; precision-first, not a complete language parser.

    Only literal phrases inside explicit positive first-person statements are accepted.
    Semantic extraction is the LLM's role. These additional checks deliberately reject
    ambiguous/quoted/negative material even when the model returns it as a preference.
    """
    # Replace literal candidate spans before clause segmentation: punctuation inside an
    # artist name (e.g. an exclamation mark) must not become a sentence boundary.
    normalized = sorted(
        {
            p.strip().casefold()
            for p in candidates
            if p.strip()
            and len(p.strip()) <= 100
            and not any(c in p for c in "\n\r<>@?")
            and not re.search(
                r"\b(?:but|not|never|hate|dislike|if|except|however|"
                r"my friend|I (?:love|like|enjoy|prefer))\b",
                p,
                re.IGNORECASE,
            )
        },
        key=len,
        reverse=True,
    )
    nonce = uuid4().hex
    while any(nonce in text for text in [*user_messages, *normalized]):
        nonce = uuid4().hex
    markers = {p: "__preference_" + nonce + "_" + str(i) + "__" for i, p in enumerate(normalized)}
    positive_tails = []
    for message in user_messages:
        # A removed quotation leaves a clause boundary, so reported speech does not
        # swallow a subsequent explicit statement in the user's own voice.
        plain = re.sub(r'"[^"\n]*"|`[^`\n]*`|“[^”\n]*”|‘[^’\n]*’', ". ", message)
        plain = re.sub(r"(?<!\w)'[^'\n]*'(?!\w)", ". ", plain)
        for preference, marker in markers.items():
            plain = re.sub(
                r"(?<!\w)" + re.escape(preference) + r"(?!\w)", marker, plain, flags=re.IGNORECASE
            )
        for sentence in re.split(
            r"(?<=[!?;\n])|(?<=\.)\s+(?=[A-Z])|\bbut\b|"
            r",\s+(?:and\s+)?(?=(?:my (?:friend|colleague)|she|he|they)\b)",
            plain,
        ):
            sentence = sentence.strip()
            if sentence.endswith("?") or re.search(
                r"\b(?:if|suppose|pretend|imagine|fictional|hypothetical|example|friend|"
                r"she said|he said|"
                r"you said|assistant)\b",
                sentence,
                flags=re.IGNORECASE,
            ):
                continue
            for match in re.finditer(
                r"\b(?:I\s+(?:(?:really|also|actually|do)\s+)?(?:love|like|enjoy|prefer|adore)|"
                r"I(?:'m| am)\s+(?:a\s+fan\s+of|into)|my\s+favou?rites?"
                r"(?:\s+(?:music|artists?|genres?|bands?|musicians?|singers?|composers?))?\s+(?:is|are)|"
                r"my\s+(?:musical\s+)?tastes\s+include)\s+(.+)",
                sentence,
                flags=re.IGNORECASE,
            ):
                prefix = sentence[: match.start()]
                if re.search(
                    r"\b(?:never said|not saying|not true|isn't true|is not true|false that|"
                    r"don't think|do not think|quote|said|says|claims|wrote|writes)\b",
                    prefix,
                    flags=re.IGNORECASE,
                ):
                    continue
                tail = re.split(
                    r"\b(?:but|not|except|however|no longer|hate|dislike|loathe|never|"
                    r"don['’]t|do not|can['’]t|cannot|avoid|without|excluding)\b",
                    match[1],
                    maxsplit=1,
                    flags=re.IGNORECASE,
                )[0]
                positive_tails.append(tail)
    return tuple(
        sorted(p for p, marker in markers.items() if any(marker in tail for tail in positive_tails))
    )


class PreferenceStore:
    def __init__(self, *, dataset_version: str = DATASET_REVISION):
        if not dataset_version:
            raise ValueError("Dataset version is required")
        self._version = dataset_version
        self._store = InMemoryStore()
        self._lock = threading.RLock()

    def _namespace(self, customer_id):
        return ("memory_profile", self._version, _customer_id(customer_id))

    def load(self, customer_id: int) -> tuple[str, ...]:
        namespace = self._namespace(customer_id)
        with self._lock:
            item = self._store.get(namespace, "user_memory")
            return tuple(item.value["music_preferences"]) if item else ()

    def merge(self, customer_id: int, preferences: tuple[str, ...]) -> tuple[str, ...]:
        namespace = self._namespace(customer_id)
        with self._lock:
            existing = self.load(customer_id)
            merged = tuple(sorted(set(existing).union(preferences)))
            if merged != existing:
                self._store.put(namespace, "user_memory", {"music_preferences": list(merged)})
            return merged


@dataclass(frozen=True)
class MemoryUpdate:
    status: str
    added: tuple[str, ...] = ()


class PreferenceMemory:
    def __init__(self, store: PreferenceStore, extractor: PreferenceExtractor):
        self.store, self.extractor = store, extractor

    def load(self, customer_id: int) -> tuple[str, ...]:
        return self.store.load(customer_id)

    def update(self, customer_id: int, messages: list) -> MemoryUpdate:
        _customer_id(customer_id)
        sources = [
            m.content
            for m in messages[-10:]
            if isinstance(m, HumanMessage)
            and m.name is None
            and isinstance(m.content, str)
            and m.content != "[verification response supplied]"
        ]
        if not sources:
            return MemoryUpdate("unchanged")
        try:
            profile = UserProfile.model_validate(self.extractor.extract(sources))
            # A model-provided customer_id is never used to select storage namespace.
            valid = supported_preferences(profile.music_preferences, sources)
            before = self.store.load(customer_id)
            if not valid:
                return MemoryUpdate("unchanged")
            merged = self.store.merge(customer_id, valid)
            return MemoryUpdate(
                "updated" if merged != before else "unchanged",
                tuple(sorted(set(valid) - set(before))),
            )
        except Exception:
            # Failed extraction/validation must not erase memory or emit raw provider errors.
            return MemoryUpdate("error")
