# AWS v1 grading release — issue 28

Status: direct EC2 v1 deployed and smoke-tested on 2026-11-12 UTC.
Public grading URL: **https://3.222.110.76/** (Elastic IP, retained across stop/start).
See [the static-address record](static-address-2026-11-12.md). The initial launch and recovery addresses are historical.
See [the launch record](launch-2026-11-12.md) for initial revisions, checks and stop time.
Current runtime: `e71bb641f0fe354279cd049762a3a0c13db96471` (device dark-mode contrast fix);
see [the repair review](../../docs/reviews/v1-dark-mode-contrast.md).
The earlier CloudFront attempt rolled back: see `attempt-2026-11-11.md`.
The requested alternative is researched in [the direct EC2 HTTPS proposal](ec2-only-proposal.md).
Preserve v0 tag `capstone-v0.0.0-preview`. This release builds v1 from an exact
40-character commit; it does not merge any pending PRs or update the running Mac app.

## Architecture

Internet → nginx HTTPS on the EC2 instance → loopback Docker port 7860 → existing
Gradio/application. The security group exposes only public TCP 80 (ACME challenge and
HTTPS redirect) and TCP 443 (chat). SSH and Gradio port 7860 are closed externally.
CloudFront is removed; no custom domain, load balancer or NAT gateway. The running
instance now uses the separately managed Elastic IP documented below.
The template originally used an auto-assigned public IP. The running grading instance
now uses a separately allocated Elastic IP; retain that allocation to preserve the link.
For fresh template deployments, auto-assigned IPs can still change on stop/start;
readiness requires a valid certificate for the current address before sharing the link.

Certbot 5.10.0 and transitive dependencies are hash-locked in `certbot.lock`, installed
in a separate host Python 3.11 virtual environment. They do not change the app image
or application dependencies. Let's Encrypt issues short-lived public-IP certificates.
`CertificateAgreement` defaults to `pending`: issuance refuses until Imran explicitly
approves subscriber agreement v1.8 (2026-07-06) and the launch uses the matching accepted
value. Do not change that value on the assumption that implementation approval accepted
legal terms. No personal email is registered; the Certbot option names this
`--register-unsafely-without-email`. Monitoring must not depend on expiration emails.
The public IP/certificate is public; the provider key is never transmitted to the CA.

On every nginx start, ExecStartPre resets the configuration to challenge-only mode;
all other HTTP paths return 503. No HTTP chat or self-signed fallback exists. The
certificate lifecycle first tests ACME in isolated staging directories, then requests
a production certificate. Only a certificate with the current IP SAN, matching private
key, valid production trust chain and more than 24 hours remaining enables HTTPS.
Production certificate/account state lives under restricted `/etc/letsencrypt` on
encrypted EBS. TLS state is separate from the app's quota volume.

A serialized guard checks every five minutes and withdraws HTTPS on invalid certificate,
address/metadata failure or approaching expiry. Configuration/reload failures record
false readiness and stop nginx. A twice-daily renewal timer and boot attempt renew the
certificate and reload nginx on fingerprint change without restarting the application.
A 160-hour certificate expires before the seven-day window ends: verify renewal, not
just initial issuance. Lifecycle units want/sequence after nginx without a Requires
relationship, so a safety stop does not kill its caller before recording failure.

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
nginx adds a burst request limit per direct client IP, not per authenticated user. It is a coarse protection, not a user quota or DDoS guarantee.

## Cost and availability

User authorized public AWS deployment with a $30 spending limit, conservatively treated
as total, and use of the existing local provider key in encrypted AWS storage. OpenAI
charges are separate. The proposed first run is **7 days**, adjustable before launch
between 1 and 14. It is not a promise of uninterrupted hosting until March 30, 2027.
Further availability needs a budget/credit decision. EC2 t2.medium, 16 GiB gp3, public
IPv4, data transfer and applicable taxes are billable; credits/free tiers
are not assumed. Standard CPU credits avoid unlimited CPU-credit charges.

The course IAM policy was inspected after the first launch failed. It permits
`t2.medium` but excludes the original `t3.small`. The corrected server has 4 GiB RAM.
At the published us-east-1 Linux on-demand rate of $0.0464/hour, seven days of server
time is $7.7952; disk, IPv4, requests/transfer and tax are additional. CloudFront listing
was explicitly denied and no allow was found in inspected policies; distribution creation
was not attempted. This replacement removes that dependency.
At illustrative gp3 pricing the fixed seven-day subtotal is about $8.94; traffic,
tax, other account usage and OpenAI charges are additional. No free credits assumed.

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

