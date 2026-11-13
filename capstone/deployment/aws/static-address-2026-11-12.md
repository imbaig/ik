# Static grading address

Approved by Imran in chat: “go ahead do it,” after reviewing Elastic IP pricing.
Configured November 12, 2026 Pacific (November 13 UTC). Operator: Codex parent chat.

- Current grading URL: **https://3.222.110.76/**.
- Region: us-east-1; instance `i-06d5035dff5a9a48e`.
- Elastic IP allocation: `eipalloc-0f9d8b0e3bfeac6ca`.
- Association: `eipassoc-050e4d16698da680a`; private IP `172.31.11.126`.
- Historical dynamic URLs: `https://18.208.205.193/`, then `https://3.239.222.171/`.
  Those dynamic addresses are no longer grading endpoints.
- Deployed application unchanged: `e71bb641f0fe354279cd049762a3a0c13db96471`.

## Recovery and validation

The original server was found stopped. Previous-boot logs show orderly shutdown at
2026-11-12 22:30 UTC, before the configured November 19 stop deadline. The caller/cause
is unconfirmed: CloudTrail LookupEvents is denied to the course user. Starting the same
instance restored the app but changed its dynamic address. Elastic IP was then allocated
and associated successfully to stabilize the grading link.

The existing certificate lifecycle service obtained a trusted production certificate for
the Elastic IP. Current-IP readiness is true; system curl verified public HTTPS and
`/healthz` reports ready with the unchanged deployed revision. Browser and live catalog
verification are recorded with operator screenshots. No security-group, identity, provider
key or model changes. Existing action limits, quota mount and shutdown deadline retained.

## Ownership and cleanup

This Elastic IP was allocated through the AWS console, **outside CloudFormation**.
The stack template and its SourceRevision/GradingUrl reflect the initial launch, not this
manual operational change. Deleting the stack does not manage/release this allocation.

At $0.005/hour, the address costs $0.12/day or $3.60 per 30 days, including stopped/idle
time. It replaces the existing in-use dynamic public IPv4 charge while attached. Other
EC2/EBS/traffic charges and the $30 total budget still apply. This is not an uptime or
hard-spend guarantee. A course shutdown still takes the application offline, but the
same allocation remains the address unless it is disassociated, released or cleaned up.

After Imran approves final teardown: disassociate this allocation from the instance,
then release it through EC2 Elastic IP addresses and verify it is no longer allocated.
Do not release it during grading. Keep the existing fixed stop timer unless a separately
authorized budget/availability extension changes it.

Pricing: https://aws.amazon.com/vpc/pricing/
