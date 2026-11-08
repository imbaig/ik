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
