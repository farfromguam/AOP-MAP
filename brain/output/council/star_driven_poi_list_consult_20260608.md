# Council consult — star_driven_poi_list.md readiness (2026-06-08)

> **Type:** design consult (not a diff done-review). **Tier:** full six (user-visible
> product-model change). **Chair:** Steward. **Verdict: ANDON → resolved to a readiness
> report + two user decisions.** Not "clear to execute as written."

#aop #council #consult #star #poi #listmode #readiness

-----

## The question

Is `tasks/10_deferred/star_driven_poi_list.md` ready to un-defer and execute, given the
gold migration + Sprint 05 (universal collector) + Sprint 07 shipped since it was written
(2026-05-29)? Resolve which open forks are still genuinely open vs. already answered, and
define the executable next slice.

## What the Steward grounded first (by observation)

- **C1 = 0** non-comment `layerKey === '` branches in `website/js/main.js` (universal
  feature-layer refactor shipped).
- **C2 done** — `collectStarredDestinations()` (main.js:1152) is the ONE collector;
  `buildPoiGroups()` (1302, POI tab) and `renderVisitorListGroup()` (1044, ★ list) are thin
  renderers over it; `VISITOR_LIST_LAYERS` retired. Shipped as
  `05_special_operation/_done/06_one_star_driven_collector.md`.
- **DB (gold):** `core.pois` + `publish.pois` **dropped**; `core.features` is the store
  (poi 4, buildings 5, cemeteries 8, trails 120, visitor 4, event 6, …). Bake-first SERVE
  shipped (`export_publish_geojson.sh` → one `publish.geojson`).
- **Exact remaining surface:** `listMode: 'wholesale'` on cemeteries(2274) / buildings(2345)
  / visitor(2653) / trails(2860); `'starred'` on editorPois(2472) + brandLogos(2778). The
  code comment at main.js:1145-1147 names it: decisions **#1/#2/#4 are "held for the user"**
  because they are user-visible.

## Seat verdicts

| Seat | Verdict | Load-bearing finding |
|------|---------|----------------------|
| **Witness** | clear + caveat | All 4 readiness claims confirmed by observation. Trap (a): baked POIs are a separate hardcoded union (collector ~1224), NOT governed by `listMode` — their gate is the bake (`publish.features WHERE permission/publish_status='publish'`), so the flip won't vanish them. Trap (b): exactly **1** feature in all 23 served files carries `highlight===true` (the editorPois seed) — flipping empties the four wholesale groups, which IS decision #2 "starts empty," not a regression. Trap (c): tile-independent harness exists (`playwright_verify_star_collector.py`). **CAVEAT:** decision #5 ("curation travels into the bake") is **unmet** for cemeteries/buildings/visitor/trails by the flip alone — their ★ lives only in localStorage; no author→DB path for those layers. |
| **Quartermaster** | andon | Do **not** un-defer the card *whole* — its engine + storage halves are a stale duplicate of card 06 + the gold cards. SUPERSEDE/FOLD: strike the shipped "one pipeline" diagram + the storage "open forks"; keep only the unshipped product directives #1/#2/#4. Remaining work = a spec-flag flip + render fields the rows already carry. Reuse-true confirmed (`pushRow(`=0, one collector, one registry, no new HTML). |
| **Mason** | andon | **THE correctness bug.** Cemeteries (2266) + buildings (2321) are **NOT `highlightable`** — no ★ control sets `highlight` on them. Flipping them to `'starred'` drops 100% of their rows on a *missing-control* basis = a banned **C5** row-dropping filter, not curation. Fix: **add `highlightable: true` to cemeteries + buildings as part of the slice** (the authored-attribute precondition) — flip + highlightable land together, never the flip alone. visitorContext (2682) + trails (2842) ARE highlightable → flip-safe. Published rows stay wholesale (bake is their gate) — make it a written guardrail. The flip itself is still a user re-confirm, not a Mason clear. |
| **Warden** | andon | **THE gate.** The flip is a true **DECISION** fork (distinct from the always-user COMMIT gate). The code comment at main.js:1145-1147 + card 06 (Step 4) + decision #2 all explicitly HELD it for the user — a user-visible change (POI tab ~20 rows → empty-until-curated) is an *end*, not a means; do not execute autonomously. Also: **annotate, don't delete** the card's directive sections (`preserve_card_directives`); storage forks answered by gold EXCEPT localStorage-as-buffer, which is **HELD as gold slice 6**. Re-home: drop stale `#04_event_app` tag + "Sprint 04 triage" header; dead `../04_event_app/` paths. |
| **Scribe** | andon | Card is stale + self-contradicting (cites dropped `core.pois`/`publish.pois` as live; pre-rename `blurb`; dead `index.html:NNNN` line numbers — JS moved to `website/js/main.js`; dead `../04_event_app/` → `04_edit`). Record the verdict in **both** the card AND `handoff/session_context.md` in the same pass or the brain self-contradicts. Preserve the user's "one pipeline" vision + verbatim quote; strike only stale storage/object/line prose; plain declaratives, no gloss. |

