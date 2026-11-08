"""Verified dataset bootstrap and serialized, read-only in-memory SQL access.

Internal utilities only: raw SQL is never exposed as an agent tool. Bootstrap executes
only the checksum-verified upstream SQL. Runtime queries use SQLAlchemy text bindings.
"""

import hashlib
import json
import logging
import os
import re
import sqlite3
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool

DATASET_REVISION = "c14389e4466cb2dac9fe97782b8dfc6113ed3ae2"
DATASET_SHA256 = "caf31d698a4a79c628215b552dfe6575e71be052ae02b8f18e763498f55f5d44"
DATASET_URL = (
    "https://raw.githubusercontent.com/lerocha/chinook-database/"
    + DATASET_REVISION
    + "/ChinookDatabase/DataSources/Chinook_Sqlite.sql"
)
MAX_DOWNLOAD_BYTES = 8 * 1024 * 1024
MAX_RESULT_ROWS = 10000
logger = logging.getLogger(__name__)
REQUIRED_COLUMNS = {
    "Artist": {"ArtistId", "Name"},
    "Album": {"AlbumId", "Title", "ArtistId"},
    "Track": {
        "TrackId",
        "Name",
        "AlbumId",
        "MediaTypeId",
        "GenreId",
        "Composer",
        "Milliseconds",
        "Bytes",
        "UnitPrice",
    },
    "Genre": {"GenreId", "Name"},
    "MediaType": {"MediaTypeId", "Name"},
    "Customer": {
        "CustomerId",
        "FirstName",
        "LastName",
        "Email",
        "Phone",
        "SupportRepId",
    },
    "Employee": {"EmployeeId", "FirstName", "LastName", "Email", "Phone"},
    "Invoice": {
        "InvoiceId",
        "CustomerId",
        "InvoiceDate",
        "Total",
        "BillingAddress",
        "BillingCity",
        "BillingState",
        "BillingCountry",
        "BillingPostalCode",
    },
    "InvoiceLine": {"InvoiceLineId", "InvoiceId", "TrackId", "UnitPrice", "Quantity"},
}


class DatasetError(RuntimeError):
    """Dataset unavailable, corrupt or incompatible; safe to show without raw SQL."""


class DatabaseQueryError(RuntimeError):
    """Sanitized internal query failure, distinguishable from an empty result."""


