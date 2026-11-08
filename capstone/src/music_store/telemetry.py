"""Local allowlisted outcome events and on-demand UTC-window reporting, no raw chat data."""

import argparse
import json
import math
import os
import tempfile
import threading
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from statistics import median
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from music_store.db import DATASET_REVISION

TOOL_NAMES = frozenset(
    {
        "get_albums_by_artist",
        "get_tracks_by_artist",
        "get_songs_by_genre",
        "search_songs_by_title",
        "get_track_details",
        "get_invoices_by_customer_sorted_by_date",
        "get_purchased_tracks",
        "get_support_rep_by_invoice",
        "get_invoice_line_items",
    }
)


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    timestamp: datetime
    session_token: UUID
    request_id: UUID
    event_type: Literal["request", "continuation", "tool", "verification", "memory"]
    branch: Literal[
        "catalog",
        "invoice",
        "mixed",
        "off_topic",
        "greeting",
        "preference",
        "memory_recall",
        "unknown",
    ]
    outcome: Literal[
        "complete",
        "error",
        "waiting",
        "cancelled",
        "catalog_only",
        "retry_limit",
        "off_topic",
        "ok",
        "not_found",
        "invalid_input",
        "verified",
        "provider_error",
        "database_error",
        "updated",
        "unchanged",
    ]
    elapsed_ms: float = Field(ge=0, allow_inf_nan=False)
    tool_name: str | None = None
    prompt_version: Literal[
        "agents-v1",
        "agents-v2",
        "agents-v3",
        "agents-v4",
        "identity-v1",
        "identity-v2",
        "memory-v1",
        "memory-v2",
    ] = "agents-v4"
    config_version: Literal["config-v1"] = "config-v1"
    dataset_version: Literal[DATASET_REVISION] = DATASET_REVISION

    @field_validator("timestamp")
    @classmethod
    def aware_timestamp(cls, value):
        if value.tzinfo is None:
            raise ValueError("Timestamp must include timezone")
        return value.astimezone(UTC)

    @field_validator("tool_name")
    @classmethod
    def allow_tool(cls, value):
        if value is not None and value not in TOOL_NAMES:
            raise ValueError("Unknown tool")
        return value


class EventSink:
    """Single-process local sink. Multiple worker processes are outside this demo scope."""

    def __init__(self, path: Path = Path(".cache/telemetry/events.jsonl")):
        self.path = Path(path)
        self._lock = threading.RLock()

    def append(self, event: Event):
        data = (event.model_dump_json() + "\n").encode()
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(self.path, flags, 0o600)
            try:
                os.fchmod(descriptor, 0o600)
                view = memoryview(data)
                while view:
                    written = os.write(descriptor, view)
                    if written == 0:
                        raise OSError("Telemetry write failed")
                    view = view[written:]
            finally:
                os.close(descriptor)

    def read(self):
        with self._lock:
            if not self.path.exists():
                return [], 0
            events, invalid = [], 0
            with self.path.open() as handle:
                for line in handle:
                    try:
                        events.append(Event.model_validate_json(line))
                    except ValueError:
                        invalid += 1
            return events, invalid

    def cleanup(self, *, now: datetime | None = None, days: int = 7):
        if days < 1:
            raise ValueError("Retention days must be positive")
        now = now or datetime.now(UTC)
        if now.tzinfo is None:
            raise ValueError("Timezone required")
        with self._lock:
            events, invalid = self.read()
            retained = [e for e in events if e.timestamp >= now - timedelta(days=days)]
            self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with tempfile.NamedTemporaryFile(
                mode="w", dir=self.path.parent, delete=False
            ) as handle:
                temp = Path(handle.name)
                for event in retained:
                    handle.write(event.model_dump_json() + "\n")
            try:
                os.replace(temp, self.path)
            finally:
                temp.unlink(missing_ok=True)
            return {"removed": len(events) - len(retained), "discarded_invalid": invalid}


