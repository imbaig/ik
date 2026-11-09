# Clarify — unresolved human decisions

**No human design/spec approval recorded.** User-authorized design discovery only.

| Decision | Recommended starting point | Alternatives / evidence needed | Authority |
|---|---|---|---|
| D1 direction | B · Clear Conversation for low custom-layout burden | A warmer editorial identity; C dense reference workspace; local render/comprehension review | Imran |
| D2 framework | Retain locked Gradio5.50; later one-day deterministic spike if explicitly authorized | React/Vite/FastAPI only if essential checks need fragile DOM hacks; compare costs/security/deadline | Imran |
| D3 spec | Review this packet and independent findings at frozen revision | Amend requirements/acceptance; baseline001 unchanged | Imran |
| D4 slices/deadline | Plain readable responses and inline recovery before rich actions | Defer sticky composer/custom components; remaining work must fit November20 or explicit rescope | Imran |
| D5 exact-value/currency presentation | Preserve decimal strings; say currency not supplied when absent | Currency display only with observed authoritative metadata; no currency inferred from locale | Imran |
| D6 reset confirmation | Inline two-step safeguard, no new modal | Keep one-step reset with clear pre-action consequences; test accidental reset risk and focus | Imran |

Boundaries are already fixed: no preference delete/replace, refunds/tickets/checkout/playback,
production-auth claims, fabricated facts, baseline approval edits, credentials or provider calls.
Local visual findings and any human-adopted findings are binding; only Imran closes/waives them.

D7: MVVM-inspired presentation separation is now a **binding requirement**, per
[Imran's architecture comment](https://github.com/imbaig/ik/pull/6#issuecomment-6730142179).
The proposed detailed contracts/module extraction in [design.md](design.md) need independent
review and Imran acceptance. This does not decide D1 direction or D2 frontend migration;
no MVVM library/API service is needed merely to satisfy the pattern.
