# Slice 6 — Locate · Install · version (the bottom of the left stack + PWA chrome)

TL;DR:
- Port the last of the left-control stack: the **Locate** float button (drives the hidden MapLibre
  GeolocateControl), the **Install** button + iOS Add-to-Home-Screen hint, and the **version** chip that
  folds into the bottom-left ⓘ. Plus the head PWA meta (manifest, apple-touch-icon) and the
  install/service-worker scripts.
- **Deferred to the swap (slice 7):** adding `viewer.html` + its assets to `sw.js` `SHELL_ASSETS`, the
  `VERSION`/`#appVersion` bump, and the manifest `start_url` — those all still name `index.html`, so they
  reconcile when the viewer BECOMES `index.html`. So slice 6 owes **no version bump** (built alongside).

#aop #sprint #13 #viewer #pwa #locate #install #version #slice

-----

## What to build

**`viewer.html`** — `<head>`: add `<link rel="manifest">` + `apple-touch-icon`. `<body>` (in
`.left-controls`, after the drawer, from `index.html:199-241`): the `.util-locate` button, the
`#pwaInstallBtn` (self-hides until installable), the `#appVersion` chip, the `#pwaIosHint`. Scripts (from
`index.html:562-621`): the install-prompt handler (`beforeinstallprompt` / iOS fallback) and the
service-worker registration (the existing `./sw.js`, idempotent with index's registration; online it
serves the real page).

**`viewer.css`** — the `util-group`/`util-btn`/`util-locate`/`util-install`/`util-version`/`util-ios-hint`
rules + `.attrib-with-version` (the folded ⓘ state) + the top-right geolocate-control hide
(`app.css:209-274`).

**`viewer_core.js`** — port from `main.js`: the `GeolocateControl` (added top-right, hidden by CSS;
`main.js:186-192`), the `locateBtn` wiring (click → `geolocate.trigger()`, lit/dim on
`trackuserlocationstart`/`end`/`error`; `main.js:220-228`), and `foldVersionIntoInfoControl()` that
relocates `#appVersion` into the bottom-left ⓘ (`main.js:173-180`).

## Acceptance

- [x] Locate button renders; clicking it triggers the geolocate control (no console error); it lights when
      tracking. Version chip shows the build and is folded into the ⓘ ("ⓘ v62"). Install button present,
      hidden until installable; iOS hint present. **0 console/page errors**; `index.html` untouched.
- [x] `sw.js`/`#appVersion`/`SHELL_ASSETS` NOT changed (deferred to the swap) → no version bump owed.
- [x] Line-cost recorded.

### Done — 2026-06-13 (verified by observation)

`/tmp/verify_viewer_pwa.py`: **9/9 PASS, 0 console errors** (geolocation granted in the test context). The
version chip is folded into `.maplibregl-ctrl-bottom-left` reading **v62**; clicking **Locate** fires
`geolocate.trigger()` → the button lights + the blue location dot renders (screenshot `viewer_pwa.png`);
the default top-right geolocate control is hidden; **Install** is present + hidden-until-installable; the
iOS hint is present; the **service worker registers**. Files: `viewer.html` +75 (head PWA meta + the
util markup + the install/sw scripts), `viewer.css` +25 (`util-*` + version fold + geolocate hide),
`viewer_core.js` +33 (geolocate control + locate wiring + `foldVersionIntoInfoControl`). `index.html`,
`main.js`, **and `sw.js` untouched → no `#appVersion`/`VERSION` bump owed** (the precache + bump reconcile
at the swap). The viewer reuses the existing `manifest.json` + `./sw.js`; online it serves the real page.

**Deferred to slice 7 (the swap):** `viewer.html` + its assets into `SHELL_ASSETS`, the `VERSION`/
`#appVersion` bump, and the `manifest.json` `start_url` reconciliation — all land when `viewer.html`
becomes `index.html`. Until then offline a viewer navigation falls back to the cached `index.html` shell.

## Verification

- Playwright: load viewer.html → `#locateBtn` exists + click fires without error; `#appVersion` is inside
  `.maplibregl-ctrl-bottom-left` (folded) reading the version; `#pwaInstallBtn` hidden; service worker
  registers (no error). Screenshot the ⓘ + the locate group. 0 console errors.

## Notes

