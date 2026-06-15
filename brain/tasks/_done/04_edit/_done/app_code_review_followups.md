# App Code Review — Follow-ups (CLOSED 2026-06-01)

> **CLOSED 2026-06-01.** Every held finding is resolved or consciously deferred.
> **Done & verified:** Group B — H1, M12, M4, M5, M8, M9, M10, M13 (`VERSION` v24
> committed = H1/M12; v25 committed = the rest); Group C/D — L10, L12, L3, L11 (+ L9
> dead-rule); M19 was a stale finding (no change). See `▶ Next up` for the full
> per-item record + verifier results (`playwright_verify_code_review_groupb.py`
> 15/15, `feature_list`, `sfwda_multiply`). **Deferred to their own pass** (routed to
> `10_deferred/viewer_polish_followups.md` → "Code-review refactor residue"): L1
> whitespace, the broad L2 extractions, the L9 raw-hex sweep + pwaIosHint focus-trap;
> L13 note-only. **Still owed:** the on-device feel/touch/GL confirm (one iPhone pass).
> Kept as the historical record of the review.

> **The held half of the 2026-05-31 app code review.** Batch 1 (15 no-decision
> fixes) shipped and is verified — see
> [`app_code_review_fixes_batch1.md`](app_code_review_fixes_batch1.md).
> This card carries the **17 remaining findings** with enough context to act on
> each without re-reading anything. They are held because they need an
> **on-device / interaction check** (Group B) or are **refactors / polish** worth
> their own pass (Groups C–D). Pull items into a work session as they earn priority.
>
> **Resolved since (now in the done card):** the queued decision **H4 + L8** (SW
> cache-staleness, stale-while-revalidate) and the **M7 / M14 / M17** no-device
> forks — see
> [`app_code_review_fixes_batch1.md`](app_code_review_fixes_batch1.md).

#aop #04_event_app #code_health #review #followups #decision

-----

## ▶ Next up

All no-device work is done (H4+L8, M7, M14, M17 — see the done card). **Group B is
fully implemented (H1, M12, M4, M5, M8, M9, M10, M13)** and **Groups C–D are worked
(2026-06-01): L10, L12, L3, L11 done; M19 was a stale finding (no change); L9 partial
(dead-rule removed, raw-hex sweep + pwaIosHint focus-trap deferred); L1 + the broad L2
extractions deferred to their own pass; L13 note-only.** What remains on this card is
the **deferred sub-items** (L1 whitespace, L2 broad extractions, L9 raw-hex/focus-trap
— own pass) + the **on-device feel confirm** the batch is owed.

**Versions:** **v24** (committed, `c4e080c "v24 batch"`) = H1 + M12. **v25**
(working tree, UNCOMMITTED) = M4 + M5 + M8 + M9 + M10 + M13. **GROUP B IMPLEMENTED
2026-06-01.** Changes (H1/M12 in `index.html`; the rest below):
- **H1** — `sfwdaMultiply` slider `input` routes through a new rAF-coalesced
  `scheduleRebakeTiles()` (≤1 36-tile bake/frame; one-shot rotate/reset/substrate
  callers stay on the immediate `rebakeTiles()`).
- **M12** — install button hides only on `outcome === 'accepted'`; a dismiss keeps
  the affordance (a fresh `beforeinstallprompt` re-arms it).
- **M4** — `fetchJson` is now memoized by URL + a warm-up loop at the top of
  `map.on('load')` fires every overlay fetch in parallel. Total overlay wait drops
  from the SUM of file load times to the MAX (one slow file no longer stalls the
  layers after it). Add-sites unchanged → z-order preserved.
- **M5** — the per-row visibility checkbox updates the dependent counts in place
  via new `refreshFeatureListCounts()` (re-derived from `runtime.state`) instead of
  rebuilding the whole subtree (3× for editorPois). Full rebuild kept for
  add/delete/expand/bulk/highlight.
- **M8** — `resyncViewport` is rAF-coalesced + skips `map.resize()` when the
  container box is unchanged (kills the visualViewport-resize thrash during the iOS
  keyboard / URL-bar animation).
