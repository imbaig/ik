# Milestone 2 — nine catalog and invoice tools

Date: November 7, 2026. Status: implemented, independently reviewed; human milestone
acceptance pending. Milestone 1 acceptance recorded separately. No commit/push or LLM calls.

## Delivered

Five catalog tools: artist albums, artist tracks, genre discovery, title search, track
lookup. Four account tools: newest-first invoices, highest-unit-price-first purchased
line items, invoice-specific support representative, invoice line items. All nine use
LangChain @tool with string input schemas and JSON success/empty/invalid/error envelopes.

SQL statements are fixed with bound parameters; literal LIKE wildcard characters are
escaped. Artist tracks sample <=20; title search <=10; genres <=10 unique artists using
lowest TrackId representative and stable ArtistId ordering. Count, returned_count and
truncation flags disclose sampling. Money is exact decimal text; corrupt/nonfinite/negative/
subcent values fail clearly instead of being rounded or fabricated.

Account tools are bound to an application-provided trusted ID per request; mismatched
customer IDs and absent verification are denied before SQL. Invoice-specific SQL always
filters ownership. Unowned and missing invoice IDs produce identical responses. No raw
SQL or trusted-context override is in tool schemas. The constructor does not authenticate
users: the future verifier must supply server-owned identity; do not cache tool sets
across customer sessions. No identity conversational flow or agents/UI built yet.

## Actual validation

- Author: **126 passed in 1.11s**, including 52 foundation + 74 tool cases.
- Independent reviewer: **126 passed in 1.07s; Ruff passed**.
- Author Ruff check and format check passed; uv sync --locked passed.
- Commands: `uv run pytest tests/ -q`, `uv run ruff check src tests`,
  `uv run ruff format --check src tests` after bootstrap described in README.
- Machine-readable test evidence: milestone-2-pytest.xml.

Coverage: each of nine found/missing-arguments/database-error contracts; all catalog
not-found cases; account empty/foreign/missing-invoice cases; malformed IDs rejected
before query; no verified context; forged customer; LIKE injection/wildcards; known
track/album truth; exact money; deterministic genre diversity/counts; sorted invoices
and purchases; line-item counts/no accidental deduplication; safe rep fields; independent
concurrent customer-bound tools. No live LLM/billable provider evaluation performed.

## Review and disposition

Read-only independent reviewer: `/root/milestone2_review`; model metadata not captured.
Initial M2-001 (P2): malformed stored money raised decimal.InvalidOperation outside JSON
handling. Author accepted and fixed sanitized stored_data_error handling, exact-cent
validation and five regressions. Reviewer independently re-ran and verified resolved;
no remaining findings in this scope. This is not Imran's milestone approval.

Final source hashes in ../reviews/milestone-2-code-manifest.json. Domain reviewer hash:
c8ef3e7d777280c6a35f5c96b7b56a3f7ae2ee6161ce35ec39f3eaeb1eaf259e.
Tool tests hash: c3107894ad5e63abecb585dcdb644159f3ae27d5f15c8307917398a539fc4b8e.
No specialized security skill was invoked; review used approved contracts and code/test
inspection. Prior foundation review is not represented as review of new tool code.

## Next

After human acceptance, build structured verification, trusted state, SystemMessage
injection and human-in-the-loop interrupt/resume. Full agent/UI/Docker dependencies,
conversation evaluations and final public repo delivery remain future milestones.
