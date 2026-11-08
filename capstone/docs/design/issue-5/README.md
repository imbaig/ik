# Issue 5 — customer experience discovery

**Draft for human review. Design discovery only; no UI implementation or approval.**
Parent [#4](https://github.com/imbaig/ik/issues/4), discovery [#5](https://github.com/imbaig/ik/issues/5).
Base: current main `8138e7d1c02e759e758c328ccf8b84c25413e4bc`. Issue 2 is complete;
its implementation is not reopened. Author: Codex `/root`. Date: 2026-11-08.
Duplicate check: GitHub search of all open repository PRs returned none before branch creation.
Branch: `design/issue-5-customer-experience`; baseline001, code, dependencies and coursework unchanged.

## Compare the artifacts

Download this directory and open [visual index](visuals/index.html) locally; no server,
network, installation, JavaScript, external fonts or application credentials are required.
GitHub displays SVG files directly; download HTML to inspect it in a browser.

| Stage | Visual review input | Accompanying decisions/evidence |
|---|---|---|
| 1: discover | [HC-01–05 journey board](visuals/01-journeys.svg) | [Inventory and journeys](discovery.md) |
| 2: arrange | [Desktop wireframes](visuals/02-desktop.svg), [mobile wireframes](visuals/02-mobile.svg) | [State matrix](states-and-responses.md#critical-state-coverage) |
| 3: compare | [A · Record Room](visuals/direction-a.html), [B · Clear Conversation](visuals/direction-b.html), [C · Reference Desk](visuals/direction-c.html) | Each includes discovery/account desktop and explicit mobile compositions; [tradeoffs](directions.md) |
| 4: recover | [Critical-state atlas](visuals/04-states.html) | [Responses and exact-fixture rules](states-and-responses.md) |
| 5: specify | [Gated slice map](visuals/05-slices.svg) | [Draft spec](../../../specs/002-customer-experience/spec.md), [acceptance](../../../specs/002-customer-experience/acceptance.md), [traceability](../../../specs/002-customer-experience/traceability.md) |
| Evaluate feasibility | [Framework/trust boundary diagram](visuals/06-framework.svg) | [Per-interaction matrix and recommendation](feasibility.md) |
| Inspect sources | [Source/use ledger](sources.md), [source hashes](source-manifest.json), [static checks](static-validation.md) | Pinned UI UX Pro Max, Gradio5.50 source evidence, Nielsen/HAX/WCAG |
| Validate locally | [Local inspection checklist](local-inspection.md) | Rendering, mobile/keyboard/assistive tech all pending |

All screens are **proposed static mockups**. Named music, invoice IDs, dates, totals and
contact details in them are **synthetic illustration, not actual store records**. Abstract
shapes are layout marks, not album artwork. No checkout, playback, refund, ticket or account
change is offered. Runtime responses must be generated from observed tool facts only.

## Recommendation for discussion

Prefer retaining Gradio5.50 initially with readable deterministic responses, theme tokens,
responsive Blocks and inline verification. Direction B is the least costly candidate;
A offers stronger editorial identity; C has more custom interaction risk. This is a
recommendation, not a selection. A React/TypeScript frontend with Vite and a same-origin
FastAPI adapter is a viable alternative if a time-boxed Gradio accessibility/mobile spike
fails agreed checks; migration is not authorized. See feasibility.md for explicit costs.

## Decisions reserved for Imran

| Decision | Options | Status |
|---|---|---|
| D1 visual direction | A / B / C / requested refinement | Pending |
| D2 frontend | Retain Gradio / approve alternative spike / other | Pending |
| D3 proposed 002 packet | Accept / amend / reject at exact reviewed revision | Pending |
| D4 scope and schedule | Approve bounded slices; defer risky custom interactions | Pending |

No proposed slice is agent-ready for UI coding. Discovery artifacts can be reviewed while
rendered evidence is pending; design/spec acceptance requires explicit human decisions.
Human findings and human-adopted agent findings remain binding and visible. Independent
review reports and separate author dispositions will be published in the draft PR against
an exact commit; they do not change approval snapshots or approve merging.

## Evidence limits

Cloud task has no usable browser/computer-use for this work: **no rendered visual QA,
screenshots, mobile testing or accessibility testing claimed**. Runtime status advertised
a desktop capability with unknown readiness; that metadata is not an observed test. Per
coordination, local reviewers will render/inspect artifacts. Only source/static structural
checks can be performed here. Direct runtime retrieval of standards sites was blocked;
primary-source text was available through coordinated parent/web-tool retrieval. No
application credentials accessed, no live provider calls, no global installation or
third-party script execution. Live evaluation is not run or required for this documentation
revision; later changes to rendering/orchestration require affected exact-revision checks.
