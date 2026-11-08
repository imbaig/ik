# Milestone 7 independent evaluation review

Reviewer `/root/milestone7_eval_cases`, separate read-only session; exact model metadata
not captured. Author is parent Codex `/root`. Fresh blind preference author is
`/root/milestone7_fresh_holdout`, who read only AGENTS, approved spec and business cases.
The first reviewer independently wrote v1 cases before inspecting any implementation;
subsequently reviewed harness and results. No reviewer made provider calls or changed
labels/code. Final human approver remains Imran; acceptance is pending.

| Finding | Severity | Accepted resolution | Independent disposition |
|---|---|---|---|
| EVAL-01 Incorrect requested row/count/order and invented prose could receive mechanical pass | P1 | Exact lookup SQL oracles with frozen expected args; strict renderer/prose checks; exploit regression; every transcript still requires semantic review | Exact18 oracle entries verified; invented-row/count/prose regression rejects |
| EVAL-02 Extractor existence/completed attempt was called validated live quality | P2 | Separate executed/completed/target fields; quality validation and milestone acceptance remain false pending review | Verified |
| EVAL-03 Reset, no-dispatch, union/isolation and semantic completeness gaps | P2 | Assert invalidated old handle, new unverified identity, no specialist traces, exact stored profiles; separate16-case semantic checklist | Mechanical fixes verified; final semantic run pending |
| MEM-QUESTION Question delimiters discarded before exclusion | P1 | Preserve delimiters; three direct regressions | Verified |
| EVAL-SUFFIX Arbitrary facts accepted as saved-preference suffix | P2 | Allow only literal observed trusted stored values; exploit regression | Verified |
| MEM-MARKER Predictable marker could bypass literal user evidence | P1 | Per-call nonce absent from all input/candidates, plus spoof regressions | Verified |

Agent findings above were accepted by author. Human-adopted/mandatory status is undecided;
no human waiver or closure is inferred. Prompt and filter changes retain executor identity
and tool ownership boundaries. Source snapshots distinguish evaluated revisions.

## Preference independent result review

- V1 corrected grading: TP23 FP0 FN6, p1/r0.7931; SC004 unmet. Casefold normalization
  corrects evaluator behavior without changing labels. First raw metric report preserved.
- V2: p1/r0.6667; SC004 unmet; misses retained. Set retired after inspection/tuning.
- V3: TP38 FP1 FN1, p/r0.97436; numerical target met, but actual hypothetical false
  positive documented and fixed. Set then retired to regression. No silent relabeling.
- V4: independently recomputed **TP38 FP0 FN1, p1/r0.97436; zero extraction errors**.
  All46 labels independently reviewed, no disputes. Sole miss: “I like Everything But
  the Girl.” Literal artist is valid; conservative negative-clause guard rejects But.
  Target met for this sampled set, not perfect/general semantic recognition.

V4 SHA256: 28fb442bf39eb625b1d41788028902637cf71a45d5c3550dcd966a1af5e34ae1.
Frozen memory/model/evaluator hashes verified. Earlier all-source snapshot precedes
agents-v3/telemetry edits; historical snapshot retained, later conversation snapshot
recorded separately. No retroactive rewrite of evaluated source hashes.

## Conversation independent result review

Run1: 2/16; run2:5/16; run3:12/16. All16 actual run2 and run3 transcripts reviewed.
Eight run2 and24 run3 tool records independently checked against SQL; no ownership/fact
mismatches. Run3 track24 was real but wrong for requested track1, correctly failed by
exact grader. Genre repeats identical with ten distinct artists. Account denial/injection
paths reached in run3: foreign invoice safely empty and substitution attack refused.

Run3 failures: wrong requested track; support contact not delivered; new taste misrouted
to recall with contradictory acknowledgment; quoted friend taste misrouted mixed. Reviewer
also flagged an unfulfilled hypothetical catalog subrequest even though the frozen
mechanical branch assertion was permissive. This requires semantic disposition rather
than interpreting a green mechanical check as completed business intent.

Fourth run remained12/16; after context framing, targeted3/4 passed. A subsequent full run reached15/16, with mixed-query action exhaustion. Final return guard ends a phase on exact framework ToolMessage/name/boolean metadata, without another provider call. Human-message and string-metadata spoofs were independently rejected. Final full independent suite:304 passed; no provider
calls by reviewer. SDK fault/security tests are deterministic evidence, distinct from
live provider evidence. Human acceptance, clean install, Docker and release remain separate.


## Final gate recommendation

Final live run **16/16 supported scenarios across47 responses**. Reviewer independently
read every transcript and checked all29 tool records against SQL: no factual, ownership,
requested-selection, ordering, count, truncation or envelope mismatches. ExactTrack1,
account-before-catalog, latest-owned-invoice contact/refund limits, preference union,
Gospel/Funk empty results, Soul61 tracks/four representative artists and customer isolation
verified. Foreign invoice access empty; attempted identity substitution returned only
verified A’s invoices. No fabricated invoice amounts/entity claims observed.

All final-run source manifest hashes matched at review. Reviewer full suite304 passed,
68 deprecation warnings; Ruff lint/format passed. Ready for Imran’s gate review, not
human approval. Conversation cases are now exposed regression data, not a fresh blind
measure of general reliability. Single model/single successful run is limited evidence.

Nonblocking observations retained: case07 unnecessarily includes owned purchased tracks;
case16 could explain refusal to switch identity more clearly. Both retain trusted customer
ownership. No blocking findings remain in reviewed milestone scope.
