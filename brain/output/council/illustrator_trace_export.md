# Council receipt — satellite → Illustrator trace export + round-trip

Date: 2026-06-14
Diff under review (my 6 paths): `mvp/scripts/export_illustrator_trace.py`,
`mvp/scripts/import_illustrator_trace.py`, `brain/tasks/14_illustrator_trace/satellite_illustrator_export.md`,
`brain/handoff/session_context.md`, `brain/search_map.md`, `brain/output/illustrator_trace/*`.
Card: `tasks/14_illustrator_trace/satellite_illustrator_export.md`.
Tier: core-three + Mason (new mvp/ tooling, hand-rolled projection, round-trip claim).

## Verdicts

- **Witness — clear.** Re-ran the round-trip and parsed the SVG independently; all
  four claims reproduce (projection sub-mm + doc bbox inside raster; alignment on
  imagery; 120/120 @ 0.911 cm; 4 layers / 1 image / all name channels). Notes:
  "8.8 MB"→9.2 MB stale (fixed); "squarely on rooftops" overstated pixel precision
  (softened to gross registration).
- **Quartermaster — clear.** Reuse real (`path_points`/`parse_transform`/`apply`
  from `import_trace_svg`; projection from `export_illustrator_trace`); hand-rolled
  UTM justified (no pyproj/GDAL/Docker on box, confirmed); gold `_meta` stamping
  correctly deferred to `export_gold_trail_network.py`; C1/C2/C6 greps pass.
- **Mason — andon → fixed → clear.** Andon: `import_trails` rebuilt props from 5
  keys, dropping 12 of the gold file's 17 (color/maturity/permission/…); the card's
  claim that `export_gold_trail_network.py` rescued this was false. Plus a latent
  `ai_unescape` leading-`_` bug and a function-local `import re`.
  **Fix:** export embeds `data-fid` (stable id); `import_trails` re-merges the full
  prior gold props by `data-fid`→name and overlays only name+geometry (no match →
  thin "needs review"); `ai_unescape` strips the digit-guard before decoding `_xHH_`;
  `re` moved to module top. **Re-review clear** — in-memory round-trip: 120/120 keep
  `maturity=gold` + color/permission; `ai_unescape(ai_escape("_15"))=="_15"`; served
  file untouched.
- **Warden — clear in isolation; andon on the commingled tree.** My 6 paths are
  on-farm, git-gate-clean (nothing committed/staged, served gold byte-identical to
  HEAD, importer not run against real data). BUT the working tree also carries a
  **concurrent session's** unreviewed changes — `website/js/viewer_core.js`,
  `website/js/main.js`, `website/index.html`, `website/sw.js`,
  `website/data/aop_landcover*.geojson`, `mvp/scripts/simplify_landcover_vegetation.py`,
  `playwright_verify_landcover.py`, + `brain/output/obs5_*`/`v5_*`/`observe_five.py`/`verify_five.py`
  ("five-item review" task). Coord board has no active claim posted.

## Round 2 — user "no drawn text" correction (re-review)

The user: *"the text of the layers is … making its way into the document as text
items. the Front office should be a polygon named correctly as an object name not a
physical document object."* Fix: removed all `<text>` labels; each feature is now ONE
named geometry object (`<path>`/`<circle>`, no wrapper group) carrying the name on
`id`/`inkscape:label`/`serif:id`/`<title>`; importers rewritten to walk named
elements. Re-reviewed by the two seats the change touches:

- **Witness — clear.** Re-parsed the regenerated SVG: 0 `<text>`/`<tspan>`, 4 `<g>`
  total (= the 4 layers, 0 wrapper groups inside categories), "Front Office" = one
  named `<path>`; round-trip 120/120 @ 0.91 cm, `maturity=gold` 120/120; served file
  SHA identical before/after (never ran main()).
- **Mason — clear.** Restructured `walk(layer)` traversal correct (120 paths, no
  double-count/miss, transforms compose), non-limiting, no dead code (old
  `named_group`/`label_at`/`.lbl` gone), `_ring` reuse clean, provenance carry intact.

## Steward decision

My work is council-clear (Witness·Quartermaster·Mason clear; Warden clear-in-isolation).
**No `.council-cleared` marker written** — the marker hash spans all of
`website/`+`mvp/`, which includes the other session's unreviewed code; clearing
would falsely certify it. The git gate is the user's; the two sessions' work needs
to be gated/committed with the user's knowledge (flagged in the handoff).
