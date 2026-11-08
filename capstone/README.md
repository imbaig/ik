# Music Store AI

An Agentic AI capstone for database-grounded music discovery and verified purchase support.
Submission deadline: November 20, 2026. Approved baseline: `specs/001-music-store/`.

## Current implementation

Working milestone7 baseline: Gradio chat, LangGraph supervisor and catalog/invoice
specialists, nine grounded tools, verification interrupts/resume, customer-scoped
process-local memory, read-only in-memory Chinook, and metadata-only telemetry.
Baseline evidence:304 automated tests,16/16 live conversation cases and final blind
preference precision100%/recall97.44%. These are recorded runs, not general guarantees.
See [validation and limits](docs/validation/milestone-7.md) and
[independent review](docs/reviews/milestone-7-review.md).

Run the live app after setup:

```sh
# Create .env from .env.example if .env does not already exist; add your own API key.
uv run python app.py
# Open http://127.0.0.1:7860
```

Ask “Show my latest invoice and its line items”, then provide sample customer ID1 or2
when prompted. Catalog browsing requires no verification. Use New conversation to switch
customers. Sample identity matching is a course demonstration, not production authentication.
Preferences survive conversations within a process; restart loses them. Docker/clean-setup
release validation and final submission are pending.

For the credential-free browser QA harness:

```sh
PYTHONPATH=src:tests uv run python tests/ui_harness.py
# http://127.0.0.1:7861 — deterministic models, real DB/graphs; not live quality evidence
```

## Setup and verification

