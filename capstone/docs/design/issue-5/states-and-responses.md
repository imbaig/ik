# Critical states and readable response contracts

**Proposed behavior and illustrative copy only.** Visual coverage: [state atlas](visuals/04-states.html).
S01–S16 families and the explicit entry/result/loading/shortcut states are linked in the atlas and flow guide. Nothing in this document claims current store inventory.

## Critical-state coverage

| ID | State / entry | Visible information and allowed next step | Identity, focus and recovery rule | Coverage |
|---|---|---|---|---|
| S01 | Welcome | Public catalog / purchases after sample verification; suggested prompts | Input label; no automatic account lookup | HC01, W-D1/M1 |
| S02 | Loading | Working on your request; send/reset disabled | Keep focus predictable; announce busy once, no fake percentage or live token facts | All |
| S03 | Verifying | Pending task; one sample ID/email/phone; submit/retry | Inline field with label; move focus intentionally to field; no private results | HC02–05, W-D2/M3 |
| S04 | Invalid input | Enter exactly one supported sample identifier | Associate error with field; allow paste; no candidate account suggestions | HC02–05 |
| S05 | Unknown/ambiguous | Could not verify that identifier; try again | No match enumeration, no echoed identifiers; same generic recovery for ambiguity | HC02–05 |
| S06 | Retry limit | Verification did not finish; start New conversation or browse catalog | Respect existing retry bound; no unlimited resubmission promise | HC02–05 |
| S07 | Cancel verification | Account request cancelled; you can ask a new question | Clear pending request; restore composer focus, no silent later execution | HC02–05 |
| S08 | Catalog-only | Account part cancelled; catalog results only | For mixed pending request only; later account query re-verifies | HC03 |
| S09 | Verified | Verified for this conversation; grounded result | Don't expose raw identity; no client authority from badge | HC02–05, W-D3/M4 |
| S10 | Request failure | Couldn't finish this request; retry or New conversation | Honest partial results separated; do not clear identity silently or auto-repeat actions | All |
| S11 | Empty catalog/account | No matching results / no invoices returned for verified account | Empty distinct from failure; refinement suggestions only, no invented stock | HC01/02 |
| S12 | New conversation | Confirmation copy: clears chat/identity/pending task, not saved process preferences | Reset existing service handle; invalidate old session; focus composer; no private flash | All |
| S13 | Preference saved/recall | Only observed saved genres/artists; lifetime note | Positive explicit evidence only; union merge; verify before recall | HC04 |
| S14 | Preference unavailable / removal request | Previous preferences unchanged; removal/edit not supported in this demo | No delete/undo promise; New conversation does not erase profile; restart is not a customer deletion control | HC04 |
| S15 | Customer-switch refusal | Identity cannot change in this conversation; New conversation starts verification | No target-ID interpolation, account existence or queries; ordinary invoice IDs unaffected | HC02/03 |
| S16 | Support / inaccessible invoice | Returned representative fields only, or generic inaccessible/unavailable | No refunds, tickets or automatic escalation; unowned IDs do not disclose existence | HC05 |

New conversation confirmation is a **proposed additional UI safeguard**, not existing behavior;
its implementation/keyboard focus is gated. Prefer inline two-step confirmation over a new
modal until tested. While busy, reset remains disabled; no cancellation/stop-provider promise.
Preference correction is limited to clarifying a question before send or adding a new explicit
positive value. Removing/replacing saved values is outside baseline001 and this proposal;
HAX correction guidance does not authorize adding mutation tools or delete controls.

## Connected review states and actual fixture values

