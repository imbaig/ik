# Local coordination handoff — all rendered checks pending

This cloud revision contains authored portable artifacts, not observed rendered screens.
No browser/computer-use, screenshot, mobile, screen-reader or accessibility QA was performed.
Source/static link/XML checks cannot establish visual quality, responsive behavior or conformance.
Local coordination should use the final draft PR SHA and verify source-manifest/review hashes.

1. Download docs/design/issue-5 with relative paths intact. Open visuals/index.html in a
   local browser, without loading the app or providing credentials. HTML needs no server,
   scripts or network. SVG can be opened independently. Record browser/OS/version and SHA.
2. Compare all A/B/C discovery and account layouts at1440x900,390x844 and320px width.
   Capture explicit desktop and mobile compositions, actual responsive reflow, and text
   clipping/overlap. Long labels and narrow phone compositions must wrap, not disappear.
3. Inspect SVG journeys/wireframes/state atlas; zoom to readable size. Flag clipped labels,
   ambiguous transitions, unsupported controls, concrete customer copy and fixture/simulation annotations outside product screens.
4. Record direction preferences and remaining questions; do not treat static mockup buttons
   as functioning application controls. Mockups contain no real session or API behavior.
5. The mockups' own browser navigation/links can be inspected, but application keyboard,
   VoiceOver/NVDA, form errors, live announcements, IME, virtual keyboard, busy/reset and
   cross-tab behavior require a later **approved implementation/spike**. Do not mark those
   passed from the HTML. Use acceptance.md to plan that future test evidence.
6. Measure rendered contrast including interactive states; run an accessibility scanner on
   implemented pages later, then manually test the selected WCAG checks. Static color-pair
   arithmetic is preliminary evidence only. Record failures as findings; no conformance claim.
7. Publish captures/findings against exact artifact SHA. Human findings/adopted agent findings
   are mandatory until Imran accepts resolution or explicitly waives them. Keep them visible.

| Evidence | Status | Owner / next step |
|---|---|---|
| Textual primary sources | Available via parent/web retrieval; runtime block retained | See sources.md |
| SVG XML, relative links, no remote/script resources | Static check only; recorded in PR | Cloud author/reviewer |
| Rendered artifact quality and comparison | Pending | Local coordinator |
| Real Gradio N/S feasibility spike | Proposed, not authorized by this design PR | Imran decides scope |
| End-to-end keyboard/mobile/assistive tech | Pending implementation | Future approved slice |
| WCAG2.2AA whole-page audit | Not performed | No conformance claim |
| Direction/framework/spec acceptance | Pending | Imran |

## PR6 binding human recheck — do before presenting completion

Use [walkthrough.html](visuals/walkthrough.html#a-S01), a single file containing all A/B/C
and states. Choose Download raw file in GitHub, save/open that HTML locally; no whole repo,
server or provider. Record exact PR SHA, browser/OS and device composition. Inspect all
routes listed in flow-guide.md. If CSS :target/:has behavior differs, record failure rather
than claiming the preview works; the all-state atlas/SVGs provide a fallback review input.

Minimum actual capture set: A/B/C × wide/phone × empty S01, public S17, verification S03,
loading S02A and owned result S09. Review invalid/retry, mixed/cancel/catalog-only, error/empty,
switch/reset and preference/contact states too; capture defects and key recovery evidence.
Confirm all nine invoice details, exact8.91 total, no inferred currency, and contextual truthful
disclosures. Keep review annotations outside product boundaries in captures.

These captures review the portable design, not the application UI or full accessibility.
Publish findings/previews before presenting this revision as complete. H5-01–03 stay
mandatory and open to human closure; even a clean agent re-review cannot close them.
