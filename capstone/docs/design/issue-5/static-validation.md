# Static validation record — initial and human-revision evidence

Author self-check, not independent approval. Revision: the commit containing this file,
identified by final exact SHA in the draft PR. Date2026-11-08. No application code changed.

Checks executed with Python standard library over this directory and the proposed002 packet:

- Parsed all5 SVG files as XML; each has title, description and viewBox.
- Parsed all5 HTML files; checked language, viewport, title, duplicate IDs, local link
  targets and same-file fragment targets. No scripts or remote src/href resources.
- Parsed source-manifest.json and checked Markdown relative file links.
- `git diff --check` passed before freezing the first review input.
- Scope inspected: only new docs/design/issue-5 and specs/002-customer-experience files;
  no baseline001, approval snapshots, application/dependency or adjacent coursework edits.

The initial audit covered25 files (before adding this record). The final repeat is recorded
in the PR. The author's standard-library checker lives in ignored .cache; it is not a
third-party script or application test. Independent reviewers may repeat structural checks
with their own parser or local inspection. These checks detect syntax/link problems, not
rendered overflow, usability, semantic completeness or browser/accessibility behavior.

## Preliminary color-pair arithmetic

Author calculated standard sRGB relative-luminance contrast on these literal pairs. This
covers selected text tokens only, not rendered pixels, focus, borders, states or overlays.

| Pair | Foreground / background | Calculated ratio |
|---|---|---|
| A body | #202a25 / #f5f1e8 | 13.13:1 |
| A secondary | #4c5a51 / #fffdf8 | 7.15:1 |
| A action | #ffffff / #245b45 | 7.90:1 |
| B body | #18283f / #f4f7fc | 13.83:1 |
| B secondary | #485a70 / #ffffff | 7.07:1 |
| B action | #ffffff / #204fbb | 7.25:1 |
| C body | #f2f5f7 / #14232d | 14.66:1 |
| C secondary | #c1cdd6 / #1d303e | 8.40:1 |
| C action | #14232d / #f4c77b | 10.17:1 |

No rendered visual QA or accessibility pass is claimed. Local coordinator must render the
artifacts; implemented controls and complete relevant A/AA criteria need actual testing later.
No application pytest/live-model run was needed for this design-only revision; no providers
or credentials were used. Any future application slice must run its required checks.

## Revision for human findings H5-01–03

Authored a self-contained HTML/CSS walkthrough, realistic copy, public pinned fixtures,
connected A/B/C states and revised desktop/mobile SVGs/atlas. No JavaScript or third-party
code. Original26-file check above is historical; updated counts and checks are recorded in
PR6 at the frozen revision. Read-only fixture extraction through existing domain tools is
new evidence, not a provider/application-UI run. Source manifest pins fixture hash/provenance.

Static recheck includes every same/cross-file mock fragment, reset Keep origins, initial
screen absence of conversation/results, fixture-derived exact amounts/counts, no remote
resources/scripts, XML bounds, and review-note separation from product areas. These detect
source/route errors only. No rendered navigation, visual layout, desktop/mobile or accessibility
QA pass is claimed. Local coordinator must provide actual preview before completion.

Updated author recheck before freezing:32 files,6 SVG,6 HTML,3 JSON. Standard-library
checks passed for all local HTML/SVG fragments,51 fixed states per direction, no scripts or
remote resources, empty S01 separation, fixture values in result/detail scenes, verified
shortcut, mixed-only catalog exit, reset origins and busy controls. Numeric SVG anchors/
rectangles stay in the viewBox; text extents and rendered layout are untested. Source-only
product DOM checks found no listed structural filler or review-note class inside screens.
No rendered navigation/visual/accessibility pass or human closure is inferred.