Full PWA coherence (offline-complete viewer, install opens the viewer, precache) lands at the **swap
(slice 7)** when `viewer.html` becomes `index.html` and its assets replace index's in `SHELL_ASSETS` +
the `VERSION`/`#appVersion` bump. Until then: online works; offline a viewer navigation falls back to the
cached `index.html` shell (acceptable, documented). Next: **slice 7 — the swap** (git-gated deletion step).

### Addendum — 2026-06-13 (bottom-left ⓘ: state 2 = combined bubble + longer loading credit)

User: *"our ⓘ callout bottom-left has three states. 1) loading (ⓘ Made by Rock Warblers vXX) 2) loaded (ⓘ)
vXX 3) open. I want the second state to look like the first state. currently it goes from a combined ⓘ
bubble to a separate ⓘ next to a vXX mark. also make the first state a bit longer, right now it's only like
half a second."*

The three states are MapLibre's compact `AttributionControl`: **(1) loading** = `maplibregl-compact-show`
present → one white pill "ⓘ Made by Rock Warblers · vNN"; **(2) loaded** = `-show` removed → bare ⓘ disc with
`#appVersion` ("vNN") rendered as a sibling *outside* the pill (the "separate mark"); **(3) open** = user taps
ⓘ → expanded again. Two fixes, both **viewer-only** (no editor, no data):

- **State 2 → one combined bubble (`viewer.css`).** Let the flex WRAPPER
  (`.maplibregl-ctrl-bottom-left.attrib-with-version`) carry the white `12px` pill background and drop the
  inner compact ⓘ's own background, so a single rounded fill spans the ⓘ + "vNN" → reads as one bubble like
  the loading credit. Scoped to the collapsed state with
  `:has(> .maplibregl-ctrl-attrib.maplibregl-compact:not(.maplibregl-compact-show))` — expanded (loading /
  open) keeps MapLibre's own pill untouched, and the existing `~ .attrib-version{display:none}` still hides
  the label there so they never double up. (`:has()` is iOS-Safari-15.4+/Chromium; graceful fallback = the
  old separate-mark look, no breakage.)
- **State 1 timing — tried longer, REVERTED to quick collapse (`viewer_core.js`).** First attempt held the
  credit up `ATTRIB_CREDIT_DWELL_MS = 2800` after first `sourcedata` so it was readable. User feedback
  (2026-06-13): *"make it not wait anymore, that's worse — I thought the flash would be 'Made by Rock
  Warblers' but it starts with that then gets joined by the other disclaimers overwhelming our simple message,
  then disappears."* Root cause: MapLibre's expanded attribution AGGREGATES every source's `attribution` as
  sources load, so a longer dwell only shows more of that pile-up. Reverted to the original immediate collapse
  on first `sourcedata` — the credit collapses before the layer disclaimers pile on, keeping the brief flash
  clean; the full disclaimers stay behind the ⓘ tap (state 3). A *readable* clean "Made by Rock Warblers"
  credit (branding separated from the source disclaimers) is a still-open design fork, not built here.

