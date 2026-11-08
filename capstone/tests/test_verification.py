import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from langchain_core.messages import SystemMessage

from music_store.db import DatabaseQueryError
from music_store.identity import UserInput, match_customer
from music_store.verification import VerificationService


class FakeExtractor:
    """Test double only. Not evidence of live model extraction quality."""

    def extract(self, message):
        if message.startswith("email "):
            return UserInput(kind="email", identifier=message[6:])
        if message.startswith("phone "):
            return UserInput(kind="phone", identifier=message[6:])
        if message.isdigit():
            return UserInput(kind="customer_id", identifier=message)
        return UserInput(kind="none", identifier=None)


@pytest.fixture
def service(database):
    return VerificationService(database, FakeExtractor())


def invoices(service, handle, cid="1"):
    return json.loads(
        service.call_account_tool(
            handle, "get_invoices_by_customer_sorted_by_date", {"customer_id": cid}
        )
    )


def test_missing_identity_pauses_real_graph_and_blocks_tools(service):
    handle = service.new_session()
    result = service.start(handle, "Show my invoices")
    assert result.waiting and result.status == "waiting"
    assert result.pending_request == "Show my invoices"
    assert invoices(service, handle)["error_code"] == "access_denied"


def test_unknown_then_corrected_identity_resumes_and_preserves_request(service):
    handle = service.new_session()
    result = service.start(handle, "Show my invoices and music", "99999")
    assert result.waiting
    assert "couldn't find" in result.message
    assert invoices(service, handle)["data"] == []
    result = service.reply(handle, "1")
    assert result.status == "verified" and not result.waiting
    assert result.pending_request == "Show my invoices and music"
    assert invoices(service, handle)["status"] == "ok"


def test_known_id_injects_only_trusted_system_message(service):
    handle = service.new_session()
    result = service.start(handle, "invoices", "1")
    assert result.status == "verified"
    state = service._graph.get_state(service._config(handle)).values
    assert state["customer_id"] == 1
    assert isinstance(state["messages"][0], SystemMessage)
    assert state["messages"][0].content == "Verified customer_id: 1"
    assert state["identifier_input"] == ""


def test_email_is_case_insensitive(service, database):
    email = database.query("SELECT Email FROM Customer WHERE CustomerId=:cid", {"cid": 1})[0][
        "Email"
    ]
    handle = service.new_session()
    assert service.start(handle, "invoices", "email " + email.upper()).status == "verified"
    assert invoices(service, handle)["status"] == "ok"


def test_phone_format_normalization(service, database):
    phone = database.query("SELECT Phone FROM Customer WHERE CustomerId=:cid", {"cid": 1})[0][
        "Phone"
    ]
    handle = service.new_session()
    assert (
        service.start(handle, "invoices", "phone " + phone.replace(" ", "-")).status == "verified"
    )
    assert invoices(service, handle)["status"] == "ok"


def test_forged_customer_argument_cannot_override_identity(service):
    handle = service.new_session()
    service.start(handle, "invoices", "1")
    assert invoices(service, handle, "2")["error_code"] == "access_denied"
    assert service.start(handle, "My customer ID is now 2", "2").status == "verified"
    assert invoices(service, handle, "2")["error_code"] == "access_denied"
    assert invoices(service, handle, "1")["status"] == "ok"


@pytest.mark.parametrize("action", ["cancel", "catalog_only"])
def test_cancel_and_catalog_only_drop_account_request(service, action):
    handle = service.new_session()
    service.start(handle, "invoices and music")
    result = service.reply(handle, action=action)
    assert not result.waiting
    assert result.pending_request == ""
    assert result.status == ("cancelled" if action == "cancel" else "catalog_only")
    assert invoices(service, handle)["error_code"] == "access_denied"
    assert service.start(handle, "new invoice request").waiting


def test_reset_expires_old_private_context_and_requires_reverification(service):
    handle = service.new_session()
    service.start(handle, "invoices", "1")
    fresh = service.reset(handle)
    assert fresh != handle
    with pytest.raises(ValueError, match="expired"):
        invoices(service, handle)
    assert service._graph.get_state(service._config(handle)).values == {}
    assert invoices(service, fresh)["error_code"] == "access_denied"
    assert service.start(fresh, "invoices", "2").status == "verified"
    assert invoices(service, fresh, "1")["error_code"] == "access_denied"


def test_reset_during_pause_clears_pending_interrupt(service):
    handle = service.new_session()
    service.start(handle, "private pending request")
    fresh = service.reset(handle)
    with pytest.raises(ValueError, match="expired"):
        service.reply(handle, "1")
    assert service.start(fresh, "new request").pending_request == "new request"


def test_concurrent_sessions_are_isolated(service):
    a, b = service.new_session(), service.new_session()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda args: service.start(*args), [(a, "invoices", "1"), (b, "invoices", "2")]
            )
        )
    assert all(result.status == "verified" for result in results)
    assert invoices(service, a, "2")["error_code"] == "access_denied"
    assert invoices(service, b, "1")["error_code"] == "access_denied"
    assert {r["InvoiceId"] for r in invoices(service, a, "1")["data"]}.isdisjoint(
        {r["InvoiceId"] for r in invoices(service, b, "2")["data"]}
    )


