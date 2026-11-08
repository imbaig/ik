# Milestone 3 — identity verification and human-in-the-loop

Date: November 7, 2026. Implemented/tested/independently reviewed; Imran acceptance
pending. No commit/push, billable API call or browser UI. M2 acceptance recorded.

## Delivered

Pydantic UserInput and configured ChatOpenAI structured extractor; deterministic exact
ID, case-insensitive email and normalized-phone matching; explicit-identifier grounding,
ambiguity rejection; real LangGraph interrupt/Command-resume with in-memory checkpointer;
server-owned session registry and per-session locks; verified ID in trusted state and
SystemMessage; account execution resolves identity at call time and uses existing ownership
checks. No user-supplied graph updates accepted by the service.

Missing/unknown details pause and preserve the pending request. Correction re-verifies;
cancel/catalog-only clears the account branch. A bounded five-attempt default requires
new conversation after exhaustion. Reset invalidates the old handle and deletes checkpoint
history; subsequent account queries need new verification. Separate sessions do not share
identity, while actions within each session serialize safely. Free-text IDs cannot switch
an already verified identity. Matching sample identifiers remains a demo, not production auth.

## Actual tests

Author: **158 passed in 2.07s**; independent reviewer reran **158 passing** and Ruff passed.
Author Ruff/format checks pass. JUnit: milestone-3-pytest.xml. Current total: 52 foundation,
74 tool and 32 verification/adapter test cases. No provider quality results implied.

The new cases cover ID/email/phone; miss/correction; actual interrupt snapshots and resume;
SystemMessage injection; pending request; forged account arguments; cancellation/catalog-only;
reset/checkpoint deletion/expired handles; simultaneous sessions; retry exhaustion;
provider and DB failures; duplicate phone ambiguity; hallucinated/multiple/invalid candidate
outputs; schema failures; invalid input/handle; structured-adapter configuration via fake
client; signed/decimal/scientific ID mis-extraction; retry-limit bypass regression.

Run from capstone/: `uv sync --locked --python 3.12`, bootstrap as in README, then
`uv run pytest tests/ -v`, `uv run ruff check src tests` and format check. Tests perform no
network or LLM calls. Live adapter construction requires OPENAI_API_KEY; the API call is
only made by extract(). Live verification uses sample IDs and sends identifier text to
the configured endpoint. Raw verification inputs may remain in process-local checkpoint
history until reset/process termination; no application telemetry/log records are emitted
with the values. No assertion of live-model recognition quality has been made.

## Independent findings and work evidence

Reviewer: `/root/milestone3_review`, separate read-only session, exact model not captured.
Initial 152-case suite passed, but reviewer reproduced two P2 issues:

| Finding | Author response | Reviewer verification |
|---|---|---|
| M3-SEC-01: retry exhaustion bypass through start() | Reject exhausted sessions before invocation and before extractor in verify node; reset starts fresh | Fixed; same-handle bypass/reset regression passes |
| M3-SEC-02: model could convert original -1 to candidate 1 | Signed-token/boundary validation plus malformed-input regressions | Fixed; -1/+1/abc-1/1.0/1e3 cannot verify candidate 1 |

Independent commands: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -p no:cacheprovider`
and `.venv/bin/ruff check --no-cache .`. Final 158 tests passed; Ruff passed. No edits,
reference implementation, subagents or additional review skills used by reviewer. This
saved report records findings, dispositions and commands, not a full raw agent transcript.
Reviewer approves handoff readiness, not human milestone acceptance.

## Scope limits

This is a service-level identity graph; it does not yet render Gradio prompts or route
mixed queries via the supervisor. Request continuation is represented as retained state
for the next orchestration milestone; account actions are exercised directly via guarded
service calls. The future UI must keep session handles server-owned and avoid client-selected
thread IDs. Memory loading and full remaining_steps graph state join the later full graph.
Live extraction evaluation and UI walkthrough remain required before final delivery.

Next: milestone disposition, then supervisor/catalog/invoice agent graph and live-provider
integration/evaluation as credentials become available. November 20 deadline unchanged.
