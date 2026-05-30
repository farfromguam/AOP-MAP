misc 4 (also in sprint 4)

events show past events button needs to go.
poi expand all groups needs to go.
about events page link needs to be added to the body of the text above as a url body link not a button

events poi about should have a consistant expand handle at the bottom.
no minimum height no max height but set defaults on page load.
browser is taller.
phone is shorter.
user can adjust as needed or can collapse completely


there is some code to assume every friday is the event week so our or countdown is 2 days vs 2+weeks. now that we have session tools this is not needed

=== RESOLVED ABOVE === PENDING BELOW ===

events looks goods
poi has a white space at the bottom and no pull handles
about has a white space and the pull handle is above that white space
it works but it is wrong. 
what are we doing different in these three tabs???

current tab in calendar is not being restored on reload

---
tag these buildings, make hem 
1033 is the farmhouse
880 is the park offices
1010 is the pavallion
make all 3 buildings native footprints. put them into our database.
export our database and reload the data.
buildings should be in two places 
buildings layers
and our footprints. at this time we are good to turn off buildings.

---

cleanup worktrees that are unused.
clean up 




---

images and region callouts should be included in our "export" script.

the updated locations will be baked into the map and we wont loose positions on data reset.

-----

## What shipped (2026-05-27)

Items 1–5 done in the working tree (uncommitted):

- Item 1: `#showPastEventsBtn` removed.
- Item 2: `#poiExpandAllBtn` removed.
- Item 3: About `Event page` button removed; Facebook URL is now an inline `<a>` on "Trail Blazing Invitational" in the lead paragraph. `.tab-footer` / `.tab-footer-btn` CSS removed.
- Item 4: Resize handles. One shared `--lr-card-body-height` on `.lr-content-col`. Each tab gets its own `.lr-resize-handle` sibling outside the scroll body. No min/max — drag to 0. Old `setCalendarBodyHeight` / `initializeCalendarResize` chain deleted. localStorage key bumped `aop_calendar_height_v1 → aop_lr_card_height_v1` (old key retained one sprint in `VIEWER_OWNED_STORAGE_KEYS` per `spinup/viewer_storage_migration.md`).
- Item 5: Friday-of-week shim removed. `parseEventAnchorFriday()` reads `eventScheduleConfig.event.date_range_label`; `CALENDAR_MONDAY_RESET_HOUR` / `mondayResetMs` deleted.

Item 6 (sticky header scroll-with-events) held out by user — leave it alone.

"PENDING BELOW" block addressed:

- POI/About empty cream space → fixed by dropping `.left-tab-panels` grid-stack-to-tallest back to `display: block` (`website/index.html:359-364`). Each tab-panel now sizes to its own content. Tab switch between Events (has `.calendar-heading`) and POI/About produces a ~62 px shift; we accept that over the dead cream gap. Reverts the misc_3 item 21 stack. Visual confirmation: `brain/output/misc_4_left_tab_{events,poi,about}.png`.
- Current tab on reload → tab restore fix shipped; the event-session auto-restore no longer force-calls `setLeftTab('events')` when `viewerSessionState.active_left_tab` is POI/About. POI and About now stay put on reload.

Routed elsewhere:

- "1033 is the farmhouse / 880 is the park offices / 1010 is the pavilion" — these are building feature-tag bindings, not a misc_4 follow-up. Owed by source verification before promotion. Captured at `tasks/04_event_app/data_integrity_publishability.md` for the tagging pass on the buildings drawer.
- "images and region callouts in the export script" — SHIPPED 2026-05-30, see below.

Verifier residue:

- `playwright_verify_event_schedule.py` Trail-lane click tests vs. `hotButtonFlyToHotspots` off→on edge (6 pre-existing FAILs) logged at `tasks/04_event_app/viewer_polish_followups.md` under Code Health. Not caused by misc_4.

No git commit per `ai_rules/no_commits.md`.

## Images + region callouts in the export script (2026-05-30)

The "images and region callouts" line is closed. Background: brand logos
(`website/data/aop_brand_logos.geojson`) and visitor-context region callouts
(`website/data/aop_visitor_context_callouts.geojson`) are **file-based** layers
the static viewer loads directly — they are not in PostGIS, so
`export_publish_geojson.sh` (PostGIS publish views only) never touched them.
Drag/resize overrides lived only in localStorage (`aop_positioned_features_v1`),
so a Reset viewer / data reset snapped them back to seed coords and lost the
placement work.

New bake script **`mvp/scripts/export_positioned_features.py`** closes the loop
(same "bake the served file" pattern as `export_gold_trail_network.py`). It reads
the viewer's right-panel export — "Export all" (`aop-viewer-preset-settings-v3`,
key `positioned_features`), section Copy (`aop-section-state-v2`, key
`positionedFeatures`), or a bare `"<layer>:<id>"` map — and bakes each
override's `geometry` (plus `icon_size` for logos) into the two seed files in
place. Runtime flags (`highlight`/`locked`) are session state and are ignored.
Coords rounded to 5 decimals to match seed style; a `generated` date is stamped
into each changed file; overrides naming an unknown id are flagged and skipped.
`--dry-run` previews.

Loop: drag/resize in viewer → right panel "Export all" → save JSON →
`python3 mvp/scripts/export_positioned_features.py <file>` → commit the changed
geojson. Both seed files carry a bake-workflow note in their metadata.

Verified on `/tmp` copies (real seed files untouched): a synthetic override
moved + resized `aop_badge`, moved the South Pittsburg callout polygon, left
`rock_warblers` alone, ignored an unknown id, and produced valid canonical
2-space GeoJSON (json.loads round-trip holds). Script + the two seed-file notes
uncommitted per `ai_rules/no_commits.md`.