Keep the new `OnCalendar` UTC date and budget decision in the release record. A past
stop timer may stop a restarted instance promptly. To resume safely, arrange to update
the timer during a controlled boot/maintenance window before restoring public service;
do not assume an offline instance can be edited through Session Manager. A separately managed Elastic IP is now reserved; see the static-address record. It
continues billing while stopped and must be explicitly released after grading approval. The TLS guard revalidates the current IP and can obtain a new
certificate, but does not update previously distributed grading links automatically.
Sessions/preferences are process-local; persistent quota is separate.

## Prepare and launch

```sh
python deployment/aws/make_template.py > /tmp/music-store-v1-ec2.json
cfn-lint /tmp/music-store-v1-ec2.json
bash -n deployment/aws/bootstrap.sh
```

The approved provider SecureString already exists; do not create or print a replacement.
Use a new CloudFormation stack name such as `music-store-v1-direct`; preserve the failed
stack's audit record. Select us-east-1, a public subnet in its VPC with internet-gateway
routing/DNS, the reviewed published source commit, and the seven-day stop interval.
The template uses a latest AL2023 AMI parameter: record its resolved AMI at actual launch.
Review public 80/443 ingress and dedicated secret-read role. Capture explicit action-time
approval for that ingress and Let's Encrypt agreement before accepting/launching.
No broad course IAM permission changes are needed by this design; actual execution may
still reveal account restrictions and must not be presumed successful from a console form.

The template can preview the address before bootstrap completes. Its GradingUrl output
is a candidate, not readiness evidence. Never share it as live until TLS/runtime checks pass.

## Certificate operations after approved launch

```sh
sudo systemctl status music-store-v1 nginx music-store-certificate.service
sudo systemctl list-timers music-store-certificate.timer music-store-tls-guard.timer music-store-stop.timer
sudo cat /var/lib/music-store/tls-state.json
sudo /opt/music-store-certbot/bin/python /usr/local/lib/music-store/tls_host.py dry-run
sudo systemctl start music-store-certificate.service
```

The dry run uses staging without deploying a staging certificate. Inspect actual trust,
expiry and renewal state afterward. Do not print private keys or `/run/music-store/provider-key`.
If certificate provisioning fails, inspect service/journal status: the app remains private.
The hosting unit tests generate only local test certificates and do not call AWS or a CA:

```sh
python -m venv /tmp/music-store-host-tests
/tmp/music-store-host-tests/bin/pip install --require-hashes --only-binary=:all: -r deployment/aws/certbot.lock
/tmp/music-store-host-tests/bin/python -m unittest discover -s deployment/aws -p 'test_*.py' -v
```

Local nginx parser testing is skipped when nginx is absent. The separate Linux CI hosting
job installs nginx and executes both challenge-only and HTTPS configuration parser checks,
using synthetic certificates, without cloud credentials or public certificate issuance.
Bootstrap also requires this complete suite to pass on the actual EC2 host before
starting the application or requesting a public certificate. This provides real Linux
nginx validation when external CI is delayed; it does not turn a queued CI run into a pass.

## Validation gate

CloudFormation success alone does not prove bootstrap or app success. Before sharing
the grading URL, verify EC2 checks, systemd service/timer, container health, `/version`
matching the exact source commit, public HTTPS without login, actual catalog and
verified-owned-invoice flows, collapsed tables, contextual suggestions and mobile
layout. Check that direct public port 7860 and SSH are unavailable. Verify quota file
owner and persistence across a controlled container restart. Record real live model
evidence separately from offline tests; do not claim Docker/runtime checks before
running them. EC2 bootstrap, image build and ACME issuance may take several minutes.

Known issues 10/11 remain deferred by Imran until before demo; issue 23 session errors
remain separate. Baseline full live evaluation was 14/16, not a perfect result.

References: [Certbot IP certificate guidance](https://letsencrypt.org/2026/03/11/shorter-certs-certbot.html),
[EC2 standard CPU credits](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-ec2-instance-creditspecification.html),
[public IPv4 pricing](https://aws.amazon.com/vpc/pricing/),
[SecureString encryption](https://docs.aws.amazon.com/systems-manager/latest/userguide/secure-string-parameter-kms-encryption.html).