Run from this directory, using Python 3.12 and [uv](https://docs.astral.sh/uv/):

```sh
cd capstone
uv sync --locked --python 3.12
PYTHONPATH=src uv run python -m music_store.db
uv run pytest tests/ -v
uv run ruff check src tests
uv run ruff format --check src tests
```

If already inside `capstone/`, omit the `cd` line. The health command downloads the official
pinned SQL once, verifies SHA-256, caches it in `.cache/chinook/`, validates schema and opens
an in-memory database. Subsequent runs use the verified cache without network access.
Bootstrap before running tests; tests themselves never download data or contact an LLM.
A checksum mismatch fails closed: restore the known-good pinned cache, or remove the corrupt
cache deliberately and rerun bootstrap. It never silently accepts changed upstream data.

Expected snapshot: 59 customers, 3,503 tracks; health reports 11 total tables (the course
names nine domain tables; the dataset also includes Playlist and PlaylistTrack).

For pip-based environments:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
PYTHONPATH=src python -m music_store.db
python -m pytest tests/ -v
```

`pyproject.toml` and `requirements.txt` state runtime constraints; `uv.lock` pins runtime
and test tools, while `requirements.lock` exports exact runtime versions, including Gradio and agent packages.

## Configuration

Copy `.env.example` to `.env` for local overrides. Process environment values override the
file; loading settings does not mutate the process environment. No actual keys are shipped.

| Variable | Default / purpose |
|---|---|
| OPENAI_API_KEY | Required for the live app/evaluations; not needed for offline tests |
| MODEL_NAME | gpt-4o-mini; configurable provider model |
| OPENAI_API_BASE | https://api.openai.com/v1; HTTPS or local HTTP, no credentials in URL |
| TEMPERATURE | 0; validated 0–2 |
| PORT | 7860; validated 1–65535 |
| HOST | 127.0.0.1; container may explicitly select 0.0.0.0 |
| REQUEST_TIMEOUT_SECONDS | 30; model request timeout per attempt |
| MAX_ATTEMPTS | 2; maximum model attempts |
| MAX_GRAPH_STEPS | 12; shared specialist model/tool action budget |
| CHINOOK_CACHE_DIR | .cache/chinook, relative to working directory |

The database has its own five-second query budget and 10,000-row hard limit, returning a
sanitized error instead of silently truncating. Internal `run_query_safe()` returns JSON
row arrays; errors raise `DatabaseQueryError`. Domain tools wrap errors in JSON envelopes. No arbitrary SQL tool is exposed to the
model. Trusted customer ownership is enforced independently of database read-only controls.

## Architecture and review

The runtime is local Gradio → supervisor → catalog/invoice specialists →
parameterized tools → Chinook, with an external configurable LLM endpoint and isolated
session/preference state. For full diagrams and approved constraints, see:

- [Feature specification](specs/001-music-store/spec.md)
- [Technical plan](specs/001-music-store/plan.md) and [tool contracts](specs/001-music-store/contracts.md)
- [Business hero use cases](docs/business-use-cases.md)
- [Review workflow](docs/development-review-workflow.md) and [audit ledger](docs/audit-ledger.md)
- [Milestone 1 validation](docs/validation/milestone-1.md)

GitHub Spec Kit provides the spec workflow. Changes are checked by a separate read-only
reviewer agent; milestone acceptance remains with Imran. Baseline 001 approval is recorded
against file hashes. Original flat specs are historical drafts, not the current baseline.

## Dataset and limitations

Chinook 1.4.5 by Luis Rocha is attributed in [provenance](data/provenance.json) and its
[license](data/CHINOOK-LICENSE.txt). The SQL snapshot, runtime databases, secrets and raw
traces are excluded from Git. Dataset upgrades require explicit provenance/schema/test
review; there is no automatic schema migration or mutable upstream download on every run.
The identity matching flow is a sample-data course demonstration, not production
authentication. Memory across application restarts is outside the approved baseline.

## Domain tools

`build_tools(database, verified_customer_id=...)` creates nine LangChain tools with
fixed SQL and JSON envelopes. Five catalog tools work without identity. Four account
tools reject calls without trusted context, reject mismatched customer IDs and filter
invoice ownership. This factory does not authenticate anyone: the verification
layer supplies the context from server-owned state. Never build it from model/user
arguments or cache customer-bound tool instances across sessions.

Catalog substring matching escapes literal percent/underscore characters. Artist track
samples cap at 20; title samples at 10; genres return up to 10 distinct artists, with
track totals and deterministic representatives. Monetary amounts are decimal strings.
`docs/validation/milestone-2.md` records exact scope, tests and review evidence.

## Identity and human-in-the-loop slice

`VerificationService` owns session handles, uses a real LangGraph checkpointer and
interrupt/Command-resume, and resolves verified identity at account-tool execution time.
Create a server-owned session; start verification for a pending account request; reply
with corrected details or an explicit cancel/catalog-only action. Reset invalidates the
old handle and deletes its checkpoint history. A free-text ID never switches an already
verified customer; use New conversation. Gradio keeps handles in server-owned State
and ConversationService integrates verification with the supervisor.

`LLMIdentifierExtractor(load_settings())` uses the configured OpenAI-compatible model
with structured Pydantic output. Only this live adapter needs a key; tests use a test
extractor and never call the provider. Matching the sample ID/email/phone is not production
authentication. Phone/email no-match and ambiguity do not disclose candidate customers.

Raw verification text is sent to the configured extraction model when live mode is used
and may exist in in-memory checkpoint history until reset/process termination; it is not
written to application logs or telemetry. Use sample identifiers for the capstone.

## Supervisor and specialists

Milestone 4 adds `ConversationService` and `AgentRuntime`: structured routing, scoped
supervisor phases, hand-built catalog loop, prebuilt invoice agent and invoice-first
mixed requests integrated with verification. The final renderer uses captured tool data
instead of unsupported model prose. `build_conversation_service(database, settings)`
wires configured provider adapters. Milestone7 records16/16 live conversation scenarios
and304 offline tests, with separate independent review. Docker delivery remains pending.
See docs/validation/milestone-7.md for current evidence and the archived-supervisor/API
deprecation limitation; progress is tracked in docs/implementation-progress.md.

## Customer preference memory

Milestone 5 adds `PreferenceMemory` with LangGraph InMemoryStore, trusted customer/dataset
namespaces, atomic union-only writes, structured UserProfile extraction and explicit
evidence filtering. Only verified user turns and the currently verified pending request
are eligible; anonymous or cancelled history is never adopted later. The catalog receives
saved tastes as context but still must query tools for store facts. New conversations
require verification to recall preferences. Reset clears chat/identity, not account memory;
process restart loses memory, as the course FAQ permits. No removal/correction operation
is provided by the union-only baseline.

The evidence filter is deliberately conservative and language-limited; it is not a general
semantic guarantee. Final blind v4 live evaluation reached precision100%/recall97.44%,
with a documented conservative artist-name miss.
Run the nonbillable candidate-filter probes with:

```sh
PYTHONPATH=src uv run python -m music_store.preference_eval --mode guardrail --output docs/validation/memory-guardrail.json
```

Guardrail mode alone leaves live quality and SC-004 target unmet. A provider run uses
`--mode live` and OPENAI_API_KEY; that mode makes billable model calls.
The 42-case corpus includes reviewed negative/quoted/hypothetical cases and is suitable
for regression, not an unbiased held-out estimate after tuning on it. A separate held-out
set is required for the final live quality claim.

## Contributing through issues

Use the GitHub capstone feedback form. The proposed queue, independent review, human
merge gate and credential boundaries are in [issue-driven development](docs/issue-driven-development.md).
Offline PR checks are defined at ../.github/workflows/capstone-ci.yml. Hosted issue
implementation and automatic reviewer access require separate account/repository setup;
no listener is implied by the workflow file. Live evaluations remain local for this trial.
