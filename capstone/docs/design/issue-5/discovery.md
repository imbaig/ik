# Current experience and proposed journeys

Source baseline: `8138e7d1c02e759e758c328ccf8b84c25413e4bc`.
Evidence is source inspection, not a rendered session or customer study. HC scenarios
come from [business-use-cases](../../business-use-cases.md); named personas are fictional.

## Inventory: observed in code versus untested hypotheses

| Area | Source-observed behavior | Hypothesis / local research needed | Proposed response |
|---|---|---|---|
| Welcome | ui.py displays title and a long paragraph covering public catalog, sample verification, identity and process memory | First-time users may miss a next action; not user-tested | Short capability intro, two starting prompts, persistent sample-data disclosure |
| Answer | agents/runtime.py render_records emits tool-name headers and JSON row strings; ui.py disables Markdown | JSON keys and raw headers may be hard to scan on narrow screens | Deterministic labels, field grouping, exact text amounts; keep tool envelope internal |
| Layout | Chatbot height440, message textbox and Row buttons; no project-specific responsive CSS | Nested chat/page scrolling and button wrapping may impede mobile use; no device observation | Single-column phone layout; avoid fixed composer until keyboard testing |
| Status | Generator yields busy output before response; status Textbox uses enum text and elapsed time | Status announcements/focus visibility unknown | Plain-language waiting/complete/error with one live announcement region |
| Verification | waiting exposes Cancel verification and Continue with catalog only; same message entry accepts ID/email/phone | Relationship between pending request and input may be unclear | Inline verification card naming pending task; no separate route/modal |
| Identity | Verification owns identity; UI State maps a UUID to server-side view; reset clears conversation | Cross-tab and back-navigation affordances need visual review, not a new auth claim | Verified/Not verified label without public raw identifier; New conversation resets identity |
| Preferences | Conversation appends explicit saved-preference outcomes; union merge, no removal; memory process-local | User may assume durable account settings or editable chips | Show only observed saved values and lifetime; no editable/delete controls |
| Safety | sanitize_html=True, allow_tags=False, no file downloads; privacy tool guards remain server-side | Future rich content could introduce unsafe HTML/links | Escaped deterministic text/allowlisted formatting, never arbitrary model HTML |
| Loading/reset | UI locks sends, disables message/send/reset while busy; double-send ignored | Spinner length, focus restoration and timeout discoverability unknown | Retain busy protection, visible phase text; no promised stop button |

Sources: [ui.py](../../../src/music_store/ui.py), [runtime.py](../../../src/music_store/agents/runtime.py),
[conversation.py](../../../src/music_store/conversation.py), [memory.py](../../../src/music_store/memory.py),
[verification.py](../../../src/music_store/verification.py). Current behavior is not proof of accessibility.

## HC-01–05 journeys

Visual: [five-lane journey board](visuals/01-journeys.svg). Wireframes W-D1/W-M1–2 cover
public entry; W-D2/W-M3 identity; W-D3/W-M4 account/mixed. State atlas covers each recovery.

| Journey and customer goal | Entry and steps | Verification/HITL | Failure/recovery | Success evidence and proposed checks |
|---|---|---|---|---|
| HC-01 find music | Welcome → ask artist/genre/title → see grounded list → ask track details by returned ID | Public; no verification interruption | Empty: clarify spelling/artist/title, no invented inventory. Failure: retry same query; album-to-tracks unsupported | Tool rows/order match; exact counts/prices; bounded sample disclosed. AC-01/02 |
| HC-02 understand purchase | Ask latest invoice → verify → newest owned invoice summary → request line items | Pause pending account request; exactly one ID/email/phone; resume only after deterministic match | Malformed/unknown/ambiguous: generic retry; cancel abandons task; unowned invoice gives generic unavailable, no existence leak | Invoice and detail match scoped SQL; exact recorded total and all returned rows. AC-03/04/05 |
| HC-03 account plus discovery | Ask both in one message → verify once → account section then catalog → contextual follow-up | Same gate; no private request runs while waiting | Catalog-only explicitly cancels account portion. Partial tool failure labels affected section; do not claim both completed | Both supported parts appear in order with independent outcome/sample labels. AC-06 |
| HC-04 remember tastes | Explicit positive taste request → verify if anonymous → save explicit values → New conversation → reverify → recall | Only verified identity owns memory; fresh verification on each new conversation | Extraction fails: previous data retained. Removal/correction unsupported; explain no removal, do not imply New conversation deletes preferences | Saved values match observed union; questions not saved; second customer isolated; restart clears process memory. AC-07 |
| HC-05 human contact | Ask invoice contact/refund help → verify → select owned invoice/latest via observed rows → retrieve permitted rep fields | Account guard before any private/contact lookup | No rep/unowned invoice/failure: generic unavailable or retry, no invented address; no ticket/refund execution | Contact exactly matches owned invoice's tool response; clear scope boundary. AC-08 |

Task completion, turns and comprehension are future measures; no conversion, sales,
retention or support-savings claims. Local walkthrough should include one first-time
participant if feasible; record observed issues separately from designer assumptions.