def report(sink: EventSink, *, start: date | None = None, end: date | None = None):
    if start and end and start > end:
        raise ValueError("Start date must precede end date")
    events, invalid = sink.read()
    events = [
        e
        for e in events
        if (start is None or e.timestamp.date() >= start)
        and (end is None or e.timestamp.date() <= end)
    ]
    requests = [e for e in events if e.event_type in {"request", "continuation"}]
    tasks = {e.request_id: e for e in requests if e.event_type == "request"}
    final = {e.request_id: e for e in requests}
    mixed = {key for key, e in tasks.items() if e.branch == "mixed"}
    tools = [e for e in events if e.event_type == "tool"]
    verification = [e for e in events if e.event_type == "verification"]
    discovery_sessions = {e.session_token for e in requests if e.branch in {"catalog", "mixed"}}
    discovery_results = {
        e.session_token
        for e in tools
        if e.branch in {"catalog", "mixed"}
        and e.tool_name
        not in {
            "get_invoices_by_customer_sorted_by_date",
            "get_purchased_tracks",
            "get_support_rep_by_invoice",
            "get_invoice_line_items",
        }
        and e.outcome == "ok"
    }
    latency = sorted(e.elapsed_ms for e in requests)
    return {
        "timezone": "UTC",
        "start": str(start) if start else None,
        "end": str(end) if end else None,
        "request_count": len(requests),
        "task_count": len(tasks),
        "invalid_event_lines": invalid,
        "requests_by_branch": dict(Counter(e.branch for e in requests)),
        "requests_by_outcome": dict(Counter(e.outcome for e in requests)),
        "discovery_sessions": len(discovery_sessions),
        "discovery_sessions_with_results": len(discovery_results & discovery_sessions),
        "discovery_success_proxy": len(discovery_results & discovery_sessions)
        / len(discovery_sessions)
        if discovery_sessions
        else None,
        "mixed_requests": len(mixed),
        "mixed_completed": sum(
            final[key].branch == "mixed" and final[key].outcome == "complete" for key in mixed
        ),
        "account_tool_outcomes": dict(
            Counter(
                e.outcome
                for e in tools
                if e.tool_name
                in {
                    "get_invoices_by_customer_sorted_by_date",
                    "get_purchased_tracks",
                    "get_support_rep_by_invoice",
                    "get_invoice_line_items",
                }
            )
        ),
        "verification_attempts": len(verification),
        "verification_outcomes": dict(Counter(e.outcome for e in verification)),
        "verification_no_match_rate": sum(e.outcome == "not_found" for e in verification)
        / len(verification)
        if verification
        else None,
        "tool_outcomes": dict(Counter(e.outcome for e in tools)),
        "memory_outcomes": dict(Counter(e.outcome for e in events if e.event_type == "memory")),
        "latency_sample_count": len(latency),
        "latency_p50_ms": median(latency) if latency else None,
        "latency_p95_ms": latency[math.ceil(0.95 * len(latency)) - 1] if latency else None,
        "limitations": [
            "Results returned is a discovery proxy, not conversion or revenue",
            "Account tool outcomes do not prove avoided support contacts",
            "Model retry/timeout attempt counts are not instrumented yet",
            "Memory precision/recall requires labeled evaluation, not these events",
            "Task completion effort requires labeled tasks, not request counts",
            "Tasks started outside the report window are excluded from mixed task totals",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=Path(".cache/telemetry/events.jsonl"))
    parser.add_argument("--start", type=date.fromisoformat)
    parser.add_argument("--end", type=date.fromisoformat)
    parser.add_argument(
        "--cleanup", action="store_true", help="Explicitly purge raw events older than7 days"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sink = EventSink(args.events)
    data = report(sink, start=args.start, end=args.end)
    if args.cleanup:
        data["cleanup"] = sink.cleanup()
    payload = json.dumps(data, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n")
    print(payload)


if __name__ == "__main__":
    main()
