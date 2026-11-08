import json
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import pytest

from music_store.db import DatabaseQueryError
from music_store.tools import build_tools

CATALOG = [
    ("get_albums_by_artist", {"artist_name": "AC/DC"}, {"artist_name": "NonexistentXYZ"}),
    ("get_tracks_by_artist", {"artist_name": "Iron Maiden"}, {"artist_name": "NonexistentXYZ"}),
    ("get_songs_by_genre", {"genre_name": "Rock"}, {"genre_name": "NonexistentXYZ"}),
    ("search_songs_by_title", {"title": "love"}, {"title": "NonexistentXYZ"}),
    ("get_track_details", {"track_id": "1"}, {"track_id": "999999"}),
]
ACCOUNTS = [
    ("get_invoices_by_customer_sorted_by_date", {"customer_id": "1"}),
    ("get_purchased_tracks", {"customer_id": "1"}),
    ("get_support_rep_by_invoice", {"customer_id": "1", "invoice_id": "98"}),
    ("get_invoice_line_items", {"customer_id": "1", "invoice_id": "98"}),
]
ALL = [(name, found) for name, found, _ in CATALOG] + ACCOUNTS


def invoke(database, name, args, customer=1):
    return json.loads(build_tools(database, verified_customer_id=customer)[name].invoke(args))


def envelope(value):
    assert set(value) >= {
        "status",
        "data",
        "total_count",
        "returned_count",
        "truncated",
        "message",
        "error_code",
    }
    assert value["returned_count"] == len(value["data"])
    assert value["total_count"] >= value["returned_count"]
    assert value["truncated"] == (value["total_count"] > value["returned_count"])
    return value


@pytest.mark.parametrize(("name", "args"), ALL)
def test_nine_tools_found(database, name, args):
    result = envelope(invoke(database, name, args))
    assert result["status"] == "ok"
    assert result["data"]
    for row in result["data"]:
        for key in ("Total", "UnitPrice"):
            if key in row:
                assert isinstance(row[key], str)
                assert Decimal(row[key]) >= 0


@pytest.mark.parametrize(("name", "found", "missing"), CATALOG)
def test_catalog_not_found(database, name, found, missing):
    result = envelope(invoke(database, name, missing))
    assert result["status"] == "not_found"
    assert result["data"] == []


@pytest.mark.parametrize(("name", "args"), ALL)
def test_all_database_errors_are_json(database, name, args):
    class FailedDatabase:
        def query(self, *args, **kwargs):
            raise DatabaseQueryError("private SQL credential context")

    result = envelope(invoke(FailedDatabase(), name, args))
    assert result["status"] == "error"
    assert result["error_code"] == "database_error"
    assert "private SQL" not in str(result)


@pytest.mark.parametrize(("name", "args"), ALL)
def test_all_missing_arguments_are_valid_json(database, name, args):
    assert envelope(invoke(database, name, {}))["status"] == "invalid_input"


@pytest.mark.parametrize(("name", "args"), ACCOUNTS)
def test_all_accounts_require_trusted_context_before_sql(name, args):
    class NoQuery:
        def query(self, *args, **kwargs):
            pytest.fail("Unverified request must not execute SQL")

    assert invoke(NoQuery(), name, args, customer=None)["error_code"] == "access_denied"


@pytest.mark.parametrize(("name", "args"), ACCOUNTS)
def test_forged_customer_rejected_before_sql(name, args):
    class NoQuery:
        def query(self, *args, **kwargs):
            pytest.fail("Forged customer must not execute SQL")

    assert invoke(NoQuery(), name, args, customer=2)["error_code"] == "access_denied"


@pytest.mark.parametrize("name", ["get_support_rep_by_invoice", "get_invoice_line_items"])
def test_foreign_invoice_indistinguishable_from_absent(database, name):
    base = {"customer_id": "2"}
    foreign = invoke(database, name, {**base, "invoice_id": "98"}, customer=2)
    absent = invoke(database, name, {**base, "invoice_id": "999999"}, customer=2)
    assert foreign == absent
    assert absent["status"] == "not_found"


