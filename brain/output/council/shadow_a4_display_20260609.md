# Council done-review — shadow-attribute resolution slice A4 (2026-06-09)

**Slice:** Path A / A4 — render-derived display unification (one drawn-POI display-name helper; seed POI
kind baked to controlled "poi" with "Pavilion" as a category facet; Source-tab File reads a baked
`source_file`; confidence/status chips relabel known source-register values and pass out-of-vocab through).
**Tier:** full six (live-viewer JS + served reference data + a controlled-vocabulary display map).
**Closes (4 catalog ids):** `poi-display-name-three-derivations` · `seed-poi-kind-is-propernoun-category` ·
`source-file-shown-as-derived-runtime-value` · `publish-confidence-status-off-vocabulary` (re-homed A1→A4).
**Diff under review (A4 increment):** `mvp/scripts/rebake_canonical.py` (seed `kind=lambda p: p.get("kind")
or "poi"`; per-feature `source_file` on named non-machine layers; `_schema.json` doc), `website/data/_schema.json`,
`website/js/main.js` (one `poiDisplayName` helper feeding listRow.name + rowLabel; the three `editor-poi-*labels`
`text-field`s become `coalesce(name,category,'POI')`), `website/js/panel.js` (`fileForItem` prefers baked
`source_file`; `CONFIDENCE_DISPLAY`/`STATUS_DISPLAY` + `vocabDisplay` wired into `provenanceFields`), the named
served `*.geojson` that gained `source_file` + the seed POI kind, the new verifier
`mvp/scripts/playwright_verify_shadow_a4_display.py`, the card A4 DONE block + the 4 audit-catalog DONE-A4 annotations.

**RESULT: FULL SIX CLEAR.** No andon this round — the card DONE block, the 4 catalog annotations, the handoff,
and this receipt were written before the Scribe reviewed, so the record was complete on first pass. (Two
non-blocking advisories were carried to the Scribe/Steward, not bounces — see below.)

-----

SEAT: witness
VERDICT: clear
ISSUE: none that blocks A4 — every doneness claim is backed by an observation of the real running system,
re-run by the seat, not narration.
EVIDENCE: Re-ran `playwright_verify_shadow_a4_display.py` on the live :8001 viewer — RESULT: PASS, exit 0,
0 console errors. It reads genuine LIVE DOM/state (the `editor-poi` map SOURCE feature name; the rendered
`#poiList .poi-row-name`; the `[data-node-id="editorPois"] .item-select` row; the right-panel
`.field-input[data-field="name"]` value; the Source-tab `.field-static` pairs) and asserts agreement — not a
read-site re-derivation. All four surfaces == "AOP Pavilion"; Kind chip == "poi"; Details facet == "Pavilion";
Source-tab File == "aop_buildings.geojson" (never "unknown"); Status "raw context"→"Raw context"; off-vocab
Confidence "medium" passes through. Independently backed up + ran the SHIPPED `rebake_canonical.py` and
byte-diffed: served files byte-identical to a fresh bake (idempotent for real), `_schema.json` differs only by
the date stamp; restored the tree to its starting state. The Mason-binding assertion calls the production CONFIG
lambda (`{'kind':'trailhead'}`→'trailhead', else 'poi'). A1/A2/A3 verifiers re-run → all PASS (no regression).
NEXT (advisory, not a blocker): the A1 DONE-block phrase "`--check` clean" is a misnomer — `--check` is a
non-writing dry run, not an idempotency assertion (idempotency is real, proven by byte-identical re-bake).
A4's DONE block already states this correctly; recommend the A1 receipt wording be corrected when next touched.

