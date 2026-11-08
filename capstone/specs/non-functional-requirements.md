# Non-functional requirements — review proposal

Prepared November 7, 2026. These proposed resolutions to HUM-001–009 await Imran's
review. Course-derived requirements are distinguished from project engineering targets.
No operational metric, test result or review closure is claimed.

| ID | Requirement | Origin | Acceptance evidence |
|---|---|---|---|
| NFR-01 | Each browser session/tab receives a unique server-managed thread ID; no shared conversation or verified identity | Course §5.8 / milestones 6 | Two simultaneous sessions, including different customers, show zero cross-session leakage |
| NFR-02 | One active customer per chat; reset/switch clears private context, pending interrupt and loaded preferences and issues a new thread ID | Proposed resolution HUM-004 | Verify A, switch, fail verification, then verify B; A's data is never available in B's thread |
| NFR-03 | All private queries enforce trusted customer ownership; bound SQL and numeric validation; no arbitrary SQL tool | Course | Direct tool security and injection tests |
| NFR-04 | Verification miss or ambiguity discloses no candidate account data; prompts retry or return to permitted catalog use | Course failure scenario + proposed CX | Invalid ID, ambiguous phone/email, correction and cancellation scenarios |
| NFR-05 | Model calls timeout within configured bounds; bounded retries and graph step budget prevent endless execution | Course remaining_steps + engineering target | Inject timeout/rate limit; verify bounded calls and honest failure, no fabricated facts |
| NFR-06 | Business logic has separate UI, orchestration, identity, SQL-tool, memory, configuration and telemetry modules | Course modularity + HUM-006 | Change memory extractor version and rerun focused/regression suites without changing SQL/UI contracts |
| NFR-07 | Memory output uses validated structured schema; only explicit positive preferences merge; empty or invalid extraction preserves existing memory | Course | Preference/question/negation/correction/empty-output evaluation corpus |
| NFR-08 | No secrets, raw identifiers or invoice content in operational telemetry; runtime files ignored in Git | Engineering target | Inspect sample logs and staged-file checks |
| NFR-09 | Python 3.12 setup, app.py entrypoint, requirements.txt and Dockerfile reproduce documented local run | Course | Clean install/start and Docker build/run evidence |
| NFR-10 | Pin Chinook source revision and SHA-256, validate required schema before use; upgrades are explicit and reversible | Proposed resolution HUM-008 | Compatible new snapshot passes contract suite; incompatible schema blocks startup with actionable error |
| NFR-11 | Capture low-cardinality operational/customer-outcome events and generate an on-demand aggregate report | Proposed resolution HUM-007 | Seeded synthetic event fixture produces expected report; no real customer data required |
| NFR-12 | Show pending state during model/tool work; prevent duplicate concurrent sends within a session; clear verification/retry/reset affordances | Engineering/UI target | Manual browser walkthrough and concurrency checks |

## Performance and availability boundaries

The capstone is a local demo, not an always-on production service. Record end-to-end
latency p50/p95, tool latency and failure rate during evaluation. No production uptime,
throughput or response-time SLA is asserted without measurement. Establish performance
budgets after baseline runs; timeouts/retry/step limits remain explicit configuration.
Report hardware, model, sample count and concurrency with performance results.

## Memory lifetime

Course FAQ permits in-memory preferences/checkpoints lost on restart, while the guide
uses broader persistence language. Baseline guarantee: preference recall across turns
and new verified conversations within the same process. Cross-restart SQLite persistence
is a proposed optional extension; it must not be represented as already implemented or
as an unambiguous course requirement. Reconcile HC-04 accordingly at baseline approval.

## Database changes

Do not download mutable upstream master automatically on every startup. Use a locally
cached, attributed SQL snapshot, load into in-memory SQLite as the course requires, then
enforce query-only access. Validate tables/columns and health queries before serving.
An intentional upgrade retains the prior snapshot, loads the candidate in a separate
validation run, runs all tool/ownership/JSON/order tests, and updates expected dataset
facts and provenance. No automatic migration or backward compatibility with arbitrary
schemas is promised. Customer-ID-based memory must be invalidated or namespaced by
dataset version when customer identities change; never silently remap old preferences.
