# Rock Warblers Content Audit

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
