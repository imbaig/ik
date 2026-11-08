"""Identifier extraction/matching. Matching sample records is not production authentication."""

import re
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from music_store.db import Database, normalize_phone


class UserInput(BaseModel):
    """Exactly one explicit identifier, or none/ambiguous; never inferred account identity."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: Literal["customer_id", "email", "phone", "none", "ambiguous"]
    identifier: str | None = Field(max_length=254)


class IdentifierExtractor(Protocol):
    def extract(self, message: str) -> UserInput: ...


def match_customer(database: Database, candidate: UserInput, original: str) -> int | None:
    """Deterministic existence lookup, not trusting model-generated IDs or fuzzy identity."""
    value = candidate.identifier
    if value is None or candidate.kind in {"none", "ambiguous"}:
        return None
    value = value.strip()
    if candidate.kind == "customer_id":
        if not re.fullmatch(r"[0-9]{1,18}", value) or int(value) < 1:
            return None
        if re.findall(r"(?<![\w.+-])[+-]?[0-9]+(?![\w.])", original) != [value] or "@" in original:
            return None
        rows = database.query(
            "SELECT CustomerId FROM Customer WHERE CustomerId=:cid", {"cid": int(value)}
        )
    elif candidate.kind == "email":
        explicit = re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", original)
        if len(explicit) != 1 or value.casefold() != explicit[0].casefold():
            return None
        remainder = original.replace(explicit[0], "")
        if re.search(r"[0-9]", remainder):
            return None
        rows = database.query(
            "SELECT CustomerId FROM Customer WHERE LOWER(Email)=LOWER(:email)", {"email": value}
        )
    else:
        normalized = normalize_phone(value)
        spans = re.findall(r"\+?[0-9][0-9 ()\-\.]{5,}[0-9]", original)
        if len(spans) != 1 or not normalized or normalized != normalize_phone(spans[0]):
            return None
        remainder = original.replace(spans[0], "")
        if re.search(r"[0-9@]", remainder):
            return None
        # Phone formats are inconsistent upstream; no SQL concatenation or fuzzy matching.
        rows = [
            row
            for row in database.query("SELECT CustomerId, Phone FROM Customer")
            if normalize_phone(row["Phone"]) == normalized
        ]
    return rows[0]["CustomerId"] if len(rows) == 1 else None