- **M9** — move anchor switched from `geometryCentroid` (vertex mean; null for
  Multi*) to a new `geometryBboxCenter` (bbox center of any coordinate tree). Fixes
  the silent no-op move on multi-part geometry; `geometryCentroid` left as-is for
  popup placement.
- **M10** — `enterMoveMode` arms the commit-click on the NEXT frame, not
  synchronously, and only if the move is still pending — a stray/triggering tap can
  no longer commit at the wrong point.
- **M13** — dropped the two heaviest **default-off** layers from the `sw.js` install
  precache (`DATA_ASSETS`): `aop_contours.geojson` (~14 MB) + `aop_synthetic_activity_tracks.geojson`
  (~1 MB) — ~15 MB no longer force-downloaded at install on weak field signal. The
  unchanged cache-first `/data/` fetch handler still caches each on first online view
  (offline-after-once). `landcover_9patch` (4.2 MB but default-ON) kept. `VERSION` +
  `#appVersion` v24 → **v25**.

**Verified by observation** (`mvp/scripts/playwright_verify_code_review_groupb.py`
15/15 PASS, 0 console errors): H1 burst of 12 inputs → 0 sync bakes then one
coalesced bake (vs ~12 pre-fix); M12 dismiss keeps / accept hides; M5 toggle
changes the count (`1/1→0/1`) with DOM nodes reused (no rebuild); M4 geojson
loaded; M13 served SW excludes contours + synth-tracks from precache, keeps
publish + landcover-9patch, `/data/` still cache-first, SW activates at v25
(`aop-shell-v25`/`aop-data-v25`). Plus `playwright_verify_feature_list.py`
(move-commit lands at click for POI + the bbox-anchored visitor-context polygon;
visibility counts correct; 0 console errors — only the **pre-existing**
retired-publishable-export FAIL) and `playwright_verify_sfwda_multiply.py` 5/5
(load chain intact). **Still owed — on-device confirm:** slider feel (H1), real
install prompt (M12), iOS keyboard resize (M8), dragging a multi-part feature
(M9/M10), install-cost + offline-after-once for the dropped layers (M13) — headless
can't fake touch/GL/native-prompt. (`playwright_verify_poi_editor.py` has two
**pre-existing** fails unrelated to this batch: a stale `<title>` assertion and a
collapsed-panel click timeout from the v12 collapse-on-all-widths change —
editorPois paths are covered by `feature_list.py` instead.)

Next: the **on-device pass** (whenever the phone's in hand) + the deferred
own-pass items (L1 whitespace, L2 broad extractions, L9 raw-hex/focus-trap). The
card's substantive fixes are all landed.

**Verifier note (pre-existing, not from this batch):** `playwright_verify_session_tools.py`
and `playwright_verify_poi_editor.py` crash in headless on a `Locator.click` the
full-bleed `#map` canvas intercepts (session_tools: `#clockUseInputs`; poi_editor:
`editor-bucket-add`) — same class flagged for `presets`. The exercised paths are
covered by `feature_list`/`groupb`/`sfwda_multiply` (all green, 0 console errors).
Worth a separate verifier-maintenance pass (force-click / reposition) so the suite
runs clean — not done here (out of card scope).

-----

## Group A — Decisions / forks  ✅ DONE

H4+L8, M7, M14, M17 all resolved — see
[`app_code_review_fixes_batch1.md`](app_code_review_fixes_batch1.md).
Nothing decision-gated remains; everything below needs a device or is a refactor.

-----

## Group B — On-device / interaction verification needed

These are real fixes, but the AOP rule
[`verify_by_observation`](../../../../ai_rules/verify_by_observation.md) wants the
running system observed — and these only manifest on a touch device / GL / live
interaction that headless Playwright can't fake (the same trap documented in
`spinup/working_pwa_css.md`). I'll implement on request; the user confirms on the
iPhone.

