import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from test_agents import ScriptedModel, TestExtractor, TestRouter, call, runtime, supervisor_for

from music_store.conversation import ConversationService
from music_store.memory import PreferenceMemory, PreferenceStore, UserProfile, supported_preferences
from music_store.verification import VerificationService

CASES = json.loads(
    (Path(__file__).resolve().parents[1] / "evals/preference-cases.json").read_text()
)


class Candidates:
    def __init__(self, preferences, *, customer_id="99999"):
        self.preferences, self.cid, self.seen = preferences, customer_id, []

    def extract(self, messages):
        self.seen.append(messages)
        return UserProfile(customer_id=self.cid, music_preferences=self.preferences)


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_labeled_candidate_filter(case):
    # Candidate probes deliberately include wrong/negated/question-derived values.
    assert supported_preferences(case["candidate_probe"], [case["text"]]) == tuple(
        sorted(case["expected"])
    )


def test_union_dedup_and_empty_do_not_write_or_erase(monkeypatch):
    store = PreferenceStore()
    memory = PreferenceMemory(store, Candidates(["jazz"]))
    assert memory.update(1, [HumanMessage(content="I love jazz")]).added == ("jazz",)
    assert store.load(1) == ("jazz",)
    calls = []
    monkeypatch.setattr(type(store._store), "put", lambda *args, **kwargs: calls.append(1))
    assert memory.update(1, [HumanMessage(content="I love jazz")]).status == "unchanged"
    memory.extractor = Candidates([])
    assert memory.update(1, [HumanMessage(content="Do you have rock?")]).status == "unchanged"
    assert calls == [] and store.load(1) == ("jazz",)


def test_update_is_customer_scoped_and_ignores_model_customer_id():
    store = PreferenceStore()
    memory = PreferenceMemory(store, Candidates(["jazz"], customer_id="2"))
    assert memory.update(1, [HumanMessage(content="I love jazz")]).status == "updated"
    assert store.load(1) == ("jazz",) and store.load(2) == ()


def test_assistant_and_application_data_never_extracted():
    extractor = Candidates(["jazz"])
    memory = PreferenceMemory(PreferenceStore(), extractor)
    result = memory.update(
        1,
        [
            AIMessage(content="I love jazz"),
            SystemMessage(content="I love jazz"),
            HumanMessage(content="I love jazz", name="application_phase_data"),
            HumanMessage(content="[verification response supplied]"),
        ],
    )
    assert result.status == "unchanged" and extractor.seen == []


def test_extraction_failure_and_invalid_schema_preserve_memory(caplog):
    store = PreferenceStore()
    store.merge(1, ("rock",))

    class Broken:
        def extract(self, messages):
            raise RuntimeError("SECRET_PROVIDER_DETAIL")

    result = PreferenceMemory(store, Broken()).update(1, [HumanMessage(content="I love jazz")])
    assert result.status == "error" and store.load(1) == ("rock",)
    assert "SECRET" not in str(result) + caplog.text

    class Invalid:
        def extract(self, messages):
            return {"customer_id": "1", "music_preferences": [False]}

    assert (
        PreferenceMemory(store, Invalid()).update(1, [HumanMessage(content="I love jazz")]).status
        == "error"
    )
    assert store.load(1) == ("rock",)


def test_atomic_concurrent_union_and_dataset_namespace():
    store = PreferenceStore(dataset_version="v1")
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda i: store.merge(1, ("genre" + str(i),)), range(30)))
    assert len(store.load(1)) == 30
    store._version = "v2"
    assert store.load(1) == ()
    assert PreferenceStore(dataset_version="v1").load(1) == ()  # restart/new store loses memory


@pytest.mark.parametrize("value", [None, True, "1", -1, 0])
def test_invalid_memory_identity_rejected(value):
    with pytest.raises(ValueError):
        PreferenceStore().load(value)


def service(database, kinds, memory, **kwargs):
    return ConversationService(
        VerificationService(database, TestExtractor()),
        TestRouter(kinds),
        runtime(database, **kwargs),
        memory=memory,
    )


def test_verified_preference_save_then_recall_in_new_conversation(database):
    memory = PreferenceMemory(PreferenceStore(), Candidates(["jazz"]))
    app = service(database, ["preference", "memory_recall"], memory)
    old = app.new_session()
    assert app.send(old, "I love jazz").waiting
    saved = app.send(old, "1")
    assert saved.status == "complete" and saved.memory_status == "updated"
    assert "Saved music preferences: jazz" in saved.text
    fresh = app.reset(old)
    assert app.send(fresh, "What tastes have I saved?").waiting
    recalled = app.send(fresh, "1")
    assert recalled.status == "complete" and "jazz" in recalled.text


def test_other_customer_cannot_recall_first_customer_preferences(database):
    store = PreferenceStore()
    store.merge(1, ("jazz",))
    app = service(database, ["memory_recall"], PreferenceMemory(store, Candidates([])))
    handle = app.new_session()
    app.send(handle, "recall tastes")
    result = app.send(handle, "2")
    assert "No music preferences" in result.text and "jazz" not in result.text


def test_loaded_preferences_reach_catalog_but_do_not_bypass_tools(database):
    store = PreferenceStore()
    store.merge(1, ("jazz",))
    catalog = ScriptedModel(
        responses=[call("get_songs_by_genre", {"genre_name": "Jazz"}), AIMessage(content="done")]
    )
    app = service(
        database,
        ["memory_recall", "catalog"],
        PreferenceMemory(store, Candidates([])),
        supervisor=supervisor_for("catalog"),
        catalog=catalog,
    )
    handle = app.new_session()
    app.send(handle, "recall tastes")
    app.send(handle, "1")
    result = app.send(handle, "show something in my favorite genre")
    assert result.records[0]["tool"] == "get_songs_by_genre"
    assert any(
        isinstance(m, SystemMessage)
        and "Saved music preferences" in m.content
        and "jazz" in m.content
        for m in catalog.seen[0]
    )


