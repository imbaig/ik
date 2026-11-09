# Binding human review findings — PR6 revision

Source: Imran, relayed in the user message following the initial PR6 review. Initial reviewed
revision: `157a8b42ffb83e7933f7653dd3ead82692b49888`. These are binding human findings,
not optional polish. The initial agent report remains preserved in PR6; it does not override
Imran's findings. No human closure, waiver, design/spec approval or implementation permission.

| ID | Human finding / impact | Author disposition and changed evidence | Status |
|---|---|---|---|
| H5-01 | Initial landing and result in 02-desktop.svg could not be distinguished; first-time experience could not be evaluated | Accepted. S01 is an empty first visit with no messages/results; S02D is loading; S17 is the public result. Desktop/mobile SVGs and A/B/C show the same questions and state distinction | Fixed in authored revision; independent re-review, local rendering and Imran closure pending |
| H5-02 | Flow into direction-a.html was unclear; entry, actions and outcomes were not connected | Accepted. One-file walkthrough carries A/B/C, all route/scene IDs, public/account/mixed paths, verified shortcut, invalid/retry, cancel/catalog-only, errors/empty and context-preserving reset/switch branches. All active product actions navigate fixed mock states | Fixed in authored revision; independent re-review, local rendering and Imran closure pending |
| H5-03 | Filler/structural labels prevented judgment in content context | Accepted. Realistic questions and replies use pinned public Chinook fixtures; product copy replaces labels such as “Result area” and “Find your next question”. Review annotations/provenance stay outside product boundaries; demo verification and preference lifetime appear contextually | Fixed in authored revision; independent re-review, local rendering and Imran closure pending |

Severity: all three block human design review until understandable rendered evidence is
available. Source=human; mandatory=true; human-adopted=null (human-origin, no adoption
inferred); human closure/waiver=null. Author: Codex `/root`. Exact resolution/review SHA and
separate read-only re-review report/dispositions will be recorded in the existing PR6.

## Required local recheck and human closure

1. Open the single-file walkthrough at S01 in wide and phone composition. Confirm it is
   visibly empty, with questions available but no previous message, result or verified account.
2. Follow public question → loading → two actual AC/DC albums. Start again and follow
   invoice question → sample verification → loading → owned invoice382 /8.91 /nine details.
3. Repeat in A/B/C; inspect all alternative paths and the exact origin preserved by reset's
   Keep action. Busy controls are noninteractive and explicitly annotated outside screens.
4. Confirm customer copy has replaced structural filler inside product areas; review notes,
   data provenance and simulated-outcome labels remain outside. Check wrapping/clipping.
5. Publish actual desktop/mobile preview/captures and findings against the new exact SHA.
   Only Imran can close/waive these human findings. Agent/static verification is not closure.

## Independent re-review repair — R5-HR1-01

Reviewer `/root/issue5_human_rereview` requested changes on
`a4b4d77821a36101df220bd91a517f7bf3da7c97`: the new SVG flow map connected recovery
alternatives sequentially and linked generic reset instead of the switch-origin reset.
Author accepted the medium finding. Replaced those arrows with actual separate routes:
S04→S03; S03M Verify→S02M, Cancel→S07, catalog-only→S08; switch S15→S12-S15 with
Keep→S15 and confirm→S01R. Empty/error alternatives are independent cards without arrows.
Every drawn edge is checked against product actions or explicit loading continuations in
flow-states.json. This is semantic source evidence, not rendered usability verification.

The unchanged first re-review report is preserved in PR6; final exact-SHA recheck/disposition
is recorded there separately. R5-HR1-01: accepted, fixed-pending-verification; human-adopted
and mandatory flags=null unless Imran adopts it, human closure=null. Human-origin H5-01–03
remain mandatory and pending local rendered preview and Imran closure regardless of recheck.

## H5-04 — binding MVVM-inspired presentation architecture

Source: [Imran's full comment6730142179](https://github.com/imbaig/ik/pull/6#issuecomment-6730142179),
read in full by the author. Source=human, mandatory=true; human-adopted=null (human-origin);
human closure/waiver=null. The comment positively reviews the walkthrough and authorizes
separation as a design requirement; it does not select visual direction/migration or accept
an unseen revised spec. No previous human finding is silently closed from that feedback.

Author response: accepted. Added canonical002 design.md and ADR with current/proposed
boundaries, neutral actions/results, projected ViewState, dependency/fact diagram, deterministic
formatter extraction, exact metadata/encoding rules and retained server authority. Added
AC17–21 fake-view/import, formatter/escaping, ownership/reset/stale-delivery and cancellation/
progress acceptance. Updated plan/spec/traceability/index and added a pointer in historical
non-snapshot specs/design.md. Current app, dependencies, approved001/snapshots and reviewed
walkthroughs unchanged. Status: authored/fixed-pending-independent-verification and Imran
acceptance; exact final SHA/report/dispositions recorded in PR6. Proposed tests are not run.

## H5-05 — app-specific layered architecture; no Microsoft MVVM framework

Source: [Imran clarification6734378270](https://github.com/imbaig/ik/pull/6#issuecomment-6734378270). Source=human; mandatory=true; human closure/waiver=null. Supersedes strict interpretations of H5-04, without removing its separation requirements.

Author: local coordinating Codex /root, taking over this documentation repair after the cloud message remained delivery-unconfirmed. Accepted: describe the design and ADR as lightweight layered server-backed architecture; retain replaceable UI adapter, neutral contracts, pure formatter and server-owned identity/workflow. No Microsoft MVVM toolkit, rigid ViewModel hierarchy, API service or frontend migration required. Canonical design, plan, spec, clarifications and navigation wording updated; current-vs-proposed distinction retained. Independent verification and Imran acceptance remain pending; no app code, walkthrough, dependency or baseline001 changes.
