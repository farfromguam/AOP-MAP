# Editor is the viewer

TL;DR: The AOP editor is `website/index.html` with editing modes layered on, not a separate page.

#ai_rules #editor #viewer #scope

-----

`northstar/map_northstar.md` says Website V2 is submission and moderation on top of V1. V2 is V1 with more controls, not a fork.

When scoping drawing, submission, or moderation work, add the feature to the existing viewer — new controls, new toggles, new modes on the same `map` instance. Do not propose a second HTML file, a second app, or a parallel editor surface unless the user asks for separation.

This applies to the POI editor, region-callout positioning, on-map logos, and anything else that edits map state.
