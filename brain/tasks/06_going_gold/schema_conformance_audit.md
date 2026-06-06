# Schema-conformance audit — make the one-shape contract self-verifying

> **Born from the council consult 2026-06-06** (schema / type-system fork). The
> council's reconciled answer to "force data into a DB + enforce a type system":
> the one-shape contract **already exists and ships** (the Common Minimum Feature
> Schema, `website/data/_schema.json` `aop-cmfs-v1`, backed by
> `brain/research/common_feature_schema.md`) — what's missing is a **receipt** that
> proves conformance. `rebake_canonical.py` *writes* the schema manifest but nothing
> *re-reads* it to verify. This card closes that gap.

TL;DR:
- A **read-only** audit that re-reads the served `website/data/*.geojson` (and the
  baked `publish.geojson`) against the CMFS contract after a bake and **REPORTS**
  conformance gaps. It **never filters, rejects, or drops** a feature.
- It already has teeth: a hand-run during the council consult caught real drift —
  `aop_user_features.geojson` is on disk but **missing from the `_schema.json`
  manifest**. Close that as a note while wiring the audit.

#aop #sprint #06 #schema #cmfs #audit #verify #no_limiting_code

-----

## Why this, and not a type system / DB constraint

The council (Steward chair; Quartermaster·Mason·Witness·Warden) resolved the fork:

- **Shape, not vocabulary (Mason / C5).** Enforce that every feature carries the
  canonical fields (id/name/description/kind + provenance/curation block) — **never**
  reject an out-of-vocabulary `kind`/`status`/`permission` value. CHECK constraints,
  enums, `NOT NULL` on value columns, and row-dropping importers are forbidden by
  `no_limiting_code_mvp` / **C5** — they silently drop the freshest field data, which
  the northstar says is worse than an honest candidate line. PostGIS already does this
  right (zero CHECK, zero enum; value columns open `text`; gate only the publish views).
- **No second surface (Quartermaster).** Do **not** write a fourth hand-maintained
  schema (a JSON type-manifest, a TS interface set, a validator module) beside the
  three that already declare the shape (`init_db.sql` DDL · `source_register.md` ·
  the `FEATURE_LIST_LAYERS` spec registry + `_schema.json`). The audit **reads** the
  existing `_schema.json`; it invents no new contract.
- **Bounded + on-farm (Warden).** "Enforce a type system across all sources" is an
  unbounded theme that would tempt hardening the localStorage/per-layer scaffolding
  the one-pipeline design says to **collapse**. This audit touches none of it.
- **Verifiable + tile-independent (Witness / C4).** No browser, no map tiles — it
  reads files. The receipt is the acceptance.
- **Conflict resolved:** Warden floated CHECK/enum constraints on `core.pois`; Mason
  pulled andon (C5, a locked contract). Steward resolves in Mason's favour — the probe
  **reports**, it does not **reject**. A value-rejecting gate would be an explicit
  **user re-confirm** (lifting "for now"), not something the council can clear.

## Scope · parallel-safe (new script + a doc/manifest line)

In:
- New `mvp/scripts/audit_canonical_schema.py` (sibling to `rebake_canonical.py`),
  run with `--check`. Re-reads each served `*.geojson` against `_schema.json`:
  - **Tier-1 assertion (report):** every feature carries `id` + `kind` (the only two
    keys universal across all 23 files today).
  - **Canonical coverage (report):** per file, how many of the 9 CMFS canonical fields
    are present on every feature; `machine:true` layers checked against the
    layer-level provenance block instead of per-feature.
  - **Manifest coverage (report):** every served `*.geojson` appears in
    `_schema.json.layers` (this is what caught `aop_user_features.geojson`).
  - Output: a coverage table + a non-zero exit **only** as an advisory signal in the
    loop (like `node -c` / the C1 grep) — it prints gaps, it does not edit data.
- Optionally pipe `export_publish_geojson.sh` output through the same Tier-1 check so
  the baked `publish.geojson` conformance is a runnable receipt too.
- Close the one found drift: add `aop_user_features.geojson` to `_schema.json` (or
  record a note on why it's intentionally absent).

Out (noticed, not done — `no_limiting_code`):
- Any CHECK/enum/`NOT NULL`-on-value/row-dropping filter. Surface gaps as notes.
- Re-typing domain attributes into one wide table (per-domain keys are real shape).
- Touching the DB write path / authoring scaffolding (gated on the authoring-surface fork).

## Observable acceptance

- [ ] `audit_canonical_schema.py --check` runs read-only, edits nothing, on a clean serve.
- [ ] Reports Tier-1 (`id`+`kind`) conformance across all served files (0 gaps expected today).
- [ ] Reports per-file CMFS canonical coverage; `machine:true` layers exempted correctly.
- [ ] Flags any served file missing from the `_schema.json` manifest.
- [ ] The known drift (`aop_user_features.geojson`) is resolved or noted.
- [ ] No CHECK/enum/filter introduced anywhere (Mason re-check: grep clean).

## Checklist

- [ ] Read `brain/research/common_feature_schema.md` + `website/data/_schema.json` (the contract).
- [ ] Write the audit reading that contract (do not redefine it).
- [ ] Verify by observation: run it, read the table, confirm it caught the manifest gap.
- [ ] Resolve/annotate `aop_user_features.geojson`.
- [ ] Pointer in `research/viewer.md` / `research/common_feature_schema.md` so the audit is findable.

## Related

- `brain/research/common_feature_schema.md` — the CMFS contract this audits against.
- `brain/northstar/editor_architecture_contracts.md` — C5 (no limiting code), C4 (observable acceptance).
- `brain/northstar/source_register.md` — the provenance stack the canonical block carries.
- `brain/tasks/10_deferred/star_driven_poi_list.md` — the one-pipeline frame; the schema/type-system consult note hangs off its open forks.
