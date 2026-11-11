# AWS v1 grading release — issue 28

Status: deployment attempted and rolled back; no live site. See `attempt-2026-11-11.md`.
The requested alternative is researched in [the direct EC2 HTTPS proposal](ec2-only-proposal.md).
Preserve v0 tag `capstone-v0.0.0-preview`. This release builds v1 from an exact
40-character commit; it does not merge any pending PRs or update the running Mac app.

## Architecture

Internet → CloudFront HTTPS (AWS hostname, redirects HTTP, caching disabled) →
EC2 nginx HTTP origin → loopback Docker port 7860 → existing Gradio/application.
The origin security group admits port 80 only from the AWS CloudFront origin prefix
list in us-east-1. There is no SSH or public Gradio rule. This does not authenticate
one particular CloudFront distribution; application admission applies to all requests.
The CloudFront-to-origin hop is HTTP, restricted by the security group. Viewer traffic
uses HTTPS. No custom domain, load balancer, NAT gateway, or production customer data.

The instance role reads exactly `/music-store/v1/openai-api-key` from SSM Parameter
Store SecureString. It also has Systems Manager heartbeat/channel permissions for
maintenance by existing authorized account operators. No broad SSM managed policy is
attached: those policies can include reads of unrelated parameters. Existing account
administrators retain their existing access; the app cannot revoke account permissions.
The key is fetched to a UID-10001-readable file under `/run`, bind-mounted read-only,
and refreshed on service startup. It is absent from Git, image layers, user data,
command-line literals, template parameters and logs. The instance requires IMDSv2
with hop limit 1. The container runs nonroot, read-only, with dropped capabilities.

## Public sample mode and limits

Public access requires both `APP_ACCESS_MODE=public-demo` and
`PUBLIC_DEMO_ACK=PUBLIC_SAMPLE_DATA_ONLY`. The default deployment still requires login.
Chinook identities are fictional sample records; identifier matching is a demonstration
of ownership checks, not production authentication. Never substitute real customer data.

SQLite quota lives at `/opt/music-store/state` on the encrypted root EBS disk and is
mounted at `/app/.cache`. It survives service/container replacement and EC2 stop/start;
instance replacement/stack deletion destroys it. Keep this volume when upgrading and
do not reset the counts just to bypass the limit. Defaults are 60 admitted actions per
UTC day and 300 over the deployment lifetime. Failed admitted actions count. Cancel,
close and reset remain available. An action can invoke several models/retries: this
is not an API-call counter or a dollar cap. Public model completions are capped at
600 tokens (narration at most 350); the model remains gpt-4o-mini by default.
nginx adds a burst request limit per CloudFront origin connection address, not per
end-user identity. It is a coarse protection, not a user quota or DDoS guarantee.

## Cost and availability

User authorized public AWS deployment with a $30 spending limit, conservatively treated
as total, and use of the existing local provider key in encrypted AWS storage. OpenAI
charges are separate. The proposed first run is **7 days**, adjustable before launch
between 1 and 14. It is not a promise of uninterrupted hosting until March 30, 2027.
Further availability needs a budget/credit decision. EC2 t2.medium, 16 GiB gp3, public
IPv4, CloudFront requests/transfer and applicable taxes are billable; credits/free tiers
are not assumed. Standard CPU credits avoid unlimited CPU-credit charges.

The course IAM policy was inspected after the first launch failed. It permits
`t2.medium` but excludes the original `t3.small`. The corrected server has 4 GiB RAM.
At the published us-east-1 Linux on-demand rate of $0.0464/hour, seven days of server
time is $7.7952; disk, IPv4, requests/transfer and tax are additional. No allowance for
CloudFront was found in the inspected policies and its `ListDistributions` call is
explicitly denied. Do not launch this CloudFront-based stack until service permissions
are resolved or a separately reviewed EC2-only HTTPS design replaces it.

A calendar systemd timer is installed before downloads/build and stops the server at
the initial deadline. It survives reboots. Stopping still incurs EBS costs; remove the
deployment after grading with Imran's approval. The timer and application quota are
not an AWS billing hard cap. Inspect actual account usage before extending. Course
lab resource cleanup/expiration may stop the app independently; verify those limits.

To inspect or extend via an authorized Session Manager session:

```sh
sudo systemctl cat music-store-stop.timer
sudo systemctl list-timers music-store-stop.timer
sudo systemctl edit --full music-store-stop.timer
sudo systemctl daemon-reload
sudo systemctl restart music-store-stop.timer
```

Keep the new `OnCalendar` UTC date and budget decision in the release record. Resuming
after a past deadline requires updating the timer before starting the instance/app.
Stop/start can change the public IP/DNS: update the CloudFront origin after inspecting
EC2's current DNS. No paid static Elastic IP is reserved. Session/preference memory is
process-local and lost on restart; persistent quota is separate.

## Prepare and launch

```sh
python deployment/aws/make_template.py > /tmp/music-store-v1-stack.json
cfn-lint /tmp/music-store-v1-stack.json
bash -n deployment/aws/bootstrap.sh
```

In us-east-1 create the approved SecureString using the AWS-managed SSM encryption
key; no plaintext key should be entered into the template. Use CloudFormation to
upload the generated template, choose a public subnet in the selected VPC with an
internet-gateway route and DNS hostnames enabled, enter the reviewed/published source
commit and stop interval, and inspect the generated IAM/security resources. The
template uses a latest AL2023 AMI parameter; the resolved AMI and image IDs must be
captured in the actual release record. CloudFront prefix-list weight consumes 55
security-group rule units. Region/account policy restrictions may reject creation.

Browser action-time confirmation is required before granting role access and launching
the public stack. Never interpret an open console form as proof of write permissions.
Do not accept an AWS toolkit setup prompt as a project requirement.

## Validation gate

CloudFormation success alone does not prove bootstrap or app success. Before sharing
the grading URL, verify EC2 checks, systemd service/timer, container health, `/version`
matching the exact source commit, public HTTPS without login, actual catalog and
verified-owned-invoice flows, collapsed tables, contextual suggestions and mobile
layout. Check that direct public port 7860 and SSH are unavailable. Verify quota file
owner and persistence across a controlled container restart. Record real live model
evidence separately from offline tests; do not claim Docker/runtime checks before
running them. CloudFront/EC2 build may take several minutes.

Known issues 10/11 remain deferred by Imran until before demo; issue 23 session errors
remain separate. Baseline full live evaluation was 14/16, not a perfect result.

References: [AWS CloudFront origin prefix list](https://aws.amazon.com/blogs/networking-and-content-delivery/limit-access-to-your-origins-using-the-aws-managed-prefix-list-for-amazon-cloudfront/),
[EC2 standard CPU credits](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-ec2-instance-creditspecification.html),
[public IPv4 pricing](https://aws.amazon.com/vpc/pricing/),
[SecureString encryption](https://docs.aws.amazon.com/systems-manager/latest/userguide/secure-string-parameter-kms-encryption.html).
