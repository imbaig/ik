# Persistent contextual suggestions — user-authorized UX feature26

Remove message-copy controls; no rubric requirement. Retain three editable starter questions throughout chat and place them beside the composer, adapting to latest successful facts. No extra model call, automatic send, fabricated catalog relation or authority. This scoped human request authorizes implementation; final UX/merge acceptance remains pending.

## Layout/wireframe

First visit:
[Welcome: What would you like to explore?]
[Show albums by AC/DC] [Show my latest invoice] [What music preferences have I saved?]
[Editable message] [Send]

After AC/DC album results:
[Conversation: intro + collapsed Albums result]
[Status]
[Show tracks by AC/DC] [Find songs with love in the title] [Show my latest invoice]
[Editable message] [Send]

After verified invoice headers:
[Conversation: owned invoices]
[Show the items on invoice382] [Who can help with invoice382?] [What tracks have I purchased?]
[Editable message] [Send]

## Architecture and rules

Pure presentation/suggestions.py consumes immutable ViewState/fact envelopes. Gradio adapter updates three labels and persistent row. First question replaces the previous single invoice-followup control (no duplicate fourth button). Output contract15slots, existing slots0–10 unchanged;11firstsuggestion,12rowvisibility,13/14otherlabels. Names bounded80chars/no HTML/controlcharacters, IDs positive observed SQL references. Button labels are editable query text, never authentication input. Only server-derived verified state permits owned-invoice references. Tool execution independently revalidates ownership after explicit Send.

During busy, keep labels and disable all suggestions; during verification keep row visible but disable to prevent suggestions being entered as identifiers. Callback checks active/busy/waiting server binding and only returns a draft update. Reset restores starters and clears old invoice references. Empty catalog results offer only catalog alternatives. Queries are suggestions, not promises of availability. Supported artist/track lookups and invoice/support tools only; no checkout/playback or unsupported album-to-track API invented.

No copy button or copy-only toolbar grid; restore normal message width. Keep native semantic collapsed tables, escaping and focus styles. Three buttons wrap naturally near composer on phone; minimum44px targets retained. Existing model/narration/identity/memory/SQL/control budgets unchanged. UI-only change: no new model-evaluation requirement, but actual browser/live app smoke checks verify rendering and interactions. Regression tests cover actual SQL context, unverified vsverified, empty/malicious data, busy/waiting/reset/expired binding, no automatic dispatch and actual Gradio callback mapping. Independent read-only exactSHA review and screenshot evidence required. Currentpreview7877 remains until candidate checks complete; updating requires reload/freshconversation.
