open event from calendar click is not working well. 
the map kinda moves to make tooltip visible then jerks around.
the tooltip on the starting point should be in the window.

---

after selecting item on mobile the calendar should collapse

---

move the version marker to the i icon.
should look like this :
(i v18)

clicking expands info as normal.

---

in trace preset:
disable park bounds 
disable osm park polygon
disable osm tracks 

---


"disable" sfwda traced trails (extracted)
keep paper trail map
keep aop trail network merged truth.

---

max size for images works - good
as we zoom out it takes a second for this to be applied and the image "forgets" it needs to stop growing and overshoots then after it realizes it shrink down to its correct max size.

see if we can change the 

---

bake info from ellis cementary into our derived dataset.
stop showing other cementaries on the 9 patch in the 

---

# Disposition (2026-05-31 execution)

The raw list above is the user's QA notes (it ends mid-sentence — the on-disk
card was truncated; the companion `pwa_qa_2_plan.md` preserved the full
intent, incl. the cut-off "…in the **park preset**"). Worked from a clean
session against the **real** `website/index.html` (the plan's calendar code
anchors were garbled by the prior session's corrupted tool channel and did not
match the file — re-derived everything fresh). All changes in the master
working tree, **UNCOMMITTED**. Verifier: `mvp/scripts/playwright_verify_pwa_qa2.py`
(serve on **8002** — 8001 was a second agent's worktree review) — all items
below PASS, 0 console errors.

| # | Item | Status |
|---|------|--------|
| 1 | open-event jerk; tooltip must stay in window | **SHIPPED** — popup now pins to a fixed `bottom` anchor (was auto-anchor, flipping sides mid-flight = the jerk) + dropped the redundant 2nd corrective pan (`setTimeout` 1.2 s); one settle-time `panPopupIntoView` keeps it in-window. `gotoEventSession`. Device-confirm the *feel*. |
| 2 | mobile: collapse calendar after selecting an event | **SHIPPED** — the `calendarDays` click handler already folded search+hot on ≤760px; added `window.lrCloseCard('cal')` so the calendar itself folds too. |
| 3 | move version into the ⓘ → "(i v18)" | **SHIPPED** — `foldVersionIntoInfoControl()` relocates `#appVersion` into the bottom-left `.maplibregl-ctrl-bottom-left` (class `attrib-with-version`); reads "ⓘ v18", click still expands credits. Standalone chip under Install is gone. |
| 4 | trace: disable park bounds / OSM park polygon / OSM tracks | **SHIPPED** — `BUILT_IN_PRESETS.trace.toggles`: `showBoundaries`, `showOsmPark`, `showOsmTracks` → false. |
| 5 | disable SFWDA extracted trails; keep paper map + merged truth | **SHIPPED** — trace now turns the merged `aop-trail-network` ON (was OFF) with its per-difficulty colour (added a trace paint so Topo→Trace doesn't carry the flat-orange); SFWDA paper raster stays ON; the extracted `sfwda-trace-trails` stays OFF (already out of every preset); legacy demo `publish-trails` set OFF for a clean "truth" view. |
| 6 | image max-size overshoots on zoom-out | **NOT SHIPPED — device-only GL artifact.** The cap is ALREADY a per-frame GPU `interpolate ['zoom']` expr (`brandLogoIconSizeExpr`), and the layer already has `icon-allow-overlap`+`icon-ignore-placement` — there is **no** deferred re-clamp to remove (the plan's premise was wrong). The ~1 s lag/overshoot on zoom-out is the classic **GeoJSON-symbol parent-tile scaling**: zooming out briefly stretches the previous tile's icons until the lower-zoom tile re-tessellates. No safe headless-verifiable fix; the user's sentence is also cut off ("see if we can change the …"). Needs a device session + the rest of the instruction before churning a working cap. |
| 7 | bake Ellis cemetery into derived dataset | **ROUTED → `pwa_qa_data_bakes.md` "Item E"** (data-pipeline + source decision). Paired "hide other cemeteries" RETRACTED (see item 9). |
| 8 (plan only) | "calendar icons not centered in their circles" | **NO-OP — false premise.** The plan's `#calRefresh`/`#calCollapse` round icon buttons do not exist in the real file (corruption artifact). Nothing to center. |
| 9 (plan only) | "I like the cemeteries showing — let me think" | **HOLD** — user deciding cemetery visibility; no action. |
| 10 (plan only) | add a `region` on-map preset button | **NOT DONE — false premise.** There is **no** `region` entry in `BUILT_IN_PRESETS` (the plan conflated the maxBounds zoom-floor 13.74 with a preset). Adding a region preset is a new design fork (what layers/camera?) for the user, not a wiring tweak. |

**Version bumped to v19** (user call, 2026-05-31): `#appVersion` + `sw.js
VERSION` both → `v19`. NOTE: a second agent is concurrently on **v19** in a
worktree — reconcile at merge so the two v19s don't collide. Commit is the user's.