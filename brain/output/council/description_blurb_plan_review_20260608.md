# Council receipt — description→`description` convergence PLAN review

Date: 20260608. Steward-chaired. Refuting seats: Mason · Witness · Warden · Quartermaster
(fresh adversarial subagents over the card, not the diagnosis). Card:
`brain/tasks/07_tables/description_blurb_convergence.md`. Diagnosis receipt:
`description_blurb_flow_review_20260608.md`.

## Verdict: CLEARED with all conditions folded into the card.

The approach (rename the DB column, source-data convergence) is the user's directed choice and was
NOT relitigated. Slice 1 is CLEAR by every seat and is independently safe/reversible. All andons were
acceptance-rigor or disposition fixes, now in the card.

- **Mason — CLEAR (2 notes folded):** `pg_get_viewdef` confirms `publish.features` is the ONLY object
  depending on `core.features.blurb` (pg_depend walk; no other view/matview/index/CHECK/generated
  col/trigger references it). `ALTER RENAME COLUMN` is metadata-only — C5 holds, no row dropped.
  Blast-radius list complete for the column; added `rebake_canonical.py` DESC_KEYS as crosswalk-exempt.
  Added the load-bearing Slice-2→3 invariant (a `description`-only served file blanks subtitles until
  the viewer cuts over).
- **Witness — Slice 1 CLEAR; Slices 2/3/4 andon → folded:** acceptance must assert VALUE not presence.
  S2 value-equality (baked `description`==DB by id) + `blurb` absent; S3 positive subtitle substring
  (`"campfire all happen here"`, `--require-description` gated, absence fails); S4 compare seed-vs-DB
  (not popup — two client features; unify = OUT gold slice 6) on FRESH localStorage. S1: count is a
  sanity line, the proof is `\d` + fresh-volume repro (3 POI rows, not live's 4).
- **Warden — 4 axes CLEAR; Slice 4 disposition andon → folded:** scope on-the-farm (OUT list honored),
  git gate intact (no commits; bump isolated to S3, owed-to-user), rename is the user's directed
  source-data fix (no re-confirm gate owed), reversibility adequate (pg_dump + txn). Slice 4 seed file
  is precached (`sw.js:92`) — added its disposition (rides Slice 3's bump / restore-to-HEAD).
- **Quartermaster — CLEAR (1 owed folded):** C1/C2/C6 greps clean; verifiers reused not reinvented;
  sidecar correctly deferred; one column (no pair), `core.activities.description` distinct. Owed:
  `rebake_canonical.py:119` already produces the seed file from `raw/` — Slice 4 must make the DB arm
  the SOLE producer (folded).

## Standing conditions the loop inherits
- Producer must not self-verify: re-witness each slice's REAL acceptance output (the gold principle).
- Serve the `description`-only bake ONLY at/after Slice 3; HEAD (dual-key) bridges S1→S3.
- External-source ingest crosswalks (`BLURB_KEYS`, `DESC_KEYS`) STAY; only our-own-data crutches go.

Seats resumable: Mason a92c0c32667a38ac4 · Witness a390148b37e0d0d47 · Warden a26398c1c4a004dd0 ·
Quartermaster a8594c8a9ec719bda.
