# Council done-review — shadow-attribute resolution slice A1 (2026-06-09)

**Slice:** Path A / A1 — the foundational canonical re-bake population
(`tasks/09_editor_maturity/shadow_attribute_resolution.md`).
**Tier:** full six (publish-zone served data + sprint-spine slice).
**Diff under review:** `mvp/scripts/rebake_canonical.py`, `website/data/_schema.json`, 9 served
`website/data/*.geojson` (aop_trail_network, aop_buildings, aop_cemeteries,
aop_visitor_context_callouts, aop_editor_seed_pois, aop_activity_hotspots,
aop_synthetic_activity_hotspots, aop_synthetic_activity_tracks, publish.geojson),
`mvp/scripts/playwright_verify_shadow_a1_canonical.py`, `brain/research/common_feature_schema.md`,
and the card + audit-catalog annotations.

**RESULT: FULL SIX CLEAR** (1 Scribe andon, folded → re-cleared; the andon had two parts — a missing
handoff line and this receipt itself being cited before it was written; both resolved).

Each seat ran in a fresh context over the diff + the A1 acceptance, prompted to refute.

-----

SEAT: witness
VERDICT: clear
ISSUE: none
EVIDENCE: Re-ran `playwright_verify_shadow_a1_canonical.py` against the live viewer on :8001 — RESULT
PASS, exit 0, all checks pass, 0 console errors, `has_trail_source=True` (the running map actually
consumed the re-baked source, not just fetched it). Then independently cross-checked every claim against
the served bytes with python (not the verifier's own assertions): trail #1 `name="Launchpad"` +
description + `facets.difficulty="easy"` + `_original.name="1"` + `trail_number=1`. Idempotency: hashed
all served geojson, ran the bake twice — run#1 == pre-existing working tree, run#2 == run#1, byte-for-byte.
`--check` exit 0, non-writing (hashes unchanged). publish.geojson: 6 features, no `blurb`, 3 descriptions.
trail-network truthy-`name` count 100 vs `git show HEAD:` 100 → no stray labels (the label layer paints
`['to-boolean',['get','name']]`; trail #1 changed text "1"→"Launchpad" but stayed truthy). All served==raw
feature counts. (Caught + corrected its own two misfired `cd &&` commands by re-running with absolute
paths; no claim rests on a misfired run.)

SEAT: warden
VERDICT: clear
ISSUE: none
EVIDENCE: HEAD still `e34c1b8 shadow attribute removal plan` (no commit); `sw.js`/`index.html` v59
unchanged and absent from the diff (no version bump — both OWED, honored). Every hunk traced: the 9 served
`*.geojson` are the bake output A1's directive + Observable acceptance explicitly target; the verifier is
the standing Witness condition (imports `playwright_base`); the card + audit edits are the Record-on-green
/ re-home-with-record channel (original directive text preserved; coverage total 22 unchanged). The two
scope calls are defensible inside A1: removing publish from CONFIG stops the 6→5 two-writers regression
without pulling the DB door (Path B reproducibility still listed/held); the re-home is recorded in four
places. No off-farm work, no git-gate violation, no attribution, no directive deletion.

SEAT: quartermaster
VERDICT: clear
ISSUE: none
EVIDENCE: The sidecar join was added INSIDE the one existing baker (`rebake_canonical.py` — new CONFIG
keys `trail_join`/`poi_source`/`status`; `join_name_desc`/`facets`/`resolve_status` called from the
existing `canonical_props`); publish removed from CONFIG retires a two-writers regression, leaving one
canonical baker. Grep of `panel_overrides.py`/`bake_panel_overrides.py`/`apply_panel_overrides_to_core.py`/
`import_*` — no pre-existing trail-catalog or poi-index join; the only prior join was the runtime
`trailCatalogLookup`(main.js:535)/`poiIndexLookup`(main.js:1112) that A1 centralizes (A2/A3 delete the
runtime versions). The verifier reuses `playwright_base` like the other importing verifiers. `_schema.json`
extended in place (new `facets`/`sidecars` blocks; crosswalk unchanged) — no second schema/registry.
Structural greps hold (data-only slice): C1 = 0 non-comment `layerKey === '` in main.js; C6 = 0 `class
[A-Z]`, one `FEATURE_LIST_LAYERS`, no new editor `*.html`; C2 = one `collectStarredDestinations(`.

SEAT: mason
VERDICT: clear
ISSUE: none
EVIDENCE: Grep across mvp/+website/: zero `raise/assert/reject/coerce/filter()/.drop`, zero
enum/CHECK/validator — non-limiting. kind/status/difficulty pass-through (live: out-of-vocab `brand_logo`
survives; trail status uncoerced). Both `continue`s are non-dropping (match-scan / missing-file SKIP).
Additive preserve verified on real data: trail #1 `name="Launchpad"` + `_original.name="1"`; raw==live
counts on all 8 files (nothing dropped); `_original` tight — exactly 8 catalogued trails, 0 spurious
(`_original` is the minimal correct fix for the only collision case, name/description vs canonical). Dead
code removed (`k_publish`/`_PUB_KIND` gone, 0 refs). Landcover lean (0/130 hotspots carry a facets block).
`_meta`/manifest maturity-preservation is a real bug fix (the old `if "_meta" not in doc` guard wiped the
stamps), not added complexity. Dispatch reads cfg flags/props, never a layerKey. (Card note, not a gate:
`strip_legacy_publish_blurb` mutates served publish in place — intentional, publish is DB-baked not
re-baked, and content-safe.)

SEAT: scribe
VERDICT: clear (after 2 andons folded)
ISSUE: none (was: (1) no A1 line in `handoff/session_context.md`; (2) handoff cited this receipt before it
existed / overstated the clear vs the card)
EVIDENCE: A1 DONE block records the observable acceptance as a RESULT and states the owed git gate plainly.
Both audit-catalog entries annotated (`publish-confidence-status-off-vocabulary` RE-HOMED A1→A4;
`legacy-blurb-key-survives-in-served` DONE A1); A4 `Closes` lists the re-homed id; coverage line A1=7 ·
A4=4 sums to 22; all 45 plan ids grep-resolve to exactly one home, no orphans. References concrete, voice
plain/terse/user-true, no misspellings. Fold 1: the A1-pickup line was appended to the handoff. Fold 2:
this receipt was written and the card banner aligned to "FULL SIX CLEAR" so the handoff's claim is backed
by the artifact.

SEAT: steward (chair)
VERDICT: clear
SYNTHESIS: A1 does the right work against the product promise — it makes the trail/poi names a trustworthy
first-class field in the served data (the map-before-app, source-led shape), additively, with provenance
preserved. The two scope calls (publish out of CONFIG; confidence/status re-homed to A4) are correct
boundary discipline, not drift — they keep the Path A/B line the plan drew and are recorded. Verification
is a real observation of the running system, not narration. The only andon was a record-completeness gap,
now folded. Clearing the gate. Owed remains the user's: one `sw.js`/`#appVersion` bump + the commit
(brain + script + `_schema.json` + 9 served `*.geojson` + the new verifier). NEXT in the loop: A2.
