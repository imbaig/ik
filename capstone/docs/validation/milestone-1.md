# Milestone 1 — database and configuration validation

Date: November 7, 2026. Status: implemented, tested, independently reviewed; human
milestone acceptance pending. No commit or push performed. No LLM calls or UI yet.

## Implemented

Python 3.12.14 isolated environment, minimum dependency declarations, uv.lock and exact
runtime export; typed environment settings and secret-safe failures; Chinook 1.4.5 pinned
revision/checksum, bounded first download and verified atomic cache; in-memory SQLAlchemy
SQLite bootstrap/schema health; parameterized JSON query utility; phone normalization;
serialized threaded reads; query-only/authorizer write protection, bounded query time and
row count; explicit close/error handling; dataset attribution/license and ignored runtime files.

## Reproduction

From capstone/: `uv sync --locked --python 3.12`; bootstrap with
`PYTHONPATH=src uv run python -m music_store.db`; run `uv run pytest tests/ -v`,
`uv run ruff check src tests`, `uv run ruff format --check src tests`.
Tests use the bootstrap cache and perform no network or LLM calls. First bootstrap
requires internet; corrupted or incompatible cached data fails clearly rather than executing.

## Actual evidence

- Author: 52 pytest cases passed in 0.31s; JUnit: milestone-1-pytest.xml.
- Independent reviewer: 52 passed in 0.27s, Ruff checks passed.
- Author real first-download/second-offline-cache smoke: both healthy, 11 tables and
  59 customers; second initialization forced download to raise if called, so reuse proven.
- Actual snapshot has 3,503 tracks, 59 customers; no private rows logged in evidence.
- `uv sync --locked` passed; Ruff format/check passed. .env, SQL cache and .venv are ignored.

Coverage includes bound input/injection, Unicode, no rows, missing binding, mutation/PRAGMA/
ATTACH/extension rejection, thread sharing, time/row limits, schema/table/column failures,
corrupt cache/download, download failures/size bounds, phone edge cases, env precedence,
missing LLM key in offline mode, secret redaction and endpoint validation.

## Independent review

Reviewer `/root/milestone1_review`, separate read-only session; exact model not captured.
Initial findings M1-001 (P2 missing requirements file at review time) and M1-002 (P3 invalid
endpoint ports) were accepted and corrected. Reviewer re-ran tests and verified both fixes.
No remaining blocking findings within foundation scope. Review did not independently
exercise fresh dependency installation or first network download; author did the latter.
No specialized security skill was available/invoked; reviewer used approved plan/contracts
and project review guidance. Details: ../reviews/milestone-1-review.md.

## Limits and next gate

Account ownership enforcement belongs to domain tools, not this internal raw-SQL utility;
no raw SQL model tool is provided. Full LLM/agent/UI dependencies and Docker are deferred
to their slices. This milestone does not claim the nine-tool requirement or final 28+
course tool/DB coverage is complete merely because current foundation has 52 cases.
Next: Imran accepts milestone, then implement/review the nine catalog/account tool contracts.
