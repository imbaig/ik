# Human spec review — proposed responses to HUM-001–009

All nine are mandatory human findings. Changes are proposals, not accepted/closed findings.

1. Gradio: source review confirms expected framework in course FAQ/milestone 6. Add
   explicit Blocks/session/interrupt validation. Original rationale was initially provisional;
   it is now supported by the course documents.
2. specs: normative behavior/design/tests/tasks; docs: explanation, business cases,
   decisions, review/audit/evidence. Link mandatory business outcomes into specs.
3. Add dedicated non-functional requirements with provenance and acceptance evidence.
4. Proposed scope: many concurrent isolated sessions, one active customer per chat.
   Explicit reset/switch re-verifies; no shared multi-user chat or silent identity switching.
5. Unknown ID: acknowledge no match, offer correction/email/phone, cancel or permitted
   catalog-only continuation; never access invoices or disclose candidate account details.
6. Separate versioned memory extraction prompt/schema/interface from validation/merge/store.
   Use focused evals and regression checks to promote changes; fine-tuning unnecessary.
7. Add lightweight event/report requirements; distinguish outcome proxies from proven ROI.
   On-demand local reporting, milestone review cadence; no background automation enabled.
8. Pin dataset revision/hash, validate schema, explicit tested upgrades and rollback;
   namespace/reset memory when customer identities change. No arbitrary schema compatibility.
9. Explicit human reviewer and agent spec/code/security/evaluation reviewer categories;
   applicable OpenAI skills recorded when actually used, not assumed installed.

Related open decisions: course verify-first graph vs public catalog; union-only memory
vs corrections; restart persistence extension; detailed rubric reconciliation. These are
not silently settled by this update. No implementation or milestone approval claimed.
