#!/usr/bin/env python3
"""Going-gold G_E umbrella seeder (gold slice 6, 2026-06-10): the event-schedule
document's umbrella wrapper -> core.event_meta (one row per umbrella event).

The wrapper used to be a hardcoded `EVENT_META` heredoc in
export_publish_geojson.sh (audit `event-umbrella-metadata-hardcoded-in-bake`).
This script lands those constants in the store of record so the bake composes the
document from DB truth, not a shell literal. The served file's `event{}` block +
`schema`/`status`/`updated_at` are the source values today; once event CRUD lands
the user edits the row directly and re-bakes.

Idempotent: upsert on event_id (ON CONFLICT refreshes the wrapper fields). Additive
/ no-limiting (C5): never rejects a value, never an allowlist. attrs holds any
future umbrella field. count==1 is asserted (no silent zero-row write).

Run (DB up: docker compose -f mvp/docker-compose.yml up -d db):
  python3 mvp/scripts/seed_event_meta.py
  python3 mvp/scripts/seed_event_meta.py --dry-run   # print SQL, run nothing
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# Reuse the gold importer's SQL helpers verbatim -- do NOT re-implement (Quartermaster).
from import_layer_to_core_features import (
    REPO,
    parse_count,
    run_psql,
    sql_jsonb,
    sql_str,
)

SCHEDULE_JSON = REPO / "website" / "data" / "aop_event_schedule.json"

# Same provenance source the session/location import uses, so the umbrella shares
# one source row with its sessions (idempotent INSERT ... WHERE NOT EXISTS).
SOURCE_NAME = "AOP event schedule (proposed sessions)"
SOURCE_PERMISSION = (
    "Proposed planning context; confirm schedule/locations/staffing/permission "
    "before publishing as official (non-publish)."
)

# event{} keys that map to dedicated core.event_meta columns. Everything else in
# event{} (none today) would ride in attrs so nothing drops.
EVENT_COL = {
    "label": "label",
    "date_range_label": "date_range_label",
    "end_date_label": "end_date_label",
    "source_context": "source_context",
    "source_summary": "source_summary",
    "caveat": "caveat",
}


def build_sql(doc: dict) -> str:
    event = doc.get("event") or {}
    event_id = event.get("id") or ""
    # attrs = every event{} field that is NOT a dedicated column (so nothing drops).
    col_event_keys = set(EVENT_COL) | {"id"}
    attrs = {k: v for k, v in event.items() if k not in col_event_keys}

    parts = ["BEGIN;"]

    # Provenance source row (idempotent, shared with the schedule import).
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

    cols = ["event_id", "schema", "label", "status", "date_range_label",
            "end_date_label", "source_context", "source_summary", "caveat",
            "schedule_updated_at", "attrs", "source_id"]
    vals = [
        sql_str(event_id),
        sql_str(doc.get("schema")),
        sql_str(event.get("label")),
        sql_str(doc.get("status")),
        sql_str(event.get("date_range_label")),
        sql_str(event.get("end_date_label")),
        sql_str(event.get("source_context")),
        sql_str(event.get("source_summary")),
        sql_str(event.get("caveat")),
        sql_str(doc.get("updated_at")),
        sql_jsonb(attrs) if attrs else "NULL",
        src_subq,
    ]
    sets = [f"{c} = EXCLUDED.{c}" for c in cols if c not in ("event_id", "source_id")]
    parts.append(
        f"INSERT INTO core.event_meta ({', '.join(cols)})\n"
        f"VALUES ({', '.join(vals)})\n"
        f"ON CONFLICT (event_id) DO UPDATE SET {', '.join(sets)};"
    )

    parts.append("SELECT 'EVENT_META=' || count(*) FROM core.event_meta WHERE archived_at IS NULL;")
    parts.append("COMMIT;")
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--schedule", default=str(SCHEDULE_JSON), help="path to aop_event_schedule.json")
    ap.add_argument("--dry-run", action="store_true", help="print the SQL; run nothing")
    args = ap.parse_args()

    doc = json.loads(Path(args.schedule).read_text())
    sql = build_sql(doc)
    if args.dry_run:
        print(sql)
        return 0

    out = run_psql(sql)
    if not out:
        print("seed: FAILED (psql error above; transaction rolled back)")
        return 1
    total = parse_count(out, "EVENT_META")
    event = doc.get("event") or {}
    print("== seeded event umbrella into core.event_meta ==")
    print(f"  event_id           : {event.get('id')}")
    print(f"  label              : {event.get('label')}")
    print(f"  core.event_meta rows: {total}")
    if total < 1:
        print("seed: FAIL -- no umbrella row present after upsert (a silent zero-row write)")
        return 1
    print("seed: OK (umbrella row present)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
