# Proposed acceptance checks — NOT executed

All checks below are future acceptance criteria, not passed results. Static artifact checks
and source inspection cannot satisfy browser, application or accessibility criteria.
References: [sources](../../docs/design/issue-5/sources.md), [state matrix/fixtures](../../docs/design/issue-5/states-and-responses.md).

| ID | Given / when / then and test evidence | Visual / requirements |
|---|---|---|
| AC-01 | Given a new anonymous chat, when opened, capabilities, sample-data limits and two editable starting prompts appear; catalog request executes without verification. Capture desktop/phone and grounded result | W-D1/M1/2, S01; CX01/09 |
| AC-02 | Given fixed tool fixtures for every one of nine tools including missing fields, markup and truncated results, when rendered, compare each displayed fact/order/count/decimal string to fixture; no omissions, additions, inferred currency, fake artwork or executable markup. Genre total vs representative artist sample remains distinct | A/B/C discovery/account; S11; CX02/10 |
| AC-03 | Given account or mixed request without identity, no account tool runs; inline task/input/error is readable. Test malformed, unknown and ambiguous identifier, bounded retry-limit, retry success and cancel. No candidates/target existence exposed; preserve pending task until explicit exit | W-D2/M3, S03–07; CX03/04 |
| AC-04 | Given verified buyer, show latest owned invoice and all returned detail rows/quantities/exact recorded total. Foreign/nonexistent invoice gives indistinguishable safe response; same-account followups work; two tabs never share private results | W-D3/M4, S09/16; CX02/04 |
| AC-05 | Given verified customer1 and explicit switch to2, fixed refusal explains New conversation; identity unchanged and no target queries. Invoice ID2 is not a switch. New conversation invalidates old handle, clears transcript/identity/pending request and requires fresh verification; no stale private flash after reset/back/reload/expiry | S12/15; CX04/08/10 |
| AC-06 | Given mixed request, show account then catalog, each with real metadata/outcome. Inject failure in each branch separately; no complete-task claim for partial response. Catalog-only drops pending account branch, later invoice query re-verifies | S08/10, W-D3; CX05 |
| AC-07 | Given explicit jazz preference, actual save outcome shows jazz and lifetime note; questions/negation not saved. New chat same process re-verifies before union recall; other customer isolated. Failure preserves old values. Removal question honestly states unsupported; reset does not promise deletion | S13/14; CX06 |
| AC-08 | Given owned invoice support request, contact fields match tool or honestly say unavailable. Refund/ticket requests explain limits; no sending/action claims. Malicious links/markup cannot execute | S16; CX07/10 |
| AC-09 | Given selected direction, compare actual1440x900 and390x844 captures to frozen approved artifact; annotate every deviation. Local review also checks320px,768px and landscape/keyboard. Long names/decimal amounts wrap without lost facts | All visuals; CX09/12 |
| AC-10 | Given busy, failure and recovery, screen reader receives one contextual state announcement; no repeated token chatter. Duplicate send suppressed; no fake percentage/cancellation; keyboard remains usable and focus restored after recover/reset | S02/10/12; CX08/09 |
| AC-11 | Given all implemented journeys, verify selected WCAG checks below, plus complete relevant A/AA criterion inventory. Scanner findings resolved/recorded with manual evidence. No conformance claim from this design packet or scanner alone | All; CX09 |
| AC-12 | Given final future PR, record exact SHA, approved vs actual visuals, offline/e2e checks, security/session cases, independent read-only report/dispositions and affected live evaluation where rendering/grounding/orchestration changes. Imran explicitly decides acceptance | Slice map; CX11/12 |

## Human-review prototype acceptance — binding, not yet closed

These checks apply now to the **design prototype**; preceding app/runtime checks remain
proposed for future implementation. [Human findings](../../docs/design/issue-5/human-findings.md),
[entrypoint](../../docs/design/issue-5/visuals/walkthrough.html#a-S01) and
[route/state key](../../docs/design/issue-5/flow-guide.md).

| ID | Check and required evidence | Findings / status |
|---|---|---|
| AC-13 | In each A/B/C wide/phone first visit S01, observe zero messages/results and no verified identity. Select public question → S02D loading → S17 actual two-album result. Capture distinct entry/result previews | H5-01; static separation authored, actual local render and human closure pending |
| AC-14 | Follow account request S03→S02A→S09→S18; verified S20→S02A skips S03. Inspect invalid/unknown/retry/limit, cancel, mixed/catalog-only, empty/error, switch/reset paths. Active mock anchors resolve; noninteractive fields/loading controls are explained outside product; every reset Keep returns to exact origin | H5-02; static link/route recheck, then local navigation preview required |
| AC-15 | Product areas contain concrete questions, realistic replies, exact pinned-Chinook values/counts and no structural filler or engineering/provenance notes. Disclosures remain truthful/contextual. Cross-check fixture JSON; inspect all A/B/C, wireframes and atlas in content context | H5-03; source/fixture checks plus rendered local review required |
| AC-16 | Freeze new SHA, publish separate read-only re-review of changed copy/flows and author dispositions; preserve mandatory human findings. Attach local actual desktop/mobile previews before presenting completion; only Imran closes/waives human findings or approves design/spec | H5-01–03; no human closure/approval inferred from agent/static evidence |

## Proposed accessibility test protocol

Target is WCAG2.2AA, not a conformance claim. Use actual implemented pages, keyboard-only,
NVDA+Firefox and VoiceOver+Safari including iPhone where available; record versions and
unavailable combinations. These selected checks are not an exhaustive WCAG audit.

| Criteria | Observable test / pass condition | Evidence status |
|---|---|---|
| 1.3.1 /1.3.2;4.1.2 | Inspect accessibility tree: labels, headings, lists and account/detail relationships; names/roles/states match controls and visual reading order | Proposed |
| 1.4.3 /1.4.11 | Measure actual normal text>=4.5:1; large text>=3:1; required component/state boundaries>=3:1. Test selected direction including focus/error states | Proposed |
| 1.4.4 /1.4.10 /1.4.12 | At200% text,400% browser zoom/320CSSpx and text-spacing override, ordinary content and actions remain readable without page-level two-axis scrolling or clipping | Proposed |
| 2.1.1 /2.1.2;2.4.3 /2.4.7 /2.4.11 | Tab/Shift+Tab through all recovery paths; use Enter/Space; no trap; logical focus order and visible focus not hidden by composer, banners or keyboard | Proposed |
| 2.5.8 | Measure interactive targets>=24x24CSSpx or document valid exception; product aims44px primary controls with8px gaps | Proposed |
| 3.3.1 /3.3.2 /3.3.3 | Submit invalid/unknown sample identifiers; error text is associated with labeled input and gives safe correction; no color-only error | Proposed |
| 3.3.8 | Paste supported sample identifiers without cognitive puzzle/memory test; do not claim sample matching is production authentication | Proposed |
| 4.1.3 | Busy/verification/result/failure/reset announced with context without unnecessary focus shift; no raw private identifier in status | Proposed |

Also inspect color-independent meaning, help consistency, no forced motion/hover-only
controls, no timeouts that strand users silently, and future confirmation behavior. A final
relevant A/AA inventory must account for every criterion, marking applicability with reasons.
Static mockup buttons do not implement forms, sessions, focus recovery or live regions.
