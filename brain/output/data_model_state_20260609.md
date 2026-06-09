# Data-model state report — where we are, what still smells, what's next

> Written 2026-06-09 (cwc session) at the user's ask: *"review our last many sessions and my
> frustration with our data model. make a report on where we are and what the data smells still
> exist. figure out what our next steps are."* Synthesizes the shadow-attribute audit
> (`tasks/09_editor_maturity/shadow_attributes_audit.md`, 45 findings), the resolution loop
> (`shadow_attribute_resolution.md`, Path A done), the CMFS (`research/common_feature_schema.md`),
> and the gold migration (`tasks/06_going_gold/gold_migration.md`, slices 1–5 + retirement done,
> slice 6 held). Point-in-time; the cards stay the source of truth.

#aop #data_model #shadow_attributes #gold #report #cmfs

-----

## TL;DR

The data model is **half-migrated, and the two halves have diverged on purpose.** The DB (`core.features`)
is the new store of record and the *served files* are now genuinely canonical — but the bake that connects
them is **not yet a pure function**, so the served truth and the DB truth are kept in sync by hand. That gap
is the whole of what still smells. Concretely:

- **Done:** the DB collapse (gold slices 1–5 + retirement) and the served-file canonicalization
  (shadow Path A, A1–A5). **22 of the 45 audited smells are closed**, all council-cleared, now shipped under
  `v60`.
- **Still smelling:** **20 findings**, all of them the same three structural roots — *localStorage is the
  published truth*, *publish.geojson can't be rebuilt from the DB*, and *there is no one identity key per
  real feature*. These are exactly gold slice 6's held doors (F1/F4/F5/F6).
- **The seam:** Path A made the served files read right; it did **not** make the DB able to *reproduce* them.
  Closing that seam is the next body of work.

## What you were actually frustrated about (your words)

- The **Launchpad trail**: one trail showing four names across four surfaces — "Launchpad" (left list),
  "Trail 1" (right panel), "1" (map label), unsearchable as Launchpad. You named the class a **shadow
  attribute**: *"something driving logic that is not apparent… this is slop. find all places where logic is
  driven in a weird edge-case way, or an MVP shortcut that needs maturing out."*
- The **shape mismatch**: *"I should be able to edit a trail description the same way I edit the pavilion
  text, because the schema is similar and the editor is consistent."* The renderer was already one renderer;
  the **data underneath named the same concept a different way in every file.**
- The **three-writers** problem: *"three masters → every 'go to the DB' attempt fought the file edits or got
  abandoned to preserve them."* Served files had three competing writers (`rebake_canonical.py` from `raw/`,
  `bake_panel_overrides.py` from browser edits, `export_publish_geojson.sh` from the DB) with a fragile
  ordering dependency.

All three are the same root feeling: **what you see ≠ what you edit ≠ what publishes**, because the truth was
never one apparent field on one feature in one store.

## What is now fixed

**The DB collapse — gold slices 1–5 + retirement (done 2026-06-06/07).** All five feature layers (POIs,
buildings, cemeteries, visitor callouts, trails) live in ONE `core.features` table: CMFS spine columns
(`id`/`name`/`description`/`kind` + provenance) + JSONB `attrs`, plus `source_key UNIQUE` and `archived_at`.
`publish.*` views gate on `permission='publish' AND publish_status='publish' AND archived_at IS NULL`.
`core.pois` was collapsed into `core.features (layer='poi')` and dropped. The drawn-POI DB door (slice 6 F2)
shipped 2026-06-08 — a drawn POI now survives a browser reset.

**The served-file canonicalization — shadow Path A, A1–A5 (done + council-cleared 2026-06-09, shipped v60).**
22 of the 45 smells closed:
- **A1** — `rebake_canonical.py` now *folds the sidecars into the bake*: trail catalog → `name`/`description`/
  `facets.difficulty`; poi-index → building/cemetery/visitor `description`. Added a Tier-3 `facets` block,
  moved building facility-role out of `status`, fixed the maturity-stamp wipe + stale manifest. The served
  data carries real canonical fields now, additively (originals preserved under `_original`).
