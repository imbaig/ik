> Superseded draft: current proposed baseline is [001-music-store/spec.md](001-music-store/spec.md).
> Historical content below remains for review provenance; conflicting details are not current requirements.

# Acceptance scenarios — Music Store AI

1. CAT-01: artist/genre/title/track-ID queries return database names and prices; unknown
   entities return honest empty results.
2. ID-01: invoice request pauses for verification; no account tool executes beforehand.
3. ID-02: valid identifiers verify; wrong/ambiguous inputs do not. Normalize phones and
   compare emails case-insensitively.
4. ID-03: requesting another customer's invoice or inserting a new ID in user text never
   bypasses trusted customer scope.
5. INV-01: date/price ordering, line items and support rep match SQL truth; empty cases
   are handled clearly.
6. OR-01/02: catalog, account, mixed and off-topic scenarios invoke appropriate specialists;
   mixed queries resume correctly after verification.
7. MEM-01: explicit preferences merge, persist across restart and remain customer-isolated.
8. MEM-02: “I love jazz” saves a preference; “Do you have jazz?” does not.
9. DB-01: apostrophes/SQL payloads remain bound data; tools cannot mutate Chinook or
   remove ownership restrictions.
10. GR-01/02: prompt injection and unknown facts cannot produce fabricated albums,
    invoices or amounts; private answers match database truth.
11. RB-01: LLM/tool/database errors return honest recoverable responses with bounded retries.
12. UI-01: two sessions never share verified identity or private conversation state.
13. LOCAL-01/DOC-01: clean setup starts local chat with documented commands.
14. VAL-01: demo/evaluation covers catalog, identity, invoice, mixed query, memory and
    refusal; offline and live-model results are reported separately.

Expand this baseline after full grading-workbook review, before implementation.


## Business journey coverage

Use `docs/business-use-cases.md` to validate complete customer outcomes as well as tools.

| Hero case | End-to-end evidence |
|---|---|
| HC-01 Discovery | Artist/genre question produces relevant actual catalog results and honest no-results behavior |
| HC-02 Purchase clarity | Verification precedes latest-invoice details; totals match SQL and other customers remain inaccessible |
| HC-03 Mixed journey | Catalog and invoice specialists answer both parts; follow-up retains context |
| HC-04 Returning customer | Explicit preference survives restart, merges and recalls only after customer verification |
| HC-05 Human contact | Assigned representative is accurate; unsupported refund request causes no fabricated action |

Business impact measures are hypotheses; capstone validation reports task correctness,
turn count, grounding, preference precision and customer isolation, not assumed ROI.


## Human-review scenario additions (pending acceptance)

- HUM-004: independent customer sessions remain isolated; explicit switch creates a new
  thread and clears private state; free-text IDs cannot switch identity.
- HUM-005: invalid customer in mixed request yields retry/cancel/catalog-only choices;
  no invoice query and no account enumeration; correction resumes under trusted identity.
- HUM-006: swap memory prompt/extractor config, compare labeled evaluations and verify
  unchanged SQL/UI contracts and regression suite; invalid extraction preserves memory.
- HUM-007: seeded telemetry produces accurate aggregate reports without raw identifiers.
- HUM-008: schema mismatch blocks serving; validated candidate snapshot can be rolled
  back; changed customer identities cannot inherit old preferences.
