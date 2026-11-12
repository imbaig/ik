# v1 device dark-mode contrast repair

Reported by Imran: iPhone screenshot showed near-white text on cream alternating rows,
plus unreadable identity/status text. Author: Codex parent chat. 2026-11-12 UTC.

Root cause reproduced in actual deployed browser with `?__theme=dark`: paragraph text
computed rgb(245,245,244), while the custom page background stayed cream. Gradio dark
values were not overridden by the approved light theme settings. This is a UI defect.

Fix: exact source `e71bb641f0fe354279cd049762a3a0c13db96471` synchronizes dark theme
tokens with the approved light palette and explicitly pairs table foreground and both
alternating row backgrounds. The app presents a consistent light design regardless of
OS preference. No prompt, tools, ownership, provider settings or database changes.

Independent read-only reviewer `/root/aws_public_review` reviewed exact e71bb64 against
56ddf3b, no findings. Model metadata not captured; no additional skill used. Reviewer
checked theme token counterparts/references for cycles and requested real forced-dark
browser verification. Human report is accepted; human closure remains pending Imran.

Validation: 12 UI tests passed; full 431 offline tests passed; Ruff check/format passed.
[CI run 43151735190](https://github.com/imbaig/ik/actions/runs/43151735190) passed both
application and hosting jobs at exact e71bb64. UI-only scope does not require a new
model-quality evaluation; browser conversation checks are separately recorded below.

Deployment uses a new pinned image on the existing EC2 instance, retaining the quota
volume, secret mount, network rules, TLS timers and original stop deadline. Previous
image and service backup are retained for rollback. CloudFormation output still records
the initial launch source; `/version` is authoritative for the current runtime revision.
No PR merge or final submission approval is claimed.

## Actual deployed verification

`/healthz` reports ready with packaging revision e71bb64; Docker reports healthy.
The live browser forced-dark mode was active (`.dark` present) at 390px viewport,
with page scroll width 390px. After repair, header paragraphs compute rgb(32,42,37)
instead of rgb(245,245,244). A real AC/DC provider-backed query completed in 6.7s;
its disclosure expanded and both alternating rows were inspected. Foreground is
rgb(32,42,37); backgrounds are rgb(255,253,248) and rgb(245,241,232). Measured WCAG
relative-luminance contrast ratios: **14.55:1 and 13.13:1**. Screenshot visually checked.
Tables remain horizontally scrollable on narrow screens; physical iPhone verification
is requested from Imran rather than claimed from desktop emulation.
Evidence: operator workspace `outputs/aws-v1/contrast-before-dark-mobile.png`,
`contrast-after-dark-mobile.png`, and `contrast-metrics.json`. Existing release URL is
unchanged. Stop timer and public permissions were not edited. Human closure pending.
