# Proposed implementation slices — not agent-ready

No application tasks are authorized by issue5. These are candidate follow-up issues, not
created/assigned issues and not a continuous queue. One active implementation PR initially.
[Visual slice map](../../docs/design/issue-5/visuals/05-slices.svg) shows ordering and gates.

| Slice | Scope / bounded deliverable | Depends on | Acceptance / evidence | Explicit exclusions |
|---|---|---|---|---|
| G0 human design gate | Local artifact rendering, findings/dispositions, D1–D4 decisions at frozen SHA | This discovery and independent review | Selected visuals/framework/spec explicitly accepted by Imran | No coding |
| P0 optional feasibility spike | <=one engineer-day, deterministic fixture UI for selected direction; source/API/keyboard/mobile proof | Explicit separate authorization | AC09–11 sample evidence; failed checks returned for decision | No provider, migration or persistent deployment |
| A0 presentation contract/extraction | Neutral actions/results, ViewState/controller and fake-view harness; stage formatter extraction from runtime without weakened grounding | G0 plus explicit architecture/refactor authorization | AC17–21; import/dependency checks, nine-tool formatting/escaping and server/reset/stale-delivery regressions | No MVVM package, API, new provider cancellation or frontend migration |
| I1 readable facts | Deterministic safe presentation for nine tool envelopes; exact amounts/counts/ordering, unavailable fallback | G0 and any P0 decision | AC02/04/08; fixture→render tests and affected exact-SHA live checks, approved vs actual desktop/phone captures | No tool/auth/model changes; no invented currency |
| I2 responsive shell + recovery | Selected theme/layout, welcome/input/status/inline verification and reset consequences | G0, proven N/S approach; may follow I1 | AC01/03/05/09/10; state walkthrough, isolation and keyboard/phone captures | No rich in-chat controls, modal/sticky hacks or new authentication |
| I3 continuity and mixed/support polish | Plain preference lifetime, split outcomes, scoped contacts/copy | I1/I2 | AC06/07/08, all HC01–05 walkthrough and relevant live re-eval | No preference removal or support execution |
| V1 release evidence | Full offline/e2e, all relevant A/AA review, approved-vs-actual visual comparison, independent review and human acceptance | Approved implementation slices | AC11/12, exact-SHA artifacts, Imran acceptance | No automatic merge or conformance claim without evidence |

React migration is not a slice implicitly authorized here. If selected later it needs its own
API/session/deployment specification, threat review and deadline decision. Do not replace
current app until parity and acceptance pass. Each PR freezes SHA/visuals, records reviewer
identity/findings/dispositions/rechecks and preserves binding human findings.

Architecture dependency: [canonical design/ADR](design.md), human H5-04. A0 is a proposed
bounded prerequisite/overlapping extraction task for I1/I2, not newly authorized coding.
Reviewed walkthroughs remain unchanged; implementation captures must still explain deviations.