The [one-file walkthrough](visuals/walkthrough.html#a-S01) and [flow guide](flow-guide.md)
make the state sequence explicit. S01 is the empty first visit, S02D public loading, S17
public albums, S03/S03M verification, S02A/S02M verified loading, S09 owned invoice, S18
all details, S20 already-verified shortcut and S21 mixed answer. S04/05/06 show invalid,
unknown/limit; S07 cancels; S08 explicitly cancels account work for catalog-only; S10/S10M
show error/partial failure; S11 is empty catalog; S15 is switch refusal; S12-* preserve
origin on Keep and clear chat/identity/pending task on confirm to S01R. S13/S13R/S14
show capture/recall/removal limitation; S16 contact and S16U inaccessible invoice.

The original synthetic fixture is superseded. [sample-fixtures.json](sample-fixtures.json)
contains actual results from the existing checksum-verified local public Chinook snapshot,
using bound domain tools with trusted fixture context customer1. This was fixture extraction,
not a live store/account connection, real verification, model evaluation or provider call.
Data revision/hash and query inputs are recorded. Loading, verification/failure and preference
outcomes are explicitly simulated outside product screens. Exact monetary strings come from
the tool envelopes, and no currency is inferred. New customer-facing copy is proposed.

## Representative customer responses

All statements below are proposed copy for the pinned public fixture, not runtime claims.
The product screens contain this kind of concrete text, with review provenance outside.

| Response / state | Proposed customer-facing text | Invariant |
|---|---|---|
| Empty first visit /S01 | “What would you like to explore? Find albums and tracks, or revisit a purchase.” Questions: “What albums by AC/DC do you carry?” /“Show my latest invoice.” | No previous messages, result rows or verified account |
| Public albums /S17 | “Here are the albums by AC/DC. Showing 2 of 2 albums. For Those About To Rock We Salute You — Album1. Let There Be Rock — Album4.” | Actual returned order; no invented artwork/playback |
| Verification /S03 | “To show your invoice, first verify one sample identifier. Your request is waiting here.” Label: “Sample customer ID, email or phone.” | Demo-auth caveat contextual; no purchase rows yet |
| Loading /S02A | “Finding your latest invoice… You’re verified for this conversation. I’m checking your invoices.” | Distinct from result; send/reset unavailable; review continuation outside screen |
| Owned summary /S09 | “Your latest invoice is 382, dated 2025-08-07. This is the most recent of the 7 invoices found for your account. Recorded total 8.91. Currency is not included in this record.” | Only owned fixture; exact total; no invented currency |
| Detail /S18 | “Invoice 382. Showing 9 of 9 line items.” Vamo Batê Lata: quantity1, unit price0.99; Mensagen De Amor (2000): quantity1, unit price0.99; Saber Amar: quantity1, unit price0.99; Cinema Mudo: quantity1, unit price0.99; Meu Erro: quantity1, unit price0.99; Será Que Vai Chover?: quantity1, unit price0.99; Mama, I'm Coming Home: quantity1, unit price0.99; Flying High Again: quantity1, unit price0.99; Paranoid: quantity1, unit price0.99. “Recorded invoice total 8.91.” | All returned rows/order/quantities; do not recalculate or round |
| Mixed /S21 | “Your latest invoice” — invoice382, 2025-08-07, recorded total8.91. Then “Albums by AC/DC” — the two albums above, showing2 of2. | Both concrete sections visible in actual mock; account first |
| Catalog-only /S08 | “Account request cancelled. Catalog results only. To ask about your purchases later, you’ll need to verify again.” Then both AC/DC albums. | Pending account portion discarded, not secretly resumed |
| Invalid /S04 | “Check the identifier. Enter one customer ID, email or phone, then try again.” Field error: “Use a single identifier, not two customer IDs.” | Retry retains pending account task; no candidates disclosed |
| Empty /S11 | “No albums matching ‘The Clockwork Lanterns’ were returned. Try a different artist name.” | Actual empty lookup; not a claim that an artist exists |
| Error /S10 | “We couldn’t retrieve your invoices. Please try again. You’re still verified for this conversation.” | Simulated failure distinct from empty; identity not silently cleared |
| Partial mixed /S10M | “Your invoice could not be retrieved. Please retry the purchase question. The account part did not finish.” Then both observed AC/DC albums. | Safe partial results labeled; no complete-task claim |
| Preference capture/recall /S13/R | “I’ve saved your preference for jazz. These preferences remain only while this service is running.” /“You’ve told me you like jazz.” | Simulated explicit-positive save/recall, not real stored profile evidence |
| Removal /S14 | “Removing or replacing saved preferences is not supported in this demo. A new conversation clears chat and verification, but does not delete saved preferences.” | No delete/undo control or success claim |
| Switch /S15 | “Your verified identity cannot change in this conversation. Select New conversation to start a fresh verification flow.” | No target data/existence; invoice IDs unaffected |
| Contact /S16 | “For invoice382, your contact is Jane Peacock. Email: jane@chinookcorp.com. Phone: +1 (403) 262-3443. I can help you find the contact, but I can’t issue refunds or create support tickets.” | Public sample contact; plain text, no real send/call/action |
| Inaccessible /S16U | “That invoice is unavailable here. Check the invoice ID or ask about your invoices.” | Same generic response for foreign/nonexistent invoice |

## Count/truncation example for genre lookup

Pinned Jazz fixture: **130 matching tracks across 10 artists; 10 representative tracks
shown, one per artist**. This is a sample, not a complete track list. Every row below is a
returned fixture row, not a curated/invented recommendation:

- Desafinado — Antônio Carlos Jobim; Warner 25 Anos; track63; unit price0.99.
- Quadrant — Billy Cobham; The Best Of Billy Cobham; track123; unit price0.99.
- Doce De Carnaval (Candy All) — Gilberto Gil; Quanta Gente Veio ver--Bônus De Carnaval; track1102; unit price0.99.
- Heart of the Night — Spyro Gyra; Heart of the Night; track456; unit price0.99.
- Now's The Time — Miles Davis; The Essential Miles Davis [Disc 1]; track597; unit price0.99.
- Jeepers Creepers — Gene Krupa; Up An' Atom; track624; unit price0.99.
- Roll Call — Dennis Chambers; Outbreak; track842; unit price0.99.
- Colibri — Incognito; Blue Moods; track1188; unit price0.99.
- Amanda — Aisha Duo; Quiet Songs; track3349; unit price0.99.
- OAM's Blues — Aaron Goldberg; Worlds; track3357; unit price0.99.

Currency was not supplied. The album examples do not offer album-to-track lookup; artist-track
or returned-track-ID questions remain within supported tools. Later implementation must compare
all nine tool projections against fixtures, keeping exact decimals/counts/order and safe failures.
No formatter, tool, provider or application UI was changed by these design artifacts.
