# Council review — Sprint 07 Slice 1 (`core.events` + DB-baked schedule) — FULL CLEAR

Date: 2026-06-07
Chair: Steward
Tier: full six (new table + new bake arm + a place_key model refinement = spine-level risk)
Under review: the Slice 1 diff — `mvp/init_db.sql` (core.events DDL), new
`mvp/scripts/import_event_schedule_to_core.py`, the schedule emit arm in
`mvp/scripts/export_publish_geojson.sh`, the `--baked` mode in
`mvp/scripts/playwright_verify_event_schedule.py` — plus the record (`tables_model.md`
Slice 1 ✅ DONE block + the handoff entry). DB state live for re-verification.

## Result: FULL CLEAR (all five worker seats `clear`, 1 round, no andons)

## Verdict receipts

```
SEAT: witness  — VERDICT: clear
Re-verified everything by observation, did NOT trust the producer. (1) Live DB: core.events=13,
core.features attrs?'event_location'=7 (6 layer='event' + annotated #pavilion). (2) Re-baked +
field-compared to HEAD: 13/13 sessions field-identical; locations identical except #pavilion gains
coordinates [-85.7482512,35.0907264] = the pavilion geom exactly (the intended gold delta). (3)
--baked verifier PASS, 0 errors, reads getSource(...).serialize() (tile-independent). ADVERSARIAL
ANTI-DEGRADATION TEST: swapped HEAD's coord-less schedule back in -> verifier FAILED (pavilion
coords=None) -> the green is genuinely bake-dependent, cannot baseline-pass. (4) publish.features
layer='event'=0. (5) import idempotent (13/13, 7/7; re-count 13 not 26). (6) fresh-volume repro: init_db
into throwaway DB exit 0, core.events + trigger + 4 indexes, no CHECK/FK on place_key/event_id. (7)
RESTORED served files; git status website/ clean; :8001 killed; no main.js change.
```

```
SEAT: warden  — VERDICT: clear
Every hunk traces to a card line (DDL -> :336-343; importer -> :344-347; bake emit arm same filename,
sibling not a REFERENCE_LAYERS entry -> :348-355; --baked verifier -> :360-369). No Slice 2 leak (grep
activity/core.activities across shipped code = 0; only forward-pointer prose in handoff). place_key
refinement is a faithful means-level change with the record intact (original card wording preserved at
:340, refinement annotated not deleted at :320-326) — matches the user's "tied to the place at the
#location tagged." Git gate untouched: HEAD is the user's plan commit 7543790; producer added no commit;
no shell asset changed -> no sw.js/#appVersion bump owed; git status website/ empty.
```

```
SEAT: quartermaster  — VERDICT: clear
Genuine reuse: import_event_schedule_to_core.py imports sql_str/sql_jsonb/run_psql/parse_count/REPO/
COMPOSE_FILE from import_layer_to_core_features.py — no SQL/psql logic re-implemented; event_location_attrs
genuinely new; point_geom_sql has a different signature than the panel-overrides one (not import-compatible).
Bake arm is a sibling block in the ONE writer (REFERENCE_LAYERS unchanged; writes the same served file the
viewer reads at main.js:8181). Verifier EXTENDED not forked (one playwright_verify_*event* file; reuses
wait_loaded + serialize). core.events is a genuinely new WHEN table, not a dup of core.features. main.js
untouched -> C1/C2/C6 grep state unchanged. (Note, separate card: the pre-existing
apply_panel_overrides_to_core.py re-implements those helpers — the file under review did NOT repeat that.)
```

```
SEAT: mason  — VERDICT: clear
Live \d core.events + pg_constraint: only PK, source_key UNIQUE (the upsert target), and the source_id
provenance FK (the established core.features pattern). NO FK, NO CHECK, NO enum, NO NOT NULL on
place_key/event_id — the 23503 throw-on-unmatched is absent. Importer adds/annotates, never drops/throws;
unknown session fields land in attrs (no allowlist); coordinate-less place stored geom NULL + notes flag;
asserts count==input, fails loud on a silent drop. Bake sessions arm is a plain SELECT with NO join (an
unresolvable place_key still emits its session — never dropped); verified live sessions_emitted=13.
jsonb_strip_nulls strips only keys HEAD omits (round-trip exact). Gate: publish.features layer='event'=0.
Minimal/idiomatic, no dead code, attrs.event_location not gold-plated, coords correctly not duplicated.
```

```
SEAT: scribe  — VERDICT: clear
Card ✅ DONE block states observed acceptance RESULTS (not "done"): 13/13 sessions, the intended pavilion
delta, --baked PASS specifics, gate=0, count==input, fresh-volume repro, served files restored; "the
commit is the user's git gate" stated. Handoff carries the same numbers; cross-checked against live DB
(events=13, places=7, publish event=0) — all match, no overclaim, no card/handoff contradiction. Model
refinement recorded honestly (card :320-326, handoff :59-61) with sound reconciliation. Owed items flagged
not buried (umbrella bake-config; editor-tag vs DB-tag convergence on gold slice 6). References accurate
(spot-checked import helpers, main.js:8181, getSource('event-schedule')). Voice is the user's plain register.
```

## Standing conditions (gold-inherited) — MET this slice
- **Witness** re-witnessed Slice 1's REAL verifier output (and adversarially proved it can't baseline-pass).
- **Mason** confirmed count==input against a live apply; no CHECK/enum/FK introduced.

## Owed (flagged, NOT this slice)
- Umbrella `event`/`schema`/`status`/`updated_at` wrapper is bake-config in `export_publish_geojson.sh`,
  not yet a DB row — gets a `core` home with event CRUD (deferred V2).
- The editor's localStorage `#tag` binding and the new DB `attrs.event_location` tag should converge
  (rides gold slice 6, HELD).
- (Quartermaster, separate card) `apply_panel_overrides_to_core.py` re-implements helpers it could import.

## Next
The user's git gate (commit). Then the loop's next iteration: **Slice 2 — `core.activities` +
`activity_key`** (ideally a fresh executor, per the gold producer-must-not-self-verify principle).

Resumable seat subagents: witness ae06d22a00f3d3448 · warden a00fe0c258ad801cd · quartermaster
a086c118e4951109d · mason ac3f66237c88581ed · scribe afe79ea487332ffeb.
