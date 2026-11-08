# Sources, provenance and actual use

Date: 2026-11-08. Source claims are separated from author proposals. No usability or
accessibility certification, customer research results or rendered QA is claimed.

## Primary UX/accessibility sources

Direct runtime HTTPS attempts to nngroup.com, microsoft.com, w3.org, react.dev and
fastapi.tiangolo.com failed with proxy tunnel403. No network change was requested. The
coordinating parent retrieved primary-source text on November8 through its web tool;
that text was available for inspection here through web-tool output as well. These are
textual source reads, not browser rendering or runtime feature tests. Gradio website
fetches through the web tool failed; installed version-specific source was used instead.

| Primary source | Text actually used | Design application / observable check |
|---|---|---|
| [Nielsen heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) | General principles for status, familiar language, control, consistency, prevention, recognition, concise design and error recovery | S02 visible busy state; plain labels; S07/08 exits; repeated control order; bounded retries; grouped facts; S10 actionable failure. Proposed checks AC-01/03/06/10 |
| [Microsoft HAX overview](https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/), [Design Library](https://www.microsoft.com/en-us/haxtoolkit/library/) | 18 evidence-based guidelines across initial interaction, use, failure and ongoing adaptation | G1/2 capability and limitation disclosure; G8 dismissal; G9 scoped correction; G10 graceful fallback; G11 refusal rationale; G12 context; G16 consequences. AC-03/06/07/08/09; no inferred preference learning |
| [WCAG2.2 Recommendation](https://www.w3.org/TR/2024/REC-WCAG22-20241212/) | W3C Recommendation dated December12,2024; technology-independent testable criteria | Proposed AA target; selected criteria/checks in acceptance.md, whole-page review still required before any conformance claim |
| [WAI reflow understanding](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) | Narrow presentation without losing ordinary content/functions | Inspect320 CSSpx and400% zoom; prefer vertical lists over wide invoice rows. No blanket table/diagram exception for whole page |
| [WAI target size understanding](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | AA24x24 CSSpx minimum or documented exception | Product target44px controls; test actual bounds/spacing; distinguish stronger target from AA minimum |
| [React official setup](https://react.dev/learn/creating-a-react-app), [from scratch](https://react.dev/learn/build-a-react-app-from-scratch) | Framework recommendation; Vite as a documented build-tool option with app-owned data/routing concerns | Alternative is supported general ecosystem, not existing project integration; added API/testing/build cost remains explicit |
| [FastAPI custom responses](https://fastapi.tiangolo.com/advanced/custom-response/) | HTML/JSON and generator-based StreamingResponse | Alternative API delivery capability, not proof of safe session/auth or application token streaming |

## UI UX Pro Max — pinned, text-only aid

Repository: [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill).
Exact inspected revision: **`4f2dbb67e64969a9a30ab00742f2d55d66ddec2b`**.
[Instruction file at that revision](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/4f2dbb67e64969a9a30ab00742f2d55d66ddec2b/.claude/skills/ui-ux-pro-max/SKILL.md).
Cloned into ignored `.cache/design-sources/ui-ux-pro-max` for inspection only. No global
installation, project dependency changes, third-party script execution, search/generator
run, font download, logo/image generation or provider call. No generated search results.

Inspected: README; `.claude/skills/ui-ux-pro-max/SKILL.md`; `references/quick-reference.md`
(accessibility, touch, layout sections); `references/pro-rules.md`; first UX CSV rows and
selected styles CSV rows; supplementary `cli/assets/skills/design/SKILL.md` (broad routing,
not followed). File hashes are in source-manifest.json. Python/search/design-system scripts
were **not inspected or run**; no safety/quality assertion about executable code is made.

Actually adopted as general text guidance: labeled inputs, text+status indicators, logical
hierarchy,8px spacing, reduced motion, touch access without hover, readable responsive text,
no fabricated artwork. A/B/C palettes and layouts were authored for this task, not outputs
of the skill's search or design-system scripts. Generic style rows are inspiration only.
Rejected/defaults not applied: forced smooth scroll, assumed certification from a style,
voice/gesture-only UI and provider-backed logo generation. Accessibility standards and
trusted store data take precedence over aesthetic advice. The skill lists React and other
stacks but **no Gradio stack**; no Gradio-specific support or migration justification claimed.
User explicitly authorized inspected-text use without scripts, so its script workflow was
not executed. This is an assessment and bounded manual use, not full skill execution.

## Gradio evidence

`uv.lock` resolves5.50.0; inspected source is the existing installed5.50.0 distribution at
`.venv/lib/python3.12/site-packages`, not a globally installed or newly provisioned version.
`source-manifest.json` includes hashes for metadata, Blocks, Chatbot, State, Row, Column,
Button, Markdown and themes. Relevant evidence:

- Blocks constructor: `theme`, `css`, `head`; component IDs/classes are explicit surfaces.
- Chatbot: `render_markdown`, `sanitize_html`, `allow_tags`, `height`, `layout`, `autoscroll`.
- State: `time_to_live`, `delete_callback`; these are lifecycle features, not authentication.
- Row/Column: min-width/wrapping/layout properties; no tested keyboard/mobile guarantee.
- Existing UI generator and queue use status/final yields, interactive flags and concurrency.

Initial attempted raw GitHub tag URLs returned404; upstream tag lookup returned no match.
No version-specific upstream source was substituted silently. Installed source is the
version-specific API evidence, not proof of rendered semantics. Hashes support local
reinspection; no dependency/source files from the distribution are copied into this PR.

## Human-review fixture/copy revision

The original synthetic records are superseded by [sample-fixtures.json](sample-fixtures.json),
extracted from the existing checksum-verified public Chinook SQL using read-only Database and
bound domain tools with fixture context1. No LLM, verification model, UI session, provider or
credential was used. source-manifest.json records SQL revision/hash, tool names and fixture
file hash. New customer copy is authored; verification, loading/error and preference outcomes
remain simulations, labeled outside product areas. This is not live application evidence.
The new walkthrough is first-party HTML/CSS only, with no scripts or external assets. Its
navigation and layout still need actual local browser inspection. No third-party skill code
was run in this revision; the previous UI UX Pro Max pin and inspected-text limits remain.
