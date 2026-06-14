---
session: pwa-warbler-icon (opus — PWA launch icon swap)
status: done
claim: website/icons/{icon-192,icon-512,icon-maskable-512,apple-touch-icon}.png + website/icons/warbler.svg (new) + mvp/scripts/build_pwa_icons.py (new)
started: 2026-06-14T16:30
---

Ran ALONGSIDE a live session doing the v89 POI/G-Central work (it owns
`viewer_core.js`, `feature_display.js`, `main.js`, `sw.js`, `index.html`, `css/viewer.css`,
`data/*` + the v88→v89 bump). I touched NONE of those — only the launch-icon claim above.

- Swapped the PWA launch icon from the AOP orange/green badge to the **Rock Warblers
  warbler mark** (bird + rocks + broken ring), **white background, brand-blue `#1668b4`
  shape** (sampled from `assets/branding/rock-warblers.jpg`). Source SVG copied in from
  `brain/import/full warbler.svg` → `website/icons/warbler.svg`.
- Reproducible baker `mvp/scripts/build_pwa_icons.py` (Playwright/Chromium render; single
  root-`fill` cascade; maskable scaled to 0.90 for the 80% safe zone). Re-run after any
  logo change.
- Manifest + `index.html` already reference these filenames — no rewiring.
- **No version bump from me** — v89 is already pending (the other session's), and its SW
  install precaches the new icon bytes by name. Bumping would collide with their claim.
- **Council-cleared, task-scoped** (Witness · Warden · Quartermaster all `clear`, scoped to
  my claim, ignoring the other session's hunks). No `.council-cleared` marker written — the
  whole-tree hash would falsely clear the commingled v89 code. Receipt:
  `brain/output/council/pwa_warbler_icon_20260614.md`.

DONE → next: user separates this task's files from the v89 session's at the git gate and
commits. The icons ride v89's SW precache.
