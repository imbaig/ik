# Frontend feasibility and recommendation

**Design assessment, not a framework proof of concept.** Installed locked dependency is
Gradio **5.50.0** (`uv.lock`). API claims below are based on inspected installed source;
[hashes and inspection limits](sources.md#gradio-evidence) identify that evidence. Current
upstream documentation is not proof of version5.50 behavior. Browser and assistive-tech
behavior remains unverified. Visual [boundary comparison](visuals/06-framework.svg).

Categories: **N** native API exists in inspected version; **S** supported customization
surface (still requires regression testing); **F** custom component / fragile internal DOM
workaround; **U** unsupported in current app or unverified. These are feasibility estimates,
not claims of implemented behavior. Retain sanitization; never insert model-supplied HTML.

## Per-interaction matrix

| Proposed interaction / artifact | Gradio5.50 route | Classification and evidence | Alternative: React/TypeScript + Vite, FastAPI adapter | Gate / effort risk |
|---|---|---|---|---|
| Welcome prompt text, S01 | Markdown and Buttons feeding composer; no automatic submit needed | N: existing components; prompt chips are composed Buttons, not a special chip API | Native HTML buttons and controlled input | Low; first prompt must remain editable |
| Editorial brand/spacing, A/B/C | Blocks theme tokens, CSS on explicit elem_id/elem_classes | S: Blocks(theme,css) and component IDs exist; internal generated selectors F | CSS variables and semantic DOM owned by app | B low, A medium, C medium; visual spike |
| Wide/narrow columns, W-D/M | Row/Column with width constraints, scoped media queries | N/S: Row flexible wrapping and Column min_width APIs; actual phone/keyboard behavior U | CSS grid/flex with project-owned breakpoints | Test320/390/768/1440 before committing design |
| Readable catalog / invoices | Deterministic plain text first; escaped allowlisted Markdown if approved | N for Chatbot Markdown flag; S for controlled formatting; rich clickable cards F | Semantic lists, definition lists, tables with escaped React text | Renderer is application work; no free-form HTML; maintain all tool facts |
| Exact totals/sample labels | Server-authored immutable projection of observed envelope | U in current app as readable UI; framework-independent formatter proposed | Same projection, typed response DTO | No model rounding, recomputation or implicit currency |
| Inline verification S03 | Existing Textbox + visible Buttons; show pending task via safe text | N: visibility updates/events already used | HTML form with explicit error association | Label/focus/error announcements U until tested |
| Retry/cancel/catalog-only S04–08 | Existing event handlers and server verification service | N events; scope catalog-only control to mixed pending task | API commands must forward only allowlisted actions | Preserve retry bounds; cancellation of verification is not provider cancellation |
| Verified indicator S09 | Text/Markdown updated from trusted service outcome | N display, U new view metadata contract | Server-derived boolean/status, never trust client badge | Do not send raw customer ID as authorization input |
| Loading / repeated send S02 | Existing generator yields + interactive flags + per-view lock | N; queue concurrency and trigger_mode APIs exist | Disable duplicate submit; server idempotency/serialization needed | No fake progress percentage or unsupported token-stream claim |
| Incremental progress | Generator phase/status updates | N API; token streaming U in current service | Fetch stream/SSE via FastAPI StreamingResponse possible, not built | Keep facts final/validated; disconnect/backpressure tests needed |
| Reset / expiry S12 | Existing State TTL/delete_callback + service.reset | N reset; proposed inline confirmation S with visibility updates | Opaque server session cookie, rotate/revoke on reset/expiry | Back/reload/tabs must not restore private state; expired UI shows fresh start |
| Invoice selection follow-up | Plain text “ask about invoice…” first; outside-chat button can submit trusted selected row ID | N external Button events; in-message rich action custom component F | Button sends invoice ID only, server always checks ownership | Query tampering/ID enumeration tests required regardless of framework |
| Preferences S13/14 | Text outcomes and lifetime note | N display; removal/edit U and outside scope | Same limitation unless separately approved backend change | No fake delete/undo toggle; New conversation does not clear profile |
| Support contact S16 | Safe text from permitted rep fields, no auto-send | N text; controlled external mail link S if separately tested | Escaped text, allowlisted URL scheme if links approved | Default text only; no ticket/refund action |
| Keyboard focus / live status | Basic native inputs/buttons; project-level focus/status behavior may need custom code | N controls, U screen-reader announcements/focus order; DOM query focus hacks F | Semantic labels/status region and explicit focus refs | Both need manual VoiceOver/NVDA, keyboard and zoom tests |
| Sticky composer, modal, chat tabs, rich card actions | Avoid for first slice; CSS pinning/custom JS can fight internal DOM and virtual keyboard | F/U; no guarantee on mobile/safe area or modal focus trap | More DOM control, still app-owned accessibility responsibility | Defer unless proven necessary; no custom component dependency now |

## Security, session and deployment tradeoffs

| Concern | Retain Gradio5.50 | Supported frontend alternative (not adopted) |
|---|---|---|
| Service boundary | Existing UIController→ConversationService calls stay in-process | Add typed create/send/action/reset/close API; keep domain tools private; no public tool endpoint |
| Trusted identity | Existing server-owned verification and per-tab State mapping stay authoritative; Gradio State is not production authentication | Browser may hold opaque session capability only, never customer identity authority; bind capability to server session; SameSite/HttpOnly/Secure cookie and CSRF/origin checks designed/tested before use |
| Public demo caveat | Sample ID/email/phone matching remains demo verification; do not label “secure sign-in” | Same caveat; React does not add authentication; production access control would need separate scope |
| Isolation/lifecycle | Preserve one process, per-view locks, reset invalidation, TTL close; test direct API requests and simultaneous tabs | Implement expiry, reset revocation, cross-tab strategy, per-session serialization, no shared-user singleton state; do not persist private transcript in URL/localStorage/service worker |
| Untrusted content | Escape field strings before Markdown; sanitize_html=True, allow_tags=False, downloads off | React text escaping; no dangerouslySetInnerHTML; server content/type/size validation; explicit CSP and no arbitrary URL schemes |
| Caching/logs | No private response caching; allowlisted telemetry only | Cache-Control:no-store on private routes; no shared CDN cache; redact payload logs/traces; verify proxy headers |
| Streaming | Existing queued generator delivers status then final results; no service token stream | FastAPI supports generator response bodies; add client parser, ordering, disconnect/timeout and duplicate replay handling. Never stream unverified facts |
| Docker/runtime | Keep Python single-image/single-worker design, existing process-local memory | Node build stage→static assets served same-origin by Python/proxy; no need for a second live Node server for this SPA. New image build/CSP/static routing tests |
| Testing | Existing service/offline suites plus browser fixtures, visual comparison, accessibility/manual phone evidence | Same service suites plus API schema/CSRF/cookie/session/stream tests, frontend component+E2E+visual tests and build auditing |
| Maintenance | Less new infrastructure; custom DOM CSS/JS is upgrade-sensitive; stay on locked5.50 pending deliberate upgrade | Own API lifecycle and frontend build chain; more UI control, larger patch/dependency surface |

## Effort and deadline

Author estimates for one engineer familiar with this code, **not measured commitments**:

| Option | Build and design translation | Validation / safety work | Total indicative effort | Deadline implication |
|---|---|---|---|---|
| Gradio B, plain readable responses and scoped theme | 3–4 working days | 2–3 days for five journeys, phone, accessibility and relevant evals | 5–7 days plus review fixes | More plausible before November20; requires prompt human decisions |
| Gradio A, rail and richer cards | 4–6 days | 3–4 days including layout/customization regressions | 7–10 days plus review fixes | Little buffer; reduce custom card actions |
| Gradio C with custom workspace/sticky interactions | 5–8 days | 3–5 days | 8–13 days plus review fixes | High deadline risk; do not assume custom component is quick |
| React/Vite + FastAPI adapter | 6–9 days for UI and API/session adapter | 4–6 days for security, deployment and parity | 10–15 days plus review fixes | Likely consumes/exceeds remaining calendar window; would require scope/date decision |

The November20 deadline is a project constraint, not evidence these estimates are achievable.
Do not reduce ownership/accessibility checks to meet it. No migrations or package versions
are installed/selected in this PR. Alternative versions/support compatibility need pinning
and reinspection if approved; React official guidance documents Vite but recommends considering
frameworks for broader needs. This small single-page prototype does not need SSR or new routing.

## Recommendation and falsifiable selection gate

Retain Gradio provisionally, favor direction B for the first approved slice. Before UI
implementation approval, reserve a **maximum one engineer-day** later feasibility spike
(no provider/credentials) against approved mockups, using deterministic service fixtures.
Test narrow reflow, keyboard/VoiceOver, verification recovery and sanitized readable responses.
If essential acceptance checks cannot be achieved through N/S surfaces without internal DOM
hacks, present the failed checks and a React adapter proposal to Imran. Do not silently migrate.
Direction, spike authorization, frontend and spec are all pending human decisions now.
