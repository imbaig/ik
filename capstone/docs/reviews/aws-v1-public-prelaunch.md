# AWS v1 public prelaunch review — issue 28

Author: Codex parent chat. Date: 2026-11-11.
Base: `eaaf902ed29f0978e1eb2f2902f5aedd1b03b786`.
Reviewed source: `6a98df880dee5ce0d7ead094050fc9dbc9931f2b`.
Independent read-only reviewer: `/root/aws_public_review`; model metadata not captured.
Instructions: capstone AGENTS, development-review-workflow and issue 28 acceptance scope.
No additional installed review skill was used. This is not human approval.

## Reviewer findings and author dispositions

| ID | Finding | Author disposition | Reviewer verification |
|---|---|---|---|
| AWS-01 P1 | Public mode allowed omitted token cap | Accepted; public deployment defaults to 600 and rejects larger caps; regression added | Verified fixed at reviewed source |
| AWS-02 P2 | Narration overrode a smaller configured token cap with 350 | Accepted; use min(configured,350); construction regressions added | Verified fixed at reviewed source |

Neither finding is recorded as human-adopted; no human decision is fabricated.
Reviewer found no additional actionable source defect in template/bootstrap. Persistent
quota mount, narrow parameter read, excluded SSH/Gradio ingress and early stop timer
were inspected. Reviewer explicitly required actual AL2023/nginx/Docker/CloudFront
runtime checks before sharing a URL. Independent test execution was unavailable to the
reviewer at report time because it initially sought a checkout-local virtual environment;
the following executed results are author evidence.

## Executed evidence

- `PYTHONPATH=src <existing-capstone-venv>/bin/python -m pytest -q`:
  **431 passed**, existing dependency deprecation warnings.
- Ruff source/tests/AWS generator: passed. `git diff --check`: passed.
- Generated JSON: `cfn-lint` passed. `bash -n deployment/aws/bootstrap.sh`: passed.
- Real gpt-4o-mini, public deployment token cap 600, exact reviewed source:
  Queen album rows grounded in tools; invoice request pauses for verification; sample
  customer 1 resumes and returns owned invoice 382: **3/3 targeted checks passed**.
  This is not a full live evaluation or deployed-container proof. Initial harness run
  used an incorrect expected invoice-tool name and reported a false failure; the
  corrected assertion uses `get_invoices_by_customer_sorted_by_date`. Both local
  redacted run reports were retained in the coordinator's outputs/aws-v1 directory.

## Deployment status and pending gate

us-east-1 EC2 launch form, IAM policy selection, Parameter Store SecureString form and
CloudFormation stack list loaded on retry. Write permissions have not been proven by
provisioning. No server, role, provider parameter or distribution was created. CloudShell
had failed earlier; it is not a prerequisite for the template approach.

CloudFormation upload chooser timed out twice. The secret-free template is generated
locally; no successful upload or stack submission is claimed. Browser file-URL access
needs user attention or a supported alternative upload flow.

Proposed stack is documented in deployment/aws/README.md. Seven-day initial stop is
proposed to preserve budget, adjustable before launch; uninterrupted availability to
March 30, 2027 is unresolved. The $30 infrastructure limit is conservatively total;
provider charges are separate. Browser policy requires action-time confirmation for
the concrete public exposure and IAM access grant. Approval has not been requested
or recorded for this exact template yet. Existing-key encrypted-storage authorization
is already recorded and does not need to be requested again.

Remaining: publish reviewed revision, prepare AWS review screen, confirm exact public
stack/IAM grant, create encrypted parameter, launch, verify real container/HTTPS and
quota-preserving restart, capture actual IDs/cost controls and share grading URL.
Only Imran merges the PR. v0 checkpoint and current Mac processes are preserved.