def normalize_phone(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    digits = re.sub(r"[^0-9]", "", value)
    return ("+" if value.startswith("+") and digits else "") + digits


def _download() -> bytes:
    try:
        with urlopen(DATASET_URL, timeout=30) as response:
            data = response.read(MAX_DOWNLOAD_BYTES + 1)
    except (OSError, URLError):
        raise DatasetError("Dataset download failed; check connectivity and retry") from None
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise DatasetError("Dataset download exceeds size limit")
    return data


def _verify(data: bytes) -> None:
    if hashlib.sha256(data).hexdigest() != DATASET_SHA256:
        raise DatasetError("Dataset checksum mismatch; restore the pinned snapshot before retrying")


def cached_sql(cache_dir: Path) -> str:
    """Reuse verified cache; atomic writes prevent partially downloaded SQL being loaded."""
    cache_dir = Path(cache_dir)
    path = cache_dir / ("Chinook-" + DATASET_SHA256 + ".sql")
    try:
        if path.exists():
            if path.stat().st_size > MAX_DOWNLOAD_BYTES:
                raise DatasetError("Cached dataset exceeds size limit")
            data = path.read_bytes()
            _verify(data)
        else:
            data = _download()
            _verify(data)
            cache_dir.mkdir(parents=True, exist_ok=True)
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(dir=cache_dir, delete=False) as handle:
                    temp_path = Path(handle.name)
                    handle.write(data)
                os.replace(temp_path, path)
            finally:
                if temp_path is not None:
                    temp_path.unlink(missing_ok=True)
        return data.decode("utf-8-sig")
    except (OSError, UnicodeError):
        raise DatasetError(
            "Dataset cache cannot be read or written; check cache permissions"
        ) from None


def _authorize(action, arg1, arg2, database_name, trigger):
    if action in {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_RECURSIVE}:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_FUNCTION:
        return (
            sqlite3.SQLITE_DENY
            if (arg2 or "").lower() in {"load_extension", "writefile", "readfile"}
            else sqlite3.SQLITE_OK
        )
    return sqlite3.SQLITE_DENY


class Database:
    """One private connection shared safely across worker threads; no public engine handle."""

    def __init__(self, sql: str, *, query_timeout_seconds: float = 5):
        if not 0 < query_timeout_seconds <= 60:
            raise ValueError("query_timeout_seconds must be positive and <=60")
        self._lock = threading.RLock()
        self._closed = False
        self._query_timeout_seconds = query_timeout_seconds
        self._engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False, "cached_statements": 0},
            hide_parameters=True,
        )
        try:
            with self._engine.connect() as connection:
                raw = connection.connection.driver_connection
                raw.executescript(sql)
                inspector = inspect(connection)
                tables = set(inspector.get_table_names())
                if not REQUIRED_COLUMNS.keys() <= tables:
                    raise DatasetError(
                        "Dataset schema is incompatible: required tables are missing"
                    )
                for table, required in REQUIRED_COLUMNS.items():
                    actual = {column["name"] for column in inspector.get_columns(table)}
                    if not required <= actual:
                        raise DatasetError(
                            "Dataset schema is incompatible: required columns are missing"
                        )
                self._table_count = len(tables)
                connection.execute(text("PRAGMA query_only = ON"))
                if connection.execute(text("PRAGMA query_only")).scalar_one() != 1:
                    raise DatasetError("Read-only database protection could not be enabled")
                raw.set_authorizer(_authorize)
            self.verify_database()
        except Exception as exc:
            self._engine.dispose()
            self._closed = True
            if isinstance(exc, DatasetError):
                raise
            raise DatasetError(
                "Dataset initialization failed; restore the pinned snapshot"
            ) from None

    def query(self, sql: str, params: dict | None = None) -> list[dict]:
        """Execute internal SQL with bindings; deny writes, PRAGMA changes and attachments."""
        with self._lock:
            if self._closed:
                raise DatabaseQueryError("Database is closed; initialize it before querying")
            try:
                with self._engine.connect() as connection:
                    raw = connection.connection.driver_connection
                    deadline = time.monotonic() + self._query_timeout_seconds
                    raw.set_progress_handler(lambda: time.monotonic() >= deadline, 1000)
                    try:
                        result = connection.execute(text(sql), params or {})
                        rows = result.mappings().fetchmany(MAX_RESULT_ROWS + 1)
                        if len(rows) > MAX_RESULT_ROWS:
                            raise DatabaseQueryError("Query result exceeds the allowed row limit")
                        return [dict(row) for row in rows]
                    finally:
                        raw.set_progress_handler(None, 0)
            except (SQLAlchemyError, sqlite3.Error, ValueError, TypeError):
                logger.warning("database_query_failed")
                raise DatabaseQueryError(
                    "Database query failed; retry or contact support"
                ) from None

    def run_query_safe(self, sql: str, params: dict | None = None) -> str:
        """Return a JSON row array, [] for no rows; errors raise sanitized exceptions."""
        return json.dumps(self.query(sql, params), ensure_ascii=False, allow_nan=False)

    def verify_database(self) -> dict:
        rows = self.query("SELECT COUNT(*) AS count FROM Customer")
        return {
            "healthy": True,
            "table_count": self._table_count,
            "customer_count": rows[0]["count"],
        }

    def close(self) -> None:
        with self._lock:
            if not self._closed:
                self._engine.dispose()
                self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def initialize_database(cache_dir: Path) -> Database:
    return Database(cached_sql(cache_dir))


def main() -> None:
    """Offline-after-first-fetch health check; no LLM credentials required."""
    from .config import load_settings

    with initialize_database(load_settings().chinook_cache_dir) as database:
        print(json.dumps(database.verify_database()))
        # Exercise shared in-memory reads without exposing private customer rows.
        with ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(lambda _: database.query("SELECT COUNT(*) FROM Track"), range(2)))


if __name__ == "__main__":
    main()
