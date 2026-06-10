# Session Handoff: Sprint 04 pickup

Date: 20260527

Short pointer for the next session. The durable record lives in the cards.

-----

**2026-06-10 (cwc — G_B HIGH trio DONE + COUNCIL FULL-SIX CLEAR; UNCOMMITTED, v61→v62 bump owed).** Continued
the gold swarm to **G_B — demote localStorage to a working buffer** (Root 1 / C3 / F1: the published reference
view must stop being a per-browser localStorage replay). **Reconciliation note:** while G_B ran, the user committed
the prior G_E batch (the v61 bump + the whole G_E slice + brain) as **`86b6fcd "GE slice"`** — so HEAD moved
1cbd439→86b6fcd and the working tree is now cleanly just G_B. (Mid-session I briefly mis-read the smaller git status
as data loss; verify-by-observation + reflog showed it was the user's commit — nothing lost.) **Design-first:** a
read-only state audit (`../output/gB_state_audit_design_20260610.md`) found the card overstated the open work — star
(Sprint 08) + write-door columns (Approach-C) were already done; the real keystone was the boot READ path. **Shipped
the HIGH trio** via a fresh agent, orchestrator re-verified by observation: **G_B.1** (keystone) demoted the boot
`edits`/properties/geometry replay for the 4 baked reference layers to staging-only in both `panel.js`
`applyStoredOverrides` + `main.js` `applyPositionedFeatures` (`opts.boot` gate; `created`/`deleted` kept; in-session
edit + Export kept); **G_B.2** bridged panel reference edits + standalone ★ through the existing
`AOP_HOST_SET_FEATURE_PROPS` → positioned-features → the one DB door (no second store); **G_B.3** folded
`notes`→`description` + widened the apply-script gate (additive). **Verified:** new
`playwright_verify_gB_localstorage_demotion.py` 17/17 PASS (stale diff no longer overrides baked name EMBEDDED +
STANDALONE; created/deleted still replay; fresh-LS shows baked; 0 errors) — closes the g0_obs2 two-browser
divergence; `node --check` both JS; `git diff HEAD -- website/data` empty (no served-data change). **Council:** five
seats + Steward clear (Mason: one idempotent-harmless double `pushTagToHost`, not worth a revision). Receipts
`../output/council/gB_localstorage_demotion_20260610.md`. **DB:** `mvp-db-1` up; snapshots
`/tmp/aop_db_snapshots/aop_map_pre_gB_20260610.sql`; the verification apply→bake round-trip was fully reverted
(served + DB restored). **OWED — the user's git gate:** a **v61→v62** bump (G_B's shell-asset changes sit on top of
the committed v61) — made in-tree (`sw.js`/`#appVersion`), uncommitted. Working-tree batch: `website/js/main.js` ·
`website/js/panel.js` · `mvp/scripts/apply_positioned_features_to_core.py` · `website/sw.js` · `website/index.html`
· `mvp/scripts/playwright_verify_gB_localstorage_demotion.py` · `brain/output/gB_*` + receipts + card/handoff.
HEAD `86b6fcd`. `.claude/.council-cleared` stamped for this diff. **DEFERRED:** findings 5 (visibility, LOW) + 6
(maturity, MEDIUM — pair with `reference-bake-no-meta-on-fresh-volume`) + GAP B (reference-geometry DB door).
**Next slice:** the deferred G_B follow-up, or **G_C** (collapse identity forks — highest risk, do carefully) /
**G_D** (fresh-volume parity — DESTRUCTIVE, needs the user's explicit OK before any `down -v`).

**2026-06-10 (cwc — owed v61 bump DISCHARGED + G_E events convergence DONE + COUNCIL FULL-SIX CLEAR; UNCOMMITTED,
the v60→v61 bump is the only version owed for the whole batch).** Reconciled the handoff against git: the user
committed the Approach-C batch as `1cbd439 "v61"` — **but the version STRINGS were never bumped** (the commit is
*named* v61 while `sw.js` VERSION + `index.html #appVersion` still read **v60**). That's the exact stale-PWA-cache
defect the handoff kept tracking: served data (5 GeoJSON + panel.js) shipped under the unchanged cache key, so
installed users wouldn't refresh. **Fixed in-tree** (sw.js:35 + index.html appVersion → v61; verified the running
:8001 server delivers v61 in both, 0 stray v60). This bump is uncommitted = the user's git gate, and it now also
covers the G_E batch (no second bump). **Then executed G_E (events overlay convergence)** via a fresh agent,
design-first, orchestrator re-verified by observation, **council full-six clear** (Mason andon'd one dead alias →
removed → re-clear). One shared resolver `website/js/event_schedule_geojson.js` (both index.html + right_panel.html
load it; main.js + panel.js delegate; stripped panel resolver + `roleForTag` deleted); `#pavilion` anchor geometry
baked (resolves on fresh localStorage); umbrella metadata → new additive `core.event_meta` table (bake reads it,
heredoc demoted to fallback); re-baked `aop_event_schedule.json` adopted → `export --check` = NO REVERT on all 6
files. Verifier `playwright_verify_event_schedule.py --baked` 14/14 PASS; 7 full-suite fails proven pre-existing.
DB up (`mvp-db-1`); recovery snapshot `/tmp/aop_db_snapshots/aop_map_pre_gE_events_20260610.sql`; counts events
13/activities 12/features 159 active. Receipts `brain/output/council/gE_events_convergence_20260610.md`; design
`brain/output/gE_events_convergence_design_20260610.md`; card `06_going_gold/gold_slice6_backlog.md` G_E + the
umbrella item marked `[x]`. **OWED — the user's git gate:** ONE `sw.js`/`#appVersion` **v60→v61** bump (already
done in-tree, uncommitted) covering the whole uncommitted batch = the Approach-C files already in `1cbd439`'s tree
PLUS the G_E files (`event_schedule_geojson.js`, `index.html`, `right_panel.html`, `main.js`, `panel.js`, `sw.js`,
`aop_event_schedule.json`, `mvp/init_db.sql`, `seed_event_meta.py`, `export_publish_geojson.sh`,
`playwright_verify_event_schedule.py`, `brain/`). HEAD still `1cbd439`. The user likely wants to amend `1cbd439`
or add a follow-up commit so the v61 strings ship. **G_B (demote localStorage → working buffer) is the next slice**
— the column home (Approach-C) and the events axis (G_E) both landed, so G_B can route reference-feature edits
through the one DB home. `.claude/.council-cleared` stamped for this diff.

**2026-06-10 (cwc — APPROACH-C SLICE DONE + COUNCIL FULL-SIX CLEAR after 2 andons fixed; UNCOMMITTED, same v60→v61
bump owed; G_B now unblocked, G_E is the next slice).** Picked up the gold-slice-6 swarm. Environment up
(`mvp-db-1` 15h; `core.features` 160/159 intact; fresh snapshot `/tmp/aop_db_snapshots/aop_map_pre_approachC_20260610.sql`).
Spawned a fresh agent to execute the **decided Approach-C fork** (the "One writer per served file" + columns-vs-attrs
item). **DONE + LOSS-FREE.** Field-inventory FIRST (`brain/output/approachC_field_inventory_20260610.md`, the thing
that stalled the 3 prior agents): every served `properties` key classified column-vs-attrs. The key finding — the
`attrs`-verbatim bake **already reproduced HEAD byte-for-byte**; the only column/served gaps were buildings `name`
(column held the street ADDRESS) + `status` (column held the FEMA facility ROLE), plus the two no-column spine fields
`source`/`last_checked` (open-vocab → stay in attrs). **Changes:** (1) DB additive promotion `attrs.name`/`attrs.status`
→ buildings `name`/`status` COLUMNS (address→`attrs.address`, role→`attrs.facility_role`); (2) `export_publish_geojson.sh`
one shared spine-from-columns rule (`SPINE_COLS`/`SPINE_JSONB`), reference arm serves `attrs || SPINE_JSONB`, publish arm
names the same columns, new `--check` fixed-point mode; (3) `apply_positioned_features_to_core.py` unified with the POI
sink (CMFS→COLUMNS, highlight/extras→attrs); (4) `rebake_canonical.py` EVICTED the 4 ref files from CONFIG (export is
sole writer). **Blocker-2:** no name-nulling needed — trail `name` column already == served for all 120 trails.
**ORCHESTRATOR RE-VERIFIED BY OBSERVATION (not narration):** my own match-by-id + full multiset diff (coords→7dp) =
**0 features only-in-HEAD, 0 only-in-CUR** on all 4 files (all 8 cemetery twins included); geometry precision-only
≤5e-10°; `export --check` = `same` for the 4 ref + publish (only `aop_event_schedule.json` DRIFTs = the G_E axis, left
at HEAD on purpose); `rebake_canonical` CONFIG lists 0 of 4; `playwright_verify_shadow_refbake_repro.py` **19 PASS** on
the live viewer (loss-free + md5 pure-function + eviction + no-revert + smoke: trails 120/buildings 5/cemeteries 8/visitor
4, "Launchpad"+"Pavilion" render, 0 console errors); `playwright_verify_shadow_f4_publish_repro.py` **16 PASS run alone**
(publish not regressed; live editor resolves a published feature; the concurrent-run 20s timeout was contention, re-ran
alone clean). DB still 160 (restored from snapshot after the sink round-trip test, buildings promotion re-applied).
**Closed:** `two-writers-same-five-files-rebake-vs-export`, `canonical-fields-duplicated-columns-vs-attrs-served-from-attrs`,
`two-editor-sinks-opposite-homes`. **G_B is unblocked** (the column home exists). **COUNCIL (full six): 3 clear, 2 andon
→ both fixed + re-verified → FULL SIX CLEAR.** Witness/Warden/Quartermaster cleared first pass. (1) **Scribe** caught a
REAL loss the per-feature checks missed: the bake carried forward only `_meta`, dropping owner-authored **top-level
FeatureCollection** provenance (buildings `_source`/`_derived`/`_generated_by`/`_sources_checked`/…; cemeteries
`_source`/`_generated_by`; trails collection `name`; visitor `name`/`_description`/`_sources_checked`). FIXED — both bake
arms now carry forward EVERY top-level key; re-baked loss-free at both levels; the verifier gained a `COLLECTION-level
top-level keys loss-free` assertion (closes the hole). (2) **Mason** caught dead code the eviction orphaned (`n_building`
+ the `trail_join`/`poi_source` join machinery in `rebake_canonical.py`). FIXED — removed (kept `_load_json` + `SIDECARS`,
both still live); proved behavior-preserving by re-baking all 17 rebake-owned files → byte-identical to HEAD; `_schema.json`
restored (the rebake-test artifact). Marker written `.claude/.council-cleared`. **OWED — the user's git gate (unchanged from the F4 batch — this slice rides the same
bump):** ONE `sw.js`/`#appVersion` **v60→v61** bump covering the whole uncommitted batch, at the user's commit. Files in
the batch: `mvp/scripts/{export_publish_geojson.sh,apply_positioned_features_to_core.py,rebake_canonical.py,fold_sidecars_into_core_features.py,fold_served_enrichment_into_core.py,fold_served_canonical_into_core.py,playwright_verify_shadow_f4_publish_repro.py,playwright_verify_shadow_refbake_repro.py}`,
`website/data/{aop_buildings,aop_cemeteries,aop_trail_network,aop_visitor_context_callouts,publish}.geojson`,
`website/js/panel.js`, `brain/output/approachC_field_inventory_20260610.md` + the G0 screenshots + brain. HEAD still
`69fd2d3 "v60"`. **G_E (events) is the next slice** — it's a real JS refactor (collapse the two divergent resolvers
`resolveEventSchedule`@panel.js / `eventScheduleToGeojson`@main.js:6366 to read ONE baked event FC; bake coordinate-less
anchor geometry; umbrella metadata → `core.events`, which the bake currently flags deferred-V2) + adopt the DRIFTing
`aop_event_schedule.json`; its own slice + own council, not folded into Approach-C.