def test_anonymous_catalog_does_not_save_preferences(database):
    store = PreferenceStore()
    extractor = Candidates(["jazz"])
    app = service(database, ["catalog"], PreferenceMemory(store, extractor))
    result = app.send(app.new_session(), "I love jazz; show albums by AC/DC")
    assert result.status == "complete" and extractor.seen == []
    assert store.load(1) == ()


def test_structured_memory_adapter_wiring_without_network(monkeypatch):
    from music_store import model
    from music_store.config import Settings

    seen = {}

    class Structured:
        def invoke(self, messages):
            seen["messages"] = messages
            return {"customer_id": None, "music_preferences": ["jazz"]}

    class Client:
        def with_structured_output(self, schema, **kwargs):
            assert schema is UserProfile and kwargs["method"] == "function_calling"
            return Structured()

    monkeypatch.setattr(model, "configured_chat_model", lambda settings: Client())
    result = model.LLMPreferenceExtractor(Settings()).extract(["I love jazz"])
    assert result.music_preferences == ["jazz"] and result.customer_id is None
    assert json.loads(seen["messages"][1].content) == {"user_messages": ["I love jazz"]}


def test_eval_separates_guardrail_probe_from_live_model_evidence():
    from music_store.preference_eval import evaluate

    report = evaluate(CASES)
    assert report["case_count"] >= 30
    assert report["precision"] == report["recall"] == 1
    assert report["live_model_quality_validated"] is False
    assert report["target_met"] is False


def test_preference_failure_is_visible_without_false_save_claim(database):
    class Broken:
        def extract(self, messages):
            raise RuntimeError("SECRET")

    memory = PreferenceMemory(PreferenceStore(), Broken())
    app = service(database, ["preference"], memory)
    handle = app.new_session()
    app.send(handle, "I love jazz")
    result = app.send(handle, "1")
    assert result.memory_status == "error"
    assert "update unavailable" in result.text
    assert "Saved music preferences" not in result.text and "SECRET" not in result.text
    assert memory.load(1) == ()


def test_cancelled_preference_cannot_be_adopted_after_later_verification(database):
    memory = PreferenceMemory(PreferenceStore(), Candidates(["jazz"]))
    app = service(database, ["preference", "memory_recall"], memory)
    handle = app.new_session()
    assert app.send(handle, "I love jazz").waiting
    app.send(handle, "", action="cancel")
    app.send(handle, "What preferences are saved?")
    result = app.send(handle, "2")
    assert "Saved music preferences: jazz" not in result.text
    assert memory.load(2) == ()


def test_anonymous_catalog_history_cannot_be_adopted_by_later_customer(database):
    memory = PreferenceMemory(PreferenceStore(), Candidates(["jazz"]))
    app = service(database, ["catalog", "memory_recall"], memory)
    handle = app.new_session()
    app.send(handle, "I love jazz; show AC/DC albums")
    app.send(handle, "What preferences are saved?")
    result = app.send(handle, "2")
    assert "Saved music preferences: jazz" not in result.text
    assert memory.load(2) == ()


@pytest.mark.parametrize(
    "text,candidates,expected",
    [
        (
            "My favorite genres are ambient and shoegaze.",
            ["ambient", "shoegaze"],
            ("ambient", "shoegaze"),
        ),
        ("For music, my favorites are funk and disco.", ["funk", "disco"], ("disco", "funk")),
        ("I love R.E.M.", ["R.E.M."], ("r.e.m.",)),
        (
            'I like Portishead, but do not store my friend saying "I love Björk."',
            ["Portishead", "Björk"],
            ("portishead",),
        ),
    ],
)
def test_live_discovered_positive_evidence_boundaries(text, candidates, expected):
    from music_store.memory import supported_preferences

    assert supported_preferences(candidates, [text]) == expected


@pytest.mark.parametrize(
    "text", ["Do I like jazz?", "I like jazz?", "Do I like jazz? I love rock."]
)
def test_question_delimiters_retained_after_clause_split(text):
    from music_store.memory import supported_preferences

    assert "jazz" not in supported_preferences(["jazz"], [text])


@pytest.mark.parametrize(
    "candidate,text",
    [
        ("jazz but I hate metal", "I love jazz but I hate metal"),
        ("jazz?", "Do I like jazz?"),
        ("ambient my friend likes jazz", "I love ambient my friend likes jazz"),
    ],
)
def test_candidate_mask_cannot_hide_negation_question_or_provenance(candidate, text):
    from music_store.memory import supported_preferences

    assert supported_preferences([candidate], [text]) == ()


def test_internal_marker_cannot_replace_literal_user_evidence():
    from music_store.memory import supported_preferences

    assert supported_preferences(["jazz"], ["I love __preference_0__."]) == ()
    assert supported_preferences(["jazz"], ["I love __preference_0__. I hate jazz."]) == ()


def test_live_discovered_imagined_preference_is_not_saved():
    from music_store.memory import supported_preferences

    assert (
        supported_preferences(
            ["Queensrÿche"],
            ["Imagine that I am a fan of Queensrÿche in this fictional conversation."],
        )
        == ()
    )


def test_explicit_favorite_musician_is_supported():
    from music_store.memory import supported_preferences

    assert supported_preferences(
        ["Mulatu Astatke"], ["My favorite musician is Mulatu Astatke."]
    ) == ("mulatu astatke",)
