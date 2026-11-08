# Milestone 5 — customer preference memory

November 7, 2026. Implemented, tested and independently reviewed; human acceptance
pending. M4 accepted. No live API/provider extraction evaluation, Gradio UI, commit or push.

## Implemented

- Pydantic UserProfile and versioned LLMPreferenceExtractor; configured provider,
  timeout/retry policy; model customer_id ignored for storage selection.
- LangGraph InMemoryStore with dataset-version/customer namespace and user_memory key;
  locked atomic union-only merge. Repeated/empty updates skip writes. No deletion or
  overwrite; process restart loses memory, as the course FAQ permits.
- Memory service separates structured extraction, evidence filtering, storage and load.
  Only verified user turns and the exact pending request upon successful verification
  are eligible. Anonymous/cancelled earlier chat is never adopted after later verification.
  Assistant/system/application messages and verification responses are excluded.
- Pure preference statements and recall requests route through verification. Saved tastes
  reload on another verified conversation in the same process; reset clears session and
  eligibility, not saved customer memory. Other customers cannot recall it.
- Catalog receives saved tastes as context only; tools remain the source of store facts.
- Failed/schema-invalid extraction preserves old memory and reports inability to update
  instead of claiming a save. Explicit positive literal evidence is required before merge.

## Actual evidence

**245 tests passed; Ruff and formatting checks passed.** Author and separate reviewer
verified the final suite. Total: prior184 +61 memory/evaluation cases, including42 labeled
candidate probes. JUnit: milestone-5-pytest.xml. LangGraph's known prebuilt-agent deprecation
warnings remain (42 in author run); no warning suppression or dependency migration claimed.

**42-case guardrail regression evaluation: precision1.0, recall1.0**, with adversarial
candidate inputs and exact labels. This tests deterministic evidence filtering, not the
LLM's ability to extract candidates. Report explicitly sets live_model_quality_validated
and target_met to false. SC-004 live extractor quality remains unvalidated. Corpus was
expanded in response to reviewer findings, so it is a tuned regression set, not held-out
quality evidence. Final live quality requires an independently held-out labeled set.

Commands from capstone/ after bootstrap:

```sh
uv run pytest tests/ -q
uv run ruff check src tests
uv run ruff format --check src tests
PYTHONPATH=src uv run python -m music_store.preference_eval --mode guardrail --output docs/validation/milestone-5-memory-guardrail.json
```

A later provider run uses --mode live and credentials; it is not run in this milestone.
Tests also verify adapter wiring with a fake client, model-ID spoofing, error preservation,
no-write empty/idempotent updates, concurrent union, namespace/version/restart isolation,
verified save/recall, catalog context with fresh tool lookup, and anonymous/cancelled history.

## Independent review and fixes

Reviewer: `/root/milestone5_review`, distinct read-only session; exact model not captured.
No additional skills, edits, subagents, published reference solution or live calls used.

| Finding | Severity | Resolution | Final reviewer disposition |
|---|---|---|---|
| M5-01 Anonymous/cancelled earlier history became account memory after verification | P2 | Separate bounded memory-eligible history; current pending request adopted only on successful verification; reset/cancel isolation regressions | Verified resolved |
| M5-02 Negative/quoted/hypothetical values accepted by positive-span filter | P2 | Quotation/provenance/negation boundaries expanded, including contracted/never negation; reviewer reproductions added to corpus | Verified resolved for reported reproductions |

Initial reviewer234 tests passed but findings remained. Interim243 passed; reviewer found
additional contracted-negation repros. Final245 passed, Ruff passed, guardrail42 cases
p/r1.0 with live/target false. No remaining actionable findings in reviewed scope. This is
handoff readiness, not Imran approval or a claim of general natural-language completeness.

## Limitations and next milestone

The evidence filter intentionally favors precision and can reject valid wording. It is
not a semantic proof. Live extraction, model calibration and held-out quality thresholds
remain required before final delivery. Memory is process-local, additive and English-
focused in the current prompts/filters. No long-term backend, deletion, user consent
management, semantic search or production authentication is claimed.

Next: Gradio browser UI, verification/status/reset UX and local telemetry/reporting,
then provider evaluation, deployment packaging and demo. Deadline remains November20.
