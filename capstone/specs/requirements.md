> Superseded draft: current proposed baseline is [001-music-store/spec.md](001-music-store/spec.md).
> Historical content below remains for review provenance; conflicting details are not current requirements.

# Requirements baseline — Music Store AI

Working baseline, November 1, 2026. Supersedes the SmartDesk proposal.

## Sources and verification status

- [General notes](https://drive.google.com/drive/folders/1rhqOnnyOaImqGGhHHXJyenbpnLxGK5rq)
- [Music-store documents](https://drive.google.com/drive/folders/1jYh3UyM_S185k_Zj-SozPxiFsBkqLkJ-)

Reviewed: general notes' music-store overview and the detailed statement's Overview and
Problem Statement. Complete detailed guide, grading workbook and milestones/FAQ review
remains outstanding. Do not apply SmartDesk grading weights to this project.
Spec-driven development is adopted by user request; it was not mandated in reviewed
material. Confirm against remaining documents before claiming it is a course requirement.
General notes request a 5–10 minute video; target five minutes pending detailed review.

| ID | Baseline capability | Evidence |
|---|---|---|
| OR-01 | LLM supervisor coordinates separate catalog and invoice specialists | Live routing traces |
| OR-02 | Handle mixed queries through both specialists; reject off-topic requests | Conversation evaluation |
| CAT-01 | Albums by artist, tracks by artist, genre search with artist diversity, title search, track details | Tool tests and grounded answers |
| INV-01 | Invoices by date, purchased tracks by price, support rep, invoice line items | SQL truth comparisons |
| ID-01 | Verify before account/invoice access; pause and resume with human input | Zero private queries before verification |
| ID-02 | Customer ID/email/phone matching; normalized phone and case-insensitive email | Match and failure tests |
| ID-03 | Use trusted verified customer context, never free-text IDs for downstream access | Cross-customer tests |
| MEM-01 | Persist explicit preferences per customer using set-union merge | Restart, merge, isolation tests |
| MEM-02 | Distinguish stated preferences from catalog questions | Positive/negative scenarios |
| DB-01 | Real Chinook database; parameterized SQL only | Provenance and injection tests |
| GR-01 | Factual answers come from tool results; exact names and numbers | Grounding evaluation |
| GR-02 | Honest no-results and out-of-scope responses | Unknown/adversarial cases |
| UI-01 | Usable multi-turn chat interface | Local browser validation |

The general notes supply detailed tool coverage and memory/verification patterns above;
confirm additional constraints against the full guide and workbook.

## Our engineering targets (not yet verified as grading requirements)

RB-01: graceful failures and bounded retries. SEC-01: environment-based secrets and no
runtime customer data in Git. DOC-01: setup README, architecture, validation report and
demo script. VAL-01: deterministic tests plus separately reported live-model evaluation.
LOCAL-01: reproducible Python 3.12 environment and loopback-only local UI.

Identifier matching is a course demonstration, not production authentication. Use sample
records and describe that limitation accurately.

Open: exact deadline, AI-assistance policy, detailed rubric and deliverable confirmation.


## Human-review additions

Quality attributes are specified in non-functional-requirements.md and measurement.md.
HUM-001–009 proposed resolutions are in design.md and docs/development-review-workflow.md.
One verified customer per chat, explicit switching/reset and safe verification failures
are proposed behavioral commitments subject to Imran review.
