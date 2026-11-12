"""Unsupported ranking is acknowledged without turning catalog order into a claim."""

import pytest
from langchain_core.messages import AIMessage
from test_agents import ScriptedModel, app, call

from music_store.application_contracts import Action, ActionKind
from music_store.conversation import POPULARITY_NOTICE, catalog_limitation
from music_store.presentation.formatter import render_result


@pytest.mark.parametrize(
    "text",
    [
        "i like the doors. name their most popular song",
        "i like the doors. name their most poular song",
        "What are the top 5 tracks by Queen?",
        "Which is their best-selling song?",
        "Show streaming counts for The Doors",
        "What is the most famous track?",
    ],
)
def test_ranked_requests_have_an_explicit_capability_limit(text):
    assert catalog_limitation("catalog", text) == POPULARITY_NOTICE
    assert catalog_limitation("mixed", text) == POPULARITY_NOTICE
    assert not catalog_limitation("invoice", text)


@pytest.mark.parametrize(
    "text",
    [
        "Show tracks by The Doors",
        "I like pop music",
        "Which track costs the most?",
        "Find a song named Popular",
        "Show albums by Queen",
    ],
)
def test_ordinary_catalog_requests_do_not_get_a_ranking_disclaimer(text):
    assert not catalog_limitation("catalog", text)


def test_real_tools_return_unranked_doors_facts_and_notice_precedes_table(database):
    model = ScriptedModel(
        responses=[
            call("get_tracks_by_artist", {"artist_name": "The Doors"}),
            AIMessage(content="made-up ranking"),
        ]
    )
    service = app(database, ["catalog"], catalog=model)
    handle = service.new_session()
    result = service.dispatch(
        handle, Action(ActionKind.SEND, "Name the most popular song by The Doors")
    )
    assert result.status == "complete"
    assert result.notices == (POPULARITY_NOTICE,)
    assert result.facts[0].envelope["total_count"] == 11
    text = render_result(result)
    assert text.index("I don't have popularity rankings") < text.index("### Tracks by artist")
    assert "Light My Fire" in text and "made-up ranking" not in text
    assert any("application will explain" in str(m.content).lower() for m in model.seen[0])
    service.close(handle)


def test_no_tool_failure_keeps_limitation_without_promising_results(database):
    model = ScriptedModel(responses=[AIMessage(content="Light My Fire is number one")])
    service = app(database, ["catalog"], catalog=model)
    handle = service.new_session()
    result = service.dispatch(
        handle, Action(ActionKind.SEND, "What is the most popular song by The Doors?")
    )
    assert result.status == "error" and not result.facts
    text = render_result(result)
    assert "I don't have popularity rankings" in text
    assert "No tool" in text and "number one" not in text
    service.close(handle)