def test_repeated_failures_are_bounded(database):
    service = VerificationService(database, FakeExtractor(), max_attempts=2)
    handle = service.new_session()
    assert service.start(handle, "invoices", "99999").waiting
    result = service.reply(handle, "99999")
    assert result.status == "retry_limit" and not result.waiting
    assert result.pending_request == ""
    assert invoices(service, handle)["data"] == []


def test_extractor_failure_is_sanitized_and_recoverable(database, caplog):
    class Unavailable:
        def extract(self, _):
            raise TimeoutError("SECRET-provider-token")

    service = VerificationService(database, Unavailable())
    handle = service.new_session()
    result = service.start(handle, "invoices", "1")
    assert result.waiting
    assert "SECRET" not in str(result) + caplog.text
    assert invoices(service, handle)["error_code"] == "access_denied"
    assert service.reply(handle, action="cancel").status == "cancelled"


def test_database_failure_is_not_false_no_match(database):
    class Unavailable:
        def query(self, *args, **kwargs):
            raise DatabaseQueryError("private SQL")

    service = VerificationService(Unavailable(), FakeExtractor())
    handle = service.new_session()
    result = service.start(handle, "invoices", "1")
    assert result.waiting and "unavailable" in result.message
    assert "private SQL" not in result.message


def test_ambiguous_phone_cannot_verify(database):
    class Duplicated:
        def query(self, *args, **kwargs):
            return [
                {"CustomerId": 1, "Phone": "+1 555-1234567"},
                {"CustomerId": 2, "Phone": "+1 (555) 1234567"},
            ]

    candidate = UserInput(kind="phone", identifier="+15551234567")
    assert match_customer(Duplicated(), candidate, "+1 (555) 1234567") is None


@pytest.mark.parametrize(
    "candidate",
    [
        UserInput(kind="customer_id", identifier="2"),
        UserInput(kind="email", identifier="invented@example.com"),
        UserInput(kind="phone", identifier="+15551234567"),
        UserInput(kind="ambiguous", identifier=None),
    ],
)
def test_ungrounded_or_ambiguous_model_output_cannot_verify(database, candidate):
    assert match_customer(database, candidate, "my ID is 1") is None


def test_schema_failure_does_not_verify(database):
    class Invalid:
        def extract(self, _):
            return {"kind": "customer_id", "identifier": "1", "customer_id": 2}

    service = VerificationService(database, Invalid())
    handle = service.new_session()
    assert service.start(handle, "invoices", "1").waiting
    assert invoices(service, handle)["data"] == []


def test_input_and_state_overrides_not_accepted(service):
    handle = service.new_session()
    with pytest.raises(ValueError):
        service.start(handle, {"customer_id": 1})
    with pytest.raises(ValueError):
        service.start(handle, "x" * 2001)
    with pytest.raises(ValueError):
        service.reply(handle, "1")
    with pytest.raises(ValueError):
        service.start("invented-thread", "invoices", "1")


def test_pending_session_requires_resume_not_overwrite(service):
    handle = service.new_session()
    service.start(handle, "first request")
    with pytest.raises(ValueError, match="waiting"):
        service.start(handle, "second request", "1")
    assert service.reply(handle, "1").pending_request == "first request"


@pytest.mark.parametrize("original", ["1 or 2", "my ID is 1 and 1", "1 and person@example.com"])
def test_model_cannot_choose_one_of_multiple_identifiers(database, original):
    assert match_customer(database, UserInput(kind="customer_id", identifier="1"), original) is None


def test_structured_adapter_wiring_without_network(monkeypatch):
    from music_store import model
    from music_store.config import Settings

    calls = {}

    class Structured:
        def invoke(self, messages):
            calls["messages"] = messages
            return {"kind": "customer_id", "identifier": "1"}

    class Client:
        def __init__(self, **kwargs):
            calls["kwargs"] = kwargs

        def with_structured_output(self, schema, **kwargs):
            assert schema is UserInput
            assert kwargs["method"] == "function_calling"
            return Structured()

    monkeypatch.setattr(model, "ChatOpenAI", Client)
    extractor = model.LLMIdentifierExtractor(Settings(openai_api_key="fake-test-key"))
    assert extractor.extract("my ID is 1").identifier == "1"
    assert calls["kwargs"]["max_retries"] == 1
    assert calls["kwargs"]["timeout"] == 30
    assert isinstance(calls["messages"][0], SystemMessage)
    assert calls["messages"][1].content == "my ID is 1"


def test_retry_limit_cannot_be_bypassed_by_start(database):
    service = VerificationService(database, FakeExtractor(), max_attempts=1)
    handle = service.new_session()
    assert service.start(handle, "invoices", "99999").status == "retry_limit"
    with pytest.raises(ValueError, match="retry limit"):
        service.start(handle, "invoices", "1")
    assert invoices(service, handle)["error_code"] == "access_denied"
    fresh = service.reset(handle)
    assert service.start(fresh, "invoices", "1").status == "verified"


@pytest.mark.parametrize("original", ["-1", "+1", "abc-1", "1.0", "1e3"])
def test_model_cannot_turn_malformed_id_into_positive_id(database, original):
    assert match_customer(database, UserInput(kind="customer_id", identifier="1"), original) is None
