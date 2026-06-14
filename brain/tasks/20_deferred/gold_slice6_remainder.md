# Gold slice 6 — the remainder (held items extracted from the backlog)

> **Extracted 2026-06-14 from `../06_going_gold/_done/gold_slice6_backlog.md`** when
> that execution backlog closed. The backlog's status log ended: *"Normalization is
> now functionally DONE — only G_D (destructive, the user's call) + the deferred-lows
> remain."* Those open items are collected here so closing the backlog does not bury
> them. Each names its own gate. Item ids are the backlog's `id` slugs (grep the
> backlog or `../09_editor_maturity/shadow_attributes_audit.md` for the verbatim catalog entry).

#aop #deferred #06_going_gold #slice6 #pathB #db_first #gold

-----

## Open items (each names its unblock)

### G_D — fresh-volume parity (F5) · ⚠ DESTRUCTIVE RISK · the user's call
Reconstruct the ~153 live-only `core.features` rows into the seed so a clean docker
rebuild reproduces the live DB (live ≈ 160, fresh seed = 7). **Do NOT run a fresh-volume
teardown (`down -v`) until the reconstruction path is proven non-destructively first**
(export the live rows → seed migration → verify a rebuild matches). The 153-row loss vs
re-import is **the one irreversible fork — confirm with the user before any `down -v`.**

**Deferred because:** the only irreversible step in the whole gold migration; the
re-import-vs-accept-loss decision is the user's, and the rebuild must be proven safe first.

### G_B finding 5 — feature-visibility as a baked attribute · LOW
`feature-visibility-paint-filter-as-curation` — make default visibility a baked data
attribute, not a per-browser paint filter. Needs a new baked default-visibility attr; sits
on the working-buffer-vs-truth boundary (F1 kept it a paint filter intentionally).

**Deferred because:** low severity, no user-facing break; revisit if visibility-as-data
is actually needed.

### GAP B — reference-geometry DB door
Reference-feature **geometry** edits still have no DB door (props/name/notes do, via the
G_B.3 widening of `apply_positioned_features_to_core.py`). Today a reference geometry edit
stages in the buffer and exports via the bundle.

**Deferred because:** a follow-up only if reference-geometry editing becomes a real need;
the prop/name edit door already covers the common case.

### G_F — hotspot twin-id (deferred-low)
`hotspot-twin-id-collision-offvocab-sort` — the cell/centroid twin-id is a latent identity
quirk with no current user-facing break; its `intensity_class` sort is already covered by
A4's controlled-vocab binding.

**Deferred because:** latent, no break; revisit only if it surfaces a real bug.

## What is NOT here (already done — see the closed backlog)

G0 (verification debt), G_A (sidecar fold + bake-as-pure-function + Approach-C column home +
one-writer eviction), G_E (events overlay convergence), the G_B HIGH trio (localStorage →
staging buffer), G_meta (maturity/`_meta`/manifest survive a fresh volume), and G_C (identity
forks) all landed + council-cleared 2026-06-09/10. The full record is in
`../06_going_gold/_done/gold_slice6_backlog.md`.

## Owed (the user's git gate — unchanged by this extraction)

The uncommitted gold-slice-6 shell/data batch still owes the user's commit + the
**v62→v63** bump the G_meta/G_C batch carried (the loop never commits or bumps —
`../../ai_rules/no_commits.md`).

## Related (treat as the thing)

- `../06_going_gold/_done/gold_slice6_backlog.md` — the closed execution backlog (the done items + status log).
- `../06_going_gold/gold_migration.md` — slice 6's home + the loop contract + guardrails (spine, at root).
- `../09_editor_maturity/shadow_attributes_audit.md` — the id-tagged finding catalog.
- `../../output/data_model_state_20260609.md` — the data-model state report this executed against.
- `../../northstar/source_register.md` — the raw→core→publish curation contract.
