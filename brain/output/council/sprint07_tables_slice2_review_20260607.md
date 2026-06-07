# Council review — Sprint 07 Slice 2 (`core.activities` + `activity_key`) — FULL CLEAR

Date: 2026-06-07
Chair: Steward
Tier: full six (new table + de-dup backfill + bake change = spine-level risk)
Under review: the Slice 2 additions — `core.activities` DDL + `core.events.activity_key`
(`mvp/init_db.sql` + live DB), the `SESSION_ACTIVITY`/`ACTIVITIES` backfill + activity upsert
in `mvp/scripts/import_event_schedule_to_core.py`, the resolved `activity` object in the bake's
session arm (`mvp/scripts/export_publish_geojson.sh`), and the record (`tables_model.md` Slice 2
✅ DONE + handoff). DB live for re-verification.

## Result: FULL CLEAR (all five worker seats `clear`)

Round 1: Witness · Mason · Quartermaster `clear`. Warden · Scribe `andon` — both on the SAME
axis (served files observed dirty vs the record's "restored byte-identical to HEAD").
Round 2 (re-review): Warden · Scribe `clear` — the andon was a **concurrency race**, not a real
breach (see below).

## The andon and its resolution (a process finding)

The Witness seat re-bakes the served files as part of its de-dup proof and restores them only at
the END of its run. It was spawned CONCURRENTLY with the read-only Warden/Scribe, which sampled
`git status` DURING the Witness's transient re-bake window and saw the served files dirty. The
tree was clean at council-spawn and clean again after the Witness restored. Re-review with no
mutation running: Warden confirmed `cksum 2525292041 8937` identical for HEAD vs the served
schedule (byte-identical, not just field-equivalent); Scribe confirmed `git diff HEAD -- website/`
empty. The record's "restored byte-identical to HEAD" describes the durable resting state (what
the git gate sees) and is TRUE.

**Lesson (recorded):** run a mutating verifier (the Witness re-bakes) ALONE, not concurrently
with seats that assert on working-tree cleanliness. Next slice: sequence the Witness first, or
have it work against a copy.

## Verdict receipts

```
SEAT: witness — VERDICT: clear
DB: core.activities=12, all 13 core.events have activity_key, night_crawl cited by exactly 2
(fri+sat night-crawl), all others by 1. DE-DUP PROOF (ran it): UPDATE night_crawl description ONCE ->
re-bake -> BOTH fri-night-crawl + sat-night-crawl carried 'WITNESS-CHECK', fri-driver-meeting +
sat-awards did NOT -> restored. Session-level fields field-identical to HEAD; every session carries
activity{key,name}. import idempotent (re-run still 12 activities, not 24). --baked verifier PASS (20
features, 13 sessions, pavilion resolves, 0 errors). Fresh-volume: core.activities + events.activity_key
present, no FK on activity_key. Restored 6 served files; git status website/ clean; :8001 killed.
```

```
SEAT: mason — VERDICT: clear
Live \d: activity_key/name/kind nullable text, no CHECK/enum; only FK is source_id provenance; catalog
fk_on_event_softrefs=0, checks=0 -> no 23503 throw. Bake is LEFT JOIN (unmatched key keeps its session,
emits {key}); FROM core.events WHERE archived_at IS NULL. ON CONFLICT DO UPDATE SET name,kind ONLY --
description/attrs EXCLUDED so a re-import never clobbers user-authored content (the subtle one, confirmed).
12 activities/13 sessions, night_crawl x2 = faithful de-dup not gold-plating. jsonb_strip_nulls drops only
absent fields; key always present. No dead code, idiomatic to the gold importer.
```

```
SEAT: quartermaster — VERDICT: clear
Extended the existing slice-1 importer (no parallel activities script; ls confirms none). activity object
added INSIDE the one session-arm query via LEFT JOIN -- one bake, one writer, same served filename.
core.activities is distinct (no geom/place column), not a core.features dup. main.js untouched -> C1/C2/C6
grep state unchanged. Activities upsert reuses sql_str/src_subq, no re-implemented SQL building.
```

```
SEAT: warden — VERDICT: clear (round 2)
R1 andon: served files dirty vs the restore claim. R2 (no mutation running): git status --porcelain
website/ empty; cksum HEAD==served (2525292041 8937, byte-identical); git diff --stat website/ empty ->
restore claim holds. Affirmed throughout: HEAD still 7543790 (no producer commit); no shell asset changed
(no bump owed); every Slice 2 hunk traces to the card; the night_crawl-only collapse + un-merged
registration sessions are a faithful backfill not content invention; deferring the viewer-render is
legitimate thin-slicing (would force a main.js change + bump), correctly named OWED.
```

```
SEAT: scribe — VERDICT: clear (round 2)
R1 andon: record claimed "restored byte-identical to HEAD" while tree showed 6 modified served files. R2:
git status website/ empty, served schedule activity-count 0 == HEAD 0, git diff HEAD website/ empty -> the
claim is true of the current durable resting state (the git-gate view). Affirmed in R1: DB facts (12/13/13),
no-FK, night_crawl-only collapse, registration NOT merged, eventScheduleToGeojson OWED honestly flagged at
main.js:6280, references accurate, voice plain.
```

## Standing conditions (gold-inherited) — MET
- Witness re-witnessed the de-dup proof on its own re-bake (one row -> N occurrences, control untouched).
- Mason confirmed count==input live; no CHECK/enum/FK; the ON CONFLICT non-clobber is correct.

## Owed (flagged, NOT this slice)
- Viewer RENDERING of activity detail (`eventScheduleToGeojson` carry-through + a `main.js` change + a
  shell bump) — a UI slice, deferred.
- The activities' "specific data" (grade/length/gate list) is the user's to author into `core.activities`.

## Next
The user's git gate (commit). Sprint 07's migration SPINE (Slices 1+2) is complete; Slice 3 (place-attached
abouts = feature bodies) is not a DDL slice. Only the flagged UI/content follow-ups remain.

Resumable seats: witness a45a401328a62f4c9 · warden(r2) ad6b2e311edd7e274 · quartermaster a5be3b4b36e4b70fd
· mason ab35bca9a809ab65c · scribe(r2) aae7bb56e1fe8b981.
