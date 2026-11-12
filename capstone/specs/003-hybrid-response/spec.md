# Hybrid conversational response layer

User approved hybrid response composer: a model writes a short explanation; deterministic code renders factual tables. Persona: friendly concise record-store clerk; help discovery and past purchases, not checkout. Respond to the actual request, explicitly distinguish unsupported qualifiers, empty matches and failures; avoid database jargon and unrelated invoice recovery for catalog questions.

## Boundaries and acceptance

Application dispatch -> verified tool result -> evidence summary -> response writer -> structural checks -> separate model grounding gate -> escaped introduction + unchanged deterministic tables. The writer and gate have no tools, history, verification authority, private rows or storage access. Original question is retained across verification continuation but account/mixed requests are replaced by generic scope for the writer; no identifier response/billing/contact/profile is sent. Catalog input includes bounded original question and bounded public artist/album/track labels with section status/counts/truncation. Tool strings and question are untrusted data, never instructions.

At most two additional model calls per eligible completed dispatch: writer and gate, each4s SDK timeout, no retries, bounded output. No calls for verification, greetings, refusals, expired sessions, preference-only answers or facts-free failures. A configuration switch disables writing; injected adapter defaults off in offline tests. Writer or gate exceptions, malformed/oversized/markup/unsupported numeric content, refusal or rejected grounding use deterministic natural fallback. No regeneration loop. Model grounding is probabilistic, not proof; deterministic tables and mandatory limitation/error notices remain authoritative and visible even if prose is accepted.

Prose maximum500characters, plain text, two or three short sentences requested. No names/amounts/IDs/dates/private fields needed in account introductions. No recommendation/popularity/training-data facts or completed checkout/refund/ticket claims. Gate checks every claim against supplied evidence and request relevance, honesty about partial/empty/error state. Both adapters use existing configured provider/model; no new dependency or secret destination. Added call time/status recorded in typed result for audit, without storing raw prompts/chat in telemetry. Legacy service.send/evaluation fact text remains unchanged.

## Tests and evaluation

Tests cover generation/approval, rejection/timeout/schema/markup/numeric fallback, minimization, zero results context-specific recovery, mixed/error/empty distinction, mandatory notices and exact table identity. End-to-end dispatch verifies original request after verification and no identity leak. Frozen SHA independent review and targeted live writer/evidence judge + browser examples required: Doors popularity, ordinary artist search, no artist match, empty title search, partial error fallback, injected unsafe prose and account scope. Record actual outputs/elapsed/status, not assumed model quality. Full existing offline/Ruff; broader live baseline remains14/16 with10/11deferred. Session-expiry issue23 remains separate.

## Tradeoff

Free generated prose improves flexibility but increases latency/cost and semantic risk. Separate grounding gate plus conservative deterministic constraints and mandatory notices reduce risk, do not guarantee correctness. Evaluate before accepting generated wording; maintain kill switch and natural fallback. Table rows remain complete and independently rendered. User approves final wording/UX and merge.
