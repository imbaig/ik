"""Local live-conversation evaluation; SQL truth checks are not a semantic LLM judge."""

import argparse
import hashlib
import json
import math
import platform
import time
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from statistics import median
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from music_store.db import DATASET_REVISION
from music_store.record_formatting import render_records
from music_store.verification import ACCOUNT_TOOLS


class Step(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(default="", max_length=2000)
    action: Literal["retry", "cancel", "catalog_only", "reset"] = "retry"
    expected_status: list[str] = Field(default_factory=list)
    expected_branch: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    expected_lookups: dict[str, dict[str, str]] = Field(default_factory=dict)
    expect_no_records: bool = False
    expect_no_data: bool = False
    oracle_customer_id: int | None = Field(default=None, ge=1)
    expected_preferences: list[str] | None = None
    must_contain: list[str] = Field(default_factory=list)
    must_not_contain: list[str] = Field(default_factory=list)
    expect_nonempty: bool = False


class Case(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^[A-Za-z0-9_-]+$")
    description: str
    steps: list[Step] = Field(min_length=1)
    customer_id: int | None = Field(default=None, ge=1)
    tags: list[str] = Field(default_factory=list)


def canonical(row):
    return {
        key: format(Decimal(str(value)), ".2f")
        if key in {"Total", "UnitPrice"} and value is not None
        else value
        for key, value in row.items()
    }


def truth_rows(database, tool, customer_id):
    """Independent full-table reference projections; no production tool calls reused.

    These validate returned facts/ownership, not completeness of a search selection.
    Required tools/content and result expectations grade intent separately.
    """
    if tool == "get_albums_by_artist":
        return database.query(
            "SELECT AlbumId, Title, Album.ArtistId, Artist.Name AS Artist "
            "FROM Album JOIN Artist USING (ArtistId)"
        )
    if tool in {
        "get_tracks_by_artist",
        "search_songs_by_title",
        "get_songs_by_genre",
        "get_track_details",
    }:
        rows = database.query(
            "SELECT Track.*, Album.Title AS Album, Artist.ArtistId, Artist.Name AS Artist, "
            "Genre.Name AS Genre, MediaType.Name AS MediaType FROM Track "
            "JOIN Album USING (AlbumId) JOIN Artist USING (ArtistId) "
            "LEFT JOIN Genre USING (GenreId) JOIN MediaType USING (MediaTypeId)"
        )
        keys = {
            "get_tracks_by_artist": ["TrackId", "Name", "Artist", "Album", "UnitPrice"],
            "search_songs_by_title": ["TrackId", "Name", "Artist", "Album", "UnitPrice"],
            "get_songs_by_genre": [
                "TrackId",
                "Name",
                "ArtistId",
                "Artist",
                "Album",
                "Genre",
                "UnitPrice",
            ],
            "get_track_details": [
                "TrackId",
                "Name",
                "AlbumId",
                "MediaTypeId",
                "GenreId",
                "Composer",
                "Milliseconds",
                "Bytes",
                "UnitPrice",
                "Album",
                "ArtistId",
                "Artist",
                "Genre",
                "MediaType",
            ],
        }[tool]
        return [{key: row[key] for key in keys} for row in rows]
    if customer_id is None:
        return []
    if tool == "get_invoices_by_customer_sorted_by_date":
        return database.query(
            "SELECT InvoiceId, InvoiceDate, Total, BillingAddress, BillingCity, BillingState, "
            "BillingCountry, BillingPostalCode FROM Invoice WHERE CustomerId=:cid "
            "ORDER BY InvoiceDate DESC, InvoiceId DESC",
            {"cid": customer_id},
        )
    if tool in {"get_invoice_line_items", "get_purchased_tracks"}:
        return database.query(
            "SELECT InvoiceLineId, Invoice.InvoiceId, Track.TrackId, Track.Name, Quantity, "
            "InvoiceLine.UnitPrice FROM InvoiceLine JOIN Invoice USING (InvoiceId) "
            "JOIN Track USING (TrackId) WHERE Invoice.CustomerId=:cid",
            {"cid": customer_id},
        )
    if tool == "get_support_rep_by_invoice":
        return database.query(
            "SELECT DISTINCT EmployeeId, Employee.FirstName, Employee.LastName, Employee.Email, "
            "Employee.Phone FROM Customer JOIN Employee ON SupportRepId=EmployeeId "
            "WHERE CustomerId=:cid",
            {"cid": customer_id},
        )
    raise ValueError("Unknown evaluation tool")


def expected_lookup(database, tool, args, customer_id):
    rows = [canonical(r) for r in truth_rows(database, tool, customer_id)]
    if tool in {"get_albums_by_artist", "get_tracks_by_artist"}:
        rows = [r for r in rows if args["artist_name"].casefold() in r["Artist"].casefold()]
    elif tool == "search_songs_by_title":
        rows = [r for r in rows if args["title"].casefold() in r["Name"].casefold()]
    elif tool == "get_track_details":
        rows = [r for r in rows if r["TrackId"] == int(args["track_id"])]
    elif tool == "get_songs_by_genre":
        rows = [r for r in rows if args["genre_name"].casefold() in r["Genre"].casefold()]
    elif tool in {"get_invoice_line_items", "get_support_rep_by_invoice"}:
        owned = database.query(
            "SELECT InvoiceId FROM Invoice WHERE InvoiceId=:iid AND CustomerId=:cid",
            {"iid": int(args["invoice_id"]), "cid": customer_id},
        )
        if not owned:
            rows = []
        elif tool == "get_invoice_line_items":
            rows = [r for r in rows if r["InvoiceId"] == int(args["invoice_id"])]
    total = len(rows)
    if tool == "get_albums_by_artist":
        rows.sort(key=lambda r: r["AlbumId"])
    elif tool == "get_songs_by_genre":
        representatives = {}
        for row in sorted(rows, key=lambda r: r["TrackId"]):
            representatives.setdefault(row["ArtistId"], row)
        rows = [representatives[key] for key in sorted(representatives)][:10]
    elif tool in {"get_tracks_by_artist", "search_songs_by_title", "get_track_details"}:
        rows.sort(key=lambda r: r["TrackId"])
        rows = rows[: 20 if tool == "get_tracks_by_artist" else 10]
    elif tool == "get_purchased_tracks":
        rows.sort(key=lambda r: (-Decimal(r["UnitPrice"]), r["InvoiceLineId"]))
    elif tool == "get_invoice_line_items":
        rows.sort(key=lambda r: r["InvoiceLineId"])
    return rows, total


def grade_reply(database, reply, step: Step, customer_id, trusted_preferences=()):
    checks = {}
    if step.expected_status:
        checks["status"] = reply.status in step.expected_status
    if step.expected_branch:
        checks["branch"] = reply.branch in step.expected_branch
    for tool, arguments in step.expected_lookups.items():
        expected_rows, expected_total = expected_lookup(database, tool, arguments, customer_id)
        matches = [r["result"] for r in reply.records if r["tool"] == tool]
        checks["exact_lookup_" + tool] = bool(matches) and all(
            [canonical(row) for row in result["data"]] == expected_rows
            and result["total_count"] == expected_total
            for result in matches
        )
    names = {r["tool"] for r in reply.records}
    checks["required_tools"] = set(step.required_tools) <= names
    if step.expect_no_records:
        checks["no_records"] = not reply.records
        checks["no_specialist_dispatch"] = not any(t.startswith("dispatch:") for t in reply.trace)
    if step.expect_no_data:
        checks["no_data"] = not any(r["result"]["data"] for r in reply.records)
    if step.expect_nonempty:
        checks["nonempty_results"] = any(r["result"]["data"] for r in reply.records)
    checks["required_text"] = all(t.casefold() in reply.text.casefold() for t in step.must_contain)
    checks["forbidden_text"] = all(
        t.casefold() not in reply.text.casefold() for t in step.must_not_contain
    )
    checks["sql_facts_and_ownership"] = True
    checks["envelope_consistency"] = True
    for record in reply.records:
        result = record["result"]
        rows = result["data"]
        references = [canonical(row) for row in truth_rows(database, record["tool"], customer_id)]
        checks["sql_facts_and_ownership"] &= all(canonical(row) in references for row in rows)
        checks["envelope_consistency"] &= (
            result["returned_count"] == len(rows)
            and result["total_count"] >= len(rows)
            and result["truncated"] == (result["total_count"] > len(rows))
            and (not rows or result["status"] == "ok")
        )
        if record["tool"] in ACCOUNT_TOOLS and customer_id is None:
            checks["sql_facts_and_ownership"] &= not rows
    if reply.branch == "mixed" and reply.status == "complete":
        phases = [t for t in reply.trace if t.startswith("dispatch:")]
        checks["mixed_invoice_first"] = phases == ["dispatch:invoice", "dispatch:catalog"]
    if reply.records:
        rendered = render_records(reply.records)
        checks["tool_render_present"] = rendered in reply.text
        if reply.status == "complete":
            remainder = reply.text.replace(rendered, "", 1)
            remainder = remainder.replace("Account request cancelled. Catalog results only.\n", "")
            remainder = remainder.replace(
                "I cannot issue refunds or create support tickets. I can help find the "
                "support representative for an invoice you own.\n",
                "",
            )
            marker = "\nSaved music preferences: "
            if marker in remainder:
                prefix, _, saved = remainder.partition(marker)
                if saved and set(saved.split(", ")) <= set(trusted_preferences):
                    remainder = prefix
            remainder = remainder.replace(
                "\nPreference update unavailable; previous preferences are unchanged.", ""
            )
            checks["no_unexpected_tool_answer_prose"] = not remainder.strip()
    return checks


def evaluate(cases, database, service_factory, *, progress=None):
    results, transcripts, latencies = [], [], []
    for case in cases:
        service = service_factory()
        handle = service.new_session()
        rows = []
        try:
            for index, step in enumerate(case.steps):
                if step.action == "reset":
                    old_handle = handle
                    handle = service.reset(handle)
                    clean = service._verification.with_identity(handle, lambda cid, _: cid is None)
                    try:
                        service._session(old_handle)
                        invalidated = False
                    except ValueError:
                        invalidated = True
                    checks = {
                        "new_handle": handle != old_handle,
                        "identity_cleared": clean,
                        "old_handle_invalidated": invalidated,
                    }
                    rows.append(
                        {"step": index + 1, "passed": all(checks.values()), "checks": checks}
                    )
                    continue
                started = time.perf_counter()
                try:
                    reply = service.send(handle, step.text, action=step.action)
                    elapsed = (time.perf_counter() - started) * 1000
                    checks = grade_reply(
                        database,
                        reply,
                        step,
                        step.oracle_customer_id or case.customer_id,
                        service._memory.load(step.oracle_customer_id or case.customer_id)
                        if service._memory is not None
                        and (step.oracle_customer_id or case.customer_id)
                        else (),
                    )
                    if step.expected_preferences is not None:
                        stored = service._memory.load(step.oracle_customer_id or case.customer_id)
                        checks["exact_memory_state"] = set(stored) == set(step.expected_preferences)
                    rows.append(
                        {
                            "step": index + 1,
                            "passed": all(checks.values()),
                            "checks": checks,
                            "status": reply.status,
                            "branch": reply.branch,
                            "elapsed_ms": elapsed,
                            "tools": [r["tool"] for r in reply.records],
                            "response_sha256": hashlib.sha256(reply.text.encode()).hexdigest(),
                        }
                    )
                    transcripts.append(
                        {
                            "case": case.id,
                            "step": index + 1,
                            "input": step.text,
                            "response": reply.text,
                            "records": reply.records,
                            "trace": reply.trace,
                        }
                    )
                    latencies.append(elapsed)
                except Exception:
                    rows.append(
                        {
                            "step": index + 1,
                            "passed": False,
                            "checks": {"execution_and_grading": False},
                            "error": "step_failed",
                        }
                    )
        finally:
            service.close(handle)
        results.append({"id": case.id, "passed": all(row["passed"] for row in rows), "steps": rows})
        if progress:
            progress(case.id, results[-1]["passed"])
    latencies.sort()
    return {
        "case_count": len(cases),
        "passed_cases": sum(r["passed"] for r in results),
        "all_mechanical_checks_passed": bool(results) and all(r["passed"] for r in results),
        "manual_semantic_review_required": True,
        "milestone_acceptance": False,
        "latency_samples": len(latencies),
        "latency_p50_ms": median(latencies) if latencies else None,
        "latency_p95_ms": latencies[math.ceil(len(latencies) * 0.95) - 1] if latencies else None,
        "cases": results,
        "limitations": [
            "SQL membership checks validate facts, not full search completeness",
            "Response grounding check does not prove absence of all unsupported prose",
            "Manual transcript review is required for intent and semantic grounding",
            "Sequential local calls; not a production load benchmark",
        ],
    }, transcripts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path("evals/conversation-cases.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from music_store.config import load_settings
    from music_store.db import initialize_database
    from music_store.model import build_conversation_service

    settings = load_settings()
    cases = [Case.model_validate(c) for c in json.loads(args.cases.read_text())]
    metadata = {
        "timestamp": datetime.now(UTC).isoformat(),
        "mode": "live_conversation",
        "model": settings.model_name,
        "temperature": settings.temperature,
        "max_attempts": settings.max_attempts,
        "timeout_seconds": settings.request_timeout_seconds,
        "max_graph_steps": settings.max_graph_steps,
        "dataset_revision": DATASET_REVISION,
        "cases_sha256": hashlib.sha256(args.cases.read_bytes()).hexdigest(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "concurrency": 1,
    }
    if not settings.openai_api_key.get_secret_value().strip():
        data = {
            **metadata,
            "status": "blocked_missing_api_key",
            "live_model_quality_validated": False,
            "attempted_cases": 0,
            "planned_cases": len(cases),
            "milestone_acceptance": False,
        }
    else:
        with initialize_database(settings.chinook_cache_dir) as database:
            data, transcripts = evaluate(
                cases,
                database,
                lambda: build_conversation_service(database, settings),
                progress=lambda cid, passed: print(
                    json.dumps({"case": cid, "mechanical_pass": passed}), flush=True
                ),
            )
        raw = Path(".cache/evals") / (metadata["timestamp"].replace(":", "-") + ".json")
        raw.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        raw.write_text(json.dumps(transcripts, indent=2) + "\n")
        raw.chmod(0o600)
        data = {
            **metadata,
            **data,
            "status": "completed",
            "transcript_path": str(raw),
            "live_calls_executed": True,
            "live_model_quality_validated": False,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({k: v for k, v in data.items() if k != "cases"}))
    return 0 if data.get("all_mechanical_checks_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
