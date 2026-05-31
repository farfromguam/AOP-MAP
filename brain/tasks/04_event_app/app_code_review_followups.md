# App Code Review — Follow-ups (NOT done)

> **The held half of the 2026-05-31 app code review.** Batch 1 (15 no-decision
> fixes) shipped and is verified — see
> [`_done/app_code_review_fixes_batch1.md`](_done/app_code_review_fixes_batch1.md).
> This card carries the **17 remaining findings** with enough context to act on
> each without re-reading anything. They are held because they need an
> **on-device / interaction check** (Group B) or are **refactors / polish** worth
> their own pass (Groups C–D). Pull items into a work session as they earn priority.
>
> **Resolved since (now in the done card):** the queued decision **H4 + L8** (SW
> cache-staleness, stale-while-revalidate) and the **M7 / M14 / M17** no-device
> forks — see
> [`_done/app_code_review_fixes_batch1.md`](_done/app_code_review_fixes_batch1.md).

#aop #04_event_app #code_health #review #followups #decision

-----

## ▶ Next up

All no-device work is done (H4+L8, M7, M14, M17 — see the done card). **What
remains needs a real device or is a refactor pass.** The next slice is **Group B
(on-device)** — I implement, the user confirms on the iPhone. Recommended first
within Group B: **H1** (slider debounce) and **M12** (install button) — the
smallest, most isolated.

-----

## Group A — Decisions / forks  ✅ DONE

H4+L8, M7, M14, M17 all resolved — see
[`_done/app_code_review_fixes_batch1.md`](_done/app_code_review_fixes_batch1.md).
Nothing decision-gated remains; everything below needs a device or is a refactor.

-----

## Group B — On-device / interaction verification needed

These are real fixes, but the AOP rule
[`verify_by_observation`](../../ai_rules/verify_by_observation.md) wants the
running system observed — and these only manifest on a touch device / GL / live
interaction that headless Playwright can't fake (the same trap documented in
`spinup/working_pwa_css.md`). I'll implement on request; the user confirms on the
iPhone.

### H1 — SFWDA multiply slider re-bakes all 36 tiles per input tick
`index.html` (~9790). Dragging the slider runs a full `getImageData` + per-pixel
loop + 36 `toDataURL` encodes dozens of times/sec → main-thread lock on
mid/low-end devices. **Fix:** rAF-coalesce the `sfwdaMultiply` handler (one
rebake/frame) or rebake on `change`, live-preview opacity during drag. **Verify:**
slider feel on device.

### M4 — ~20 independent data fetches are fully serialized, no timeout
`index.html` `map.on('load')` body (~8167+). Each overlay is `await fetchJson(...)`
back-to-back; a slow/hanging file stalls every later layer (no fetch timeout).
**Fix:** kick the independent fetches off up front (collect promises, await each
where its layer is added); keep the landcover-9patch/landcover pair sequenced;
optional `AbortController` timeout. **Verify:** map still assembles correctly +
faster cold load on a throttled connection.

### M5 — Feature list re-renders the whole subtree on every tick
`index.html` `renderFeatureList`/`renderFeatureListInto` (~4796). Every checkbox /
chevron / tag / highlight clears `innerHTML` and rebuilds all rows + reattaches
~10 listeners each (3× per render for `editorPois`). **Fix:** mutate the affected
row in place for the toggle path; reserve the full rebuild for add/delete/expand;
at minimum extract `buildFeatureRow(...)`. **Verify:** no jank / focus loss on a
real list, on device.

### M8 — `resyncViewport` thrashes `map.resize()` on visualViewport resize
`index.html` (~10366). Bound to `visualViewport resize`, which fires continuously
while the iOS keyboard / URL bar animates → many `map.resize()` (layout + GL
reset)/sec. **Fix:** rAF-coalesce; only resize when the container size actually
changed. **Verify:** iOS keyboard open/close + URL-bar collapse on device.

### M9 + M10 — Move-mode anchor + armed commit (do together)
`index.html` `geometryCentroid` (~4455) + `enterMoveMode` (~4599). M9:
`geometryCentroid` is a vertex mean (wrong for uneven polygons; null for
multi-part → move silently no-ops) — switch the move anchor to the bbox center.
M10: `map.on('click')` is registered synchronously on entry, so the next click
**anywhere** (incl. accidental water tap) commits with no armed guard — defer
registration one tick (`requestAnimationFrame`/`setTimeout 0`). **Verify:**
actually drag a polygon + a multi-part feature and confirm the drop point + that
a stray click doesn't commit.