- **A2** — the runtime `trailCatalogLookup` join is **deleted**; every trail surface reads the one baked
  `name`. The four-surface fork is closed (left == right == map == search == "Launchpad").
- **A3** — the `poiIndexLookup` cross-layer blurb join is **deleted**; building name is the facility name
  ("Pavilion"), address demoted to a facet.
- **A4** — one `poiDisplayName` helper; kind chips + source-file + confidence/status all read baked/declared
  values (additive display maps, never reject).
- **A5** — five per-layer edge-dispatch call sites converged onto declarative spec capabilities (C1).

Net: the **render-time shadows are gone** — no more sidecar joins, render-derivations, or `layerKey ===`
branches supplying display values. The served files are the canonical truth and the editor reads one field.

## What still smells — the 20 held findings, three roots

These are **Path B = gold slice 6's remaining doors (F1/F4/F5/F6)**. The shadow audit enumerated them at
finding-granularity; the gold card bounds them as doors into `core`. Same work.

### Root 1 — localStorage is the published truth (C3 violation) · 7 findings · F1
The "published" reference map **is** the editing browser's `aop_panel_overrides_v1` + `aop_positioned_features_v1`
diff, replayed onto the served files at boot. **Two browsers see different data.** Worse, the same name edit
forks to two different stores with **opposite bake fate** depending on which surface made it: a left-dock
rename is browser-local forever; a right-panel rename of the identical feature bakes to the DB. Stars, tags,
and per-feature visibility filters are all per-browser curation with no store of record.
- `served-features-edited-props-localstorage-only-no-db-door` · `name-edit-two-store-fork-by-surface` ·
  `panel-overrides-replayed-as-published-view` · `highlight-two-store-by-surface` ·
  `feature-visibility-paint-filter-as-curation` · `visitor-file-two-kinds-one-orphaned-from-host-star` ·
  `maturity-tier-derived-from-panel-tree-position`.

### Root 2 — publish.geojson can't be rebuilt from the DB · 7 findings · F4 + F5
The served `publish.geojson` is **not a pure function** of the live DB + the bake SQL. It carries ids 1–6,
**disjoint from the live DB serials 139–201**; it still holds the retired `blurb` key; and **five served
files have two competing writers** (`rebake_canonical.py` vs `export_publish_geojson.sh`) — whichever runs
last wins, and running the wrong one **silently reverts gold-migrated state**. The published id is the
*volatile serial PK*, so a fresh-volume rebuild renumbers every feature. And the trail human names
("Launchpad") **never entered the DB** — they live only in `aop_trail_catalog.json` — so a bake from the
store of record can still only emit `name=number`.
- `publish-geojson-stale-not-reproducible` · `published-id-is-volatile-serial` ·
  `two-writers-same-five-files-rebake-vs-export` · `trail-human-name-not-in-db-bake-can-only-emit-number` ·
  `canonical-fields-duplicated-columns-vs-attrs-served-from-attrs` · `event-umbrella-metadata-hardcoded-in-bake` ·
  `reference-bake-no-meta-on-fresh-volume`.

### Root 3 — no one identity key per real feature · 6 findings · F6 (highest risk, do last)
Every cemetery is **two features** (parcel + marker) sharing one **non-unique** id, disambiguated by an
off-canonical `geom_role`; host keys on `parcel_id`, panel on `name`, DB on `parcel_id+geom_role`. The Ellis
cemetery appears as 4+ distinct ids across two files and three layers. Buildings serve a FEMA UUID in the
reference arm and a serial PK in the publish arm — two id semantics for one table. There is no single `id`
that means "this real-world feature."
- `served-id-heterogeneous-no-canonical-key` · `cemetery-parcel-marker-twin-nonunique-id` ·
  `ellis-cemetery-multi-id-across-files` · `buildings-served-id-is-attrs-businesskey-not-pk` ·
  `two-editor-sinks-opposite-homes` · `publish-kind-taxonomy-fork`.

