# A nontechnical guide to the revised experience

Open [the complete walkthrough](visuals/walkthrough.html#a-S01). It contains all three
visual directions and all fixed mock scenes in **one self-contained HTML file**. From
GitHub, open this file, choose **Download raw file**, save it as walkthrough.html and open
it locally. No repository download, package installation, server, account or provider is needed.
GitHub's HTML source view does not run a preview; the local coordinator will provide rendered
wide/phone captures before presenting completion. [SVG flow map](visuals/07-flow-map.svg)
and [desktop](visuals/02-desktop.svg)/[mobile](visuals/02-mobile.svg) are viewable directly on GitHub.

Select **Wide composition** or **Phone composition** in the review controls above the
screen. Select A, B or C to return to that direction's first visit. These controls and all
review notes are outside the product. Product question/buttons only move to fixed mock
states; fields are read-only text samples. No verification, database lookup or provider runs.
No JavaScript, network or external asset is required; CSS :target navigation and :has selectors
select the scene. If the local browser does not support the selectors, use the all-state atlas
or the SVG sequence and record the limitation. Rendered behavior remains pending local check.

## Main routes (identical in A/B/C)

| Route | States and visible actions | Expected distinction |
|---|---|---|
| First-time public | S01 → “What albums by AC/DC do you carry?” → S02D → outside-screen “Next preview” → S17 | Empty first visit, then a user question/loading, then two catalog results; no verification |
| First-time account | S01 → “Show my latest invoice.” → S03 → Verify → S02A → “Next preview” → S09 → “Show the items on invoice382.” → S18 | Account data appears only after simulated verification; summary8.91 and all nine details |
| Already verified | S20 → Send → S02A → S09 | Existing conversation; no identifier prompt; never confused with S01 |
| Mixed request | S01 → combined question → S03M → Verify → S02M → S21 | Invoice first, then catalog; both outcomes readable |
| Catalog-only | S03M → Continue with catalog only → S08 → later account question → S03 | Explicit account cancellation, public albums only, later verification required |
| Invalid / unknown / limit | Review alternatives from S03 → S04/S05/S06 | Error near sample field; retry returns to same pending invoice question; no account enumeration |
| Cancel | S03 or S03M → Cancel verification → S07 | Pending account work cancelled; a new purchase request verifies again |
| Empty / error | S17 → another artist → S11; review map → S10 or S10M | Empty actual catalog result differs from simulated error/partial completion |
| Switch / reset | S15 → New conversation → context-specific S12-S15 → confirm → S01R | No switch by assertion; clear chat/identity/pending task, not preferences. Keep returns to S15 |
| Preferences / human contact | S13 → S13R → S14; S09 → S16 | Explicit positive taste and lifetime; no delete. Contact only, no ticket/refund action |

S12-* are context-preserving reset confirmations: each Keep action returns to its exact
origin, while confirm goes to S01R. S12/S12U are explicit review entry examples for owned
invoice/verification respectively. Busy/loading controls are noninteractive; outside-screen
continuation links advance time in the preview. Generic unavailable S16U does not reveal
whether another account owns a requested invoice; ordinary invoice IDs do not switch identity.

## Provenance and limits

[Sample fixture](sample-fixtures.json) records the source revision/hash, existing bound-tool
inputs/results and selected public sample data. Album/invoice/contact facts are real pinned
Chinook fixture values, **not a live store or real account connection**. New copy is proposed;
verification, loading, failures and preference outcomes are simulated. Public catalog shows
2 of2 AC/DC albums; owned invoice382 is dated2025-08-07, total8.91, with9 line items and
unit prices0.99. Currency is absent in the tool payload; none is invented. No album art,
playback, checkout, refund execution, ticket creation or preference deletion is introduced.

Imran's findings H5-01–03 remain binding in [human-findings.md](human-findings.md). The
separate exact-commit re-review and author dispositions are published in PR6. Local rendered
review and human acceptance/closure remain pending, regardless of static or agent checks.
