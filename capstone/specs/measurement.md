# Business and operational measurement — proposed

Purpose: show whether discovery/account self-service works and expose regressions.
Metrics are project targets, not a course mandate or proven commercial impact.

| Metric | Definition | Limitation |
|---|---|---|
| Discovery success | Sessions with catalog results / sessions with catalog requests | Results returned is only a proxy for finding useful music |
| Invoice self-service outcome | Verified invoice requests yielding grounded success or honest empty / verified invoice requests | Cannot establish avoided support contacts without follow-up data |
| Verification failure rate | Failed verification attempts / all verification attempts | Track technical failures separately from no-match outcomes |
| Mixed-query completion | Both requested branches complete / mixed requests | Record partial outcomes without inflating success |
| Memory extraction quality | Precision/recall on labeled held-out preference cases | Offline metric; production intent cannot be inferred from capture count |
| Tool/model reliability | Errors, timeouts, retries per attempted operation | Separate infrastructure failures from valid no-results |
| Customer effort | Turns to complete a labeled task; optional explicit helpfulness response | Never treat an abandoned session as a successful task |
| Latency | p50/p95 request time and sample count | Report configuration and test load |

Proposed local event schema: UTC timestamp, random session correlation token, request ID,
event type, branch, outcome, elapsed_ms, prompt/config version, dataset version and tool
name. No email, phone, customer ID, invoice rows or raw messages. Correlation tokens are
pseudonymous, not an anonymity guarantee. Default raw-event retention: seven days, with
on-demand cleanup; aggregate reports contain no correlation token.

Use a local append-only JSONL sink and an on-demand reporting command; report windows
accept a date range. For the capstone, review reports at each milestone and after evals.
A production deployment could run a daily/weekly report externally; no scheduler or
notification automation is being enabled. Revenue uplift, retention and contact-deflection
claims require a real pilot and appropriate measurement, not this demo's event counts.
