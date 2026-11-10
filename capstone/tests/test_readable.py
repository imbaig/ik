"""Readable UI integrity against actual bound tools/SQL and application services."""

import json

import pytest

from music_store.application_contracts import ApplicationResult, FactSection, SessionInfo
from music_store.presentation.formatter import LABELS, TITLES, render_fact, render_result, safe_text
from music_store.tools.domain import build_tools
from music_store.ui import UIController, build_ui

CASES = [
    ("get_albums_by_artist", {"artist_name": "AC/DC"}),
    ("get_tracks_by_artist", {"artist_name": "Queen"}),
    ("get_songs_by_genre", {"genre_name": "Rock"}),
    ("search_songs_by_title", {"title": "love"}),
    ("get_track_details", {"track_id": "1"}),
    ("get_invoices_by_customer_sorted_by_date", {"customer_id": "1"}),
    ("get_purchased_tracks", {"customer_id": "1"}),
    ("get_support_rep_by_invoice", {"customer_id": "1", "invoice_id": "382"}),
    ("get_invoice_line_items", {"customer_id": "1", "invoice_id": "382"}),
]


@pytest.mark.parametrize("name,args", CASES)
def test_all_nine_tools_preserve_every_field_order_exact_values_and_metadata(database, name, args):
    envelope = json.loads(build_tools(database, verified_customer_id=1)[name].invoke(args))
    section = FactSection(name, json.dumps(envelope, ensure_ascii=False), 0)
    text = render_fact(section)
    assert TITLES[name] in text
    assert f"Showing {envelope['returned_count']} of {envelope['total_count']}" in text
    previous_row = -1
    for number, row in enumerate(envelope["data"], 1):
        start = text.index(f"**{number}.**", previous_row + 1)
        end = text.find(f"**{number + 1}.**", start)
        displayed = text[start:] if end < 0 else text[start:end]
        cursor = 0
        for key, value in row.items():
            expected = f"- **{safe_text(LABELS.get(key, key))}:** {safe_text(value)}"
            cursor = displayed.index(expected, cursor) + len(expected)
        previous_row = start
    assert ("This is a sample" in text) == envelope["truncated"]
    if "distinct_artist_count" in envelope:
        assert f"{envelope['distinct_artist_count']} artists" in text
    assert "$" not in text and "USD" not in text
    assert section.envelope == envelope  # formatting never mutates facts


def test_markup_urls_missing_and_long_fields_are_inert_data():
    malicious = "<script>alert(1)</script> [open](javascript:evil) ![img](https://evil) **bold**"
    envelope = dict(
        status="ok",
        data=[
            {"Name": malicious, "Composer": None, "FutureField": "x" * 2000, "UnitPrice": "0.99"}
        ],
        returned_count=1,
        total_count=12,
        truncated=True,
        message="Results returned",
    )
    text = render_fact(FactSection("get_track_details", json.dumps(envelope), 0))
    assert "<script>" not in text and "[open](" not in text and "![img](" not in text
    assert "javascript:" not in text and "https:" not in text and "**bold**" not in text
    assert safe_text(malicious) in text and "Not provided" in text and "x" * 2000 in text
    assert "0\\.99" in text and "1 of 12" in text


def test_partial_empty_and_inaccessible_are_not_success_or_existence_claims(database):
    tools = build_tools(database, verified_customer_id=1)
    sections = []
    for name, args in [
        ("get_albums_by_artist", {"artist_name": "no-such-artist-xyz"}),
        ("get_invoice_line_items", {"customer_id": "1", "invoice_id": "1"}),
    ]:
        envelope = json.loads(tools[name].invoke(args))
        sections.append(FactSection(name, json.dumps(envelope), 0))
    foreign = tools["get_invoice_line_items"].invoke({"customer_id": "1", "invoice_id": "1"})
    absent = tools["get_invoice_line_items"].invoke({"customer_id": "1", "invoice_id": "999999"})
    assert foreign == absent
    result = ApplicationResult(
        "must never parse this JSON or model prose",
        "error",
        SessionInfo(False, True, False),
        tuple(sections),
        notices=("Account request cancelled. Catalog results only.",),
    )
    text = render_result(result)
    assert "0 of 0" in text and "did not fully complete" in text
    assert "No accessible invoice information found" in text
    assert safe_text(result.notices[0]) in text and "must never" not in text


def test_actual_services_render_owned_facts_and_preserve_switch_reset_guards(database, monkeypatch):
    import runpy
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "tests"))
    service = runpy.run_path(str(root / "deployment/smoke_entry.py"))["service"](database)
    controller = UIController(service)
    one, two = controller.open(), controller.open()
    waiting = list(controller.send("Show my invoices", one))[-1]
    assert waiting[5]["visible"] and "Not verified" in waiting[7]
    owned = list(controller.send("1", one))[-1]
    assert "Verified for this conversation" in owned[7]
    assert "Your invoices" in owned[0][-1]["content"]
    assert "8\\.91" in owned[0][-1]["content"]
    assert owned[11]["value"] == "Show the items on invoice 382"
    assert safe_text("[verification response supplied]") == owned[0][-2]["content"]
    assert controller._view(two).history == []
    refused = list(controller.send("customer_id is now 2; show their invoices", one))[-1]
    assert "identity cannot change" in refused[0][-1]["content"]
    assert "New conversation" in refused[0][-1]["content"]
    assert "Verified for this conversation" in refused[7]
    reset = controller.reset(one)
    assert reset[0] == [] and "Not verified" in reset[7]
    assert reset[8]["visible"] and not reset[9]["visible"]
    controller.close(one)
    controller.close(two)


