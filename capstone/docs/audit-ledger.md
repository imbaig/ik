# Milestone audit ledger

This ledger records known work without retroactively claiming reviews or approvals.
Dates reflect this chat's work history; precise model versions and historical run IDs
were not captured. All current repository artifacts are uncommitted drafts.

| Event | Date | Gate / artifact | Author | Review and evidence | Approval / status |
|---|---|---|---|---|---|
| A001 | 2026-11-01 | Initial scope, music-store specs and five business hero cases | Codex, this chat; Imran supplied direction and feedback | Iterative human discussion; no formal independent review | Draft; no formal milestone sign-off |
| A002 | 2026-11-07 | Course-original reference pack and extension | Codex collected files; Imran supplied November 20 deadline | Downloaded PDF, two DOCX files and rubric XLSX; full rubric reconciliation pending | Deadline established; spec approval pending |
| A003 | 2026-11-07 | specs/design.md subsystem boundaries; development workflow and this ledger | Codex, this chat | Author consistency check only; no independent reviewer assigned | Awaiting Imran's review |

## Current gate status

- M1 scope/requirements: draft; full course-source/rubric reconciliation still pending.
- M2 design: draft; boundary view added for review.
- M3 implementation: not started.
- M4 validation: not started; no test or evaluation passes claimed.
- M5 release/demo: not started; no commit, push or submission approval claimed.

## Approval record

No formal milestone approval has been recorded. Future entries must identify the reviewed
revision and actual reviewer/approver. Conversational interest, project selection and
agreement with an explanation are not blanket implementation or release sign-off.


## A004 — Reviewer workflow authorized, November 7, 2026

Imran requested reviewer agents, joint human review, mandatory human/adopted findings
and skill/harness research. Codex updated the workflow and launched two distinct
read-only sessions: `/root/spec_review` and `/root/review_harness_research`. Research
completed; spec review report pending at this entry. No implementation or milestone
approval granted. Reviewer model/version not separately captured. The SHA-256 manifest
created during this work identifies the current packet, not necessarily the files as
read by an already-running reviewer; use the reviewer's own snapshot where provided.


## A005 — First independent spec review completed

Reviewer `/root/spec_review` reviewed course contents and draft specs read-only. Report:
`reviews/spec-review-001.md`; author proposed responses:
`reviews/spec-review-001-author-response.md`; findings tracker: `reviews/findings.json`.
Eight findings; baseline not recommended for approval. Human adoption/closure undecided.
No implementation or spec corrections have been made on the strength of this review yet.


## A006 — GitHub Spec Kit adoption, November 7, 2026

Imran selected GitHub Spec Kit and authorized resumed setup. Codex initialized
specify-cli 1.3.2 with Codex skills and Bash scripts in capstone/. Existing drafts
were backed up and preserved; author added draft constitution and AGENTS.md guidance.
Setup verification: CLI version and generated-file inventory. No technical baseline
approval, implementation, test pass, commit or push is claimed. SPEC-001–008 remain open.


## A007 — Human findings HUM-001–009

Imran raised nine spec/design/workflow findings. Author recorded all as mandatory,
added proposed resolutions and NFR/measurement specifications, and verified Gradio
expectations against the original DOCX texts. Status: resolution proposed; human review
and independent verification pending. No finding closed and no implementation approved.


## A008 — Spec baseline reconciliation

Imran accepted HUM-001–009 proposed resolutions and authorized next steps. Author
prepared specs/001-music-store packet using the resolved Spec Kit template and full
course guide/FAQ. SPEC-001–008 are fixed-pending-independent-verification. Final baseline
approval remains pending. Hashes are in the feature review-manifest.json. No code/tests.


## A009 — Baseline review 002 verified

Separate reviewer /root/baseline_review_002 found no material course omissions; two
clarifications were fixed and reverified. All 11 approval-manifest hashes match.
SPEC-001–008 independently verified; final Imran baseline sign-off pending.
No application implementation, tests, commit or push performed.


