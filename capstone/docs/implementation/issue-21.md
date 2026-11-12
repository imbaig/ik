# Issue21 — compact copy actions and honest capability explanations

Human feedback requested a compact inline copy action and lightly conversational answers that acknowledge unsupported qualifiers rather than silently substituting catalog lists. No popularity ranking exists in the current tools.

## Acceptance and implementation

- Gradio5.50 message-row/action sibling layout is a scoped two-column CSS grid. Each copy icon is36x36px with18px glyph beside its message, rather than a tall separate row. Native button labels/copy behavior remain intact; other buttons retain44px minimum. DOM measurements found copy top3px from its corresponding row top, desktop. Mobile browser verification remains required before completion.
- A bounded, deterministic capability rule recognizes popularity, most-popular (including observed poular typo), chart, streaming-count and selected ranking phrases. Applies only catalog/mixed requests. It is not a general semantic detector of every unsupported qualifier. Future tools/capabilities must update the rule and tests together.
- The application states it cannot determine popularity and can offer unranked catalog lookup. A narrowly scoped trusted system context asks existing specialists to do that lookup; no extra model call, guessed ranking or fact-generating prose is introduced. Existing action budget/ownership/memory remain authoritative. A no-tool failure remains an error and retains the limitation rather than falsely claiming results exist.
- Typed notices precede facts; successful ordinary fact replies receive a short introduction. Results remain exact structured tables. Text-node Markdown escaping leaves quotes literal (they are not attributes), fixing apostrophe entities in notices/user messages without relaxing HTML delimiter or Markdown escaping.
- Offline regressions use actual graphs/tools for The Doors11tracks, notice-before-table, no-tool error and no fabricated ranking, plus positive/negative capability patterns. All377tests passed; Ruff checks required on frozen revision. Existing multiline/CRLF/CR, security, ownership and lifecycle tests retained.

## Actual browser/live evidence

Initial candidate, real local provider: exact human phrase "i like the doors. name their most popular song" completed9.6s. Displayed the explicit no-ranking explanation, one Doors album and11unranked Doors tracks, no claimed most-popular song. Copy control measured36x36px,3px from message-row top, no extra toolbar row. Actual rendered apostrophes readable. Ordinary AC/DC follow-up and mobile checks in progress at authoring. These targeted checks are not a full live-suite or accessibility-conformance claim.

Existing phone session on7875 is preserved; candidate uses7876. Source stacks on #20/#16, does not overwrite v0. Independent read-only exact-SHA review/dispositions belong in PR conversation. Human visual acceptance/merge remains Imran's decision. Existing10/11 issues remain deferred until before demo; no general no-tool reliability fix is claimed.
