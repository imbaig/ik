# Issue 5 — customer experience discovery

**Draft for human review. Design discovery only; no UI implementation or approval.**
Parent [#4](https://github.com/imbaig/ik/issues/4), discovery [#5](https://github.com/imbaig/ik/issues/5).
Base: current main `8138e7d1c02e759e758c328ccf8b84c25413e4bc`. Issue 2 is complete;
its implementation is not reopened. Author: Codex `/root`. Date: 2026-11-08.
Duplicate check: GitHub search of all open repository PRs returned none before branch creation.
Branch: `design/issue-5-customer-experience`; baseline001, code, dependencies and coursework unchanged.

## Start here — no repository download needed

1. Open [the complete customer walkthrough](visuals/walkthrough.html#a-S01), choose
   **Download raw file** on GitHub, save the single HTML file and open it locally. It includes
   A/B/C, all linked states and wide/phone composition controls. No server, install or network.
2. Begin at the **empty first visit**. Choose the AC/DC question for public discovery;
   restart and choose the invoice question to follow verification → loading → owned result.
3. Use the flow map for the already-verified shortcut and recovery branches. See the
   [plain-language guide](flow-guide.md) for the route/state key.
4. The local coordinator will render actual desktop/mobile previews before this revision
   is presented as complete. [Human findings H5-01–03](human-findings.md) remain binding;
   no human closure or approval is claimed.

GitHub displays [desktop](visuals/02-desktop.svg), [mobile](visuals/02-mobile.svg) and
[flow-map](visuals/07-flow-map.svg) SVGs directly. HTML source view is not a rendered
preview. The one-file walkthrough is the primary portable entrypoint; the older visual
index and direction files are also retained for directory-based/local review.

| Stage | Visual review input | Accompanying evidence |
|---|---|---|
| Discover | [HC01–05 journey board](visuals/01-journeys.svg) | [Inventory/journeys](discovery.md) |
| Follow actions | [One-file A/B/C walkthrough](visuals/walkthrough.html#a-S01), [flow map](visuals/07-flow-map.svg) | [Flow guide](flow-guide.md), [route IDs](flow-states.json) |
| Arrange | [Desktop](visuals/02-desktop.svg), [mobile](visuals/02-mobile.svg) wireframes | Empty entry is separate from question/loading/result |
| Compare | [A · Record Room](visuals/direction-a.html#a-S01), [B · Clear Conversation](visuals/direction-b.html#b-S01), [C · Reference Desk](visuals/direction-c.html#c-S01) | Each has the same unverified/verified/recovery routes and wide/phone controls |
| Recover | [All-state atlas](visuals/04-states.html) | [State/copy matrix](states-and-responses.md) |
| Architecture | [Canonical proposed design and ADR](../../../specs/002-customer-experience/design.md) | [Current vs proposed, contracts, server authority and migration tests](../../../specs/002-customer-experience/design.md#1-current-implementation-versus-proposed-extraction); binding H5-04, acceptance pending |
| Specify | [Gated slice map](visuals/05-slices.svg) | [Draft002](../../../specs/002-customer-experience/spec.md), [acceptance](../../../specs/002-customer-experience/acceptance.md), [traceability](../../../specs/002-customer-experience/traceability.md) |
| Evaluate feasibility | [Framework boundary](visuals/06-framework.svg) | [Gradio/alternative matrix](feasibility.md) |
| Inspect sources | [Ledger](sources.md), [source hashes](source-manifest.json), [sample fixture](sample-fixtures.json) | [Static evidence](static-validation.md) |
| Recheck binding findings | [Human findings/dispositions](human-findings.md) | [Local inspection handoff](local-inspection.md) |

Product areas contain proposed customer-facing copy. All review labels/state IDs/provenance
stay outside them. Read-only sample fields and noninteractive loading controls are explained
in review notes; active actions lead to identifiable fixed mock states. Data now uses the
existing checksum-verified public Chinook fixture, rather than the first revision's synthetic
records; exact amounts/counts and extraction provenance are in sample-fixtures.json. No live
store/account/provider connection, application change, new production feature or human approval.

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

## Architecture amendment — H5-04

Imran's [full architecture requirement](https://github.com/imbaig/ik/pull/6#issuecomment-6730142179)
requires MVVM-inspired server-backed separation. Read the canonical [proposed design.md](../../../specs/002-customer-experience/design.md)
for subsystem/dependency diagram, current/proposed responsibilities, action/result/view-state
contracts, server session authority, exact facts/escaping, cancellation/reset limits, ADR and
migration/testing cost. No app extraction, new API/MVVM library, frontend migration or detailed
spec acceptance is claimed. Reviewed walkthroughs and their visual bytes are unchanged.
H5-01–03 closure remains separate; positive walkthrough feedback is not inferred closure.
