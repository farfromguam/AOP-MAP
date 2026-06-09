# Council done-review — shadow-attribute resolution slice A3 (2026-06-09)

**Slice:** Path A / A3 — building / cemetery / visitor name + subtitle convergence (delete the runtime
`poiIndexLookup` blurb join; building name = facility name, address → facet; read canonical).
**Tier:** full six (live-viewer JS + served reference data).
**Diff under review (A3 increment):** `mvp/scripts/rebake_canonical.py` (`n_building` = facility_name
preferred; `facets.address`), `website/js/main.js` (building/cemetery/visitor `listRow` + building
`rowLabel` + building search read canonical; `poiIndexLookup` DELETED), `website/js/panel.js` (building node
label = canonical name, detail = address), re-baked `aop_buildings`/`aop_cemeteries`/
`aop_visitor_context_callouts.geojson`, new verifier `mvp/scripts/playwright_verify_shadow_a3_poi_name.py`,
the card + the 4 audit-catalog DONE-A3 annotations.

**RESULT: FULL SIX CLEAR.** (No andon this round — the catalog was annotated and the handoff/receipt written
before the Scribe reviewed, so the record was complete on first pass.)

-----

SEAT: witness
VERDICT: clear
ISSUE: none
EVIDENCE: Re-ran `playwright_verify_shadow_a3_poi_name.py` against the live viewer (:8001) — PASS, exit 0, 0
console errors. The verifier OBSERVES live surfaces (fetched served geojson; rendered `#searchResults`
inner_text — 'pavilion'→Pavilion, '1010 ellis'→Pavilion alias; panel `.item-select` text; right-panel
`.field-input[data-field="name"]` `.value`=="Pavilion") — not a read-site trace. `grep` poiIndexLookup → 0
callers; the `- function poiIndexLookup` + 3 callers are deleted (not relocated); `fetchPoiIndex`/`poiIndex`
kept only for `poiGroupLabel`/`poiGroupOrder` (POI-tab group taxonomy = config). `node --check` clean.
Served data: Pavilion name="Pavilion" + facets.address="1010 Ellis Cove Road" + description; private 665
keeps the address as name (no crash). A1 + A2 verifiers re-run → both PASS.

SEAT: quartermaster
VERDICT: clear
ISSUE: none
EVIDENCE: `poiIndexLookup` 0 callers / 0 defs in website/js (deleted, not relocated); the per-feature
blurb+revisit join now lives ONCE in the bake (`poi_match`/`join_name_desc` → `description` +
`facets.revisit_note`); cemetery/building/visitor listRows read those fields. `fetchPoiIndex`/`poiIndex`
retained only for the group taxonomy (`poiGroupLabel`/`poiGroupOrder`). `n_building` mirrors
`n_trail`/`n_cell`/`n_osm` — no parallel name path; address→`facets.address`. Verifier reuses
`playwright_base.viewer_url`. C1 = 0 non-comment `layerKey === '`; C6 = 0 `class [A-Z]`, one registry, no new
editor *.html; C2 = one `collectStarredDestinations(` with both renderers as thin consumers.

SEAT: mason
VERDICT: clear
ISSUE: none
EVIDENCE: Non-limiting (C5): traced building/cemetery/visitor read-site edge cases in node — private
building (no facility_name) renders with the address as name (`first(NAME_KEYS)` fallback in `n_building`),
facility renders "Front Office", cemetery/visitor with no description render with blurb null (not dropped);
no filter/throw/reject added; blurb/revisitNote/detail are `||` safe-default fallbacks. Additive: facility
canonical name="Front Office" with the street address preserved in BOTH `facets.address` AND
`_original.name`; raw keys retained; nothing dropped/overwritten. Clean deletion (prose pointer, not
commented-out code). `n_building` idiomatic; `facets.address` emitted only `if props.get("address")`. No
literal layerKey dispatch — facets() reads props declaratively. `node --check` clean; `rebake --check` no
write. Note (not a gate): facets.address also lands on cemeteries (any feature with an `address`) — additive
+ unread by the cemetery read site; the twin-id cemetery collision is the held Path-B root, still renders.

SEAT: warden
VERDICT: clear
ISSUE: none
EVIDENCE: Every A3 hunk traces to the card: main.js building/cemetery/visitor listRow + building rowLabel +
facility search + `poiIndexLookup` deletion (card lines 234-236), panel.js buildings node (line 236). The
challenged `rebake_canonical.py` `n_building` + `facets.address` + 3 re-baked geojson ARE the card's own A3
directive verbatim ("building prefers facility_name; address → a facet", line 234) — a name promotion is a
bake change by construction, not creep. The remaining bake machinery + other re-baked files belong to A1/A2
(own cleared receipts) and ride the one batch. Git gate UNTOUCHED: HEAD `e34c1b8` (no commit); sw.js +
index.html `v59` unbumped; DONE blocks record bump+commit as OWED. A1/A2 directives intact; the 4 A3 catalog
ids carry append-only DONE-A3 annotations (original text preserved). Noticed-not-done: the cemetery
address-facet breadth (additive, harmless); the pre-existing feature_list Move failure (documented).

SEAT: scribe
VERDICT: clear
ISSUE: none
EVIDENCE: A3 DONE block records the live-DOM verifier + RESULT: PASS + the owed git gate (rides the one
batch bump + commit). All 4 A3 Closes ids grep-resolve to one catalog home and carry `DONE A3 (2026-06-09)`
annotations mirroring A1/A2's form; coverage line A3=4 consistent. The `aop_copy_registry.json` note was
fixed in A2. Handoff updated (A3 done; NEXT pointer → A4). Voice plain/terse, references concrete, no
misspellings.

SEAT: steward (chair)
VERDICT: clear
SYNTHESIS: A3 finishes the reference-layer name/subtitle convergence — the building "Pavilion" now reads one
canonical field on every surface (the second shadow fork after Launchpad), descriptions come from the baked
field, and the per-feature poi-index join is deleted (the group taxonomy correctly kept as config).
Additive, non-limiting, on-farm, git gate untouched, observed live. Owed remains the user's: the one batch
`sw.js`/`#appVersion` bump + commit. NEXT in the loop: A4 (render-derived display unification — one
display-name helper, kind chips from canonical kind, baked source string; + the re-homed
publish-confidence-status display map).
