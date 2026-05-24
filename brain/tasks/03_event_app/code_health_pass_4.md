# Code Health Pass 4

Date: 2026-05-24

TL;DR:
- Sprint 02's leftover CSS / theme / smell notes move here.
- This pass is visual system hygiene plus adjacent code cleanup, not a new feature wave.
- Keep the viewer stable. If a fix changes behavior, name it and verify it.

#aop #03_event_app #code_health #css #theme #viewer

-----

## Source

- `viewer_polish_carryover.md` Lane 6.
- `../01_mvp/_done/code_health_pass.md` Pass 3 "Out of Scope" block.
- `../02_edit/tasks.md` user lines:
  - `[] css needs a review top to bottom`
  - `[] theme. review`
  - `[] code needs a review for smells.`
- `../../northstar/personas.md` for sun / phone / dusk readability checks.
- `../../research/viewer.md` for the current layer catalog and default policy.

## Job

Pass 3 cleaned the stringly localStorage drift, verifier duplication, and the
first chunk of palette repetition. It intentionally left the broader style pass
alone.

This card is that broader pass.

The goal is not a redesign. The viewer already has a working visual language:
muted earth, dense right rail, map-first left chrome, readable trace labels. The
job is to make the CSS and adjacent JS less brittle while preserving that
shape.

## Scope

### CSS Top-To-Bottom

- Audit the `!important` cluster left behind by Pass 2 and Pass 3.
  The known cluster is around `.section-toggle`, `.layer-expand`, and
  `.tune-control`. Normalize base panel button styling if that removes the need
  for overrides without widening visual churn.
- Audit inline `display` state.
  The known case is `.search-results`; any change has to update the JS write
  sites at the same time. If it isn't clearly safer, leave it and write why.
- Audit font shorthand and text scale.
  Pass 3 found the repeated font shorthands were not identical enough to hoist.
  Re-check after the Sprint 02 chrome work, especially calendar rows, feature
  rows, section headers, tune controls, and import/export buttons.
- Audit spacing and control dimensions.
  The right rail has many button-like controls. Keep them uniform where the
  user expects uniformity, especially collapse buttons and compact action rows.
- Audit un-tokenized hex literals in the CSS block.
  Do not blindly replace MapLibre paint colors embedded in JS. Tokenize only
  repeated UI colors or colors whose role is clear.

### Theme Review

- Check the cream / brown / rust palette against the actual personas:
  driver in sun, spectator on phone, marshal at dusk.
- Trace mode gets special attention. A pretty label that vanishes on satellite
  or hillshade is not a finished label.
- Review hover, focus, selected, disabled, collapsed, and active states. The
  interface should scan cleanly even when the right panel is dense.
- Keep the product vocabulary honest. "Live heat" and similar wording stays
  out unless the data is actually live and privacy-reviewed.

### Code Smells

- Touch adjacent JS only when it sits under the CSS/theme work.
- Prefer small helper extraction over broad file architecture changes.
- Keep storage keys, layer ids, and preset ids named. No new stringly state.
- Look for duplicated DOM-state updates around controls being touched.
- Capture real follow-ups in this card. Don't hide them in comments.

## Out Of Scope

- Public submissions, upload moderation, event CRUD, and app auth. Those belong
  to `full_loop_crud_upload_audit.md`.
- Single-file viewer extraction. Still not worth cracking open without a real
  module/build decision.
- Reworking trail data, trail names, or SFWDA georeferencing. That stays on
  `../01_mvp/_done/community_trails_import.md`.
- Offline/PWA and asset-weight work. Still deferred.

## Acceptance

- [ ] The `!important` cluster is either reduced or documented with a concrete
      reason it should stay.
- [ ] Inline display-state handling is either cleaned up or explicitly kept
      with the JS coupling named.
- [ ] CSS color tokens cover repeated UI colors; one-off or layer-paint colors
      are left alone unless their role is clear.
- [ ] Font, spacing, and compact-control treatment is audited top-to-bottom.
- [ ] Theme review is recorded against driver / spectator / marshal
      readability.
- [ ] Adjacent JS smells found during the pass are fixed or moved to a named
      follow-up.
- [ ] `website/index.html` parses cleanly after the pass.
- [ ] The full Playwright verifier sweep is rerun, or every skipped verifier
      has a reason.

## Verification

- Extract and syntax-check the inline viewer script with Node.
- Run `git diff --check`.
- Start the viewer on the Playwright port (`8001`) and run the full verifier
  set from `mvp/scripts/`.
- Spot-check the viewer manually in Park, Topo, and Trace presets at desktop
  and narrow widths.

## Notes

The Sprint 03 carryover card stops being the holder once this file exists. This
card is now the work surface for Pass 4.