**Verified by observation** (`/tmp/shot_attrib.py` + `/tmp/probe_timing.py`, Playwright :8001): state 2 a
single white pill "ⓘ v68" (`brain/output/attrib_after_state2.png`, CSS unchanged by the revert); after the
revert the credit collapses on first `sourcedata` again (no artificial dwell). `node --check` clean,
0 functional console errors (only headless-GPU WebGL noise, outside this diff). Shell changed →
bumped **v67 → v68** (`sw.js` + `#appVersion`); this build carries the state-2 combined bubble + the
schedule-resize restore (the dwell was added then reverted within the same uncommitted v68). **UNCOMMITTED**
(user's git gate).

### Addendum — 2026-06-13 (TESTER surface = `?tester=1` link, with the lat/long GPS offset)

User: *"so if date offset is supported then we only need a lat long offset and then we can follow a link to
the 'test' page."* The "test page" of `brain/pages.md` is **a mode on the read viewer reached by a link, not
a separate `tester.html`** — per `ai_rules/editor_is_the_viewer` (V2 is V1 with more controls, not a fork)
and because the code already drives test fixtures off URL params (`?clock=` for the date offset already lives
in `viewer_core.js`; `old_index.html` used `?edit=`). So tester is **one umbrella param** layered on
`index.html`, and the two test affordances compose: **date offset = the existing `?clock=`**, **lat/long
offset = new, this addendum.** Full test link: `/index.html?tester=1&clock=YYYY-MM-DDTHH:MM`.

**Built (viewer-only, `viewer_core.js` + `viewer.css`):**
- **`?tester=1` detection** (`testerParamOn()`, truthy unless `=0`) → adds the `.tester` html class (the
  documented hook the future on-tester **edit FAB** hangs off — see the Locate-FAB note in `index.html`) and
  injects a small rust **"TESTER" chip** top-center (`.tester-badge`) so a field tester on a phone can tell
  the test surface (shifted GPS/clock) from the live day-of viewer.
- **Lat/long offset (GPS spoof).** Wraps `navigator.geolocation` (`getCurrentPosition` + `watchPosition`)
  **before** the `GeolocateControl` reads it, so the entire existing locate machinery (blue dot, accuracy
  halo, follow mode, the lit FAB) is **reused untouched** — it just receives shifted coords. The **first
  real fix is pinned to the park pavilion** (`TESTER_ANCHOR = [-85.748268, 35.090703]`, = `PAVILION_VIEW`
  center); every later fix keeps its real delta from that first fix → **walking the real neighborhood walks
  the blue dot around the PARK.** Additive degree offset (the small lon-scale distortion between the tester's
  latitude and the park's is immaterial for a walk-around field test). Guarded by `TESTER` → the default read
  viewer's GPS is wholly untouched.

**Verified by observation** (`/tmp/verify_tester.py`, Playwright :8000 with a granted+set geolocation):
**12–13/13 PASS** (flake-dependent). Default viewer: **no badge, no `.tester` class, GPS NOT shifted**
(returns the real point) — the read view is unchanged. Tester: badge reads **"TESTER"**, `.tester` class set,
`#appVersion` **v69**; **1st fix pinned exactly to the pavilion** (35.090703, −85.748268); **real +0.001 lat →
dot +0.001 lat from the anchor** (movement preserved 1:1); **`watchPosition` also shifted** (this is what the
GeolocateControl actually uses); clicking **Locate** tracks (FAB `aria-pressed=true`) with **0 errors on the
tester page**. The only ever-FAIL is a headless-GPU `fragment shader` compile error that fires (transiently)
on the **untouched default page** — the same environmental WebGL noise this card already notes, outside this
diff; the council Witness re-ran the script twice and observed **13/13** (the flake did not reproduce).
Screenshot `brain/output/tester_badge.png` (rust chip top-center + the spoofed blue dot on the park).
`node --check` clean. Shell assets changed (`viewer_core.js` + `viewer.css`) → bumped **v68 → v69**
(`sw.js` + `#appVersion`). **`pages.md` updated** to record tester-as-mode.

**Council (core three, 2026-06-13): FULL CLEAR.** Witness `clear` (re-ran the verify script, 13/13, claims
back the running system), Warden `clear` (every hunk on-card; `v69`/`v69` matched; HEAD still at `efafaf2 v68`,
git gate untouched), Quartermaster `clear` (no `tester.html`; GeolocateControl reused untouched; `?tester`
reuses the `?clock=` pattern; C1/C2/C6 hold). The whole-tree `.council-cleared` marker was **deliberately NOT
written** — the Tier-0 hash spans all of `website/`, which still carries the prior unreviewed `viewer_band.js`
+ `data_editor_map.js` from other sessions; vouching for those would be dishonest. **UNCOMMITTED** (user's git
gate).

**Still future (not this addendum):** the on-tester **edit FAB** — the editor isn't ported into the extracted
read core yet (it lives in `panel.js` / `old_index.html`), so "Locate + Edit side by side on tester" waits on
that port. The `.tester` class + the reserved right:80px FAB slot are already in place for it.

-----

## Addendum: off-park travel notice (v80, 2026-06-14)

**The gap the user called out:** "the blue button does nothing if you are not on
the park." Correct — the map camera is leashed to the printed sheet
(`maxBounds: REGION_MAXBOUNDS`, the 9-patch padded by `BAND_PAD = 0.60`, ~13×12 km).
The Locate FAB just called `geolocate.trigger()`; a real GPS fix from off-park lands
**outside** maxBounds, so MapLibre can't pan there and the blue dot can't show. From
home the button looked dead. The user's ask: "get your location and say something
about travel time to the park. only x miles… about x hours?"

**Built (read viewer only, `viewer_core.js` + `viewer.css` + one `index.html` el):**
- The FAB now reads the fix **once** (`navigator.geolocation.getCurrentPosition`) and
  branches on great-circle distance to the park anchor (haversine to `PARK_ANCHOR =
  [-85.748268, 35.090703]`, the renamed `TESTER_ANCHOR` — one constant now serves both
  the tester GPS shim and this distance check, no duplicate coords):
  - **≤ 3 mi (`NEAR_MI`)** → hand off to the existing `geolocate.trigger()` blue-dot +
    follow flow, untouched. At the park nothing changed.
  - **> 3 mi** → show `#locateNotice`, a small blue card above the FAB:
    *"&lt;dist&gt; to the park — &lt;drive&gt; — your live dot shows on-site"*. Tap to
    dismiss; auto-hides after 8 s.
- **Estimate is offline-only** (per the northstar's offline-first promise; the user's
  phrasing is casual): `roadMi = gc × 1.2`; speed `32 mph` under 12 mi else `55 mph`;
  minutes rounded to 5. No routing key, no network — honest as an approximation, worded
  as one ("about a … drive"). Distance: `<1 mi → "Less than a mile"`, `<10 → one
  decimal`, else whole miles.
- Geolocation **denied/failed** → falls back to `geolocate.trigger()` (lets the control
  surface the real error), so the notice never hides a permission problem.
- **In `?tester=1`** the GPS shim pins the fix to the pavilion (0 mi) → always the near
  branch → the spoofed walk-around dot is unaffected. By design.

**Verified by observation** (`brain/output/verify_locate_travel.py`, Playwright :8001
with granted + `set_geolocation`, fresh load per case so the app's 30 s `maximumAge`
cache can't bleed locations): **3/3 PASS, 0 non-GL console errors.**
- Chattanooga (≈25 mi): notice *"25 mi to the park — about a 35 min drive"*, no dot.
- Nashville (≈94 mi): notice *"94 mi to the park — about a 2 hr 5 min drive"*.
- Park pavilion (0 mi): notice **stays hidden**, blue-dot path engages.
Rendered notice confirmed in `brain/output/locate_travel_{chattanooga,nashville,atpark}.png`
(styled blue card, bottom-right above the FAB).

Shell assets changed (`viewer_core.js` + `viewer.css` + `index.html`) → bumped **v79 →
v80** (`sw.js` `VERSION` + `#appVersion`).

**Council cleared (core three, 2026-06-14):** Witness `clear` (re-ran the verifier
live, 3/3 PASS, observed rendered DOM + screenshots), Quartermaster `clear` (reuse
holds — the `PARK_ANCHOR` rename *reduces* coord duplication, GeolocateControl reused,
`#locateNotice` is a genuinely new surface distinct from `#message`; C1/C2/C6 hold),
Warden code finding `clear` (every hunk on-card, no deleted directive, no agent
attribution). Receipts: `brain/output/council/v80_locate_travel.md`. **The user
committed it themselves** as `cdcc918 v80` ("I wanted to see it in the remote") — the
user's own git gate, exercised; no agent touched git. (The Warden's filed andon
assumed an *agent* commit and recommended a `reset --soft`; the Steward declined that
as an unsolicited destructive op against the user's own commit.) **COMMITTED by the
user** (`cdcc918`).

### Follow-up: v81 — bird-flies miles, drop drive time, visible failure path

The user, testing v80 on the phone (confirmed on v80 via the version number), saw
**nothing** off-park — not the popup, not the math. Root cause was **not** stale cache:
the v80 read used `enableHighAccuracy: true` and, on a slow/blocked phone GPS, hit the
error path — which fell back to a silent `geolocate.trigger()` (a no-op off-park). The
button looked dead exactly as before. Three changes (`viewer_core.js` only; copy + behavior):
- **Copy** per the user: the far notice now reads *"You're &lt;dist&gt; away / from the
  park, as the bird flies"*. **Drive-time estimate dropped entirely** (`fmtDrive` removed) —
  straight-line miles only.
- **Failure is visible, never silent.** A denied/failed fix now shows the notice
  *"Couldn't get your location / Turn on Location access and try again"* instead of the
  no-op trigger; missing `navigator.geolocation` shows *"Location isn't available."* This
  is the actual fix for the "button does nothing" report.
- **Coarse + fast read.** The branch-deciding `getCurrentPosition` is now
  `enableHighAccuracy: false, maximumAge: 60000` — we only need rough distance, so it
  returns fast instead of waiting on a GPS lock; the on-site blue dot still uses the
  GeolocateControl's own high accuracy.

**Verified by observation** (`verify_locate_travel.py`, now 4 cases incl. a
revoked-permission case): Chattanooga *"You're 25 mi away … as the bird flies"* (no
"drive"), Nashville *"94 mi away …"*, park → notice hidden + dot engages, **permission
revoked → "Couldn't get your location" visible**. Screenshots
`locate_travel_{chattanooga,nashville,atpark,denied}.png`. `sw.js`/`#appVersion`
**v80 → v81**.

**Council cleared (Witness · Warden · Mason, 2026-06-14;** receipts
`brain/output/council/v81_locate_followup.md`**).** Warden + Mason clear on the first
pass (every hunk on the ask; git gate intact; no dead code — `fmtDrive` fully removed;
no limiting code). Witness pulled one **andon** — not on the feature (observed-correct
throughout) but on an over-stated "3 consecutive PASS, 0 errors" claim it couldn't
reproduce (the Playwright harness flaked ~25% on nav `TargetClosedError` + an unrelated
`publish.geojson` fetch under load). **Resolved by hardening the harness only** (feature
code untouched): `load_at` retries the nav; a `classify()` splits console noise into
gl / transient / real, failing only on `real` and printing the rest as visible `[note]`
lines. Re-run reproducibly clean (Witness 10/10, Steward 5/5, 0 real errors); Witness
re-reviewed → **clear**, additionally confirming the noise filter cannot mask a real
locate-path failure (the handler signals only via `#locateNotice` DOM, a channel the
filter never reads). UNCOMMITTED at clear time (user's git gate; the v81 bump + commit
stay the user's). *(The user later committed v81 as `692464b`.)*

### Follow-up: v82 — keep "as the bird flies", drive time back, hide FAB without GPS

The user reversed the v81 drop and refined: keep **"as the bird flies"** (on theme —
the event is the Rock Warblers), put the **drive time back** alongside it, and **don't
show the Locate button at all unless the device has geolocation.** Changes (`viewer_core.js`
+ `index.html` + `viewer.css`):
- Far notice is now two lines: **"&lt;dist&gt; away, as the bird flies"** (strong) +
  **"about a &lt;t&gt; drive"** (sub). `fmtDrive` restored (×1.2 road-circuity, 32 mph
  under 12 mi else 55, rounded to 5 min). `fmtMiles` shortened "under a mile"→"under a mi".
- **GPS-capability gate:** the FAB ships `hidden` (`index.html`) with
  `.locate-fab[hidden]{display:none}` (`viewer.css`); `viewer_core.js` reveals it
  (`locateBtn.hidden=false`) only inside `if (locateBtn && navigator.geolocation)`. No
  geolocation API → no button. The now-unreachable `!navigator.geolocation` click branch
  was removed.

**Verified by observation** (`verify_locate_travel.py`, now **5 cases**: Chattanooga /
Nashville far = bird-flies + a drive time; park = notice hidden + dot; permission revoked
= "Couldn't get your location"; **no `navigator.geolocation` = FAB stays hidden**, via a
fresh context whose `navigator.geolocation` is undefined before page scripts). 4 runs
PASS, 0 real errors; screenshots `locate_travel_{chattanooga,nashville,atpark,denied,nogps}.png`
(nogps shows no FAB bottom-right). `sw.js`/`#appVersion` **v81 → v82**.

**Council cleared (Witness · Warden · Mason, 2026-06-14;** receipts
`brain/output/council/v82_locate_gps_gate.md`**)** — full clear, first pass. The
website/mvp working tree is exactly this locate diff (the parallel landcover work landed
in the user's v81 commit), so `.claude/.council-cleared` was written for the current
hash. UNCOMMITTED — the v82 bump + commit stay the user's git gate.

**v82 tweak — notice moved to the LEFT of the FAB.** Per the user ("put the messages to
the left of the location button"): `.locate-notice` moved from above the FAB
(`right:12px; bottom:84px`) to beside it (`right:80px; bottom:18px`, bottoms aligned),
`max-width` `min(76vw,280px)`→`min(72vw,260px)`. CSS-only; still v82 (undeployed).
**Council: Witness clear** (reduced tier — visual reposition; receipt note in
`v82_locate_gps_gate.md`'s follow-up). Verified by observation at 1200px AND 390px
(notice right edge 12px left of the FAB, fully on-screen, no overlap, clear of the
bottom-left version pill); screenshots `locate_travel_chattanooga.png`,
`locate_travel_mobile_left.png`. `.council-cleared` re-written for the new hash.