@pytest.mark.parametrize(
    "name", ["get_invoices_by_customer_sorted_by_date", "get_purchased_tracks"]
)
def test_no_invoices_is_honest_empty(database, name):
    # Trusted context is supplied by the app/verifier, not established by this factory.
    result = invoke(database, name, {"customer_id": "999999"}, customer=999999)
    assert result["status"] == "not_found"
    assert result["data"] == []


@pytest.mark.parametrize("bad", ["abc", "0", "-1", "1.5", "1 OR 1=1", "9" * 100, True, 1])
def test_bad_numeric_ids_do_not_query(bad):
    class NoQuery:
        def query(self, *args, **kwargs):
            pytest.fail("Bad ID must not execute SQL")

    assert invoke(NoQuery(), "get_track_details", {"track_id": bad})["status"] == "invalid_input"


@pytest.mark.parametrize(("name", "args"), ACCOUNTS)
def test_account_invalid_numeric_is_json(database, name, args):
    invalid = {**args, "customer_id": "nope"}
    assert invoke(database, name, invalid)["status"] == "invalid_input"
    if "invoice_id" in args:
        assert invoke(database, name, {**args, "invoice_id": "abc"})["status"] == "invalid_input"


@pytest.mark.parametrize("value", ["", " ", "%", "_", "' OR 1=1 --", "\\"])
def test_search_literals_cannot_broaden_catalog(database, value):
    result = invoke(database, "get_albums_by_artist", {"artist_name": value})
    assert result["status"] in {"invalid_input", "not_found"}


def test_substring_match_and_track_truth(database):
    albums = invoke(database, "get_albums_by_artist", {"artist_name": "AC/"})["data"]
    assert len(albums) == 2
    assert all(row["Artist"] == "AC/DC" for row in albums)
    track = invoke(database, "get_track_details", {"track_id": "1"})["data"][0]
    assert track["Name"] == "For Those About To Rock (We Salute You)"
    assert track["Artist"] == "AC/DC"
    assert track["UnitPrice"] == "0.99"
    assert {"Composer", "Milliseconds", "Bytes", "MediaType", "Genre"} <= track.keys()


def test_track_and_title_samples_disclose_total(database):
    artist = invoke(database, "get_tracks_by_artist", {"artist_name": "Iron Maiden"})
    expected = database.query(
        """
        SELECT COUNT(*) AS count FROM Track t JOIN Album al ON t.AlbumId=al.AlbumId
        JOIN Artist ar ON ar.ArtistId=al.ArtistId WHERE ar.Name=:name
    """,
        {"name": "Iron Maiden"},
    )[0]["count"]
    assert artist["returned_count"] == 20 < artist["total_count"] == expected
    title = invoke(database, "search_songs_by_title", {"title": "love"})
    assert title["returned_count"] == 10 < title["total_count"]


def test_genre_diversity_determinism_and_representative_truth(database):
    first = invoke(database, "get_songs_by_genre", {"genre_name": "Rock"})
    for _ in range(3):
        assert first == invoke(database, "get_songs_by_genre", {"genre_name": "Rock"})
    artists = [row["ArtistId"] for row in first["data"]]
    assert len(artists) == 10 == len(set(artists))
    assert artists == sorted(artists)
    counts = database.query(
        """
        SELECT COUNT(*) AS count, COUNT(DISTINCT al.ArtistId) AS artists
        FROM Track t JOIN Album al ON al.AlbumId=t.AlbumId
        JOIN Genre g ON g.GenreId=t.GenreId WHERE g.Name LIKE :pattern
    """,
        {"pattern": "%Rock%"},
    )[0]
    assert first["total_count"] == counts["count"]
    assert first["distinct_artist_count"] == counts["artists"]
    for row in first["data"]:
        minimum = database.query(
            """
            SELECT MIN(t.TrackId) AS tid FROM Track t JOIN Album al ON al.AlbumId=t.AlbumId
            JOIN Genre g ON g.GenreId=t.GenreId
            WHERE al.ArtistId=:aid AND g.Name LIKE :pattern
        """,
            {"aid": row["ArtistId"], "pattern": "%Rock%"},
        )[0]["tid"]
        assert row["TrackId"] == minimum


