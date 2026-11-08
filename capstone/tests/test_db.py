import json
from concurrent.futures import ThreadPoolExecutor
from urllib.error import URLError

import pytest

from music_store import db
from music_store.db import Database, DatabaseQueryError, DatasetError, normalize_phone


def test_health(database):
    health = database.verify_database()
    assert health["healthy"] is True
    assert health["customer_count"] == 59
    assert health["table_count"] >= 9


def test_basic_query_json(database):
    assert json.loads(database.run_query_safe("SELECT COUNT(*) AS count FROM Track")) == [
        {"count": 3503}
    ]


def test_parameterized_lookup(database):
    rows = database.query("SELECT CustomerId FROM Customer WHERE CustomerId = :cid", {"cid": 5})
    assert rows == [{"CustomerId": 5}]


def test_empty_is_json_array(database):
    assert (
        database.run_query_safe(
            "SELECT CustomerId FROM Customer WHERE CustomerId = :cid", {"cid": 99999}
        )
        == "[]"
    )


def test_quote_unicode_roundtrip(database):
    assert database.query("SELECT :value AS value", {"value": "O'Brien — São Paulo"}) == [
        {"value": "O'Brien — São Paulo"}
    ]


def test_injection_stays_data(database):
    assert (
        database.query(
            "SELECT CustomerId FROM Customer WHERE Email = :email",
            {"email": "' OR 1=1; DROP TABLE Customer; --"},
        )
        == []
    )
    assert database.verify_database()["customer_count"] == 59


@pytest.mark.parametrize(
    "statement",
    [
        "DELETE FROM Customer",
        "UPDATE Track SET UnitPrice=0",
        "DROP TABLE Invoice",
        "PRAGMA query_only=OFF",
        "ATTACH DATABASE ':memory:' AS other",
        "CREATE TEMP TABLE stolen AS SELECT * FROM Customer",
        "SELECT load_extension('anything')",
    ],
)
def test_runtime_write_and_escape_denied(database, statement):
    with pytest.raises(DatabaseQueryError):
        database.query(statement)
    assert database.verify_database()["customer_count"] == 59


def test_multiple_statements_denied(database):
    with pytest.raises(DatabaseQueryError):
        database.query("SELECT 1; DELETE FROM Customer")


def test_errors_are_sanitized(database, caplog):
    secret = "private-token-do-not-print"
    with pytest.raises(DatabaseQueryError) as error:
        database.query("SELECT * FROM missing_table WHERE email = :email", {"email": secret})
    assert secret not in str(error.value) + caplog.text
    assert "missing_table" not in str(error.value) + caplog.text


def test_missing_binding_errors(database):
    with pytest.raises(DatabaseQueryError):
        database.query("SELECT :missing")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("+1 (555) 123-4567", "+15551234567"),
        ("5551234567", "5551234567"),
        ("555-123-4567", "5551234567"),
        ("", ""),
        (None, ""),
        ("  +44 (20) 1234-5678  ", "+442012345678"),
        ("+", ""),
    ],
)
def test_phone_normalization(value, expected):
    assert normalize_phone(value) == expected


def test_threaded_reads_share_healthy_snapshot(database):
    def read_customer(customer_id):
        return database.query(
            "SELECT CustomerId FROM Customer WHERE CustomerId=:cid", {"cid": customer_id}
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(read_customer, range(1, 30)))
    assert results == [[{"CustomerId": i}] for i in range(1, 30)]


def test_missing_tables_fail_fast():
    with pytest.raises(DatasetError, match="required tables"):
        Database("CREATE TABLE Customer (CustomerId INTEGER);")


def test_missing_columns_fail_fast(sql_snapshot):
    incompatible = sql_snapshot + "\nALTER TABLE Track RENAME COLUMN Composer TO OldComposer;"
    with pytest.raises(DatasetError, match="required columns"):
        Database(incompatible)


def test_corrupt_sql_fails_safely():
    with pytest.raises(DatasetError, match="initialization failed"):
        Database("not valid SQL secret-context")


def test_closed_database_fails_clearly(sql_snapshot):
    database = Database(sql_snapshot)
    database.close()
    database.close()
    with pytest.raises(DatabaseQueryError, match="closed"):
        database.query("SELECT 1")


def test_expensive_query_is_bounded(sql_snapshot):
    with Database(sql_snapshot, query_timeout_seconds=0.001) as database:
        with pytest.raises(DatabaseQueryError):
            database.query("""
                WITH RECURSIVE numbers(x) AS (
                    SELECT 1 UNION ALL SELECT x+1 FROM numbers WHERE x<100000000
                ) SELECT SUM(x) FROM numbers
            """)
        assert database.query("SELECT 1 AS value") == [{"value": 1}]


def test_result_limit_does_not_silently_truncate(database, monkeypatch):
    monkeypatch.setattr(db, "MAX_RESULT_ROWS", 1)
    with pytest.raises(DatabaseQueryError, match="row limit"):
        database.query("SELECT TrackId FROM Track LIMIT 2")


def test_download_and_cache_reuse(tmp_path, sql_snapshot, monkeypatch):
    calls = []

    def download():
        calls.append(1)
        # The official file starts with a newline and has no BOM.
        return sql_snapshot.encode("utf-8")

    monkeypatch.setattr(db, "_download", download)
    assert db.cached_sql(tmp_path) == sql_snapshot
    assert db.cached_sql(tmp_path) == sql_snapshot
    assert len(calls) == 1
    assert len(list(tmp_path.iterdir())) == 1


def test_corrupt_cache_not_executed_or_replaced(tmp_path, monkeypatch):
    path = tmp_path / ("Chinook-" + db.DATASET_SHA256 + ".sql")
    path.write_text("DROP TABLE Customer;")
    monkeypatch.setattr(db, "_download", lambda: pytest.fail("Must not silently replace bad cache"))
    with pytest.raises(DatasetError, match="checksum"):
        db.cached_sql(tmp_path)
    assert path.read_text() == "DROP TABLE Customer;"


def test_bad_download_not_cached(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "_download", lambda: b"not the official data")
    with pytest.raises(DatasetError, match="checksum"):
        db.cached_sql(tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_network_failure_is_actionable(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise URLError("private network details")

    monkeypatch.setattr(db, "urlopen", fail)
    with pytest.raises(DatasetError, match="check connectivity") as error:
        db.cached_sql(tmp_path)
    assert "private network" not in str(error.value)


def test_oversize_download_rejected(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def read(self, size):
            return b"x" * size

    monkeypatch.setattr(db, "urlopen", lambda *a, **k: Response())
    monkeypatch.setattr(db, "MAX_DOWNLOAD_BYTES", 16)
    with pytest.raises(DatasetError, match="size limit"):
        db._download()
