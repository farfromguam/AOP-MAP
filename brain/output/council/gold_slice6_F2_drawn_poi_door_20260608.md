# Council done-review — Gold slice 6 / F2: the drawn-POI DB door

Date: 2026-06-08. Chair: Steward. Tier: **full six** (gold DB-door work; the user's "no shortcuts" mandate).
Trigger: the user PULLED gold slice 6 (held "until a human pulls it") after Sprint 09 Slices 1–4.

**Goal:** close spike-audit F2 — hand-drawn POIs (`aop_editor_pois_v1`) had no direct DB door (they reached
`core.features` only via the panel's opt-in `created[]` export, so a drawn POI vanished on browser reset and
never published). Make `core.features (layer='poi')` the store of record for drawn POIs.

## Scope (bounded — the DB door only)
Executed: **F2** (drawn-POI → core door). NOT executed (separate, higher-risk, surfaced to the user): F1
(geometry/icon_size → core), F4 (re-bake `publish.geojson` = the git gate), F5 (fresh-volume parity), F6
(identity-fork collapse, "highest risk, do last").

## Diff
- new `mvp/scripts/apply_editor_pois_to_core.py` — the door: a thin INPUT ADAPTER mapping the drawn-POI
  FeatureCollection (`aop_editor_pois_v1` / "Copy all as GeoJSON") to the panel-overrides `created[]` shape
  (`_src='editorPois'` → `source_key='editorPois:<id>'`, the seed convention) and feeding the EXISTING
  `apply_panel_overrides_to_core` sink (`build_sql`/`run_psql`) — one sink, no duplicated upsert/provenance.
- new `mvp/scripts/verify_editor_poi_db_door.py` — browserless verifier (the gold "baked-file assertion").
- folded (Mason andon): `mvp/scripts/panel_overrides.py` — new `safe_geometry()` guards
  `build_created_feature` so null/partial/unparseable geometry upserts geom-less instead of throwing (R13);
  behavior-preserving for well-formed geometry (identical dict).

## Verdicts — FULL SIX CLEAR (1 round + 1 Mason andon-bounce)

**witness — clear.** Ran `verify_editor_poi_db_door.py` (DB up), all checks PASS, independently
re-observed the real system: both POIs land active in `core.features` (survives reset = in DB); the
publishable one (permission/publish_status='publish') reaches the baked `publish.geojson`; the candidate is
gated out by the real `publish.features` view; idempotent re-apply (count unchanged); cleanup restores
served files byte-identical to HEAD (sha equal) with zero DB residue; website/ git-clean. Confirmed (not
andon'd) that the slice-1 `playwright_verify_baked_pois_author.py` failure (`names=[]`) is PRE-EXISTING —
the committed star-only flip removed the `published_destinations` group it reads (`grep -c` = 0 in main.js);
F2 touches only `mvp/scripts`, so it is not an F2 regression.

**mason — andon → re-review clear.** ANDON: a drawn POI with `geometry:null` / partial geometry made
`build_created_feature` (panel_overrides.py) THROW and abort the whole batch — contradicting the door's
no-throw/no-drop docstring; `aop_editor_pois_v1` is a hand-draw store where that is realistic. FOLDED:
`safe_geometry()` guards the build (null/partial/unparseable → geom-less, never throws), the docstring made
accurate, a `geometry:null` POI added to the verifier. RE-REVIEW: clear — verified `safe_geometry` returns
the identical dict for well-formed geometry (file-baker output unchanged), `None` (no exception) for the
three throw cases; the verifier's null-geom check PASSes (geom-less, not dropped); the full 3-feature batch
upserts 3/3 with no abort; no new limiting code.

**quartermaster — clear.** `apply_editor_pois_to_core.py` is a thin input adapter — imports
`build_sql`/`run_psql`/`parse_count`, redefines none of the upsert/provenance/no-drop logic, emits no
`INSERT INTO core`/`ON CONFLICT`/`source_register` SQL of its own. No second store of record (live rows are
all `editorPois:<id>`, the seed convention). The third apply script is justified by a genuinely distinct
INPUT shape (the editor's own draw store vs the panel OVERRIDES export vs the positioned-features map) —
`apply_positioned_features_to_core.py` explicitly reserved "editorPois has its own DB door." Verifier reuses
the bake + read-only `git show HEAD:` restore (the gold slice-runner pattern). C1/C2/C6 greps at target.

**warden — clear.** Bounded to F2 (no F4/F5/F6, no production file committed). NO shell asset touched
(`mvp/scripts`-only) → NO `sw.js`/`#appVersion` bump owed. Git gate untouched: every git verb in the diff is
read-only (`status`/`show`); HEAD is the user's own `5e576d9 "v59"` (the committed Sprint 09 batch), which
does not contain the F2 scripts; F2 is the two untracked files. The production script has NO `DELETE FROM
core` (the verifier's test-row cleanup is its own scaffolding, the established gold pattern). Served files
restored byte-identical to HEAD.

**steward (cross-check) — clear.** Serves the gold promise — a drawn POI now has `core.features` as its
store of record (survives reset) and publishes ONLY through the gate (a candidate does not leak); source-led
(provenance via the `source_register` 'AOP web editor (apply)' row; true permission/publish_status travel,
not coerced). Correct bounded scope; dev-time apply + bake only (northstar V1). F4/F5 remain open
(out of F2 scope) — surfaced.

**scribe — (Steward-written records).** Records landed: this receipt; the gold_migration.md slice-6 PULLED +
F2-done annotation; the Sprint 09 card Slice-5 F2 note; the handoff entry. References (the spike audit F2,
the two-sink split, the seed `editorPois:` convention) treated as the real things.

## Result
Gate CLEARED for F2. `core.features (layer='poi')` is now the store of record for drawn POIs; the door is
idempotent, no-throw, no-drop; production untouched. **OWED (the user's git gate):** the commit (the two new
`mvp/scripts` files + the `panel_overrides.py` guard + brain) — NO version bump (no shell asset). **Remaining
gold slice 6 (HELD / the user's call):** F1 (geometry/icon_size door), F4 (re-bake `publish.geojson`), F5
(fresh-volume parity), F6 (identity collapse).
