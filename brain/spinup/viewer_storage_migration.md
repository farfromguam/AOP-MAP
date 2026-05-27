# Viewer storage migration (`_v1` → `_v2`)

TL;DR:
- The viewer carries two kinds of versioned state — localStorage keys
  (`aop_*_v1`) and JSON bundle schemas (`aop-*-v1`). Both are versioned for
  the same reason: when the on-disk shape changes incompatibly, the old
  shape stops being readable.
- Migration is forward-only. Bump the suffix, drop the old read path,
  rely on the Reset viewer affordance to clear stale state.
- This is a procedure, not a policy debate. If you find yourself writing
  an in-place v1→v2 migration, stop — the cost is rarely worth it for a
  static viewer with a hard-reset button.

#aop #viewer #localstorage #migration #schema

-----

## When to bump

Bump the version suffix when the **shape** changes incompatibly. Examples
of shape changes:

- A required field is added that the v1 reader cannot synthesize a default
  for.
- A field is renamed, removed, or its type changes.
- Nested structure is reorganized (e.g. an array becomes a map keyed by id).
- A unit changes (seconds → minutes, RGBA → hex string).

Do **not** bump when:

- A new optional field is added that v1 readers can ignore.
- An existing field's semantics tighten in a way the v1 writer's outputs
  already satisfy.
- The change is purely cosmetic (key reordering, whitespace).

In those compatible cases, leave the version pinned and update the reader
to tolerate either shape.

## Two surfaces, same rule

### 1. localStorage key suffix

Pattern: `aop_<purpose>_v<N>`. Twelve keys today, all `_v1`:

```text
aop_calendar_height_v1
aop_calendar_collapsed_v1   (legacy — cleanup target only)
aop_visitor_context_overrides_v1
aop_brand_logos_overrides_v1
aop_feature_visibility_v1
aop_feature_tags_v1
aop_feature_tags_seeded_v1
aop_editor_pois_v1
aop_viewer_preset_settings_v1
aop_left_rail_drawer_v1
aop_virtual_clock_v1
aop_viewer_session_state_v1
```

The full list lives in `VIEWER_OWNED_STORAGE_KEYS` at
`website/index.html:882-895`. Add new keys to that array — the `Reset
viewer` button in the Session tools section iterates it.

**To bump a key:**

1. Add the new constant alongside the old:
   `const FEATURE_VISIBILITY_KEY = 'aop_feature_visibility_v2';`
2. Update every read and write to the new constant.
3. Add the new key to `VIEWER_OWNED_STORAGE_KEYS`.
4. **Drop the old key from `VIEWER_OWNED_STORAGE_KEYS` only after the
   feature has shipped at least once with the new key in the list.** This
   way a user whose browser still holds the v1 payload gets the v1 key
   cleared on `Reset viewer`, not orphaned forever.
5. Once the wave of users has rolled forward (or after one sprint), drop
   the v1 reader entirely.

Do not write a v1→v2 in-place migrator. The viewer is a static page; the
user can always reload and the Reset viewer button is one click away in
the right rail. The migrator code earns less than it costs to keep
working.

### 2. JSON bundle schemas

Pattern: `schema: 'aop-<purpose>-v<N>'`. Three live today:

- `aop-section-state-v1` — per-section Export ↑/↓ payloads.
- `aop-viewer-preset-settings-v2` — Export-all/Import-all panel bundle.
  The v1 form is **rejected on import** at
  `website/index.html:4523-4524`; v1 export was retired in the v2 ship.
- `aop-event-schedule-v1`, `aop-poi-index-v1`, `aop-virtual-clock-v1`,
  `aop-viewer-session-state-v1` — internal/persisted payloads, not
  user-facing export shapes.

**To bump a bundle schema:**

1. Bump the `schema` string emitted by every writer:
   `'aop-viewer-preset-settings-v2'` → `'aop-viewer-preset-settings-v3'`.
2. Update every reader to reject the previous string explicitly:
   `if (payload.schema !== 'aop-viewer-preset-settings-v3') throw ...`.
3. Add a one-line note to the user-visible failure path so a v2 paste
   into a v3 reader fails with a readable message ("Not an
   aop-viewer-preset-settings-v3 payload."), not a silent no-op.
4. Do **not** add a v2 → v3 in-place adapter unless the data is
   irreplaceable. Bundle payloads are export artifacts — a user with a
   v2 bundle can re-export the same state from a v2 viewer if they
   still need it. Adapters become carry-on baggage.

## The Reset viewer affordance is part of the migration

A `_v2` ship that leaves stale `_v1` payloads in user browsers is a
support story waiting to happen. The Session tools `Reset viewer` button
(shipped 2026-05-26 in `tasks/03_event_app/_done/viewer_session_state_test_clock.md`)
is the explicit user-facing escape hatch.

When you ship a `_v2`, mention `Reset viewer` in the card's "How to
recover" section if there is any chance a user has v1 state from a
previous load.

## Why no in-place migration

Three reasons, in order of weight:

1. **The viewer is static.** No server-side migration job, no schema
   registry, no rolling deploy window. Migration would have to live
   inside the page itself.
2. **The page is reloaded constantly.** Hard reset is one click. The
   user already accepts that local state is per-browser; one extra
   reset is not a regression.
3. **Adapter code is load-bearing dead weight.** Every v1→v2 reader
   that ships in v2 becomes v3's adapter chain, and v4's, and so on.
   Pick a version, draw a line, force forward.

The cost case for an in-place adapter would have to be: irreplaceable
data, lost on reset, that the user cannot re-derive. Editor-drawn POIs
sit closest to that bar — but the Editor POI list already has its own
`Export GeoJSON` action a user can run before resetting. The
`Reset viewer` confirm() prompt names what's being cleared so an
informed user can export first.

If a future bump genuinely needs an adapter, write it as a one-time
read-and-rewrite at app boot (read v1, write v2 in-place, delete the v1
key), gated by a constant that can be flipped off in the next sprint.
Do not let it grow into a permanent two-shape reader.
