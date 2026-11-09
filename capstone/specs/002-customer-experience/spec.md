# Proposed feature specification: customer experience

Feature002; branch `design/issue-5-customer-experience`; created2026-11-08.
**Status: DRAFT — revised for binding human findings; local visual review, direction/framework/spec decisions and human closure pending Imran.**
Input: issues [#5](https://github.com/imbaig/ik/issues/5) and [#4](https://github.com/imbaig/ik/issues/4).
This packet proposes future work; it does not authorize coding, migration or baseline changes.
Baseline001 and its approval snapshots remain authoritative and unchanged. Feature002 adds
presentation requirements without extending store capabilities or authentication claims.

## User scenarios and testing

| Priority / story | Why / independent test | Acceptance scenarios |
|---|---|---|
| P1 · HC-01 readable public discovery | First useful task without account gate; inspect known and empty artist/title/genre responses | Given catalog success, show observed labels/IDs/prices and counts/sample. Given empty/error, distinguish and offer supported refinement. AC-01/02 |
| P1 · HC-02 purchase understanding | Buyer can read exact latest invoice and detail after verification | Given anonymous buyer, pause before private lookup; on unambiguous verification resume pending task. Given owned invoice, show exact rows and total. Given foreign invoice, generic unavailable only. AC-03/04/05 |
| P2 · HC-03 combined task | No support/discovery handoff; test two-part request and catalog-only exit | Given mixed query, account before catalog, independently labeled outcomes. Given catalog-only choice, cancel account part and require verification for a new account task. AC-06 |
| P2 · HC-04 continuity with honest memory | Read saved values without implying editable/durable account settings | Given explicit positive taste, save observed union. Given new chat in same process, reverify before recall. Given restart/removal question, disclose process lifetime/no removal rather than promise deletion. AC-07 |
| P2 · HC-05 reach a human | Avoid dead end while retaining honest action boundaries | Given owned invoice, show only permitted returned rep details. Given refund/ticket request, explain no execution; no invented escalation/contact. AC-08 |

Visual trace: [artifact index](../../docs/design/issue-5/README.md), [journeys](../../docs/design/issue-5/visuals/01-journeys.svg),
[desktop](../../docs/design/issue-5/visuals/02-desktop.svg), [mobile](../../docs/design/issue-5/visuals/02-mobile.svg),
[state atlas](../../docs/design/issue-5/visuals/04-states.html), [connected walkthrough](../../docs/design/issue-5/visuals/walkthrough.html#a-S01) and [flow key](../../docs/design/issue-5/flow-guide.md). Representative A/B/C higher-fidelity
mockups are candidates, not approved references; see [directions](../../docs/design/issue-5/directions.md).

## Proposed functional requirements

- **CX-01**: Introduce public discovery and verified purchases with short starting guidance,
  sample-verification caveat and persistent access to New conversation. No checkout/playback.
- **CX-02**: Present all nine supported tool results with deterministic human labels, exact
  observed monetary strings/quantities/IDs, ordering, total/returned/sample metadata and failure
  states; tool JSON remains internal. Do not add currency, recomputed totals or model facts.
- **CX-03**: Show inline verification naming pending task with one labeled sample ID/email/phone
  input, error association, bounded retry, cancellation and mixed-only catalog continuation.
- **CX-04**: Derive verification display only from server outcomes; preserve all existing
  trusted identity, session ownership and SQL guards. Switch refusal stays explicit; an
  invoice ID is not a customer switch. Badge/client values never authorize tools.
- **CX-05**: Split mixed answers into account then catalog sections, retaining partial failures
  without representing unfinished work as complete. Catalog-only explicitly abandons account part.
- **CX-06**: Display saved/loaded preferences only with observed evidence and process lifetime.
  No removal/replacement/undo controls; New conversation is not preference deletion.
- **CX-07**: Display only observed permitted invoice-contact fields with clear inability to
  issue refunds, send messages or create tickets. Generic inaccessible invoice copy hides existence.
- **CX-08**: Provide welcome/busy/verifying/invalid/unknown/retry-limit/cancel/catalog-only/
  verified/error/empty/reset/preferences/switch/support states S01–S16. Avoid duplicate sends,
  preserve pending task safely and explain reset consequences before proposed confirmation.
- **CX-09**: Use the human-selected visual direction; support readable desktop and mobile,
  narrow reflow, keyboard, visible focus and assistive-technology announcements, targeting
  WCAG2.2AA with actual evidence before claims. Scope known limitations explicitly.
- **CX-10**: Keep untrusted content escaped, HTML sanitization enabled, no arbitrary tags/URLs
  or downloads, no account data in URLs/shared caches/telemetry, and no new credential surfaces.
- **CX-11**: Keep existing application runnable until any approved replacement passes parity,
  safety, deployment and visual acceptance. No new framework/tooling without human decision.
- **CX-12**: Each future implementation PR links approved frozen visuals to actual desktop/
  phone captures, deviations, exact-revision tests/review and affected live evidence. Imran
  approves design/spec and merging; passing checks or agent review does not do so.

- **CX-13**: The review prototype must begin with an empty first visit, distinct from public
  result and existing verified conversation. A/B/C share a navigable, state-ID-mapped public,
  account, mixed and recovery flow in wide/phone composition. Every active mock action leads
  to its identifiable fixed outcome; noninteractive fields/loading controls are explicitly
  explained outside the product screen. No account/provider connection is implied.
- **CX-14**: Product screen areas use realistic proposed customer questions/replies and pinned
  sample fixtures where available. Structural labels, state IDs, provenance and review notes
  remain outside; demo-verification and process-local-memory limits appear contextually.
  Binding human findings H5-01–03 remain pending human closure after actual local previews.

- **CX-15**: Honor binding H5-04 with the [canonical MVVM-inspired server-backed design](design.md):
  Gradio View adapter → framework-independent presentation controller/model → application
  conversation/verification services → agents/tools/storage/config, with explicit external LLM
  boundary. No Gradio objects in core; no API/MVVM library or client identity authority required.
- **CX-16**: Use neutral typed actions/results and presentation view-state contracts; move
  customer-facing record rendering out of agent runtime into deterministic formatting without
  moving/weakening grounding, ownership, SQL or execution-budget checks. Preserve exact values,
  counts/truncation/order, safe notices and sink escaping; markup is not the sole machine contract.
- **CX-17**: Make presentation driveable through a fake View without Gradio. Application owns
  identity, session/pending lifecycle and guards; view state is a read-only projection. Specify
  generation/request association for stale delivery, reset isolation, verification cancellation
  distinct from provider cancellation, and only actually supported busy/final/progress semantics.

## Edge cases and success criteria

Required walkthrough: all HC-01–05 plus S01–S16, malicious markup in catalog fields, long
labels, missing currency/contact fields, exact decimal strings, model/provider failure,
partial mixed completion, foreign invoice, two tabs/customers, expiry, reset while waiting,
repeat send, input method composition, virtual keyboard and narrow/zoomed layout.

Success is defined by [acceptance.md](acceptance.md): no unauthorized facts in defined tests,
all returned fields faithfully represented, supported recovery paths usable, and visual/
accessibility evidence attached to the selected revision. Discovery does not establish actual
customer task completion, conformance, measured revenue or production authentication.

## Dependencies and unresolved decisions

D1 visual direction, D2 framework/spike, D3 spec and D4 slice scope/schedule remain open in
[clarifications.md](clarifications.md). No baseline001 edit, production auth, preference
mutation, durable storage, checkout, playback, ticket creation or provider cancellation.
Approved-spec references:001 FR-003–010, contracts, HC scenarios; source/rendering code was
inspected to distinguish current facts from proposals. [Traceability](traceability.md).

## Binding human review revision

[H5-01–03](../../docs/design/issue-5/human-findings.md) originate with Imran and are
mandatory. The initial agent report did not establish human acceptance. Added CX13/14 and
AC13–16 require distinguishable entry/results, connected actions and realistic copy; exact
new review SHA and unchanged reviewer report/dispositions are recorded in existing PR6.
Local coordinator must render actual desktop/mobile preview before presenting completion.
No human closure/waiver or application implementation follows from this revision.

## Binding architecture amendment H5-04

Full [human comment](https://github.com/imbaig/ik/pull/6#issuecomment-6730142179) is the
source of CX15–17 /AC17–21 and [design.md](design.md). The separation choice is a requirement;
this revised design/spec still needs exact-revision independent review and Imran acceptance.
Current implementation and reviewed walkthroughs are unchanged. No framework migration,
production authentication, new cancellation/streaming capability or implementation claimed.