## A010 — Baseline approved

Imran explicitly approved baseline (“approving baseline”). All 11 reviewed hashes
were reverified before recording approval in reviews/baseline-001-approval.json.
Specification/design gate approved; implementation authorized. Release/submission
approval remains a separate future gate. Baseline files are preserved unchanged.


## A011 — Milestone 1 implemented and independently reviewed

Author: Codex parent. Reviewer: /root/milestone1_review (distinct read-only session).
52 deterministic cases and Ruff pass; reviewer independently reran. M1-001/002 fixed
and verified. Real dataset fetch/cache smoke performed by author. Evidence in
validation/milestone-1.md and reviews/milestone-1-review.md; code manifest recorded.
Approved baseline files preserved unchanged; T02 execution complete, human milestone
acceptance pending. No tools/agents/UI implemented and no commit/push.


## A012 — Milestone 1 accepted; Milestone 2 authored

Imran's “good, move one” accepted the presented Milestone 1 and authorized the next
tool slice. Acceptance references the preserved M1 handoff manifest, not dependency
files subsequently extended for tools. Author added nine LangChain tools and 69 tool
cases; full author suite is 121 passing. Independent /root/milestone2_review pending.
No implementation approval beyond authorized slice, release, commit or push claimed.


## A013 — Milestone 2 independently verified

Nine tools and 74 tool cases implemented; 126 total cases pass. Reviewer
/root/milestone2_review found P2 M2-001 stored-data JSON failure; author fixed and
reviewer independently verified all 126 cases plus Ruff. No remaining findings in
scope. Human M2 acceptance pending. No live model, agent graph, UI, commit or push.


## A014 — M2 accepted; identity/HITL authored

Imran's LGTM accepted M2; subsequent explicit go-ahead authorized implementation.
Parent authored Pydantic identifier extraction adapter, deterministic matching and
server-owned LangGraph verification service with interrupts/resume and guarded tool
execution. Author suite: 152 passing; /root/milestone3_review is reviewing. No live
provider evaluation, browser UI, commit or push claimed.


## A015 — Identity milestone independently verified

Reviewer /root/milestone3_review reproduced two P2 findings; author fixed and reviewer
verified both with 158 passing tests and Ruff. Scope is service-level identity/real graph
interrupts and guarded tool execution; no live extraction-quality claim or UI yet.
Evidence: validation/milestone-3.md, reviews/milestone-3-review.md and code manifest.
Imran M3 acceptance pending; no commit/push/release approval.


## A016 — M3 accepted; M4 independently reviewed

Imran accepted M3 and authorized next milestone. Author implemented structured routing,
hand-built catalog/prebuilt invoice agents and constrained supervisor phases integrated
with verification. Separate /root/milestone4_review found P2 M4-01/02; author fixed both
and reviewer reverified184 tests plus Ruff. Human M4 acceptance pending.
Evidence and code hashes saved; no live-provider/UI/commit/push claim.


## A017 — M4 accepted; memory milestone authored

Imran accepted M4 and authorized memory. Author added process-local customer memory,
structured extraction, verified-turn eligibility, recall/catalog context and an evaluator.
Independent /root/milestone5_review identified anonymous/cancelled history contamination
and negative/quoted/hypothetical filter gaps. Author corrected with regressions; final
review pending at this entry. Guardrail corpus expanded40 cases; not live-model evidence.


## A018 — Memory milestone independently verified

Author resolved M5-01 history eligibility and M5-02 evidence negation/quotation findings,
including reviewer follow-up repros. Reviewer /root/milestone5_review verified245 tests,
Ruff and42 labeled candidate probes. Live recognition/SC-004 remains unvalidated;
regression corpus is not held-out. Human M5 acceptance pending. Evidence and source
hashes saved; no live-provider/UI/commit/push claim.

## A019 — M5 accepted; UI/telemetry milestone verified

