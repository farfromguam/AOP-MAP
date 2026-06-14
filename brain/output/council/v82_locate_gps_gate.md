# Council — v82 Locate: bird-flies + drive time + GPS-capability gate (2026-06-14)

Tier: Witness · Warden · Mason. Reviewed over the locate-only working-tree diff on top
of committed v81 (`692464b`): `website/js/viewer_core.js`, `website/index.html`,
`website/css/viewer.css`, `website/sw.js`. (The earlier parallel landcover changes
landed in the user's v81 commit, so the website/mvp working tree is now exactly this
locate slice.)

## The user's three asks (this round)
"I want it to say 'as the bird flies' -- because bird related. then drive time. Can you
mke it so the button does not show up unless the device has gps?" →
(1) keep "as the bird flies", (2) bring the drive time back (reverses v81's drop),
(3) hide the Locate FAB unless the device exposes geolocation.

## Outcome: FULL CLEAR

```
SEAT: witness   VERDICT: clear
  Re-ran verify_locate_travel.py 4× on live :8001 (served v82 — appVersion=v82,
  fmtDrive present): 4/4 PASS, exit 0, 0 real console errors, all five cases stable.
  The new no-gps case is genuine (fresh ctx + add_init_script making
  navigator.geolocation undefined BEFORE page scripts, then a 3-part real-DOM assert:
  has_geo False AND #locateBtn el.hidden true AND offsetParent null). Far cases now
  require BOTH "as the bird flies" AND "drive" via real #locateNotice reads.
  Screenshots: locate_travel_chattanooga.png = "25 mi away, as the bird flies / about a
  35 min drive"; locate_travel_nogps.png = NO Locate FAB bottom-right (only v82 pill).

SEAT: warden    VERDICT: clear
  Every hunk traces to the three asks. fmtDrive re-add is the user's explicit reversal
  of "drop drive hours" — on-ask, not drift. FAB hide: index.html `hidden` on
  #locateBtn + viewer.css `.locate-fab[hidden]{display:none}` + viewer_core.js guard
  `if (locateBtn && navigator.geolocation)` with `locateBtn.hidden=false`; dead
  !navigator.geolocation click branch removed. fmtMiles "under a mile"→"under a mi" is
  a one-word copy tweak on the same line (noted, minor). Version v81→v82 strings only.
  Git gate intact: HEAD 692464b v81, no agent v82 commit, no attribution; the v80/v81
  commits are the user's own.

SEAT: mason     VERDICT: clear
  node --check OK. No dead code / no orphans — lit, dim, fmtMiles, fmtDrive, showNotice,
  noticeTimer, milesToPark, NEAR_MI all defined+referenced. fmtDrive math correct
  (×1.2, 32/55 mph at 12 mi, round-5, hr/min split). Removed !navigator.geolocation
  branch is provably unreachable (button never revealed without geolocation → click
  can't fire). CSS specificity: `.locate-fab[hidden]` (0,2,0) beats `.locate-fab`
  (0,1,0) → default-hidden hides reliably, no flash-of-visible (JS only un-hides).
  navigator.geolocation is the minimal-right capability check (Permissions API would
  over-build). No limiting code — a UI capability gate, not a data constraint. Single
  noticeTimer clear-then-set guard intact; one innerHTML write, no leaked setTimeout.
```

## Steward synthesis

**Full clear** — all three convened seats clear on the first pass, each by its own lens
(observed 5-case run incl. the new no-gps hide; on-ask against the user's three explicit
requests; clean craft with the removed branch proven unreachable). The website/mvp
working tree equals exactly this reviewed locate diff, so `.claude/.council-cleared` is
written for the current hash. UNCOMMITTED — the v82 bump + commit stay the user's git
gate (consistent with the user self-committing v80 and v81).

## Follow-up (same v82, undeployed): notice moved LEFT of the FAB

User: "can we put the messages to the left of the location button." CSS-only —
`.locate-notice` `right:12px;bottom:84px` (above) → `right:80px;bottom:18px` (left of
the FAB, bottoms aligned); `max-width` `min(76vw,280px)`→`min(72vw,260px)`. Reduced
tier (Witness only) — a 2-line visual reposition, below copy-edit risk.

```
SEAT: witness   VERDICT: clear
  Own fresh Playwright run at TWO viewports. Desktop 1200x900: notice {right 1120} <=
  btn {left 1132} (12px gap), bottoms aligned, fully on-screen, no overlap. Phone
  390x844: notice {left 93.7, right 310} <= btn {left 322} (12px gap), left >= 0 (not
  clipped), right <= 390, clear of #appVersion pill (right 61). FAB still visible.
  Screenshot eyeballed. All assertions pass.
```

Steward: clear at the reduced tier. `.council-cleared` re-written for the new hash.