### M12 — PWA install button vanishes on a dismissed prompt
`index.html` (~10866). `btn.hidden = true` runs **before** awaiting `userChoice`,
then nulls `deferredPrompt`; a dismiss removes the affordance for the session.
**Fix:** only hide on `outcome === 'accepted'`; keep visible on `'dismissed'`.
**Verify:** install flow on a real installable browser/device.

### M13 — 22 MB forced precache on install
`sw.js` (~97-103); `aop_contours.geojson` 14 MB + `aop_landcover_9patch.geojson`
4.3 MB. `install` `allSettled`s the whole list with `{cache:'reload'}` — a 22 MB
background download the moment a phone installs, maybe on weak field signal.
**Fix:** drop the heaviest non-essential layers (contours, synthetic-activity
tracks) from the *install* precache; let them cache-first lazily on first online
view. **Verify:** install cost + that those layers still work offline-after-once.
(Also a `VERSION`-bump item; overlaps the H4 decision.)

-----

## Group C — Routed to the polish backlog

Already-flagged polish; logged in
[`viewer_polish_followups.md`](viewer_polish_followups.md) rather than re-tracked
here.

- **M19** — clickable `<div>`s (`#calendarToggle` ~997, `.panel-header` ~1080)
  have no `role`/`tabindex`/`aria-expanded`/keyboard → not operable by keyboard
  or AT. Make them `<button>` or add the role + keydown + aria.
- **L9** — CSS hygiene: dead `.left-context-card` + permanently-hidden `#message`
  rules; inline styles on `#pwaIosHint` duplicating palette tokens; dozens of raw
  hex bypassing the `:root` palette; `#pwaIosHint role="dialog"` with no
  modal/focus-trap.
- **L10** — `setLeftTab` persists the raw (possibly stale) tab key instead of the
  resolved one; `togglePanel`'s `settle` transitionend listener has no
  `setTimeout` safety net (rapid double-toggle can leak it).
- **L12** — `map.on('error')` is registered *inside* the `load` handler, so
  style/glyph errors during initial load go unlogged. Register at construction.

-----

## Group D — Code-health refactors (own pass)

Mechanical / structural cleanups; no behavior change. Lowest priority.

- **L1** — 88 tab-indented lines in a space-indented file (`index.html` lines
  4379-4410, 4715-4723, 5440, 5753-5759, 6874-6897, 7003-7049, 10255-10260).
  Held only to keep the batch-1 fix diff reviewable; do as its own whitespace-only
  pass.
- **L2** — duplication worth a shared helper: three identical `loadXStore`
  wrappers (3859/4146/4283), near-identical row builders
  (`renderVisitorListGroup`/`renderPoiTab`), brand-logo clamp/format triads,
  ~10 road `addLayer` objects, 3 tile-loop reimplementations. Extract
  `loadObjectStore`, `buildFeatureRow`, `clampRound`/`trimZeros`, a roads config
  array, `forEachTile`.
- **L3** — `tileSourceId` and `tileLayerId` are byte-identical (`index.html`
  ~9617-9618); collapse to one id fn to remove the desync footgun.
- **L11** — `bindEditorClick`/map listeners have no idempotence guard; fine today
  (single-shot init) but latent multi-fire if init ever re-runs.
- **L13** — `trimCache` is fire-and-forget + racy (`sw.js` ~147); cosmetic at the
  1500-entry cap. Note only.

-----

## Cross-cutting themes (inform the remaining work)

1. **Manual sync points with no guardrail** — H4 (SW triple-sync, now **mitigated**
   by the release-checklist comment + SWR self-heal), M17 (categories vs
   `<select>`), L3 (`tileSourceId`==`tileLayerId`), the two `*_SESSION_*_MIN`
   duration constants. Prefer a runtime single source where cheap.
2. **Full-subtree re-render as the default update path** — M5 (feature list),
   tune controls, search results, editor tree. Decomposing row/knob construction
   enables in-place updates.
3. **Resource lifecycle** — M7 (ticker), M8 (resize thrash), M9/M10 + L11
   (move/editor listeners). None are cleaned up; fine for a single-shot page,
   latent the moment any re-runs.

## Recommended sequence

1. ~~**H4 + L8**~~ — **DONE** (stale-while-revalidate, shipped with the v21 bump).
2. ~~**Quick decision-forks** (M7, M14, M17)~~ — **DONE**.
3. **On-device batch** (next): H1, M12 first (smallest), then M5, M8, M9+M10, M4
   — I implement, user verifies on the iPhone. M13 (install-precache trim) rides
   a future `VERSION` bump.
4. **Refactors** (L1 whitespace first, then L2/L3/L11) and the polish-routed
   Group C — as priority allows.
