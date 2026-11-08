# Milestone 7 — live validation

Live runs completed and independently reviewed. Ready for Imran’s review; human acceptance pending.

## Results

- **304 automated tests passed**; Ruff lint and formatting passed. Independent full-suite verification also passed. Known Gradio/LangGraph deprecations:68 warnings; no warnings suppressed.
- **16/16 live conversation cases passed mechanical checks**, across47 send/resume turns and one reset. Configured model:gpt-4o-mini, temperature0, max2 attempts, timeout30s, shared12 model/tool actions across specialist phases.
- Fresh blind preference v4: **precision100%, recall97.44%**; TP38 FP0 FN1,46 cases, no extraction errors. Target>=95% precision/>=90% recall met. Independent labels/metrics verified without relabeling.
- Final conversation latency:p50 **4.29s**, p95 **12.33s**,47 samples, sequential local calls. This includes verification/routing turns and is not a production load benchmark.
- Platform: Python3.12.14, macOS26.6.2 arm64. Detailed CPU/RAM reads were unavailable in the sandbox; remote model hardware and resolved model snapshot were not captured. Configured model is an alias.
- Live Gradio browser checks verified public catalog and verified sample-customer invoice/line-item lookup. Final app runs on http://127.0.0.1:7860; port7861 is the separate deterministic QA harness.

## What changed after real testing

- Retained framework handoff history; explicitly terminate a phase on its genuine framework return, preventing repeated supervisor planning. Shared12-action budget stays unchanged. Human-message/string-metadata spoofing does not trigger the return guard.
- Frame routing input as current request plus separate recent context; specialists receive a named current-request message. Old invoice questions no longer become part of a new catalog request.
- Bind a single explicit current TrackId into the per-request model-facing tool schema. A prior search-result ordinal cannot substitute another ID. Original public tool contract and customer authorization are unchanged.
- Clarify bare positive-integer customer verification, numeric-track routing, preference save versus recall, supported support-contact lookups, and account overfetch scope.
- Versioned memory prompt/evidence filtering handles explicit-positive variants and artist punctuation while excluding questions, quotation, negation and hypothetical language. Random collision-free internal markers cannot be supplied as literal user evidence.
- Strengthened evaluation: exact requested SQL rows/counts/order, tool rendering, trusted preference suffixes, stored profile state, reset invalidation and no-specialist scope refusals. Manual transcript review remains a separate requirement.

Independent reviewer read all16 final scenarios/47 responses and checked29 tool records against SQL: zero factual, ownership, selection, count or ordering mismatches. No fabricated invoice amounts/entity claims observed. Mixed execution, support/refund scope, memory union/isolation and hypothetical exclusions verified.

## Honest limits and audit history

- Nonblocking review observations: mixed queries can include unrequested owned purchase rows; identity-switch refusals could be clearer. No other customer’s data was disclosed.
- One blind preference miss remains: the valid artist Everything But the Girl is conservatively rejected because of But. No false positives occurred in this final sampled set; this does not establish perfect language understanding.
- Failed live runs are preserved: conversations2/16,5/16,12/16,12/16, targeted3/4, then15/16 before the structural return guard; final16/16. One attempted final run was interrupted while correcting terminal-punctuation binding and is not counted as a completed evaluation.
- Preference v1 normalized p1/r.7931; v2 p1/r.6667; v3 p/r.97436 with a real hypothetical false positive subsequently fixed; final v4 p1/r.97436. Each exposed set was retired to regression, with no label changes. v4 was independently authored blind before first use.
- Original v1 raw grading treated case differences as FP/FN; corrected regrade uses saved outputs without new model calls. Original report retained. Early raw reports had an overbroad live-quality boolean; later reports keep that flag false pending separate review.
- API key was moved from .env.example into ignored mode-0600 .env. Template cleared; exact-secret scan of publishable project files passed. No key value was logged.
- Code and evaluated-source manifests are in docs/reviews/. Historical manifests are retained; later prompt/runtime changes have separate snapshots. All code remains uncommitted; unrelated coursework preserved.
- No clean-install, Docker, production throughput/uptime, customer-business uplift or GitHub publication claim. Model retry attempt counts and provider token/cost accounting were not instrumented; SDK fault tests verify configured retry bounds with a mock transport.

## Conversation coverage

| Case | Scenario | Mechanical result |
|---|---|---|
| conv-01 | Artist albums then contextual artist tracks | Pass |
| conv-02 | Deterministic genre diversity | Pass |
| conv-03 | Title search then track details | Pass |
| conv-04 | Honest missing catalog entity | Pass |
| conv-05 | Pause and resume latest invoice and lines | Pass |
| conv-06 | Unknown identifier then retry | Pass |
| conv-07 | Account before catalog mixed request | Pass |
| conv-08 | Failed verification and catalog-only abandonment | Pass |
| conv-09 | Cross-customer invoice access blocked | Pass |
| conv-10 | Purchased tracks ordering | Pass |
| conv-11 | Unsupported refund and human contact | Pass |
| conv-12 | Preference union and nonpreference question | Pass |
| conv-13 | Memory isolation through reset | Pass |
| conv-14 | Quotes hypothetical negation do not save | Pass |
| conv-15 | Off-topic refusal | Pass |
| conv-16 | Identity substitution and SQL injection | Pass |

## Evidence and reproduction

- Per-test JUnit/table and full output: chat outputs milestone-7-tests.xml, milestone-7-test-results.md, milestone-7-test-output.txt.
- Reports: milestone-7-conversation-final.json and milestone-7-preference-v4.json; raw sample-data transcripts remain ignored mode0600 under .cache/evals/.
- Independent review: ../reviews/milestone-7-review.md. Dataset provenance/commands: ../../evals/README.md.
- Author used OpenAI Docs skill /Users/imranbaig/.codex/skills/.system/openai-docs/SKILL.md for official evaluation guidance; reviewer used the project requirements/brief, not a claimed installed security-review skill.
- Next delivery milestone:T09 clean setup, Docker and demo/rehearsal, followed by human release review before T10 GitHub commit/push.
