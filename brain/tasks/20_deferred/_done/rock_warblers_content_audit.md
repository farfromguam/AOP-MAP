# Rock Warblers Content Audit

> **Addendum — About tab reworked into web copy (v92, UNCOMMITTED). 2026-06-14.**
> Follow-on to the v78 rewrite below. The user found the About tab "mixed up": the
> v78 pass stapled the spoken **Driver's Meeting** transcript onto the fact card, so
> it welcomed twice and the bottom half repeated the spec bullets + the schedule.
> Reworked into website copy, schema `aop-about-v1 → v2`:
> - One welcome (the duplicate "Welcome, everyone…" gone); the "good attitude" line
>   folds into it. Crew lore is now a prose paragraph, not a one-item bullet.
> - `items[]` (label:value list) + `driver_meeting` replaced by `sections[]`: a crew
>   paragraph, then two subheads — **The park & the map** and **What to expect**
>   (pavilion / GPS-share, yield-to-full-scale, the C.O.W., the 50/50). Times stay in
>   the Events tab. `rules` lifted to a top-level block.
> - **Dropped at the user's direction:** the one-item "Mandatory skills: Good
>   attitude" row, and the **rig spec entirely** — *"people can bring whatever RCs
>   they want"* (the event is open). Also cut "Every line traces back…" and a "the
>   weekend fills in…" line that didn't read.
> - `renderAbout()` in `viewer_core.js` generalized from items[]/driver_meeting to
>   `sections[] + rules` (same DOM primitives, same http(s)-only link + textContent
>   safety). Net simpler — one fewer branch.
> - Verified by observation on live `:8001` — `verify_tbi_copy.py` rewritten to the
>   new shape, **18/18 About checks pass** (`brain/output/tbi_about.png` shows the
>   live render), no console errors from this change. The 2 non-About fails are
>   pre-existing tree state, not this task: the schedule's new `#firepit` anchor and
>   the bronze fema-buildings production-tier alert.
> - `_data_manifest.json` (top_keys/bytes) + `aop_copy_registry.json` (note) updated;
>   scratch `website/about_preview.html` created for the user's preview, then removed.
>   **v91 → v92** (`sw.js` + `#appVersion`).
> - **Council-cleared (5/5):** witness · warden · quartermaster · mason · scribe all
>   `clear` over this task's scoped diff (witness re-ran the verifier live + read the
>   shot; mason confirmed the renderer stays permissive + textContent/http(s)-safe;
>   scribe confirmed the host voice). Receipt:
>   `brain/output/council/about_rework_v92_20260614.md`.
> - **Owed (user's git gate):** the commit. The 600-acre reconcile still owes
>   (carried in `owed_work`).

> **Shipped 2026-06-14 (v78, UNCOMMITTED — user's git gate; council-cleared,
> core three: witness·warden·quartermaster all `clear`).** The gating external
> truth arrived: the event lead supplied the real copy in `brain/import/TBI.copy`.
> The placeholder sister-event copy is now replaced across the app. Moved to
> `_done/`. What landed:
>
> - **About tab** (`website/data/aop_about.json`): rewritten from TBI.copy. New
>   intro (keeps the FB event link); reference items reduced to the five real ones
>   (Mandatory skills = "Good attitude"; Rigs gains the 2.2″ class + "No bashers";
>   The park / The map / The crew rewritten). Dropped the placeholder Format,
>   Trail buddies (user marked `>>> remove`), and Night crawl items. Added a new
>   **Driver's Meeting** prose section (the welcome / "what to expect" script + the
>   weekend rules) — required a small `renderAbout` addition in `viewer_core.js`
>   (`info-subhead` / `info-rules`, CSS in `viewer.css`).
> - **Event schedule** (`website/data/aop_event_schedule.json`): replaced with the
>   real 18-session Fri/Sat/Sun timetable, `status: live`, hedge caveat + per-session
>   `inspired_by` dropped. Fork decision (user): **keep the pavilion pin, drop the
>   rest** — only `#pavilion` carries coordinates (the one map anchor); `#trails`
>   and `#camping-field` are named but coordinate-less, so the calendar reads
>   honestly with zero fabricated pins.
> - **Stale provenance copy** fixed: the map attribution `"Event schedule: proposed
>   from sister-event references"` (`viewer_core.js` + `main.js`) → "Rock Warblers
>   Trail Blazing Invitational"; the editor `<small>` "proposed RC event sessions"
>   (`old_index.html`) de-hedged.
> - **Registry** (`aop_copy_registry.json`): About + Event schedule flipped
>   `proposed → live` with notes.
> - Verified by observation (`brain/output/verify_tbi_copy.py`, 30/30; About DOM +
>   the GL-independent `eventScheduleToGeojson` transform: 18 sessions, one
>   `#pavilion` anchor, composed clock windows; Events screenshot shows the live
>   calendar + a working "Gates open in 5d 15h" countdown). `tbi_about.png` /
>   `tbi_events.png`. v76 → **v78** (`#appVersion` + `sw.js`). Council receipts:
>   `brain/output/council/{witness,warden,quartermaster}_tbi_copy.md`.
>
> **The Crew's Rock Warbler call** was filled at v79 — the user chose "caw-craaawl!"
> from four candidates. (Steward tier: copy-only, re-cleared at Tier-0.)
>
> **Still open** (not gated on this card): the event-tab name stays generic
> "Events" until multi-event support exists; the 600-acre figure still owes the
> parcel reconcile.