### Residue (named, not silently dropped)
- **Events overlay (2, out of scope of the shadow axis):** two divergent render-time resolvers (host vs
  panel) + coordinate-less anchors positioned from a localStorage `#tag` binding. Re-homed to its own
  event-overlay convergence card.
- **Deferred-low (1):** `hotspot-twin-id-collision-offvocab-sort` — latent, no user-facing break.
- **Verification debt (C4):** the entire audit was **static** — no one has actually *observed* the
  two-browser divergence in the running app. Owed: a Playwright run that screenshots the four trail-name
  surfaces (now should agree post-A2) and confirms the panel-overrides replay differs across two browsers.

## The seam — why "right" but not "reproducible"

Path A made the **served files** canonical by baking from `data/raw/` + the sidecars. The gold northstar wants
the **DB** to be the reproducible store of record. Right now those two truths agree **by hand**: the served
files read correctly, but the DB can't regenerate them (trail names aren't in it, publish ids don't match,
two writers fight). So the data is correct but **fragile** — re-running the wrong bake reverts it. Closing
Root 2 is what turns "we keep it right" into "it can't be wrong."

## Next steps — recommended sequence

The remaining work is gold slice 6. Recommended order (rationale: kill the active danger first, leave the
highest-risk identity surgery for last):

1. **Make the bake a pure function (Root 2 / F4 + the trail-catalog-into-DB prerequisite).** Fold
   `aop_trail_catalog.json` + `aop_poi_index.json` rows into `core.features` so the DB can emit the canonical
   names/descriptions Path A baked into the served files; settle **one writer per served file** (A1 already
   evicted `publish.geojson` from `rebake_canonical`'s CONFIG — finish for the other four); rebuild
   `publish.geojson` from the DB with a **stable business-key id**, not the serial PK. *This touches the
   production served file → your git gate.* **Highest leverage: it ends the silent-revert danger and closes
   the served-vs-DB seam at once.**
2. **Demote localStorage to a working buffer (Root 1 / F1).** Edited props/geometry/stars/tags flow through
   one DB door; the published view stops being a per-browser replay. (Do the **C4 observation first** so we've
   actually seen the divergence we're fixing.)
3. **Collapse the identity forks (Root 3 / F6).** One canonical `id` per real-world feature; the cemetery
   twin becomes one record with the parcel as related geometry. Highest risk — do it last, on its own.
4. **Fresh-volume parity (F5).** Get the ~153 live-only imported rows into the seed so a clean docker rebuild
   reproduces the live DB. Blocked until 1–2 retire the legacy writers.
5. **Events overlay convergence** — separate card, whenever the events surface is next worked.

### The one genuine fork for you
The order above attacks **Root 2 first** (reproducibility/danger). The alternative is to attack **Root 1
first** (localStorage → DB door) because it's the most *visible* (two browsers disagreeing is the symptom you
feel). Both are defensible; I recommend Root 2 first because two-writers is actively dangerous (it can revert
gold state on the next bake) and because it unblocks F5. Your call on which root leads.

## Pointers
- `tasks/09_editor_maturity/shadow_attributes_audit.md` — the 45-finding catalog (ids grep-resolve).
- `tasks/09_editor_maturity/shadow_attribute_resolution.md` — Path A done (A1–A5), Path B tagged.
- `tasks/06_going_gold/gold_migration.md` slice 6 — F2 done; F1/F4/F5/F6 held (= Path B).
- `research/common_feature_schema.md` — the CMFS target (Tier 1 identity / Tier 2 provenance / Tier 3 facets).
- `output/council/spike_code_dbfirst_audit_20260608.md` — the F1–F9 store-of-record audit this extends.
