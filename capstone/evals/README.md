# Evaluation protocol and provenance

These evaluations are local Python harnesses; no hosted evaluation service is required.
We use task-specific checks and independent test data, consistent with the
[OpenAI evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices).

## Data lifecycle

- preference-cases.json: original 42-case tuned guardrail regression. Synthetic candidates,
  not a live extraction benchmark.
- preference-heldout-v1.json: 46 cases independently authored by
  `/root/milestone7_eval_cases` without reading implementation/prompts/existing cases.
  First live results exposed case-sensitive grading plus real recall gaps. Original
  report and normalized regrade are preserved. After inspection, this is regression data.
- preference-heldout-v2.json: 44 fresh cases independently authored by
  `/root/milestone7_fresh_holdout`, who read only AGENTS, approved spec and hero use cases.
  First live run exposed additional explicit-positive/punctuation/clause misses. It is
  now regression data; no relabeling was performed.
- preference-heldout-v3.json: 46 additional blind cases from the same independent data
  author. First live run met numerical thresholds but had one hypothetical false positive
  and one missed musician favorite. Both were fixed with tests. This exposed set is now
  regression data. Do not present a tuned rerun as held-out evidence.
- preference-heldout-v4.json: 46 further blind cases, frozen before its first provider
  call. Final first-run result: TP38/FP0/FN1, precision1.0, recall0.97436; no extraction
  errors. This is the final held-out check for this milestone revision. Subsequent tuning
  against it would require another independent final check. It is agent-authored sample
  data, not a statistically representative customer-traffic sample.

Literal artist/genre labels are normalized with strip/casefold, matching storage. Preference
micro precision/recall and per-case exact-set results are separate; all-negative data cannot
pass the target. At least 30 cases and no extraction errors are required for target_met.
Failures are included in metrics. A target pass never implies perfect recognition.

Original dataset hashes and source snapshots are in docs/reviews/ manifests. No hidden
cherry-picking of passed cases or changed labels is permitted. Every completed run is saved,
including failed runs. Guardrail-only tests, SDK mock failures and live extraction are
labeled separately. Reviewer agents do not make provider calls or approve milestones.

## Conversation cases and grading

source/independent-conversation-recommendations-v1.json preserves 16 independent scenario
recommendations, plus separate fault/lifecycle recommendations. fixture-resolution-v1.json
records semantic enum mappings and SQL-verified public Chinook fixtures. The normalized
conversation-cases.json uses actual enums and adds required tools and exact lookup args.
These oracle arguments are grading data only; they are never supplied as trusted runtime
identity. Users must still verify through the normal interface.

Each case starts a fresh service/profile; steps share that service. Exact SQL projections
check requested rows, totals, stable ordering, truncation and ownership for the frozen
required lookups. Full-table membership checks cover additional returned facts. Reset checks
new handle/cleared identity/invalidated old handle. No-record refusals also require no
specialist dispatch. Memory cases check stored union/isolation, not just response wording.
Tool prose must match the deterministic renderer plus permitted application prefixes and
literal observed stored-preference suffix values.

Mechanical grading is insufficient for intent, arbitrary prose, completeness of every
subrequest, or production safety. A separate agent reads every actual transcript against
the original per-scenario SQL/behavior checklist. Semantic failures block readiness even
if a mechanical row is green. Keep raw transcripts under ignored .cache/evals/ (0600),
export only outcome summaries. Reports do not contain API keys or raw provider exceptions.

## Commands

From capstone/ using Python3.12, configured ignored .env, and the pinned Chinook cache:

```sh
PYTHONPATH=src uv run python -m music_store.preference_eval --mode live --cases evals/preference-heldout-v4.json --output docs/validation/milestone-7-preference-v4.json
PYTHONPATH=src uv run python -m music_store.conversation_eval --output docs/validation/milestone-7-conversation.json
uv run pytest -q
```

The live CLI exits nonzero for failed criteria or a missing key; missing-key reports say
zero attempted cases. Conversation reports keep quality validation/acceptance false until
separate review. A CLI mechanical pass is not human approval. Provider alias resolution,
production load, revenue uplift and general model reliability are not established here.
SDK MockTransport tests exercise retry/timeout bounds without calling the provider.
