# Sprint 08 — Data Normalization

TL;DR:
- **The spine is `star_driven_poi_normalization.md`** — normalize curation across ALL
  destination layers into the one `core.features`-backed pipeline, then flip the POI tab to
  the curated ★ set (star_driven decisions #1/#2/#5). Three thin slices along the existing
  AUTHOR→STORE→BAKE→SERVE pipeline.
- This **executes a scoped piece of gold slice 6** (HELD in
  `../../06_going_gold/gold_migration.md`): demote the four reference layers' ★ from per-browser
  localStorage to a durable `core.features` attribute that bakes into the served artifact.
  Scoped to the **curation/star axis** — not the whole localStorage→buffer convergence.
- **Design source (the why):** `../10_deferred/star_driven_poi_list.md` (the feeling-out doc
  + the 2026-06-08 full-six council readiness verdict) and the receipt
  `../../../output/council/star_driven_poi_list_consult_20260608.md`. This sprint is the
  execution; that card is the rationale.

#aop #sprint #08 #normalization #star #poi #core_features #bake

-----

## Why this is a sprint, not a one-line flip

The council consult (2026-06-08) found the POI-list **structural** work already shipped (one
collector, gold store, one bake). The only remaining step — flipping the POI tab to the
curated ★ set — hits a **durability gap**: the four reference layers
(buildings/cemeteries/visitor/trails) have no path for their ★ to reach the bake, so a naive
flip leaves those groups permanently empty in the deployed read-only viewer. The user chose
to **build the ★ path first, then flip** — decisions #1 (★ governs all destination layers) +
#5 (curation travels into the bake) both met before anything visible changes. That ★ path is
the normalization: the four reference layers' curation joins POIs in the same shape.

## The spine card

`star_driven_poi_normalization.md` — the 3-slice plan, council-corrected, with a
tile-independent observable acceptance per slice and the loop contract.

**✅ COMPLETE (2026-06-08).** Plan committed (`c781f59`), then all 3 slices ralph-looped + verified
by observation in a fresh session; **full-six council done-review CLEAR** (receipt:
`../../../output/council/sprint08_done_review_20260608.md`). The card holds the EXECUTION RECORD. The
spine card stays in this dir (not moved to `_done/`) to preserve its inbound links — the EXECUTION
RECORD + DONE banner are the acceptance result. **OWED (user's git gate):** the commit (main.js +
`sw.js` + `index.html` + `apply_positioned_features_to_core.py` +
`playwright_verify_starred_poi_flip.py` + brain records). Production ★ curation is the user's to author.

**⚠️ Post-clearance correction:** the card's "v53→v54 bump" was stale — HEAD already carried v54, so
the flip didn't reach installed browsers (cached pre-flip code = the unstarred-trail-showing bug the
user caught). Fixed by bumping **v54→v55**; new code confirmed to gate correctly. See the card's
VERSION-BUMP CORRECTION block.

## Relationship to the rest of the brain

- **Gold slice 6** (`../../06_going_gold/gold_migration.md`, HELD): Sprint 08 executes the
  curation-axis slice of it. The broader localStorage→working-buffer convergence stays held
  there; this sprint takes only the ★ / `is_destination` flag for the four reference layers.
- **The editor contracts** (`../../../northstar/editor_architecture_contracts.md`): the flip
  stays non-limiting (**C5**) — the ★ gate reads an authored attribute, never rejects an
  unknown value; the published `layer='poi'` union stays bake-curated, never `'starred'`.
- **The source register** (`../../../northstar/source_register.md`): the ★ is a curation
  attribute that travels raw→core→publish; this sprint makes that literally true for the
  four reference layers.
