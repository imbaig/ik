# Capstone agent guidance

Work within this capstone; preserve adjacent Wk-* coursework and unrelated changes.
Read .specify/memory/constitution.md and docs/development-review-workflow.md first.
GitHub Spec Kit is the selected workflow; Superpowers has not been installed.

Baseline 001 is approved; implementation is authorized. See docs/reviews/baseline-001-approval.json.
Current baseline is specs/001-music-store/; flat specs are historical drafts.
SPEC-001 through SPEC-008 were independently verified before approval.
Preserve the approval snapshot; substantive baseline changes require review.

Reviewer agents are authorized for this project. Launch them with focused context,
reviewed revisions, the rubric and reviewer brief, rather than inherited author history
where possible. Reviews are read-only. Record actual identities and evidence. Human
findings and human-adopted agent findings are mandatory; only Imran may waive them.

Run Spec Kit from this directory. From elsewhere, set SPECIFY_INIT_DIR to this capstone
path when using project-scoped commands. Ignore runtime state/secrets; do not publish
course-original files. No code or submission approval is implied by tooling setup.

## Pull request review guidelines

Follow docs/issue-driven-development.md for issue/PR changes. Review the exact PR SHA
against linked acceptance criteria and approved specs. Inspect tests for real regression
coverage, trusted customer/session ownership, literal SQL bindings, bounded agent control,
preference evidence and no fabricated store claims. Prompt/identity/memory/orchestration
changes require live evaluation evidence matching the revision; offline doubles alone
are insufficient. Record independent reviewer identity, findings and author dispositions.
Do not self-approve implementation work, merge PRs or weaken human-adopted findings.
