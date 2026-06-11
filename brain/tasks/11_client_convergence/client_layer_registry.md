# Client layer registry — converge the per-layer sprawl onto one descriptor

The data spine is normalized; the client is not. `website/js/main.js` (~10.6k lines) carries ~800
per-layer string references — each of ~14 layers has 40–87 bespoke touchpoints across load, paint,
list, edit, and toggle. Adding or changing a layer means hunting those touchpoints. This card converges
them onto **one layer descriptor** the way the data already converged onto one `core.features`.

This is the real debt named in `_readme.md` layer ③. It is directional until the user green-lights it —
it edits the production client in a high-blast-radius file, so it is loop-eligible but not loop-started
blind.

-----

## The problem, concretely

There are already two partial registries — `TUNABLE_LAYERS` (paint drawers, `main.js:1711`) and
`FEATURE_LIST_LAYERS` (CRUD index, `main.js:2187`) — plus a long tail of scattered per-layer `if`/string
branches that neither registry owns (load sites, addSource blocks, toggle wiring, source-chip labels,
seed migrations). A layer's behavior is spread across all of these. The two registries are the seed of
the fix: they prove the pattern works; they just don't cover the whole lifecycle yet.

## The shape of the fix

One **layer descriptor** per data source — `{ key, file, origin, geometryKinds, paint, list, editable,
toggle, sourceChip }` — and a small set of generic functions that read the descriptor (load → addSource
→ register paint → register list → wire toggle). The ~800 bespoke touchpoints collapse into descriptor
fields. Adding a layer becomes a data edit, not code archaeology. This stays **non-limiting** (C5): an
unknown origin or geometry still loads; the descriptor classifies, it never rejects.

The descriptor's `file` + `origin` fields are exactly what `_data_manifest.json` already records — the
x-ray and the registry describe the same set of sources, so they should not drift. Wire the registry to
be checkable against the manifest.

## Scope

In: unify the client's per-layer lifecycle onto one descriptor, migrating layers one at a time. Out:
changing the data, the bake, or the served-file shapes (the spine is fine — do not touch it); UI
redesign (this is a refactor behind the same behavior).

## Decisions

### 1. Big-bang rewrite, or migrate layer by layer?

**Suggested:** Migrate one layer at a time, each green before the next.

**Why:** Every layer already has a Playwright verifier (`playwright_verify_<layer>.py`) — that suite is
the safety net that makes incremental migration provable. A big-bang rewrite of a 10.6k-line file has no
safe checkpoint and is exactly the "looks done but isn't" trap the user is exhausted by. Thin vertical
slices (`practices/`) is the house style.

**Alternatives:**
- **Big-bang rewrite:** loses — no green checkpoint, high regression risk, no incremental proof.
- **Start fresh client, port features over:** the user floated this. Loses for now — it throws away the
  working PWA layout (`spinup/working_pwa_css.md`, a hard-won locked snapshot) and every passing
  verifier. Revisit only if incremental migration stalls.

## Acceptance (per migrated layer, not the whole sprint at once)

[ ] The layer's load/paint/list/edit/toggle all read from its descriptor; its bespoke branches are gone.
[ ] The layer's `playwright_verify_<layer>.py` still passes (no behavior change).
[ ] The descriptor set stays reconcilable with `_data_manifest.json` (same files, same origins).

## Verification

- Per slice: run the migrated layer's verifier + the adjacent suites (presets, feature_list) — all green.
- Net: grep `main.js` for the migrated layer's name; the per-layer touchpoint count drops toward the
  descriptor fields, not 40–87 scattered hits.

## Notes

- No commits without the user's git gate (`no_commits.md`). Convene the council before declaring any
  slice done (`council/completion_gate.md`).
