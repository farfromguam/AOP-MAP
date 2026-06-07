#!/usr/bin/env python3
"""Going-gold WHEN importer: website/data/aop_event_schedule.json -> PostGIS core
(sprint 07 slice 1). The schedule's two halves land in two homes:

  sessions[]  --> core.events   (one row per occurrence; the WHEN junction)
  locations{} --> core.features (the WHERE each occurrence's #tag resolves to)

then export_publish_geojson.sh rebakes aop_event_schedule.json from core (sole
writer), so the schedule survives the gold one-writer bake instead of being a
hand-curated served file. Card: brain/tasks/07_tables/tables_model.md (slice 1).

The locations split exactly as the design says:
  * a tag with inline `coordinates` (the 6 anchors: #observed-trailhead, ...) has
    no feature today -> a NEW core.features row, layer='event', geom = its point,
    non-publish. The schedule-display fields (label/map_label/role/source/
    confidence/caveat) ride in attrs.event_location so the bake can rebuild the
    locations block; the #tag is attrs.event_location->>'tag'.
  * a tag already bound to a real feature (#pavilion -> the seeded editor POI; the
    binding lived in volatile editor tag-state, made explicit here as the gold
    redirect of the edit path into core) -> the existing row is ANNOTATED with the
    same attrs.event_location block; its geom is the feature's own point. No new row.

No-limiting-code (C5 / loop contract): this path ADDS/annotates rows. It never
rejects a value, never drops a session, never enforces a FK. place_key on
core.events stores the #tag verbatim; an occurrence whose place is not yet present
is stored and resolves later (LEFT join at bake), never dropped. count==input is
asserted on the session upsert (no silent zero-row write).

Run (DB up: docker compose -f mvp/docker-compose.yml up -d db):
  python3 mvp/scripts/import_event_schedule_to_core.py
  python3 mvp/scripts/import_event_schedule_to_core.py --dry-run   # print SQL, run nothing
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# Reuse the gold importer's SQL helpers verbatim -- do NOT re-implement (Quartermaster).
from import_layer_to_core_features import (
    COMPOSE_FILE,
    REPO,
    parse_count,
    run_psql,
    sql_jsonb,
    sql_str,
)

SCHEDULE_JSON = REPO / "website" / "data" / "aop_event_schedule.json"

SOURCE_NAME = "AOP event schedule (proposed sessions)"
SOURCE_PERMISSION = (
    "Proposed planning context; confirm schedule/locations/staffing/permission "
    "before publishing as official (non-publish)."
)

# Tags already bound to a real feature today. The binding lived in editor tag-state
# (aop_feature_tags_v1 / the seed_tag loader); the gold redirect makes it explicit
# in core. #pavilion is the only feature-backed schedule tag today.
PREBOUND = {"#pavilion": "editorPois:aop-pavilion"}

# locations-block fields, in HEAD's key order, that ride in attrs.event_location.
EVENT_LOC_FIELDS = ("label", "map_label", "role", "source", "confidence", "caveat")

# --- the reusable WHAT (slice 2) ---------------------------------------------
# Activities are the place-agnostic reusable content the schedule cites. The
# current schedule has ONE genuine recurrence -- "Night Crawl" runs Friday AND
# Saturday (fri-night-crawl + sat-night-crawl) -- so it collapses to a SINGLE
# activity cited by two occurrences (the de-dup the card names). Every other
# session is a one-off today, so it gets its own first-class activity record (the
# reusable identity the user attaches grade/length/gate-list to later, and future
# occurrences cite). description/attrs start empty -- the "specific data" is the
# user's content to author into core.activities, not invented here.
# session_id -> activity_key (ALL 13 sessions; only night_crawl is shared).
SESSION_ACTIVITY = {
    "fri-registration": "registration",
    "fri-driver-meeting": "driver_meeting",
    "fri-night-crawl": "night_crawl",
    "sat-late-registration": "late_registration",
    "sat-show-and-shine": "show_and_shine",
    "sat-g6-cove-rally": "g6_cove_rally",
    "sat-proving-grounds": "proving_grounds",
    "sat-king-of-hill": "king_of_the_hill",
    "sat-awards": "awards",
    "sat-night-crawl": "night_crawl",
    "sun-feedback-board": "feedback_board",
    "sun-short-loop-photo": "short_loop_photo",
    "sun-checkout": "checkout",
}
# activity_key -> reusable name. night_crawl is the abstraction over its two
# occurrence titles; the 1:1 activities take their session's title verbatim.
ACTIVITIES = {
    "registration": "Registration + wristband check",
    "driver_meeting": "Driver meeting + map review",
    "night_crawl": "Night Crawl",
    "late_registration": "Late registration + tech check",
    "show_and_shine": "Show & Shine: The Advance Party",
    "g6_cove_rally": "G6 Cove Rally stages",
    "proving_grounds": "Proving Grounds / comp gates",
    "king_of_the_hill": "King of the Hill / technical crawl",
    "awards": "Awards + raffle + food",
    "feedback_board": "Coffee, cleanup, map feedback board",
    "short_loop_photo": "Sunday Funday short loop / photo scavenge",
    "checkout": "Final check-out",
}


def event_location_attrs(tag: str, loc: dict) -> dict:
    """The display block the bake rebuilds the locations entry from. `tag` first so
    a single attrs key (event_location) carries both the #tag and its display data;
    coordinates are NOT stored here -- they come from the row's geom at bake."""
    block = {"tag": tag}
    for f in EVENT_LOC_FIELDS:
        if loc.get(f) is not None:
            block[f] = loc[f]
    return {"event_location": block}


