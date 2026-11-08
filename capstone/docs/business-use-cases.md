# Customer business use cases — Music Store AI

## Business context

The end customer is a shopper or existing buyer at a digital music store. The business
buyer is the store operator, whose support team handles repetitive catalog and purchase
questions. The assistant gives customers one conversational place to find music and
understand past purchases, while reducing routine work for support staff.

These are proposed customer scenarios and value hypotheses, not findings from customer
research or measured business results. The capstone demonstrates discovery and purchase
support; checkout, refunds, playback and account changes are outside the current scope.
Persona names are fictional; runnable demos will use appropriate Chinook sample records.

## HC-01 — Find music without navigating a complex catalog

**Who:** Maya, a first-time shopper who knows an artist or genre but does not know the
store's catalog or exact album names.

**How:** Maya asks, “What albums by AC/DC do you carry?” She follows with “Show me tracks by that artist,” or asks for jazz tracks from several artists. The
assistant retrieves actual catalog records and returns names, identifiers and available
prices. If an artist or title is unavailable, it says so clearly instead of inventing stock.
Album-to-tracks lookup is outside the nine-tool baseline.

**Business value:** Reduces the effort of finding relevant music and helps the store turn
browsing intent into informed purchase consideration. This supports conversion, though
the capstone cannot prove increased sales because it has no checkout funnel.

**Success evidence:** Complete an artist-to-track discovery task with relevant database
results; measure task completion, turns and unsupported-claim rate. In a production pilot,
compare catalog-to-product engagement and conversion with ordinary search.

**Spec links:** CAT-01, OR-01, GR-01, GR-02, UI-01.

## HC-02 — Understand a purchase without contacting support

**Who:** Daniel, a returning customer who wants to check a recent music purchase.

**How:** Daniel asks, “What was on my latest invoice, and what was the total?” The
assistant pauses for identity verification, retrieves only his invoices, and shows the
selected invoice's line items and exact recorded total. If he has no invoices, it explains
that clearly. It does not disclose someone else's invoice when given another invoice ID.

**Business value:** Provides immediate self-service for routine purchase questions,
reducing avoidable support contacts and customer waiting time. Accurate amounts and
customer-scoped access support trust.

**Success evidence:** Correct latest invoice, line items and total compared with SQL
truth; zero cross-customer disclosures. A production pilot could measure self-service
resolution rate and invoice-related contact volume.

**Spec links:** INV-01, ID-01, ID-02, ID-03, GR-01, UI-01.

## HC-03 — Continue shopping while reviewing past purchases

**Who:** Priya, an existing buyer who wants to revisit a purchase and explore more music
in the same chat.

**How:** Priya asks, “Show my latest invoice, and what albums by Iron Maiden do you have?”
After verification, the supervisor coordinates the invoice and catalog specialists and
returns both results. Follow-up questions retain the conversation's customer and artist
context, so Priya does not have to start over with a different assistant.

**Business value:** Removes the handoff between account support and product discovery,
reducing friction for repeat customers and creating an opportunity for repeat purchases.
The system surfaces catalog options; it does not promise purchase or recommendation uplift.

**Success evidence:** Both parts answered correctly in one conversation, identity gate
respected and follow-up context retained. Measure mixed-task completion and turns needed;
repeat-purchase impact requires a production experiment.

**Spec links:** OR-01, OR-02, CAT-01, INV-01, ID-01, GR-01, UI-01.

## HC-04 — Return to an experience that remembers musical tastes

**Who:** Elena, a repeat shopper who prefers jazz and wants to avoid restating her taste
every visit.

**How:** In a verified session, Elena says, “I love jazz. Please remember that.” The
assistant saves that explicit preference. On a later visit while the service is still running, she verifies again and asks,
“What genres have I told you I like?” It recalls jazz. If she later adds blues, both remain
saved. “Do you carry rock?” is treated as a search, not a new preference. Any catalog
suggestions must still come from database results.

**Business value:** Creates continuity across visits and reduces repeated information
entry, supporting loyalty and relevant discovery. The capstone proves memory and scoped
recall; recommendation quality and retention gains require further validation.

**Success evidence:** Preferences survive a new conversation in the same process, merge correctly and remain isolated
between customers. Measure explicit-preference capture precision and recall correctness;
production measures could include repeat engagement and perceived relevance.

**Spec links:** MEM-01, MEM-02, ID-03, CAT-01, GR-01.

## HC-05 — Find the right human contact when self-service is insufficient

**Who:** Omar, an existing customer who has a purchase question that requires a person,
such as requesting a refund the assistant cannot process.

**How:** Omar asks, “Who is the support representative for my latest invoice?” After verification, the assistant
selects his owned invoice and retrieves its assigned representative and returns the contact details permitted by the
tool. For a refund request it explains its limits and helps him identify that contact,
without claiming it issued a refund or created a support ticket.

**Business value:** Reduces dead ends and helps customers reach the right person with
less effort. This can reduce misrouted contacts and protect customer trust when automation
cannot complete a request. Automatic escalation/ticket creation is outside this scope.

**Success evidence:** Representative matches the customer's database record, no invented
contact details or action claims, and correct handling if no representative is assigned.
Measure correct-contact identification; production could track misrouted support contacts.

**Spec links:** INV-01, ID-01, ID-03, OR-02, GR-01, GR-02.

## Demo storyline and priority

All five are hero scenarios within the current scope. HC-01 and HC-02 establish core
utility; HC-03 shows multi-agent coordination; HC-04 demonstrates persistence; HC-05
shows the boundary between self-service and human help.

For a five-minute demo: spend about one minute on discovery, one on verified invoices,
one on a mixed query, one on remembered preferences, and one on the human-contact path
and a privacy/empty-result check. Prepare known sample records and expected SQL results.
Measure the capstone's task correctness and safety directly. Present cost savings,
conversion and retention as business hypotheses until a real pilot provides evidence.


Baseline memory lifetime: process-local. Restart clears preferences; this limitation is
explicitly permitted by the course FAQ. See specs/001-music-store for current behavior.
