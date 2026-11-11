"""Contextual questions are editable suggestions, never automatic actions/authority."""

import json
from dataclasses import replace

import pytest
from test_agents import app
from test_ui import Service

from music_store.application_contracts import ApplicationResult, FactSection, SessionInfo
from music_store.presentation.contracts import ChatMessage, ViewState
from music_store.presentation.suggestions import DISCOVERY, STARTERS, next_questions
from music_store.tools.domain import build_tools
from music_store.ui import UIController, build_ui


def state(facts=(), verified=False):
    result = ApplicationResult("legacy", "complete", SessionInfo(False, verified, False), facts)
    return ViewState(
        (ChatMessage("assistant", "Result"),),
        "complete",
        0,
        1,
        "test",
        verified=verified,
        result=result,
    )


def fact(tool, envelope):
    return FactSection(tool, json.dumps(envelope), 0)


def test_initial_and_reset_starters():
    assert next_questions(replace(state(), messages=(), result=None)) == STARTERS
    controller = UIController(Service())
    token = controller.open()
    list(controller.send("hello", token))
    reset = controller.reset(token)
    assert reset[11]["value"] == STARTERS[0]
    assert reset[13]["value"] == STARTERS[1] and reset[14]["value"] == STARTERS[2]
    assert reset[12]["visible"]
    controller.close(token)


def test_real_album_track_and_owned_invoice_context(database):
    tools = build_tools(database, verified_customer_id=1)
    albums = json.loads(tools["get_albums_by_artist"].invoke({"artist_name": "AC/DC"}))
    assert (
        next_questions(state((fact("get_albums_by_artist", albums),)))[0] == "Show tracks by AC/DC"
    )
    tracks = json.loads(tools["get_tracks_by_artist"].invoke({"artist_name": "The Doors"}))
    suggestions = next_questions(state((fact("get_tracks_by_artist", tracks),)))
    assert suggestions[:2] == (
        "Tell me about Break on Through (track 2639)",
        "Show albums by The Doors",
    )
    invoices = json.loads(
        tools["get_invoices_by_customer_sorted_by_date"].invoke({"customer_id": "1"})
    )
    context = (fact("get_invoices_by_customer_sorted_by_date", invoices),)
    assert next_questions(state(context, verified=True))[:2] == (
        "Show the items on invoice 382",
        "Who can help with invoice 382?",
    )
    assert not any("382" in text for text in next_questions(state(context, verified=False)))


def test_empty_catalog_offers_only_catalog_alternatives(database):
    envelope = json.loads(
        build_tools(database, verified_customer_id=1)["get_albums_by_artist"].invoke(
            {"artist_name": "NoSuchArtistXYZ"}
        )
    )
    assert next_questions(state((fact("get_albums_by_artist", envelope),))) == DISCOVERY
    assert not any("invoice" in question.lower() for question in DISCOVERY)


def test_unsafe_context_labels_and_identifiers_are_not_promoted():
    envelope = dict(
        status="ok",
        data=[{"Artist": "<script>bad</script>", "TrackId": "-1", "InvoiceId": "382"}],
        returned_count=1,
        total_count=1,
        truncated=False,
        message="Results",
    )
    questions = next_questions(state((fact("get_tracks_by_artist", envelope),)))
    assert questions == STARTERS and "<script>" not in str(questions)


def test_suggestions_stay_visible_but_busy_or_waiting_cannot_fill_identifier():
    service = Service()
    controller = UIController(service)
    token = controller.open()
    stream = controller.send("account", token)
    busy = next(stream)
    assert busy[12]["visible"] and not busy[11]["interactive"]
    assert "value" not in busy[11]  # No label flash back to starter text while loading.
    assert "value" not in controller.choose_suggestion(STARTERS[0], token)
    waiting = next(stream)
    assert waiting[12]["visible"] and not waiting[11]["interactive"]
    assert not waiting[13]["interactive"] and not waiting[14]["interactive"]
    assert "value" not in controller.choose_suggestion(STARTERS[0], token)
    list(stream)
    controller.reset(token)
    before = list(service.calls)
    assert (
        controller.choose_suggestion("Show albums by Queen", token)["value"]
        == "Show albums by Queen"
    )
    assert service.calls == before
    controller.close(token)
    assert "value" not in controller.choose_suggestion(STARTERS[0], token)


def test_invoice_suggestions_reset_without_retaining_private_context(database):
    controller = UIController(app(database, ["invoice"], phases=("invoice",)))
    token = controller.open()
    list(controller.send("Show my invoices", token))
    verified = list(controller.send("1", token))[-1]
    assert verified[11]["value"] == "Show the items on invoice 382"
    assert verified[12]["visible"] and verified[11]["interactive"]
    reset = controller.reset(token)
    assert "382" not in str((reset[11], reset[13], reset[14]))
    assert reset[11]["value"] == STARTERS[0]
    controller.close(token)


def test_actual_blocks_remove_copy_and_place_suggestions_before_composer():
    demo = build_ui(Service())
    components = demo.config["components"]
    chat = next(c for c in components if c["type"] == "chatbot")["props"]
    assert chat["show_copy_button"] is False
    assert "grid-template-columns:minmax(0,1fr) 36px" not in demo.css
    starter_index = next(
        i
        for i, c in enumerate(components)
        if c["type"] == "button" and c["props"].get("value") == STARTERS[0]
    )
    chat_index = next(i for i, c in enumerate(components) if c["type"] == "chatbot")
    composer_index = next(i for i, c in enumerate(components) if c["type"] == "textbox")
    assert chat_index < starter_index < composer_index
    assert (
        len(
            [
                fn
                for fn in demo.fns.values()
                if fn.fn is not None and fn.fn.__name__ == "choose_suggestion"
            ]
        )
        == 3
    )


def test_unverified_private_track_rows_and_huge_ids_are_not_suggested():
    envelope = dict(
        status="ok",
        data=[{"TrackId": "9" * 5000, "Name": "private title"}],
        returned_count=1,
        total_count=1,
        truncated=False,
        message="Results",
    )
    assert next_questions(state((fact("get_purchased_tracks", envelope),))) == STARTERS
    assert next_questions(state((fact("get_tracks_by_artist", envelope),))) == STARTERS


@pytest.mark.parametrize("control", ["\x00", "\x1b", "\x7f", "\x85", "\u202e", "\u200b"])
def test_control_characters_are_not_promoted_into_suggested_questions(control):
    envelope = dict(
        status="ok",
        data=[{"Artist": "AC" + control + "/DC"}],
        returned_count=1,
        total_count=1,
        truncated=False,
        message="Results",
    )
    assert next_questions(state((fact("get_albums_by_artist", envelope),))) == STARTERS