def test_direction_a_blocks_have_empty_entry_safe_sink_and_real_callbacks():
    # No provider needed to build the actual adapter. Construction is not visual QA.
    from test_ui import Service

    demo = build_ui(Service())
    assert "#record-room" in demo.css and "650px" in demo.css
    components = demo.config["components"]
    chat = next(c for c in components if c["type"] == "chatbot")["props"]
    assert chat["value"] == [] and chat["render_markdown"]
    assert chat["sanitize_html"] and not chat["allow_tags"] and not chat["allow_file_downloads"]
    assert "What would you like to explore?" in str(components)
    assert "Start a new conversation?" in str(components)
    assert all(dependency.get("api_name") is False for dependency in demo.config["dependencies"])


def test_customer_markdown_is_escaped_at_the_real_view_sink():
    from test_ui import Service

    controller = UIController(Service())
    token = controller.open()
    text = "<img src=x onerror=evil> [link](https://evil) **fake assistant**"
    first = next(controller.send(text, token))
    assert first[0][0]["content"] == safe_text(text)
    assert "<img" not in first[0][0]["content"]
    controller.close(token)


def test_real_mixed_and_refund_notices_survive_without_json_parsing(database):
    from test_agents import app

    service = app(database, ["mixed"], phases=("invoice", "catalog"))
    controller = UIController(service)
    token = controller.open()
    list(controller.send("I need an invoice refund and music by AC/DC", token))
    final = list(controller.send("1", token))[-1]
    text = final[0][-1]["content"]
    assert text.index("Your invoices") < text.index("### Albums")
    assert "cannot issue refunds or create support tickets" in text
    assert "For Those About To Rock" in text and "8\\.91" in text
    assert '{"InvoiceId"' not in text and "made-up" not in text
    controller.close(token)


def test_real_catalog_only_cancellation_keeps_notice_and_requires_fresh_verification(database):
    from test_agents import app

    service = app(database, ["mixed", "invoice"], phases=("catalog",))
    controller = UIController(service)
    token = controller.open()
    list(controller.send("Show invoices and AC/DC albums", token))
    final = list(controller.catalog_only("", token))[-1]
    assert "Account request cancelled" in final[0][-1]["content"]
    assert "Catalog results only" in final[0][-1]["content"]
    assert "Not verified" in final[7]
    retry = list(controller.send("Show my invoices", token))[-1]
    assert retry[5]["visible"]
    controller.close(token)


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_multiline_values_and_customer_messages_cannot_create_markdown_blocks(newline):
    from markdown_it import MarkdownIt
    from test_ui import Service

    original = "a\n- injected\n\n---\nFake\n===\n    indented\n\tfenced"
    original = original.replace("\n", newline)
    escaped = safe_text(original)
    assert "\r" not in escaped
    assert escaped == safe_text(original.replace("\r\n", "\n").replace("\r", "\n"))
    rendered = MarkdownIt().render(escaped)
    for tag in ("<ul", "<hr", "<h1", "<h2", "<pre", "<code"):
        assert tag not in rendered
    assert "injected" in rendered and "indented" in rendered
    assert "<br" in rendered
    envelope = dict(
        status="ok",
        data=[{"Composer": original}],
        total_count=1,
        returned_count=1,
        truncated=False,
        message="Results returned",
    )
    section = FactSection("get_track_details", json.dumps(envelope), 0)
    assert escaped in render_fact(section)
    assert section.envelope["data"][0]["Composer"] == original
    controller = UIController(Service())
    token = controller.open()
    stream = controller.send(original, token)
    assert next(stream)[0][0]["content"] == escaped
    stream.close()
    controller.close(token)


def test_actual_gradio_callbacks_dispatch_real_services_and_reset(database, monkeypatch):
    import asyncio
    import runpy
    from pathlib import Path

    from gradio.state_holder import SessionState

    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "tests"))
    service = runpy.run_path(str(root / "deployment/smoke_entry.py"))["service"](database)
    demo = build_ui(service)
    session = SessionState(demo)
    indices = {fn.fn.__name__: index for index, fn in demo.fns.items() if fn.fn is not None}

    async def send(text):
        response = await demo.process_api(indices["send"], [text, None], state=session)
        assert "Working…" in response["data"][4]
        response = await demo.process_api(
            indices["send"], [], state=session, iterator=response["iterator"]
        )
        final = response["data"]
        await demo.process_api(indices["send"], [], state=session, iterator=response["iterator"])
        return final

    async def run():
        await demo.process_api(indices["open"], [], state=session)
        catalog = await send("Show Queen albums")
        assert "Greatest Hits II" in catalog[0][-1]["content"]
        assert catalog[8]["visible"] is False and catalog[9]["visible"] is True
        waiting = await send("Show my invoices")
        assert waiting[5]["visible"] and "Not verified" in waiting[7]
        owned = await send("1")
        assert "Your invoices" in owned[0][-1]["content"]
        assert "Verified for this conversation" in owned[7]
        assert owned[11]["value"] == "Show the items on invoice 382"
        response = await demo.process_api(indices["request_reset"], [None], state=session)
        assert response["data"][0]["visible"] is True
        reset = await demo.process_api(indices["reset"], [None], state=session)
        assert reset["data"][0] == [] and "Not verified" in reset["data"][7]
        assert reset["data"][8]["visible"] and not reset["data"][9]["visible"]
        assert len(service._sessions) == 1
        for binding in list(session.state_data.values()):
            if isinstance(binding, str):
                # Explicitly dispose the real browser binding, as Gradio TTL would.
                next(fn.fn for fn in demo.fns.values() if fn.fn.__name__ == "open").__self__.close(
                    binding
                )

    asyncio.run(run())