### H1 — SFWDA multiply slider re-bakes all 36 tiles per input tick  ✅ DONE (headless) 2026-06-01
`index.html` (~9790). Dragging the slider runs a full `getImageData` + per-pixel
loop + 36 `toDataURL` encodes dozens of times/sec → main-thread lock on
mid/low-end devices. **Fix:** rAF-coalesce the `sfwdaMultiply` handler (one
rebake/frame) or rebake on `change`, live-preview opacity during drag. **Verify:**
slider feel on device. — **Shipped:** rAF-coalesced via `scheduleRebakeTiles()`;
slider `input` now schedules one rebake/frame. Headless-proven (burst of 12 →
one bake); **slider feel still owed on device.**

### M4 — ~20 independent data fetches are fully serialized, no timeout  ✅ DONE (headless) 2026-06-01
`index.html` `map.on('load')` body (~8167+). Each overlay is `await fetchJson(...)`
back-to-back; a slow/hanging file stalls every later layer (no fetch timeout).
**Fix:** kick the independent fetches off up front (collect promises, await each
where its layer is added); keep the landcover-9patch/landcover pair sequenced;
optional `AbortController` timeout. **Verify:** map still assembles correctly +
faster cold load on a throttled connection.

### M5 — Feature list re-renders the whole subtree on every tick  ✅ DONE (headless) 2026-06-01
`index.html` `renderFeatureList`/`renderFeatureListInto` (~4796). Every checkbox /
chevron / tag / highlight clears `innerHTML` and rebuilds all rows + reattaches
~10 listeners each (3× per render for `editorPois`). **Fix:** mutate the affected
row in place for the toggle path; reserve the full rebuild for add/delete/expand;
at minimum extract `buildFeatureRow(...)`. **Verify:** no jank / focus loss on a
real list, on device.

### M8 — `resyncViewport` thrashes `map.resize()` on visualViewport resize  ✅ DONE (headless) 2026-06-01
`index.html` (~10366). Bound to `visualViewport resize`, which fires continuously
while the iOS keyboard / URL bar animates → many `map.resize()` (layout + GL
reset)/sec. **Fix:** rAF-coalesce; only resize when the container size actually
changed. **Verify:** iOS keyboard open/close + URL-bar collapse on device.

### M9 + M10 — Move-mode anchor + armed commit (do together)  ✅ DONE (headless) 2026-06-01
`index.html` `geometryCentroid` (~4455) + `enterMoveMode` (~4599). M9:
`geometryCentroid` is a vertex mean (wrong for uneven polygons; null for
multi-part → move silently no-ops) — switch the move anchor to the bbox center.
M10: `map.on('click')` is registered synchronously on entry, so the next click
**anywhere** (incl. accidental water tap) commits with no armed guard — defer
registration one tick (`requestAnimationFrame`/`setTimeout 0`). **Verify:**
actually drag a polygon + a multi-part feature and confirm the drop point + that
a stray click doesn't commit.

### M12 — PWA install button vanishes on a dismissed prompt  ✅ DONE (headless) 2026-06-01
`index.html` (~10866). `btn.hidden = true` runs **before** awaiting `userChoice`,
then nulls `deferredPrompt`; a dismiss removes the affordance for the session.
**Fix:** only hide on `outcome === 'accepted'`; keep visible on `'dismissed'`.
**Verify:** install flow on a real installable browser/device. — **Shipped:**
the click handler awaits `userChoice` first and hides only on accept; a dismiss
keeps the button (a fresh `beforeinstallprompt` re-arms it). Headless-proven
(simulated dismiss keeps it visible, accept hides it); **real install flow still
owed on a device.**

### M13 — 22 MB forced precache on install  ✅ DONE (headless) 2026-06-01
`sw.js` (~97-103); `aop_contours.geojson` 14 MB + `aop_landcover_9patch.geojson`
4.3 MB. `install` `allSettled`s the whole list with `{cache:'reload'}` — a 22 MB
background download the moment a phone installs, maybe on weak field signal.
**Fix:** drop the heaviest non-essential layers (contours, synthetic-activity
tracks) from the *install* precache; let them cache-first lazily on first online
view. **Verify:** install cost + that those layers still work offline-after-once.
(Also a `VERSION`-bump item; overlaps the H4 decision.)

-----

## Group C — polish (worked 2026-06-01)

