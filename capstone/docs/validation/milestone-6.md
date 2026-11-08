# Milestone 6 — Gradio UI and local telemetry

November 7, 2026. Implemented and independently reviewed; human acceptance pending.
Imran accepted M5 with “looks good. move to next milestone”. No live-provider quality,
clean-environment installation, Docker, commit or push is claimed.

## Implementation

Gradio 5.50 Blocks with messages Chatbot, Textbox, Send, New conversation, status,
verification cancellation and catalog-only controls. Generator callbacks immediately
show the user's message and working state; controls disable during execution. Per-view
locks reject concurrent sends. Histories and service handles are server-owned, never
accepted from Chatbot input. Each tab gets an opaque UUID in Gradio State and a separate
service UUID. Reset and the Chatbot Clear icon invalidate identity, history and pending
verification. Expired State closes the server session/checkpoint after one hour; saved
customer preferences retain the existing process-local lifetime.

Local metadata events use an allowlisted Pydantic schema, mode-0600 JSONL, no raw chat,
customer identifiers or tool rows. Request IDs correlate verification continuations with
one task. Mixed completion requires a final mixed success; catalog-only fallback cannot
inflate it. Tool duration is measured around invocation. Reports distinguish tasks from
turns; latency samples are individual send/resume calls. Reports contain no session UUID.
Seven-day cleanup is explicit, not scheduled. Single-process operation only.

## Verification

- Full pytest: **267 passed**, 59 deprecation warnings; no failures. Gradio 5 APIs and
  LangGraph prebuilt-agent APIs have upstream deprecation warnings; dependencies remain
  below their next incompatible major versions. Warnings were not suppressed.
- Ruff lint: all checks passed. Ruff formatting: 27 files already formatted.
- 22 new UI/telemetry tests cover immediate/busy outputs, duplicate sends, per-session
  isolation/reset/expiry, cancellation, bad input and sanitized failures; event allowlists,
  concurrency, retention/date windows/counts, actual service-to-sink task correlation and
  controlled-delay tool duration.
- Independent reviewer `/root/milestone6_review`: 80 focused tests passed and Ruff passed;
  all three findings resolved. See ../reviews/milestone-6-review.md.
- Author browser QA with tests/ui_harness.py: public Queen catalog returns three albums;
  unknown customer 99999 reveals no invoices; correcting to 1 resumes original request;
  separate tab initially empty/requires verification, customer 2 returns Germany invoices
  while tab 1 retains Brazil sample invoices; New conversation clears history and requires
  verification again; Cancel verification returns control; mixed catalog-only fallback
  explicitly cancels account work and returns only catalog; Clear resets server state.
  Immediate working state/disabled controls observed in browser. These are public Chinook
  sample records, not real customer data.
- Browser QA uses deterministic model/extractor/router doubles with real ConversationService,
  LangGraph graphs, tools and Chinook. It does not establish live model quality. No memory
  extraction quality or production concurrency/latency claim follows from this walkthrough.
- app.py starts directly from the repository (src path resolved), and without credentials
  fails with the explicit OPENAI_API_KEY-required configuration error before serving.

## Run

From capstone/ with the existing Python 3.12 environment:

```sh
uv sync --locked
# Add your key to ignored .env, using .env.example as a template.
uv run python app.py
# http://127.0.0.1:7860; localhost only, no Gradio share tunnel
```

Separate browser QA harness (clearly labeled; not the production application):

```sh
PYTHONPATH=src:tests uv run python tests/ui_harness.py
# http://127.0.0.1:7861
```

Report and explicit retention cleanup:

```sh
PYTHONPATH=src uv run python -m music_store.telemetry --start 2026-11-07 --end 2026-11-08
PYTHONPATH=src uv run python -m music_store.telemetry --cleanup
```

Default events: ignored .cache/telemetry/events.jsonl. Dates are inclusive UTC. Mixed tasks
started outside the date window are excluded from mixed-task totals. Model retry/timeout
attempt counts are not yet instrumented; contact deflection, revenue and satisfaction are
not measured. Memory quality still requires held-out labeled evaluation.

Evidence exported to the chat's outputs: milestone-6-tests.xml (every test),
milestone-6-test-output.txt, milestone-6-ui.png and milestone-6-browser-metrics.json.
The browser metrics file includes exploratory QA runs before/after instrumentation fixes,
including a fixed harness error; it is a command smoke test, not a clean benchmark.

Next: T08 live and held-out evaluation, error/security cases and independent evaluation
review, followed by T09 clean setup/Docker/demo and T10 approved GitHub publication.
