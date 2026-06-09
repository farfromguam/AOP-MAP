# Council done-review — shadow-attribute resolution slice A2 (2026-06-09)

**Slice:** Path A / A2 — trail read-site convergence (the "Launchpad" fix: delete the runtime catalog
join, read the canonical field A1 baked).
**Tier:** full six (live-viewer JS; the bug that opened Sprint 09).
**Diff under review (A2 increment over the cleared A1):** `website/js/main.js` (trail rowLabel / listRow /
popup / search read canonical; `trailCatalogLookup`+`fetchTrailCatalog`+`trailCatalog` DELETED),
`website/js/panel.js` (`aopTrails` label reads canonical name), `mvp/scripts/rebake_canonical.py`
(`facets()` folds catalog `length_mi`/`tr`→`onx_tr`/`connects`), `website/data/aop_trail_network.geojson`
(re-bake), `website/data/aop_copy_registry.json` (stale catalog-note fixed),
`mvp/scripts/playwright_verify_shadow_a2_trail_name.py` (new live-DOM verifier), the card + audit annotations.

**RESULT: FULL SIX CLEAR** (1 Scribe andon, folded → re-cleared: A2 Closes ids annotated in the catalog,
this receipt written, the stale handoff "NEXT: A2" pointer fixed).

-----

SEAT: witness
VERDICT: clear
ISSUE: none
EVIDENCE: Re-ran `playwright_verify_shadow_a2_trail_name.py` twice against the live viewer (:8001, HTTP 200)
— PASS, exit 0, 0 console errors. The verifier reads genuine running surfaces, not re-derivations:
right-panel Name input `.value` via `.field-input[data-field="name"]` == "Launchpad"; rendered
`#searchResults .search-item` text names "Launchpad" + shows the baked description; rendered `aopTrails`
`.item-select` row == "Launchpad · easy" (regression trail #15 still "Trail 15"). Independently triangulated
the map-label surface with `querySourceFeatures('aop-trail-network')` (renderer-held tile data) + the live
source `serialize().data` — trail #1 == "Launchpad" in the in-memory source the `aop-trail-network-labels`
layer paints `['to-string',['get','name']]` from. `grep` → 0 refs of trailCatalogLookup/fetchTrailCatalog.
`node --check` clean on both JS files. A1 verifier still PASS. Hardening note (non-blocking): Surface-1 has
a disk fetch-fallback; closed the gap by reading querySourceFeatures directly.

SEAT: quartermaster
VERDICT: clear
ISSUE: none
EVIDENCE: The bake-time join (`rebake_canonical.join_name_desc`/`facets`) is the ONE join; A2 DELETES the
viewer's second resolver (`trailCatalogLookup`/`fetchTrailCatalog`) rather than relocating it (0 refs in
website/js). C2: one `collectStarredDestinations(` (main.js:1148), `pushRow(` = 0, trail `listRow` stays 1
of 6 spec strategies fed via `spec.listRow`. The new verifier imports `playwright_base.viewer_url`
(`wait_until="load"`, no networkidle/queryRenderedFeatures) — thin adapter. C1 non-comment `layerKey === '`
= 0; `class [A-Z]` = 0; no new editor *.html. `renderPoiTabIfActive` (the call that lived inside the deleted
fetchTrailCatalog) still defined + 7 valid callers — no orphan. (Flagged the stale `aop_copy_registry.json`
note for the Scribe — since fixed.)

SEAT: mason
VERDICT: clear
ISSUE: none
EVIDENCE: Traced all six read-site edge cases in node — `{name:"15"}`, `{name:"Launchpad",trail_number:1}`,
`{name:null,trail_number:32}`, `{}`, `{name:"Riot Hill"}`, `{name:"1",trail_number:1}` — every path returns
a string, no throw, no row dropped; `revisitNote`/`status`/`source` are `||` safe-default fallbacks, never
gates; `filterLayers:[]` keeps all 120 edges rendering. Deletion clean (0 refs; the replacement is a prose
pointer, not commented-out code). `facets()` additive (116/120 carry a facets block, 4 don't; each key under
an `if present` guard). Dropped onX-license footer was genuinely always empty (0 trails carry
`license_on_text`). Dispatch stays declarative (trail read sites are properties of the `trails` spec). Craft
note (non-blocking, pre-existing): left-list `rowLabel` returns bare "15" for an uncatalogued numeric trail
while popup/panel read "Trail 15" — cosmetic prefix, the name itself agrees; unchanged by A2.

SEAT: warden
VERDICT: clear
ISSUE: none
EVIDENCE: HEAD still `e34c1b8` (no commit); `sw.js`/`index.html` v59 unchanged, absent from the diff (no
bump — OWED). Every main.js hunk traces to an A2 directive (delete-join @504, rowLabel @2845, listRow @2880,
search @9142/@10093+, popup @9165); panel.js single hunk @607 is the `aopTrails` node (card line 186). The
`rebake_canonical.py` `facets()` + `aop_trail_network.geojson` re-bake are the data-side half of "delete the
runtime catalog join" — committed-HEAD main.js read `cat.length_mi`/`cat.tr`/`cat.connects` from the join,
and A1 baked only `difficulty`, so those popup fields had no baked home until A2 gave them one; deleting the
join without baking them would have dropped popup rows. Re-bake additive (trail #1 name="Launchpad",
`_original.name="1"`, count 120==120, A1 directives intact). A3's `poiIndexLookup` untouched. Onx-license
footer removal is inside "repoint the popup" (recorded). (Flagged the missing receipt → now written.)

SEAT: scribe
VERDICT: clear (after 1 andon folded)
ISSUE: none (was: A2 Closes ids unannotated in the catalog; this receipt missing; stale "NEXT: A2" in the
handoff)
EVIDENCE: A2 DONE block records the live-DOM verifier + RESULT: PASS + the owed git gate; both Closes ids
grep-resolve to one home and are now annotated `DONE A2` in `shadow_attributes_audit.md` (mirroring A1's
form); coverage line A2=2 consistent; pre-existing feature_list failure honestly noted; voice plain/terse,
references concrete, no misspellings. Fold: catalog annotations added, this receipt written, and the handoff
"NEXT" pointer corrected from A2 to A3.

SEAT: steward (chair)
VERDICT: clear
SYNTHESIS: A2 closes the exact fork that opened the sprint — "Launchpad" now reads from one canonical field
on every surface, observed live on four of them, with the runtime join deleted (not relocated) and
number-search preserved (AOP IDs by number). The bake-facets extension is correct boundary work, not creep:
deleting the join required the data to be complete. Non-limiting, additive, on-farm, git gate untouched. The
single andon was record-completeness, folded. Owed remains the user's: the one batch `sw.js`/`#appVersion`
bump + commit. NEXT in the loop: A3 (building/cemetery/visitor name+subtitle convergence; delete
`poiIndexLookup`).