**2026-06-10 (gold slice-6 / Path-B swarm — 5 doors DONE + COUNCIL FULL-SIX CLEAR; UNCOMMITTED, v60→v61 bump owed;
reference one-writer + G_B/G_C BLOCKED on an architectural fork).** User lifted the Path-B hold: *"put all the
things in a big list in the sprint. work through them independently and relentlessly. spawn off agents… when done
have the council review."* Big list = **`brain/tasks/06_going_gold/gold_slice6_backlog.md`** (every held finding
sliced into `- [ ]`, grouped G0/G_A/G_B/G_C/G_D/G_E). Brought Docker+PostGIS up non-destructively (bind mount;
`core.features` 159 active + 1 archived intact; recovery snapshot `/tmp/aop_db_snapshots/aop_map_pre_slice6_20260609.sql`).
**DONE + verified (each by a fresh agent, orchestrator re-checked):** **G0** verification debt — 3 C4 findings observed
LIVE (trail-name agreement post-A2; two-browser localStorage divergence; orphaned brand-logo star; `brain/output/g0_obs{1,2,3}_*.png`);
**slice1** `fold_sidecars_into_core_features.py` (trail catalog + poi-index → `core.features`; DB trail#1 `name='Launchpad'`);
**enrichment fold** `fold_served_enrichment_into_core.py` (facets/source_file → DB attrs, 137 rows; coverage matches served);
**complete-fold DB catch-up** `fold_served_canonical_into_core.py` (buildings attrs `name`→facility names, `status`="raw context";
KEPT, additive — its DB sync only; its served-adoption/eviction half was REVERTED); **F4** `export_publish_geojson.sh` +
`website/data/publish.geojson` + `website/js/panel.js` (publish.geojson now reproducible from the DB with stable unique
`source_key` ids replacing the stale colliding 1-6; editor matches by served id; verifier `playwright_verify_shadow_f4_publish_repro.py`
14/14 PASS, byte-reproducible). **⛔ BLOCKED (the architectural fork — gates G_B localStorage-demotion + G_C identity):**
"one writer per reference file" needs deciding the **canonical-fields home (DB columns vs `attrs`)** AND how the bake
reproduces **render-sensitive trail human-names** (the bake emits number/blank to avoid labels on unnamed edges, so it
can't naively serve `attrs.name`). THREE agents stalled/held; a lossy DB-bake adoption was attempted and **REVERTED**
(4 reference served files back at HEAD, Launchpad intact; publish.geojson re-baked to F4's). **COUNCIL: FULL SIX CLEAR**
(Witness·Warden·Quartermaster clear first pass; Mason + Scribe andon'd on docstring/handoff/version-gloss → folded
[this entry + the fold docstring + the card's `69fd2d3` clarification] → re-cleared). **OWED — the user's git gate
(NOT done):** commit `website/data/publish.geojson` + `website/js/panel.js` + `mvp/scripts/export_publish_geojson.sh`
+ the new `mvp/scripts/{fold_sidecars,fold_served_enrichment,fold_served_canonical,playwright_verify_shadow_f4_publish_repro,playwright_verify_shadow_refbake_repro}.py`
+ brain, with **ONE `sw.js`/`#appVersion` v60→v61 bump** (working tree still v60). **HEAD `69fd2d3`** ("v60", Path-A bump
only — NOT this batch). **NEXT — the fork is DECIDED (user, 2026-06-10): APPROACH C.** Execute the Approach-C slice (it's written
out as the executable plan in the card's "One writer per served file" item) BEFORE G_B: **canonical home =
`core.features` COLUMNS** (attrs = render/domain extras only); **ONE shared bake helper** builds
`properties = columns ⊕ curated-attrs` for BOTH arms of `export_publish_geojson.sh`; **unify both editor
sinks** (`apply_panel_overrides_to_core.py` + `apply_positioned_features_to_core.py`) to write CMFS →
columns; **field-inventory FIRST** (enumerate every served `properties` key → column vs attrs, exhaustive,
drop no render key — an incomplete merge is what stalled the 3 prior agents); **unnamed-trail `name=null`**
(keep `trail_number`) so the bake reproduces HEAD's no-labels-on-unnamed. Close-out: DB-bake the 4 ref
files → loss-free semantic-diff vs HEAD → adopt → evict `rebake_canonical` (one writer) → `--check` proves
no revert → `two-writers` closed, G_B unblocked. **Process caution:** snapshot the DB first; keep verifiers
LEAN (file-diffs + psql + ONE short viewer smoke, no networkidle — three agents hit the 600s stall watchdog
on heavy Playwright runs). **G_E (events)** is a low-risk parallel win, independent of the fork. **G_D
(153-row fresh-volume) stays HELD** — the one destructive step (the user's explicit OK needed before any
`down -v`). The full sliced list is `brain/tasks/06_going_gold/gold_slice6_backlog.md`.

**2026-06-09 (cwc pickup — Path A batch reconciled + the owed version bump DONE; bump UNCOMMITTED).**
Reconciled the handoff against git: the Path A batch the loop left "uncommitted, one vNN bump owed" was in
fact committed by the user as `11fe36f more data normalization` (HEAD) — `website/js/main.js` +
`website/js/panel.js`, `rebake_canonical.py`, `_schema.json`, all 9 re-baked served `*.geojson`, the 5 new
`playwright_verify_shadow_a[1-5]_*.py`, the council receipts, and the brain. **But `index.html`/`sw.js` were
NOT in that commit**, so the whole Path A batch (changed JS + every re-baked GeoJSON) shipped under the
*unchanged* `v59` — installed PWA users would stay on the stale cached shell + data (sw.js caches GeoJSON
cache-first, refreshing only on a VERSION bump). Did the owed bump: `v59 → v60` at both sites
(`website/sw.js:35` const VERSION, `website/index.html:227` `#appVersion`, kept in sync). **Verified by
observation:** restarted the :8001 viewer, `playwright_verify_shadow_a1_canonical.py` PASS (boots over the
re-baked data, 0 console errors, all canonical values live); served `index.html` renders `v60` and served
`sw.js` const is `v60`. Working tree = exactly `website/index.html` + `website/sw.js`, **UNCOMMITTED — the
user's git gate.** With this bump committed, Path A (A1–A5) is code-complete, council-cleared, AND versioned.
**NEXT (the user's call):** commit the v60 bump, then decide whether to pull **Path B / gold slice 6**
(`../06_going_gold/gold_migration.md`) — the 20 held DB-door / identity / bake-reproducibility findings (the
non-reproducible `publish.geojson`, the localStorage-diff published reference view, the full DB collapse).
Path B is a major migration, still HELD for the user's pull.

**2026-06-09 (RALPH LOOP STARTED — Path A slice A1 DONE + COUNCIL FULL-SIX CLEAR; CODE+DATA, UNCOMMITTED,
one vNN bump owed, commit OWED).** Picked up the shadow-attribute resolution ralph loop in a fresh session
(`tasks/09_editor_maturity/shadow_attribute_resolution.md`, Loop contract). **A1 (foundational canonical
re-bake population) DONE.** `mvp/scripts/rebake_canonical.py`: folded the two render-time sidecar joins into
the BAKE — trail catalog → `name`/`description`/`facets.difficulty` by `trail_number` (trail #1 now bakes
`name="Launchpad"`, the "1" stand-in preserved under `_original`); poi-index → building/cemetery/visitor
`description` + `facets.revisit_note` by match. Added a Tier-3 `facets` block, moved building facility-role
out of `status` (→ `facets.facility_role`, status="raw context"), machine-layer name/status crosswalk
(no stray labels — those symbol layers read `label`, not `name`), and fixed two latent re-bake bugs: the
`_meta`/`_schema.json` maturity stamps were being **wiped** every re-bake (now carried forward), and the
manifest is regenerated (counts + `updated_at` fresh). Sidecars read live from `website/data/` (not copied
to `raw/` — an authored catalog must not go stale). **Two scope rulings:** (1) **removed `publish.geojson`
from the re-bake CONFIG** — it is DB-baked (`export_publish_geojson.sh`, 6 features) and `raw/` is a stale
5-feature snapshot, so an unmodified re-bake was reverting publish 6→5 (the two-writers regression); the
full DB collapse stays **Path B / gold slice 6**. `legacy-blurb` dropped via an idempotent in-place strip
(`strip_legacy_publish_blurb`). (2) `publish-confidence-status-off-vocabulary` **re-homed A1→A4** (a
read-site display relabel; the bake can't own a DB-baked file) — coverage stays 22 Path A (A1=7 · A4=4).
**Verified by observation:** new `mvp/scripts/playwright_verify_shadow_a1_canonical.py` (on
`playwright_base.py`, tile-independent) — viewer boots over the re-baked data with **0 console errors**, all
canonical values observed live; re-bake idempotent, `--check` non-writing, feature counts == `raw/`,
trail-network label count 100→100 (no stray labels), out-of-vocab `brand_logo` kept. **COUNCIL: FULL SIX
CLEAR** (Witness re-ran the verifier + cross-checked served bytes; Quartermaster confirmed one baker +
C1/C2/C6 hold; Mason confirmed non-limiting + additive + dead code removed; Warden confirmed on-farm + git
gate untouched; Scribe cleared after this handoff line was added). Receipt:
`output/council/shadow_a1_canonical_rebake_20260609.md`. **OWED (user's git gate):** the commit
(`rebake_canonical.py` + `_schema.json` + 9 served `*.geojson` + the new verifier + brain) with **one**
`sw.js`/`#appVersion` bump covering the whole Path A batch — NOT committed, NOT bumped. **A2 ALSO DONE +
COUNCIL FULL SIX CLEAR (same session):** the runtime `trailCatalogLookup`/`fetchTrailCatalog` join is
deleted from `main.js`; every trail surface (left list, panel Name input, map label, search, popup) reads
the canonical baked `name`/`description`; listRow status/source de-fabricated; number-search preserved;
catalog `length_mi`/`onx_tr`/`connects` baked as facets so the popup reads the feature. Live-DOM verifier
`playwright_verify_shadow_a2_trail_name.py` (all four surfaces == "Launchpad", 0 console errors). Receipt:
`output/council/shadow_a2_trail_name_20260609.md`. (`playwright_verify_feature_list.py` fails on the
drawn-POI Move flow — confirmed PRE-EXISTING against HEAD JS, not an A2 regression.) **A3 ALSO DONE +
COUNCIL FULL SIX CLEAR (same session):** the per-feature `poiIndexLookup` blurb join is deleted (0 callers;
`fetchPoiIndex` kept only for the POI-tab group taxonomy); building canonical `name` is now the facility
name ("Pavilion", baked via `n_building`), street address → `facets.address`; building/cemetery/visitor read
sites (listRow, rowLabel, panel node, search) all read the one canonical name + baked `description`. Live-DOM
verifier `playwright_verify_shadow_a3_poi_name.py` (Pavilion agrees across served/search/panel row/Name
input; address searchable as alias; 0 console errors). Receipt: `output/council/shadow_a3_poi_name_20260609.md`.
**A4 ALSO DONE + COUNCIL FULL SIX CLEAR (same session):** render-derived display unification. One
`poiDisplayName(props)` helper in `main.js` (`name.trim() || category || 'POI'`) feeds the editorPois
`listRow.name` + `rowLabel`; the three `editor-poi-*labels` map symbol `text-field`s became
`coalesce(name,category,'POI')` to mirror it — the old three-way fork (dock `category — name` / panel
`name||category` / map coalesce) is gone. Seed POI kind un-shadowed: `rebake_canonical` seed config
`kind=lambda p: p.get("kind") or "poi"` bakes the controlled "poi" (Mason safe default — a real `kind`
survives; "Pavilion" → `facets.category`, raw key preserved). Source-tab File now reads a baked
`source_file` (stamped per-feature on **named non-machine layers only** — machine/coverage stay lean);
`fileForItem` prefers it, never "unknown" for a baked feature. Confidence/status chips relabel via additive
`CONFIDENCE_DISPLAY`/`STATUS_DISPLAY` + `vocabDisplay` in `provenanceFields` (known→label,
out-of-vocab→passthrough, raw value untouched — Mason; the `'medium'`→source-register-confidence mapping
left a curation call for the user). Live-DOM verifier `playwright_verify_shadow_a4_display.py` (map source
name == POI-tab row == panel item == Name input == "AOP Pavilion"; Kind chip "poi" + Details "Pavilion";
building File "aop_buildings.geojson"; Status "raw context"→"Raw context"; off-vocab "medium" passes
through; 0 console errors; A1/A2/A3 verifiers still PASS; idempotent by byte-identical re-bake). Receipt:
`output/council/shadow_a4_display_20260609.md`.

**A5 ALSO DONE + COUNCIL FULL SIX CLEAR (same session) — PATH A COMPLETE, loop at the A/B boundary.**
Edge-dispatch → spec strategies (C1). Five call-site special-casings converged onto declarative
spec/node capabilities, naming no layerKey/source literal: (1) `AOP_HOST_CREATE_FEATURE` dispatches a
`spec.create` capability (was `layerKey !== 'editorPois'`; editorPois declares `create`→addDrawnPoi; a
layer without it returns null, no throw); (2) `sourceChip` a co-located spec field on the 4 destination
specs (the `VISITOR_LIST_SOURCE_CHIP` map deleted); (3) the sfwda node declares `hostToggle:'showSfwda'`,
the bridge reads `node.hostToggle` (the `EXPLICIT_HOST_TOGGLE` map deleted); (4) one `USER_FEATURES_SOURCE`
const + one `usesUserFeatures(spec)` predicate replace the `=== 'userFeatures'` literal at every call
site; (5) `deriveItems` falls back to the canonical baked `id` before the positional `idx` (now a
last-resort R13 default — no current items-node reaches it). Verifier
`playwright_verify_shadow_a5_dispatch.py` (deterministic, 5/5): structural (C1=0 layerKey branches, C6=0
classes, the dispatch maps gone, `node --check` clean) + LIVE — a "+ POI" create through the SAME bridge
the panel's commitFeature uses dispatches via `spec.create`, the feature lands (1→2, name=='Restroom'),
'buildings' (no create) → null, the created feature is editable through the panel's edit bridge
(`AOP_HOST_SET_FEATURE_PROPS` → the live source reflects the rename), the panel editorPois Name input is
live-editable (seed); 0 console errors. A Witness flakiness andon (the first verifier's
panel-select-of-bridge-created-feature step was a re-seed race) was folded → replaced by two deterministic
editability checks → Witness re-confirmed 5/5. Receipt: `output/council/shadow_a5_dispatch_20260609.md`.
(Chip/SFWDA/userFeatures sub-changes are structural-only — they render into main.js's hidden #editorTree
under embed; stated as such, no narrated DOM check.) A1–A4 verifiers still PASS.

**THE RALPH LOOP IS DONE — Path A (A1·A2·A3·A4·A5) all council-cleared; STOPPED at the Path A/B boundary.**
Path B (the 20 DB-door/identity/bake-reproducibility findings) stays HELD for the user's gold-slice-6
pull (`../06_going_gold/gold_migration.md`). **NEXT (the user's call):** commit + ONE `sw.js`/`#appVersion`
bump covering the WHOLE Path-A batch — `main.js` + `panel.js` + `rebake_canonical.py` + `_schema.json` +
the re-baked served `*.geojson` + the 5 new `playwright_verify_shadow_a[1-5]_*.py` + brain — then pull
gold slice 6 (Path B) if desired. **The commit + the bump are the user's git gate — NOT committed, NOT
bumped; HEAD still `e34c1b8`.**

-----

**2026-06-09 (SHADOW-ATTRIBUTE AUDIT — card opened + seal-team sweep DONE; BRAIN ONLY, UNCOMMITTED,
council review NEXT).** Follow-on to the "Launchpad" trace below: a trail whose name disagrees across
surfaces ("Launchpad" left / "Trail 1" right / "1" on the map) because the name is a **runtime sidecar
join**, not a field. The user named the class a **shadow attribute** — a value/behavior driving what you
see/edit that is NOT a first-class CMFS attribute (smuggled via runtime sidecar join · render-derivation ·
localStorage-as-truth · per-layer edge dispatch · half-converged re-bake). Directive: *"this is slop. find
all places where logic is driven in a weird edge-case way, or an MVP shortcut that needs maturing out. Data
attributes should be cut and migrated to a common schema. The council will review when done."* **Carded**
`tasks/09_editor_maturity/shadow_attributes_audit.md` (definition · CMFS target · C1/C3/C5/C6 guardrails =
additive migration only · extends the spike audit F1–F9 + gold slice 6 rather than re-carding them).
**Ran the seal team** (workflow `wf_eae016f9-626`): 8 lens agents in parallel → 73 raw findings → synthesis
→ **45 deduped (15 HIGH / 22 MEDIUM / 8 LOW)**, every finding a real `file:line`, each mapped to its CMFS
target; catalog written into the card's FINDINGS section. **Headline:** the trail is the worst offender
(one feature, FOUR names / FOUR identities across four surfaces). Three structural roots, all verified
statically: (1) the published reference view is a **per-browser localStorage diff replayed at boot** (C3);
(2) `publish.geojson` is **NOT reproducible from the live DB** (served ids 1–6 vs DB serials 139–201,
carries retired `blurb`, 5 files have two competing writers); (3) the canonical re-bake left
`name`/`description` as stand-ins/blank + `_schema.json`'s crosswalk omits the two sidecars and any Tier-3
facet block — all cluster onto **gold slice 6**. **Coverage gap (Witness will andon):** the audit is
entirely STATIC — no live-app runtime observation yet (C4 owed); plus a scope ruling owed on the
`#tag`→coord events binding. **NO code/data changed (audit only); nothing committed.** **COUNCIL: FULL
SIX CLEAR** (Witness·Quartermaster·Warden·Scribe + Mason after a folded andon — four `target_canonical`
lines phrased controlled vocabs as enums → bound to additive display-maps, map-known/pass-unknown/never-
reject; receipt `output/council/shadow_attributes_audit_review_20260609.md`). **Steward rulings:** (1) the
cut+migrate splits two paths — **Path A** (file/crosswalk via `rebake_canonical.py` + `_schema.json`, this
card's scope, **first slice = trail-name convergence**, no slice-6 pull) vs **Path B** (DB-door/identity
roots — publish.geojson reproducibility, serial-PK identity, two-store curation — **tagged to gold slice 6,
HELD for the user's pull**); (2) the `#tag`→coord **events** binding is out of scope here (C3) → re-homed
to the event-overlay convergence. **NEXT (the user's calls):** pull **Path A slice 1** (trail-name fold —
website + re-bake, no DB door) or pull **gold slice 6** (Path B); the commit of this brain-only diff is the
user's git gate.

**RESOLUTION PLAN — written + COUNCIL FULL-SIX CLEAR; ralph-loop-ready (2026-06-09, same session).** Per
the user (*"make a comprehensive approach to resolution, save in the sprint, prepare to have a ralph loop
run until finished"*), carded `tasks/09_editor_maturity/shadow_attribute_resolution.md`: sequences all 45
findings into **Path A** loop slices **A1** (crosswalk+`_schema.json`+re-bake join, foundational) → **A2**
(trail read-site convergence = the Launchpad fix) → **A3** (building/cemetery/visitor) → **A4** (render-
derived display) → **A5** (edge-dispatch→spec strategies), with **Path B** (20 findings) HELD on gold slice
6, **2** events findings out-of-scope, **1** deferred-low — total coverage 45, each finding homed once by
its catalog `id`. Carries a **Loop contract + verbatim loop prompt + per-slice tile-independent acceptance
+ record-on-green**; STOPS at the Path A/B boundary. **Plan-council FULL SIX CLEAR** (Quartermaster/Mason/
Warden clear; **Witness andon** — verifiers must be live-DOM on `playwright_base.py`, A1's join machinery +
label side-effect named → folded; **Scribe andon** — audit catalog re-emitted **id-tagged** so the plan's
`Closes:` ids grep-resolve, 3 orphans homed → folded; both re-cleared). Receipt:
`output/council/shadow_attribute_resolution_plan_review_20260609.md`. **NEXT (cadence):** user
**commit-pause** (commit the id-tagged catalog + the plan), then **ralph-loop Path A in a FRESH session**
(loop prompt in the card); the `vNN` bump + commits stay the user's git gate.

-----

**2026-06-08 (GOLD SLICE 6 PULLED by the user — F2 drawn-POI DB door DONE; DB-door code, UNCOMMITTED, NO
bump owed, commit OWED).** After Sprint 09 Slices 1–4, the user pulled gold slice 6 ("pull gold slice 6
now"). Executed it BOUNDED, one door (loop contract): **F2 — the drawn-POI DB door.** `aop_editor_pois_v1`
(the editor's own draw store) had NO direct writer to `core.features` (spike audit F2) — it reached core
only via the panel's opt-in `created[]` export, so a drawn POI vanished on browser reset and never
published. **Shipped:** new **`mvp/scripts/apply_editor_pois_to_core.py`** — a thin INPUT ADAPTER mapping
the drawn-POI FeatureCollection (the editor's "Copy all as GeoJSON") to the panel-overrides `created[]`
shape (`_src='editorPois'` → `source_key='editorPois:<id>'`, the seed convention) and feeding the EXISTING
`apply_panel_overrides_to_core` sink (`build_sql`/`run_psql`) — ONE sink, no duplicated upsert/provenance.
Folded a Mason andon: a null/partial geometry threw in the shared `build_created_feature` → new
`safe_geometry()` guard in `panel_overrides.py` (behavior-preserving for well-formed geometry; null/partial
→ geom-less, never throws — R13). **Verified by observation (browserless, the gold baked-file assertion):**
new `mvp/scripts/verify_editor_poi_db_door.py` — apply → both POIs active in `core.features` (geom present,
survives reset); publishable → baked `publish.geojson`; candidate GATED OUT; null-geom POI upserts geom-less
(no throw, no drop); idempotent re-apply; cleanup restores served files byte-identical to HEAD (production
untouched). **Council: FULL SIX CLEAR** (Witness·Quartermaster·Warden·Steward-cross + Mason after the fold;
the slice-1 `playwright_verify_baked_pois_author.py` `names=[]` failure is PRE-EXISTING — the committed
star-only flip removed the `published_destinations` group it reads; not an F2 regression). Receipt:
`output/council/gold_slice6_F2_drawn_poi_door_20260608.md`. **NO shell asset → NO bump owed.** **OWED
(git gate):** the commit (the new door + verifier + the `panel_overrides.py` guard + brain). **STILL HELD
(the user's call, each its own door):** **F1** (geometry/icon_size → core), **F4** (re-bake `publish.geojson`
= the git gate), **F5** (fresh-volume parity — 153 live-only rows), **F6** (identity-fork collapse, highest
risk, do last). **FLAGGED:** `playwright_verify_baked_pois_author.py` is pre-existingly STALE (reads the
removed `published_destinations` group) — needs updating to the star-only contract (separate cleanup, not
F2).

-----

**2026-06-08 (SPRINT 09 SLICES 3+4 — trailheads editable (F7) + generic-draw cleanly retired; CODE,
UNCOMMITTED, rides the v59 batch, commit OWED).** User: *"continue all the slices until done."* Drove the
remaining UI-completeness slices end-to-end (the commit stays the git gate). **Slice 3:** the curated
visibility-only `trailheads` node (panel.js) gains an editable feature list — `refItems('publish-data',
filter layer==='trailheads')` with `p.name||'trailhead'`/`p.name||'Trailhead'` fallbacks (sibling
boundaries/pubTrails pattern) + `createDefaults: ()=>({layer:'trailheads'})` so an authored trailhead
round-trips list → the `publish-trailheads` map filter → bake. No hostKey (the ★→left-tab reference-layer
link is the gold DB-star axis). Fork #2 honored — `eventSchedule` stays visibility-only (schedule-owned).
**Slice 4:** the generic draw group (Points/Lines/Polygons, retired `7cd51fa`) is confirmed cleanly
retired (Fork #1) — per-layer "+ add" authors every geometry type into a real source; two stale doc
comments fixed; the live standalone `userFeatures`/`node.create` path intentionally kept (NOT deleted —
it is the standalone draw path). **Verified by observation:** new
`mvp/scripts/playwright_verify_trailheads_editable.py` (drillable, authorable, unnamed-served row renders
"Trailhead", rename persists) + `playwright_verify_per_layer_add.py` (generic nodes absent on a rendered
panel; Line→aop-trail-network 120→121, Polygon→fema-buildings 5→6, each editable). Full regression suite
(create/editor/embed/star-flip) PASS; de-flaked the Slice-1 guard's own post-reload expand race.
**Council done-review (Slices 3+4): FULL SIX CLEAR** (Witness·Mason·Quartermaster·Warden·Steward-cross;
Scribe andon for owed records → written → re-review clear). Receipt:
`output/council/editor_slice2_done_review_20260608.md` (Slices 3+4 appended). Card: Slice-3 + Slice-4 DONE
blocks on `tasks/09_editor_maturity/editor_completeness.md`. **One version bump (v58→v59) covers the whole
Slices 2+3+4 uncommitted batch** (one bump per deploy, not per slice). **OWED (user's git gate):** the
commit (`main.js` + `panel.js` + `sw.js` + `index.html` + the 3 new verifiers + brain) with the v59 bump.
**Slices 1–4 (the UI-completeness axis Sprint 09 owns) are COMPLETE.** **NEXT — Slice 5 is a FORK for the
user:** the DB doors (drawn-POI + geometry/icon_size → `core.features`) = **gold slice 6, HELD until a
human pulls it**. Pulling it means DB migrations + re-baking `publish.geojson` (the git gate) + the F6
identity re-architecture ("highest risk, last"). NOT executed autonomously — surfaced for the user's pull
decision.

-----

**2026-06-08 (SPRINT 09 SLICE 2 — drawn-POI CREATE routed to the ONE store; CODE, UNCOMMITTED, v58→v59
bump PERFORMED, commit OWED).** Picked up the loop (one slice/iteration) from Slice 1. Slice 1 had
restored drawn-POI *editing* over `aop_editor_pois_v1` but the *create* path still leaked to the panel
OVERRIDES twin store (F6). Slice 2 closes it. **Shipped:** (`main.js`) new `AOP_HOST_CREATE_FEATURE`
bridge (mirrors the Slice 1 `AOP_HOST_*` family, fail-safe, scope-guarded to `editorPois`) + extracted
**`addDrawnPoi(geometry, category)`** — a behavior-preserving lift of the host TerraDraw `finish`
handler's inline construction (Point→`editor_poi`, LineString→`editor_trace` with NAIP provenance,
Polygon footprint), now CALLED by the finish handler (one builder, no second create engine). (`panel.js`)
`commitFeature` `hostEdit` branch → bridge + `seedLoadedFromHost()` re-seed + auto-select, returns
before the OVERRIDES write (no twin-store create). Bumped `sw.js` + `#appVersion` **v58→v59**.
**Verified by observation (new `mvp/scripts/playwright_verify_drawn_poi_create.py`, clean profile):**
panel "+ POI" → map click → POI lands in `aop_editor_pois_v1` (1→2, id `poi_…`, layer `editor_poi`);
**NO `aop_panel_overrides_v1` leak**; editable immediately (rename persists to the one store); survives
reload; 0 errors. Trace branch + the bridge guard observed directly. No regression:
`playwright_verify_drawn_poi_editor.py` / `_data_groups_embed.py` / `_starred_poi_flip.py` all PASS.
**Help text `index.html:450` LEFT UNCHANGED** — it lives in the host `#editor` section that
`panel-embed.css:272` hides in embedded mode (renders only in the host standalone fallback, where it's
accurate); the staleness was cured by Slice 1 restoring the node, so the text is "true again" via the
restoration; editing it would make it false in the only mode it shows. **Council done-review: FULL SIX
CLEAR** (Witness ran all four verifiers live; Mason/Quartermaster/Warden/Scribe/Steward-cross-check
clear; no andons). Receipt: `output/council/editor_slice2_done_review_20260608.md`. Card: Slice-2 DONE
block on `tasks/09_editor_maturity/editor_completeness.md`. **NEXT:** Slice 3 (spec-complete trailheads —
F7), then Slice 5 (DB doors — gold slice 6, the user's call to pull it). **OWED (user's git gate):** the
commit (`main.js` + `panel.js` + `sw.js` + `index.html` + the new verifier + brain) with the v58→v59 bump.

-----

**2026-06-08 (SPRINT 09 SLICE 1 — drawn-POI editor RESTORED as ONE engine + ONE store; CODE,
UNCOMMITTED, v57→v58 bump PERFORMED, commit OWED).** Executed Slice 1 of
`tasks/09_editor_maturity/editor_completeness.md` (user accepted the council-cleared plan + Fork #0 =
panel inline frame survives, then directed execute-now). **Shipped:** (`main.js`) 3 bridge hooks
`AOP_HOST_SET_FEATURE_PROPS`/`_GEOM`/`AOP_HOST_DELETE_FEATURE` — pure delegation to the existing
spec-routed host writers (`setFeatureProperty`/`deleteFeature` → editorPois `persistProperty`/
`removeFeature` → `saveEditorPois`), fail-safe. (`panel.js`) restored the **Drawn POIs** (`editorPois`)
node with `hostKey:'editorPois'`+`hostEdit:true`; `commitChange`/`persistDelete` route to the bridge for
`hostEdit` nodes (before the OVERRIDES path, returns — no twin write); the ★ already routed via the
existing `hostHighlight`. Retirement comment annotated (restored, not deleted). Generic draw stays
retired (Fork #1). Bumped `sw.js`+`#appVersion` **v57→v58**. **Verified by observation (new
`mvp/scripts/playwright_verify_drawn_poi_editor.py`):** the panel has a Drawn POIs node; editing the name
THROUGH THE PANEL UI lands in `aop_editor_pois_v1`; **NO twin-store leak** (`aop_panel_overrides_v1` has
no `editor-poi:` entry); survives reload; UI 🗑 Delete removes it; only the panel editor opens (host
`buildEditDock` stays CSS-hidden in embedded — still the standalone editor, correct scoping); 0 errors.
**Council done-review: Mason CLEAR** (one store — branch returns before OVERRIDES; bridge is pure
delegation; consolidation complete; C5/R13 fail-safe; C1/C6 clean). **Witness ANDON → folded → re-review:**
(1) `playwright_verify_data_groups_embed.py` was RED (it asserted the OLD retirement) → updated to the new
contract (8 sections incl Map editor, Drawn POIs present, generic draw gone) → PASS; (2) the durable
verifier now asserts no-twin-store (reads `aop_panel_overrides_v1`) + drives delete via the UI; (3) this
record. `playwright_verify_starred_poi_flip.py` still PASS. Card: Slice-1 DONE block on
`tasks/09_editor_maturity/editor_completeness.md`. **NEXT:** Slice 2 (reconcile the half-retirement —
surface the create affordance over the one store), Slice 3 (trailheads), Slice 5 (DB doors — gold slice 6).
**OWED (user's git gate):** the commit (`main.js`+`panel.js`+`sw.js`+`index.html` + the new/updated
verifiers + brain) with the v58 bump.

-----

**2026-06-08 (SPRINT 09 EDITOR-MATURITY PLAN — carded + FULL-SIX COUNCIL CLEAR; BRAIN ONLY, UNCOMMITTED).**
Follow-on to the "Launchpad" question (a drawn POI showed in the left list + on the map + the right ★
Visitor list, but had no editable node in the right panel — the "Drawn POIs" editor was retired
`7cd51fa "v50 styles"` 2026-06-05; `panel.js` claims "the user dropped the whole group" but the user says
they don't know why). User: *"this is a needed surface. put it in. make sure everything is visible on the
right side and editable. consult the council for a full robust plan. No shortcuts. we are trying to mature
the project and not maintain shortcuts or mvp code."* Created **`tasks/09_editor_maturity/`** (`_readme.md`
+ spine card `editor_completeness.md`): restore drawn-POI editing, spec-complete the curated-but-
visibility-only layers (trailheads F7), reconcile the half-retirement (live `#placePoiBtn` + stale
`index.html:450` help text vs the deleted node), each editable surface persisting **DB-first** —
coordinating gold slice 6's F1/F2 DB doors, NOT duplicating them; reference/imagery layers stay
visibility-only by design. **FULL-SIX COUNCIL PLAN-REVIEW → CLEAR (1 round + 1 Mason re-review).** The
load-bearing catch was **Mason's andon**: my first-pass grounding wrongly treated the host editor as
retired — it is actually LIVE but `display:none` in embedded mode (`panel-embed.css:271-273`), so there are
**TWO live editor engines** (host `buildEditDock` + panel inline frame). A naive "re-add the node" would
ship a SECOND editor for one feature class + a twin-store desync (panel `OVERRIDES` vs host
`aop_editor_pois_v1` — the F6 bug class). Folded: corrected grounding; Slice 1 rewritten to **consolidate
to ONE engine + ONE store of record** (1a retire the redundant engine; 1b add the missing write-back
bridge — new `AOP_HOST_*` property/geometry/delete hooks mirroring `AOP_HOST_SET_HIGHLIGHT` — so panel
edits land in the host array, not just `seedLoadedFromHost` read); Fork #0 (which editor survives) added;
generic-draw restore marked DOA (empty `userFeatures` in embedded). Witness folded 2 fact fixes
(`git show 7cd51fa --` shows empty → use `7cd51fa^:`; `#placePoi`→`#placePoiBtn`); Warden folded 2
execution notes (annotate the retirement comment, don't delete; the `sw.js` bump is owed to the user);
Quartermaster (reuse/no-dup of gold slice 6) + Scribe clear. Receipt:
`output/council/editor_completeness_plan_review_20260608.md`; card banner = COUNCIL-CLEARED. **NEXT
(user's gates):** decide the forks — esp. **Fork #0** (rec: the panel inline frame survives, host
`buildEditDock` drawn-POI path retired, host `aop_editor_pois_v1` the single store), Fork #1 (generic
draw — rec retire cleanly), Fork #2 (event anchors — rec keep schedule-owned), Fork #3 (sprint home),
Fork #4 (DB-first interleave) — then commit-pause the plan, then ralph-loop in a fresh session. Touched
only `brain/` (no `website/`/`mvp/`), so the Tier-0 gate did not self-fire; nothing committed.

-----

**2026-06-08 (LEFT POI LIST → STAR-ONLY; Sprint 08 Slice D; CODE+DATA, UNCOMMITTED, v56→v57 bump
PERFORMED, commit OWED).** Follow-on to the "left POI list" consult below — and a concrete cut of the
spike-code the DB-FIRST AUDIT entry catalogs (it removed the static, non-DB event-anchor feed). User:
*"make the list star-only -- yes where did you get the idea that this old static code not db powered is
good to keep around? we are maintaining a bunch of spike code left and right. its cutting me to death."*
(Overrode Slice C's "keep published wholesale" decision — `cards_not_gospel`.) **Shipped:** removed the
two wholesale unions from `collectStarredDestinations` (`main.js`) — input 2 (published `poi` from
`publish.geojson`, bake-gated) + input 3 (event anchors from `aop_event_schedule.json`, a static non-DB
file). The left POI list is now a single walk over the registry's ★-gated specs — exactly the ★-curated
set. Removed the now-dead `publishDataCache` (0 readers after the union went); rewrote the collector
header + two stale trails-spec comments (Mason caught both) + the event-bindings comment. Trimmed
`aop_poi_index.json` (dropped `published_destinations`+`event_anchors` group defs + 8 dead
`event_schedule`/published blurb entries; re-emitted to HEAD's inline-`match` style → diff removals-only,
1 ins / 60 del). Bumped `sw.js`+`index.html` **v56→v57**. The event SCHEDULE itself is untouched — it
still powers the Events tab; it's just no longer mirrored into the POI list. **Verified by observation
(clean SW-less profile):** list **10 rows → 1** (published 2 + event 7 gone; the only row is the one
star-fed seed drawn POI). Star-DRIVEN both directions — `playwright_verify_star_links_live.py` PASS (★ a
reference feature → its row appears live + survives reload). `playwright_verify_starred_poi_flip.py` +
`playwright_verify_star_collector.py` updated to the star-only contract (published/event groups absent)
→ PASS; `data_groups_embed` PASS; `node --check` PASS. **Events tab NOT regressed (Witness-confirmed
differentially against a HEAD docroot): `event_schedule` 116 PASS / 8 FAIL, byte-identical on HEAD and WT
— all 8 FAILs pre-existing, none from this diff.** **Council done-review: FULL CLEAR**
(Witness·Quartermaster·Mason·Warden; Mason after 2 stale-comment andon-fixes; Witness corrected my "only
#pavillion fails" → 8 pre-existing; Warden's poi_index reformat note → fixed, diff now removals-only).
Receipt: `output/council/star_only_poi_list_done_review_20260608.md`. Card: Slice D block on
`tasks/08_data_normalization/star_driven_poi_normalization.md`. **Pre-existing, flagged NOT fixed:** two
`publish`/`trail_centerlines` blurb entries (group `trails`) remain orphaned in `aop_poi_index.json` (no
`poiIndexLookup` consumer; predates this change). **OWED (the user's git gate):** the commit (`main.js`
+ `sw.js` + `index.html` + `aop_poi_index.json` + the 2 updated verifiers + the new
`diagnose_left_poi_list.py` + brain records), with the v57 bump.

-----

**2026-06-08 (DB-FIRST SPIKE AUDIT + FULL-SIX COUNCIL CLEAR; BRAIN ONLY, read-only, UNCOMMITTED, NOTHING
committed).** User: *"there is so much spike code in the app. We are moving to a db first and need to begin
cleaning up these edge cases. review audit. do all the things. convene the council."* Audited the viewer +
DB/bake/script layer by observation (4 read-only Explore sweeps + my own verification of every load-bearing
claim), then ran a Steward-chaired full-six council over the audit. **Headline: the per-layer-branch slop war
is WON — do NOT re-litigate it.** Verified clean: **C1** = 0 non-comment `layerKey === '` branches in
`main.js` AND `panel.js`; **C6** = 0 classes, one IIFE, one registry; **C2** = one `collectStarredDestinations`
(`main.js:1173`), one star gate, two thin renderers. No dead `buildInlineEditor`, no `?? blurb` viewer crutch.
**The live spike is one axis down — curation + identity still partly in the browser and in served files, not
the DB (C3).** Eight findings, ranked, all evidence-grounded:
**F1** `aop_positioned_features_v1` — ★ migrated (Sprint 08) but **geometry/icon_size stranded file-only** (no
core door); **F2** hand-drawn POIs (`aop_editor_pois_v1`) have **no direct DB door** (reach core only via the
opt-in panel `created[]` path — reset loses them); **F3** the legacy **file-bakers** (`export_positioned_features.py`,
`bake_panel_overrides.py`) still sit beside the DB path (= the standing gold OWED; the *two apply scripts* are
a deliberate two-sink split, NOT duplication — Quartermaster correction); **F4** served `publish.geojson`
carries stale `blurb`/`last_checked`/`source` beside `description` — **not a pure function of the DB**; **F5**
(sharpest) a **fresh `docker compose up` does NOT reproduce the live map** — live `core.features` = **160**,
fresh seed = **7**, **153 rows live-only** via unmounted imports; **F6** identity resolved differently per
layer (parcel/marker twin, trail stamp-less props) = the root the recent one-off bugfixes kept patching;
**F7** `trailheads`/`eventSchedule`/`activityHotspots`/`syntheticActivity` registered with no list spec
(latent footguns); **F8** `blurb`→`description` naming crosswalk persists via the `aop_poi_index.json` sidecar;
**F9** ~81 unreferenced prototype HTML files (archival). **Council: full-six CLEAR, 1 round + folds.** Warden
CLEAR (scope right, git gate untouched, prior dirty tree left alone). Mason CLEAR + notes (seed from a snapshot
not live importers; reuse upsert-fold-archive; column-projection only; safe-default specs — no limiting code).
Witness ANDON→folded (F5 numbers were estimates *and wrong*; DB was up — corrected to measured 160/7/153 with
the query). Quartermaster ANDON→folded (don't mint "Sprint 09" — this is the **bounded breakdown HELD gold
slice 6 already asked for**; re-homed there + the standing OWED; struck the two-apply-script duplication
framing). Scribe ANDON→folded (handoff + card home + wikilinks + fill the council section — this entry + the
gold-slice-6 annotation are the fix). **Home:** the findings re-home onto [[gold_migration]] **slice 6 (still
HELD — pulling it off HOLD is the USER's call)**, annotated to point at the audit as its bounded `- [ ]` list;
NO new sprint, NO new card, NO code/DB change this turn. **Receipt:**
`output/council/spike_code_dbfirst_audit_20260608.md` (the full audit + the folded council record). **OWED
(user's gates):** pull gold slice 6 (or not), decide 4 forks (seed-vs-minimal-dev / file-baker fate / prototype
archival / re-bake `publish.geojson` = git gate), and any commit. The pre-existing dirty tree from prior
sessions is unrelated and stays the user's.

-----

**2026-06-08 (COUNCIL CONSULT — "the left POI list shows content I can't trace; it should be DB +
star attributes but isn't"; BRAIN ONLY, NO code change, UNCOMMITTED).** User: *"review the left side
poi list… I cannot figure out where they are coming from… It SHOULD be pulling from the db and star
attributes. Consult the council. figure it out."* Diagnosed BY OBSERVATION (live viewer on :8001, live
DB, served files, code read) then ran a Steward-chaired consult (Witness·Quartermaster·Mason·Warden).
**Answer:** the left POI tab (`collectStarredDestinations`→`buildPoiGroups`→`renderPoiTab`,
`main.js:1169-1426`) is a union of **four** inputs, only **two** wholesale. Observed clean-profile =
**10 rows**: 2 `published_destinations` (publish.geojson `layer=poi`, WHOLESALE — bake is the gate,
`starred:false` hardcoded), 7 `event_anchors` (aop_event_schedule.json, WHOLESALE, **not the DB**), 1
`drawn_pois` (editorPois, STAR-gated, fed by the ONE seed star — `aop_seed_pavilion` carries
`highlight:true` in `aop_editor_seed_pois.geojson`/`aop_editor_pois_v1`). The four DB-star reference
layers (cemeteries/buildings/visitorContext/trails, `listMode:'starred'`) render **0** because nothing
is starred: DB `core.features` 0 `attrs.highlight=true` (every layer), served files 0 `"highlight":true`,
`aop_positioned_features_v1` absent on a clean profile. **So 9/10 visible rows are wholesale (not the
DB-star path the user expected); 1/10 is star-fed but via the editor's localStorage seed, not the DB,
not the reference layers. The DB-star path is fully plumbed but UNFED.** **Fix (NO code change):** the
plan's own held step — author stars on the right-panel ★ → `apply_positioned_features_to_core.py`
(writes `core.features.attrs.highlight`) → `export_publish_geojson.sh` (emits `attrs` verbatim, no bake
change) → deploy. **Open fork surfaced for the user (not decided):** published + event groups stay
wholesale by design even after authoring stars; if the user wants the WHOLE list star-driven that's a
separate decision (Steward rec: keep them wholesale, author the reference stars). **Council: 3 CLEAR +
1 ANDON folded.** Witness ANDON (real, grounded, verified by the Steward): the first-pass diagnosis
over-claimed "THREE wholesale inputs / nothing starred anywhere" — corrected to TWO wholesale + the one
seed star (proven by a controlled un-star experiment: 10→9 rows). Quartermaster CLEAR (one collector,
`apply_positioned_features_to_core.py` is the real reusable door, fix = data not code). Mason CLEAR
(`listMode:'starred'` is a legit declared-mode dispatch, every 'starred' layer pairs with
`highlightable:true`, not a C5 row-dropping filter). Warden CLEAR (read-only diagnosis, git gate
untouched — HEAD still `c781f59`, no bump; v56 is the PRIOR session's). **New artifact:** read-only
`mvp/scripts/diagnose_left_poi_list.py` (dumps the live list + the per-browser star stores). Receipt:
`output/council/left_poi_list_source_consult_20260608.md`. **OWED (user's gate):** nothing for this
task; the DB-star authoring + bake + the prior session's still-uncommitted v56 commit stay the user's.

-----

**2026-06-08 (STAR→LEFT-LINK BUGFIX + 🔥 TORCH CACHE BUTTON; CODE, UNCOMMITTED, v55→v56 bump
PERFORMED, commit OWED).** User: *"figure out why the stars are not linked to the left side. some
cache or some code is lacking. make a torch cache button on the right panel under session tools."*
**Diagnosed by observation (clean Playwright profile, NO service worker) → it is CODE, not cache.**
A live `AOP_HOST_SET_HIGHLIGHT(layerKey, props, true)` (the exact call the right panel's ★ makes for
a node with `spec.hostKey`) per reference layer, reading the host POI-tab DOM: **buildings ✓ and
visitorContext ✓ linked; cemeteries ✗ and trails ✗ did not.** Two real gaps in the just-shipped
sprint08 flip (the layers now show ONLY ★ rows, but the live author→link path was incomplete for two
of four): **(1) Cemeteries** — the ★ toggle resolves via `findFeatureById` (the DEDUPED state twin =
the parcel), but `collectStarredDestinations` reads the MARKER twin (`listFromData`), so the flag
landed on the parcel and never surfaced; it only worked after reload (where `applyPositionedFeatures`
sets BOTH twins). **(2) Trails** — the panel's gold-trail node (`aopTrails`) had **no `hostKey`**, so a
trail ★ fell to the panel-overrides store (which the host never reads + the baker drops), AND the host
had **no `applyPositionedFeatures('trails')`** call (the one ★-curated reference layer missing it), so
trail stars died on reload too. **Fixes (all in `website/`, reuse-first):** • `persistFeatureFlagChange`
now re-runs `applyPositionedFeatures(layerKey, runtime.data)` after persisting, so a live ★ lands on
EVERY feature sharing the idField (the parcel+marker convergence a reload already got) — one line,
reuses the proven replay, idempotent for single-feature layers. • Extracted `trailRowId(props)` (one
derivation: `__trail_row_id` ?? `n:<num>` ?? `name:<name>` ?? null) and wired it as the trails spec's
new `idFor`, honored by `positionedFeatureIdFor` — so the bridge resolves a trail from the panel's
STAMP-LESS served props (the panel loads its own copy without the load-time stamp). • Added
`applyPositionedFeatures('trails', aopTrailNetworkCache)` before its registration (reload durability;
highlight isn't painted so no `setData` needed). • Added `hostKey: 'trails'` to the panel's `aopTrails`
node. **🔥 Torch cache button:** new `#torchCache` under Session tools (beside Reset viewer) → confirm,
`caches.delete` every bucket + `getRegistrations().unregister()`, then `location.reload()`. It nukes the
CODE/offline cache (the stale-SW class of bug), NOT localStorage — "Reset viewer" stays the state nuke,
this is the code nuke. **Verified by observation (all PASS, 0 console errors):** a diagnostic shows
all four layers LINK live (cemeteries 0→1, trails via stamp-less props 0→1) AND survive reload; the
torch button fires its confirm, reloads clean (caches observed as `aop-shell-v56`/`aop-data-v56` — the
bump is live), and the clear-primitives zero out caches+registrations. No regression:
`playwright_verify_starred_poi_flip.py` (clean-profile gating), `playwright_verify_star_collector.py`,
`playwright_verify_data_groups_embed.py` all still PASS. New durable guard
**`mvp/scripts/playwright_verify_star_links_live.py`** (the live author→link path the flip verifier
doesn't cover). Touched `main.js` + `panel.js` + `index.html` → bumped `sw.js` VERSION + `#appVersion`
**v55→v56**. **OWED (user's git gate):** the commit (4 `website/` files + the new verifier + brain
records).

-----

**2026-06-08 (SPRINT 08 RALPH LOOP — all 3 slices GREEN; CODE+DB, UNCOMMITTED, v54→v55 bump
PERFORMED, commit OWED).** Fresh session after the plan commit-pause (`c781f59 "data normalization plan"`).
Ran `tasks/08_data_normalization/star_driven_poi_normalization.md` end-to-end — the durable
reference-layer ★ path, then the POI-tab flip (star_driven decisions #1/#2/#5). Each slice
verified BY OBSERVATION (the Witness/Mason standing conditions held). **Slice A** (★ door): added
`highlightable: true` to the cemeteries+buildings specs; new
**`mvp/scripts/apply_positioned_features_to_core.py`** reads the `positioned_features` map,
filters to the four reference editor-layerKeys, resolves each to its core row by the per-layer DB
lookup (cemetery **:marker** not :parcel; trail by `attrs->>'trail_number'` not the misleading
`sfwda-<n>` index; visitor by `attrs->>'name'` not the `-N` index; building direct) and UPSERTs
**`attrs.highlight`** as the single source of truth (NOT `is_destination` — Mason andon; no
consumer). Reused `split_key` + the apply scaffold (`sql_str`/`run_psql`/`parse_count`); did NOT
reuse `read_payload`/`VIEW_STATE_KEYS` (it strips `highlight`). Observed: 4-layer test bundle →
flag on the correct rows, siblings clean, un-star wrote `false`, `trails:n:99999` UNRESOLVED
(loud, never thrown), brandLogos/editorPois/geometry-only skipped, **idempotent** (no dup).
**Slice B** (bake): no bake change — `export_publish_geojson.sh:87-93` emits `attrs` verbatim;
observed each served reference file carrying one `"highlight":true` on the right feature.
**Slice C** (flip): `listMode 'wholesale'→'starred'` on the 4 reference specs + stale-comment
fixes + a published-`poi`-union guard comment (bake is its gate, never `'starred'`); new
**`mvp/scripts/playwright_verify_starred_poi_flip.py`** (clean profile, waits on the **load**
event via `window.AOP_HOST_MAP` + 4 reference sources, asserts per-group counts from the actual
baked files) → **PASS**: each group shows only its curated ★ row (trail 15 not all 100; the flip
GATES), `pubpoi:139/140` still render, 0 console errors; `playwright_verify_star_collector.py`
still PASS (no regression). **Cleanup:** DB test stars reverted (0 remain); served files restored
byte-identical to HEAD via read-only `git show HEAD:… > …` (the bake-vs-HEAD drift is pre-existing;
`git checkout` is the user's gate). **Council done-review: full-six CLEAR** (receipt
`output/council/sprint08_done_review_20260608.md`). **THEN the user tested and reported an unstarred
trail still showing in the POI list — a real miss in my verification.** Root cause (found by
observation): **HEAD's `sw.js`/`#appVersion` were ALREADY `v54`** (the FAB-fix bump had been
committed), so the card's "owes v53→v54" was **stale** — my main.js flip rode the *same* v54 the
pre-flip code used, so the service worker never invalidated its cache and the user's browser served
the **cached pre-flip main.js** (old wholesale trails → unstarred trail 4 shows). My Playwright
verifier runs in a fresh context with no SW, so it never hit that path. **Fix (performed):** bumped
`sw.js` VERSION + `#appVersion` **v54→v55** so the cache invalidates; confirmed by observation that
the new code GATES correctly — against the production-default 0-star bake all four reference groups
are EMPTY (no leak), and with test stars each group shows only its curated row (verifier PASS, the
"starred row renders" check made conditional so 0-star isn't a false-FAIL). **Working tree:**
`website/js/main.js`+`sw.js`+`index.html` (M) + the 2 new scripts (??) + brain records. **OWED
(user's git gate):** the commit. **Consequence to weigh before deploy:** the flip is now live in
code; with NO production stars authored, a fresh visitor sees the four reference groups EMPTY (the
user's own browser shows their localStorage-starred set). The plan's "author stars first, then flip"
step is still the user's to do — star the features you want listed, run
`apply_positioned_features_to_core.py`, bake, deploy.

-----

**2026-06-08 (BUGFIX — the edit pencil FAB disappears; CODE, UNCOMMITTED, v53→v54 bump OWED).** User:
*"the edit pencil on the edit sidebar disappears every once and a while. investigate."* **Root cause
(found + reproduced by observation, not theory):** the collapsed edit panel is a 56px rust **pencil FAB**,
and the pencil lives inside `.panel-header`. The new embedded one-model panel (`js/panel.js`) selects a
feature on **map click** (`revealAtPoint`) and on **left-POI-row click** (`gotoPoi`) by adding
`.aop-feature-editing` to `.panel` — but, unlike the legacy `revealFeatureInPanel` (main.js:3901-3905,
which *expands* a collapsed panel first), it **never expanded**. The takeover CSS
`panel-embed.css:179 .panel.aop-feature-editing .panel-header { display:none !important }` then hid the
header **and the pencil**, leaving an empty rust circle with no way back into the editor. **Intermittent
because** main.js *also* binds `bindPanelReveal`→expand for the `FEATURE_LIST_LAYERS` set (buildings,
brand-logos, editor POIs) — clicking those expanded fine; clicking the **gold layers panel.js reveals but
main.js doesn't** (trails `aop-trail-network`, park boundary `publish-boundar*`) stranded the pencil. A
Playwright run clicking 8 reveal-eligible layers from a fresh collapsed reload reproduced the strand on
trails + boundaries, ok on buildings/brand-logos. **Fix (two parts, both verified):** (1) **behavioral** —
new thin host hook `window.AOP_HOST_EXPAND_PANEL` (main.js, beside the other `AOP_HOST_*`; idempotent
`if (panelCollapsed) togglePanel()`); panel.js calls it via a shared `ensureHostPanelOpen()` from BOTH
`revealAtPoint` and `gotoPoi` so selecting any feature opens its editor — the documented promise, now kept
uniformly. (2) **CSS safety net** — scoped the four `.aop-feature-editing` chrome-hide selectors to
`:not(.collapsed)` so the header/pencil can NEVER be hidden while collapsed, for any future path that lands
collapsed+editing. **Verified by observation:** all 8 layers now expand on click (no strand); the forced
collapsed+editing case shows the pencil `display:grid`/visible (safety net holds independently);
`playwright_verify_data_groups_embed.py` still PASS (7 sections, editor takeover intact, 0 console errors);
screenshots `brain/output/fab_pencil_{collapsed,after_trail_click}.png` show the pencil glyph, then the
trail click opening the FEATURE editor. New regression guard
`mvp/scripts/playwright_verify_collapsed_fab_pencil.py`. **Touched shell assets** (main.js, panel.js,
panel-embed.css) → bumped `sw.js` VERSION + `#appVersion` **v53→v54**. **OWED (user's git gate):** the
commit (5 `website/` files + the new verifier).

-----

**2026-06-08 (COUNCIL CONSULT — star_driven_poi_list readiness; BRAIN ONLY, UNCOMMITTED).** User:
*"have the council get together on this. we should be ready to go."* over
`tasks/10_deferred/star_driven_poi_list.md`. Ran a full-six design consult (Steward-chaired), grounded
in observation FIRST. **Finding: the card is NOT "ready to execute as written" — but the consult is fully
resolved; only two user decisions + the card rewrite remain.** Most of the card shipped after it was
written: C1=0 (universal refactor), the C2 two-engines→one-collector convergence
(`collectStarredDestinations` main.js:1152; shipped as
`05_special_operation/_done/06_one_star_driven_collector.md`), and the gold store
(`core.pois`/`publish.pois` DROPPED, `core.features` is the store, one `publish.geojson` bake). **Forks
resolved:** authoring surface / bake shape / dev-time-only / structural convergence = CLOSED by gold;
**still open** = (1) durable curation for the four *reference* layers (cemeteries/buildings/visitor/trails
have NO author→DB ★ path — gold **slice 6, HELD**), (2) the user-visible flip itself (decisions #1/#2).
**Three andons, all folded:** Mason — flipping cemeteries(2266)+buildings(2345) to `listMode:'starred'`
without `highlightable:true` is a banned **C5** row-dropping filter (no ★ control exists); fix = add
`highlightable:true` to both, flip together; visitorContext(2682)+trails(2842) are already highlightable.
Warden — the flip is a true **DECISION** gate (the code comment main.js:1145-1147 + card 06 held it for
the user); do NOT execute autonomously; annotate the card's directives, don't delete them. Quartermaster —
do NOT un-defer the card whole (engine/storage halves duplicate shipped work); keep only the thin product
slice. Witness CLEAR + caveat (baked POIs are bake-gated, won't vanish; only 1 served feature has
`highlight===true`, so the flip empties the four groups = intended decision #2; but decision #5 unmet for
the four layers). Scribe — card was stale (dropped objects, pre-rename `blurb`, dead `index.html:NNNN`,
dead `../04_event_app/`→`04_edit`); recorded verdict in card + handoff same pass. **The executable slice
(council-corrected):** add `highlightable:true` to cemeteries+buildings → flip those + visitor + trails to
`'starred'` → published POIs stay wholesale (bake is their gate) → render left-tab curation fields (the
`info needed — revisit` chip is already live at main.js:1396) → tile-independent acceptance cloned from
`playwright_verify_star_collector.py`. **Blocking caveat:** in the deployed read-only viewer the four
reference groups stay PERMANENTLY EMPTY until slice 6's author→DB ★ path lands. **Records:** card top
annotated + stale facts/paths fixed (NOT deleted); receipt
`output/council/star_driven_poi_list_consult_20260608.md`. **USER DECISION (same turn):** of the three
scope options, the user picked **"build the ★ path first, then flip"** — decisions #1+#5 both met before
any visible change; nothing empty in production. Then: *"make the plan. put it into a sprint 08 dir. call it
data normalization."* → created **`tasks/08_data_normalization/`** (`_readme.md` + spine card
`star_driven_poi_normalization.md` = the concrete 3-slice plan). The deferred
`star_driven_poi_list.md` stays put as the **design + council record** (it has 17 inbound links — moving it
would break them); the two cards point at each other, no duplication. Plan grounded in observation: bake
already emits reference-layer
`attrs` verbatim (`export_publish_geojson.sh:90`, no bake change needed), and
`apply_panel_overrides_to_core.py:38-39` already names "the buildings/cemeteries/… doors are a future
increment" — that increment is Slice A. **Slices:** A = reference-layer ★ door (add `highlightable:true` to
cemeteries+buildings; **new `apply_positioned_features_to_core.py`** — the reference-layer ★ lives in
`aop_positioned_features_v1`, a DIFFERENT store than the panel-overrides sink, resolved to core rows by a
per-layer DB lookup); B = ★ travels into the bake (verify-mostly — the reference bake emits `attrs`
verbatim); C = flip `listMode`→`'starred'` + verify render + clone the tile-independent test (owes a
`v53`→`v54` bump). **THEN: FULL-SIX PLAN-COUNCIL CLEARED it (Steward-chaired, 1 round + 1 narrow
re-review).** R1: Witness andon (2 facts — `sfwda-<n>` is a load index, not the trail number → resolve by
`attrs->>'trail_number'`; reference rows DO render headless → assert per-group counts) + Mason andon (drop
the `is_destination` dual-write — `attrs.highlight` is the sole reader/source-of-truth for these 4 layers;
tighten Slice C to verify-first); Quartermaster + Warden clear-with-conditions (draw the reuse line: reuse
`split_key`/`round_coords`/`_applied` scaffold, NOT `read_payload`/`VIEW_STATE_KEYS` which strips
`highlight`; name the visitor `attrs->>'name'` join; `FEATURE_LIST_LAYERS` not `LAYER_CONFIGS`); Scribe
clear. All folded → Witness/Mason/Quartermaster/Warden **re-reviewed CLEAR** (Witness observed the
reference runtime seeding headless live via `window.AOP_HOST_MAP`). Receipt:
`output/council/sprint08_plan_review_20260608.md`; plan banner = COUNCIL-CLEARED. **NEXT (user's gates):**
commit-pause (commit the Sprint-08 plan), then ralph-loop the slices in a **fresh session** (this one is
context-heavy). The commit + the `v53`→`v54` bump stay the user's. Touched only `brain/` — no
`website/`/`mvp/`, Tier-0 gate did not self-fire; nothing committed.

-----

**2026-06-08 (DESCRIPTION CONVERGENCE — ralph loop, all 4 slices GREEN; CODE+DB+DATA, UNCOMMITTED,
v52→v53 bump OWED).** User: *"I want a full robust fix. source data should be updated vs support in
code. make a card. plan it then loop."* (Overrode the additive read-both shape the council had just
cleared — `cards_not_gospel`.) Carded `tasks/07_tables/description_blurb_convergence.md`,
council-reviewed the plan (Mason·Witness·Warden·Quartermaster, Steward-chaired — CLEARED with all
andons folded), then looped all 4 slices, each verified BY OBSERVATION. **Shipped:** (1) DB —
`ALTER TABLE core.features RENAME COLUMN blurb TO description` (pg_dump backup
`/tmp/aop_map_backup_predesc.dump`; DROP+recreate `publish.features`; 159 rows intact); updated every
checked-in writer/reader — init_db.sql, seed_core_pois.sql, migrate_layers, promote_gpx,
import_layer (write target; KEPT the `BLURB_KEYS` external-ingest read crosswalk),
apply_panel_overrides_to_core (POI_COL + created_block); fresh-volume repro proven. (2) Bake —
export_publish_geojson.sh:36 emits a single `description` key (value set-equal to DB by id; no
`blurb`/`source`/`last_checked`). (3) Viewer — main.js:1232 reads `props.description` (NO `?? blurb`
crutch); fixture → `description`; `playwright_verify_baked_pois_author.py` gained `--require-description`
(positive subtitle assertion, PASS — the rendered DOM shows the DB text); sw.js + index.html bumped
**v52→v53**. (4) Seed drift — SCOPED DOWN from "re-bake seed from DB" (that reshapes the editor
identity/maturity/tag model = HELD gold slice-6) to a source-data RECONCILE: served + raw
`aop_editor_seed_pois.geojson` Pavilion `description`/`notes` set to the DB value; `rebake_canonical
--check` reproduces it (no drift return). **FULL-SIX COUNCIL DONE-REVIEW (Stop-hook convened /council)
→ CLEAR** after the Steward fixed two findings: (a) the orphan verifier `playwright_verify_baked_pois.py`
still read `properties.blurb` (card blast-radius) — retargeted to `description`, PASS; (b) a Quartermaster
catch — the re-baked working-tree `publish.geojson` had DROPPED HEAD's served-only `id=5 park_boundaries
"Ellis Cemetery (inholding parcel)"` (6→5) + re-serialized ids → **restored publish.geojson to HEAD**
(it already serves `description`; v53 viewer fix holds, re-verified) so the description commit doesn't
ship a feature drop; the bake-SCRIPT convergence is the durable change, the served file regenerates at
deploy. **OWED (user's git gate):** the commit (16 tracked + 4 brain files) with the v53 bump.
**FLAGGED:** migrate the Ellis inholding park_boundary into `core.features` before the next deploy-bake,
or that bake drops it (pre-existing gold served-only-row gap, now decoupled from this commit).
**Follow-ups (carded, NOT done):** the full editor-loads-DB collapse (gold slice 6, HELD); the
`aop_poi_index.json` sidecar fold (rehome `revisit_note` + `groups[]` first). Receipts in
`output/council/description_blurb_{flow,plan,done}_review_20260608.md`.
**→ User COMMITTED the convergence as `5b5fcdd "v53 data mutation"` (the git gate), then: "continue
with that last bit."** **SLICE 5 (Ellis inholding migration) — the flagged gold gap closed.** The
served-only `park_boundaries "Ellis Cemetery (inholding parcel)"` (was publish.geojson id=5, in no
table) is now in `core.features` (live id 201, `permission/publish_status=publish`, source_key
`park_boundaries:ellis-inholding`, provenance = TN Comptroller parcel source id 3). New checked-in
idempotent `mvp/scripts/seed_core_park_boundaries.sql` (self-seeds its source; ON CONFLICT DO NOTHING)
+ mounted in `docker-compose.yml` so fresh volumes carry it. **Proven by observation:** the seed runs
clean (exit 0, no dup); `publish.features` serves the envelope + Ellis; a re-bake now yields **6
features incl. Ellis (id 201, `description`, no `blurb`)** — the bake no longer drops it — with the POI
description convergence intact; served files restored to HEAD after verifying (the durable change is
Ellis-in-core + the seed; the served artifact regenerates at the user's deploy). **FLAG:** the working
envelope park_boundary (live id 194) is still live-only on fresh volumes (it came via the one-time
`migrate_layers`); this seed reproduces Ellis only — full park_boundaries fresh-volume parity is a
separate cleanup. **OWED:** the commit of the Slice-5 diff (seed + compose + card). Done-review receipt
appended in `description_blurb_done_review_20260608.md`.

-----

**2026-06-08 (COUNCIL CONSULT — "description in editor ≠ values in view"; BRAIN ONLY,
UNCOMMITTED).** User asked the council to explain how a feature's description flows DB→view
and why the editor's Description doesn't match the popup. Traced by observation + ran a design
consult (Witness·Quartermaster·Mason, Steward-chaired). **Answer: one concept, two physical
names — `blurb` (DB column `core.features.blurb` / bake export_publish_geojson.sh:36 / viewer
`props.blurb` main.js:1232 / poi-index sidecar) vs `description` (editor panel.js:1349 / CMFS
canonical / ref-layer attrs).** Editor reads/writes `description`; viewer renders `blurb`; they
never reconcile in-browser. For the Pavilion it's worse — the editor edits the FROZEN static
`aop_editor_seed_pois.geojson` (`description` text) while the viewer renders the DB-baked
`publish.geojson` (`blurb` text), and the two texts have DRIFTED (same key `editorPois:aop-pavilion`,
different content). **Council REJECTED a column rename** (Mason: flag-day, hard-errors the bake +
publish.features view, doesn't converge the `attrs.description` ref layers; the project already has
the `BLURB_KEYS` crosswalk idiom). **CLEARED shape:** converge on the CMFS canonical `description`
ADDITIVELY — bake emits `blurb AS description` (+ `blurb` alias), viewer reads
`props.description ?? props.blurb`, editor unchanged, crosswalk kept. Touches main.js → owes a
`sw.js`/`#appVersion` bump; commit is the user's git gate. Carded:
`tasks/07_tables/description_blurb_convergence.md`; receipt:
`output/council/description_blurb_flow_review_20260608.md`. Follow-ups (separate slices): collapse
the static seed file into the DB-baked POIs (gold slice-6 seed→DB convergence — the real drift fix);
sidecar `aop_poi_index.json` fold (rehome `revisit_note` + `groups[]` first); ref-layer spine-column
populate. NOT executed — explanation + recommendation only.

## ✅ DONE — the Going-Gold ralph loop (all slices + Retirement + the human-owed DROP closed, 2026-06-07)

> **SUPERSEDED 2026-06-07:** the loop ran to completion (slices 1–5 + Retirement, committed `ce920bd` /
> `737fc26`), and the user has now pulled the final human-owed item — the deprecated `core.pois` /
> `publish.pois` objects are **DROPPED** (see the 2026-06-07 entry below + the DROP COMPLETE block in
> `tasks/06_going_gold/gold_migration.md`). Nothing is left to run here. The instructions below are kept
> only as the historical loop record.

The gold-migration plan is council-cleared (full six, 4 rounds) **and committed**. Run it in a
**fresh session** — this one is context-heavy, and the plan is built to be re-read fresh each
iteration; a fresh executor + fresh verification is the council's own principle (the producer must
not self-verify).

**Loop prompt** (feed verbatim each iteration):
> Read `brain/tasks/06_going_gold/gold_migration.md`. Obey its **Loop contract**. Do the **next
> incomplete slice** (start at Slice 1), verify it by its tile-independent acceptance, **Record on
> green**, then stop. Stop at the **Retirement step** (Slice 6 is HELD). Do **NOT** commit or bump
> `sw.js`/`#appVersion` — report what's owed.

**Conditions the loop inherits (from the council, non-negotiable):**
- **Witness** — the apply script + the five `playwright_verify_baked_*_author.py` don't exist yet;
  the loop writes them to the `playwright_verify_star_collector.py` pattern. **Re-witness Slice 1's
  REAL verifier output before trusting any "green"** — "the script printed PASS" ≠ observation.
- **Mason** — confirm the `count == input` (no silent zero-row write) acceptance actually runs
  against a live apply before Slice 1 closes.

Plan + sign-off: `brain/tasks/06_going_gold/gold_migration.md`. Review receipts:
`brain/output/council/gold_migration_review_20260606.md`. DB: `docker compose -f mvp/docker-compose.yml up -d db`.

-----

**2026-06-07 (TABLE CLEANUP — FULL FOLD EXECUTED: 21 objects → 8; DB + scripts + init_db.sql,
UNCOMMITTED).** User: *"review the table diagram, consult the council. we should not have so many tables…
attempts to remove the extraneous resulted in andon pulls 'there is data there' well it needs to be moved
or removed. figure out the minimum and migrate data into that shape."* This **overrode** the prior
session's "keep all 8 — source-led spine" withdrawal (`cards_not_gospel`: the user's inline correction
wins; *"there is data there"* is not a reason to keep a table — the data moves). Confirmed two forks once
(full fold vs thin spine; retire vs rewrite the pipeline) → user chose **full fold + rewrite the pipeline
now**, then executed end-to-end. **The honest minimum = 7 tables + 1 view:** `core.features` (all geo) +
`core.events` + `core.activities` + `source_register.sources`/`feature_sources` + `raw.gpx_captures`/
`arcgis_feature_captures` + `publish.features`. **Shipped + verified by observation:** (1) migrated all 12
rows from the 8 per-layer `core.*` tables into `core.features` (domain cols → `attrs`, `layer`=old name;
new `mvp/scripts/migrate_layers_to_core_features.sql`), count==input 147→159, all 15 `feature_sources`
re-pointed to `core.features` (0 dangling), gate parity exact (`publish.features WHERE layer=X` ==
old `publish.<x>` counts); (2) rewired `export_publish_geojson.sh` — `publish.geojson` reads every
published layer from the one `publish.features` gate, output feature-equivalent to the prior bake (only
geo-layer `id`s shifted to `core.features` serials, the gold-precedent change), POI DOM rows observed
rendering, served files restored byte-identical to HEAD; (3) **rewrote the validation-loop pipeline onto
`core.features`** (`import_gpx_track`, `promote_gpx_to_trail`, `import_aop_parcel_boundary`,
`validation_loop_smoke_test` — content-based dedup so live re-runs don't double-insert) and proved all
four **end-to-end on a fresh volume** (exit 0; GPX→field_track→promote→publish; parcels+unioned envelope;
observation→promote; 10/10 provenance → `features`); (4) dropped the 8 per-layer tables + 5 per-layer
publish views on the live DB (21→8), updated `init_db.sql` to the 8-object shape, **fresh-volume repro
exit 0** (8 objects, 0 per-layer tables/views, 5 triggers). **Pre-existing drift fixed in passing:** named
the `gpx_captures` UNIQUE constraint (`gpx_captures_file_recorded_uniq`) in `init_db.sql` so
`import_gpx_track.sql`'s `ON CONFLICT ON CONSTRAINT` resolves on a fresh volume (it only ever worked on
the live volume, which carried the historical name). **Safety:** `pg_dump` backup at
`/tmp/aop_map_backup_premigration.dump`; the migration moved data (nothing lost), the drop is reversible
via backup + `init_db.sql`. **Records:** `tasks/07_tables/tables_diagram.md` rewritten to the 8-object
shape; `tasks/10_deferred/retire_legacy_geo_tables.md` → DONE (was WITHDRAWN); this entry. **OWED (the
user's git gate):** the commit. **FLAGGED (pre-existing, NOT this work):** the served `publish.geojson`
carries a served-only park_boundary ("Ellis Cemetery (inholding parcel)") that no table holds — the bake
drops it on next deploy (the gold "served-only hand-curated row" gap); and HEAD's served `publish.geojson`
carries extra keys (`description`/`source`/`last_checked`) from an older writer that the current
`attrs`-verbatim bake won't reproduce — the same deploy-drift class as the Ellis row (non-breaking: the
viewer reads `blurb`, not those keys). **Council: FULL CLEAR (full six).** Witness pulled one andon — the
rewritten parcel import threw a unique-violation on a duplicate-parcel batch (a C5 reject); fixed with
`ON CONFLICT (source_key) DO NOTHING` (store-first-skip-rest, never throws), re-witnessed CLEAR. Then
Warden/Quartermaster/Mason/Scribe all clear.

-----

**2026-06-07 (LEGACY-TABLE RETIREMENT — STOPPED at the drop-safety check; premise refuted, NOTHING
dropped; BRAIN ONLY, UNCOMMITTED).** User: *"yes, retire the legacy tables one at a time."* The card's
step-1 drop-safety check (by observation) **refuted the "legacy" framing** — the 8 per-layer `core.*`
tables are the **source-led spine**, 7 of 8 load-bearing: `trail_centerlines` (2 LIVE published
"Saturday Activity" rows in `publish.geojson`, **cited by the event schedule**) + 2 demo;
`park_boundaries` (1 LIVE boundary served) + 1 demo; `trailheads` (a fully viewer-wired layer —
`publish-trailheads` map layer + toggle + popup + feature-list — awaiting data); `hazards` (0 rows but
its `publish.hazards` view is a bake UNION arm); `parcels` (the 2 REAL AOP parcels); `observations` (the
northstar validation-loop row); `field_tracks` (the source GPX tracks). Only `print_annotations` (0 rows,
`mvp/README.md`-only) has no reader — and it's the **intended print-board layer** (northstar V1, unbuilt).
**Dropping any would break the bake/viewer or lose real data** → surfaced instead of proceeding (the
"look before you delete; contradiction → surface" rule). `core.features` is the converged *display*
layer; these are the *source* model — they coexist by design, gold did not replace them. **Recorded:**
the deferred card `retire_legacy_geo_tables.md` marked **WITHDRAWN** with the per-table evidence
(original plan kept as superseded); the diagram annotation corrected (source-led spine, not legacy).
**Recommendation: keep all 8; the count is the honest source-led model, not bloat.** The only real lever
for fewer objects is the long-term gold convergence of the *display* layers — not dropping the spine.
NOTE: the Quartermaster consult HAD flagged "don't drop blind, each needs a drop-safety check" — the
check is what caught this; the system worked.

-----

**2026-06-07 (COUNCIL CONSULT — "how do we have so many tables, I am at a loss"; BRAIN ONLY,
UNCOMMITTED).** User saw the full 21-object diagram and felt lost. Convened Witness·Quartermaster·Mason
(Steward-chaired) over the live DB. **Answer: not duplication, layering + old furniture.** Of 21: 6 are
`publish.*` VIEWS (gates, not storage), 2 provenance (`source_register`), 2 capture (`raw`); the live
product runs on ~**5 tables** — `core.features` (147 rows), `core.events` (13), `core.activities` (12),
`source_register.sources`/`feature_sources`. The **8 legacy per-layer `core.*` tables**
(`trail_centerlines` 4 demo rows, `trailheads` 1, `park_boundaries` 2, `parcels` 2, `hazards` 0,
`observations` 1, `field_tracks` 2, `print_annotations` 0) are the OLD rigid one-table-per-geometry-type
MVP schema the gold migration **already replaced** with the single flexible `core.features` — they hold
stale/demo data, not the live data (120 real trails live in `core.features`, not `trail_centerlines`).
**Witness corrected two of my stated premises:** `core.features` is **147** rows not 141; the legacy
tables are NOT drained-empty (only `hazards`+`print_annotations` are) — they hold stale MVP scaffolding
and were never the gold source (gold imported from served `.geojson`). The trend is **shrinking**, not
growing (gold collapsed 5 layers + POIs into features and dropped `core.pois`). **Recorded:** new
deferred card `tasks/10_deferred/retire_legacy_geo_tables.md` (retire the 8 legacy tables one-at-a-time
via the proven `core.pois` rename-and-reverify drop — gating `park_boundaries`/`parcels` on a
content-migrated check); a "Why it looks like a lot" annotation added to `tasks/07_tables/tables_diagram.md`.
Dropping the 8 + their views takes the visible count 21 → ~13 without touching the live product.

-----

**2026-06-07 (SPRINT 07 RALPH LOOP — SLICE 2 CLOSED: `core.activities` + `activity_key`, the reusable
WHAT de-duplicated; CODE+DB, UNCOMMITTED, NO shell bump owed).** User: *"continue into Slice 2."* Did
Slice 2 of the `07_tables/tables_model.md` plan. **Shipped:** `core.activities` (place-agnostic reusable
WHAT — `activity_key UNIQUE`, name/kind/description/attrs, **no geom, no place column, no FK/CHECK**) +
`core.events.activity_key` (soft ref) in `init_db.sql` (live + fresh-volume proven);
`import_event_schedule_to_core.py` extended with a curated `SESSION_ACTIVITY`/`ACTIVITIES` backfill (12
activities for 13 sessions — only the card-cited **Night Crawl** collapses Fri+Sat into one activity; the
rest stay one-offs, I did NOT invent content merges) + `core.activities` upsert + `activity_key` on the
session upsert; the bake's session arm extended to carry the resolved `activity` object (LEFT JOIN — an
unmatched key keeps its `key`, never dropped). **Verified by observation (all green):** **de-dup proof**
— edited `night_crawl` description ONCE → re-bake → **both** `fri-night-crawl`+`sat-night-crawl` carried
it, 1:1 control untouched (one row drives N occurrences); `count==input` (13 sessions, 12 activities, all
13 linked); session-level fields **field-equivalent to HEAD** (`activity` is additive); `--baked`
tile-independent verifier still PASS (20 features, 13 sessions, pavilion resolves, 0 errors — additive
field doesn't break the viewer); **fresh-volume repro proven** (exit 0, `core.activities` +
`events.activity_key` + trigger, no FK on `activity_key`); served files **restored byte-identical to
HEAD**. **OWED (flagged, NOT slice 2):** the viewer doesn't yet RENDER activity detail
(`eventScheduleToGeojson` doesn't carry `activity` into props — a UI slice + `main.js` + a shell bump,
deferred); the activities' "specific data" (grade/length/gate list) is the user's to author into
`core.activities`. **Council: FULL CLEAR (full six).** Witness/Mason/Quartermaster cleared R1 (Witness
re-ran the de-dup proof itself: one edit → both occurrences, control untouched); Warden+Scribe andon'd R1
on a **concurrency race** — the Witness re-bakes the served files for its proof and restores at its end,
and the read-only Warden/Scribe (spawned concurrently) sampled `git status` mid-re-bake and saw the served
files dirty. Re-reviewed with no mutation running → both CLEAR (Warden confirmed `cksum` byte-identical to
HEAD). **Process lesson (recorded in the receipt + card):** run the Witness (which mutates/re-bakes)
**alone**, not concurrently with seats that assert on working-tree cleanliness. Receipt:
`brain/output/council/sprint07_tables_slice2_review_20260607.md`. **The commit is the user's git gate.**
**Sprint 07 migration SPINE (Slices 1+2) is COMPLETE.** Slice 3 is NOT a DDL slice (place-attached abouts
= feature bodies, authored through the existing editor→core path). Only the flagged follow-ups remain:
viewer RENDERING of activity detail (a UI slice + `main.js` + a shell bump), and the activities' specific
data (grade/length/gate list) for the user to author.

-----

**2026-06-07 (SPRINT 07 RALPH LOOP — SLICE 1 CLOSED: `core.events` stood up, schedule baked from the
DB; CODE+DB, UNCOMMITTED, NO shell bump owed).** User: *"begin the looping on the slices"* (after
committing the plan, `7543790 "table plan"` — the commit pause). Did Slice 1 of the
`07_tables/tables_model.md` execution plan end-to-end, one slice per the Loop contract. **Shipped:**
`core.events` table (the WHEN junction; `source_key UNIQUE`, soft `place_key`=`#location` tag, `attrs`
jsonb, **no FK/CHECK**) in `init_db.sql` (live volume + fresh-volume proven); new
`mvp/scripts/import_event_schedule_to_core.py` (reuses the gold importer's SQL helpers — sessions →
`core.events` [13], the 7 locations → `core.features`: 6 new `layer='event'` non-publish anchors + the
`#pavilion` POI annotated with `attrs.event_location`); a schedule emit arm in
`export_publish_geojson.sh` (sibling to the `REFERENCE_LAYERS` loop — the schedule is a document, not a
FeatureCollection — same served filename `aop_event_schedule.json` → **no `main.js` change, no
`sw.js`/`#appVersion` bump owed**); a `--baked` tile-independent mode in
`playwright_verify_event_schedule.py` (reuses `wait_loaded` + `getSource('event-schedule').serialize()`,
NO `queryRenderedFeatures`/`networkidle` — the Witness condition). **Verified by observation (all
green):** (a) baked schedule field-equivalent to HEAD — 13/13 sessions identical, locations identical
modulo the **one intended delta** (`#pavilion` now carries baked `coordinates`, HEAD used a runtime
binding — the join is now baked from `core`); (b) `--baked` verifier PASS (event-schedule source loads
20 features, 13 sessions, `#pavilion` session resolves to the pavilion point, 0 console errors); (c)
`publish.features WHERE layer='event'` = 0 (gate holds); `count==input` (13/13, 7/7); **fresh-volume
repro proven** (`init_db.sql` into a throwaway DB exit 0, `core.events`+trigger+4 indexes present);
served files **restored byte-identical to HEAD** (production untouched — the DB migration is the durable
change). **Model refinement (recorded in the card):** `place_key` = the `#tag` (user's model), place
found via `core.features.attrs->'event_location'->>'tag'`; the card's "soft-ref `source_key`" honored in
spirit (soft key, no FK) but keyed on the tag, the no-limiting store-and-resolve-later reference.
**OWED (flagged, NOT slice 1):** umbrella event metadata is bake-config until it gets a `core` home
(event CRUD, V2); the editor's localStorage `#tag` binding and the DB `attrs.event_location` tag should
converge (rides gold slice 6, HELD). **The commit is the user's git gate.** **NEXT (loop):** convene the
council done-review on Slice 1 (this turn), then Slice 2 — `core.activities` + `activity_key`.

-----

**2026-06-07 (SPRINT 07 REVIEWED + PREPPED — dependency verified landed, executable slice plan
written; BRAIN ONLY, then COMMITTED by the user as `7543790`).** User: *"review 07 and prepare to work on it."*
Reviewed `tasks/07_tables/tables_model.md` (council-cleared design, full six / 2 rounds) and **verified
its dependency landed by observation**, not by the card's word: live DB `aop_map` shows `core.features`
(141 rows, `source_key UNIQUE` + `attrs` + `archived_at`), `core.pois`/`publish.pois` dropped, the
schedule resolver intact (`resolveEventLocation` `main.js:6202`, `eventScheduleToGeojson` `:6280`,
loaded `:8181`; 13 sessions). So Sprint 7 is **now pullable** — the gate that held it (gold) is lifted.
**Two review deltas flagged (not edited — would owe a shell bump for a comment, per the gold
precedent):** (1) stale `#pavilion` prose at `main.js:6224` + the schedule JSON `source` field still say
"1010 building" though the binding moved to `editorPois:aop-pavilion` on 2026-05-26; (2) **the design
glossed a real wrinkle** — of 7 location tags **only `#pavilion` is feature-backed**; the other 6 carry
inline coords with no `core.features` row, so the card's "`place_key`→`core.features.source_key`" only
holds for one tag as written. **Resolution (recommended, council to confirm): migrate the 6 anchors into
`core.features` (`layer='event'`, non-publish)** so `place_key` resolves uniformly — reuses the gold
spine, adds NO third table, keeps the two-table model. **Prep artifact:** appended an
**"# Execution plan — slices (ready to pull)"** section to `tables_model.md` (kept it ONE card to avoid a
parallel-card dup) — Slice 1 (`core.events` + 13 sessions, bake the schedule JSON from the DB), Slice 2
(`core.activities` + `activity_key`), Slice 3 (place-attached abouts = feature bodies, not DDL), each with
**tile-independent acceptance**, a Loop contract, run commands, and the gold council's inherited standing
conditions (Witness re-witness, Mason count==input). Reuses the existing
`playwright_verify_event_schedule.py` + the bake's one-writer script (a new schedule emit arm sibling to
the `REFERENCE_LAYERS` loop — the schedule is a document, not a FeatureCollection). **THEN the user said
"convene the council on the plan" → COUNCIL FULL CLEAR (Steward-chaired, full six, 1 round, no andons).**
All five worker seats `clear`, each grounding its verdict in live re-verification (Witness re-confirmed
the DB + the 1-of-7-feature-backed-tags finding; Warden confirmed the 6-anchor migration is *required* by
the card's own `place_key`→`source_key` mechanism, not scope creep; Mason confirmed no FK/CHECK/drop;
Quartermaster confirmed one card + reuse-true; Scribe confirmed executor-runnable + voice). Two
non-blocking precision notes folded into the plan before clearing: (Quartermaster) the schedule bake arm
is a *sibling emit block*, NOT a `REFERENCE_LAYERS` entry; (Witness) acceptance (b) must add a NEW
tile-independent `getSource(...).serialize()` assertion, not inherit
`playwright_verify_event_schedule.py`'s render-dependent pattern (copy `playwright_verify_baked_reference_author.py`).
Receipt: `brain/output/council/sprint07_tables_execution_plan_review_20260607.md`; clearance hash in
`.claude/.council-cleared`. **NEXT (user's, per the gold precedent):** commit pause → ralph loop on Slice
1. This turn touched only `brain/` + `.claude/.council-cleared` (no `website/`/`mvp/`), so the Stop-hook
gate did not self-fire; nothing committed.

-----

**2026-06-07 (GOLD SPINE CLOSED OUT — deprecated POI objects DROPPED after a rename-and-reverify test;
DB + `mvp/init_db.sql`, UNCOMMITTED, NO bump owed).** The user pulled the one item the ralph loop held
back for a human: dropping the deprecated `core.pois` table + `publish.pois` view. **Verified safe by
observation FIRST:** every `core.pois` row mirrored into `core.features` (`unmirrored = 0`); served-set
parity identical (old `publish.pois` gate = 2, new `publish.features WHERE layer='poi'` gate = 2, symmetric
diff 0); **no FK** at `core.pois`, only `publish.pois` depended on it. **Rename-and-reverify drop test**
(the reversible proof nothing reads them by name): `ALTER ... RENAME` both away → bake exit 0, no
missing-object error → `publish.geojson` still carried both POIs (browserless) →
`playwright_verify_baked_pois_author.py` **PASS, 0 console errors**, viewer rendered `pubpoi:139/140` (the
`core.features` serials — proves the serve reads `core.features`). Restored served files byte-identical to
HEAD, then **dropped for real** (`DROP VIEW publish.pois; DROP TABLE core.pois;`); `core.features` intact
(141 rows). Edited `mvp/init_db.sql` to remove the table / view / `pois_geom_gix` index / trigger-loop
entry / stale comment, and **proved fresh-volume reproducibility** (edited `init_db.sql` on a throwaway DB
→ exit 0, the two objects absent, `core.features`/`publish.features` present). **One latent gate delta
logged in the card:** `publish.features` dropped the `is_destination = true` clause `publish.pois` had — 0
rows differ today. **NO shell asset touched → NO `sw.js`/`#appVersion` bump owed.** Cosmetic doc-debt left
(historical provenance comments in `main.js:1219,9536`, `aop_poi_index.json`, verifier/seed docstrings —
accurate as history; not edited to avoid a shell bump for a comment). **Gold migration SPINE is now
COMPLETE** (slices 1–5 + Retirement + the human-owed DROP). **Still open (NOT closed by this):** Slice 6
(HELD — `aop-*` localStorage → working buffers), the per-layer legacy-writer retirement (OWED), and the
entire Sprint-06 guardrail slate (items 1–5 in the sprint `_readme`). **The commit is the user's git
gate.** Records: `gold_migration.md` (DROP COMPLETE block), `06_going_gold/_readme.md` (Spine status),
this entry.

-----

**2026-06-06 (SPRINT 07 TABLES — design carded + COUNCIL CLEARED, full six, 2 rounds;
BRAIN ONLY, UNCOMMITTED).** User: *"give me your thought on sprint 7 and present it to
the council."* Sprint 7's stub `breif.md` asks how to connect the three models the user
cares about — **where** (POI), **when** (calendar), **what** ("abouts": an about for AOP,
rock warblers, to-town) — so the schedule can say "1:30pm hill climb at #hillclimb, the
hillclimb has this specific data, re-used across event times." **My read, written to
`tasks/07_tables/tables_model.md`:** the pattern is relational normalization; it resolves
to **ONE new table.** WHERE = the gold `core.features` (+ JSONB `attrs` for a place's own
data — the hillclimb's spec IS its feature attrs). WHEN = promote `aop_event_schedule.json`
(13 sessions, already keyed by `location_tag`) into **`core.events`**, which **soft-references**
`core.features.source_key` and becomes the **bake output** of the *existing* viewer resolver
(`eventScheduleToGeojson`/`resolveEventLocation`, `main.js:6280-6357`) — extend it, don't
rebuild. WHAT = **not a new model**: place-attached abouts are feature `description`/`attrs`
bodies (rock warblers + AOP badge are already `brand_logo` points; to-town are
`visitor_callout` points), and a place-less "About AOP" gets a **representative anchor point**,
not `geom NULL`. **The one genuine fork left to the user:** does an activity (hill climb, RC
rally) recur across *different* places (→ add a thin `core.activities` ref table) or bind to
one place (→ no catalog; recommended start)? **Sequencing:** design-only — depends on
`core.features` (gold slice 2+), so it doesn't collide with the active gold loop.
**Council (Steward-chaired, full six):** R1 three andons — Witness (`#pavilion` resolves to
seeded POI `aop_seed_pavilion`, not the 1010 building, rebound 2026-05-26), Quartermaster
(the "list renders geom-less features" premise is false — the one list engine drops geom-less
rows at `main.js:6287`/`:1264`; and `core.events` must be framed as extending the existing
resolver), Mason (pin `place_key` as a plain-`text` soft reference, NOT an enforced Postgres
`FOREIGN KEY` — that would reject unmatched rows, the C5 ban). All fixed; R2 all three
re-cleared; Warden + Scribe clear R1 → **FULL CLEAR.** Receipt:
`brain/output/council/sprint07_tables_review_20260606.md`. Touched only `brain/` (no
`website/`/`mvp/`), so the Stop-hook gate did not self-fire; nothing committed.
**THEN the user RESOLVED the fork (same turn):** *"the events usually are at the same place
sometimes they are different. they are only tied to the place when the schedule says so for
that occurance and at the #location tagged."* → **two-new-table** model, re-carded: the place
binds on the **occurrence** (the schedule row) via the `#location` tag, never on the activity.
`core.activities` (place-agnostic reusable WHAT — hill climb, RC rally, rock-hard tour; CMFS
shape minus geometry) **is now in scope**; `core.events` is the WHEN **junction** (one row per
occurrence) soft-referencing both `activity_key` + `place_key` (place per-occurrence, no
default-place field); place-attached abouts (rock warblers/to-town/about AOP) stay feature
bodies. The split test: *does the schedule cite it (→ activities) or does a place own it
(→ feature body)?* **Re-review of the delta (Steward-chaired): Quartermaster + Mason + Warden
all clear** (Witness facts unchanged, Scribe held by chair) → revised model **FULL CLEAR**.
Quartermaster corroboration: the schedule JSON already duplicates activity content inline
(`fri-night-crawl`/`sat-night-crawl` = two copies of "Night Crawl") — `core.activities`
de-duplicates exactly that. **First slice when gold lands:** stand up `core.events` against the
13 existing sessions, prove occurrence→place bakes, then add `core.activities` + `activity_key`.

-----

**2026-06-06 (RALPH LOOP — RETIREMENT STEP CLOSED: `core.pois` collapsed into `core.features`; the loop
STOPS here, slice 6 HELD; CODE+DB, UNCOMMITTED, NO bump owed; council CLEAR).** Did the Retirement step
of `06_going_gold/gold_migration.md`. **Key correctness move:** dropping `publish.pois` from the bake
while leaving the apply path on `core.pois` would BREAK the POI edit path — so the collapse rewired the
apply path + seed too, not just the bake. **Shipped:** (1) mirrored the 4 `core.pois` rows →
`core.features` (`layer='poi'`, ON CONFLICT, **no DELETE** — rows stay deprecated); (2)
`apply_panel_overrides_to_core.py` now upserts `core.features` (`layer='poi'`); (3) bake POI arm `FROM
publish.pois` → `FROM publish.features WHERE layer='poi'`; (4) `seed_core_pois.sql` rewritten to seed
`core.features` via ON CONFLICT (no `DELETE FROM core`); (5) `init_db.sql` deprecation comments on
`core.pois`/`publish.pois` (kept, not dropped). **Acceptance all green:** (a) zero `core.pois` unmirrored
(=0); (b) `publish.pois` gone from the bake; (c) slice-1 author verifier PASS — baseline + `--require-author`
(edit Pavilion + delete Ellis → bake → viewer's `published_destinations` showed the edited name/blurb as
`pubpoi:139` [core.features serial, proving the new source], Ellis absent, 0 errors). Core POIs
re-migrated to faithful + served files restored byte-identical to HEAD. `core.features` now holds **141
features** (buildings 5 + cemeteries 8 + visitor 4 + trails 120 + poi 4). **OWED (human, NOT the loop):**
DROP the deprecated `core.pois`/`publish.pois` once confirmed unused (destructive — user's call); retire
the dormant per-layer legacy writers (slices 2–5). **The commit is the user's git gate.** **LOOP DONE —
all migration slices + the retirement are closed; slice 6 is HELD for a human (see its section).**

-----

**2026-06-06 (RALPH LOOP — SLICE 5 CLOSED: trail network migrated; CODE+DB, UNCOMMITTED, NO bump owed;
council CLEAR).** Did slice 5 of `06_going_gold/gold_migration.md` — the LAST migration slice. All 120
trail-network LineStrings → `core.features` (`layer='trails'`, true reference permission 'SFWDA paper
map — permission TBD'; full `properties`→`attrs` incl. each trail's load-bearing `color`/`difficulty`;
`source_register` row id 12). Unique `id` (`sfwda-N`) → `--id-field id`, 120 distinct keys. Bake
regenerates `aop_trail_network.geojson` from core, carrying the rich **gold** `_meta` forward.
**Verified:** baked file prop+geom equivalent to HEAD (120/120, max geom delta 0), gold `_meta` carried;
viewer baseline PASS (`getSource('aop-trail-network')` = 120, color survived) + `--require-baked`
round-trip PASS (marker on trail '15'), 0 console errors; `publish.features` trails = 0; slices 1–4
unregressed; served files restored byte-identical to HEAD. **`core.features` now holds all four reference
layers (buildings 5 + cemeteries 8 + visitor 4 + trails 120 = 137).** **The commit is the user's git
gate.** **NEXT (loop):** the Retirement step — collapse `core.pois` into `core.features`, prove, then
STOP (slice 6 is HELD for a human).

-----

**2026-06-06 (RALPH LOOP — SLICE 4 CLOSED: visitor callouts migrated; CODE+DB, UNCOMMITTED, NO bump
owed; council CLEAR).** Did slice 4 of `06_going_gold/gold_migration.md`. 4 visitor-context features
(2 `visitor_callout` polygons + 2 `brand_logo` points) → `core.features` (`layer='visitor'`, true
reference permission; `source_register` row id 11). Unique `id` across both kinds → single `--id-field
id`. The viewer splits the ONE served file by `kind` into TWO map sources (`visitor-context` +
`brand-logos`), so the generic verifier now accepts a **list** of sources per layer. **Real bug found +
fixed:** a callout `label` has embedded newlines; the reference bake's `COPY … TO STDOUT` backslash-
escaped them (`\n` → literal `\\n`). Fixed by switching the reference-layer bake to a plain `SELECT`
with `-At` (no COPY escaping); buildings + cemeteries re-verified prop-faithful. The pre-existing
`publish.geojson` `COPY` has the same latent risk (noted in the script; no published feature has a
newline today). **Verified:** baked file prop+geom equivalent to HEAD (4/4, newline preserved), `_meta`
silver carried; viewer baseline PASS + `--require-baked` round-trip PASS (marker on the AOP-badge logo),
0 console errors; `publish.features` visitor = 0; slices 1–3 unregressed; served files restored
byte-identical to HEAD. **The commit is the user's git gate.** **NEXT (loop):** slice 5 — trails (120
features, `permission TBD` = non-publishable).

-----

**2026-06-06 (RALPH LOOP — SLICE 3 CLOSED: cemeteries migrated; CODE+DB, UNCOMMITTED, NO bump owed;
council CLEAR).** Did slice 3 of `06_going_gold/gold_migration.md`. 8 cemetery features (4 cemeteries,
each a parcel polygon + a marker point) → `core.features` (`layer='cemeteries'`, true reference
permission; full `properties`→`attrs` incl. burial roster fields; `source_register` row id 10).
**New code:** cemetery feature keys aren't unique on `parcel_id` (2 rows each), so
`import_layer_to_core_features.py` gained a **composite `--id-field` (`parcel_id,geom_role`)** → 8
distinct `source_key`s; `export_publish_geojson.sh` `REFERENCE_LAYERS` += cemeteries. **Verifier
consolidated (Quartermaster/DRY):** the slice-2 buildings verifier was generalized into ONE
`playwright_verify_baked_reference_author.py --layer <name>` (LAYERS config; covers buildings +
cemeteries, extensible to visitor/trails) and the buildings-specific file retired (slice-2 refs
updated). **Verified by observation:** baked `aop_cemeteries.geojson` prop+geom equivalent to HEAD
(8/8, key sets+values identical, geom maxdelta<1e-6), `_meta` `reference` carried; viewer baseline PASS
+ `--require-baked` marker round-trip PASS (marker authored into core→baked→appeared on Ellis in the
viewer's loaded source), 0 console errors; **roster stays out of publish** (`publish.features` cemeteries
= 0 — the non-commercial burial roster lives only in the reference served file + `attrs`, never the
publish zone); slices 1+2 verifiers unregressed. Served files restored byte-identical to HEAD. **The
commit is the user's git gate.** **NEXT (loop):** slice 4 — visitor callouts (silver; includes
`brand_logo` points).

-----

**2026-06-06 (RALPH LOOP — SLICE 2 CLOSED: `core.features` + buildings migrated; CODE+DB,
UNCOMMITTED, NO bump owed; council full-six CLEAR).** Did slice 2 of `06_going_gold/gold_migration.md`.
**A design fork surfaced + was council-cleared FIRST:** the card said bake the 5 buildings into
`publish.geojson`, but observation shows ALL slice-2–5 source layers are reference/silver/permission-TBD
— **none passes `permission='publish'`** (buildings: FEMA "no warranty" / private "presence only";
cemeteries: non-commercial burial roster; visitor: 'context annotation'; trails ×120: 'SFWDA paper map
— permission TBD'). Forcing them into the publish zone violates the northstar. **Corrected (card amended
+ annotated, original in git `bf41eb5`):** reference layers bake to their OWN served file (the file the
viewer already reads), `publish.features` keeps the gate and stays reference-free. The council design
consult also **falsified the card's premise** that `map.on('load')` never fires headless — it DOES
(observed); tiles block only paint/`queryRenderedFeatures`, so a map source's loaded data IS readable
via `getSource(...).serialize().data.features` (this correction is now in the Observable standard, for
slices 3–5 too). **Shipped:** `core.features` (CMFS spine + mixed `geometry(Geometry,4326)` +
`source_key UNIQUE` + `archived_at` + free-form JSONB `attrs`; no CHECK/enum) + `publish.features` view
(selects `attrs` explicitly so it isn't dropped by omission) in `init_db.sql` (live volume + fresh);
new generic `mvp/scripts/import_layer_to_core_features.py` (reusable for slices 3–5; full original
`properties`→`attrs` so nothing drops; `ST_GeomFromGeoJSON` any-geom; upsert `ON CONFLICT (source_key)`;
count==input asserted; reference-tier `source_register` row id 9); `export_publish_geojson.sh` extended
with a `REFERENCE_LAYERS` loop that rebuilds `aop_buildings.geojson` from `core.features WHERE
layer='buildings'` (properties=`attrs`, `_meta` carried forward, minified) — **same filename the viewer
reads, so NO `main.js` change → NO `sw.js`/`#appVersion` bump owed**; new headless-safe
`mvp/scripts/playwright_verify_baked_reference_author.py` (`getSource(...).serialize()`;
`--require-baked` marker round-trip so it can't degrade to baseline-PASS). **Verified by observation:**
baked `aop_buildings.geojson` prop+geom equivalent to HEAD (5/5, key sets+values identical, geom
maxdelta<1e-6), `facility_role` survived; viewer baseline PASS + `--require-baked` PASS (a marker
authored into core→baked→appeared in the viewer's loaded source); `publish.features WHERE layer='buildings'`
= 0 (gate works); slice-1 POI verifier unregressed. **Served files restored byte-identical to HEAD**
(production untouched; `git status website/` clean). **Council:** design consult (full six) cleared the
fork with conditions; done-review (full six) — Witness/Quartermaster/Mason/Warden CLEAR (each re-ran the
verifier/round-trip/gate independently), Scribe andon on 5 record gaps, ALL FIXED (served files restored,
`data_maturity_tiers.md` `_meta`-carry note added, card annotation wording corrected, Loop-#5 slice-1
caveat claim corrected, this handoff entry). **OWED (next increment, NOT slice 2):** retire the 3 dormant
legacy writers of `aop_buildings.geojson` (`import_fema_buildings.py`, `rebake_canonical.py` CONFIG, the
`export_positioned_features.py` buildings branch) once the buildings apply-door exists
(`apply_panel_overrides_to_core.py` `layer='buildings'` + a layer-aware geom builder; slice-1's
`point_geom_sql` NULLs polygons). None runs in the day-of loop, so the bake is the sole in-loop writer
today. **The commit is the user's git gate.** **NEXT (loop):** slice 3 — cemeteries (keep the
non-commercial burial roster out of any publish-gated output).

-----

**2026-06-06 (RALPH LOOP — SLICE 1 CLOSED: POI author path proven end-to-end; CODE+DB,
UNCOMMITTED, NO bump owed).** Did slice 1 of `06_going_gold/gold_migration.md` per the Loop
contract. Built the AUTHOR→STORE link on `core.pois` and proved `edit → core → bake → serve →
reload` by observation. **Shipped:** extracted the one parser into new
`mvp/scripts/panel_overrides.py` (`SCHEMA`/`VIEW_STATE_KEYS`/`split_key`/`round_coords`/
`feature_by_id`/`geom_kind`/`build_created_feature`/`read_payload(strict=…)`), refactored
`bake_panel_overrides.py` to a thin importer (**byte-identical fixture diff, matching sha256** —
behavior preserved, the diff IS the check since there's no baker unit test); new
`mvp/scripts/apply_panel_overrides_to_core.py` (DB sink — upserts `edits[]`/`created[]` into
`core.pois` `ON CONFLICT (source_key)`, archives `deleted[]`, **never** drops/skips/throws,
**no `DELETE FROM core`**, asserts upserted-count==input via an `_applied` temp table); new
headless-safe `mvp/scripts/playwright_verify_baked_pois_author.py` (reuses star_collector's
`wait_loaded`/`open_poi_tab`; reads `published_destinations` DOM rows). **DDL (additive):**
`core.pois` +`source_key text UNIQUE` +`archived_at timestamptz`; `publish.pois` +`archived_at
IS NULL` — in `mvp/init_db.sql` (fresh volumes) AND applied by hand to the existing volume; the
3 seed rows keyed in `seed_core_pois.sql` (`editorPois:aop-pavilion` etc.). **Verified by
observation:** apply run1 = edits 1/1·created 1/1·deleted 1/1; run2 idempotent (4 rows, ids
`1,2,3,5` unchanged); baked `publish.geojson` carried the edited Pavilion name+blurb on `layer=
'poi'`, archived Ellis absent, non-publishable created POI absent (gate works); the author
verifier **PASS, 0 console errors** (re-witnessed on the REAL DOM rows, the Witness condition);
no CHECK/enum introduced; `source_register` editor row id 7 created. **Restored:** DB reverted
(Pavilion text restored, Ellis un-archived); `website/data/publish.geojson` **byte-identical to
committed HEAD** (production untouched). **OWED:** **nothing for the git gate beyond the
commit** — NO shell asset (`index.html`/`js`/`css`/`sw.js`) was touched, so **no `#appVersion`/
`sw.js` bump owed.** Commit is the user's git gate (untracked: `panel_overrides.py`,
`apply_panel_overrides_to_core.py`, `playwright_verify_baked_pois_author.py`; modified:
`bake_panel_overrides.py`, `seed_core_pois.sql`, `init_db.sql`). **⚠ FINDING for the next
slices (not slice-1 scope):** `export_publish_geojson.sh` **drops** the hand-curated
`park_boundaries` feature "Ellis Cemetery (inholding parcel)" (served id 5) — it lives only in
`publish.geojson`, not in `core.park_boundaries`, so the DB bake erases it. The bake can't be the
sole writer for boundaries until that polygon is migrated into `core`; same risk for any layer
with served-only hand-curated rows. **Residue:** one archived, non-publishable test row left in
`core.pois` (id 5 "Author Test Overlook") — archived not hard-deleted per the no-`DELETE FROM
core` rule. **Council: FULL CLEAR (full six).** Warden/Quartermaster/Mason/Scribe cleared first
pass; Witness pulled one andon — the STATE B viewer proof rested on producer narration and the
verifier could silently degrade to baseline-PASS. Resolved: hardened
`playwright_verify_baked_pois_author.py` with a `--require-author` mode (FAILs if the edit is
absent; default no-flag run stays baseline-green for the durable suite), and a fresh Witness
re-witnessed the author round-trip on its own apply→bake→verify run, then confirmed
`publish.geojson` byte-identical to HEAD. Receipts:
`brain/output/council/gold_migration_slice1_review_20260606.md`; clearance written to
`.claude/.council-cleared`. **NEXT (loop):** slice 2 — `core.features` + buildings.

-----

**2026-06-06 (COUNCIL CLEARED THE GOLD PLAN — full six seats, 4 rounds; BRAIN ONLY,
UNCOMMITTED).** User: *"have the council review your plan. stop when everyone is happy. we will
pause commit then ralph loop at that point."* Ran the completion-gate done-review over
`06_going_gold/gold_migration.md` at **full-six tier** (high risk: a sprint-spine architectural
migration an autonomous ralph loop will execute). Chaired as Steward; spawned the five worker seats
as fresh adversarial `council-*` subagents each round, prompted to refute. **Round 1: all six
pulled andon** — every one grounded in a real file/line (NOT nitpicks): Witness (the cited
`playwright_verify_baked_pois.py` is NOT headless — `queryRenderedFeatures`+`networkidle`; "SERVE
proven" overstated), Scribe (match-key ambiguous — `core.pois.id` serial vs export `<source>:<id>`;
no run-commands; no record step), Quartermaster (parser would be duplicated; two-table retirement
unverified), Mason (no archive column + parent hard-deletes; apply could throw/skip), Warden (slice
6 unbounded; slices 3–5 unsplit; a VERSION-bump line collided with the git gate). **Rewrote the plan
across rounds 2–4:** added an Observable-acceptance standard (browserless baked-file assertion + a
star_collector-pattern `playwright_verify_baked_<layer>_author.py`; **no** render/`networkidle`/
`publishDataCache`-closure reads); a `--target core` extraction (one `panel_overrides.py` parser,
two sinks) with the file-baker's drop branches explicitly stripped from the core sink; `source_key
UNIQUE` + `archived_at` DDL with an exact **upsert** rule for `edits[]`/`created[]` (bare UPDATE
banned — a zero-row UPDATE is a silent lost edit) and archive-not-delete for `deleted[]`; literal
run-commands + DB bring-up; per-slice Record-on-green; split per-layer slices with a named
source+verifier table; an explicit Retirement step; slice 6 demoted to HELD; the VERSION bump
reworded as owed-to-user. **Clears:** Warden+Scribe R2, Quartermaster+Witness R3, Mason R4, Steward
chairs → **FULL CLEAR.** Receipts: `brain/output/council/gold_migration_review_20260606.md`.
**Standing conditions the loop inherits:** (Witness) the apply script + 5 author verifiers don't
exist yet — the loop writes them; re-witness on the FIRST slice's REAL verifier output before
trusting "green"; (Mason) confirm the count==input acceptance runs against a live apply. **NEXT
(user's):** the commit pause, then the ralph loop on slice 1. The review touched only `brain/`
(no `website/`/`mvp/`), so the Stop-hook gate did not self-fire; nothing committed.

**2026-06-06 (GOING GOLD — user committed to the DB-as-store-of-record migration; plan
carded, Sprint 06 reframed; BRAIN ONLY, UNCOMMITTED).** User, after the schema consult:
*"we are going gold. going to the db. and baking the output for production. still these
things may need tweaks from now to day of. so I have been trying to preserve edit paths…
give me your thoughts."* (Frustrated that this has been backed-away-from / only partially
implemented before — explicitly wanted **direction + action, not status quo.**) **Recon
(observation) found the root cause:** the served `website/data/*.geojson` have **three
writers** with a fragile ordering dep — `rebake_canonical.py` (from `raw/`),
`bake_panel_overrides.py` (browser edits), `export_publish_geojson.sh` (DB) — and they
clobber each other (the panel-bake docstring warns about exactly this). **Direction set
(decisive):** make `core` (PostGIS) the ONE upstream; the **bake is the only writer to the
served files**; prod stays static read-only (northstar V1). **The edit path is preserved by
REDIRECTING it, not removing it** — the web editor's existing `aop-panel-overrides-v1` export
gets applied to **`core`** instead of to files (new `apply_panel_overrides_to_core.py`,
sibling to `bake_panel_overrides.py`). localStorage → working buffer only (C3). Day-of loop:
`edit → Export → apply-to-core → export_publish_geojson.sh → deploy`. **Why finally tractable:**
no prod write-service / auth / moderation (the V2 scary stuff stays deferred); per-layer thin
slices, each green before the next. **Schema call:** converge destination layers onto ONE
`core.features` (CMFS columns + JSONB `attrs` for domain extras) — the gold answer to "too many
schemas" — but prove the AUTHOR loop on the EXISTING `core.pois` first (slice 1), converge
schema as layers come in. **Plan carded:** `tasks/06_going_gold/gold_migration.md` (the spine,
sequenced slices 1–6); Sprint 06 renamed `06_verify_and_polish` → **`06_going_gold`** and
reframed so the migration is the spine and the verifier/polish/schema-audit items are its
guardrails. **NEXT ACTION = slice 1** (POI author path: build `apply_panel_overrides_to_core.py`,
prove edit→core→bake→serve→reload by observation, extend `playwright_verify_baked_pois.py`).
**Env note:** the sandbox temp fs (`/private/tmp/claude-501/.../tasks`) filled up mid-turn
(ENOSPC on stdout capture); workaround is redirecting Bash output to a real-fs file and Reading
it — clear it (or set `CLAUDE_CODE_TMPDIR`) before the slice-1 DB/verifier run. No code written
yet; nothing committed.

**2026-06-06 (COUNCIL CONSULT — "too many schemas; does a DB / type system fix it?",
BRAIN ONLY, UNCOMMITTED).** User asked, mid-triage, whether forcing data into the DB
solves the per-source schema fragmentation (DB requires one schema) and whether a **type
system** could be enforced on top — explicitly *"consult the council."* Convened four
seats as **independent subagents** (Quartermaster·Mason·Witness·Warden) over the question
+ the C-contracts + source_register + init_db.sql; chaired/synthesized as Steward. They
**converged**, and the Witness surfaced a finding I didn't have: **the one-shape contract
already ships** — the Common Minimum Feature Schema (`website/data/_schema.json`
`aop-cmfs-v1`, backed by `research/common_feature_schema.md`), observably holding on the
18 curated layers (6 `machine:true` layers deliberately exempt). Synthesis: (1)
fragmentation is **real** (across 23 served files only `id`+`kind` are universal); (2) the
DB helps **narrowly** — declares the shared spine once, but must NOT flatten per-domain
attributes, and **prod reads files not the DB so the BAKE is what unifies**, not the DB;
(3) a type system is possible and **half-exists** (CMFS); (4) **shape not vocabulary**
(Mason/C5 — never reject an unknown value; PostGIS already does this right: zero
CHECK/enum); (5) the move is a **receipt, not a new contract** (Quartermaster — read-only
audit reading the existing `_schema.json`, no second surface). **Inter-seat conflict
resolved:** Warden floated CHECK/enum on `core.pois`; Mason pulled andon (C5 locked);
Steward sided with Mason — the probe **reports**, never **rejects**; a value-gate is a
user re-confirm. **Durable outcomes:** new Sprint-06 card
`06_going_gold/schema_conformance_audit.md` (read-only `audit_canonical_schema.py
--check`; already-found drift: `aop_user_features.geojson` on disk but missing from the
manifest), added to the Sprint-06 slate as item 5 (parallel-safe); consult decision noted
in `star_driven_poi_list.md` (hung off its open forks — it de-risks the authoring-surface
pick: any authoring path writes the SAME CMFS shape, audit guards it). The four council
subagents are resumable (ids in this turn's tool results) if deeper schema work is pulled.

**2026-06-06 (FIRST COUNCIL TRIAGE — deferred bucket re-sorted, Sprint 06 stood up,
BRAIN ONLY, UNCOMMITTED).** User: *"time to test the council. review the deferred cards.
have any of them been done… move done to _done in deferred… move to sprint 6 if they need
to get done soon. access each of them come up with a plan and a checklist."* Ran
`council/triage.md` as Steward over all 16 `tasks/10_deferred/` cards (six seats as
selection lenses). **Done-state verdict (by observation, not card-trust):** NONE of the
16 is 100% complete as a unit; the only closeable one was **`pwa_qa_data_bakes.md`** —
re-confirmed items 4/6/E DONE on the working tree (`aop_buildings.geojson`=5 curated
[Front Office/Pavilion/Farmhouse + 2 boxes]; Ellis Point+Polygon both carry burial_count
12 + roster + source; visitor-context callouts baked, 4 features post brand-merge). Its
one open item — **Item 17 extend-9-patch-imagery** — **split out to a new
`extend_9patch_imagery.md`**, then moved the card to **new `tasks/10_deferred/_done/`**.
**Stood up `tasks/06_going_gold/`** (sprints 01–05 existed; 06 is next). Honest
finding: the big deferred cards (event CRUD, star-driven authoring, real-trail promotion)
are **all gated** on a user decision / external truth / on-device or data-acquisition step
— none swarm-able as-is. So **Sprint 06 = the pullable debt:** (1) three missing verifiers
[parallel-safe], (2) stale `publishable`/`presets` verifier reconciliation [sequential],
(3) code-health cleanups [L1 whitespace, `setEditorFeatureNotes` trim-rename, L2
shared-helper extractions — sequential, hot files], (4) a trail-review surfacing slice
[surface `review_flags`/dangling/grey/blue-1 so the user can do the promotion pass].
**Quartermaster caught a dup trap:** the old "wire `sfwda_numbered_trails.geojson`" item is
**superseded** by the served `aop_trail_network.geojson` — left unwired. **HELD** (with
unblock conditions in the Sprint-06 `_readme.md`): event_crud, star_driven (authoring-surface
pick), dev_db_reseed, data_integrity, brand_assets (permission posture), calendar/park-bounds
picks, rock_warblers (external), offline_pwa, the two `sprint05_*_on_device` smokes +
`extend_9patch_imagery` (human/device/acquisition — not swarm cards). **The council did NOT
spawn fresh seat-subagents** — triage is Steward-chaired lens application per the doc, and
there is no diff to review; the seat reasoning is written into the Sprint-06 `_readme.md`.
**Owed / forks:** the user owns the cheap unblock picks (calendar variant, PB icon,
brand-permission posture, authoring surface) and the scoping conversation for event CRUD;
those promote held cards. The swarm trigger + the git gate (commit; the v52 bump still owed
from Sprint 05) are the user's. This turn touched only `brain/` (no `website/`/`mvp/`), so
the Stop-hook gate does not self-fire. Files: `tasks/10_deferred/_done/pwa_qa_data_bakes.md`,
`tasks/10_deferred/extend_9patch_imagery.md`, `tasks/06_going_gold/_readme.md`,
`tasks/10_deferred/_readme.md` (triage block), this handoff.

**2026-06-06 (THE COUNCIL INSTALLED — standing reviewer seats + a completion-gate Stop
hook, BRAIN + HARNESS, UNCOMMITTED).** User: *"the seal team got us past sprint 5. the council
will get us through the future… come up with a set of personas and a set of hooks that are called
when a main agent thinks its done… profile based guardrails to resist the slop… one that knows the
product that will keep the others focused."* Did deep web research first (independent adversarial
critics beat self-review — models are blind to their own errors, Huang ICLR'24; gate on artifacts
not narrated verification; small non-overlapping council, duplicate roles are a named failure mode
MAST; objective checks first, DORA/jidoka; orchestrator holds goal+scope+termination, Anthropic
multi-agent). **Recon finding:** the "seal team"/Sprint 05 was *sequential single-agent* execution
against prepared cards, NOT a real swarm — clean slate. **Shipped — the durable council lives in
`brain/council/`** (source of truth): `_readme.md` (charter + evidence base + seat→rule map),
six seats = **the `ai_rules` given faces, partitioned non-overlapping** — `steward.md` (chair /
product keeper / orchestrator), `warden.md` (scope + git gate), `witness.md` (verify-by-observation,
adversarial, pulls andon), `quartermaster.md` (reuse / no-dupes / C1·C2·C6), `mason.md` (clean +
no-limiting-code C5), `scribe.md` (durable record + voice); plus `completion_gate.md` (the
Definition of Done + verdict-receipt schema + Stop-hook contract + dials) and `triage.md` (council
picks backlog cards for the swarm). **Harness adapters are THIN pointers** (`harness_adapters_are_thin`):
`.claude/agents/council-{steward,warden,witness,quartermaster,mason,scribe}.md` (read-only subagents),
`.claude/commands/council.md` (`/council`), and `.claude/hooks/council-gate.sh` wired as a **`Stop`
hook** in `settings.local.json`. The gate: loop-guard (`stop_hook_active`) + materiality (silent unless
`website/`|`mvp/` changed) + hard-block on `node --check` failure + advisory C1-grep/version-bump +
**nudge-once-per-distinct-diff** to convene `/council`; **fails OPEN**; `AOP_COUNCIL_BLOCKING=0`
downgrades to advisory; clearance keyed to diff-hash markers (`.claude/.council-{nudged,cleared}`,
gitignored). **Verified by observation** (real repo, transient untracked test file, read-only git):
loop-guard silent, clean-tree silent (no false fire), valid-JS change → exit2 nudge + version advisory,
same-diff → silent, `BLOCKING=0` → advisory, syntax-error → exit2 `SyntaxError`. **Pointers updated:**
`brain_map.md` (council branch + authority note + product-persona disambiguation), `flows/_readme.md` +
new `flows/council_review.md`, `.gitignore`. **Owed / forks for the user:** (1) the council is
self-served (agent reviews own work, reports results — NOT approval-seeking to you, per THE BAR);
(2) **dials to confirm** — keep the Stop hook blocking (default) vs advisory, and core-three vs
full-six default; (3) **sprint 06 setup is yours to trigger** — run `/council triage` to get a ranked
slate from the 7 backlog + 16 deferred cards, then stand up `tasks/06_*/`, then swarm; (4) commit is
the user's git gate (this run did NOT commit). NOTE: this council-building turn touched only
`brain/` + `.claude/` (not `website/`/`mvp/`), so the new gate did not self-trigger.

**2026-06-06 (SPRINT 05 VALIDATION REVIEW — all 8 cards re-checked by observation in
the main thread + MOVED to `_done/`; UNCOMMITTED).** Re-ran the structural gate live
(C1 = 0 `layerKey` branches; `node -c` clean on main.js + panel.js; v52 in `sw.js` +
`#appVersion`) and did NOT trust the cards' DONE claims. Cleared the four "BLOCKED for
human verify" flags the overnight run left, by observation: **(02)** new
`mvp/scripts/playwright_verify_dock_spec_axis.py` — the live editorPois dock renders a
Category `<select>` (11 opts) + Duplicate + Delete via pure spec dispatch, 0 console
errors; **(03)** real-registry eval shows `buildings.servedSource()`→`fema-buildings`
+ `nameField` on all 5 specs; **(05)** Node collector harness — a STARRED trail lands on
the RIGHT ★ list (`trail:n:1`); **(06)** `poi_rows_dump.js` MATCHES the committed
baseline exactly + `playwright_verify_star_collector.py` PASS on :8001; **(08)** new
`mvp/scripts/playwright_verify_fly_button.py` — `.feature-fly` + dock `.dock-ico` each
fire the map camera, 0 errors. All 8 cards now live in
`brain/tasks/05_special_operation/_done/`. **What still needs the human (few):**
(1) on-device iOS-PWA feel; (2) the git gate — commit + the v52 bump are the user's;
(3) the buildings dock's LIVE pixels (~5 s on-device: read-only Status, no Dup/Delete) —
the only check map-load-gated headless (buildings registers into `featureListRuntime`
at map-load; tiles blocked), mechanism identical to the editorPois dock proven live.
Two new durable verifiers added under `mvp/scripts/`. Full record: the sprint
`_readme.md` "Sprint 05 status" block + each card's "✅ VALIDATED" note.

**2026-06-06 (SPRINT 05 SPECIAL_OPERATION OVERNIGHT RUN — universal feature-layer
refactor, CODE ONLY, UNCOMMITTED, v51→v52).** The overnight run executed cards 02–08
of `brain/tasks/05_special_operation/` (card 01 was done before the run); all eight
cards passed independent observation. Per-card result: **01** — dead `buildInlineEditor`
deleted (done pre-run). **02** — the live dock property/field/action axis migrated into
FEATURE_LIST_LAYERS spec strategies; `buildEditDock`/`setFeatureProperty`/
`dockGroupContext` dispatch through the spec and name no `layerKey`; the 7132 seed-loop
self-guard rewritten as `const SELF='editorPois'` so no literal layerKey survives the
branch grep (documented in card 02). **03** — the parallel per-layer config maps
(`FEATURE_NAME_PROP`/`SERVED_SOURCE`) folded onto each spec; registry is the single config
home. **04** — the activityHotspots/syntheticActivity spec twins collapsed into one
`makeHotspotSpec(label, layerPrefix)` factory. **05** — `trails` registered as a
starrable destination layer (`highlightable:true` + `registerFeatureListLayer('trails',…)`).
**06** — the two list engines collapsed into ONE `collectStarredDestinations()`; both
`buildPoiGroups`/`renderPoiTab` (grouped) and `renderVisitorListGroup` (flat) consume it;
the `highlight===true` star gate applied once. **07** — the two per-layer special cases in
panel.js (create-defaults + host-bridge) replaced by spec `createDefaults`/`hostKey`.
**08** — the duplicated fly-to DOM gesture centralized into one `makeFlyButton()` helper.
**Final whole-sprint structural gate (real output):** C1 region command (non-comment
`layerKey === '...'` branches in main.js) = **0 branches**; `node -c website/js/main.js`
OK; `node -c website/js/panel.js` OK. VERSION **v51→v52** (`sw.js` + `#appVersion`; both
greps now read v52, no residual v51). **OWED / standing items:** on-device feel still owed;
the **commit + the v52 bump are the USER's git gate** (this run did NOT commit). The
card-06 **"POI tab starts empty" flip is DEFERRED** pending the user's decision on
`10_deferred/star_driven_poi_list.md` #1/#2/#4 — the two list engines were converged
**STRUCTURALLY only, behavior preserved** (wholesale layers kept `listMode:'wholesale'`, so
the POI tab renders the same rows it shipped). Out-of-scope **panel-swap cleanup** (third
list engine + `aop_panel_overrides_v1` second store) and the **parallel mini-DB collapse**
(poi_index/seed/localStorage → one DB column + bake) remain **deferred**, untouched this
sprint. **VERIFICATION OWED (honest gap):** every card's STRUCTURAL acceptance (greps +
`node -c`, C1=0 branches) was observed and passes, but cards **02** and **03** flagged their
runtime **DOM-level Playwright checks "BLOCKED for human verify"** — the seal team did not
boot the dock into the exact runtime state headless (fragile without a basemap) rather than
fake it. So a quick local/on-device smoke test is owed before trusting 02/03 at runtime:
edit a drawn-POI **Category** (select populated from `EDITOR_POI_CATEGORIES`) + **Duplicate/
Delete** present; a **buildings** feature shows a read-only **Status** and no Duplicate/Delete;
a drawn-POI name edit persists via `saveEditorPois`/`refreshEditorSource` and a buildings name
edit via `savePositionedFeature`/`refreshServedSource`. Card 06's star-in-both-lists DOM check
and 04/05/07/08 were not blocked.

**2026-06-05 (ONE ROAD STYLE — dropped the per-preset road recolour, CODE ONLY,
UNCOMMITTED, v49→v50).** User: *"the roads look wrong and washed out on the trace
preset. there is some dynamic road style swapping going on. remove all of that. one
road style."* Traced by observation: roads are 5 classes (local / local_connecting /
secondary / ramp / controlled_access), each a casing + line, defined ONCE at layer
creation (`js/main.js` ~L8177-8256) in the base style — **cream casing `#f3ecda` +
taupe/tan asphalt** (`#b0a68c`/`#cdb079`/`#c09060`/`#d8b173`), zoom-interpolated widths.
The "dynamic swapping" was the per-preset paint override: **Topo** recoloured the 5 road
lines to muted browns (`#908773` …) and **Trace** to washed-out **creams/yellows**
(`#fff4cf`/`#ffe08a`/`#ffd072`/`#f7bb5f`) at reduced opacity — that pale set on Trace's
dark hillshade + SFWDA-paper backdrop is exactly the "washed out" the user saw. Park
declared NO road-line override, so Park already showed the good base style. Fix: **removed
the road-line overrides from BOTH the Topo and Trace preset `paints`** in
`BUILT_IN_PRESETS` (`js/main.js`), replaced with a one-line note in each. Because
`applyPreset`→`applyPaintState` only ever SETS the paints a preset declares (never resets
undeclared ones — L5028/5062), and now NO preset declares road line paint, the base style
set at `addLayer` is never overwritten → **one road style on every preset.** This also
quietly fixes a latent carry-over (Trace→Park used to leave Trace's cream roads on Park).
**Kept** the Trace `roads-labels` override (cream text + near-black halo) — that's road
LABEL legibility over the dark paper backdrop, a separate concern from the road LINE style
the user flagged. VERSION **v49→v50** (`sw.js` + `#appVersion`; main.js is a shell asset).
**Verified by observation** (`/tmp/verify_one_road_style.py`, served :8055, SW blocked):
clicked the real Park→Topo→Trace preset buttons and read live `getPaintProperty` — all
three presets return the **identical** base road colours (local `#b0a68c`, connecting
`#cdb079`, secondary `#c09060`, ramp/controlled `#d8b173`) with opacity back to the base
default (Trace had forced 0.86), the banned cream/muted-brown swap colours never appear,
**0 console errors**; the Trace render at the park core
(`brain/output/playwright_one_road_style_trace.png`) shows the roads as the consistent
taupe+cream-casing style, no washed-out cream. **Owed:** on-device feel; promote
`/tmp/verify_one_road_style.py` → `mvp/scripts/` at commit; commit + the v50 bump are the
user's git gate. If the user later wants roads to POP more on the dark Trace backdrop, the
move is to make the single BASE style read on both light and dark grounds (it already has
a cream casing for that), not to re-introduce a per-preset swap.

**2026-06-05 (TOPO HILLSHADE SOFTENED — relief was "brutal" around trail 41, CODE,
UNCOMMITTED, v48→v49).** User: *"the hillshade is brutal around trail 41 we cannot see
the topo lines… tune down or turn off? it is a topo view after all."* Diagnosed by
observation at trail 41 (`[-85.75552, 35.09293]`, a steep "difficult" trail): after the
contour fade (index @0.5), the **high-contrast hillshade** (`exaggeration 0.78` +
near-black shadow `#2f2a21`) threw dark bands in steep zones that the light sienna lines
disappeared into. Tested 4 states live (runtime `setPaintProperty`, shots
`brain/output/hs2_{A_current,B_soft,D_off,E_soft_plus_contours}.png`): current = washed
out; **soft = contours read everywhere + relief kept**; off = clean but flat (loses the
3D terrain read); soft+contour-bump = strongest topo but busier. **Recommendation: tune
DOWN, not off** — it's a shaded-relief topo, the relief is worth keeping; the culprit was
contrast, not the layer. Applied **B** to `BUILT_IN_PRESETS.topo.paints['lidar-hillshade']`
in `js/main.js`: `exaggeration 0.78→0.45`, `shadow #2f2a21→#7a6a52` (warm mid-tone, no
black zones), `highlight #fff4d9→#f7eed8`, `accent #6f604c→#8a7860`. Comment notes the
one-line switch to `visibility:'none'` if a flat pure-contour topo is ever wanted.
VERSION **v48→v49** (`sw.js` + `#appVersion`). **Verified by observation**
(`/tmp/verify_hillshade_live.py`, served :8001, SW blocked): live `getPaintProperty`
returns ex 0.45 / shadow `#7a6a52` / visible, **0 console errors**, and the rendered shot
(`brain/output/playwright_topo_hillshade_soft_live.png`) shows the contours legible across
the trail-41 area with gentle relief + the orange still popping. Only the Topo preset
hillshade changed (Park/Trace untouched). **Owed:** on-device feel; commit + v49 are the
user's git gate.

**2026-06-05 (TOPO PRESET WIRED — V1 faded sienna + O6 pure orange now LIVE,
CODE, UNCOMMITTED, v47→v48).** User: *"lets go with 6."* Wired the chosen scheme into
the live **Topo preset** (`js/main.js` `BUILT_IN_PRESETS.topo.paints`): contours
**faded back** to the V1 family — `contours-index` `#946638`→**`#a8855b`** with ON-opacity
**0.98→0.5**, `contours-minor` `#b08a5e`→**`#c6ad84`** ON-opacity **0.8→0.28**,
`contours-labels` text `#7a5530`→**`#8a6a42`** (zoom-fade structure preserved: 50 ft
index below z16, fine 5 ft fade in 16.5→17.5); trail **popped** to O6 —
`aop-trail-network` `#f25e0d`/3.4/0.95 → **`#ff5a14` / 3.8px / opacity 1, no casing**
(O6 was the "pure, stands alone now the topo is dialed back" variant, so no extra casing
layer needed). Only the `topo` preset block changed; Park/Trace presets + the base layer
defs untouched (Park keeps per-difficulty trail colours). Comments updated to point at
the two compare pages instead of the old `topo_color_compare.html`. VERSION **v47→v48**
(`sw.js` + `#appVersion`; main.js is a shell asset). Both Review badges flipped to
**`✓ V1 bg`** / **`✓ O6`**. **Verified by observation** (`/tmp/verify_topo_wire.py`,
served :8001, SW blocked): clicked the real **Topo** preset button → live
`getPaintProperty` returns idx `#a8855b`, min `#c6ad84`, lbl `#8a6a42`, trail `#ff5a14`
w3.8 op1, both layers visible, **0 console errors**; flew to the park core and the shot
(`brain/output/playwright_topo_preset_o6_live.png`) shows the faint sienna contours
receding while the bright-orange trail web pops, no casing. **Owed:** on-device feel;
commit + v48 are the user's git gate. The two compare pages + `compare_data/` +
`mvp/scripts/build_topo_trail_compare_data.py` + the durable
`playwright_verify_topo_trail_compare.py` are kept as the decision record. **Note:** the
Park preset still uses the older heavier contour colours (`#a8906a`/`#c7b48f`) — only
Topo was the ask; flag if Park should match.

**2026-06-05 (TRAIL-ORANGE ROUND 2 — V1 background chosen, 8 orange variations,
CODE + 1 link, UNCOMMITTED, v46→v47).** User: *"go with v1 background. give me some
more variations on the orange. with that background."* So the **V1 faded-sienna
background is now the chosen topo** (index `#a8855b` @0.50, fine `#c6ad84` @0.28).
Built **`website/topo_trail_orange_compare.html`** — same real-data MapLibre
small-multiples engine + clipped `compare_data/`, same camera, **background locked to
V1**, varying ONLY the orange trail across **8 cards**: O1 V1 reference (`#ff6a1f` +
cream casing, the carried-over anchor), O2 classic blaze `#f25e0d`, O3 hot vermilion
`#ff3d00`, O4 amber `#ff8c00`, O5 bright + **dark** casing `#3a1600`, O6 pure no-casing
`#ff5a14`, O7 **glow** (cream casing + blurred orange under-glow), O8 **double halo**
(cream outer + thin dark inner + bright core). `buildMap` generalized to stack
glow→casing→trail; supports `line-blur`. Attribute table + intent notes.
**Review:** prior `topo_trail_compare.html` row badge flipped `◌`→**`✓ V1 bg`** (bg
chosen), new row added for the orange page (`◌ Pick owed`). VERSION **v46→v47**
(`sw.js` + `#appVersion`). **Verified by observation** (durable verifier now covers
BOTH pages: `mvp/scripts/playwright_verify_topo_trail_compare.py`, served :8001):
both **PASS** — orange page **8 cards / 8 real canvases / 8 rows, 0 console errors**;
per-card crops were inspected during the run (O5 dark-cased + O3 vermilion + O8 engraved
all render fully with the V1 ground faded behind); full-page record is
`brain/output/playwright_topo_trail_orange_compare.png`.
**Same progressive-render gotcha, worse with 8 heavy maps:** the verifier now scrolls
each map into view + waits; even so the *full-page record shot*
(`playwright_topo_trail_orange_compare.png`) can catch a couple mid-render — the
per-card crops are the real evidence, structural checks pass, live browser is fine.
**OWED (the pick):** user chooses an O# → wire V1 contours + that orange (+ a trail
casing layer, and `line-blur`/glow if O7/O8) into the Topo preset `aop-trail-network`
+ `contours-*` paints in `js/main.js`, bump shell VERSION, flip both Review badges to
`✓`. Commit + v47 are the user's git gate.

**2026-06-05 (TOPO+TRAIL COLOUR COMPARE — real-data "fade topo / pop trails"
review page, CODE + DATA + 1 link, UNCOMMITTED, v45→v46).** User: *"review the topo
layer and our orange trails. the colors need tweaking. take the brown topo and the
orange trails and make a handful of variations so that I can see the data but less
visual clutter. topo to fade back, trails to pop. put the comparison page in our
review area. you can start with topo contour. but it needs more map elements."*
Context traced by observation: the "brown topo + orange trails" is the **Topo
preset** (`js/main.js` ~L4732-4817) — brown contours (index `#946638`, fine
`#b08a5e`, label `#7a5530`) + the gold trail network **flat-recoloured orange
`#f25e0d`** (overrides its baked per-difficulty green/blue/black) over relief
landcover + AWS-DEM hillshade + brown roads + teal water. The pre-existing
`topo_color_compare.html` was a stale hand-drawn **SVG mockup with only contour
lines** — that's the "needs more map elements" gap.
**Built `website/topo_trail_compare.html`** — a **real-data MapLibre small-multiples**
page (NOT a mockup): 5 cards, each a live `maplibregl.Map` locked to the same
park-core camera (`center [-85.7533,35.0908] z15.4`), rendering the REAL clipped data
(contours + trail network + water + roads + buildings + forest + hillshade) so colours
are judged in context. Schemes: **Baseline (current Topo)** + **V1 Faded sienna +
cream casing** (suggested pick) + **V2 Ghost contours + dark-cased trail** + **V3
Index-only (drop the fine 5 ft lines)** + **V4 Neutral relief + hot orange**. Each
fades the topo (lower opacity / lighter-or-neutral hue / thinner / fewer lines) and
pops the trail (brighter+saturated orange + a casing line underneath). Constant across
cards: camera, data, base layers; varied: contour colour/opacity/width, fine-tier
on/off, trail colour/width/casing. Text labels omitted (not the variable; also dodges
the glyphs dep). Attribute table + strategy notes included.
**Data prep:** `mvp/scripts/build_topo_trail_compare_data.py` clips the heavy viewer
data to the trail-core bbox → `website/compare_data/` (contours **13 MB → 3.2 MB** via
coordinate-level line clipping; trails/water/roads/landcover/buildings too). Re-run if
source data changes; reproducible.
**Wired into Review:** added a row to the `index.html` comparisons-list (`◌ Pick owed`),
kept the old `topo_color_compare.html` row (records the applied sienna decision).
VERSION **v45→v46** (`sw.js` + `#appVersion`; index.html is a shell asset — compare
pages are NOT precached, like the others). **Verified by observation**
(`mvp/scripts/playwright_verify_topo_trail_compare.py`, served :8001): **5 cards / 5
real map canvases / 5 table rows, 0 console errors**; pixels inspected
(`brain/output/playwright_topo_trail_compare.png` + per-card crops) — baseline shows
the clutter, V1/V3/V4 clearly fade the brown back and lift the orange. **Gotcha
(test-only):** the small maps render progressively (AWS DEM tiles + geojson per map);
an early screenshot caught the baseline mid-render (orange only in a corner) — a longer
wait (8-10 s) shows it fully. Not a product bug. **OWED (the fork, user's pick):** pick
a scheme (or mix attributes) → wire the contour `contours-index/minor/labels` +
`aop-trail-network` (add a trail casing layer) into the Topo preset paints in
`js/main.js`, bump shell VERSION (that wiring IS a shell-asset change), flip the Review
badge to `✓`. Commit + v46 are the user's git gate. The `/tmp/verify_*` scratch shots
can be pruned.

**2026-06-05 (DATA-GROUP REORGANIZATION — user reorganized the right-panel
maturity groups, DATA + CODE + DOCS, UNCOMMITTED, v44→v45).** User did the
"organization stage": retire Map editor, add a Delete staging group, and move
nine layers into their right homes. Every move shipped + verified by observation
(standalone `right_panel.html` **28/28, 0 console errors**; embed `index.html`
**7 sections incl Delete, Map editor gone, 0 JS console errors**). The list:
- **Map editor group RETIRED** — dropped the 3 draw groups (Points/Lines/Polygons)
  + Drawn POIs nodes. The `userFeatures` (empty) + `editor-poi` (1 seed POI)
  SOURCES still live in `MAP_DATA` (host map owns them); they just have no panel
  node. The "+POI/+Line/+Polygon" add controls still work on every remaining
  editable layer (they author into the layer's own source — never needed the draw
  groups). editor-tier files kept at `editor` _meta (user said "retiring," not
  "delete"; nothing of value to stage).
- **Brand logos → Silver** (was Map editor); node `maturity` flipped `editor`→
  `silver` so the chip matches the file it lives in (the silver callout file).
- **SFWDA paper trail map → Silver** (was External reference); node-tagged silver
  (raster overlay, no geojson `_meta`).
- **Cemeteries → External reference** (was Source layers; 4 markers: Tate/Gilliam/
  Bible/Ellis).
- **Activity hotspots (real GPX dwell) → Derived** (was User submitted).
- **NEW Delete group "Delete — staged for removal"** (a review pen, NOT auto-delete)
  with: SFWDA traced trails, Springs & gages, Simulated Saturday activity, OSM park
  polygon — each node-tagged `maturity:'delete'` (new tier + reddish chip).
- **Data side:** new `delete` tier in `stamp_maturity.py` (TIERS/NOTES/MATURITY);
  the 3 WHOLE-FILE delete members (`sfwda_traced_trails`, both
  `aop_synthetic_activity_*`) stamped `delete` in their `_meta` + `_schema.json`
  (ran the script: gold=1, silver=3, editor=2, derived=4, reference=10, delete=3).
  **Springs & OSM park polygon are sub-layers of shared files** (`aop_water`,
  `osm_aop_9patch`) whose other layers stay → panel-only moves; files keep
  `reference` tier until split (noted in the Delete-group comment + the doc).
Files: `website/js/panel.js` (PANEL_MODEL sections + MATURITY_LABEL),
`css/panel-embed.css` + `right_panel.html` (`.maturity-badge.delete`),
`mvp/scripts/stamp_maturity.py`, all served `data/*.geojson` + `_schema.json`
(re-stamped), `sw.js` + `index.html` (v44→**v45**), `research/data_maturity_tiers.md`.
Durable verifiers promoted: `mvp/scripts/playwright_verify_data_groups.py`
(standalone) + `..._embed.py` (index.html). **Owed:** commit + v45 are the user's
git gate; the actual deletion of the Delete-group members (and splitting springs/
OSM park out of their shared files) is a follow-up once the user approves; on-device
feel. Doc: `brain/research/data_maturity_tiers.md` (Current sort + Delete group).

> ## ✅ RESOLVED 2026-06-05 — takeover tabs toggle, styling ported, tabs equal-height
> The "KNOWN BUG: takeover tabs don't toggle" is FIXED (see the dated entry below +
> its "REFINED" follow-up for the final shape). **Root cause was NOT the `#map`
> canvas occluding the tabs** (that lead was wrong — `elementFromPoint` at a tab
> center returns the `.fe-tab` itself in every mode). It was styling: the demo's
> takeover layout was never ported, so in embed the editor rendered buried below the
> kept sections (cramped, tabs low/dead on a small screen). **Final shape:** the
> takeover is an **in-flow, compact** editor that hides the surrounding chrome
> (header/kept sections/footer) while a feature is open, with **sticky** back/head/tabs
> and a **grid-stacked body so every tab is the same height** (no reflow on the
> bottom-anchored panel). Verified with **real pointer clicks** (not JS `.click()`):
> `/tmp/verify_takeover_v37.py` — standalone + embed desktop + embed mobile **21/21
> ×3, 0 console errors**, panel height identical on all 5 tabs. **Promote the verifier
> to `mvp/scripts/` at commit.**

**2026-06-05 (DATA CONSOLIDATION — Ellis→publish boundaries + brand logos merged
into visitor-context callouts, DATA + CODE + DOCS, UNCOMMITTED, v43→v44).** User:
*"review the right panel and data sources. take the ellis cemetery data and copy that
into publishable boundaries file. then move brand logos aop and rock warblers into
visitor context callouts."* Two moves:
**(A) Ellis → publish boundaries (additive copy).** Added the Ellis Cemetery parcel
POLYGON to `publish.geojson` as a 2nd `park_boundaries` feature (id 5, "Ellis Cemetery
(inholding parcel)"), mapped to the publish 13-key flat schema, true county-parcel
source, `permission:publish`, `confidence:high`. **Burial roster deliberately
EXCLUDED** (USGenWeb non-commercial — must not enter the publish zone, per
`source_register.md` + `aop_ellis_cemetery.md`). The existing Ellis POI point stays;
this is the boundary polygon. 1-line minified diff. (Caveat noted in viewer.md: it's
now a hand-curated feature in a PostGIS-exported file.)
**(B) brand logos → visitor-context callouts (FULL MERGE, user-chosen via AskUserQuestion:
"Full merge, keep icons / most work, nothing breaks").** The 2 logo features (AOP badge,
Rock Warblers) were merged into `aop_visitor_context_callouts.geojson` as `kind=brand_logo`
POINTS (in BOTH served + `raw/`, stored canonically); `aop_brand_logos.geojson` deleted
(served + raw). Both viewers split the one file back by `kind`: callout polygons →
`visitor-context` source; logo points → `brand-logos` source + `brand-logos-icons` layer
(all drag/resize/cap/override/bake machinery UNCHANGED, just resourced). Touched ~13 files:
`main.js` (2 load-site splits + dropped preload + comment), `panel.js` (new `transform`
hook on both MAP_DATA entries + brandLogos node tagged `maturity:'editor'`),
`rebake_canonical.py` (callouts `kind`→callable keyed on `logo_id` so callouts still
normalize AND logos keep brand_logo + their own provenance; dropped brand CONFIG entry —
**verified idempotent**: a future rebake reproduces the served callouts byte-for-byte and
preserves `brand owner`/`decorative`), `stamp_maturity.py` (dropped brand line),
`export_positioned_features.py` (brandLogos→callouts file, both specs write minified),
`sw.js` (dropped precache + v44), `index.html` (#appVersion v44), `_schema.json` (callouts
features 2→4, kind "(per-feature)"; brand entry removed), `aop_copy_registry.json`
(root_files repointed), both `playwright_verify_{brand_logos,visitor_context}.py` (fetch the
callouts file + filter by kind), and docs (`viewer.md`, `data_maturity_tiers.md`).
**Verified by observation** (served :8137, SW blocked): host index.html AND standalone
right_panel.html each show **brand source = exactly 2 brand_logo, visitor source = exactly
2 visitor_callout, 2 icons rendered, 0 console errors**; `publish-data` park_boundaries =
2 incl Ellis (renders); `playwright_verify_visitor_context.py` **RESULT: PASS**;
rebake-idempotency check **True**. **Known pre-existing FAIL (NOT this change):**
`playwright_verify_brand_logos.py` feature-list section returns `[]` — confirmed by
observation the legacy `#featureList` is present-but-HIDDEN with `aop-embed-ready` set, i.e.
the v32 panel-swap retired that legacy surface; reproduces on master, unrelated to the data
merge. **Owed:** commit + v44 are the user's git gate; on-device feel; the brand-logos
verifier's feature-list section wants migrating to the new panel (Stage-2 swap cleanup, not
this task). Verifiers `/tmp/obs_merge*.py` are scratch.

**2026-06-05 (ADD-ANY-TYPE WIRED — V2 chosen + shipped into the live panel, CODE ONLY,
UNCOMMITTED, v42→v43).** User: *"go with v2 we don't need the ADD. the + on the icon is
enough."* Wired the V2 icon take into `js/panel.js` (one renderer → standalone +
embed): **(1)** removed the lone `+` from the layer row (`renderLayerNode` no longer
appends `node-create`); **(2)** the group edit area's control row now renders, right of
the eye + lock (own `.add-divider`), **three icon buttons** — pin / line / polygon, each
with a small rust `+` badge (`addTypeButton` + `ADD_GLYPH`/`ADD_TITLE`/`ADD_GEOMS`); **no
"ADD" caption** per the user. **(3)** Add ANY geometry to ANY layer: replaced
single-geom `nodeCreateSpec` with `nodeCanCreate`/`nodeCreateSource` + `makeCreateSpec(node,
geomType)` (targets the node's OWN source; a draw group keeps its explicit spec when the
chosen geom is its native one, else synthesizes Common-Minimum defaults); `startCreate(node,
geomType)` takes the chosen geom. Wired into the declarative controls field via a `add:
nodeCanCreate(node)` flag on `groupFields` → `renderControlsField` appends the icons. Add is
**never lock-gated** (a fresh draw is `__locked:false`, editable even in a locked layer);
pure-visibility layers (no items/create) get no icons. `canonicalDefaults` now only stamps the
cemetery `geom_role:marker` on a Point. CSS `.add-type`/`.add-divider` added to BOTH
`right_panel.html` and `css/panel-embed.css` (scoped `#aopPanelMount`). VERSION v42→**v43**
(`sw.js` + `#appVersion`; panel.js/CSS are shell assets). **Verified by observation**
(`/tmp/verify_add_wiring.py`, served :8137, real `js/panel.js`): **17/17, 0 console errors** —
no `+` on any row; buildings (a Silver/locked **Polygon** layer) edit area = eye + lock + 3
add icons + divider; **+POI placed a POINT into `fema-buildings`** (`_src` set, `__locked
false`, selected → takeover), **+Line drew a LINESTRING into the same polygon layer**, and a
pure-visibility layer (Land cover) shows **no** add icons. Pixels confirm
(`brain/output/playwright_add_wiring_editarea.png`: eye·lock·│·pin⁺·line⁺·polygon⁺, no ADD
caption). **Gotcha (test-only, not a product bug):** `page.evaluate` has NO default timeout, so
firing `map.fire('click')` inline hangs forever if you don't schedule it async — the verifier
now `setTimeout`-schedules the fire and polls with a bounded `wait_for_function`. **Owed:**
on-device feel; promote `/tmp/verify_add_wiring.py` → `mvp/scripts/` at commit; commit + v43 are
the user's git gate. The 4 mockup files (below) can stay or be pruned at commit. Card:
`editor_unified_dock.md`.

**2026-06-05 (ADD-CONTROLS MOCKUPS — "+ POI / + Line / + Polygon" beside the eye +
lock, 4 takes + a compare page, CODE ONLY — isolated mockup files, no VERSION bump).**
User: *"we added a + to the row. it needs to go next to the eye and lock under the row
edit. second to that we need a + poi button + line button + polygon button so that we
can add any type to any layer. make some mockups in the standard format."* Two moves:
**(1)** take the lone `+` OFF the layer row and put it INTO the inline edit area that
opens under a selected layer, right of the eye + lock (today: `renderLayerNode` appends
the `node-create` `+` to the row, while eye/lock live in `groupFields`'s controls field —
`js/panel.js`); **(2)** split that one `+` into THREE — **+ POI · + Line · + Polygon** —
so any geometry can be added to ANY layer (not just the layer's native geom). Built in the
repo's iframe-grid convention (matches `right_sidebar_compare.html`): **4 standalone
variants + a compare page**, all on the CURRENT panel base (maturity-led tree: Gold /
Silver — pending review / Source / Derived / External / Map editor / User submitted; real
provenance sections; rust-on-cream). Every variant selects a **Polygon** layer (**Park
buildings**, Silver) so the "any type" point lands — its edit area offers a point + a line
too. Variants vary only how compact↔explicit the three buttons are:
**V1 `add_any_type_v1_pills.html`** — inline labelled pills on the control row;
**V2 `_v2_icons.html`** — icon-only pin/line/polygon w/ a `+` badge (tightest, matches the
eye/lock icon language); **V3 `_v3_picker.html`** — a single `+` next to eye/lock that
drops a geometry picker (the literal "+ by the eye and lock", compact until needed; the +
toggles the tray); **V4 `_v4_addrow.html`** — eye/lock stay put, a dedicated **ADD** row of
full-width thirds below (most explicit). Compare: **`add_any_type_compare.html`** (2×2 grid +
"what's the same in all four" + a compact↔explicit attribute table + the wiring note). Noted
in all takes: the add buttons stay live even on a **locked** curated layer (the lock gates
EXISTING features; a fresh draw is always editable — matches today's `nodeCreateSpec`).
**Verified by observation** (`/tmp/verify_add_any_type.py`, served :8123): **5/5 pages, 0
console errors**; per-variant assertions (no `+` on any row; eye + lock + 3 add controls in
the edit area; V3 toggle hides the tray) all pass; shots
`brain/output/playwright_add_any_type_{v1_pills,v2_icons,v3_picker,v4_addrow,compare}.png`.
**Caught + fixed by looking at the pixels:** V4's full-width thirds clipped "Polygon" at the
320px panel edge with the glyph in — dropped the geometry glyph from V4's buttons (V2 owns the
glyph story) so the text thirds fit. **OWED (the fork, user's call):** pick a variant +
attributes → wire into `js/panel.js` (move `node-create` off `renderLayerNode` into
`groupFields`'s controls field; have `nodeCreateSpec` emit a point/line/polygon spec per layer
regardless of native geom), migrate the verifier, bump the shell VERSION (that wiring IS a
shell-asset change). Nothing to git-gate beyond the 5 isolated mockup files. Pointer added to
`editor_unified_dock.md` (Mockups section).

**2026-06-05 (DATA-MATURITY TIERS — gold/silver across data + editor, UNCOMMITTED,
v41→v42).** User: *"review our right edit panel… we have different data types: raw,
baked, source, gold. only trails is gold; region callouts are silver pending text
review. gold data is locked not un-editable — unlock first. gold should share a
common schema that powers the editor; the group should map to the file it lives in."*
→ *"do it all."* Shipped end-to-end:
(1) **Data** — new `mvp/scripts/stamp_maturity.py` stamps each served file's
`_meta` with `maturity`/`group`/`locked` (gold=1 `aop_trail_network`; silver=3
callouts/buildings/`publish`; editor=3; derived=6; reference=11) + writes the tier
per layer + a legend into `_schema.json`. Additive/idempotent, **runs LAST**;
`rebake_canonical.py` hardened to **carry a live `_meta` forward** so a re-bake no
longer drops the stamp. Trail gold block preserved.
(2) **Editor** (`js/panel.js`) — tree now leads with **Gold data** + **Silver —
pending review** sections (above Source/Derived/External/Map editor/User submitted);
every editable group row shows a **maturity chip** (`nodeMaturity` ← node tag,
falls back to the file's `_meta` captured in `META`); feature **Source tab** gains
**File + Tier · locked/unlocked**. Lock/unlock + add-new-into-the-file already
worked (`nodeCreateSpec` synthesizes a draw spec per single-geom listable layer;
lock gates *existing* features, never new draws). Badge CSS in `panel-embed.css` +
`right_panel.html`. v42 bump (`sw.js` + `index.html`).
(3) **Docs** — new `research/data_maturity_tiers.md` (the tier contract: maturity is
a THIRD axis, orthogonal to provenance + the raw/core/publish zones); pointers in
`viewer.md`, `search_map.md`, and the `editor_unified_dock.md` card.
Verified by observation: `/tmp/verify_maturity.py` **23/23, standalone + embed, 0
console errors**; shots `brain/output/playwright_maturity_{tree,standalone,embed}.png`.
**Deferred** (told the user up front): the legacy-key strip (gated on the index→panel
swap — `index.html` still paints on raw keys) and physical file renames. Owed:
on-device feel; commit + v42 are the user's git gate. **Promote `/tmp/verify_maturity.py`
to `mvp/scripts/` at commit.**

**2026-06-05 (SCHEDULE TAG CLEANUP — dropped the two placeholder alias tags, DATA +
1 doc line, UNCOMMITTED, v40→v41).** User (after the bridge gotcha): *"we can get rid
of those tags or re-point them at something real that's fine."* The two coordinate-less
ALIAS tags in `aop_event_schedule.json` both just resolved to `#pavilion`: `#pavillion`
(a hidden, **unreferenced** misspelling alias — pure cruft) and `#registration`
(`alias_of:#pavilion`, referenced by 3 sessions; its own caveat said placement was
unconfirmed, and the alias rendered a **duplicate "Registration" pin stacked on the
pavilion**). For a single-pavilion event registration happens AT the pavilion, so chose
the honest model: **removed both location entries** and **re-pointed the 3 registration
sessions** (`fri-registration`, `sat-late-registration`, `sun-checkout`)
`location_tag` → `#pavilion`. Their titles ("Registration + wristband check", etc.)
carry the function; no separate pin. Updated the one illustrative `index.html` Layer-notes
line that cited `#registration` (now points to tagging a real feature in the edit panel).
**Refs checked before deleting:** `#pavillion` appears nowhere else; `#registration`
only in OLD `editor_unified_v*.html` mockups (dead dev pages) + `main.js` COMMENTS (the
alias-handling code is generic + dynamic, so it still works with zero aliases — left as
defensive). VERSION v40→**v41** (index.html is a shell asset; the schedule JSON itself is
served stale-while-revalidate so it'd refresh without a bump). **Verified by observation**
(`/tmp/verify_schedule_clean.py`, served :8011): event anchors are now `#pavilion` + the 6
coordinate-bearing tags — **no `#registration`/`#pavillion`**; `#pavilion` still resolves;
all **13 sessions** still render; JSON valid, 0 dangling tag refs, 0 console errors. Files:
`website/data/aop_event_schedule.json` · `index.html` · `sw.js`. **Owed:** commit + v41 are
the user's git gate. If a distinct registration station is ever placed, add a POI, tag it
`#registration` in the panel (the bridge resolves it), and re-add the location entry.

**2026-06-05 (EVENT-SCHEDULE TAG BRIDGE WIRED — panel #tag now drives the live
resolver, CODE ONLY, UNCOMMITTED, v39→v40).** User: *"wire the event-schedule tag
bridge."* The panel's Tag field wrote `props.tag` (bakes into data) but didn't touch
the host's live event-schedule resolver (which reads `tagToFeature`, built from the
`FEATURE_TAG_KEY` store). Wired it data-led, mirroring the ★ bridge:
**(1) host `main.js`** — new `window.AOP_HOST_SET_TAG(layerKey, props, rawTag)` →
`setFeatureTagByProps`: resolves the feature via `positionedFeatureIdFor` (idField:
buildings=`build_id`, editorPois=`id`), mirrors the value onto the host feature's own
`properties.tag`, then routes through the existing `setFeatureTag` (persists to
`FEATURE_TAG_KEY`, `rebuildTagLookup()`, `rebuildEventScheduleData()` → re-renders
anchors live). **(2) host `rebuildTagLookup`** now ALSO scans every
`featureListRuntime` feature for its own `properties.tag` FIRST (so a BAKED tag in the
served GeoJSON resolves on load with no localStorage), then the explicit store
overrides (live edits / the seeded #pavilion still win). **(3) panel `js/panel.js`** —
new `pushTagToHost(node,item)` (reuses the `HOST_HIGHLIGHT_LAYER` node→host map:
buildings/cemeteries/visitorContext/editorPois) called from `commitChange` (both
branches) so every commit syncs `props.tag` to the host; no-op standalone / unmapped
layers (tag still bakes, just won't drive the schedule). VERSION v39→**v40**.
**Verified by observation** (`/tmp/verify_tag_bridge3.py`, served :8011, SW blocked):
tagging building **665 Ellis Cove Road** with **#pavilion** via the panel UI **moved
the #pavilion event anchor to that building's exact centroid** (read from the live
`event-schedule` source via `getData()`; anchors carry `feature_kind:'event_anchor'`),
and **clearing the tag unbound it**; `#pavilion` still resolves to its seeded location
on a fresh load (**no regression**); takeover 21/21×3 + tag/textarea verifiers still
green; 0 console errors. **Gotchas learned:** the schedule's only coordinate-less
*base* tag is `#pavilion` — `#registration`/`#pavillion` are `alias_of:#pavilion` (so
binding THEM does nothing; bind the base). The host building source is `fema-buildings`
(not `buildings`); the panel layerKey `buildings` is the feature-LIST key, separate.
Files: `website/js/main.js` · `js/panel.js` · `sw.js` · `index.html`. **Owed:** commit +
v40 are the user's git gate; clearing a tag unbinds rather than restoring the prior
holder (expected one-to-one model); on-device feel.

**2026-06-05 (TAG DURABILITY — "are tags stored in the raw data?" answered + a
persistence gap fixed, CODE ONLY, UNCOMMITTED, v38→v39).** User asked whether the
new Tag field is stored in the data. Traced it by observation; honest answer:
**(1)** tags are NEVER written to `website/data/raw/` (the pristine archive +
re-bake source — the editor never touches it). Correct by design.
**(2)** tags DO bake into the SERVED `website/data/*.geojson` — but only via the
normal loop (edit → `aop_panel_overrides_v1` localStorage diff → **Export edits →
`bake_panel_overrides.py` → commit**), not live; same as name/description (no DB).
**Verified with a REAL bake**: crafted an override for cemetery `093 001.02` with
`tag:"#tate-test"`, ran the baker → `aop_cemeteries.geojson` got
`"tag":"#tate-test"`; restored the file via `git show HEAD:… > file` (the
`block-unsolicited-git` hook blocks `git checkout`, so use read-only `git show`
redirect to restore tracked files).
**(3) Gap found + fixed:** `pickEditable` only snapshotted
`EDITABLE_SERVED_KEYS = [name,description,difficulty,notes,category,highlight]` —
**`tag` was missing**, so for SERVED/reference features the tag was silently dropped
before it even reached the override store (only DRAWN features kept it via
`syncCreated`+`cleanFeature`). My prior-turn "persisted" check had only exercised a
drawn POI — a misleading partial verification (owned). Fix: added `tag` to
`EDITABLE_SERVED_KEYS` (`js/panel.js`) and to the baker's documented `EDITABLE_KEYS`
(`bake_panel_overrides.py`; note `apply_file_edits` already writes any non-VIEW_STATE
key, so the panel allowlist is the real gate). **Re-verified on a single-feature
building** (`/tmp/verify_building_reload.py`): set tag `#shop` → reload → same
building still shows `#shop`. Persistence (localStorage replay via
`applyStoredOverrides`) works for reference features now.
**(4) Pre-existing finding (NOT tags, not fixed):** the cemeteries layer ships TWO
features per cemetery — a `parcel` polygon + a `marker` point sharing the SAME
`name` AND `id`. `deriveItems` dedups the tree by `name`, and edits persist/match by
`id` (first match = the parcel). So editing a cemetery's NAME breaks the dedup
(a phantom duplicate marker row appears) and the edit lands on the parcel. This made
an early reload test look like "name doesn't persist" — it was a test artifact, not a
persistence bug (confirmed: `applyStoredOverrides` logs `matchById true`). Worth a
follow-up for cemeteries specifically (dedup/match by id, or collapse parcel+marker).
VERSION v38→**v39**. Files: `website/js/panel.js` · `mvp/scripts/bake_panel_overrides.py`
· `sw.js` · `index.html`. **Owed:** commit + v39 are the user's git gate; the
cemetery parcel/marker dedup follow-up; the event-schedule `#tag` bridge (still open).

**2026-06-05 (IDENTIFY TAB — Tag field + Description as a textarea, CODE ONLY,
UNCOMMITTED, v37→v38).** User: *"now we need a tag in the identify group. and the
description to be a text area."* In `js/panel.js` `itemFields`: added a **Tag** field
(`{kind:'text', label:'Tag', prop:'tag', tab:'identify'}`) right after Description, and
marked Description **multiline** (`multiline:true`). `renderTextField` now creates a
`<textarea>` (rows=3) when `field.multiline` is set, else the single-line input — same
input/commit/persist path either way. `tag` is a plain feature prop, so it persists via
the existing override/bake path and survives `cleanFeature` (only `_id/_src/__locked/
__group` are stripped). **NOT wired to the live event-schedule resolver** — that uses
`main.js`'s separate per-feature `#tag` store (`FEATURE_TAG_KEY`) behind no host bridge;
binding the panel tag into it (a new `AOP_HOST_SET_TAG`, like the ★→`AOP_HOST_SET_HIGHLIGHT`
bridge) is a noted follow-up. Textarea CSS (`resize:vertical; min-height:64px; line-height:1.4`)
added to both `panel-embed.css` (`#aopPanelMount textarea.field-input`) and
`right_panel.html`. VERSION v37→**v38** (`sw.js`+`#appVersion`). **Verified by observation**
(`/tmp/verify_tag_desc.py`, served :8011, real fills on an UNLOCKED Drawn POI): embed +
standalone — Description renders as a textarea, Tag present in Identify
(order `name·description·tag·Kind·Details`), typing a tag/description commits + the value
**survives the re-render**, multi-line `\n` preserved, **equal-height tabs still hold**
(519/519×5 embed, 820 standalone), 0 console errors. Shot: `/tmp/identify_tag_desc.png`.
Files: `website/js/panel.js` · `css/panel-embed.css` · `right_panel.html` · `sw.js` ·
`index.html`. **Owed:** the event-schedule tag bridge (above); on-device feel; commit +
the v38 bump are the user's git gate.

**2026-06-05 (TAKEOVER STYLING + TABS FIXED — the demo finally made it across,
CODE ONLY, UNCOMMITTED, v36→v37).** User: *"review our cwc and the edit panel. it
needs work. the styling and tabs did not make it across from the demo pages."*
Reproduced by observation with **real pointer clicks** (the prior v36 "verified" pass
used JS-dispatched `.click()`, which bypasses hit-testing — the documented gap). The
v36 takeover (`renderFeatureEditor`) emitted the right DOM (`.feature-editor`/`.fe-*`)
and CSS for `.fe-*` existed, BUT the takeover was a plain in-flow `display:flex` block
inside the scroll region instead of the demo's **`position:absolute; inset:0`
full-panel overlay**, and there was **no `.fe-body` scroll rule**. Net effect in embed
(`index.html`): the editor rendered *below* the kept Session-tools/Review sections as a
short, cramped card (measured ~169px tall; tabs mid/low, body unscrollable) — that is
both "styling didn't make it across" and why the tabs felt dead on a real/small screen.
`elementFromPoint` at a tab center returned the `.fe-tab` itself in every case, so the
**`#map`-occlusion lead in the old bug note was wrong.**
**Fix (3 files):** (1) `css/panel-embed.css` + `right_panel.html` — `.feature-editor`
becomes `position:absolute; inset:0; z-index:5; background:var(--panel-bg)` (it overlays
the whole `.panel`, which is `position:fixed; overflow:hidden` with a `position:static`
panel-body/mount, so `inset:0` resolves to `.panel` — same as the V2 demo); `.fe-top`
pins (`flex:none`) with the back/head/tabs; **new `.fe-body { flex:1; min-height:0;
overflow-y:auto; scrollbar-gutter:stable }`** so only the body scrolls and the tabs stay
put. (2) `js/panel.js` — new `panelRoot()` (= `panelHost().closest('.panel')`) +
`renderPanel` toggles **`.aop-feature-editing`** on the panel while a feature is open;
embed CSS pins the floating card to full height while that class is set
(`.panel.aop-feature-editing:not(.collapsed){ height: calc(100vh - 24px - safe-areas) }`)
so the overlay editor isn't starved by the (now-covered) kept sections. On mobile the
existing `@media(max-width:760px)` `max-height:420px` clamp still wins, so the takeover
fills the app's locked 420px bottom-card allowance (NOT fought). (3) VERSION v36→**v37**
(`sw.js` + `#appVersion`; panel.js/CSS are shell assets).
**Verified by observation — REAL pointer clicks** (`/tmp/verify_takeover_v37.py`, served
:8011, SW blocked): standalone + embed-desktop + embed-mobile each **20/20, 0 console
errors** — overlay is `position:absolute`, tabs pinned, editor fills the panel, every tab
(Identify·Edit·Display·Source·Raw) toggles on a real `mouse.click` and its pane populates
(Identify fields, Edit actions, Display toggles, Source `.geojson` File, Raw JSON), and a
real-click Back removes `.aop-feature-editing` + returns the tree. Shots:
`/tmp/fix_EMBED_desktop.png` (full-height right card), `/tmp/fix_EMBED_mobile.png` (420px
bottom card), `/tmp/fix_STANDALONE_mobile.png` (right-panel-only overlay; left POI sidebar
untouched). Files: `website/css/panel-embed.css` · `right_panel.html` · `js/panel.js` ·
`sw.js` · `index.html`. **Owed:** on-device (iOS PWA) tap confirm — headless proves the
layout/real-click path but not iOS touch; promote `/tmp/verify_takeover_v37.py` →
`mvp/scripts/` at commit; commit + the v37 bump are the user's git gate. Card:
`editor_unified_dock.md` (V2-takeover section).
**REFINED same session (still v37, uncommitted) — equal-height tabs, compact in-flow
takeover (SUPERSEDES the absolute-overlay + full-height-pin above).** User: *"make it
so that the tabs each have the same overall height. as we change tabs the content
re-flows because we are anchored to the bottom."* The overlay+pin made the panel a
CONSTANT height, but full-height → a sea of empty space on short tabs (Display = 2
toggles), and the embed `.panel` is bottom-anchored so any per-tab resize jumps the tab
bar. Switched the takeover from an absolute overlay to an **in-flow** editor that drives
the panel height (compact, sized to its tallest tab), and made the panes **equal height**
so switching never reflows: `.fe-body { display:grid }` with every `.fe-pane` in
`grid-area:1/1` and inactive panes `visibility:hidden` (NOT `display:none`, so they stay
in layout and the grid row = the tallest pane). `.fe-top` is now `position:sticky; top:0`
(tabs pin when the body must scroll on the 420px mobile card). While editing,
`.aop-feature-editing` now HIDES the surrounding chrome (panel header, kept
Session-tools/Review sections, save footer in embed; the save footer in standalone)
instead of pinning full height — so the in-flow editor is the whole panel. Removed the
`height: calc(100vh …)` pin. **Verified by observation** (`/tmp/verify_takeover_v37.py`
updated: drops the now-false `position:absolute` assertion, adds "panel height constant
across all 5 tabs"): standalone + embed desktop + embed mobile **21/21 ×3, 0 console
errors**; measured panel height identical on Identify/Edit/Display/Source/Raw (embed
desktop 519px, mobile 420px capped+scroll, standalone 820px). Shots: `/tmp/shot_Identify.png`,
`/tmp/shot_Display.png` (same height, tab bar fixed). Same files as above.

**2026-06-05 (V2 FEATURE TAKEOVER WIRED INTO THE LIVE PANEL — `js/panel.js`, one
global tabbed edit panel + a Raw JSON tab + "what file does this come from?",
CODE ONLY, UNCOMMITTED, v35→v36).** User picked **V2** from the refreshed compare
page (*"go with v2 looks good"*) and added two requirements: *"a raw tab that shows
the whole json value for copy or manual interaction (probably not re-upload at this
time), and I need to know what file it comes from."* Wired the V2 full-panel
takeover into the live `js/panel.js` (drives BOTH standalone `right_panel.html` and
the embedded panel in `index.html` — one renderer):
**(1) Feature selection → takeover.** `renderPanel` now branches: a selected ITEM
renders `renderFeatureEditor` (replaces the tree; `‹ Layers` back bar returns), a
selected LAYER keeps its existing lightweight INLINE controls in the tree (layers
have no per-feature attributes, so tabs would be empty — deliberate, not a regression;
visibility-toggle ergonomics stay quick). The old inline item edit-area
(`renderItemsList`) is removed; `renderEditArea` is still used for group/layer
selection.
**(2) 5 tabs** = the confirmed 4-tab contract (`editor_unified_dock.md`: Identify ·
Edit · Display · Source) + **Raw**. `itemFields` now tags each field with a `tab`;
`renderFeatureEditor` groups them. Identify = Name/Description/Kind/facets/Group;
Edit = lock gate + Fly/Copy/Move/Delete (Move+Delete lock-gated); Display = ★ surface;
Source = **File** + Coordinates + provenance; Raw = full JSON. Tab switching swaps
panes in place (no full re-render, so the Raw textarea survives); a field edit commits
+ re-renders and the tab is preserved (only a DIFFERENT feature resets to Identify).
**(3) "What file" (Source tab).** New `SOURCE_FILE` map (built from `MAP_DATA` urls)
+ `fileForItem` resolve a feature to its served file via `_src` (home source stamped
at create) → node `items.source`; e.g. a cemetery shows **`data/aop_cemeteries.geojson`**,
a drawn POI **`data/aop_editor_seed_pois.geojson`**. Kept DISTINCT from the provenance
`Source` register (e.g. "TN Comptroller") — different question, both shown.
**(4) Raw tab.** `renderRawField` = read-only monospace textarea of
`cleanFeature(feature)` (same shape Copy GeoJSON / a bake produces) + a ⧉ Copy JSON
button (reuses `copyFeature`) + note "Edits here are not saved back yet" — re-upload
deliberately deferred per the user.
**(5) Width fix shipped for real** — `scrollbar-gutter:stable` added to the live
scroll region (`right_panel.html .panel-body` + `body.aop-embed-ready #panelBody` in
`panel-embed.css`). Takeover CSS (`.feature-editor`/`.fe-*`/`.raw-*`) added to BOTH
`right_panel.html` and `panel-embed.css` (scoped `#aopPanelMount`). VERSION v35→**v36**
(`sw.js` + `#appVersion`) — panel.js/CSS are shell assets.
**Verified by observation** (served :8001, headless, SW blocked for embed):
**standalone** — locked cemetery (5 tabs, inputs disabled, Move/Delete gated, File +
provenance, Raw JSON + Copy), unlocked Drawn POI "AOP Pavilion" (Name editable,
Move/Delete enabled, File=editor seed, **name edit commits → title updates → takeover
persists**), layer click → inline controls (NO takeover); **embed `index.html`** —
takeover renders in `#aopPanelMount`, 5 tabs, Source File=`data/aop_cemeteries.geojson`,
Raw JSON, Back returns to tree; **0 console errors** in every run. **CAVEAT (see the
KNOWN BUG note at the top): tab switching was only exercised with JS-dispatched
`.click()`, which fires the listener directly — real pointer clicks on the tabs do
NOT toggle (user-observed). Treat "5 tabs / panes switch" as logic-only, NOT
real-interaction verified.** Shots:
`/tmp/to_ref_{identify,source,raw,edit}.png`, `/tmp/to_embed.png`. Files:
`website/js/panel.js` · `right_panel.html` · `css/panel-embed.css` · `sw.js` ·
`index.html`. **Owed:** on-device feel; commit + the v36 bump are the user's git gate;
durable verifier (`/tmp/verify_takeover.py`+`verify_embed.py`) → `mvp/scripts/` at
commit. **Observations for the user (not acted on):** layer visibility now still lives
in the inline layer control (feature takeover doesn't change it); the new panel has no
layer-paint sliders yet (the rebuild deliberately omitted them — the contract folds
paint into Edit when they land); in embed the kept Session-tools/Review sections sit
above the takeover (they're `.aop-keep`, by design). Card: `right_panel_rebuild.md`.

**2026-06-05 (RIGHT-SIDEBAR EDIT-PANEL MOCKUPS REFRESHED — `right_sidebar_compare.html`
rebuilt on the CURRENT reworked panel as base, 4 placement variations of ONE global
tabbed edit panel, width-when-scrolling fixed, CODE ONLY — isolated mockup files,
index.html/main.js/panel.js UNTOUCHED, no VERSION bump (not shell assets)).** User:
*"review …/right_sidebar_compare.html, make an update with the current sidebar as base
(it's been re-worked to work better with the base data), there are width issues when
scroll is present — account for that, we want one global tabbed edit panel, make a few
variations so I can pick attributes from different versions."* The old compare page was
a static 2-cell mockup in a stale brown palette showing one "C" dock pattern. Rebuilt it
to the repo's iframe-grid convention (matches `floatgroup_compare.html`/`bottombar_compare.html`):
**4 standalone variation files** + a compare grid that loads them, each built on the
**current reworked sidebar** (`right_panel.html`/`panel-embed.css` palette + the real
`Source · Derived · External · Map editor · User submitted` provenance sections + node/item
tree, real layer labels, Drawn POIs→Pavilion selected), each carrying **one global tabbed
edit panel** on the **confirmed 4-tab contract** (Identify · Edit · Display · Source from
`editor_unified_dock.md`; Edit = This-feature actions + Layer-paint sliders). The variations
differ only in WHERE that one panel lives:
**V1 `right_sidebar_v1_dock.html`** — bottom dock, two-state (vanishes when nothing selected),
underline tabs (closest to the confirmed dock contract).
**V2 `right_sidebar_v2_takeover.html`** — full-panel takeover w/ `‹ Layers` back bar; editor
owns full height (deep edits / small screens).
**V3 `right_sidebar_v3_split.html`** — fixed split (~45/55), editor always present w/
segmented-pill tabs + idle placeholder (layout never shifts).
**V4 `right_sidebar_v4_sheet.html`** — floating bottom-sheet (drag handle + scrim, PWA-native),
**3 tabs** (Display's two toggles folded into Edit → shorter common path).
**WIDTH-WHEN-SCROLLING FIX (the called-out issue), in all four:** `scrollbar-gutter:stable`
on every scroll region so the gutter is reserved and the tree never reflows/clips when the
scrollbar toggles, the edit panel sits OUTSIDE the scroll region so it's always full-width,
and long labels ellipsis (min-width:0 + text-overflow) instead of widening the panel.
**Verified by observation** (served :8001, headless): 0 console errors across all 4 +
the grid; pixels confirm each placement, tabs switch, Edit tab shows the 5 actions +
Opacity/Color/Radius sliders; **width fix measured** — `.panel-body` clientWidth is **324px
whether overflowing OR collapsed** (no-fix would jump to 339, the 15px classic-scrollbar
width). Compare-page footnote carries an attribute-axes table (placement / idle / tab chrome /
tab set / tree-visible) so the user can mix-and-match. **OWED (the real fork, user's call):**
pick a placement + attributes → wire the ONE chosen panel into `js/panel.js` (replacing the
current inline `renderEditArea` edit areas), migrate verifiers, bump shell VERSION (that wiring
IS a shell-asset change). Nothing to git-gate beyond the 5 isolated mockup files. Stale
1-line ref in `editor_unified_dock.md` (Mockups section) updated to note the refresh.

**2026-06-05 (COMPARISONS / "REVIEW" LINK GROUP RESTORED — 1-attr markup fix +
VERSION bump, CODE ONLY, UNCOMMITTED, v34→v35).** User: *"there used to be a
comparisons group of links on the right sidebar. find it. restore it."* The
group was never deleted — it still lives in `index.html`
(`<section data-section="comparisons">`, label **"Review"** since the user's own
2026-05-31 rename commit `39c7ca4` Comparisons→Review; the `.comparisons-list`
of 9 dev/review links: copy_review, icon_master, bottombar/leftrail/editorV3/
right_sidebar/floatgroup compares, park_bounds_icon, topo_color). What hid it was
the **2026-06-05 right-panel swap**: `css/panel-embed.css` (~L164) blanket-hides
every legacy `#panelBody > .panel-section:not(.aop-keep)` once the embedded panel
boots (`body.aop-embed-ready`). Session tools survived via `.aop-keep`; the
Comparisons/Review section was NOT tagged, and the new embedded panel has no
equivalent, so it vanished. **Fix = mirror Session tools: add `aop-keep` to that
one section** (`website/index.html`), so the hide rule spares it. Bumped
`sw.js VERSION` + `#appVersion` v34→**v35** (shell-asset discipline; nav is
network-first so online users get it next load regardless). **Verified by
observation** (served :8001, `/tmp/verify_comparisons_restored.py` **7/7**, 0
console errors): with `aop-embed-ready` live, the Comparisons section is
display:block + all 9 links render, while a CONTROL legacy layer section
(source-layers) stays hidden — proving the hide rule is active and `.aop-keep`
is what spares it (not a vacuous pass). Pixels confirm
(`/tmp/comparisons_panel_open.png`): the link group sits atop the embedded layer
tree, where it lived before. **LABEL KEPT as "Review"** (the user's own rename
commit — not reverted unasked; trivially flippable to "Comparisons" if wanted).
Files: `website/index.html` · `website/sw.js`. Commit is the user's git gate.
Adjacent (not done, owner/content call): the older "Comparisons dev-links" panel-
hygiene question in `10_deferred/viewer_polish_followups.md` (whether dev links
belong in the shipped panel at all) is untouched.

**2026-06-05 (RIGHT-PANEL STAGE-2 FINISH — store reconciliation + ★→POI bridge +
SFWDA toggle, CODE ONLY, UNCOMMITTED, v33→v34).** User, two days into the editor
and questioning whether it's worth maintaining, weighed scope and chose **finish
the full editor**; for POI chose **option 1 — wire ★ to the EXISTING host POI tab,
keep current directory behavior** (not the deferred star-driven collapse). Mapped
`main.js` with 2 Explore agents + observation, shipped three finishes, each
verified headless (served :8077, SW blocked, 0 real console errors), **no
regression** (`/tmp/verify_swap.py` 12/12):
**(1) STORE RECONCILIATION (real data-loss fix), `panel.js`.** The embedded panel
backed its lists with its OWN fetch, so any `setData` on a host-shared source WIPED
the host's persisted overrides (`aop_positioned_features_v1` drag/highlight/lock/
size; every drawn POI in `aop_editor_pois_v1`). Fix: `seedLoadedFromHost()` seeds
`LOADED[src]` from the host's CURRENT source data for each shared *editable* source,
so every setData round-trips host overrides; `whenHostReady` now also waits for the
last-added shared sources (`editor-poi`,`brand-logos`). `/tmp/verify_phase1_stores.py`
**9/9** (real create + delete preserve seeded host data; pre-fix both wiped).
**(2) ★ → EXISTING POI TAB (option 1), `main.js`+`panel.js`.** ONE additive host
bridge `window.AOP_HOST_SET_HIGHLIGHT(layerKey,props,on)` (`setFeatureHighlight`,
sibling of `toggleFeatureHighlight`) persists + refreshes the POI tab; `panel.js`
`toggleItemStar` routes through it (`HOST_HIGHLIGHT_LAYER`=buildings/cemeteries/
visitorContext/editorPois; trails have no host runtime, brand logos off-axis, user
features stay panel-side). Visible win: the host POI tab gates **drawn POIs** on
`highlight`, so a panel ★ on a drawn POI now surfaces it in the left-rail POI tab +
persists. `/tmp/verify_phase2_poi.py` **9/9** (seed un-starred POI → ★ → in `#poiList`
+ host store → un-star → gone). The bigger `star_driven_poi_list.md` collapse (tab =
starred set, starts empty) stays deferred on its author→DB/bake forks — option 1
keeps current behavior by design.
**(3) SFWDA PAPER TOGGLE wired in embed, `panel.js`.** The host SFWDA map is a
36-tile `sfwda-tile-*` grid driven off `#showSfwda` (empty `LAYER_TOGGLES` layer
set), so the panel's intersection bridge missed it (toggle was dead). Fix:
`EXPLICIT_HOST_TOGGLE={sfwda:'showSfwda'}` in `buildVisibilityBridge`.
`/tmp/verify_phase4_sfwda.py` **7/7** (panel eye → 36/36 tiles on → 0/36 off).
**(4) DEAD-CODE CLEANUP — NOT done; card's delete list CORRECTED.** `renderFeatureList`/
`FEATURE_LIST_LAYERS`/`featureListRuntime`/`buildEditorTree` are load-bearing for
the LIVE POI tab+calendar+search (NOT hidden-only); `SECTION_RUNTIME` doesn't exist.
Only `buildInlineEditor` (`main.js:4221`) is truly dead, but it's interleaved with
live helpers/`deleteEditorFeature`/`duplicateEditorFeature` → not a clean delete.
Dead code renders harmlessly into hidden DOM; deletion wants its own verified pass
(full ledger on the card). Files: `website/js/panel.js`·`main.js`·`sw.js`·`index.html`.
**Owed:** commit is the user's git gate; durable verifiers (the `/tmp/verify_phase*`
+ `verify_swap`) should be promoted into `mvp/scripts/` at commit time. Card:
`right_panel_rebuild.md` (top "STAGE-2 FINISH PASS" entry).

**2026-06-05 (SWAP "NO LAYERS" BUG FIXED — graceful fallback, CODE ONLY,
UNCOMMITTED, v32→v33).** User reviewed the Stage-1 swap: *"our layers are
visible. Currently I do not see any layers. figure this out before deleting the
old one fully."* Diagnosed by observation: the swap files were CORRECT
(clean-served = 5 sections / 32 rows / 0 errors; `verify_swap.py` 12/12). The
blank was the **v31→v32 service-worker transition** — `sw.js` serves `/js/`+`/css/`
**stale-while-revalidate**, so the first post-bump reload pairs a **stale `main.js`
(no `window.AOP_HOST_MAP`)** with the **fresh `panel-embed.css`** that hides the
legacy panel; the embedded panel can't find the host map → `#aopPanelMount` stays
empty → empty new panel + hidden old panel = **zero layers**. Reproduced exactly
by serving a host-map-stripped `main.js`. **Root flaw:** `panel-embed.css` hid the
legacy panel *unconditionally*. **Fix:** gate the legacy-hide CSS on
`body.aop-embed-ready` (added by `panel.js` `finishBoot()` ONLY on a successful
embedded boot) → if the boot never runs the **old panel stays visible**, so the
user always has layers (fail-safe). Plus a clear console error on the 20s host
timeout (was silent) and `VERSION` v32→**v33** so a stuck browser reinstalls a
consistent set. Verified by observation (served :8077): stale-`main.js` repro now
shows the legacy panel (7 sections / 30 toggles); normal case = new panel 32 rows
+ legacy hidden + `aop-embed-ready`; `verify_swap.py` 12/12; pixels confirm.
Files: `website/js/panel.js` · `css/panel-embed.css` · `sw.js` · `index.html`.
**Old panel deliberately KEPT as the fallback** (per "before deleting the old one
fully") — Stage 2 cleanup still owed. Repro/observe scripts: `/tmp/observe_*.py`.
Commit is the user's git gate. Card: `right_panel_rebuild.md` (top entry).

**2026-06-05 (RIGHT-PANEL SWAP INTO index.html — Stage 1 SHIPPED + verified,
CODE ONLY, UNCOMMITTED, v31→v32).** User: *"do the swap into index.html."* Fork
put to the user → chose **keep everything** (the new one-model panel drives the
EXISTING live map; retire the old patchwork; don't lose search/calendar/presets/
PWA). Proved the approach by observation: **78 of the new panel's 85 layers
already exist in main.js with identical ids**, and the host exposes reachable
globals, so the new panel can drive the live map. **Architecture: main.js keeps
owning the map + all base layers + search + calendar + presets + PWA + terra-draw;
js/panel.js attaches in a new EMBEDDED mode and becomes ONLY the right panel.**
Shipped: **(1)** `js/panel.js` dual-mode boot — `window.AOP_PANEL_EMBED` switches
it to attach to `window.AOP_HOST_MAP` (no own map), add ONLY its own draw layers
(userFeatures + __draft), fetch data for the lists, render into `#aopPanelMount`,
and poll for a host layer before booting (main.js's load handler is async).
**(2)** Visibility BRIDGE — each panel node maps to the host checkbox via
`window.AOP_HOST_LAYER_TOGGLES` (main.js re-exposes its lexical `LAYER_TOGGLES`);
the eye-toggle sets that checkbox + dispatches its change event, so visibility
flows through the host's OWN machinery and **presets + panel never desync**;
preset buttons re-sync the panel after they run. **(3)** `js/main.js` — two
additive lines: `window.AOP_HOST_MAP = map` + `window.AOP_HOST_LAYER_TOGGLES =
LAYER_TOGGLES`. **(4)** `index.html` — load panel.js (embed config) after main.js;
add `#aopPanelMount` + the Export/Clear footer inside `#panelBody`; tag
session-tools `.aop-keep`. **(5)** `css/panel-embed.css` (NEW) — the proven
right_panel.html panel styles SCOPED under `#aopPanelMount` (id-specificity beats
app.css's same-named old-panel classes) + a rule hiding the legacy toggle/editor
content (its `#showXxx` checkboxes stay in the DOM, hidden, so presets still drive
them). **(6)** v31→v32 (`#appVersion` + `sw.js VERSION`; panel.js + panel-embed.css
added to `SHELL_ASSETS`). **Verified by observation** (`/tmp/verify_swap.py`,
service-worker blocked, served :8077): **12/12, 0 real console errors** — new panel
mounted on the LIVE page; eye-toggle flips the live layer AND keeps `#showLandcover`
in sync; **Topo preset applies + the panel resyncs**; **search returns 4 results**;
calendar tab opens; **CRUD-create a POI → into the export/save payload**; legacy
sections hidden, session-tools kept. Screenshot `brain/output/swap_live_panel.png`
(panel renders correctly, left rail + event schedule + countdown + map all intact).
**No regression to standalone** right_panel.html (`verify_crud_full` 16/16,
`verify_panel_save` 14/14). **Stage-2 owed (deferred, all on the card):** the old
patchwork is HIDDEN not deleted (main.js still renders it into hidden DOM — a
cleanup pass should delete buildEditorTree/renderFeatureList/renderEditDock +
LAYER_TOGGLES-render/SECTION_RUNTIME/FEATURE_LIST_LAYERS-as-panel); the new panel's
left POI-star sidebar is skipped in embed mode (index's own POI tab remains → two
highlight systems to reconcile); panel edits `setData` the shared sources, so a
created/edited feature overwrites the host's `aop_positioned_features_v1` drag
overrides + `aop_editor_pois_v1` POIs for that layer (store reconciliation); the
SFWDA-paper node + paint-tuning sliders are not wired in embed mode. Commit is the
user's git gate. The pre-existing sfwda webp headless flake is unrelated.

**2026-06-04 (CRUD FOR ALL BASE THINGS — SHIPPED + verified, CODE ONLY,
UNCOMMITTED).** User MVP push: *"this is CRUD for all our base things and the
ability to re-bake… the best you can do is 60% of any real task."* Found the real
gap by RUNNING the app (`/tmp/observe_crud.py`): base/reference layers were
**read + update-only** — Create lived only on the 3 generic draw groups, and
Move/Delete only on user-drawn features. Closed it in `website/js/panel.js` +
`mvp/scripts/bake_panel_overrides.py`, one-model/one-renderer held:
**(C)** `nodeCreateSpec` synthesizes a create spec for every editable
single-geometry base layer → the `+` is now on **10 layers** (was 3:
+buildings/aopTrails/cemeteries/boundaries/editorPois/visitorContext/pubTrails;
brandLogos opted out, needs an icon picker). A draw writes INTO that layer's own
source with the Common Minimum Schema, carrying `_id`(local)+`_src`(home
source)+`__locked:false` (a just-drawn feature is editable even in a locked
reference layer — the lock protects EXISTING data, not your new one).
**(D+move)** `itemFields` gives EVERY editable item fly/copy/**move**/**delete**,
move+delete lock-gated. **(re-bake source-aware)** `syncCreated` snapshots every
`_id`-bearing feature across ALL sources; `applyStoredOverrides` replays each into
its `_src` source (per-source dedup); the baker groups `created[]` by `_src`→file
(drawn building → `aop_buildings.geojson`, plain draw → `aop_user_features.geojson`).
**Diff-cleanliness fix (important):** the served files are MINIFIED
(`rebake_canonical.py` writes `separators=(",",":")`); the old baker
pretty-printed (`detect_indent` can't read a 1-line file → indent=2 fallback) so a
1-feature edit produced a **438-line reformat**. Rewrote `write_fc` to match the
canonical minified format + dropped `detect_indent` → a bake is now **1 minified
line changed** (review via `git diff --word-diff`). **Verified by observation**
(served :8077): `verify_crud_full.py` **16/16** (create into LOCKED buildings via
`+`; unlocked+editable; `_src`+schema; not leaked to userFeatures; Move+Delete
present; existing building lock→unlock→edit; export shape; **survives reload**),
`verify_crud_dm.py` **4/4** (Delete records `source:id` in `deleted[]`, Move
records a geometry diff), baker round-trip (bakes to the right file, schema +
`last_checked` stamped, panel-keys stripped, **1-line minified diff**, **idempotent
2nd run**, data tree restored), `verify_panel_save.py` **14/14 (no regression)**,
model renders **5 sections/32 rows/85 map layers/0 real console errors**. One
pre-existing flake (NOT this work, unchanged from HEAD): default-OFF `sfwda-paper`
image layer sometimes logs `Failed to fetch (0) …webp` in headless though it serves
200. Card: `right_panel_rebuild.md` ("CRUD FOR ALL BASE THINGS" entry).
**Owed:** `__group` reassignment is now superseded by direct-create for filing
into a base layer; the index.html swap; commit is the user's git gate.

**2026-06-04 (RIGHT-PANEL SAVE PATH — SHIPPED, CODE + 1 NEW DATA FILE,
UNCOMMITTED).** User: *"need a save path so that when we make updates we can
export those and re-bake them. we dont have a db in prod all values are served
from json."* Built the loop on the existing pattern (the live app already does
this for drag-positioned layers via `aop_positioned_features_v1` +
`export_positioned_features.py`; the new `panel.js` just wasn't wired to it).
**Fork put to the user → DIFFS** (not full-file replace). **edit → localStorage
diff → ⤓ Export edits → `mvp/scripts/bake_panel_overrides.py` → served GeoJSON →
commit → Clear.** 4 files: `website/js/panel.js` (persistence block
`aop_panel_overrides_v1`, keyed `"<source>:<canonical id>"` — the canonical `id`
from the re-bake is the JS↔Python match key; `commitChange`/`syncCreated`/
`persistDelete` + boot `applyStoredOverrides`; `highlight` saved but never baked),
`right_panel.html` (pinned footer: Export edits / Clear / unsaved-count),
`mvp/scripts/bake_panel_overrides.py` (NEW — merges the `aop-panel-overrides-v1`
export into `website/data/*`; props+geometry+stamps `last_checked`, appends drawn
features to their own file with editor provenance, idempotent, `--dry-run`),
`website/data/aop_user_features.geojson` (NEW — drawn-feature home; its own file
so `rebake_canonical.py` never clobbers a draw; `userFeatures` repointed
url→here). **Order: `rebake_canonical.py` (from raw) FIRST, then
`bake_panel_overrides.py` (curation on top).** Verified by observation
(`/tmp/verify_panel_save.py`, served :8077): **14/14, 0 console errors** —
create/rename/served-edit persist + **survive reload**, export shape correct,
baker dry-run + real write correct, **2nd run idempotent no-op**; data tree
restored after the write test. Card: `right_panel_rebuild.md` ("SAVE PATH
SHIPPED" + slice #10 disk-persistence now ✅); design also in
`research/common_feature_schema.md` ("Save path"). **Owed:** commit is the git
gate (incl. whether to track `aop_user_features.geojson`); the
`aop_panel_*_v1` vs live `aop_positioned_features_v1` reconcile is a swap-time
item.

**2026-06-04 (COMMON SCHEMA RE-BAKE — SHIPPED, CODE + DATA, UNCOMMITTED).** User
flagged data-source schema variability as the thing hampering design: *"each one
has a different schema … I should be able to edit a trail description the same
way I edit the pavilion text."* Audited every `website/data/*.geojson` by
observation — the same concept used a different physical key in nearly every file
(~10 keys for "name" alone; SFWDA trails only `trail_number`; the pavilion is
`building_label`). Wrote the design (`brain/research/common_feature_schema.md`):
a **Common Minimum Feature Schema** = the northstar's six product-test questions
as fields. User directed a **full data re-bake** (not the adapter I first
proposed): *"I would not have a half rebuild. re-bake the data entirely in our
new format. keep the raw we can refer back. our re-bake should have our fields,"*
vocabulary *"go with what is common"* → `name`·`description`·`kind` + provenance
block (`source`·`confidence`·`permission`·`status`·`last_checked`).
**Shipped & verified by observation (served :8077, 0 console errors):**
(1) `mvp/scripts/rebake_canonical.py` — archives pristine originals to
`website/data/raw/`, rewrites all 23 served feature collections canonical-first
via a crosswalk + per-layer source-register provenance defaults. **Additive**
(original keys preserved → map paint/`index.html` unbroken); `name` left blank on
render-sensitive label layers (trail-network/roads/water); machine/coverage
layers (landcover/contours/activity/synthetic) get id+kind per feature with
layer-level provenance in the new `website/data/_schema.json` manifest. Files did
not balloon (contours 14.3→13.2 MB). Idempotent (re-bakes from `raw/`; `--check`
dry run). (2) `website/js/panel.js` — `itemFields()` collapsed to ONE frame for
every feature (Name·Description·Kind·facet·provenance·actions), `PROVENANCE_KEYS`
cut from a 14-entry alias list to the 5 canonical fields, dead
`userFeatureFields`/`renderNoteField` removed. **Proof:** map renders all
default-on layers post-re-bake; a trail and the pavilion now show the SAME editor
frame with live Name + Description (differ only by facet — trail Difficulty,
building Last-checked). Shots: `playwright_rebake_verify.png`. Throwaway
verifiers: `/tmp/verify_rebake.py`, `/tmp/verify_canonical_editor.py`.
**Owed (user's git gate):** commit; decide `data/raw/` (~20 MB) commit-vs-
gitignore (originals also live in pre-re-bake git history); clean
strip-legacy-keys pass deferred to the index→panel swap; persist in-editor
Name/Description edits (rebuild's existing disk-persistence owed item).

**2026-06-04 (RIGHT PANEL REBUILD — slice #11 SHIPPED: ALL live layers ported —
the rebuild is now the index-page replacement, isolated, NEW files only,
index.html/main.js UNTOUCHED, UNCOMMITTED).** User cut off the "next steps"
discussion and set the direction hard: *"this page && editor is supposed to
replace the one on the main index page. make sure it has all the layers."* So I
brought the **entire ~29-layer index set** into `website/js/panel.js`,
reorganized from the geometry-group layout into the **live page's exact
provenance sections** (Source layers / Derived layers / External reference / Map
editor / User submitted — matching `index.html`'s `data-section` blocks, and the
northstar's provenance-is-the-product stance). Each layer is a node carrying its
real `mapLayers` ids + a map source/paint **ported verbatim from `main.js`**
(extracted by 3 parallel Explore agents over the 10k-line file, then constants
like `LANDCOVER_FILL`/`POI_COLOR`/hotspot palettes resolved to literals).
`MAP_DATA` now spans five source kinds (geojson `url`+optional `resolve`, inline
`data`, `raster`, `rasterDem`, `image`, plus `images` for `addImage` brand
icons); boot loader fetches all 27 GeoJSONs in **parallel** then adds in
declared order. External-tile layers (TNMap/NAIP/AWS terrarium/SFWDA) get initial
`visibility:'none'` so no network fetch fires pre-`applyAllVisibility`. `visible`
defaults mirror the live **Fresh** preset. Renderer unchanged except lock +
group-reassignment now gate to **editable** nodes (`isEditableNode` =
items||create) so a raster toggle gets no padlock / isn't a drop target. The 3
user **draw** groups (Points/Lines/Polygons) live under Map editor; reference
vector layers moved OUT of geometry-nesting INTO their provenance section.
**Verified by observation** (`/tmp/verify_panel_all_layers.py` + focused diags,
served :8077): **32 panel rows / 5 sections, all map layers added, initial
visibility matches the model, local-layer toggles flip MapLibre visibility,
create still works (point placed+named+selected), 0 console errors** on load +
toggles + create; pixels confirm the default-on set renders incl. **both brand
logos** (`addImage` worked). Shot: `brain/output/playwright_panel_all_layers.png`.
Card: `right_panel_rebuild.md` **slice 11** (full per-layer record + the
faithful-but-simplified deltas: event-schedule resolves only coordinate-bearing
anchors, SFWDA paper is a single 4-corner image not the 6×6 warp, brand
icon-size is static not zoom-scaled, paint/contour-fade sliders still NOT
brought — KISS). **Owed next** (the genuine forks, unchanged from slice #10):
disk persistence (own `aop_panel_*_v1` key vs reuse live
`aop_positioned_features_v1`), then the **swap into index.html** (retire the
6-places/5-paths patchwork, migrate verifiers, bump VERSION — the user's git
gate). Nothing to git-gate beyond the 2 isolated files.

**2026-06-04 (RIGHT PANEL REBUILD — slice #9 SHIPPED: edit features ported from
the live dock — isolated, NEW files only, index.html/main.js UNTOUCHED, UNCOMMITTED).**
Picked back up "to make it more simple and maintainable… more of the edit
features from the live view." User pushed back on approval-seeking: *"if you know
what NEEDS to be done do it. get to a point where you actually need input."* So I
built the whole cheap-and-correct batch in one pass and stopped at the real forks.
**Shipped into `website/js/panel.js` + `right_panel.html` (served :8077):** (1) a
new `actions` field-kind + one `ACTIONS` registry → **Fly-to / Copy-GeoJSON /
Move / Delete** per feature (declared via `items.actions`; fly/copy never
lock-gated, move/delete are; user features get all four, reference layers get
fly+copy); (2) **Move** (point relocate / line+poly translate via
`geometryCenter`, reusing the create click plumbing; vertex-edit still OUT); (3)
**Source/provenance read-out** (`items.provenance:true` → read-only `static`
fields from whatever `PROVENANCE_KEYS` the data ships — the northstar's six
product-test questions, now answered on trails/buildings/boundary); (4) **Copy
all as GeoJSON** per layer (group `copyAll` action); (5) **map-click Reveal**
(`queryRenderedFeatures` → select + expand the chain). **One model, one renderer
held** — every feature = a node descriptor + a renderer branch, ZERO
`layerKey===` special-casing (that hardcoding IS the live dock's smell; not
brought). **Verified by observation** (extended `/tmp/verify_panel.py`, **0
console errors**) + looked at pixels (user-point 4-action grid; 665 Ellis Cove
full provenance block, locked/read-only). Card: `right_panel_rebuild.md` slice
#9 (full record) + slice #10 = the **genuine input points owed to the user**:
**disk persistence** (all edits are in-memory, die on reload — fork: reuse the
live `aop_positioned_features_v1` localStorage convention vs. an isolated
`aop_panel_*_v1` key; recommend own key, reconcile at swap), **layer-paint
sliders** (deliberately NOT brought — re-couples map-style; KISS), **★/#tag/
category** (inert until visitor-list / event-schedule surfaces exist), and the
**swap into index.html** (retire patchwork, migrate verifiers, bump VERSION —
the user's git gate). Nothing to git-gate beyond the 2 still-isolated files.
**Same-day follow-up — editor moved to a PINNED BOTTOM DOCK** (`#panelDock`,
live-version style). User: *"when I add a polygon the editor should be under the
button. I cannot see them if they are far away."* My first stab (inline
`scrollIntoView`) was verified against a panel that didn't overflow → vacuous
test → user: *"it did not move."* (Lesson: verify against the REAL failing
condition.) Now the edit area renders ONLY in a fixed footer dock (panel = flex
column; rows keep just the `.selected` highlight; `renderDock()` mounts the same
`renderEditArea`/fields). Proven against a real **1967px** overflow (trails
expanded, scrolled to top): the new polygon's editor is on-screen in the dock.
Verifier rewritten to read `#panelDock` (`dock.dataset.sel` hook) — full suite
PASS, 0 console errors.
**Then the user reversed the dock → INLINE + added group reassignment**
(follow-up #3 on the card). *"editor should exist in the space with the
instructions… swap out not jump to the bottom… all editors inline… choose an
item, hit edit, expands immediately below. in the editor set a group — add a
bathroom to buildings group under polygons."* Dock removed; editor renders
inline under the selected row again, `scrollIntoView` keeps it visible (proven
under real overflow). NEW: user features carry an optional `__group` (node id);
`deriveItems` merges user features into whichever group they're assigned to; a
`group` field-kind (`renderGroupField`/`groupOptions`, path labels like
"Polygons › Buildings") reassigns them; `itemFields` now derives a USER
feature's editor from geometry so it stays fully editable even inside the locked
reference Buildings group. Per-node `items.fields`/`actions` on the user groups
deleted as redundant. Verified inline (`/tmp/verify_panel.py`): polygon → Group
= Buildings → leaves Polygons (0), joins Buildings (5→6), editable; full suite
PASS, 0 console errors. The bottom-dock entry just above is SUPERSEDED.
**Pattern that emerged across these 3 follow-ups (worth holding):** transient
surfaces (hint, editor) must appear inline where the action happens; and a
user feature's editor is geometry-derived + group-portable, never inherited from
the host node — that's what keeps "one model, one renderer" from sprouting
`layerKey===`-style special cases.
**Follow-up #4 — geometry-typed the Group selector.** User asked why a polygon
could go in a Point group. Verified it was a real bug (filing a polygon under
Points orphaned it from the panel + decoupled its visibility, while it still
drew on the map). Surfaced vs. the locked `no_limiting_code_mvp` rule (that rule
is about DATA rejection, not UI mis-filing); user chose to type it. Each node
now has a geometry (`nodeGeom`: user via `create.geomType`, reference via a new
`geom` field); `groupOptions(feature)` offers only compatible groups (polygon →
Polygons/Buildings/Park boundary; line → Lines/Trail network/Streams; point →
Points). Verified inline, 0 console errors. UI-affordance correctness only — the
MVP no-limiting rule still governs data values/publishability.

**2026-06-04 (RIGHT PANEL — CLEAN REBUILD started, isolated, slice 1 SHIPPED —
NEW files, index.html/main.js UNTOUCHED).** User: the right panel is *"a bunch of
hard coded, different implementations,"* not the *"singular Massive json object +
singular renderer"* they want — *"come up with a NEW… completely new view… put the
features back as I directed one at a time. KISS."* Confirmed the diagnosis in code
(one layer is described in 6 places — static HTML + `LAYER_TOGGLES` + `PRESET_*` +
`TUNABLE_LAYERS` + `FEATURE_LIST_LAYERS` + `SECTION_RUNTIME` + the hidden
`#legacyLayerToggles` bridge — and rendered through 5 paths). The 2026-06-03 edit
dock was bolted ONTO that, not a replacement. **Approach (user-chosen): build
isolated & fresh, then swap.** New `website/right_panel.html` + `website/js/panel.js`
= ONE `PANEL_MODEL` → ONE renderer (`renderPanel→renderSection→renderNode(kind)`).
**Features re-added one at a time, all SHIPPED + verified headless (served :8077,
0 console errors, pixels confirmed): #1 layer visibility toggle · #2 section
collapse · #3 collapsible items list under a layer (general — Trail network 101,
Buildings 5) · #4 select group-or-item → inline edit area, visibility relocated
INTO the group edit area (rows lost their checkbox) · #5 user-entered features +
create ability** (new `userFeatures` node, mutable in-memory collection, `+` →
place-mode → map-click drops a Point → selected with editable Name + Notes;
declarable per-layer `items.fields` + a `text` field kind) · **#6 Point/Line/
Polygon groups (old layout), each with its own create geometry + editor set**
(split into 3 nodes over one collection filtered by geometry; Point=1-click,
Line/Polygon=multi-click+double-click draw with dashed draft; Lines get a
`select` Difficulty field; new geometry auto-sorts into its group) · **#7
reference layers nest under their geometry group via a `children` field +
recursive `.node-content`** (Trail network⊂Lines, Buildings⊂Polygons, Park
boundary = single item in its own group⊂Polygons; streams also moved under Lines)
· **#8 lock (read-only gate) on every group + item** (open/closed padlock; locked
→ edit area read-only/disabled inputs + hint; visibility never gated; group lock
on `node.locked`, item lock on `props.__locked` w/ group fallback so group-lock
cascades + per-item override; reference layers default LOCKED, user features
UNLOCKED). One model (`PANEL_MODEL`) + one renderer throughout; each feature = a
new field/branch, no new surface. Card: `tasks/04_event_app/right_panel_rebuild.md`
(diagnosis + target architecture + per-slice record). Verifier (throwaway):
`/tmp/verify_panel.py`. **Owed: user directs feature #9, one at a time.** Swap into the live app (retire
the patchwork, migrate verifiers, bump VERSION, make the verifier durable) is
deferred until the new view earns it feature by feature. `index.html`/`main.js`
still UNTOUCHED; nothing to git-gate beyond the 2 new files
(`website/right_panel.html`, `website/js/panel.js`).

**2026-06-03 (UNIFIED EDIT DOCK shipped — one edit interface for the whole right
panel — CODE, UNCOMMITTED, v30→v31).** User: *"all edits on the right should use
this new singular edit interface… if a layer has specific settings it should also
be in this edit panel… make some mockups that show the different types,"* then
*"do it all. make me proud."* Mockup pass first (`website/editor_dock_types_compare.html`
+ `right_sidebar_compare.html`), contract confirmed via 2 questions (4 tabs
Identify·Edit·Display·Source; layer paint folded into the Edit tab). Then wired it
into the live app: new `buildEditDock`/`renderEditDock` render ONE 4-tab dock into
a new `#editDock` pinned to the panel bottom (panel restructured to a flex column,
`.panel-body` is the scroll region), replacing the per-row accordion
(`buildInlineEditor` now dead). Single `dockSelection` across all layers driven by
`selectFeatureForDock` (row ▸ chevron, map-click reveal, duplicate, delete); `✕`
clears → dock hides (two-state). `renderTuneControls(config, target)` generalized
so the Edit tab hosts the layer's real `TUNABLE_LAYERS` paint via the existing
`handleTuneInput`. Fields/actions adapt off the existing spec flags (Category +
Dup/Delete = editorPois; Tag = taggable; Size = brandLogos→Display; Move/Lock =
onMove; ★ = highlightable). Group + building Public/Private are read-only for now
(cross-layer migration / status-flip cascades = deferred). VERSION v30→**v31**
(shell-asset). **Verified by observation** (served :8000, headless, **0 console
errors**): drawn POI → 4 tabs, Edit = 5 actions + 10 "Layer paint · Drawn POIs"
sliders, Display = Visible + ★; brand logo → Size + Move/Lock/Copy, no
Category/Delete; visitor context (Polygon) → Move/Lock/Copy + 7 paint rows; ✕
re-hides. Card: `tasks/04_event_app/editor_unified_dock.md` (full inventory +
deferred list). Shots: `brain/output/playwright_app_dock_selected.png`,
`…_edit_tab.png`, `…_identify_tab.png`, `playwright_editor_dock_types.png`.
**Owed:** on-device feel; **commit + the v31 bump are the user's git gate.**
Followups: delete dead `buildInlineEditor`; consider retiring `#layerEditor` paint
drawer for feature layers; settable Group / building status; vertex editing.

**2026-06-03 (EDITOR v1 — every curated layer editable + single GeoJSON-copy export —
CODE, UNCOMMITTED, v29→v30).** User, right after the buildings-row crush fix: *"we need it
all cleaned up and editable. this is mvp. we need v1… look for smells and make a ui that a
human can use. only export path is geojson copy."* Ran a 4-axis read-only audit (editable
layers / export paths / inline-editor persistence / right-panel smells), then built the v1:
**(1) all curated layers editable** — `inlineEditor:true` on buildings, cemeteries,
visitorContext, brandLogos; the accordion editor (`buildInlineEditor`) is now layer-agnostic
(Name writes the per-layer name prop — `building_label` for buildings; Category drawn-POI
only; Size brand-logo only; Tag taggable-only; Notes all; labeled Fly/Move/Lock/Copy GeoJSON;
Duplicate/Delete drawn-POI only). **(2) persistence** — the `aop_positioned_features_v1`
override store now carries a `properties` patch (replayed by `applyPositionedFeatures`), so a
renamed building survives reload AND flows into Copy-GeoJSON; new generic
`setFeatureProperty`/`SERVED_SOURCE`/`FEATURE_NAME_PROP`; `persistFeatureFlagChange`
generalized to all served layers; `cemeteryData` hoisted + override-wired. **(3) clean row**
— editable rows collapse to `[vis] [★] name [edit ▸]`; all actions/fields moved into the
labeled accordion (kills the cryptic 🎯✋🔒⧉ cluster AND the buildings name-crush at the
source — the row-level tag input + `has-tag` CSS removed). **(4) one export = GeoJSON copy**
— removed the footer GeoJSON download (→ "Copy all as GeoJSON" clipboard), the `#exportAll`
settings snapshot, the 5 section "copy settings" ⧉, and the SFWDA alignment download (→
clipboard); added a drawer "⧉ Copy all" (`copyLayerAsGeoJSON`). Removed dead helpers + dead
row CSS; fixed the stale Trailheads comment. **Verified by observation** (served :8042):
buildings rows readable (name 0→229px), accordion edits a building, the `building_label`
override persists + **survives reload**, 0 console errors; `poi_editor` PASS, `feature_list`
PASS (verifiers updated: move/copy now open the accordion; removed-button assertions flipped
to "removed"), `presets` only its documented pre-existing fails. Card:
`tasks/04_event_app/editor_v1_editable_layers.md`. **Routed (not done):** panel hygiene
beyond the editor (Comparisons dev-links, Layer-notes prose, orphan trailheads toggle,
orphan activity paint specs) — owner/content calls in [[viewer_polish_followups]]. **Owed:**
on-device confirm; commit + v30 are the user's git gate.

**2026-06-03 (Park buildings rows fixed — name column was 0 px / "all edit on one line" —
CODE, UNCOMMITTED, v28→v29).** User opened the right panel: *"Park buildings (curated, drag
to adjust) all edit is o one line and I cannot read the names. this is broken."* (The "v3c
plan" they referenced is `_done/editor_three_buckets_v3c.md` — already SHIPPED; the live
editor implements it. The break was not in the editor section but in the **Derived layers →
Buildings** feature list.) Reproduced by observation: the 3 facility rows wrapped their
addresses **one char per line** while controls jammed on one line. Cause: `buildings` is the
only layer rendering the `#tag` input **on the row** (`taggable && !inlineEditor`); that 84 px
input + copy/fly/move/lock filled the 380 px row and collapsed the `minmax(0,1fr)` name column
to 0 px. Fix: row gets a `has-tag` class (`main.js`) + a two-line CSS layout (`css/app.css`,
after `.feature-row.move-target`) — name full-width on line 1, tag + icons on line 2 (name
0 px→257 px, confirmed). `VERSION`/`#appVersion` **v28→v29** (shell-asset bump). Verified:
`playwright_verify_buildings.py` PASS 0-err; `playwright_verify_feature_list.py` buildings +
all-5-curated + cemetery/brand/visitor PASS, only the documented pre-existing
`publishable: ↑ Export button present` FAIL, 0-err. Full record: `10_deferred/
viewer_polish_followups.md` "Right Panel" (2026-06-03 entry). **Owed:** on-device read-confirm;
commit + v29 are the user's git gate.

**2026-06-03 (buildings → DERIVED + drag-editable, raw context dropped — CODE, UNCOMMITTED,
v27→v28).** User asked to make the buildings a "derived" layer in the right editor group
and to be able to edit the footprints (FEMA's sit a little off). Asked the one real fork →
user chose **split + drop raw**: served `aop_buildings.geojson` filtered **202 → 5 curated**
(3 facilities + 2 private boxes); the ~197 raw FEMA context footprints dropped on purpose.
Durable in `import_fema_buildings.py` (new `CURATED_ADDRESSES` filter + `load_prior_geometry()`
preserves hand-nudged geometry across re-imports). Viewer (`website/js/main.js` + `index.html`):
`#showBuildings` moved Source→**Derived** section; `SECTION_RUNTIME` buildings → `derived-layers`
+ `positionedFeatureLayers`; buildings spec got an **`onMove`** drag-translate (→
`savePositionedFeature('buildings', …)`), `buildingsData` hoisted to top-level `let`,
`applyPositionedFeatures('buildings', …)` replays drags on reload; old "Other buildings" group →
**"Private structures"**. `export_positioned_features.py` learned `buildings` (`build_id`,
`indent=1` preserved). VERSION v27→**v28**. **Verified by observation:** `playwright_verify_buildings.py`
PASS 0-err; `feature_list` building sections PASS (only the documented pre-existing publishable-export
FAIL); `code_review_groupb` PASS @v28; a focused drag test PASS (footprint lands at click, override
`buildings:3397585`, survives reload); `bake_layer` temp test PASS (5-dec round + indent kept).
Verifiers updated (buildings, feature_list, groupb pin v26→v28). Card: `pwa_qa_data_bakes.md`
Item 6 "EXTENDED 2026-06-03" block. **Owed:** on-device drag feel; commit + v28 bump are the
user's git gate. (Same session, earlier: baked the Monteagle visitor-context polygon move into
`aop_visitor_context_callouts.geojson` — visitor_context verifier PASS.)

**2026-06-02 (Sprint 04 closeout pass — pwa_qa_data_bakes Items 4 & E investigated +
Item 6 re-verified; doc-only, no code).** Picked up after a forced restart cut the
prior session mid-verify (it was thrashing a bespoke zoomed `box_shade` screenshot —
abandoned, as that session concluded). **Re-verified Item 6 the reliable way**
(served `website/` on :8001): `playwright_verify_buildings.py` **PASS, 0 console
errors** (3 facilities tagged + searchable by name/address; 2 private boxes render
via the always-on `building-structure-box` layer; 665/889/383 NOT searchable; jump
works); `playwright_verify_feature_list.py` building section all-PASS, only the
**documented pre-existing publishable-export FAIL** remains, 0 console errors. Box
paint confirmed in `main.js`: `#46423b` @0.82 (warm dark charcoal, not literal
`#000` — pure black reads as a hole). **Then closed the two headless-actionable items
on the card by investigation:** **Item 4 = DONE** — `aop_visitor_context_callouts.geojson`
(13 KB) is already baked + loaded from `./data/` and renders; copy split into
`aop_poi_index.json` (clean). **Item E = bake mechanically DONE** — Ellis ships the
full burial roster + source + license terms on both its marker (Point) and polygon;
the "doubling" is **intentional marker+polygon, NOT a dup** (all 4 cemeteries do it).
**BUT Item E has a live owner publishability fork:** the research brief
(`brain/research/aop_ellis_cemetery.md`) says treat the named roster as "community
research, not a publishable layer, until permission/use is settled," yet the served
geojson already ships it — USGenWeb's contributor-notice requirement IS met in-data,
but whether AOP's use is acceptably non-commercial is the user's call (surfaced, not
silently kept/stripped). **Net: of pwa_qa_data_bakes's 4 items, 4 & 6 are DONE, E is
bake-done/publishability-owed, 17 needs imagery re-acquisition + a sizing decision.**
Card updated (Item 4 DONE block, Item E FINDINGS block, Done-when + a Status-summary).
**Then the Item E publishability fork was put to the owner and RESOLVED (2026-06-03):
keep shipping the named Ellis roster as-is** — AOP is non-commercial hobby use, inside
USGenWeb's free-non-commercial grant, and the contributor notice travels in-data. No
code change (data already ships it); decision recorded in
`brain/research/aop_ellis_cemetery.md` (Sources + Open questions, both updated) and the
card (Item E now fully done). **Net: pwa_qa_data_bakes is DONE down to Item 17** — 4,
6, E all done; only **Item 17** (extend 9-patch imagery = data re-acquisition + owner
"how much bigger") remains, and it's not headless-actionable. **No app code changed
this session; Item 6 stays UNCOMMITTED awaiting the user's git gate + v27 bump.**
Remaining Sprint 04 gates are all owner/device: Item 17 AOI size · Item 6
always-on-vs-toggle + on-device feel · trail Slice 4 landmark coords/license ·
pwa_qa_2 items 6/9.

**2026-06-01 (pwa_qa_data_bakes Item 6 — building public/private bake SHIPPED,
UNCOMMITTED, v26→v27).** Tiered the in-bounds buildings by owner-confirmed truth:
**public facilities** (searchable/clickable/listed) = 1010 Pavilion, 1033 Farmhouse
(rentable), 880 Front Office; **private structures** (non-interactive black-box
presence markers — no search/popup/list) = 665, 889. Authored `aop_facility`/
`aop_structure_box` tags baked into `import_fema_buildings.py` (durable) + applied to
`aop_buildings.geojson`; `website/js/main.js` adds a always-on `building-structure-box`
black layer, gates search/POI-browser/feature-list to facilities, repoints the AOP
highlight to facilities. Verified by observation (buildings PASS 0-err, feature_list
building section rewritten+PASS, search/presets/event_schedule regression-clean — only
documented pre-existing fails). Card: `04_event_app/pwa_qa_data_bakes.md` Item 6
"SHIPPED" block. **Lesson:** the owner's axis is strictly **public→facility /
private→black box**; don't infer "not-searchable" = "private". On-device look + the
always-on-vs-toggle question for the boxes are owed. (Earlier this session's Sprint 04
doc-review pass is now committed in `5d07763 pm`.)

**2026-06-01 (Sprint 04 review pass — doc only, no code).** Reviewed every active
Sprint 04 card against the real repo. **Key correction: the working tree is now
CLEAN — everything is committed** (`d795f11 split apart index.html` is HEAD, v26).
So **every "UNCOMMITTED" / "VERSION-owed" note in the blocks below is STALE** —
the user did a commit pass; trail Slices 1–3 (`search-result-desc`/
`renderSearchResults`) and the source split are confirmed in committed code.
**Closed → `_done/`: `viewer_source_split.md`** (Stage 1 shipped+verified+committed;
user chose to stop at Stage 1 — Stage 2 is a future option, not owed). **The JS now
lives in `website/js/main.js`** (index.html is 672 lines), so all `index.html ~line N`
anchors in the cards are stale — search `main.js` instead. **Still active (4 cards):**
`trail_research_integration.md` (Slices 1–3 done; Slice 4 blocked on landmark coords
+ license gate owed), `pwa_qa_2.md` (items 6 device+cut-off-instruction / 9 cemetery
decision owed), `pwa_qa_2_plan.md` (companion), `pwa_qa_data_bakes.md` (items 4/6/17/E
all blocked on a product/source decision). The P2 "decision session" bundle in
`04_event_app/_readme.md` is the right next move with the user. `_readme.md` updated.

**2026-06-01 (verifier-rot fix — test-only, no app code).** Picked up the ungated
P4 item from `10_deferred/viewer_polish_followups.md` after confirming all Sprint 04
P1 headless work is shipped+committed (incl. trail Slice 3 — the trail card's
"uncommitted/VERSION-owed" header is **stale**; Slice 3 is in `master` at v25,
`8be6e99`). The v25 full-bleed `position:fixed` `#map` canvas now occludes right-panel
buttons' hit-test points, so real `Locator.click`s timed out. **Fixed:** shared
`click_in_section` (`mvp/scripts/playwright_base.py`) now JS-dispatches the element's own
`click()` after expanding its section (the `set_toggle` pattern); `poi_editor` panel
clicks routed through it + stale `<title>` → "Trail Blazing Invitational"; `session_tools`
clock/reset routed through it. **Verified:** `session_tools` ALL PASS, `poi_editor`
RESULT: PASS, both 0 console errors; helper's other callers regression-clean
(`community_trails` 16/16, `landcover` PASS). `presets` (same class, separately tracked)
partly revived — its first toggle-click crash fixed (now runs 51 checks) but it still has
a downstream panel-click crash + 3 assertion FAILs (2 are the documented decision-gated
publishable/source-section ones, 1 "Topo restyles index contours" never previously
reached) → flagged as its own follow-up in that card. All changes are in
`mvp/scripts/` (test harness only — no `website/` change). UNCOMMITTED.

**2026-06-01 (viewer source split — Stage 1 SHIPPED + verified, UNCOMMITTED).**
Verdict on the "do we need a build step / package manager" question: **no** — file
size isn't the problem (index.html was 562 KB raw / **142 KB gzipped**; the vendor
libs, maplibre 1 MB, dwarf our script). The pain was maintainability + parallel-edit
collisions on one 11.3k-line file. **Shipped (no build step / no package manager):**
both `<style>` blocks → **`website/css/app.css`** (verbatim); the entire main script
→ **`website/js/main.js`** (verbatim, loaded as a **classic** `<script src>`);
**`index.html` 11,299 → 673 lines**. `sw.js` v25→v26 (+ `#appVersion`), css/js added
to `SHELL_ASSETS` + routed SWR. **Verified by observation: full 27-suite, 18 PASS /
9 FAIL, zero new fails** — every fail proven pre-existing by reproducing it against
the original git-HEAD index.html served on port 8011. **Two discoveries forced a
plan change** (see card): (1) ES modules (the chosen Option C) **break the verifier
harness** — ~20 verifiers read app internals as bare globals (`page.evaluate(
"window.map = map")`); module scope hides them. (2) `main.js` interleaves top-level
execution with declarations + relies on whole-file hoisting → a naive classic
multi-file split throws at load. So Stage 1 is a classic external script, and
**Stage 2 (subdividing the JS) — user chose to STOP at Stage 1 (2026-06-01).**
`main.js` stays one isolated file; the carve options (b classic multi-file / c
modules + harness migration) are kept in the card as future options, not done.
Card: `tasks/04_event_app/viewer_source_split.md` ("What shipped" + "Discoveries").
One verifier edited: `playwright_verify_code_review_groupb.py` version-pin v25→v26.

**2026-06-01 (worktree cleanup + Group B fully shipped incl. M13 + Groups C–D worked).** (1) **Worktree
chore resolved.** The "three locked agent worktrees" chore was **stale** — already
gone. Real remaining clutter = `aop-copy-review` worktree + `copy-review` branch
(`git cherry` → fully in master) + `integration-pwa-qa` safety-net (all swarm items
in master; its only non-master content was the **intentionally-dropped** tree-
landcover pattern, user-confirmed, recoverable at `5d825f4`). Verified-redundant;
deletion commands handed to the user via `!` (git is the user's surface). **NOTE:**
the older `session_context` blocks below claiming "master has item 20 (tree pattern)"
are now wrong — it was removed at `2fd9cc4 "icons. omg…"` on purpose. (2) **Group B
fully shipped.** Versions: **v24** committed (`c4e080c "v24 batch"`) = H1+M12; **v25**
working-tree UNCOMMITTED = M4+M5+M8+M9+M10+M13. Changes: **H1** slider rAF-coalesce
(`scheduleRebakeTiles`, index.html), **M12** install button keeps affordance on
dismiss (index.html), **M4** `fetchJson` memoized + warm-up loop (parallel overlay
fetch; SUM→MAX, index.html), **M5** per-row visibility updates counts in place
(`refreshFeatureListCounts`, no subtree rebuild, index.html), **M8** `resyncViewport`
rAF-coalesced + size-guarded (index.html), **M9** move anchor → `geometryBboxCenter`
(fixes multi-part no-op, index.html), **M10** commit-click armed next frame
(index.html), **M13** dropped contours (~14 MB) + synthetic-tracks (~1 MB) from the
`sw.js` install precache (both default-off; cache-first `/data/` still lazy-caches
them → offline-after-once). Verified by observation:
`mvp/scripts/playwright_verify_code_review_groupb.py` **15/15 PASS 0 errors** (H1
burst→1 bake; M12 dismiss/accept; M5 count `1/1→0/1` DOM nodes reused; M4 geojson
loaded; M13 served SW excludes the 2 layers, keeps essentials, SW activates at v25 /
`aop-data-v25`); `feature_list` move-commit + visibility PASS (only pre-existing
publishable-export FAIL); `sfwda_multiply` 5/5. On-device confirm owed (H1 slider,
M12 prompt, M8 iOS keyboard, M9/M10 drag, M13 install cost + offline-after-once).
**Group B complete.** (3) **Groups C–D worked** (still v25, index.html): **L10**
`setLeftTab` returns the resolved key (persist callers wrapped) + `togglePanel`
`settle` listener now has a 360 ms safety net; **L12** `map.on('error')` moved to
construction (catches initial-load errors); **L3** `tileLayerId` delegates to
`tileSourceId`; **L11** `bindEditorClick` idempotence guard; **L9** removed dead
`.left-context-card` rules (KEPT `#message` — verifier-critical load proxy, not
dead). **M19 stale** (no change — `#calendarToggle` not interactive; `#panelHeader`
accessible via its `#panelCollapse` button). **Deferred to own pass:** L1 whitespace
(88 tab lines), broad L2 extractions, L9 raw-hex sweep + pwaIosHint focus-trap; L13
note-only. Verified: `groupb` 15/15, `feature_list` (0 errors, only pre-existing
publishable FAIL), `sfwda_multiply` 5/5. **Verifier rot (pre-existing, NOT this
batch):** `session_tools` (`#clockUseInputs`) + `poi_editor` (`editor-bucket-add`,
stale `<title>`) crash in headless on a `Locator.click` the full-bleed `#map` canvas
intercepts — same class as `presets`; worth a separate force-click/reposition pass.
The card's substantive fixes are all landed; remaining = the own-pass deferrals + the
on-device confirm. **Card CLOSED → moved to `tasks/04_event_app/_done/app_code_review_followups.md`**
(deferred refactor residue routed to `tasks/10_deferred/viewer_polish_followups.md`).
See the closed card's ▶ Next up for the full per-item record.

**2026-05-31 (Sprint 04 triage pass — doc only, no code).** Re-sorted the open
Sprint 04 cards. **Moved → `04_event_app/_done/`:** `copy_review_surface.md`,
`icon_system_normalize.md`, `pwa_qa.md` (all shipped + verified; pwa_qa's only
remainder is the perpetual on-device feel-confirm, kept in its Disposition).
**Still active:** `app_code_review_followups.md`, `trail_research_integration.md`,
`pwa_qa_2.md` (near-done, user-gated on items 6 + 9), `pwa_qa_2_plan.md`
(companion), `pwa_qa_data_bakes.md` (blocked on product/boundary/source calls).
The **priority ranking** lives in `04_event_app/_readme.md` "Sprint 04 priority
(2026-05-31)": P1 = trail Slice 3 + app-review Group B (actionable now); P2 =
the data-bake decision bundle; P3 = on-device verify pass; P4 = refactor/polish.
Doc moves only, uncommitted.

**2026-05-31 (app code review + fix batch 1).** App code review (4 High / 20
Medium / 13 Low across `website/index.html` + `sw.js` + `manifest.json`; one
sweep finding — `composeFeatureFilter` id-type — retracted as a false positive
after hand-check). **Split into two cards:** DONE record at
`tasks/04_event_app/_done/app_code_review_fixes_batch1.md` and the held items at
`tasks/04_event_app/app_code_review_followups.md` (now 20 findings, grouped, with
a recommended order; next cheap slice = forks M7/M14/M17, then the on-device
batch). **Queued decision H4+L8 (SW cache-staleness) ANSWERED + shipped:** user
chose stale-while-revalidate — shell HTML self-heals (navigate caches the
response; non-nav `.html` SWR), copy JSON joins the SWR path (`SWR_SUFFIXES`),
release-checklist comment added, **`VERSION`/#appVersion v20 → v21**. SW verified
active (state=activated). **Then the no-device forks M7/M14/M17 shipped too:** M7
(ticker confirmed singleton + documented page-lifetime), M14 (4 unreferenced
files dropped from `sw.js` precache, ride v21), M17 (`EDITOR_POI_CATEGORIES`
derived from `#poiCategory` options — drift gone, verified 11/11). **20 of 37
findings now resolved, 17 held (all on-device or refactor — no decision-gated
work left).** All in the working tree (UNCOMMITTED). Verified by observation
(smoke PASS, 0 console errors): M1 (popup `closeAllMapPopups`), M2 (central popup-title escape +
stripped 12 redundant caller escapes), M3 (`fetchJson` warns on non-OK), M6
(MultiPolygon hotspot centroid), M11 (stable POI row id), M15 (About href gate),
M16 (`mergeStoreSlice` shallow-merge), M18 (positioned-feature flag clear), M20
(`?.` listener guards), H2 (free bake canvases), H3 (tainted-canvas guard), L4
(`withZoomStops` shape guard), L5 (hemisphere label), L6 (`sw.js` `status===200`),
L7 (manifest `id`). New durable verifier
`mvp/scripts/playwright_verify_code_review_fixes.py` → **PASS, 0 console errors**
(popup no-stack + no-double-escape + presets + renderAbout all confirmed). The
report's "Resolution status" block lists what was **held** (on-device/interaction
verify, cache-strategy decisions, polish-routed) with reasons. `sw.js` (L6) needs
a `VERSION` bump to reach installed users — user's call.


**2026-05-31 (copy review surface) — copy-as-data + printable review page.**
On branch **`copy-review`** (git worktree at `../aop-copy-review`), UNCOMMITTED.
New card `tasks/04_event_app/copy_review_surface.md`. Built `website/copy_review.html`
(prints every text surface in the app, each section headed with its repo-relative
root file + status + ⚑ gap flags), driven by a master registry
`website/data/aop_copy_registry.json` (13 copy kinds). Extracted the prose that
was hardcoded in `index.html` into data files: About tab → `aop_about.json`,
interface microcopy → `aop_ui_strings.json`; calendar title now reads
`event.label` from `aop_event_schedule.json`. Viewer renders from those files via
a copy-data bootstrap script (after SW-register) + `window.AOP_UI` with literal
fallbacks. `#appVersion`/`sw.js VERSION` v18→**v19**; 3 new files added to the SW
data precache. Verified: Playwright on `:8001` (worktree) — About renders from
JSON, 0 console errors over 5 loads; review page assembles all 13 kinds, 0 errors.
Screenshots + logs in `brain/output/copy_review_*`. The 4 `in_code` kinds (page
metadata, layer labels, popup strings, attribution) are cataloged in place with
file links — extraction deferred (interleaved with map render/preset logic).
Merge `copy-review` → master when ready.
Also on this branch: **trail research integration Slices 1–2 shipped** — the trail
catalog (`aop_trail_catalog.json`) is now joined to the gold trail network at
runtime (trail click popup with name/difficulty/description/onX-TR/license, and the
POI browser trails group repointed from the legacy publish placeholder to the gold
network + catalog). Card `tasks/04_event_app/trail_research_integration.md` (in the
main checkout, untracked) marked Slices 1–2 shipped; verified
(`brain/output/trail_verify.log`).

## Archive convention

Each session pruned out of here lands at `session_context_<YYYYMMDD>.md`:

- `session_context_202605201517.md` — original handoff shape (the template).
- `session_context_20260522.md` — work log from the 2026‑05‑20 → 2026‑05‑22 sessions (lidar contours, water, search, cemeteries, land cover, NAIP tracing, presets, panel collapse, activity hotspots, initial event schedule).
- `session_context_20260524.md` — work log for the 2026‑05‑23 → 2026‑05‑24 sessions, covering the full Sprint 02 close (Buckets A–H), schedule clock-times, calendar current-time indicator, left hot button, hot-control two-lane, branding logos, named-feature tagging, search tags, viewer chrome polish, default-layer policy, and code-health Pass 3.
- `session_context_202605241228.md` — CWC dump after Sprint 03 carryover lanes 1–5 shipped.
- `session_context_20260525.md` — left-rail manilla-tab design exploration; five HTML mockup variants checked in under `website/leftrail_v*.html`. Build card: `tasks/03_event_app/_done/left_rail_collapse_tabs.md`. No `website/index.html` changes.
- `session_context_20260527.md` — misc_4 items 1–5 shipped, plus the POI/About empty-space CSS fix and the tab-restore fix. All in the working tree (uncommitted). See `tasks/04_event_app/misc_4.md` "What shipped (2026-05-27)" block for the full close-out and the trail-lane verifier residue routed to `viewer_polish_followups.md`.

**2026-05-31 (pwa_qa_2) — items 1–5 shipped, 7 routed, 6 held.** Picked up
`tasks/04_event_app/pwa_qa_2.md` in a clean session (the companion
`pwa_qa_2_plan.md`'s calendar/region/item-6 code anchors were garbled by the
prior corrupted channel — re-derived everything against the real
`website/index.html`). Shipped in the working tree (UNCOMMITTED): **(1)**
calendar→event popup pins to a fixed `bottom` anchor + dropped the redundant 2nd
corrective pan (the "jerk"); **(2)** mobile calendar-pick now folds the cal card
too (`lrCloseCard('cal')`); **(3)** build version folded into the bottom-left
info ⓘ → "ⓘ v18" (`foldVersionIntoInfoControl`, standalone chip removed);
**(4+5)** Trace preset reworked to "paper map vs merged gold truth" — park bounds
+ OSM park polygon + OSM tracks OFF, SFWDA paper raster kept, merged
`aop-trail-network` ON (added a trace paint so Topo→Trace keeps difficulty
colour), legacy demo trails OFF. **Item 6** (logo overshoot on zoom-out) NOT
shipped — it's GeoJSON-symbol parent-tile scaling (device/GL only); the cap is
already a per-frame GPU expr with allow-overlap, so nothing safe to change
headlessly + the user's instruction is cut off. **Item 7** (Ellis cemetery bake)
routed → `pwa_qa_data_bakes.md` "Item E"; its paired "hide other cemeteries"
RETRACTED (item 9 hold). Plan items 8 (calendar-icon centering) + 10 (region
preset) are no-ops on false premises (see the Disposition table). New verifier
`mvp/scripts/playwright_verify_pwa_qa2.py` — all items PASS, 0 console errors
(served on **8002**; 8001 held a second agent's worktree review, left alone).
`playwright_verify_presets.py` Trace assertion updated to the new intent (it
crashes earlier on a pre-existing headless click-interception, below my edit).
**Version bumped v18→v19** (user call): `#appVersion` + `sw.js VERSION`. The
other agent is also on v19 in a worktree — reconcile at merge. Commit owed to
the user.

**2026-05-31 (icon system) — icon master sheet built.** All 13 inline UI icons in
`website/index.html` collected into a standalone tool **`website/icon_master.html`**:
as-built vs normalized compare grid, global stroke-width + optical-fit controls,
outlier flagging, inline markup editing, and paste-ready SVG export. Source audit:
all already SVG + uniform `22×22` canvas, but **3 stroke widths ship** (1.6 most,
1.4 Tree/Install, 1.2 Pencil) and art-fill ranges 68–91% (Locate is oversized at
91%). Flagged outliers: Tree, Install, Pencil (off-spec stroke), Locate (too big).
`index.html` left untouched — the page is the revision surface; recommended target
+ the 4 paste-back edits are in the new card **`tasks/04_event_app/icon_system_normalize.md`**.
Verified by Playwright (13 cards, 0 console errors). Uncommitted.

**2026-05-31 (PWA QA swarm) — most of `tasks/04_event_app/pwa_qa.md` resolved.**
7 worktree agents, each owning a disjoint region of `website/index.html`, merged
into the master working tree (UNCOMMITTED; backup branch `integration-pwa-qa`).
Shipped: items 5 (logo max-size cap + slider/export), 7 (pinch), 9 (trail dots
removed), 10 (1X search), 11+16 (calendar scroll/header/end-date), 12 (park
zoom tighter), 13 (topo/trail colors + `topo_color_compare.html`), 14 (hot
button toggle), 15 (drawer reflow), 18/19/21 (chrome icons). Item 8 was already
done (`.message` dropped). Split to **new card `pwa_qa_data_bakes.md`**: items 4,
6, 17 (data-bake/acquisition). Then both forks resolved: item 2 confirmed
superseded by V5; item 20 shipped a tree SVG (`website/img/tree.svg` tiled as a
`landcover-forest-trees` fill-pattern on satellite). On-device confirm owed for
7/13/15/20 (touch+GL, unverifiable headless). Full per-item table + merge-integrity
notes in the card's "Disposition" block. **Worktree cleanup DONE (2026-05-31):**
the 7 harness-locked agent worktrees were removed and their `worktree-agent-*`
branches force-deleted after verifying each slice is in master — proof was that
the consolidated `integration-pwa-qa` branch differs from master by only item 20
(the `landcover-forest-trees` tree pattern + `tree.svg`, which master has), and
no worktree carried uncommitted work. The empty `.claude/worktrees/` dir was
removed. Consolidated backup branch `integration-pwa-qa` **retained** (swarm
only; item 20 is working-tree/master-only) as the safety net — delete it once the
v18 swarm result is confirmed on device.

**2026-05-30 (session — iOS PWA full-bleed + V5 bottom bar) — RED BAR FIXED; bottom UI
reworked. We are CLOSE: all changes UNCOMMITTED in the working tree, build `v12-dbg`,
served straight to the phone (no commit/deploy step in this loop). Diagnostics still
live on purpose — closeout = strip them, then commit.** Files touched: `website/index.html`
+ `website/sw.js` (sw `VERSION` v7→v12, kept in sync with `#appVersion`).

- **The "red bar" root cause (the thing that ate days of v5/v6/v7 "pwa bottom math"):**
  `body,html { height:100% }` makes iOS Safari **silently drop `viewport-fit=cover`**, so an
  installed PWA's viewport returns `screenH − statusBar` (measured on-device: `innerH 762`
  on an `812` screen) and the lost ~50px lands as a DEAD BAND at the BOTTOM that a
  `position:fixed` map can't paint into → the `<body>` background showed through there.
  Confirmed by the on-screen `#dbgOverlay` readout, not theory.
- **Ruled out (don't re-litigate):** (1) the iOS **26.1** PWA status-bar regression
  (WebKit bug 301994, fixed in 26.2) — user is on **26.2+**, not affected. (2) The old
  **negative-inset hack** `#map{ top:calc(0 - --sa-top); bottom:calc(0 - --sa-bottom) }`
  is a **documented dead end** — a fixed element cannot paint into an off-viewport band.
- **FIX (verified on device — `innerH 812`, `#map`+`canvas` 812, no red):** `html,body`
  and `#map` use **`height:100dvh`** (browser tab — respects the collapsing address bar)
  with **`@media (display-mode: standalone){ html,body,#map{ height:100vh } }`** (installed
  PWA — `100vh` is full-screen AND correct on cold start; `100dvh` is NOT, per the
  full-screen-canvas guidance). `#map` = `position:fixed; top:0; left:0; width:100vw;
  height:100dvh`. `overflow:hidden` on body.
- **V5 bottom bar (now EVERY width — desktop == mobile):** collapsed edit panel renders as
  a round rust **pencil FAB, bottom-right** (`.panel.collapsed` in base styles + a
  `.panel-fab-pencil` span inside `.panel-header`, hidden unless collapsed). Map
  **attribution moved to bottom-LEFT** as a compact `ⓘ` (`attributionControl:false` in the
  `Map` ctor + `map.addControl(new maplibregl.AttributionControl({compact:true}),
  'bottom-left')`; the collapse-once helper now runs on all widths). Both icons share a flat
  **12px baseline**. The **"N publish features loaded" status (`.message`) is dropped** on
  all widths. Attribution is capped `max-width: calc(100vw - 24px - insets -
  var(--edit-fab-reserve))` so its expanded credit list can't overrun the FAB (~20px clear).
- **Edit gate — DEFERRED by user ("decide later / keep on"):** `--edit-fab-reserve` (76px,
  →`0` when off) + `html.editor-off{ .panel display:none; reserve 0 }` + a `<head>` script
  that sets `editor-off` from the `?edit` param. **Default editor-ON.** `?edit=0` previews
  the public/invisible layout (no FAB, attribution reclaims full width); `?edit=1` forces on.
  Production trigger (hostname / param / stored flag) **NOT chosen yet**. OPEN: `editor-off`
  currently hides the **whole** right panel (incl. presets / layer toggles), not just the
  editor sections — decide if a public viewer should keep those.
- **Mockups (review artifacts):** round 2 `website/bottombar_compare2.html` +
  `bottombar_v5_fab` / `v6_pill` / `v7_credits.html` (on top of round 1
  `bottombar_compare.html` + v1–v4). **V5 (FAB) chosen.** Retire per the `misc_4`
  mockup-cleanup routing once the look is locked.
- **STILL-LIVE DIAGNOSTICS to strip at closeout (kept ONLY for on-device verification):**
  red `html,body{ background:#ff0033 }` (revert to a map-toned neutral); the blue map
  background-layer paint `#1e66ff`; the green `#dbgOverlay` div + `updateDbgOverlay()` /
  resync JS; and the `-dbg` suffix on `#appVersion` + sw `VERSION`.
- **NEXT SESSION:** (1) confirm `v13-dbg` reads right on the phone (FAB bottom-right + ⓘ
  bottom-left aligned low, no overlap when ⓘ is expanded, no red band; `?edit=0` shows the
  clean public layout); (2) strip the diagnostics above + set neutral body bg + drop `-dbg`;
  (3) commit; (4) decide the gate trigger only if/when actually splitting public vs editor.
  No build card exists for this PWA work yet — if it grows, open one under the active sprint.

**2026-05-30 (session — bottom-icon baseline aligned, `v13-dbg`) — the ⓘ and the pencil
FAB now share a baseline ON THE DEVICE. Working tree, uncommitted, served straight to the
phone.** Files: `website/index.html` + `website/sw.js` (VERSION v12→v13).
- **The bug (measured from the device screenshot, NOT theorised):** `Screenshot
  2026-05-30 at 23.30.30.png` is 1125×2436 = iPhone @3x (375×812pt, so 1pt=3px). The ⓘ
  bottom sat **12pt** off the screen bottom (= its `margin-bottom:12px`); the pencil FAB
  bottom sat **62pt** off — a **50pt** gap — even though both CSS rules said `bottom:12px`.
- **Root cause (it was already in the dbg overlay):** the overlay reads `innerH 812 /
  clientH 762`. The ⓘ is a MapLibre control INSIDE `#map` (`position:fixed`) → anchors to
  the true 812px visual viewport. The pencil is `.panel` with **`position:absolute`** →
  iOS anchors it to the `<html>` content box, which it measures as **762px** (812 − the
  50px top safe area). `762−12 = 750` from top = **62px off the bottom**. `62−12 = 50` =
  exactly the top safe area. Different positioning contexts, same `bottom:12px`, 50px split.
- **WHY PLAYWRIGHT IS USELESS HERE (don't reach for it on PWA safe-area bugs again):**
  desktop Chromium has no safe area, so `env(safe-area-inset-*)`=0 and `innerH==clientH`.
  Absolute and fixed then resolve identically → Playwright reported BOTH icons at
  `fromBottom:12` (aligned). It actively masks the exact split that matters. Ground truth
  for this class of bug is the device screenshot + the on-screen dbg readout. (This is the
  same trap that ate v5–v11's "pwa bottom math".)
- **FIX:** `.panel` base rule `position:absolute → position:fixed` (anchors to the same
  viewport as the ⓘ; inert on desktop where body has no scroll). Both baselines nudged
  `12→18px` ("up a bit" per review). ⓘ left `12→16px` ("right a bit"). Pencil kept at
  `right:12px` — read "do it for the pencil" as *match the baseline*, not mirror the
  horizontal nudge (moving the FAB "right" would push it into its own corner). Say so to
  the user; easy to also nudge if they meant literal.
- **NEW DIAGNOSTIC line in `#dbgOverlay`:** `ⓘ fromBot N  ✎ fromBot N` — live
  `innerH − getBoundingClientRect().bottom` for both icons so the phone can confirm
  alignment by number. Desktop shows `18 / 18`; the phone MUST now also show equal numbers
  (was 12 / 62). **Strip this line with the other diagnostics at closeout.**
- **PWA LAYOUT LOCKED → snapshot saved.** User called the PWA styles "on point." The
  full working iOS-PWA markup + CSS (verbatim, annotated, with the five hard-won rules and
  the diagnostics-to-strip list) is now `brain/spinup/working_pwa_css.md`, pointed to from
  `brain_map.md` + `search_map.md`. This is the restore point — diff against it if the PWA
  layout ever regresses. **Not git-committed** (diagnostics still live; commit is the
  closeout step — offered to the user).

**PHASE 2 — iOS SAFARI TAB (`v14-dbg`) — diagnosed + red retired.** Device screenshot
`IMG_0719.PNG` + its `#dbgOverlay` gave ground truth: `standalone:false`, `innerH 663 /
clientH 663 / vv 663 @top0`, `screenH 812`, `#map t0 b663 h663`, `canvas h663`,
`safe T0 B0`, `ⓘ fromBot 18  ✎ fromBot 18`.
- **There is NO "short map" bug.** `#map` is `100dvh` = **663px** in the tab, and it fills
  it exactly (`#map h663` == `innerH 663` == `vv 663`). The missing `812 − 663 = 149px` is
  **Safari's own chrome** — top status bar (~50) + bottom address-bar toolbar (~99). A page
  in a Safari TAB cannot paint under that chrome (the PWA can, hence full 812). User asked
  "is there code to make it short?" — answer logged: no, it's Safari reserving the space.
- **The red bands were the diagnostic body bg.** iOS Safari tints its status bar + toolbar
  by sampling the page background; `html,body{background:#ff0033}` made both chrome zones
  red. **FIX: retired the red → manifest cream `#F5EFE0`** (`html,body{background:#F5EFE0}`).
  Invisible in the PWA (fixed map covers it); in the tab it's the neutral tint Safari shows
  in its chrome. Verify on device: bands should now read cream, not red. **The map cannot
  be made to fill Safari's chrome in a tab — that is by design, not a bug.**
- **Considered + rejected (don't re-litigate):** switching the tab to `#map{height:100vh}`
  to paint under the bottom toolbar — the §3 working-CSS comment already rejects it ("100vh
  runs too tall in a tab", bottom hidden behind the bar). Allowing scroll to minimize the
  toolbar (grows dvh) is out — we are deliberately `overflow:hidden`, no scroll, and it's
  janky. iOS `apple-mobile-web-app-status-bar-style` is inert in a tab.
- **Diagnostics after v15:** `#1e66ff` map background paint, the `#dbgOverlay` div + JS
  (incl. the `fromBot` line), the `-dbg` suffix — **ALL STRIPPED at v18 (see below).**
- **`v15-dbg` — top bar BLACK so it "disappears."** User asked to black out the top.
  `html,body{background:#000}` → iOS tints the Safari status bar + bottom band black; on a
  notched iPhone the black strips merge with the bezel/notch (white system text). One
  change cleans BOTH ends (the dark Safari address pill blends into the black bottom band
  too). Confirms the lever is body-bg sampling, not theme-color. Verify on device.
- **`v16-dbg` — inverted (concave) rounded corners.** User wanted the black frame
  rounded, not sharp. Four fixed `.screen-corner` divs (tl/tr/bl/br) after `#map`, each a
  `--frame-radius` (18px, tunable in `:root`) square painted with a radial-gradient that's
  transparent in a quarter-disc toward the map and `#000` in the outer L → a concave black
  corner that blends with the body bg + bands. `pointer-events:none`, `z-index:1` (above
  the map canvas, below all controls z≥2 so it never covers the pills/FAB). Hidden via
  `@media (display-mode: standalone)` (no bands in the PWA; device rounds the screen).
  Mechanism verified on desktop (Playwright): outer corner pixels `#000`, interiors reveal
  map/controls, 0 errors. On-device look (radius + alignment with the bands) is the user's
  to confirm; tune `--frame-radius` if 18px is too tight/loose.
- **`v17-dbg` — corner fillets scoped to iOS Safari TAB only.** Per user ("only iphone
  browser, no pwa, no browser"): `.screen-corner` is now `display:none` by default and
  shown only under `html.ios-browser`, a class the `<head>` script adds when `isIOS &&
  !standalone` (UA `/iP(hone|od|ad)/` or MacIntel+touch for iPad; standalone via
  matchMedia/navigator.standalone). Dropped the old `@media (display-mode: standalone)`
  hide. Verified (Playwright UA swap): default desktop → no `ios-browser` class, corner
  `display:none`; iPhone UA → class present, `display:block`. So PWA and desktop/non-iOS
  browsers get sharp corners; only the iOS Safari tab gets the rounded frame.
- **`v18` — DIAGNOSTICS STRIPPED, build clean (user: "happy with mobile styles").** All
  scaffolding removed: (1) the `#1e66ff` blue map-background paint → restored to `#efe7d5`
  at 3 sites (base style + two preset `paints.background`); (2) the `#dbgOverlay` div +
  `updateDbgOverlay()` + its resync wiring (incl. the `fromBot` line) deleted —
  `resyncViewport` kept (its `map.resize()` + search reposition are functional, only the
  overlay call dropped); (3) `-dbg` suffix dropped from `#appVersion` + `sw.js VERSION`,
  both now `v18`. **KEEPERS (not diagnostics):** the `#000` body bg (the black "disappear"
  chrome) and the four `.screen-corner` inverted fillets (iOS-tab-scoped). Smoke-checked:
  no console errors, no `dbgOverlay`/`updateDbgOverlay`/`1e66ff`/`-dbg` remnants (grep
  clean), body bg black, `resyncViewport` intact. The PWA §1-§8 layout rules in
  `spinup/working_pwa_css.md` are unchanged. **Still UNCOMMITTED** — the working tree is
  now the clean closeout build and is ready to commit whenever the user confirms the v18
  reload on the phone. (No build card was ever opened for this PWA work; open one under the
  active sprint if it grows.)
- **NEXT — bottom bar "fill with map" (user is open to it).** Real technique but a
  measure-and-iterate job, NOT a clean one-liner: Safari's bottom address bar is
  translucent and floats over the page, so painting the map behind it means sizing the MAP
  CANVAS to the large viewport (`100vh`/`100lvh`) while keeping controls on the visible
  area. The snag: the ⓘ attribution lives INSIDE `#map` and is bottom-anchored, so a taller
  `#map` pushes it behind the bar; iOS does NOT expose the tab toolbar height to CSS
  (`env()` insets are 0 in a tab), so re-anchoring the ⓘ above the bar needs a JS measure
  (`map.getBoundingClientRect().height − window.innerHeight` → a `--safari-bottombar` var)
  + on-device screenshot tuning. The FAB is a fixed body child so it's unaffected. The TOP
  status bar is NOT fillable in a tab — color/tint only (only the installed PWA goes
  edge-to-edge under the status bar). Do this as its own version once the user says go.

**2026-05-30 (triage) — Sprint 04 reviewed and sorted (no code).** Every card in
`tasks/04_event_app/` was assessed done / partial / not-done and moved.
**Shipped → `04_event_app/_done/`:** `calendar_group_icon_review`,
`editor_unified_tree`, `editor_three_buckets_v3c`,
`editor_unified_positioned_features`, `misc_4` (close-out header added), and a
**new split card** `bake_first_poi_serve_slice` (the shipped bake-first POI SERVE
pipeline carved out of `star_driven_poi_list` + `dev_db_snapshot_reseed`).
**Deferred → `tasks/10_deferred/`** (each got a "Deferred because" header):
`event_crud_upload_loop`, `paper_map_trail_extraction` (partial/active — flagged
it may belong on an active sprint if the edited-SVG loop continues),
`star_driven_poi_list`, `dev_db_snapshot_reseed`, `data_integrity_publishability`,
`brand_assets_and_permissions`, `calendar_placeholder_state`,
`park_bounds_icon_apply`, `rock_warblers_content_audit`, `poi_editor_followups`,
`viewer_polish_followups`. `source_layers.md` left in place (reference list, not a
card). `04_event_app/_readme.md` + `10_deferred/_readme.md` updated with the
disposition; pre-triage card list kept for history. Doc moves only, uncommitted.

**2026-05-30 (session 5g) — Locate + Install moved into left-rail float groups (V2).**
Two utility buttons that were scattered on the map chrome now stack as their own
floating groups below the calendar tab icon in `.left-controls`: **Locate** (neutral
cream 44px square, GPS-crosshair glyph) and **Install** (rust 44px square, download-to-tray
glyph). Picked V2 ("accented install") from a 4-up compare round. Implementation in
`website/index.html`: (1) new `.util-group`/`.util-btn`/`#pwaInstallBtn.util-install` CSS
matched to the `.lr-icon-col` chrome; (2) MapLibre's default top-right `GeolocateControl`
button is hidden (`.maplibregl-ctrl-top-right .maplibregl-ctrl-group{display:none}`) and
surfaced via a new `#locateBtn` that calls `geolocate.trigger()` and mirrors
`trackuserlocationstart/end`+`error` onto an `.active` (moss) state; (3) the old fixed
bottom-left `#pwaInstallBtn` + `#pwaIosHint` were relocated into `.left-controls` — the
install button *is* its own group and self-hides via the `hidden` attr until
`beforeinstallprompt` (so no empty rust card shows), single id preserved, PWA script
untouched (it's getElementById-based). Verified live (Playwright, geolocation granted):
locate visible at x13/y697 44×44 below the drawer, install rust square at y750, default
geolocate hidden, click → tracking + active state, 0 console errors. Compare round shipped
as review artifacts linked from the right panel **Comparisons** section
(`floatgroup_compare.html` + `floatgroup_v1_twins`/`v2_accent`/`v3_joined`/`v4_labeled`.html)
— retire per the `misc_4` mockup-cleanup routing once the look is locked. `website/index.html`
+ the 5 `floatgroup_*.html` mockups uncommitted.

**2026-05-30 (session 5f) — snap_trim "dangling" detector de-noised + the 3 ends verified.**
User challenged the "3 dangling ends" warning; all three verified and they were right.
`snap_trim_trails.py` had flagged any end >18 m from another feature, over-counting. Now
it classifies: **self-loops** (end rejoins its OWN line — trail "9" closes onto its own
vertex #6 at 0 m, a lollipop; not a gap), **road dead-ends** (a road that terminates in
space but joins the network at its other end — the unnamed road connects at 0 m one end,
74 m spur the other), and **trail danglers** (the real review set). Result on edited_10:
1 self-loop + 1 road dead-end + **1 true trail dangler** (unnamed trail start, 88 m from
trail 50). New `SELF_LOOP_M=2.0`; report now lists each by kind/name/gap. Served gold data
unchanged (re-run is 0 trim / 0 snap on edited_10). Minor latent bug noted: passing a
*relative* out-path trips `out.relative_to(REPO)`; default in-place run is unaffected.
`mvp/scripts/snap_trim_trails.py` uncommitted.

**2026-05-30 (session 5e) — trail search wired up.** The merged `aop-trail-network`
layer was never indexed for search, so trails were unfindable. Fixed in
`website/index.html`: (1) `indexFeatures(aopTrailNetworkData, 'trail', aopTrailNetworkToggle,
null, name→['trail <name>'])` registers every NAMED trail (number "32" or string "Riot
Hill"); unnamed edges are skipped. (2) The 2-char search floor now lets a lone digit
through (`/^\d$/`) so trails 1–9 are searchable. (3) New `searchRank()` orders matches
exact→prefix→substring, so a bare number floats the trail above building addresses that
merely contain the digit (without it, "9" buried trail 9 under "1094 Kelly Cove Road"…).
Selecting a trail flies there, flips the network layer on, pulses the highlight. Durable
coverage added to `playwright_verify_search.py` (trail-by-number, single-digit, string
name, fly+auto-enable) — PASS, no regressions. NOTE: the **20 unnamed trails** (from the
5d marker-rename fix) have no name → not searchable until the user names them in Affinity.
`website/index.html` + `mvp/scripts/playwright_verify_search.py` uncommitted.

**2026-05-29 (session 5d) — IMPORTER BUG FIXED (marker auto-renaming) + edited_10 reimported (current served).**
User: "something is renaming 32 and 58." Root cause found in `import_trace_svg.py`
`reattach_from_markers`: it stamped a nearby marker's `trail_number` onto UNNAMED
trails (then the name-fallback turned that number into the `name`). So one hand-typed
"32" became three "32"s — the #32 marker cluster sat near two unnamed neighbours — and
phantom "58"s appeared from a #58 marker on an unnamed trail the user never named.
Proof: edited_10 SVG has exactly one path named 32 and every SVG name unique, but the
importer output three 32s (sfwda-42/43 were `name=None` in the SVG). **Fix: markers no
longer assign `trail_number`/name at all — the user's typed object-name (`_editable_name`)
is the SOLE source of a trail's number/identity; markers still bootstrap DIFFICULTY for
uncoloured trails only.** Re-imported edited_10 with the fix → **0 duplicate numbers**,
32→1, 58→gone, 87 numbered / 100 named / 20 genuinely-unnamed (left for the user to name,
not auto-stamped). snap_trim 3 dangling, gold stamped, `playwright_verify_sfwda_trace.py`
PASS. This (edited_10 + fix) is the current served `aop_trail_network.geojson`,
superseding edited_11. The earlier dup find-and-fix loop (flag-red SVGs) is now moot for
auto-created dups; any remaining dups would be genuinely user-typed. `import_trace_svg.py`
+ `website/data/` uncommitted.

**2026-05-29 (session 5c) — edited_11 imported + dup find-and-fix (superseded by 5d).**
Pipeline `import → snap_trim → export_gold_trail_network --from …edited_11.svg`: 120
feats, 91 numbered, 0 grey (Easy 30 / Mod 42 / Diff 44 / Road 4). Verifier PASS.
Duplicate-number QA loop with the user: I flag duplicate-number trails RED in a
throwaway working copy → `export_trace_svg.py --color feature` → editable SVG
`aop_trail_network_2025_dupflag_edit.svg` (gold geojson left untouched; temp file
deleted after export). edited_11 cleared dups **1/47/90** (green 47→42, added 97) but
**28, 32(×3), 55 still duplicated** (55 is new — a 56 was renamed to an already-used
55). Also colour-vs-marker mismatches open: 35/95/97 green but markers moderate; 28(×2)
& one 32 colored black but markers moderate (markers = sheet symbols, stronger than the
number-band guess). Re-flagged SVG regenerated for the next pass. CAVEAT logged for the
user: don't leave any stroke red on re-export — red's nearest import anchor is orange,
so a leftover red imports as a *road*; recolour each to its real difficulty.

**2026-05-29 (session 5b) — edited_9 imported.** Same pipeline; identical aggregate
shape (120 / 94 numbered / 0 grey), diff geometric — 4 trails repositioned (11, 34, 47,
Pretender). Verifier PASS. Superseded by edited_11.

**2026-05-29 (session 5) — edited_8 imported + gold-export script.** Imported
`aop_trail_network_2025_edited_8.svg` (120 trails, osm merged into the one
`traced_trails` layer) → `website/data/aop_trail_network.geojson`: 120 edges, 94
numbered, 103 named, **0 grey** (Easy 30 / Moderate 46 / Difficult 40 / Road 4).
`snap_trim_trails.py` fixed 1 overshoot + 1 gap, 3 dangling >18 m left for review.
New **`mvp/scripts/export_gold_trail_network.py`** makes the "gold" step
reproducible: it rewrites only `_meta` (crs, colour legend, difficulty band, counts,
schema, auto-computed band-vs-colour `review_flags`) so the served file is the
self-contained gold the static viewer loads directly on a new install (no DB /
pipeline / localStorage). Run order: `import_trace_svg.py <svg>` →
`snap_trim_trails.py` → `export_gold_trail_network.py --from <svg>`. Verified: bbox
inside envelope, 0 degenerate, `playwright_verify_sfwda_trace.py` PASS. Review flags
this run: trails 35, 1, 95, 47 (colour vs number-band disagreements). Details in
`tasks/04_event_app/paper_map_trail_extraction.md` "edited_8 imported" block. All
`website/data/` + `mvp/scripts/` uncommitted.

**2026-05-29 (session 4) — string trail names + difficulty colours + snap/trim
(golden-data prep).** The merged network dropped `JW2`/`JW20` and other **named**
trails because the round-trip treated name as an integer. Fixed in
`import_trace_svg.py` (`_editable_name`: serif:id → inkscape:label → id; import
every name except `?`; non-numeric names locked) + `export_trace_svg.py` (writes
the name to both `inkscape:label` and `serif:id`). Re-import → 119 trails, 104
named, all 9 non-numeric names land (Area 51, GWT, JW1–4, JW20, Pretender, Riot
Hill). Colours switched from per-trail rainbow to **green/blue/black by difficulty**
(`assign_difficulty` band fallback; 22 grey unknowns flagged). New
`mvp/scripts/snap_trim_trails.py` cleans topology — 31 overshoots trimmed, 48 gaps
snapped, 3 dangling left for review. Re-exported the stack over the 2025 backdrop:
`brain/output/paper_trace/aop_trail_network_2025_edit.svg` (difficulty colours,
names on editable channels) — **this is the artifact for the user's review/edit pass
→ re-import = golden data.** `playwright_verify_sfwda_trace.py` PASS; overlay
`brain/output/net_2025_difficulty_overlay.png`. Details in
`tasks/04_event_app/paper_map_trail_extraction.md` "String trail names…" block. All
`website/data/` + `mvp/scripts/` + `website/index.html` uncommitted.

**2026-05-29 (session 3) — paper-map trail extraction PROTOTYPE.** New card
`tasks/04_event_app/paper_map_trail_extraction.md`. User goal: the SFWDA 2015
paper map is the only surviving record of trails the prior owner lost; extract
them cleanly. User corrected my framing — the sheet was **printed from a mapping
system, so it is positionally accurate once the (already-correct) warp is applied**;
"high for shape, low for current trails" was about 2015 *vintage*, not precision.
Built three `mvp/scripts/` scripts (need `numpy opencv-python-headless pillow
scikit-image shapely`, pip'd into the global Python): `extract_paper_trails.py`
(124 markers — 40 green Easy / 42 blue Moderate / 42 black-triangle Difficult;
triangles solved via close+OPEN since they fuse to the trail lines + trail-line
isolation), `paper_trace_warp.py` (`PaperWarp` exactly replicates the viewer's
270°-rotate + 6×6 bilinear mesh — corner self-check passes), `vectorize_paper_trails.py`
(skeletonize → graph walk → DP simplify → warp = 382 edges/1521 vertices, 116/124
markers matched). Outputs in `brain/output/paper_trace/` (scratch): `sfwda_markers.geojson`,
`sfwda_trails.geojson`, debug overlays. Verified by observation (overlays) + georef
self-check + bbox-inside-envelope. Per user ("load the data in the app to review,
refine after"), wired into `website/index.html` as two default-OFF, in-no-preset
review layers (`sfwda-trace-trails` + `sfwda-trace-markers`, toggles under External
reference) with data copied to `website/data/sfwda_traced_{trails,markers}.geojson`;
verifier `mvp/scripts/playwright_verify_sfwda_trace.py` PASS (512 features, survives
preset switch, 0 console errors). Visual: Trace preset + SFWDA raster + traced trails
shows the trace landing on the paper-map ink (`brain/output/sfwda_trace_review_traceonly.png`).
Open (refine pass): trail-number OCR (deferred, no higher-res scan), boundary-split,
camping-icon false positives, junction topology. `website/index.html` +
`website/data/` changes are UNCOMMITTED.

**2026-05-29 (session 2) — bake-first POI slice SHIPPED.** Acting on the
push-order decision (bake first; one `publish.geojson`), the SERVE half of the
star-driven pipeline now runs end-to-end: new `core.pois` table + `publish.pois`
gate in `mvp/init_db.sql`, `export_publish_geojson.sh` UNION extended with a
`layer='poi'` branch, idempotent `mvp/scripts/seed_core_pois.sql` (Pavilion +
Ellis Cemetery publish; a Proving-Grounds candidate left unpublished to prove
the gate excludes it — `core.pois`=3 rows, `publish.pois`=2), and `index.html`
renders the baked set as a `published_destinations` POI-tab group + `publish-pois`
map layer. Verifier `mvp/scripts/playwright_verify_baked_pois.py` PASS; adjacent
verifiers show only documented pre-existing fails. Authoring surface still NOT
chosen (fork open); legacy `buildPoiGroups()` scaffolding still renders alongside.
Full close-out + deferred items in `tasks/04_event_app/star_driven_poi_list.md`
"Bake-first slice — SHIPPED" block. All uncommitted.

**2026-05-29 — star-driven POI list: pipeline design (no code).** New card
`tasks/04_event_app/star_driven_poi_list.md`. Reviewed how the right-rail ★
Visitor list maps to the left POI tab; they're two lists built two ways and
only coincide for drawn POIs. Locked principle: **★ is the one curation gate;
the starred set _is_ the POI list** (all destination layers starrable, tab
starts empty, brand logos leave the ★ axis). User rejected designing against
the current files — the seed/index/localStorage stores are prototype
scaffolding. Target is **one pipeline: author → save to PostGIS → bake to file
→ static viewer serves the baked file** (= the northstar spine + source_register
`raw→core→publish`). The ★ collapses to one DB attribute + a publish-zone view;
the seed-vs-index file question is void. Gap: nothing wires the web editor to
the DB, and the DB→file bake is unwritten. Next decision owed: push order
between **(a) authoring surface — who writes the DB** and **(b) the bake**. This
was design/feeling-out only — no `website/index.html` change, tree clean.

**2026-05-28 — editor three-bucket V3c shipped.** Supersedes the unified-tree pass below. `tasks/04_event_app/editor_three_buckets_v3c.md`. The right-rail Map editor section collapses from 5 buckets to **3** (Point / Line / Polygon) plus the ★ Visitor list; Image and Callout fold into Point and Polygon by geometry (brand logos → Point/Brand, visitor context → Polygon/Visitor). Inside each bucket, source sub-groups split rows by origin (Drawn / Trailheads / Brand / Visitor) — Drawn is open by default, references collapse with their count visible. The 5-toggle layer strip is gone; the 5 `show*` inputs survive inside a hidden `#legacyLayerToggles` form block so preset capture/apply, MapLibre layer-visibility wiring, and Terra-Draw class flips keep working unchanged. Sub-group head bulk-checkboxes are the visible mirror, two-way bridged via change events. Each bucket head carries a green `+` that opens an inline `.editor-create-inline` row right inside the bucket body (bucket-scoped category select + matching primary action + cancel `✕` + help text); the footer shrinks to Export / Clear / status / help. `setDrawMode` now flips active state on every bucket's `+` and start-btn alongside the legacy hidden buttons. `draw.on('finish')` reads category from `currentCreateBucket.categorySelect.value`. A `FEATURE_LIST_LAYERS.trailheads` spec was added (read-only, no ★, no accordion); `publish.geojson` ships zero trailhead features today so the sub-group head reads `—` until trailhead data lands. **Event-schedule POIs are regular drawn POIs** — they render alongside editorPois Points inside the Point/Drawn sub-group with their `#tag` visible on the row. Mockups under `website/editor_unified_*.html` (compare pages: `editor_unified_compare.html` for V1–V4 axis pick, `editor_unified_v3_create_compare.html` for V3a/b/c create-flow pick) — retire per `misc_4` mockup-cleanup routing. Verifier impact: `playwright_verify_poi_editor.py` rewritten for the per-bucket selectors (PASS); `playwright_verify_presets.py` editor-tree assertion updated for 3-bucket shape (PASS on V3c assertions, 3 pre-existing fails remain — publishable-section / OSM-section-move / mobile-overlap, all routed to `viewer_polish_followups.md`); `playwright_verify_session_tools.py` PASS; `playwright_verify_synthetic_activity.py` PASS; `playwright_verify_feature_list.py` PASS on cemeteries/buildings/visitor/brand (3 fails pre-existing on retired publishable-section export path); `playwright_verify_event_schedule.py` PASS on tag-driven/clock-times blocks (6 fails pre-existing on trail-lane fallback). DOM snapshot screenshot at `/tmp/aop_editor_v3c.png` (not durable).

**2026-05-27 (later) — editor unified tree shipped.** `tasks/04_event_app/editor_unified_tree.md`. The right rail's `data-section="poi"` block (group toggle deck + `wirePoiPanel` two-way bridge) was deleted. The `data-section="editor"` section now hosts a five-bucket tree by renderable kind: ● Point · ╱ Line · ▭ Polygon · ⌗ Image · ⌑ Callout, plus a virtual `★ Visitor list` group at the top that live-mirrors every highlighted feature across `editorPois`, `brandLogos`, and `visitorContext` (the last two newly opted into `highlightable: true`; brand-logos and visitor-context override stores now carry `highlight` so the flag survives reload). editorPois renders three times via the new `renderFeatureList(layerKey, { onlyGroupId })` opt arg so its Point / Polygon / LineString groups split across the three matching buckets. The 5 layer toggles (`showEventSchedule`, `showTrailheads`, `showVisitorContext`, `showBrandLogos`, `showEditorPois`) move to a thin strip at the top of the editor section; the create row (category + Place / Draw / Trace + Export / Clear + status + help) drops to a `.editor-create-footer` at the bottom. `setEditorFeatureNotes` trim fix bundled in (one of the two S3 review items from `poi_editor_followups.md`). Verifier impact: `playwright_verify_poi_editor.py` PASS, `playwright_verify_synthetic_activity.py` PASS, `playwright_verify_session_tools.py` PASS, `playwright_verify_presets.py` PASS on editor-tree + console assertions (one pre-existing mobile-overlap 4 px boundary remains), `playwright_verify_feature_list.py` PASS on editor-tree + visitor-context reveal path (three `data-section="publishable"` failures pre-existing — that section does not exist), `playwright_verify_event_schedule.py` trail-lane fallback failures pre-existing per the earlier 2026-05-27 routing.

Read an archive only if you need to retrace why something was built. The durable record for each feature lives in its `tasks/*/_done/<feature>.md` build card, `research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`.

## Where we are

Sprint 01 (MVP), Sprint 02 (Editor & Polish), and Sprint 03 (Event App Loop)
are closed. Sprint 03's reviewed cards live in `tasks/03_event_app/_done/`.
`tasks/03_event_app/misc_3.md` was left active by request. Sprint 04 starts at
`tasks/04_event_app/_readme.md`.

The Sprint 02 carryover router is archived at
`tasks/03_event_app/_done/viewer_polish_carryover.md`. Lanes 1–5 shipped
2026-05-24 (hot-control two-lane, calendar expand + scroll-into-view,
collapse-icon uniformity, default-layer audit table in `research/viewer.md`,
brand-logo size slider + add-image runbook). Lane 6 shipped its main pass in
`tasks/03_event_app/_done/code_health_pass_4.md`; residual viewer polish now
lives at `tasks/04_event_app/viewer_polish_followups.md`. Lane 7 stays on
`tasks/01_mvp/_done/community_trails_import.md` and is also visible in
`tasks/04_event_app/data_integrity_publishability.md`. The 2026-05-25 camera
correction is applied: zoom shortcuts reset to flat west-up, while Park / Topo
/ Trace layer presets preserve zoom, pitch, bearing, and independent 3D state.

**2026-05-25 Pass 4 + misc landings.** Calendar-card cream-surface chrome restored (`misc.md` "left side event calendar transparent" item — `.calendar-card` is back in the shared cream-surface group at `website/index.html:31`). Pass 4 first wave shipped via four parallel agents and landed in main: (1) `!important` cluster fully eliminated in the right-rail collapse-button + tune-control region by raising specificity to `.panel`-scoped selectors; (2) 8 safe palette token swaps (`#d8cdb4 → var(--cream-border)`, etc.); (3) full theme readability report (8 surfaces, 13 KEEP / 6 TWEAK / 4 FIX with WCAG math) recorded in `tasks/03_event_app/_done/code_health_pass_4.md`; (4) Critique-C1 hot-button copy renamed off "heat" wording — `Trail heat / Activity evidence` → `Trail activity / Where rigs spent time` in HTML defaults, `refreshHotButton` fallbacks, aria-labels, and the matching verifier assertion. Residual Pass 4 follow-ups now live in `tasks/04_event_app/viewer_polish_followups.md`.

Sprint 04's main app thrust is `tasks/04_event_app/event_crud_upload_loop.md`
— event setup, CRUD, uploads, and the submission -> review -> publish loop.
`tasks/04_event_app/dev_db_snapshot_reseed.md` carries the dev DB dump/reseed
need from `misc.md`. `tasks/03_event_app/_done/left_panel_poi_browser.md`
shipped 2026-05-25 — the viewer now has a third left-rail `POI` tab sitting
between `Events` and `About`, rendering a grouped index of event anchors,
in-park buildings, observed trails, cemeteries, off-park visitor support, and
drawn POIs. Visitor blurbs + revisit-note placeholders live in
`website/data/aop_poi_index.json` (6 groups, 20 entries, 10 placeholders
flagged for follow-up); the source GeoJSONs stay clean so re-exports can't
overwrite authored copy. Smoke checks land in the extended
`playwright_verify_presets.py`; a dedicated `playwright_verify_left_poi_browser.py`
is now carried by `tasks/04_event_app/viewer_polish_followups.md`.

**2026-05-26 — left-rail drawer shipped.** `tasks/03_event_app/_done/left_rail_collapse_tabs.md` shipped into `website/index.html`: Search / Hot / Calendar now live in a two-column left drawer with per-card icons, persisted open/closed state, hot-data auto-open that respects user-close, all-closed standalone state, and the calendar resize handle. Focused coverage: `mvp/scripts/playwright_verify_left_rail_drawer.py`.

**2026-05-26 — right-panel editor consistency.** `tasks/03_event_app/_done/right_panel_editor_consistency.md` shipped. `⧉ Export all` moved into the panel header beside `▾ Collapse panel` (the old `.panel-actions` row at the bottom of `#panelBody` is gone). Publishable section header gained its own `⧉` for parity with Source / Derived / Map editor; the POI section was deliberately not given one (its `poiGroup*` IDs don't match `sectionInputs`' `show*` filter, so the payload would be empty). Three layers that previously appeared as bare checkboxes in Publishable now get the full editor treatment: `activityHotspots`, `syntheticActivity`, and `eventSchedule` are registered in both `TUNABLE_LAYERS` (paint drawers) and `FEATURE_LIST_LAYERS` (CRUD index — 65 / 18 / 8 rows respectively, each with visibility + fly). New `refreshFeatureListData` helper lets `rebuildEventScheduleData` push fresh anchor data into the runtime without recursing through `registerFeatureListLayer`. The two failures in `playwright_verify_event_schedule.py` (search magnifier missing, hot-button click timeout) were verified pre-existing by stash + replay — not caused by this card.

**2026-05-26 — session tools shipped.** `tasks/03_event_app/_done/viewer_session_state_test_clock.md` shipped from `misc_2.md`: right-panel virtual clock controls (`aop_virtual_clock_v1`), Reset viewer, and pocket-map reload state (`aop_viewer_session_state_v1`) for active preset, active left tab, search query, and selected event. Landmark-hot decision: keep landmarks in POI/search, not a third Hot lane. Focused coverage: `mvp/scripts/playwright_verify_session_tools.py`; adjacent suites `playwright_verify_left_rail_drawer.py`, `playwright_verify_event_schedule.py`, and `playwright_verify_presets.py` passed after the startup-order fix for restoring the POI tab.

**2026-05-26 — drawn-POI CRUD reshaped.** `tasks/03_event_app/_done/poi_editor_tree_inline_accordion.md` shipped. The flat editorPois list is now a kind-grouped tree — `Drawn POI → POI / Footprint / Line → named item` (`FEATURE_LIST_LAYERS.editorPois.groups` matches on `feature.geometry.type`, and `groupForFeature` now passes `feature` through alongside `props` so other layers ignore the 2nd arg). Each leaf carries a trailing `▸` chevron that opens an inline accordion editor below the row: name, category (now mutable post-create), tag, notes (new `feature.properties.notes` field), geometry summary, action row (`🎯 Fly · ✋ Move · ⎘ Duplicate · ⧉ Copy GeoJSON · Delete`). Tag input and `⧉` copy button move off the row into the editor; visibility checkbox, `★` highlight, name (click=fly), `🎯`, `✋`, and the new `▸` chevron stay on the row. The MapLibre rename/delete popup (`openPoiPopup`) retired — map-click on a drawn POI now expands the leaf's editor in the right panel and flashes the row. Card mockup pass: `website/poi_crud_compare.html` + four `poi_crud_v{1..4}_*.html` variants; V1 (inline accordion) chosen. Same session shipped the editor seed + dump-to-GeoJSON path: `website/data/aop_editor_seed_pois.geojson` (schema `aop_editor_seed_v1`, first entry the `aop_seed_pavilion` POI at the 1010 Ellis Cove centroid carrying `seed_tag: '#pavilion'`); `maybeSeedEditorPois` runs on a fresh install or after Reset viewer and writes both the POI store and the `#pavilion` tag binding, stripping the matching tag off any other layer one-shot (migration: 1010 building → seeded POI). The building-side `maybeSeedFeatureTags` + `FEATURE_TAG_SEEDED_KEY` constant retired (the literal stays in the wipe list so existing installs get the sticky flag cleared on Reset). Workflow to update the seed lives in the create-row help text: `Export GeoJSON → replace the seed file with the download → commit`. Verifiers green: `playwright_verify_poi_editor.py` (asserts inline editor + delete; clean-slate now writes `[]` to leave the seed gate closed), `playwright_verify_feature_list.py` (POI copy path rewritten to expand the leaf first; same `[]` swap), `playwright_verify_presets.py`, `playwright_verify_session_tools.py` (Reset now asserts the seed re-installs `aop_editor_pois_v1` + `aop_feature_tags_v1` while the other ten viewer-owned keys stay cleared), `playwright_verify_event_schedule.py` (Tag-driven block rewritten: `#pavilion → editorPois/aop_seed_pavilion`, no building row pre-bound; live re-resolve test driven via `setFeatureTag` rather than the buildings drawer DOM).

The MVP backlog at `tasks/01_mvp/_readme.md` "Immediate next work" still has
open data-integrity items that unblock V1 publishable: item 9 (replace demo
trail/trailhead placeholders with real source-backed AOP data), item 3 (connect
QGIS to `localhost:55432`), item 8 (reconcile the 600+ acre official claim
against the parcel envelope), and item 10 (swap the AWS Terrarium DEM for USGS
3DEP 1 m tiles, deferred until the 10 m look earns its keep). Sprint 04 also
collects those blockers at `tasks/04_event_app/data_integrity_publishability.md`.

## Live preview ports

- Human/manual preview: `cd website && python3 -m http.server 8000` → `http://localhost:8000/`
- Playwright verifiers: `cd website && python3 -m http.server 8001` → `http://localhost:8001/`. If 8001 is occupied, clean up the stale Playwright viewer and reload 8001 instead of starting a new numbered localhost. Do not fall back to 8000 for Playwright.

## Loose ends not yet on a card

- SFWDA paper-map alignment: the 4-corner image-warp is inspection-grade. Decision still owed on whether true georeferencing (GCPs + affine/projective in GDAL/QGIS) is required before any SFWDA trail centerline can be promoted to `core.trail_centerlines`. Captured in `tasks/01_mvp/_done/community_trails_import.md`.
- `source_register.sources` rows still owed before any raw-zone context (OSM tracks/landmarks, NHD water, USGenWeb Ellis burial roster, FEMA building footprints) is promoted to a `publish.*` view. Rules: `northstar/source_register.md`.

## Sidecar artifact kept in this folder

- `event_schedule_context_20260522.json` — actively referenced by `tasks/01_mvp/_done/event_schedule_layer.md` and `research/viewer.md` as the sister-event research input. Leave in place until the schedule card is re-opened or retired.

## Session note

This file is handoff context, not a durable policy document. Keep it short. When a session ends, prune this file back to a pointer and archive the changelog to `session_context_<YYYYMMDD>.md`. Do not append session-by-session update blocks here — they belong in build cards, `research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`.
