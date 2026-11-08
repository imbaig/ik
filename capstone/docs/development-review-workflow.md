# Development, review and approval workflow

## Roles and independence

| Role | Responsibility | Assignment |
|---|---|---|
| Human reviewer and final approver | Reviews specs/code evidence and agent findings; raises binding findings; adopts agent findings; signs off milestones | Imran Baig |
| Author / implementation agent | Drafts, implements approved scope, proposes dispositions, collects evidence | Codex parent chat |
| Agent spec/design reviewer | Separate read-only session; rubric, business cases, architecture and testability review | Codex reviewer, recorded per review; first run /root/spec_review |
| Agent code/security reviewer | Separate read-only session; approved spec/diff, tools, ownership, security and tests | Codex reviewer assigned when code exists |
| Agent evaluation reviewer | Reviews dataset, graders, coverage and actual results independently of author | Assigned at validation milestone |
| Automated verification | Tests, exact SQL comparisons and mechanical checks | Local harness; neither human nor agent sign-off |

There are two reviewer categories: **Imran (human)** and **reviewer agents**. Agent
review does not replace human review. Reviewers use project rubric/brief and relevant
OpenAI skills where available and applicable: OpenAI security-best-practices and
security-threat-model for code/security; documents/spreadsheets skills for source reading
when appropriate. Spec Kit analyze/checklists supplement the spec reviewer. OpenAI Docs
supports checking OpenAI-specific APIs. Record actual skill paths, versions/hashes and
invocations for each run. Candidate skills are not presumed installed or used; the first
spec reviewer used an explicit brief, not newly installed OpenAI security skills.
Select skill coverage during each review; no general security skill proves course or
business completeness. Add focused project instructions where no applicable skill exists.

A second pass by the author is a self-review and must be labeled that way. An independent
review requires a distinct agent session or person with recorded identity and artifacts.
We will not invent a model name, reviewer, run ID, approval or test result. Record model
metadata only when available from the actual run; otherwise record “not captured.”

Reviewer agents are authorized for this project by Imran's review-workflow request.
Use a distinct read-only reviewer session for each gate, with the reviewed revision,
reviewer identity, instructions and evidence recorded. The author remains responsible
for changes; reviewer agents report findings and verify resolutions. Imran signs off.

## Decision rights and finding lifecycle

1. Freeze the review inputs with a commit or SHA-256 manifest. Supply the course sources,
   spec, hero cases, architecture and acceptance criteria to a separate reviewer agent.
2. Publish the reviewer report without silently removing or rewriting findings. Imran
   reviews both the artifact and report, adds human findings, and may adopt agent findings.
3. Findings raised by Imran, or agent findings explicitly adopted by Imran, are mandatory.
   The author cannot decline, downgrade, defer or close them unilaterally. If infeasible,
   conflicting or unsafe, document the issue and escalate to Imran for a decision.
4. For other agent findings, the author may accept or decline with evidence and rationale.
   A declined finding remains visible. Imran can adopt it later. Disputed mandatory course
   requirements block the gate pending reconciliation; they cannot be waived by the author.
5. Implement accepted changes, record tests/evidence, and return them to the reviewer for
   verification. Human-origin/adopted findings close only with Imran's acceptance of the
   resolution (individually or as an explicit identified batch). Only Imran can waive them.
6. Provide a final disposition table and revision to Imran for gate sign-off. No silence,
   author self-review, automated pass or agent recommendation counts as human approval.

Finding fields: ID; source (human/agent); severity; location; evidence; requirement;
recommendation; author response; human-adopted flag; mandatory flag; status; resolution
revision; verification evidence; reviewer verification; human closure/waiver reference.
Use JSON null for undecided flags, not a fabricated human decision.

Statuses: open → accepted/declined-with-rationale → fixed-pending-verification →
verified-pending-human-closure (where mandatory) → closed. Waived-by-Imran is distinct
from fixed. Severity describes impact; mandatory status describes decision authority.

## Milestone gates

| Gate | Author's deliverable | Review focus | Sign-off evidence |
|---|---|---|---|
| M1 Requirements and business scope | Source inventory, rubric mapping, hero cases, acceptance criteria | Coverage, scope, measurable outcomes | Imran's explicit approval of a recorded spec revision |
| M2 Architecture and design | Boundaries, tool contracts, identity/storage/config design | Feasibility, ownership enforcement, state lifecycle | Recorded review findings and Imran's design approval |
| M3 Implementation | Runnable catalog/account/memory/UI slices | Code correctness, grounding, query safety and scope | Reviewer findings resolved; Imran accepts implemented scope |
| M4 Validation | Test/eval reports with commands, results, model configuration and commit | Scenario coverage, leakage, failure behavior, evidence quality | Independent or human review disposition; Imran accepts results |
| M5 Release and demo | Clean setup, docs, demo evidence and submission revision | Reproducibility, limitations and delivery readiness | Imran authorizes final submission |

Implementation waits for spec review, as requested. Drafting docs and collecting course
sources can continue before approval. Gate status must reflect actual review, not an
assumption from silence or a completed checkbox.

## Audit record format

For each material deliverable/review, record: event ID, date, milestone, artifact paths,
author/person or agent identity, role, base and resulting Git commit when available,
reviewer identity, review type (self/independent/human), findings/report path, validation
commands and report links, disposition, approver and approval date/message reference.

Until commits exist, record “uncommitted” and avoid presenting a mutable draft as an
approved baseline. At approval, capture an immutable commit or file hash manifest and
link the approval to that exact revision. Changes after approval require a new review
of affected behavior. Keep detailed evidence in docs/reviews/ and evals/reports/ once
created; the ledger links to it. Secrets and private raw records are excluded.

Use planned → authored → reviewed → changes requested/accepted → approved states.
“Reviewed” does not mean “approved”; passing tests does not mean all risks are reviewed.
