# Three candidate directions — no selection yet

Compare the [visual index](visuals/index.html). These are authored HTML/CSS mockups, not
Gradio screens or rendered screenshots. Each direction shows discovery and account at a
wide composition and narrow phone composition. Responsive behavior is proposed, untested.
No external fonts, logos or fabricated album covers. All example content is synthetic.

| Direction | Visual system and layout | Customer benefit hypothesis | Cost / risk | Human choice |
|---|---|---|---|---|
| A · Record Room | Warm paper, ink, forest accent; Georgia display + system body; 8px spacing; editorial masthead and context rail | Music discovery feels curated; account context remains visible | Two-column desktop rail must collapse predictably; more scoped CSS than B | Pending |
| B · Clear Conversation | Cool off-white, navy, blue action; system typography; 8px spacing; narrow readable transcript with inline cards | Simplest reading order and least context switching; aligns closest with existing chat | Rich card details may still require customization; verify real Markdown semantics | Pending; author recommends starting feasibility here |
| C · Reference Desk | Dark ink surfaces, warm amber action; system type; 4/8px density; summary strip and delineated result workspace | Repeat users can scan invoices and facts quickly | Sticky/workspace behavior and in-message actions can become fragile; dark state contrast needs independent testing | Pending |

Shared proposed tokens: body16px/1.5; heading28–40px; content measure<=72ch; phone gutters16px;
controls44px design target with >=8px gaps; minimal motion; visible text labels; data values
use tabular numerals. 44px is a product target, not the WCAG2.2AA minimum (see sources.md).
CSS tokens are candidates; only static foreground/background pairs can be calculated here.
Rendered contrast including focus, borders, disabled and any overlays must be measured locally.

The mockups purposely omit persistent cart, playback, album art and tabs requiring new
routing. C's workspace is visual grouping, not an implemented navigation feature. Buttons
in mockups have no application behavior. Catalog selection would submit a normal grounded
follow-up through the existing service after approval; no client-supplied customer identity.

Refine selected direction after local 1440x900 and 390x844 inspection, 320px reflow and
landscape/keyboard checks. Capture both discovery and verified invoice views; compare
against frozen artifact hashes, explain deviations, and get Imran's explicit direction decision.
