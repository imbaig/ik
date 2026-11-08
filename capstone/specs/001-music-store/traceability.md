# Source/rubric traceability

Full guide and milestones/FAQ read as DOCX XML; workbook criteria must be cross-checked
by the independent reviewer. Original sources are local in the reference pack. No reference
implementation inspected. Course original files are not published with the project.

| Criterion | Weight | Source | Spec | Design | Required evidence | Demo |
|---|---|---|---|---|---|---|
| Architecture | 20% | Guide 5.1/7; FAQ M4; workbook criterion | FR-001 | plan graph/agent roles | Route catalog, invoice, invoice→catalog mixed, off-topic; hand-built vs prebuilt loops | HC-03 |
| Tools/safety | 20% | Guide 5.2/3/7; FAQ M1/2 | FR-002–005 | contracts.md | Nine found/empty/error cases; LIKE, numeric, JSON, genre determinism/diversity, ownership | HC-01/02/05 |
| Identity/HITL | 15% | Guide 5.4; FAQ M3/6 | FR-005–007 | plan identity/state | ID/email/phone; invalid/ambiguous retry; SystemMessage + code boundary; UI resume/reset | HC-02/03 |
| Memory | 10% | Guide 5.5; FAQ M5 | FR-008 | plan memory | Explicit vs question; union; empty skip; customer isolation and reload | HC-04 |
| Prompts | 15% | Guide 5.6; FAQ grounding | FR-009 | plan prompt contract | Six rules in all three prompts; exact amount/count/truncation; no invented synthesis | HC-01/02/03 |
| Testing | 10% | Guide 5.9/8/11; FAQ M1/2/6 | SC-001/002 | tasks.md | >=28 deterministic tests: >=11 DB and >=17 tools; pytest tests/ -v | Evidence report |
| Code/deployment | 10% | Guide 5.10/7/8/11; FAQ M6 | FR-010; SC-003 | plan delivery | python app.py; Docker build/run; env endpoint/model/temp; README/logging | Five-minute demo |

## Source ambiguities resolved for this proposal

- Guide calls for 25+ tests in sections 5.9/8 and 28+ in section 11; target >=28 and
  expand beyond that for full nine-tool error/ownership coverage. No count is a result yet.
- Broad persistence wording is narrowed by FAQ: in-memory restart loss acceptable.
  Retain across conversations only while process lives; document limits in HC-04/demo.
- FAQ explicitly permits catalog verification bypass; choose this option, keeping account
  gating and invoice-first mixed execution mandatory. Catalog-only continuation cancels
  the account portion rather than violating mixed ordering.
- Friendly error messages must remain valid JSON, reconciling M2 wording and JSON checks.
- Guide prohibits committed Chinook SQL; first-run pinned download/cache meets this.
- Both course and project engineering targets are traced. NFR/metrics extensions are
  project commitments, not invented grading requirements. No commercially proven ROI claimed.
