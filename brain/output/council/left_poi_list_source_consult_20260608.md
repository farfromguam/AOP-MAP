# Council consult — "the left POI list shows content I can't trace; it should be DB + star attributes but isn't"

Date: 2026-06-08
Mode: CONSULT (diagnosis + pressure-test), not a done-review. No diff to clear.
Chair: Steward. Seats convened: Witness, Quartermaster, Mason, Warden.
Grounding: observation FIRST (live viewer on :8001, live DB, served files, code read).

-----

## The question

User: *"review the left side poi list. It has contents I cannot figure out where they
are coming from or what they are doing. It SHOULD be pulling from the db and star
attributes. ITs not appearing to do it. Consult the council. figure it out."*

## The answer (council-corrected)

The left POI tab is built by `collectStarredDestinations()` → `buildPoiGroups()` →
`renderPoiTab()` (`website/js/main.js:1169-1426`). It is a union of **four** inputs, and
only **two** of them are wholesale (not star-gated):

| Input | Source | Star-gated? | Clean-profile rows |
|---|---|---|---|
| Registry layers — cemeteries, buildings, visitorContext, trails | served `aop_*.geojson` → `featureListRuntime` | **Yes** (`listMode:'starred'`, `highlight===true`) | **0** |
| Registry layer — editorPois (Drawn POIs) | `aop_editor_pois_v1` localStorage (seeded from `aop_editor_seed_pois.geojson`) | **Yes** (`listMode:'starred'`, main.js:2514) | **1** |
| Published destinations | `publish.geojson` `layer=poi` (PostGIS bake) | **No** — bake is the gate, `starred:false` hardcoded (main.js:1268) | **2** (Pavilion, Ellis) |
| Event anchors | `aop_event_schedule.json` (static file, **not the DB**) | **No** — wholesale | **7** |

Observed live on a clean profile = **10 rows**. **9 of 10 are wholesale** (published bake +
event JSON) — neither is the DB-star path the user expected. **1 of 10 is star-fed**, but
via the editor's localStorage seed (the pavilion seed carries `highlight:true`), **not** the
DB and **not** the four reference layers.

The four DB-star reference layers render **zero** because nothing is starred anywhere they read:
- DB `core.features`: **0** rows with `attrs.highlight=true` (every layer — observed).
- Served reference files: **0** `"highlight":true` flags (all four — observed).
- `aop_positioned_features_v1` localStorage: **absent** on a clean profile (observed).

**The DB-star path is fully plumbed but UNFED for the reference layers.** Path:
right-panel ★ → `aop_positioned_features_v1` → `apply_positioned_features_to_core.py`
(writes `core.features.attrs.highlight`) → bake (`export_publish_geojson.sh` emits `attrs`
verbatim) → served `highlight` → the collector's one star gate. No star has been authored,
so the served files carry no highlight, so the four groups are empty. What's left filling the
list is the wholesale half plus the one pre-seeded editor star.

## The fix (no code change)

Run the existing author→DB→bake path — the plan's own "author stars first, then flip" step
held for the user (`tasks/08_data_normalization/star_driven_poi_normalization.md`):
author stars on the right panel ★ → `mvp/scripts/apply_positioned_features_to_core.py`
→ `mvp/scripts/export_publish_geojson.sh` → deploy. Then the four reference groups populate
from the DB.

## Open fork for the user (surfaced, not decided)

Even after authoring DB stars, `published_destinations` (2 rows) and `event_anchors` (7 rows)
stay wholesale by design — the bake is the published-POI gate, and event anchors come from the
schedule JSON, not the DB. If the user's model is "the whole left list should be starred DB
features," those two groups are a separate decision. Steward recommendation: keep them
wholesale (they serve a different purpose — bake-curated destinations and schedule anchors) and
author the reference-layer stars so those groups fill. The user's call.

-----

## Seat verdicts

**Witness — ANDON (folded).** Two load-bearing claims in the first-pass diagnosis were FALSE by
observation: (1) it said THREE wholesale inputs — but `drawn_pois`/editorPois is
`listMode:'starred'` (main.js:2514), star-gated, so there are only TWO wholesale inputs; (2) it
said "nothing is starred anywhere" — but the seed POI `aop_seed_pavilion` carries `highlight:true`
in `aop_editor_seed_pois.geojson`, stored in `aop_editor_pois_v1`, so the star path has exactly
ONE live star feeding one row. Proven by a controlled experiment: flipping the seed star to false
dropped the `drawn_pois` group and took the total 10→9. The "four reference layers render zero
because DB+served+positioned-store are all unstarred" sub-claim STANDS. Corrections verified by
the Steward directly (main.js:2514 `listMode:'starred'`; seed `highlight=true`).

**Quartermaster — CLEAR.** Reuse framing survives. `collectStarredDestinations` (main.js:1169) is
the ONE collector; `buildPoiGroups` (:1321) and `renderVisitorListGroup` (:1070) are thin
renderers that both call it and re-derive nothing (`grep "pushRow(" = 0`). published + event are
genuinely separate non-registry inputs, not duplicated registry layers. C1=0 branches, C6=0
classes / one registry / no new editor HTML. `apply_positioned_features_to_core.py` is the real
reusable store-side door (writes `attrs.highlight` :96-105, reuses split_key/sql_str/run_psql);
bake emits `attrs` verbatim (export_publish_geojson.sh:90) — no bake change. Fix = data authoring,
not code.

**Mason — CLEAR.** `listMode:'starred'` is a legitimate declared-mode dispatch with a permissive
fall-through (anything not `'starred'` emits), applied ONCE in the collector (main.js:1178) — not a
banned C5 row-dropping filter. Every 'starred' layer pairs with `highlightable:true` (a real ★
control): cemeteries 2305/2294, buildings 2387/2361, visitorContext 2699/2728, trails 2917/2894,
editorPois 2514/2614, brandLogos 2824/2807 (right-list only). Nothing throws on an unknown mode.
The empty list is by design — nothing starred yet. The apply script reports orphan keys loudly,
never drops silently. Routed the pre-existing `buildPoiGroups` question to Quartermaster (cleared
as a thin renderer); untouched by this diff.

**Warden — CLEAR.** Stayed on the farm. Read-only diagnosis. Git gate untouched (HEAD still
`c781f59`, no commit, no version bump — `sw.js`/`#appVersion` `v56` is the PRIOR session's
star-link/torch work, not this task). The only new artifact is `mvp/scripts/diagnose_left_poi_list.py`
— a read-only Playwright probe (grep for mutating verbs returns none), reversible, squarely inside
a "figure it out" directive. The recommendation correctly leaves the DB-star authoring + bake +
commit as the user's gate (`no_commits`). No card directive deleted.

## Steward synthesis

One andon (Witness), three clears. The andon is folded — the corrected diagnosis is above and is
sharper than the first pass. **Consult resolved:** the left list isn't "broken" — the star path
works, but for the four reference layers it has never been fed (0 DB stars), so 9 of 10 visible
rows come from the two wholesale inputs and 1 from the editor's pre-seeded star. The fix is the
user's held authoring step, not a code change. One product fork (should published + event also be
star-gated?) surfaced for the user.
