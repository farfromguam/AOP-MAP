# Council receipt — PWA launch icon → warbler mark (task-scoped)

Date: 2026-06-14
Chair: Steward (this session)
Task: *"update the PWA launch icon to be the full warbler svg. white background blue shape."*

## Scope (the claim — reviewed task-scoped, per `council/completion_gate.md` "Scoped to your task")

- `website/icons/icon-192.png`, `icon-512.png`, `icon-maskable-512.png`, `apple-touch-icon.png` — re-baked
- `website/icons/warbler.svg` — new source vector (byte-identical copy of the user-directed `brain/import/full warbler.svg`)
- `mvp/scripts/build_pwa_icons.py` — new reproducible generator

**Ignored (a concurrent session owns these — not mine):** `website/js/viewer_core.js`,
`feature_display.js`, `main.js`, `website/sw.js`, `website/index.html`, `website/css/viewer.css`,
`website/data/*`, and the v88→v89 bump.

## What was done

The "full warbler" is the Rock Warblers brand mark (bird + rocks + broken ring). Its SVG
paths carry no fill, so a single `fill:#1668b4` on the root `<svg>` cascades to every path;
the bird's evenodd holes read as white line-art. Brand blue `#1668b4` sampled from
`website/assets/branding/rock-warblers.jpg`. Rendered white-bg / blue-shape via
Playwright/Chromium at 192/512/180; the maskable 512 is scaled to 0.90 so the art sits
inside the platform 80% safe zone. Manifest + `index.html` already reference these exact
filenames — no rewiring needed.

## Verdicts (core three, scoped)

| Seat | Verdict | Risk | Evidence |
|------|---------|------|----------|
| Witness | clear | low | PIL: dims 192/512/512/180; 4 white corners; center `#1668b4`(22,104,180); 0% orange/green (old AOP badge ruled out); maskable outer-margin 6.4× the "any" icon's; manifest+index filenames match; v89 install (`shell.addAll` fail-hard into new `aop-shell-v89`) precaches the new icon bytes → installed users get fresh icons, no bump owed. |
| Warden | clear | low | Only claimed paths touched; `warbler.svg` byte-identical to the user-directed source; manifest unmodified (correct — names unchanged); index.html/sw.js carry only the other session's v89 hunks, my diff to them empty; no commit / attribution / version bump by this task. |
| Quartermaster | clear | low | No prior PWA-icon builder existed (`icon_master.html` is an in-browser design sheet, not a builder); reused existing filenames + manifest/index/SHELL_ASSETS wiring; single root-fill cascade, no per-path re-implementation. C1/C2/C6 greps unaffected. |

## Outcome

**Cleared.** No `.council-cleared` written: the tree is commingled with the other
session's v89 work, so the whole-tree Tier-0 marker would falsely clear code I never
reviewed. This receipt is the durable, per-task clearance.

## Owed / the user's git gate

- The new icons ride the **already-pending v89** SW install (the other session's bump) — no
  separate bump from this task. If v89 is dropped/renamed at the gate, the icons still
  serve fresh on the next bump (same filenames in `SHELL_ASSETS`).
- Commit is the user's. The icon files + `build_pwa_icons.py` + `warbler.svg` are part of
  the uncommitted tree the user separates at the gate (this task's files vs the v89 session's).
