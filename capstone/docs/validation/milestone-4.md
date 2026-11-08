# Milestone 4 — supervisor and specialist agents

November 7, 2026. Implemented, tested and independently reviewed; human acceptance
pending. No live provider evaluation, browser UI, preference memory, commit or push.

## Delivered runtime

- Structured LLM intent routing: catalog, invoice, mixed, greeting and off-topic. Greeting
  and off-topic paths return directly with no specialist or domain tool call.
- Hand-built catalog assistant/tools ReAct graph, prebuilt invoice ReAct agent, and
  course-required langgraph-supervisor utility for specialist dispatch.
- Mixed requests execute two constrained supervisor phases: invoice then catalog. Only
  the permitted specialist is available per phase, so a model cannot reverse order.
- Invoice-derived TrackId/Name references are passed to catalog for dependent follow-ups;
  billing/contact fields are excluded. Catalog still queries its own tools for facts.
- Identity service integration: invoice/mixed requests pause, retry/resume their original
  task, or cancel. Catalog-only continuation explicitly cancels the account branch.
- Application resolves current verified identity under the same session lock as model
  execution; free-text customer IDs cannot alter it. Reset clears conversation history,
  pending task, verification checkpoints and old handles.
- Versioned prompts for supervisor/catalog/invoice each contain the six grounding rules.
- One shared model/tool action budget bounds both supervisor phases; each graph also
  has a recursion limit. Model timeouts/retries come from validated configuration.
- Customer-facing store facts are rendered from actual server-recorded tool envelopes;
  model-authored factual prose is not shown. Refund requests receive a deterministic
  unsupported-action explanation. Errors and partial completion never claim full success.
- Recent conversation context supports follow-ups; verification responses are represented
  by a placeholder in specialist/router history, not raw identifier input.

## Actual validation

Author: **184 tests passed in 2.70s**, Ruff and format checks passed. Independent reviewer
reran **184 tests passing; Ruff passed**. Total: prior 158 plus 26 agent/integration cases.
JUnit: milestone-4-pytest.xml. Test code: tests/test_agents.py.

Tests use scripted BaseChatModel responses but execute real LangGraph handoffs, tool
nodes, prebuilt invoice and hand-built catalog graphs, identity interrupts, actual database
tools and renderer. They establish deterministic orchestration/guard behavior, not live
LLM classification/tool-choice quality. Provider credentials and live evaluation remain
required later. No API call or billable request was made.

Coverage: catalog/invoice/mixed/off-topic/greeting; verified SystemMessage; wrong-customer
and wrong-specialist tools; invoice-first order; pending query resume; catalog-only and
cancel; reset; shared-service session identity; concurrent customer workflows; history
follow-up; raw verification text omission; no-tool hallucinated outputs blocked; global
action budget; sanitized model failure/partial results; truncation/empty disclosures;
dependent mixed track references; exact tool facts; refund limitation.

Reproduce from capstone/: `uv sync --locked --python 3.12`, bootstrap dataset as README,
then `uv run pytest tests/ -q`, `uv run ruff check src tests` and format check.

## Independent findings

Reviewer: `/root/milestone4_review`, distinct read-only session; model metadata not captured.

| ID | Finding | Resolution and verification |
|---|---|---|
| M4-01 / P2 | Catalog phase lacked completed invoice tool context for dependent requests | Minimal TrackId/Name projection added; new context-transfer/catalog-lookup regression; reviewer verified fixed |
| M4-02 / P2 | Deterministic renderer discarded model-authored refund limitation | Explicit code-rendered refund limitation/support-contact offer; reviewer verified fixed |

Reviewer initial run182 passed; final184 passed, Ruff passed, no remaining blocking
findings in reviewed changes. No edits, additional skills, subagents or reference solution
used. This record is a findings/command summary, not a full raw reviewer transcript.

## Dependency limitation

Pinned environment uses langgraph-supervisor 0.0.31. Its official upstream is archived,
and required prebuilt create_react_agent APIs emit deprecation warnings (39 in final
suite). The tested LangGraph major version is constrained below2; retain required course
pattern now, track migration as maintenance work. Warnings are reported, not suppressed.
Full agent compatibility is established only for scripted tests until provider evaluation.

## Scope and next slice

The full conversation service composes the verification graph and constrained supervisor
phases; it is not a single global StateGraph and has no browser interface yet. This preserves
server-owned session/identity controls; later UI uses those handles rather than client IDs.
There is no preference store/extraction/load yet. Next milestone adds per-customer memory
with versioned extraction, union merge, empty-output preservation and focused evaluation.