**No `VERSION` bump for Groups C–D (deliberate).** v25 is already committed
(`c9fae3e`); these changes are `index.html`-only (the app shell), which the SW serves
**stale-while-revalidate** — installed users self-heal to the new shell on the next
navigation with no bump. Bumping would needlessly invalidate the version-keyed DATA
cache and force a full GeoJSON re-download for a no-data refactor. So C–D rides v25.

- **M19** — ✅ **investigated, no change (stale finding).** `#calendarToggle` has no
  click handler and no `cursor:pointer` — it's a static heading, not a clickable div
  (the calendar collapse moved to the left-rail tab icon). `#panelHeader` is already
  keyboard-operable via the **`#panelCollapse` button it contains** (real button,
  `aria-expanded`/`aria-controls`); making the wrapping div `role=button` would be
  invalid (it nests buttons). No accessible gap to fix. (Vestigial `aria-controls`
  on `#calendarToggle` left as harmless.)
- **L9** — ✅ **partial.** Removed the genuinely-dead `.left-context-card` rules (2
  sites — no element uses the class). **KEPT `#message`** — it is NOT dead: the
  element ships at index.html ~1359 and the verifiers (`sfwda_multiply` waits on its
  "publish feature" text) use it as a load proxy; JS writes to it though it's
  `display:none`. **Deferred to its own pass:** the raw-hex→`:root`-token sweep
  (dozens of sites, visual-regression risk) and the `#pwaIosHint` dialog focus-trap
  (interaction-risky for a minor iOS-only hint).
- **L10** — ✅ **DONE.** `setLeftTab` now returns the resolved key and both persist
  callers use `persistLeftTab(setLeftTab(...))` so a stale/invalid key can't be
  stored. `togglePanel`'s `settle` transitionend listener is now a named handler with
  a 360 ms `setTimeout` safety net (reflows + drops the listener) so a rapid
  re-toggle / missing transitionend can't leak it.
- **L12** — ✅ **DONE.** `map.on('error')` moved out of the `load` handler to right
  after the `Map` constructor, so style/glyph errors during the initial load are
  logged too.

-----

## Group D — Code-health refactors (worked 2026-06-01; rides v25, see Group C note)

Mechanical / structural cleanups; no behavior change. Lowest priority.

- **L1** — ⏸ **DEFERRED to its own whitespace pass** (the card's own recommendation).
  88 leading-tab lines remain (now scattered ~4404–4429, ~7003-area, ~10255-area —
  the original line ranges drifted with the v19→v25 churn). A bulk tab→space
  conversion is safe only if each line's space-count matches its surrounding indent;
  doing it carefully across 88 scattered lines is its own pass, not worth mixing into
  this batch.
- **L2** — ⏸ **mostly DEFERRED** (own pass). Only the cheap, safe one was done here
  (see L3). The broad extractions — `loadObjectStore` (3 sites), `buildFeatureRow`
  (the ~250-line row builder; risky, M5 territory), `clampRound`/`trimZeros`, a roads
  config array, `forEachTile` — are a multi-site refactor with real regression
  surface for "no behavior change" cleanup; left for a dedicated pass.
- **L3** — ✅ **DONE.** `tileLayerId` now delegates to `tileSourceId` (one literal,
  the layer id derives from the source id) — desync footgun gone.
- **L11** — ✅ **DONE.** `bindEditorClick` guards on an `editorClickBound` Set —
  re-binding a layer is now a no-op, so a re-run of init can't multi-fire the
  click/hover handlers.
- **L13** — ℹ️ **note only** (per the card). `trimCache` fire-and-forget race is
  cosmetic at the 1500-entry cap; left as-is.

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
3. **On-device batch**: ~~H1, M12, M5, M8, M9+M10, M4, M13~~ **ALL DONE (headless)
   2026-06-01** — see ▶ Next up (M4/M5/M8/M9/M10/M13 = `VERSION` v25). User verifies
   the feel/touch/GL paths + install cost on the iPhone in one pass.
4. ~~**Groups C–D** (refactor/polish)~~ — **WORKED 2026-06-01:** L10, L12, L3, L11
   done; M19 stale (no change); L9 partial (dead-rule done). **Remaining = own pass:**
   L1 whitespace, the broad L2 extractions, L9 raw-hex/focus-trap (L13 note-only).
