from pathlib import Path

import pytest

from music_store.db import DATASET_SHA256, Database


@pytest.fixture(scope="session")
def sql_snapshot():
    path = (
        Path(__file__).resolve().parents[1]
        / ".cache/chinook"
        / ("Chinook-" + DATASET_SHA256 + ".sql")
    )
    if not path.exists():
        pytest.fail("Bootstrap dataset first: PYTHONPATH=src uv run python -m music_store.db")
    import hashlib

    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == DATASET_SHA256
    return data.decode("utf-8-sig")


@pytest.fixture(scope="session")
def database(sql_snapshot):
    with Database(sql_snapshot) as db:
        yield db
