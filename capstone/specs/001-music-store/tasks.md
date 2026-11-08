# Tasks — proposed delivery sequence

All implementation tasks are pending. These dates are targets, not scheduled automation.

- [ ] T01 Baseline review: independent spec/design/traceability review; resolve findings;
  Imran signs off exact revision before implementation.
- [ ] T02 Nov 8–9: Python 3.12 environment; exact dependency compatibility; minimum
  requirements + lock; config; pinned official SQL revision/hash; ignored first-run cache;
  in-memory bootstrap, query-only health/query utilities and >=11 DB tests.
- [ ] T03 Nov 10–11: nine @tool functions per contracts, all found/empty/error JSON cases,
  numeric/LIKE/order/genre tests, ownership and SQL injection tests; >=17 tool tests
  (expand count to cover behavior), >=28 total; separate code/security reviewer.
- [ ] T04 Nov 12: structured identifier extractor, deterministic matching, SystemMessage
  plus executor ownership, interrupts/retry/cancel/reset; review human finding scenarios.
- [ ] T05 Nov 13: hand-built catalog ReAct, prebuilt invoice agent, supervisor invoice-first
  sequencing, bounded graph state, six grounding rules and verified identity propagation.
- [ ] T06 Nov 14: per-customer InMemoryStore; versioned extractor, skip empty, atomic union;
  load into catalog prompt; >=30 labeled extraction evaluations; reviewer verifies evidence.
- [ ] T07 Nov 15: Gradio Blocks, State UUID, immediate message/status, duplicate-send
  guard, interrupt/resume and two-session/switch walkthrough; redacted telemetry/report.
- [ ] T08 Nov 16–17: >=12 live cases plus SQL-truth evaluation; error injection, security
  tests and independent code/evaluation review; fix and reverify findings.
- [ ] T09 Nov 18–19: Docker build/run, clean setup, README/architecture/limits, sample
  usage, demo capture/rehearsal; editorial/source/secret check and human release review.
- [ ] T10 Nov 20: approved capstone-only commit/push and final submission. Preserve
  unrelated Wk-* work. Capture immutable revision and human acceptance evidence.

No test/model run or deadline completion is implied by these tasks. API credentials and
Docker/runtime availability will be checked during setup. AI-assistance course policy
remains an external administrative question, not a fabricated approval.
