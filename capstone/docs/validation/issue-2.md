# Issue 2 cloud trial validation

Base: current main `3f26baac94722a3c828a60088cdb3771a4a07f4d` (historical brief baseline not used).
Author: Codex `/root`. Only capstone changes; no merge authorization.
Duplicate check: GitHub open PR search returned none; all branches paginated (only main);
registered task lookup returned none. Local checkout initially clean.

Approved-spec mapping: FR-006 verification, FR-007 one active customer per chat;
account ownership contracts and US2 private-account isolation. No approved-spec edits.
Explicit numeric customer labels differing from trusted identity now receive a fixed
refusal before router, specialist, memory extraction or account lookup. The text does
not interpolate the asserted identifier or reveal account existence. Bare invoice IDs
and matching customer IDs retain the existing flow and ownership guards.

## Offline evidence

Using project-local ignored `.cache/uv` and `.cache/pip`, Python 3.12, uv 0.12.5,
`uv sync --locked --python 3.12` succeeded without lockfile changes.
Commands from capstone (uv executable `.cache/cloud-tools/bin/uv`):

- `uv run --locked pytest -q tests/test_agents.py tests/test_verification.py tests/test_conversation_eval.py tests/test_telemetry.py`: 99 passed.
- `uv run --locked pytest -q --junitxml=test-results/issue-2.xml`: 313 passed.
- `uv run --locked ruff check src tests app.py`: passed.
- `uv run --locked ruff format --check src tests app.py`: passed, 30 files.

Existing framework deprecation warnings remain. These tests use deterministic doubles,
real graphs and SQL fixtures; they are not live-model evidence. Initial test authoring
runs failed on a reserved pytest parameter and a reset fixture still targeting customer1;
both test fixtures were corrected before the successful runs.

## Required live evaluation — PENDING

No application API key is configured in this cloud environment. No provider calls,
credential searches or credential copying were performed. Imran must run the targeted
live substitution evaluation locally on the exact final draft PR head SHA, using the
existing ignored local .env. Verify `git rev-parse HEAD` equals that SHA before and after:

```sh
export UV_CACHE_DIR="$PWD/.cache/uv"
export PIP_CACHE_DIR="$PWD/.cache/pip"
uv sync --locked --python 3.12
PYTHONPATH=src uv run --locked python -m music_store.conversation_eval \
  --cases evals/issue-2-substitution.json \
  --output .cache/evals/issue-2-live.json
```

Publish a redacted summary identifying exact Git SHA and source/cases hashes, model
configuration, actual results and semantic transcript review. Keep raw transcripts in
ignored .cache/evals. The targeted case requires an explicit refusal with no dispatch or
records, then successful same-account invoice access. Mechanical success alone is not
human approval. Any implementation change requires affected validation and review again.
Independent read-only reviewer identity, report, author dispositions and exact reviewed
SHA are recorded in the draft PR conversation/body so recording them does not mutate
the reviewed implementation revision. No agent or tests approve merging; only Imran does.

## Independent review repair cycle 1

Reviewer `/root/issue2_readonly_review` reviewed implementation
`b53702231899051f482d530d26873af8a1bc63b8` and raised I2-R1 (medium): the
new refusal status was missing from the telemetry outcome allowlist, dropping request
events. Author accepted the finding. Added the explicit outcome and an end-to-end
regression checking retained request/outcome/latency counts without raw identity text.
The full unchanged first report is preserved in draft PR #3, comment 6722819677.
Human-adopted and mandatory flags are undecided (null); no human closure/waiver claimed.
Final exact-SHA recheck and disposition are recorded in that PR conversation.
