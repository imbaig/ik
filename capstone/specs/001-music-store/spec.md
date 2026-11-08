# Feature Specification: Music Store AI

**Feature**: 001-music-store (no branch created)
**Created**: 2026-11-07
**Status**: Reconciled proposal; independent review and final baseline approval pending
**Input**: Customer-facing music discovery and verified purchase support with preference memory.

## User Scenarios & Testing

### User Story 1 — Discover available music (Priority: P1; HC-01)

A shopper finds actual albums/tracks by artist, title or genre without knowing exact names.
**Why this priority**: Delivers immediate discovery value without account information.
**Independent Test**: Search a known partial artist/title and a missing entity; compare results
with catalog truth. No verified account is needed.
**Acceptance Scenarios**:
1. Given catalog data, when the shopper searches a partial artist/title, then matching real
   records are returned, with total/sample disclosure where limited.
2. Given a genre with several artists, when searched repeatedly, then the same diverse
   sample is returned with one representative track per artist.
3. Given a missing entity, when searched, then an honest no-results response appears.

### User Story 2 — Understand my purchases (Priority: P1; HC-02)

A buyer verifies an identifier and inspects invoices, purchased tracks, line items and
an invoice's assigned support representative.
**Why this priority**: Resolves routine account questions without support waiting.
**Independent Test**: Verify a sample account and compare account answers against its records.
**Acceptance Scenarios**:
1. Given no verified account, when invoices are requested, then the conversation pauses
   for ID/email/phone and no account tool executes.
2. Given a matching identifier, when verified, then the pending request resumes using
   the verified account; invoices are newest first and purchases highest price first.
3. Given another customer's invoice ID, when details are requested, then no private rows
   or existence details are disclosed.
4. Given an unknown identifier, when submitted, then explain no match and offer retry,
   cancellation/reset or catalog-only continuation; invoice access remains blocked.

### User Story 3 — Combine account support and discovery (Priority: P2; HC-03)

A buyer asks both purchase and music questions in one conversation.
**Why this priority**: Avoids separate support and discovery handoffs.
**Independent Test**: Verify a sample customer and complete a mixed request; inspect trace.
**Acceptance Scenarios**:
1. Given verified identity, when a mixed question is asked, then account work completes
   before catalog work, and the reply combines only supported results.
2. Given failed verification, when catalog-only is chosen, then explicitly abandon the
   pending invoice branch for that request and return only catalog results. It is no
   longer a mixed request. A later invoice request requires verification again.

### User Story 4 — Remember my stated taste (Priority: P2; HC-04)

A verified returning shopper receives continuity from explicitly stated music preferences.
**Why this priority**: Reduces repeated information entry.
**Independent Test**: Save preferences, start another conversation in the same running
service, reverify, and inspect recall without relying on other customer profiles.
**Acceptance Scenarios**:
1. Given existing jazz preference, when blues is explicitly added, then both remain.
2. Given a catalog question or no new preference, when processed, then saved preferences
   remain unchanged. Negation, quotation or inferred taste is not a positive preference.
3. Given customer B, when verified after a reset, then customer A's preferences are not loaded.
4. Given an application restart, then memory loss is documented; persistence across
   restarts is outside this baseline.

### User Story 5 — Find my human contact (Priority: P2; HC-05)

A buyer selects an invoice and finds the assigned support representative for human help.
**Why this priority**: Avoids a dead end for unsupported requests.
**Independent Test**: Retrieve a verified customer's invoice-specific representative.
**Acceptance Scenarios**:
1. Given a verified customer and owned invoice, when the representative is requested,
   then only the returned representative details are shown.
2. Given a refund request, then explain that refunds cannot be performed; offer the
   invoice-specific contact without claiming a refund or support ticket was created.

### Edge Cases

Empty catalog/account results; malformed identifiers; duplicate normalized identifiers;
model timeout; invalid model schema; attempted identity substitution; prompt injection;
reset during pending verification; concurrent tabs; invalid numeric tool input; repeated
sends; missing/corrupt/incompatible source data; an unavailable LLM endpoint.

## Requirements

### Functional Requirements

- **FR-001**: Coordinate distinct catalog/account specialists and reject off-topic requests
  without invoking specialists. Mixed requests execute account first, catalog second.
- **FR-002**: Support artist albums, artist tracks, genre discovery, title search and track details.
- **FR-003**: Report track totals and bounded samples, deterministic genre diversity,
  exact prices/numbers and honest empty/error outcomes.
- **FR-004**: Support verified-customer invoices, purchased tracks, invoice representative
  and invoice line items, always enforcing ownership.
- **FR-005**: Accept numeric ID, case-insensitive email or normalized phone; exactly one
  unambiguous matching account establishes trusted identity; miss/ambiguity keeps access blocked.
- **FR-006**: Pause/resume verification, retain pending request, and allow cancel/reset or
  explicit catalog-only continuation. Never infer verified identity from downstream free text.
- **FR-007**: Keep one active customer per chat; isolate concurrent sessions; switching
  clears private history/identity/pending state and requires fresh verification.
- **FR-008**: Load verified-customer preferences; extract explicit positive preferences,
  union-merge without removal; empty/invalid extraction preserves existing data.
- **FR-009**: All factual store claims require observed tool results, exact unrounded
  values, honest failures, explicit scope limits and disclosure of truncated totals.
  Prior chat/model knowledge is not a source of catalog/account facts.
- **FR-010**: Show messages and processing/waiting/success/error states; provide reset.
- **FR-011**: Produce local aggregate reliability/customer-outcome reports without raw
  identity/account/message content; distinguish outcome proxies from actual business impact.
- **FR-012**: Validate source compatibility before serving and support explicit validated
  snapshot upgrades/rollback; never silently transfer preferences across changed identities.

### Key Entities

Customer and verified session; artist/album/track/genre; invoice and line items; assigned
support representative; customer preference set; request outcome event and aggregate report.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All nine supported lookup operations match expected records/ordering on
  the deterministic validation set, including missing and invalid-input cases.
- **SC-002**: Zero unauthorized account disclosures in the defined adversarial, switch
  and simultaneous-session acceptance scenarios.
- **SC-003**: All five hero journeys complete with expected outcomes in a documented
  manual walkthrough; failed verification never yields account data.
- **SC-004**: In a versioned set of at least 30 preference cases (explicit, questions,
  negation, quotation and ambiguous language), precision >=95% and recall >=90%; exact
  union-preservation and isolation assertions pass. This is a project target, not a course threshold.
- **SC-005**: At least 12 live conversation cases cover routing, grounding, verification,
  memory and failures; record actual outcomes, latency and limitations. Zero fabricated
  invoice amounts/entity claims in these cases; failures block acceptance pending correction.
- **SC-006**: Seeded outcome events produce correct date-window aggregates; no claimed
  revenue/retention uplift without a real pilot.

## Assumptions

Sample identity matching demonstrates the course flow; it is not production authentication.
Catalog-only verification bypass is explicitly allowed by the FAQ. Memory survives turns
and conversations within one process; FAQ permits loss at restart. Checkout, playback,
refund execution, ticket creation, shared multi-person rooms and automated reporting
schedules are excluded. Deadline is November 20, 2026. LLM credentials and a compatible
endpoint are runtime dependencies. Review/approval records remain separate from this spec.
