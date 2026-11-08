import copy
import json
from dataclasses import replace

import pytest

from music_store.conversation import ConversationReply
from music_store.conversation_eval import Case, Step, evaluate, grade_reply, truth_rows
from music_store.tools import build_tools


@pytest.mark.parametrize(
    "name,args,cid",
    [
        ("get_albums_by_artist", {"artist_name": "AC/DC"}, None),
        ("get_tracks_by_artist", {"artist_name": "AC/DC"}, None),
        ("get_songs_by_genre", {"genre_name": "Jazz"}, None),
        ("search_songs_by_title", {"title": "Love"}, None),
        ("get_track_details", {"track_id": "1"}, None),
        ("get_invoices_by_customer_sorted_by_date", {"customer_id": "1"}, 1),
        ("get_purchased_tracks", {"customer_id": "1"}, 1),
        ("get_invoice_line_items", {"customer_id": "2", "invoice_id": "1"}, 2),
        ("get_support_rep_by_invoice", {"customer_id": "2", "invoice_id": "1"}, 2),
    ],
)
def test_all_nine_oracle_projections_accept_actual_facts(database, name, args, cid):
    result = json.loads(build_tools(database, verified_customer_id=cid)[name].invoke(args))
    record = {"tool": name, "result": result}
    from music_store.agents.runtime import render_records

    reply = ConversationReply(render_records([record]), "complete", records=(record,))
    checks = grade_reply(database, reply, Step(required_tools=[name], expect_nonempty=True), cid)
    assert all(checks.values())


def test_oracle_rejects_fabrication_foreign_rows_and_missing_answer(database):
    name = "get_invoices_by_customer_sorted_by_date"
    result = json.loads(
        build_tools(database, verified_customer_id=2)[name].invoke({"customer_id": "2"})
    )
    record = {"tool": name, "result": result}
    reply = ConversationReply("invented answer", "complete", records=(record,))
    checks = grade_reply(database, reply, Step(), 1)
    assert not checks["sql_facts_and_ownership"] and not checks["tool_render_present"]
    forged = copy.deepcopy(record)
    forged["result"]["data"][0]["Total"] = "999999.99"
    assert not grade_reply(database, replace(reply, records=(forged,)), Step(), 2)[
        "sql_facts_and_ownership"
    ]
    assert not grade_reply(
        database,
        ConversationReply("nothing", "complete"),
        Step(required_tools=[name], expect_nonempty=True),
        1,
    )["required_tools"]


def test_real_graph_runner_grades_and_closes_sessions(database):
    from test_agents import app

    instances = []

    def factory():
        service = app(database, ["catalog"])
        instances.append(service)
        return service

    cases = [
        Case(
            id="smoke",
            description="mechanical runner test",
            steps=[
                Step(
                    text="Albums by AC/DC",
                    expected_status=["complete"],
                    expected_branch=["catalog"],
                    required_tools=["get_albums_by_artist"],
                    expect_nonempty=True,
                )
            ],
        )
    ]
    report, transcripts = evaluate(cases, database, factory)
    assert report["all_mechanical_checks_passed"]
    assert report["manual_semantic_review_required"] and not report["milestone_acceptance"]
    assert len(transcripts) == 1
    assert not instances[0]._sessions


def test_oracle_fails_unknown_tool(database):
    with pytest.raises(ValueError):
        truth_rows(database, "invented", 1)


def test_exact_lookup_rejects_wrong_track_false_total_and_extra_prose(database):
    from music_store.agents.runtime import render_records

    name = "get_track_details"
    result = json.loads(build_tools(database)[name].invoke({"track_id": "2"}))
    result.update(total_count=123456, truncated=True)
    record = {"tool": name, "result": result}
    reply = ConversationReply(
        render_records([record]) + "\nThe invoice total is 999999.99.",
        "complete",
        records=(record,),
    )
    checks = grade_reply(database, reply, Step(expected_lookups={name: {"track_id": "1"}}), None)
    assert not checks["exact_lookup_" + name]
    assert not checks["no_unexpected_tool_answer_prose"]


def test_saved_preference_suffix_requires_observed_values(database):
    from music_store.agents.runtime import render_records

    name = "get_track_details"
    result = json.loads(build_tools(database)[name].invoke({"track_id": "1"}))
    record = {"tool": name, "result": result}
    reply = ConversationReply(
        render_records([record]) + "\nSaved music preferences: The invoice total is 999999.99.",
        "complete",
        records=(record,),
    )
    assert not grade_reply(database, reply, Step(), None)["no_unexpected_tool_answer_prose"]


def test_failed_send_with_memory_expectation_stays_failed_report(database):
    from test_agents import app

    def factory():
        service = app(database, ["catalog"])

        def fail(*args, **kwargs):
            raise RuntimeError("private error")

        service.send = fail
        return service

    cases = [
        Case(
            id="failure",
            description="fault boundary",
            customer_id=1,
            steps=[Step(text="hi", expected_preferences=[])],
        )
    ]
    report, _ = evaluate(cases, database, factory)
    assert report["passed_cases"] == 0
    assert report["cases"][0]["steps"][0]["error"] == "step_failed"


def test_runner_reset_checks_identity_and_invalidates_old_thread(database):
    from test_agents import app

    cases = [Case(id="reset", description="reset assertions", steps=[Step(action="reset")])]
    report, _ = evaluate(cases, database, lambda: app(database, []))
    checks = report["cases"][0]["steps"][0]["checks"]
    assert checks == {"new_handle": True, "identity_cleared": True, "old_handle_invalidated": True}
