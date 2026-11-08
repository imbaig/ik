# Critical states and readable response contracts

**Proposed behavior and illustrative copy only.** Visual coverage: [state atlas](visuals/04-states.html).
S01–S16 are linked in the atlas. Nothing in this document claims current store inventory.

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

## Exact-value illustrative fixture

The following invented fixture is a formatting contract only, not a database extract. All
names/IDs/amounts/contact addresses below and in visual artifacts are synthetic. Decimal
strings remain exact; no currency symbol/code is invented when the tool lacks one.

- Catalog genre fixture: 6 matching tracks across 2 artists; 2 representative rows returned,
  `truncated=true`: track9001 “Window Light”, artist “Morrow”, album “Quiet Lines”, unit price
  `0.9900`; track9002 “Slow Orbit”, artist “Northline”, album “Open Hours”, unit price `0.9900`.
  This is one representative per artist, not all genre tracks and not an album track list.
- Owned invoice fixture: invoice9001, date `2026-10-03`, recorded total `2.9700`.
  Two returned line items: Window Light qty2/unit price `0.9900`; Slow Orbit qty1/unit price
  `0.9900`. Preserve recorded invoice total rather than recomputing/rounding it in UI.
- Support fixture: representative “Demo Representative”, `support@example.invalid`,
  phone “not supplied”. This reserved domain is deliberately non-deliverable, not a contact.

## Response examples

| Response | Proposed customer-facing text (synthetic fixture unless stated) | Required invariant |
|---|---|---|
| Album list | “Albums matching Morrow: Quiet Lines — album9101. Showing 1 of 1 returned match.” | Use observed album/artist IDs; no invented track list, artwork or play button |
| Genre/catalog list | “6 matching tracks across 2 artists. Here are 2 representative tracks, one per artist; this is a sample. Window Light — Morrow · Quiet Lines · track9001 · unit price0.9900. Slow Orbit — Northline · Open Hours · track9002 · unit price0.9900. Currency was not supplied.” | Preserve returned_count/total_count/truncated and distinct artists separately; do not call sample complete |
| Invoice summary | “Your latest invoice: 9001 · 2026-10-03 · recorded total2.9700. Currency was not supplied. Ask for line items for invoice9001.” | Latest only from sorted observed results; verified account required; no account-switch field |
| Invoice detail | “Invoice9001 — Window Light: quantity2, unit price0.9900. Slow Orbit: quantity1, unit price0.9900. Recorded invoice total2.9700.” | All returned rows and quantities, exact decimals; do not silently total the sample or add currency |
| Mixed answer | “Your purchase: [the owned invoice summary above]. Catalog: [the observed album list above].” | Account first; separate source/outcome/count labels; failure in either section never hidden |
| Catalog-only continuation | “Account request cancelled. Catalog results only. [Observed catalog list].” | Pending account part discarded; no private data |
| Preference capture | “Saved music preferences: jazz. These remain only while this service process runs.” | Only after actual save outcome; a catalog question is not preference evidence |
| Preference recall | “Saved music preferences: jazz, blues. These remain only while this service process runs.” | Actual loaded union only; verify fresh conversation; no cross-account recall |
| Removal request | “Removing or replacing saved preferences is not supported in this demo. A new conversation clears this chat and identity, but does not delete saved preferences.” | Do not invent successful correction/removal |
| Empty | “No matching catalog records were returned. Try a different artist, title or genre.” / “No invoices were returned for your verified account.” | Empty only after successful empty result; errors never represented as empty |
| Error/partial | “Invoice details could not be retrieved. Please retry. Catalog results are shown below; the account part did not finish.” | Preserve actual safe partial records, no internal exception/SQL/provider text |
| Switch refusal | “Your verified identity cannot change in this conversation. Select New conversation to start a fresh verification flow.” | Existing merged behavior retained; no target existence disclosure |
| Support | “I cannot issue refunds or create support tickets. For this invoice, the returned representative is Demo Representative; email support@example.invalid. No phone was supplied.” | Only tool-returned fields; no link auto-open, ticket, email send or refund claim |
| Unowned invoice | “That invoice is unavailable for this conversation. Check the invoice ID or ask about your invoices.” | Same generic result regardless of whether another account owns it |

Fallback rule: if a new/unrecognized tool envelope cannot be formatted without losing facts,
show a safe unavailable message and log only an allowlisted internal outcome. Never ask the
model to fill missing fields. Later rendering implementation needs deterministic projection
and escaping tests; this PR neither changes renderer nor claims regression/live passes.