## Steward synthesis — the resolved answer

**Verdict: the card is NOT "ready to un-defer and execute as written."** But the consult is
fully resolved — no blocking unknowns remain, only two user decisions + the card rewrite.

### Forks resolved

- **CLOSED** (gold / Sprint 05): authoring surface for POIs/editorPois
  (`apply_panel_overrides_to_core.py` → core → bake); bake artifact shape (one
  `publish.geojson`); dev-time-only write (northstar V1); structural convergence (one
  collector, two renderers); store of record (`core.features`).
- **STILL OPEN:** (1) localStorage-as-durable-curation for the four **reference** layers
  (cemeteries/buildings/visitor/trails) — no author→DB ★ path exists; gold **slice 6, HELD**.
  (2) The user-visible flip itself — decision #1/#2 green-light.

### The executable next slice (council-corrected)

1. **Add `highlightable: true`** to cemeteries (2266) + buildings (2321) — Mason precondition.
2. Flip `listMode: 'wholesale'`→`'starred'` on cemeteries, buildings, visitorContext, trails.
3. **Published POIs stay wholesale** (the bake is their curation gate) — written guardrail;
   never retrofit `'starred'` onto the baked `layer==='poi'` union.
4. Render left-tab curation fields — largely already present (the `info needed — revisit`
   chip exists at main.js:1396; rows already carry blurb/status/kind/sourceChip).
5. **Tile-independent acceptance:** clone `playwright_verify_star_collector.py` — assert
   (a) `pubpoi:1`/`pubpoi:2` still render post-flip; (b) the four wholesale groups are empty
   in a clean profile.

### The blocking caveat the user must weigh

Even after the flip, **in the deployed read-only viewer** (no localStorage author session)
the four reference groups would be **permanently empty** — their ★ never reaches the bake.
So the flip delivers decision #2 (POI tab = curated set, starts empty) but **not** decision
#1/#5 *in production* for those four layers until an author→DB ★ path lands (gold slice 6).
For editorPois (drawn POIs) and the baked POIs, curation already travels end-to-end.

## Two user decisions (true forks — the legitimate stop)

- **(A) Ship the user-visible flip?** POI tab goes from ~20 unconditional rows to the curated
  starred set (empty until starred). Locked as decision #2 but held because it's user-visible.
- **(B) Scope of the flip given the durability gap?** Flip only the layers with a durable star
  path today (editorPois + baked POIs already work end-to-end), or also flip the four reference
  layers now as browser-local curation (empty in production until gold slice 6's author path
  lands), or build that author path first so #1/#5 are fully met before flipping.

## Resolution (same turn)

User picked **(B) "build the ★ path first, then flip"** — decisions #1 + #5 both met
before any visible change; nothing empty in production. A concrete **3-slice execution
plan** was written into the card ("## Execution plan — slices (ready to pull)"): Slice A
reference-layer ★ door (AUTHOR→STORE), Slice B ★ travels into the bake (STORE→SERVE),
Slice C flip + render (SERVE→view). Next gates are the user's: council the plan
(full six), commit-pause, ralph-loop in a fresh session.

## Records written this pass

- This receipt.
- `tasks/10_deferred/star_driven_poi_list.md` — readiness annotation at top; stale facts /
  dead paths fixed; directive sections annotated (not deleted).
- `handoff/session_context.md` — verdict entry.