def point_geom_sql(coords) -> str:
    if isinstance(coords, (list, tuple)) and len(coords) >= 2:
        return f"ST_SetSRID(ST_MakePoint({float(coords[0])}, {float(coords[1])}), 4326)"
    return "NULL"


def build_sql(doc: dict) -> str:
    event = doc.get("event") or {}
    event_id = event.get("id") or ""
    locations = doc.get("locations") or {}
    sessions = doc.get("sessions") or []

    parts = ["BEGIN;", "CREATE TEMP TABLE _ev(source_key text, inserted boolean);"]

    # Provenance source row (idempotent).
    parts.append(
        "INSERT INTO source_register.sources\n"
        "  (name, source_type, url_or_contact, license_or_permission,\n"
        "   publish_status, confidence_default, notes)\n"
        f"SELECT {sql_str(SOURCE_NAME)}, 'import',\n"
        "  'mvp/scripts/import_event_schedule_to_core.py',\n"
        f"  {sql_str(SOURCE_PERMISSION)},\n"
        "  'reference', 'proposed',\n"
        "  'Event schedule sessions + locations imported into core (going gold, sprint 07).'\n"
        "WHERE NOT EXISTS (\n"
        f"  SELECT 1 FROM source_register.sources WHERE name = {sql_str(SOURCE_NAME)}\n"
        ");"
    )
    src_subq = f"(SELECT id FROM source_register.sources WHERE name = {sql_str(SOURCE_NAME)})"

    # --- activities -> core.activities (the reusable WHAT) ----------------------
    # Upsert on activity_key; only name/kind set here (description/attrs are the
    # user's to author later). ON CONFLICT refreshes name/kind but NEVER clears a
    # description/attrs the user has since added (those columns are not in the SET).
    for akey, aname in ACTIVITIES.items():
        parts.append(
            "INSERT INTO core.activities (activity_key, name, kind, source_id)\n"
            f"VALUES ({sql_str(akey)}, {sql_str(aname)}, 'activity', {src_subq})\n"
            "ON CONFLICT (activity_key) DO UPDATE SET name = EXCLUDED.name, kind = EXCLUDED.kind;"
        )

    # --- locations -> core.features --------------------------------------------
    for tag, loc in locations.items():
        attrs = event_location_attrs(tag, loc)
        bound = PREBOUND.get(tag)
        if bound:
            # Annotate the existing feature; its geom stays the feature's own point.
            parts.append(
                "UPDATE core.features SET attrs = coalesce(attrs, '{}'::jsonb) || "
                f"{sql_jsonb(attrs)} WHERE source_key = {sql_str(bound)};"
            )
            continue
        coords = loc.get("coordinates")
        note = None if coords else "import: schedule tag has no coordinates and is not pre-bound -- geom NULL, resolves later"
        source_key = "event:" + tag.lstrip("#")
        cols = ["layer", "source_key", "name", "kind", "permission", "publish_status",
                "confidence", "attrs", "geom", "source_id", "last_verified"]
        vals = [
            sql_str("event"), sql_str(source_key), sql_str(loc.get("label") or tag),
            sql_str(loc.get("role") or "event_location"),
            sql_str("reference"), sql_str("reference"),
            sql_str(loc.get("confidence") or "proposed"),
            sql_jsonb(attrs), point_geom_sql(coords), src_subq, "now()",
        ]
        if note:
            cols.append("notes")
            vals.append(sql_str(note))
        sets = [f"{c} = EXCLUDED.{c}" for c in cols if c not in ("source_key", "source_id", "last_verified")]
        sets.append("last_verified = now()")
        parts.append(
            f"INSERT INTO core.features ({', '.join(cols)})\n"
            f"VALUES ({', '.join(vals)})\n"
            f"ON CONFLICT (source_key) DO UPDATE SET {', '.join(sets)};"
        )

    # --- sessions -> core.events -----------------------------------------------
    COLS = ("source_key", "event_id", "sort_order", "title", "date_label",
            "start_local", "time_label", "status", "place_key", "activity_key", "attrs", "source_id")
    for s in sessions:
        # attrs = every session field that is NOT a core.events column (so nothing drops).
        col_keys = {"id", "sort_order", "title", "date_label", "start_local",
                    "time_label", "status", "location_tag"}
        attrs = {k: v for k, v in s.items() if k not in col_keys}
        vals = [
            sql_str(s.get("id")), sql_str(event_id),
            str(int(s["sort_order"])) if s.get("sort_order") is not None else "NULL",
            sql_str(s.get("title")), sql_str(s.get("date_label")),
            sql_str(s.get("start_local")), sql_str(s.get("time_label")),
            sql_str(s.get("status")), sql_str(s.get("location_tag")),
            sql_str(SESSION_ACTIVITY.get(s.get("id"))), sql_jsonb(attrs), src_subq,
        ]
        sets = [f"{c} = EXCLUDED.{c}" for c in COLS if c not in ("source_key", "source_id")]
        parts.append(
            f"WITH up AS (\n"
            f"  INSERT INTO core.events ({', '.join(COLS)})\n"
            f"  VALUES ({', '.join(vals)})\n"
            f"  ON CONFLICT (source_key) DO UPDATE SET {', '.join(sets)}\n"
            f"  RETURNING source_key, (xmax = 0) AS inserted\n"
            f")\n"
            f"INSERT INTO _ev SELECT source_key, inserted FROM up;"
        )

    parts.append("SELECT 'EVENTS=' || count(*) FROM _ev;")
    parts.append("SELECT 'EVENTS_TOTAL=' || count(*) FROM core.events WHERE archived_at IS NULL;")
    parts.append("SELECT 'EVENT_PLACES=' || count(*) FROM core.features WHERE attrs ? 'event_location' AND archived_at IS NULL;")
    parts.append("SELECT 'ACTIVITIES=' || count(*) FROM core.activities WHERE archived_at IS NULL;")
    parts.append("SELECT 'EVENTS_W_ACTIVITY=' || count(*) FROM core.events WHERE activity_key IS NOT NULL AND archived_at IS NULL;")
    parts.append("COMMIT;")
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--schedule", default=str(SCHEDULE_JSON), help="path to aop_event_schedule.json")
    ap.add_argument("--dry-run", action="store_true", help="print the SQL; run nothing")
    args = ap.parse_args()

    doc = json.loads(Path(args.schedule).read_text())
    sessions = doc.get("sessions") or []
    locations = doc.get("locations") or {}
    sql = build_sql(doc)
    if args.dry_run:
        print(sql)
        return 0

    out = run_psql(sql)
    if not out:
        print("import: FAILED (psql error above; transaction rolled back)")
        return 1
    events = parse_count(out, "EVENTS")
    total = parse_count(out, "EVENTS_TOTAL")
    places = parse_count(out, "EVENT_PLACES")
    activities = parse_count(out, "ACTIVITIES")
    ev_with_act = parse_count(out, "EVENTS_W_ACTIVITY")
    print("== imported event schedule into core ==")
    print(f"  sessions in file       : {len(sessions)}")
    print(f"  core.events upserted   : {events}")
    print(f"  core.events total      : {total}")
    print(f"  locations in file      : {len(locations)}")
    print(f"  event-places in core   : {places}")
    print(f"  activities defined     : {len(ACTIVITIES)}")
    print(f"  core.activities total  : {activities}")
    print(f"  events w/ activity_key : {ev_with_act}")
    if events != len(sessions):
        print("import: FAIL -- core.events upserted count != session count (a silent drop)")
        return 1
    if places != len(locations):
        print("import: FAIL -- event-place count != locations count (a location was dropped)")
        return 1
    if activities != len(ACTIVITIES):
        print("import: FAIL -- core.activities count != defined activities (a silent drop)")
        return 1
    if ev_with_act != len(sessions):
        print("import: FAIL -- not every session got an activity_key")
        return 1
    print("import: OK (every session + location + activity landed; nothing dropped)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
