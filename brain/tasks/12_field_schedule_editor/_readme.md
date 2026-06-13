# Sprint 12 — Field schedule editor (basic, offline, someone-else-can-use-it)

TL;DR:
- The user's real, long-sought requirement, finally stated plainly (2026-06-11): *"I need an editor.
  I am not the one with final say on the schedule. It needs to be basic. What I DON'T want is to hope
  you [Claude] are around or I have internet at crunch time. What if I need to make the update in the
  field?"*
- Shipped v1: **`website/schedule_editor.html`** — a standalone, mobile-first, offline-first schedule
  editor. Auto-saves every keystroke to the device (`localStorage` `aop_schedule_override_v1`), works
  with no signal, no server, no AI. Verified by observation (edit → reload → edit survived).
- This is **the thing the user has been working toward** the whole project. The 3,000-line browser
  editor was a bloated misfire at this; this is the small, focused hit.

#aop #sprint #12 #schedule #editor #offline #pwa #field

-----

## The requirement (why the earlier answers were wrong)

The user does not need QGIS (desktop, won't learn it, no good for tabular schedule data) and does not
want "tell me and I'll edit the DB" (fails exactly at crunch time — no AI, no internet in a Tennessee
field). They need a **basic editor a non-technical person with schedule authority can run on a phone,
offline, during the event.**

The architectural truth that resolves the whole project's tension: **for offline field use, the device
must be the source of truth in that moment** — a server DB or an AI cannot be. So editing a local copy
(localStorage) is not the hack it was called earlier; for field use it is the *only correct* design.
The original browser-editor instinct was right; it went wrong by ballooning to edit *everything* and
never syncing back. v1 is the corrected shape: small, schedule-only, offline-first.

## What shipped (v1) — `website/schedule_editor.html`

Standalone self-contained page (no build step, does NOT touch `main.js`/`panel.js` — low blast radius).
- Loads the schedule from `./data/aop_event_schedule.json` (PWA-cached) or the local override.
- Per session: edit title / day (`date_label`) / when (`time_label`) / exact time (`start_local`) /
  status; reorder (↑/↓, renumbers `sort_order`); delete (confirm); **＋ Add session**.
- Edit event name / dates / status.
- **Auto-saves every keystroke** to `localStorage['aop_schedule_override_v1']` (debounced 250 ms) — no
  Save button to forget in the field. Full-doc override model (preserves `locations`, `activity`,
  `inspired_by`, `location_tag` on round-trip — nothing lost).
- **Export** downloads the edited `aop_event_schedule.json` (to feed back to the DB). **Reset** discards
  device edits back to published (with a confirm dialog).
- Mobile-first: big tap targets, safe-area insets, sticky event/save/online bar, sticky action bar.

## The honest limit (stated to the user, not hidden)

An offline edit shows on **that device** immediately. It reaches **other** devices only when some device
regains signal and syncs — that is physics, not a code gap. For a single info-booth tablet, the edit is
right there. For broadcast to all attendees, the Export→DB→re-publish loop runs when back online.

## Finishing steps (earned once the user confirms v1's shape — NOT done yet)

1. **PWA precache** — add `./schedule_editor.html` to `sw.js` `SHELL_ASSETS` so it's on the phone
   BEFORE signal is lost (today it self-caches stale-while-revalidate on first online open). Needs the
   user's `VERSION`/`#appVersion` bump (the bump is the user's — `no_commits`/completion gate).
2. **Export → DB loop** — wire the downloaded schedule back into `core.events` via the EXISTING
   `mvp/scripts/import_event_schedule_to_core.py` (the round-trip skeleton already exists). Then the bake
   re-publishes to everyone.
3. **(Optional) viewer reflects edits** — make the public calendar in `main.js` read the
   `aop_schedule_override_v1` overlay so on-device edits show in the viewer too (touches `main.js`).

## Acceptance

[x] v1 renders the real 13-session Rock Warblers schedule; edit/add/delete/reorder work; auto-save
    persists across reload (verified headless 2026-06-11, screenshot `/tmp/aop_sched_editor.png`).
[ ] (finishing) precache + Export→DB loop + optional viewer overlay — after user confirms the shape.

## Verification

- `cd website && python3 -m http.server 8000`, open `http://localhost:8000/schedule_editor.html`.
- Headless (2026-06-11): loaded event "Rock Warblers Trail Blazing Invitational", 13 session cards;
  edited session 1 title → auto-saved to `localStorage`; **reloaded → edit persisted** (cold-load too);
  source flipped to "your edits"; Add → 14 sessions; reorder/delete/reset work; no console/page errors.

## Council done-review (2026-06-11) — CLEAR (5 seats)

Witness/Warden/Quartermaster/Mason/Scribe all clear (receipt under `../../output/council/`). No blockers.
Findings acted on / noted:

- **APPLIED (Mason field-hardening):** a `pagehide` + `visibilitychange→hidden` listener now flushes the
  pending edit immediately, closing the sub-250 ms debounce window where closing the app right after a
  keystroke could lose it. Verified by observation (edit → fire close event with no debounce wait → the
  edit was in `localStorage`). This directly serves the field-reliability requirement.
- **NOTE for finishing step 2 (Export→DB):** `addSession()` mints a thinner session (no `activity` /
  `inspired_by` / `location_tag`). Correct here — but `import_event_schedule_to_core.py` must TOLERATE a
  session lacking those keys (do NOT add a validator in the editor; keep it non-limiting). Verify on the
  import side when that loop is wired.
- Confirmed lossless round-trip (full-doc override preserves `locations` / `activity` / `inspired_by` /
  `location_tag`), no limiting code, git gate intact (no commit, `sw.js`/`VERSION` untouched),
  `main.js`/`panel.js` untouched.
