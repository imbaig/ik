# Direct EC2 HTTPS implementation review

Date: 2026-11-11. Author: Codex parent chat.
Reviewed exact commit: `862aa86b5726e32653d873fc6bbaa1a559ad8f73`; base `9c0ba7d`.
Independent read-only reviewer: `/root/aws_public_review`; model metadata not captured.
Instructions: capstone AGENTS, development-review-workflow and EC2-only proposal.
No additional installed review skill was used. Reviewer consulted primary certificate
guidance during the prior design review; this pass inspected code and ran checks.

## Findings and dispositions

| ID | Finding | Disposition | Verification |
|---|---|---|---|
| EC2-01 | Author identified full-transition I/O errors could leave an old listener running | Accepted; encompass config/read/write/test/reload failures and stop nginx | Reviewer verified fix at reviewed source |
| EC2-02 | Reviewer identified Requires dependency could kill caller before false readiness was written | Accepted; false state before stop, Wants/After instead of Requires | Reviewer verified fix at reviewed source |
| EC2-03 P3 | README overstated CloudFront evidence as complete service exclusion | Accepted; listing denial/no inspected allow, create not attempted | Documentation corrected in the following commit |

Human-adoption flags are undecided; no human findings or sign-off are fabricated.
Reviewer found no source blocker after the fixes. Exact reviewed source independently
ran **14 TLS tests: 13 passed, 1 skipped**, plus bash syntax. The skip is the real nginx
parser test because nginx is unavailable locally. Linux CI installs nginx and tests both
generated modes with local test certificates; no AWS/CA/provider credentials are used.

Author checks: same focused TLS result; generated CloudFormation cfn-lint; Ruff and shell
syntax passed. Certbot 5.10.0 installed from the separate hash-locked host dependency set;
its webroot implementation explicitly creates readable challenge files. No application
dependencies or business code changed; prior 431 application tests and targeted live
provider checks remain distinct evidence, not proof of a deployed container.

## Pending release gates

Capture Linux CI results on the published revision. Real EC2/systemd, bootstrap/container,
production IP certificate issuance, renewal dry run, browser trust, current IP handling,
quota-preserving restart and exact stop time remain unverified. CloudFormation output is
a candidate URL until these checks pass. The old failed stack remains audit evidence.

Imran authorized implementing the EC2-only design in chat. The amended public 80/443
ingress and acceptance of Let's Encrypt subscriber agreement v1.8 require explicit
action-time confirmation before launch/issuance. `CertificateAgreement` defaults pending
and no public CA request has been made. Existing encrypted provider key use is already
approved and is not being re-requested. No new AWS resources were created by this review.
Only Imran merges the PR or approves final submission.