SEAT: quartermaster
VERDICT: clear
ISSUE: none — A4 extends the single crosswalk / renderer / schema; it does not multiply.
EVIDENCE: C1 region grep on main.js = 0 non-comment `layerKey === '` branches (A4 added none). C6:
`class [A-Z]` = 0/0 in main.js/panel.js; no new `website/*.html`; exactly one `FEATURE_LIST_LAYERS`. The new
`CONFIDENCE_DISPLAY`/`STATUS_DISPLAY` are display lookup tables wired into the existing
`PROVENANCE_KEYS`/`provenanceFields` renderer (optional 3rd tuple slot) — co-located config on the one renderer,
not a second registry. C2: one `collectStarredDestinations(`. `poiDisplayName` is ONE helper (single def),
consumed by editorPois rowLabel + drawn-POI listRow.name; the three map-label symbol expressions are a faithful
`coalesce(name,category,'POI')` mirror (a MapLibre expr can't call JS), not a third engine. `fileForItem`
extends the existing `SOURCE_FILE` fallback. rebake A4 changes live in the one CONFIG + `canonical_props`. The
verifier imports `viewer_url` from `playwright_base` (no re-implemented helpers). `node --check` clean.

SEAT: mason
VERDICT: clear
ISSUE: none — the A4 slice is additive, permissive, idiomatic, and leaves nothing dead.
EVIDENCE: `vocabDisplay` = `map[key] || String(value)` — known `'raw context'`→`'Raw context'`; off-vocab
`'observed'`/`'medium'`/`'single_track'`/`'synthetic_multi_user_model'` pass through as their own label, never
blank/drop/throw; `provenanceFields` builds a fresh array and leaves `props` byte-identical (no mutation). The
seed-kind lambda is the real shipped CONFIG (`p.get("kind") or "poi"`): `{'kind':'trailhead'}`→'trailhead'
survives, `{'category':'Pavilion'}`→'poi'; served seed `kind='poi'`, `facets.category='Pavilion'`, raw
`category` preserved. No CHECK/enum/regex-reject/row-drop introduced (the only pre-existing `.filter`/`.test`
are unchanged display logic with safe else-branches). `source_file` is additive (fresh `out` dict, non-machine
branch only; the two raw files carrying a `source_file` key are machine=True / value None → preserved, no
collision). No dead code: old `_PUB_KIND`/`k_publish` gone (0 refs), old `'category — name'` rowLabel branch
removed (survives only in a comment); new helpers all live. `node --check` clean; bake `--check` non-writing.

SEAT: warden
VERDICT: clear
ISSUE: none — every A4 hunk traces to one of the four named findings; the git gate is untouched; the loop
stopped at the Path A/B boundary.
EVIDENCE: main.js (`poiDisplayName` + editorPois rowLabel + three `editor-poi-*labels` `'POI'` fallbacks) and
panel.js (`fileForItem` reads `item.props.source_file` first; `vocabDisplay`+DISPLAY maps with pass-through)
close the four findings additively. rebake_canonical.py seed kind `p.get("kind") or "poi"` + `source_file` in
the non-machine branch; `_schema.json` adds the field. Verified live: seed POI `kind="poi"`/`category="Pavilion"`
(raw + facet)/`source_file` set; `source_file` present only on named non-machine layers (trail_network/buildings
True; roads/water/lidar/synthetic False — no key delta). publish.geojson = 6 features, geometry identical, only
the A1 `blurb` no-op; off-vocab `confidence='medium'`/`status='observed'` preserved. Git: HEAD `e34c1b8`
unchanged, index empty, reflog shows no mutating op, no `sw.js`/`#appVersion` bump in the diff (owed, reported).
Card A5 section + the Path A/B boundary line intact; no `spec.create`/`sourceChip`/`hostToggle`/`spec.idField`
work in the JS diff. NEXT (non-blocking, to Scribe/Steward): the A4 DONE block was unwritten at review time
(now written); the diff is the cumulative uncommitted A1–A4 batch (correct per the one-bump-per-batch contract).

SEAT: scribe
VERDICT: clear
ISSUE: none
EVIDENCE: The A4 DONE block records the live-DOM verifier + RESULT: PASS + the owed git gate (rides the one
batch bump + commit). All 4 A4 `Closes:` ids grep-resolve to one catalog home each and carry append-only
`DONE A4 (2026-06-09)` annotations mirroring A1/A2/A3's form; the coverage line A4=4 is consistent. The receipt
exists and is artifact-backed. Handoff updated (A4 done; NEXT pointer → A5). The `--check` wording the Witness
flagged is stated correctly in A4's DONE block ("`--check` is a non-writing dry run, not an idempotency gate;
idempotency proven by byte-identical re-bake"). Voice plain/terse, references concrete (treated as the thing),
no misspellings.

SEAT: steward (chair)
VERDICT: clear
SYNTHESIS: A4 finishes the render-derived display convergence — the last of the "same feature, different
string per surface" shadows. A drawn POI now shows ONE name on the map, the list, and the panel (the old
`category — name` dock fork is gone); a seed POI's kind is the controlled "poi" with the proper-noun as a
facet (a real class still survives — Mason); the Source-tab File is a baked attribute, never "unknown"; and the
confidence/status chips relabel the known vocabulary while passing an out-of-vocab value through visibly (the
`medium`→confidence normalization left, correctly, a curation call for the user). Additive, non-limiting,
on-farm, git gate untouched, observed live; A1–A3 unregressed. The two Witness/Warden advisories were
wording/recording notes, both resolved before clearance — no open andon. Owed remains the user's: the ONE Path-A
batch `sw.js`/`#appVersion` bump + commit. NEXT in the loop: A5 (edge-dispatch → spec strategies), then STOP at
the Path A/B boundary (already the loop's terminus — A5 is the last Path-A slice).
