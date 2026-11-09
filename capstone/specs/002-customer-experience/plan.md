# Proposed plan — gated, no implementation authorization

Uses the repository Spec Kit specify→clarify→plan→tasks→analyze structure and templates,
manually authored for discovery. No automated Spec Kit command, third-party generator or
implementation command was run. Existing workflow review gates are not bypassed: this is a
candidate plan to inform review, not an approved implementation plan.

## Technical context and alternatives

Current Python3.12, locked Gradio5.50, server ConversationService and tool contracts remain
unchanged. No new package selection/installation. A human-selected direction can first be
expressed through deterministic readable text, theme tokens and explicit component IDs.
Rich card controls, sticky composition and arbitrary frontend DOM hooks are deferred.
Alternative React/TypeScript+Vite with a same-origin FastAPI adapter is assessed in
[feasibility](../../docs/design/issue-5/feasibility.md), not chosen or integrated.

## Canonical proposed architecture

[design.md](design.md) is the canonical proposed002 architecture and ADR-002-01. Imran's
[architecture feedback](https://github.com/imbaig/ik/pull/6#issuecomment-6730142179) makes
the **MVVM-inspired server-backed presentation boundary** binding, while detailed spec
acceptance, visual direction, framework migration and implementation permission remain open.
This is not full client-side MVVM and requires no MVVM library or API service now.

Current UIController still mixes Gradio update tuples with display/action logic, and current
agent runtime still formats observed records. Proposed extraction separates View adapter,
framework-neutral presentation controller/contracts/formatter and authoritative application
services; no such refactor is claimed implemented. Neutral application contracts prevent
core imports of Gradio/presentation. Structured facts are the machine contract, not markup.

Add an architecture-contract slice before I1/I2: fake-view actions without importing Gradio,
server ownership/reset/stale-delivery tests, deterministic formatting and sink-escaping tests.
Then stage the runtime renderer extraction and Gradio adapter conversion while retaining a
working app and SQL-truth/grounding checks. See design.md sections3–7 and AC17–21 for exact
contracts, module map, cancellation/progress limits, migration cost and verification plan.
The current callbacks remain in-process; a future transport adapter needs its own security,
serialization/session and integration validation, not agent/tool/DB policy rewrites.

## Constitution check and trust boundary

Specification precedes implementation; separate read-only design/spec review on frozen
commit; Imran approves. Every store fact still requires tool evidence; server owns customer
identity, bound SQL guards and session locks. Frontend receives display data, never authority.
No baseline001/approval change; no course-originals/secrets. Process-local memory and demo
verification caveats remain. Discovery-only gates are satisfied by reviewable artifacts;
implementation gates remain pending human decisions and actual validation.

## Proposed sequence

See [tasks](tasks.md) and [visual slice map](../../docs/design/issue-5/visuals/05-slices.svg).
First local rendering/visual feedback and D1–D4 decisions. Then approved bounded issue(s),
one active implementation PR initially, each with approved mockup and actual captures.
No framework migration or custom-component dependency follows from this document alone.

A presentation formatter may change deterministic grounding checks/eval render expectations;
update those carefully rather than weakening evidence rules. Run fixture comparisons across
all nine tools, full offline pytest/Ruff, UI E2E/keyboard/mobile and affected exact-revision
live conversation evidence before claiming application acceptance. This doc-only revision
needs structural/link/scope checks and independent review, not application live calls.

## Risks / mitigations

Unknown Gradio focus/mobile semantics → later authorized one-day spike; no internal DOM
hacks assumed. Exact amounts/counts lost in cards → field-level deterministic assertions.
Migration adds API session risk → preserve service authority, origin/CSRF/expiry tests before
adoption. Deadline buffer small → select small N/S changes and explicit deferrals; do not
weaken ownership/accessibility. Static artifacts unrendered → local inspection is a visible
gate, not a cloud pass. Recommendations remain proposals and all decisions remain pending.