> **Deferred — Sprint 04 triage (2026-05-30).** Not done. **Deferred because** it
> is gated on external truth: it needs Rock Warblers to confirm the real event
> details (format, skills, schedule clock-times, contacts, etc.) before the
> placeholder sister-event copy can be replaced. Until those confirmations land,
> the UI stays confident and the source data carries the uncertainty.

Sprint 03 put production-voice event copy into the left sidebar using the thin
public event record plus sister-event patterns.

Sprint 04 needs the truth pass. Replace vibes with confirmed Rock Warblers
details.

#aop #04_event_app #content #rock_warblers #event

-----

## Source

- `../03_event_app/_done/left_sidebar_content_audit.md`
- `website/data/aop_event_schedule.json`
- `website/index.html`
- `brain/handoff/event_schedule_context_20260522.json`
- `../../northstar/whats_this_for.md`

## Job

Walk the Events / POI / About left rail and the event schedule data against
Rock Warblers-confirmed details.

The UI should stay confident. The source document should carry uncertainty
until the real answer lands.

## Needed Confirmations

- [ ] Format: number of stages, scoring rules, winching rules.
- [ ] Mandatory skills: which skills, whether every stage uses them, exact names.
- [ ] Trail buddies: whether required, what the penalty-winch rule actually is.
- [ ] Rigs: classes, dig/rear-steer policy, scale-accessory minimum.
- [ ] Night crawl: exists or not, route, finish point.
- [ ] Base camp: registration location, camping, food/drink, awards location.
- [ ] Contact: event page link, primary contact, day-of contact.
- [ ] Schedule: actual clock times vs. the current generic Friday-Sunday list.
- [ ] Event tab name: generic `Events` or specific event name once multi-event support exists.

## Adjacent Cleanup

- [ ] Review right-panel small text that still says `proposed RC event sessions`.
- [ ] Review map attribution text that still says `proposed from sister-event references`.
- [ ] Review `aop_event_schedule.json` `status: "proposed"` and caveat strings before any future UI surfaces them.

## Acceptance

- [ ] Rock Warblers have signed off the Event/About text line by line, or supplied replacement text.
- [ ] `website/data/aop_event_schedule.json` matches the confirmed schedule/status posture.
- [ ] User-facing UI does not expose stale sister-event placeholders.
- [ ] Editor/tooling copy can still name provenance honestly without leaking hedge language into visitor chrome.