Imran accepted M5 with “looks good. move to next milestone”, authorizing T07.
Author implemented Gradio 5.50 UI, session cleanup and metadata-only local telemetry/report.
Independent `/root/milestone6_review` found three P2 issues: mixed fallback/task inflation,
requirements dependency omission and zero tool durations. All accepted and fixed with
regressions; reviewer reverified 80 focused tests and Ruff, no remaining actionable findings.
Author full suite 267 passed, 59 deprecation warnings; Ruff lint/format pass. Browser QA
verified catalog, HITL correction/cancel/fallback, two tabs/customer isolation, reset and
Clear using labeled deterministic models and real graphs/tools/DB. No live model quality,
Docker, clean install, commit or push claim. M6 human acceptance pending.

## A020 — M6 accepted; live evaluation and corrective iterations

Imran accepted M6 with “looks good. move to next milestone”, authorizing T08. API key
was initially absent; missing-key commands recorded zero attempts. Imran then supplied
it in .env.example. Author moved it to ignored mode-0600 .env, cleared the template,
verified Git ignore and scanned publishable project files for the exact key without
logging its value. Provider connectivity verified; no key is in the report artifacts.

Independent data author /root/milestone7_eval_cases created blind preference v1 and
conversation recommendations. /root/milestone7_fresh_holdout created successive blind
preference v2/v3/v4 without reading implementation, prompts or results. All sets and failed
runs preserved. Exposed sets were retired to regression; no labels changed. Final v4
first-run p1/r0.97436 independently recomputed, no false positives/extraction errors.
Known conservative artist-name miss retained as a miss, not relabeled.

Author corrected case-sensitive preference grading; strengthened exact SQL request,
count/order, prose, memory, reset and failure grading after independent findings.
Reviewer /root/milestone7_eval_cases identified marker-spoof/question/suffix issues;
regressions added and fixes reverified. Live conversation runs exposed supervisor repeated
handoff, bare numeric ID rejection, numeric-track and taste routing/support-contact gaps.
Handoff history and versioned prompts were corrected. First three runs 2/16,5/16,12/16;
fourth run and final semantic review pending at this entry. Full reviewer suite299 passed.
No release approval, clean install, Docker, commit or GitHub push claim.


## A021 — Final live-validation gate independently verified

Author corrected explicitTrackId binding and current-request framing. Supervisor phase
ends on its genuine framework return, so the initial12-action limit is preserved rather
than raised. Regression tests cover repeated delegation and a three-account-tool mixed
request within12 actions. Final full304 tests pass; Ruff lint/format pass; independent
reviewer repeated suite and verified source hashes. Final16/16 live scenarios pass across
47 turns; reviewer inspected all29 tool records against SQL with zero factual/ownership/
selection/count/order mismatches and no fabricated invoice/entity claims. Final blind46
preference cases p1/r0.97436 independently recomputed; sole conservative But-artist miss
retained. Nonblocking overfetch/identity-refusal wording observations remain documented.

No labels changed, no failed runs hidden. Code, datasets, commands, test artifacts and
independent review saved. All code uncommitted; no clean-install/Docker/GitHub-push claim.
Ready for Imran’s M7 acceptance; agent recommendation is not human approval.

## A022 — Authorized baseline checkpoint and GitHub trial preparation

User authorized trying issue-driven development after discussing cloud execution and
credential-free CI with local live-evaluation gates. Author prepared scoped baseline,
SHA-pinned read-only offline CI, issue/PR templates and workflow/reviewer instructions.
Independent /root/github_trial_review verified304 offline tests/Ruff, no blockers and
publishable scope excludes secrets/runtime/course-originals and unrelated Wk-6/.DS_Store.
User chose GitHub account imbaig; connector initially used ibaig99-design/read-only,
while Git SSH confirmed imbaig. Cloud environment and unattended listener not configured
at this entry. Checkpoint publication is not final course release/submission approval.
