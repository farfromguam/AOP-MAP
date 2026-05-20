#!/usr/bin/env python3
"""Parse a GPX 1.1 file into a single JSON payload for psql ingestion.

Output schema (stdout, one JSON object, no newline):
{
  "creator": str | null,
  "recorded_at": str | null,           # ISO 8601 from <metadata><time>
  "track_name": str | null,
  "total_point_count": int,
  "segments": [
    {
      "segment_index": int,            # 1-based
      "point_count": int,
      "recorded_start": str | null,
      "recorded_end": str | null,
      "ele_min": float | null,
      "ele_max": float | null,
      "wkt": str                       # 'LINESTRING(lon lat, ...)' in EPSG:4326
    }, ...
  ],
  "raw_xml_b64": str                   # base64 of original file bytes
}

Notes:
- Skips degenerate segments (<2 distinct points).
- Drops elevation from geometry (schema is 2D), preserves min/max in metadata.
- Single <trk> assumed; if multiple, all are flattened and track_name is the first non-empty.
"""

import base64
import json
import sys
from xml.etree import ElementTree as ET

NS = {"gpx": "http://www.topografix.com/GPX/1/1"}


def parse(path: str) -> dict:
    with open(path, "rb") as f:
        xml_bytes = f.read()

    root = ET.fromstring(xml_bytes)
    creator = root.attrib.get("creator")
    recorded_at = root.findtext("gpx:metadata/gpx:time", namespaces=NS)

    track_name = None
    segments = []
    total_points = 0
    seg_counter = 0

    for trk in root.findall("gpx:trk", NS):
        name = trk.findtext("gpx:name", namespaces=NS)
        if name and not track_name:
            track_name = name
        for seg in trk.findall("gpx:trkseg", NS):
            seg_counter += 1
            pts = seg.findall("gpx:trkpt", NS)
            coords = []
            times = []
            eles = []
            for p in pts:
                try:
                    lat = float(p.attrib["lat"])
                    lon = float(p.attrib["lon"])
                except (KeyError, ValueError):
                    continue
                coords.append((lon, lat))
                ele = p.findtext("gpx:ele", namespaces=NS)
                if ele:
                    try:
                        eles.append(float(ele))
                    except ValueError:
                        pass
                t = p.findtext("gpx:time", namespaces=NS)
                if t:
                    times.append(t)

            distinct = list(dict.fromkeys(coords))
            if len(distinct) < 2:
                continue

            wkt_pts = ", ".join(f"{x} {y}" for x, y in coords)
            wkt = f"LINESTRING({wkt_pts})"
            total_points += len(coords)
            segments.append({
                "segment_index": seg_counter,
                "point_count": len(coords),
                "recorded_start": times[0] if times else None,
                "recorded_end": times[-1] if times else None,
                "ele_min": min(eles) if eles else None,
                "ele_max": max(eles) if eles else None,
                "wkt": wkt,
            })

    return {
        "creator": creator,
        "recorded_at": recorded_at,
        "track_name": track_name,
        "total_point_count": total_points,
        "segments": segments,
        "raw_xml_b64": base64.b64encode(xml_bytes).decode("ascii"),
    }


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: parse_gpx.py /path/to/file.gpx\n")
        sys.exit(2)
    payload = parse(sys.argv[1])
    if not payload["segments"]:
        sys.stderr.write("No non-degenerate segments found.\n")
        sys.exit(1)
    sys.stdout.write(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
