# Issue 19: responsive history and glanceable results

Imran requested browser-height conversation history and collapsible, readable tables instead of numbered/bulleted records. This feedback authorizes the presentation change. No service, prompt, identity, tool, database or evaluation behavior changes.

## Behavior and acceptance

- Chat history uses viewport-relative CSS height with a 260px minimum, desktop offset340px/mobile280px. At1280x900 observed560px; at1280x1200 observed860px. Transcript scrolls within that region; small windows can still scroll the page.
- All nine fact types use semantic tables with captions and scoped column headers. Source fields and row order, exact string amounts, nullable values, counts and truncation/sampling summaries remain available. No amounts or currencies are inferred.
- More than five returned rows collapse by default behind native details/summary. Small results remain directly visible. Disclosure works with Enter; results count and sample warning remain outside the collapsed region. This changes presentation only, not the existing bounded result limit.
- Table regions scroll horizontally within the chat bubble on narrow viewports. Mobile390px document width measured390px; expanded table scroll426px inside220px region. Native keyboard focus retained. This is not a VoiceOver/conformance claim.
- Table cells are escaped raw HTML data; Markdown syntax cannot become links/headings, and encoded CR/LF/tab avoid Markdown block parsing. Every actualSQL field/value is checked by HTMLParser regression; sparse/future fields retained. HTML sanitizer and disabled arbitrary custom tags/downloads remain unchanged.
- Actual live Queen query returned20/45rows. Expanded browser table correctly displays apostrophes (It's A Hard Life and I'm Going Slightly Mad); addresses issue17 in table facts. User-message/notice Markdown escaping remains unchanged.
- Related issue18 header now stacks on mobile rather than squeezing store title into three columns.

## Evidence

364 offline tests passed (Python3.12 existing locked environment); Ruff check/format passed. No extra dependencies/model calls. Actual browser used real provider and verified database, not P0 callbacks. Browser snapshots confirmed headers/cells/native disclosure, Enter toggle and viewport measurements. Screenshots local outputs/issue-19; not committed. Independent exact-SHA review pending at authoring; report/dispositions in PR conversation.

The running initialv1 on7874 and v0 on7872 remain unchanged; this change is previewed separately on7875. Dependencies: integration PR16 must reach main first. Only Imran merges and accepts visual design. Existing issues10/11 remain deferred until before demo. Broad live lifecycle/VoiceOver/Docker deployment checks are not claimed by this presentation-only update.
