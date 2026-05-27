# POI Editor Follow-ups

Sprint 03 made the drawn-POI editor usable: tree groups, inline accordion,
notes, category edits, seed file, and the pavilion tag migration.

This card keeps the work that was intentionally deferred.

#aop #04_event_app #poi #editor #crud

-----

## Source

- `../03_event_app/_done/poi_editor_inline_list_and_highlight.md`
- `../03_event_app/_done/poi_editor_tree_inline_accordion.md`
- `../03_event_app/_done/full_loop_crud_upload_audit.md`

## Work

- [ ] Add dedicated verifier coverage for the visitor-surface star: draw POI, confirm absent from POI tab, star it, confirm present, reload, confirm still present, unstar, confirm absent.
- [ ] Re-introduce star and on-map toggles inside the expanded accordion editor if row-only controls prove too easy to miss.
- [ ] Decide whether the `N star to visitors` count earns a compact chip.
- [ ] Decide whether the inline list auto-scrolls to a newly drawn POI.
- [ ] Add reshape/re-vertex action for polygons and lines, or explicitly rule it out until a stronger geometry editor lands.
- [ ] Add source-register fields to the editor surface once the event/submission loop has real storage: source, confidence, permission, publishable, last checked.
- [ ] Consider a seeded chip for features with `properties.source === 'aop_editor_seed_v1'`.
- [ ] Consider bulk select within a kind group for category changes. Not MVP unless editing volume proves it.
- [ ] **S3 review 2026-05-27 — `setEditorFeatureNotes` does not trim.** `website/index.html:3871-3879` reads `const trimmed = String(value || '');` and then `if (trimmed)` saves the value. The variable name `trimmed` implies whitespace stripping but the code only string-casts. A user who clears a notes textarea but leaves a trailing space writes `' '` into `feature.properties.notes`. Minor: decide whether whitespace-only notes should delete the field (`String(value).trim()` gate) or stay preserved. Either way, drop the misleading `trimmed` name.
- [ ] **S3 review 2026-05-27 — Reset viewer re-runs `maybeSeedEditorPois` and re-applies `seed_tag` migrations.** `website/index.html:6287-6310` strips the seed's `#tag` off any non-`editorPois` layer on every fresh-install / Reset. By design, but a user who explicitly re-binds `#pavilion` to a different layer after the initial seed install will lose that binding on Reset. Document in `spinup/viewer_storage_migration.md` (or in the seed file's leading comment) so the behavior is intentional rather than surprising.

## Acceptance

- [ ] POI editor verifier covers the star-to-visitor path.
- [ ] Deferred accordion controls are either shipped or intentionally kept row-only.
- [ ] Geometry reshape has a clear decision.
- [ ] Source-register editor fields wait for real app storage instead of becoming decorative localStorage fields.