def test_invoice_order_totals_and_purchase_rows(database):
    invoices = invoke(database, "get_invoices_by_customer_sorted_by_date", {"customer_id": "1"})
    expected = database.query(
        """
        SELECT InvoiceId, InvoiceDate, Total FROM Invoice WHERE CustomerId=:cid
        ORDER BY InvoiceDate DESC, InvoiceId DESC
    """,
        {"cid": 1},
    )
    assert [row["InvoiceId"] for row in invoices["data"]] == [row["InvoiceId"] for row in expected]
    assert [Decimal(row["Total"]) for row in invoices["data"]] == [
        Decimal(str(row["Total"])) for row in expected
    ]
    tracks = invoke(database, "get_purchased_tracks", {"customer_id": "1"})["data"]
    prices = [Decimal(row["UnitPrice"]) for row in tracks]
    assert prices == sorted(prices, reverse=True)
    count = database.query(
        """
        SELECT COUNT(*) AS count FROM InvoiceLine il JOIN Invoice i ON il.InvoiceId=i.InvoiceId
        WHERE i.CustomerId=:cid
    """,
        {"cid": 1},
    )[0]["count"]
    assert len(tracks) == count
    assert len({row["InvoiceLineId"] for row in tracks}) == count


def test_invoice_details_and_rep_truth(database):
    result = invoke(database, "get_invoice_line_items", {"customer_id": "1", "invoice_id": "98"})
    expected = database.query(
        """
        SELECT InvoiceLineId FROM InvoiceLine WHERE InvoiceId=:iid ORDER BY InvoiceLineId
    """,
        {"iid": 98},
    )
    assert [row["InvoiceLineId"] for row in result["data"]] == [
        r["InvoiceLineId"] for r in expected
    ]
    rep = invoke(database, "get_support_rep_by_invoice", {"customer_id": "1", "invoice_id": "98"})
    expected = database.query(
        """
        SELECT e.EmployeeId FROM Invoice i JOIN Customer c ON c.CustomerId=i.CustomerId
        JOIN Employee e ON e.EmployeeId=c.SupportRepId WHERE i.InvoiceId=:iid
    """,
        {"iid": 98},
    )
    assert rep["data"][0]["EmployeeId"] == expected[0]["EmployeeId"]
    assert set(rep["data"][0]) == {"EmployeeId", "FirstName", "LastName", "Email", "Phone"}


def test_customer_bound_tools_do_not_share_context(database):
    a = build_tools(database, verified_customer_id=1)
    b = build_tools(database, verified_customer_id=2)

    def get(tools, cid):
        return json.loads(
            tools["get_invoices_by_customer_sorted_by_date"].invoke({"customer_id": cid})
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        ar, br = list(pool.map(lambda pair: get(*pair), [(a, "1"), (b, "2")]))
    assert {row["InvoiceId"] for row in ar["data"]}.isdisjoint(
        {row["InvoiceId"] for row in br["data"]}
    )
    assert get(a, "2")["error_code"] == "access_denied"


def test_tool_schemas_cannot_set_trusted_identity(database):
    tools = build_tools(database)
    assert len(tools) == 9
    for item in tools.values():
        assert "verified_customer_id" not in item.args
        assert all(arg.get("type") == "string" for arg in item.args.values())


@pytest.mark.parametrize("value", ["bad stored price", "NaN", "Infinity", "-0.01", "0.999"])
def test_bad_stored_prices_fail_as_json_without_rounding(value, caplog):
    class BadData:
        def query(self, *args, **kwargs):
            return [{"TrackId": 1, "UnitPrice": value}]

    result = invoke(BadData(), "get_track_details", {"track_id": "1"})
    assert result["status"] == "error"
    assert result["error_code"] == "stored_data_error"
    assert result["data"] == []
    assert "bad stored price" not in str(result) + caplog.text
