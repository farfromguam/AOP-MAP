# Sprint 06 — Going Gold

TL;DR:
- **The spine is `gold_migration.md`** — the user's 2026-06-06 decision: PostGIS `core`
  becomes the store of record, the bake is production, and the edit path is **preserved by
  redirecting it into the DB** (the web editor's existing export → `core`, not files). This
  ends the three-writer contention over `website/data/` that stalled every prior attempt.
  Sequenced into thin per-layer slices, each green before the next. **Slice 1 (POI author
  path) starts now.**
- **The rest of this sprint is the guardrails that protect that migration** — they came out
  of the council triage below and now serve the spine: the schema-conformance audit (proves
  each baked output holds the CMFS shape), verifier coverage, stale-verifier reconciliation,
  code-health cleanups, and the trail-review surfacing slice.
- The **fork list** at the bottom is the remaining held work. The authoring-surface fork is
  largely **answered** by the gold decision (all doors write `core`, dev-time, editor preserved).

#aop #sprint #06 #gold #postgis #bake #council #verify

-----

## Spine status — gold migration COMPLETE (2026-06-07)

`gold_migration.md` (the spine) is fully landed. Slices 1–5 + the Retirement step closed and
council-cleared (committed `ce920bd`, `737fc26`); on **2026-06-07** the user pulled the last item the
ralph loop held back for a human — the deprecated `core.pois` table + `publish.pois` view were
**drop-tested (rename-and-reverify) and dropped** from both the live DB and `mvp/init_db.sql`, with
fresh-volume reproducibility re-proven. `core.features` (141 rows) is now the sole POI/feature table; the
bake serves POIs from `publish.features WHERE layer='poi'`. NO shell asset touched → no version bump owed.
See the **DROP COMPLETE** block in `gold_migration.md`.

**Still open (this did NOT close them):** Slice 6 (HELD — demote the `aop-*` localStorage stores to working
buffers), the per-layer **legacy-writer retirement** (OWED), and the **entire guardrail slate (items 1–5
below) is unstarted**. So the sprint's *spine* is done; the *slate* is not — Sprint 06 stays open for the
guardrails and the held forks.

-----

## How the guardrail slate was chosen (council triage, 2026-06-06)

Steward chaired; each seat scored its lens over the 16 deferred cards (see
`brain/council/triage.md`). The findings that shaped the slate:

- **Witness (verifiable?):** only work with a tile-independent, observable
  acceptance was pulled. The two `sprint05_*_on_device` cards and
  `extend_9patch_imagery` are **not headless-observable** → they stay human-checked
  owed items, not swarm cards. `pwa_qa_data_bakes` was **re-confirmed done by
  observation** and closed to `_done/`.
- **Warden (bounded?):** `viewer_polish_followups` and `poi_editor_followups` are
  grab-bags → **reshaped**: only specific bounded items pulled, not the whole card.
- **Quartermaster (reduces duplication?):** the code-health shared-helper
  extractions (`loadObjectStore`, `clampRound`/`trimZeros`, roads config,
  `forEachTile`) score **up** — they collapse dup. Caught a likely dup trap: the old
  "wire `sfwda_numbered_trails.geojson`" item is **superseded** by the served
  `aop_trail_network.geojson` — do **not** wire a second trail surface (see item 4).
- **Mason (limiting code?):** any search/visibility gating stays **display-scope, not
  data-rejecting** (`no_limiting_code_mvp`) — note attached to the trail slice.
- **Steward (northstar now?):** the northstar is *trustworthy map before app*, so the
  trail-review slice (moves real trail data toward publishable) outranks pure
  hygiene; event/upload work is explicitly northstar-**deferred** (V2) and stays held.

### Swarm shape

Items **1** (new verifier files) and **5** (the new audit script) are
**parallel-safe** (distinct new files, touch no hot shared file). Items **2/3/4** all
touch the hot shared files (`website/index.html`, `website/js/main.js`, the verifiers)
and are **sequential** — queue them, do not run concurrently in the same checkout (the
Sprint-05 lesson: nearly everything touches `main.js`). If two agents must move at
once, isolate in a worktree (`ai_rules/feedback_work_in_worktree`).

-----

## Sprint 06 slate — PULL, in order

### 1. Verifier coverage — add the three missing verifiers  · parallel-safe
**From:** `viewer_polish_followups.md` (POI Browser, Right Panel) + `poi_editor_followups.md`.
**Why now (Steward):** coverage gaps let regressions slip silently; the cheapest
trust insurance. **Observable (Witness):** the verifier passing *is* the acceptance.
**Quartermaster:** new coverage, no new product surface. **Warden:** bounded — three
named scripts.

Plan:
- `mvp/scripts/playwright_verify_left_poi_browser.py` — placeholder chip count,
  click-row fly, popup HTML, source-layer auto-enable.
- `mvp/scripts/playwright_verify_right_panel_consistency.py` — every Publishable
  editor row carries its expand control; each exportable section header carries `⧉`;
  panel header carries global `⧉ Export all`.
- POI star-to-visitor verifier — draw POI → absent from POI tab → star → present →
  reload → still present → unstar → absent. (May extend the existing
  `playwright_verify_poi_editor.py` rather than add a file — decide at build time.)

Checklist:
- [ ] `playwright_verify_left_poi_browser.py` written + PASS on `:8001`, 0 console errors.
- [ ] `playwright_verify_right_panel_consistency.py` written + PASS, 0 console errors.
- [ ] Star-to-visitor path covered + PASS.
- [ ] Each new verifier registered wherever the suite is listed; runs from a clean serve.

### 2. Stale-verifier reconciliation — `publishable` section + `presets` rot  · sequential
**From:** `viewer_polish_followups.md` (Right Panel + Code-review residue blocks).
**Why now (Steward):** these are *known-failing* assertions masking real signal — they
make the suite lie. **Witness:** observable (the suite goes green or documents why).
**Warden:** one decision-gated sub-part — surface a recommendation, don't guess.

Plan:
- The 3 `data-section="publishable"` assertions fail because that section no longer
  exists (the editor unified-tree rework moved those toggles into `data-section="editor"`).
  **Decision (route to user, recommend):** *rewrite the assertions to read from
  `editor` and document that "publishable" is no longer a separate UI surface* —
  cheaper than re-introducing a section that the redesign deliberately removed.
- `presets` verifier: route its second panel-interior raw click through the JS-dispatch
  helper (mirror the line-387 pattern already in the file); then re-check the
  "Topo restyles index contours" assertion fresh (it was never being *reached* before).

Checklist:
- [ ] User's call on publishable-section: **rewrite assertions** (recommended) vs reintroduce section.
- [ ] `playwright_verify_feature_list.py` publishable assertions resolved (no stale FAIL).
- [ ] `presets` verifier runs to completion (no mid-run click crash); remaining FAILs each have a named cause.
- [ ] Suite re-run; the only documented FAILs are intentional/decision-gated, listed in the card.

### 3. Code-health cleanups  · sequential (hot files — queue)
**From:** `viewer_polish_followups.md` (Code Health + code-review residue) +
`poi_editor_followups.md` (S3 items).
**Why now (Quartermaster/Mason):** dedup + clean diffs; no behavior change.
**Warden:** each is a stand-alone bite — do **not** ride along with semantic changes.

Plan:
- **L1 whitespace** — convert the ~88 leading-tab lines in space-indented
  `website/index.html` to spaces matching surrounding indent. Whitespace-only pass.
- **`setEditorFeatureNotes` trim** (`index.html` ~3871) — decide whitespace-only notes:
  `String(value).trim()` gate (recommended) vs preserve; either way drop the misleading
  `trimmed` name.
- **L2 shared-helper extractions** (deferred subset) — `loadObjectStore` (3 identical
  wrappers), `clampRound`/`trimZeros`, the roads config array (~10 near-identical
  `addLayer` objects), `forEachTile` (3 reimpls). Skip the risky ~250-line
  `buildFeatureRow` unless M5's in-place path is coordinated.
- Document the Reset-reseed `seed_tag` migration behavior in
  `spinup/viewer_storage_migration.md` (poi_editor S3 item — explains the lost re-bind).

Checklist:
- [ ] L1: `grep -nP '^\t' website/index.html` returns 0; `node -c` clean; verifiers stay green.
- [ ] `setEditorFeatureNotes` renamed + trim decision applied; persistence verified by observation.
- [ ] At least the low-risk L2 helpers extracted; `node -c` clean; behavior unchanged (verifiers PASS).
- [ ] Reset-reseed behavior documented.
- [ ] NOTE for the user: a VERSION bump is **owed** if a shell asset (`index.html`/`js/*.js`/css/`sw.js`) changed — the user owns the bump + commit (`no_commits.md`); the loop reports it, never performs it.

### 4. Trail-review surfacing slice  · sequential
**From:** `paper_map_trail_extraction.md` ("Still open").
**Why now (Steward):** the served `aop_trail_network.geojson` (120 features) is the
northstar's real-trail spine; the **promotion to publish is gated on a human review
pass**, and the data the human needs (`review_flags`, dangling ends, grey/unrated,
the blue-circle "1") is computed into `_meta` but **not surfaced**. Surfacing it
unblocks the user's pass. **Quartermaster:** do **not** wire `sfwda_numbered_trails.geojson`
— it is superseded by `aop_trail_network.geojson`; that old open item is now void.
**Mason:** any difficulty/road filtering stays display-scope, not data-rejecting.

Plan:
- Surface the gold `_meta.review_flags` (band-vs-colour disagreements — this run:
  trails 35/1/95/47), the **3 dangling ends** snap/trim won't close at 18 m, the
  **22 grey/unrated** trails, and the **blue-circle "1"** band-flag, in a review
  artifact (a `brain/output/` review page or an in-app review affordance) so the user
  can make the calls the card lists as theirs.
- Do **not** promote to `publish` here — promotion routes through
  `northstar/source_register.md` after the user's review (held, see forks).

Checklist:
- [ ] `review_flags` + dangling + grey + blue-1 surfaced where the user can act on them.
- [ ] Confirmed by observation (the served network still renders; review surface lists the right counts).
- [ ] `playwright_verify_sfwda_trace.py` still PASS.
- [ ] No second trail surface introduced (`sfwda_numbered_trails` stays unwired).

### 5. Schema-conformance audit — make the CMFS contract self-verifying  · parallel-safe
**From:** council consult 2026-06-06 (schema / type-system fork). Card:
`schema_conformance_audit.md`.
**Why now (Steward):** answers the user's "too many schemas" pain the right way — the
one-shape contract (CMFS, `_schema.json`) already ships; what's missing is a **receipt**
that proves conformance. **Witness/C4:** read-only, tile-independent; the receipt is the
acceptance — and a hand-run already caught real drift (`aop_user_features.geojson` is on
disk but missing from the manifest). **Mason/C5:** the audit **reports**, never rejects —
no CHECK/enum/filter. **Quartermaster:** reads the existing `_schema.json`, builds no
second schema surface.

Checklist:
- [ ] `mvp/scripts/audit_canonical_schema.py --check` written, read-only, edits nothing.
- [ ] Reports Tier-1 (`id`+`kind`), per-file CMFS coverage, and manifest coverage.
- [ ] Known drift (`aop_user_features.geojson`) resolved or noted.
- [ ] Mason re-check: no limiting construct introduced (grep clean).
- [ ] See the card for full acceptance.

-----

## HOLD — gated, with the unblock condition

Not pulled into Sprint 06. Each names what would let it move.

**User-decision forks (cheap — recommendation attached):**
- `calendar_placeholder_state.md` — pick 1 of 4 mockups; then a ~15-min wire into
  `index.html`. *Recommend:* V1 skeleton (matches the calendar-card tokens best).
- `park_bounds_icon_apply.md` — pick `PB1`–`PB9`; then a ~5-min inline-SVG swap.
- `brand_assets_and_permissions.md` — settle the brand-use **permission posture**;
  reconcile the live default-on (`showBrandLogos:true`) with the card's old
  default-off promise. *Recommend:* confirm permission is in hand → retire the
  off-by-default safeguard, then do the asset cleanup.
- `star_driven_poi_list.md` — pick the **authoring surface** (web-writes-DB / QGIS
  authors / both). Unblocks the AUTHOR half of the one POI pipeline.

**Scoping conversation:**
- `event_crud_upload_loop.md` — answer the 6 forks (invite-codes vs accounts;
  moderator; R2 vs S3; photos publishable?; GPX timestamps; QGIS-review mandatory?)
  + a storage baseline. The sprint's main *future* thrust (northstar V2).
- `dev_db_snapshot_reseed.md` — wants a stable `core` schema first; rides on the
  `star_driven` authoring pick.

**External truth:**
- `rock_warblers_content_audit.md` — Rock Warblers confirm real event details.
- `data_integrity_publishability.md` — real trails ride on the trail-promotion review
  pass (item 4 above); acreage reconciliation; DEM upgrade. Partially unblocks as the
  trail review lands.

**Human / on-device / data-acquisition (owed, not swarm cards):**
- `sprint05_buildings_dock_on_device.md` — ~30-s live pixel check; needs tiles + the git gate.
- `sprint05_on_device_smoke.md` — iOS-PWA feel pass for the v52 refactor; needs a device + the git gate.
- `extend_9patch_imagery.md` — owner "how much bigger" + imagery/terrain re-acquisition.
- `offline_pwa.md` — measure/reduce/document; wants a stable layer set first (the PWA
  install itself already ships).

**The git gate (precondition for the two sprint05 cards):** commit + the v52 bump are
the user's (`ai_rules/no_commits.md`). This sprint does not commit.

-----

## Done → moved to `../10_deferred/_done/`

- `pwa_qa_data_bakes.md` — items 4/6/E DONE + re-confirmed by observation; Item 17
  split to `../10_deferred/extend_9patch_imagery.md`.

## Lifecycle

Cards pull *into* this sprint from `../10_deferred/` by getting a real scope +
acceptance (above). A held fork that the user resolves promotes its card here. The
user owns the trigger to start the swarm and the git gate; the council proposed this
slate, it does not auto-start (`stay_on_the_farm`).
