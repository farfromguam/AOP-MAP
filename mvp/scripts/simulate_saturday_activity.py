#!/usr/bin/env python3
"""Generate deterministic synthetic Saturday-afternoon AOP activity.

The simulator creates timestamped GPX tracks for many RC users who all start at
the pavilion, share parts of the observed Saturday trail, vary their routes,
follow nearby OSM track/service geometry when possible, and dwell/crawl at a mix
of known and simulated technical spots. The output is synthetic evidence for
testing the hotspot extractor, not field data.
"""

from __future__ import annotations

import argparse
import heapq
import json
import math
import random
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PUBLISH = REPO_ROOT / "website" / "data" / "publish.geojson"
DEFAULT_EVENTS = REPO_ROOT / "website" / "data" / "aop_event_schedule.json"
DEFAULT_EXISTING_HOTSPOTS = REPO_ROOT / "website" / "data" / "aop_activity_hotspots.geojson"
DEFAULT_OSM = REPO_ROOT / "website" / "data" / "osm_aop_9patch.geojson"
DEFAULT_GPX_OUTPUT = REPO_ROOT / "brain" / "import" / "synthetic_saturday_activity.gpx"
DEFAULT_TRACKS_OUTPUT = REPO_ROOT / "website" / "data" / "aop_synthetic_activity_tracks.geojson"
DEFAULT_REPORT_OUTPUT = REPO_ROOT / "website" / "data" / "aop_synthetic_activity_report.json"

LOCAL_TZ = ZoneInfo("America/Chicago")
EARTH_RADIUS_M = 6_371_000.0

Coord = tuple[float, float]
TimedPoint = tuple[float, float, datetime]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def haversine_m(a: Coord, b: Coord) -> float:
    lon1, lat1, lon2, lat2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.atan2(math.sqrt(h), math.sqrt(max(0.0, 1 - h)))


def projectors(origin: Coord):
    lon0, lat0 = origin
    meters_per_deg_lat = 110_540.0
    meters_per_deg_lon = 111_320.0 * math.cos(math.radians(lat0))

    def to_xy(coord: Coord) -> tuple[float, float]:
        lon, lat = coord
        return (lon - lon0) * meters_per_deg_lon, (lat - lat0) * meters_per_deg_lat

    def to_lonlat(x: float, y: float) -> Coord:
        return lon0 + x / meters_per_deg_lon, lat0 + y / meters_per_deg_lat

    return to_xy, to_lonlat


def offset_coord(origin: Coord, east_m: float, north_m: float) -> Coord:
    _, to_lonlat = projectors(origin)
    return to_lonlat(east_m, north_m)


def jitter_coord(coord: Coord, rng: random.Random, radius_m: float) -> Coord:
    if radius_m <= 0:
        return coord
    angle = rng.uniform(0, math.tau)
    distance = radius_m * math.sqrt(rng.random())
    return offset_coord(coord, math.cos(angle) * distance, math.sin(angle) * distance)


def path_distance_m(coords: list[Coord]) -> float:
    return sum(haversine_m(a, b) for a, b in zip(coords, coords[1:]))


def nearest_index(coords: list[Coord], target: Coord) -> int:
    return min(range(len(coords)), key=lambda idx: haversine_m(coords[idx], target))


def dedupe_path(coords: list[Coord]) -> list[Coord]:
    cleaned: list[Coord] = []
    for coord in coords:
        if not cleaned or haversine_m(cleaned[-1], coord) > 0.35:
            cleaned.append(coord)
    return cleaned


def resolve_locations(schedule: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_locations = schedule.get("locations", {})
    resolved: dict[str, dict[str, Any]] = {}

    def resolve(tag: str, stack: tuple[str, ...] = ()) -> dict[str, Any]:
        if tag in resolved:
            return resolved[tag]
        if tag in stack:
            raise ValueError(f"Location alias cycle: {' -> '.join(stack + (tag,))}")
        current = raw_locations[tag]
        alias = current.get("alias_of")
        if alias:
            base = dict(resolve(alias, stack + (tag,)))
            for key, value in current.items():
                if key not in {"alias_of", "hidden"}:
                    base[key] = value
            resolved[tag] = base
        else:
            resolved[tag] = dict(current)
        return resolved[tag]

    for tag in raw_locations:
        resolve(tag)
    return resolved


def location_coord(locations: dict[str, dict[str, Any]], tag: str) -> Coord:
    coords = locations[tag].get("coordinates")
    if not coords:
        raise ValueError(f"{tag} does not resolve to coordinates")
    return float(coords[0]), float(coords[1])


def publish_trail_coords(publish: dict[str, Any], name: str) -> list[Coord]:
    for feature in publish.get("features", []):
        props = feature.get("properties", {})
        if props.get("name") == name:
            return [(float(lon), float(lat)) for lon, lat in feature["geometry"]["coordinates"]]
    raise ValueError(f"Missing publish trail: {name}")


def hotspot_points(data: dict[str, Any]) -> list[dict[str, Any]]:
    points = []
    for feature in data.get("features", []):
        if feature.get("geometry", {}).get("type") != "Point":
            continue
        props = feature.get("properties", {})
        points.append(
            {
                "rank": int(props.get("rank", 0)),
                "dwell_minutes": float(props.get("dwell_minutes", 0)),
                "class": props.get("intensity_class", ""),
                "coordinates": tuple(feature["geometry"]["coordinates"]),
            }
        )
    return sorted(points, key=lambda item: item["rank"])


def hotspot_coord(points: list[dict[str, Any]], rank: int) -> Coord:
    for point in points:
        if point["rank"] == rank:
            lon, lat = point["coordinates"]
            return float(lon), float(lat)
    raise ValueError(f"Existing hotspot rank {rank} not found")


def path_between(base_route: list[Coord], start: Coord, end: Coord) -> list[Coord]:
    start_idx = nearest_index(base_route, start)
    end_idx = nearest_index(base_route, end)
    if start_idx <= end_idx:
        route = base_route[start_idx : end_idx + 1]
    else:
        route = list(reversed(base_route[end_idx : start_idx + 1]))
    if not route or haversine_m(route[0], start) > 6:
        route.insert(0, start)
    if haversine_m(route[-1], end) > 6:
        route.append(end)
    return dedupe_path(route)


class OsmRouteIndex:
    def __init__(self, osm_data: dict[str, Any], origin: Coord, max_feature_distance_m: float = 1400.0) -> None:
        self.nodes: list[Coord] = []
        self.node_index: dict[Coord, int] = {}
        self.edges: dict[int, list[tuple[int, float, int | None, str | None]]] = {}
        self.feature_count = 0
        self.track_feature_count = 0
        self.service_feature_count = 0
        self.total_osm_m = 0.0

        for feature in osm_data.get("features", []):
            props = feature.get("properties", {})
            highway = props.get("highway")
            geometry = feature.get("geometry", {})
            if geometry.get("type") != "LineString" or highway not in {"track", "service"}:
                continue
            coords = [(float(lon), float(lat)) for lon, lat in geometry.get("coordinates", [])]
            if len(coords) < 2:
                continue
            if min(haversine_m(origin, coord) for coord in coords) > max_feature_distance_m:
                continue
            osm_id = int(props.get("osm_id", 0) or 0)
            self.feature_count += 1
            self.track_feature_count += 1 if highway == "track" else 0
            self.service_feature_count += 1 if highway == "service" else 0
            for a, b in zip(coords, coords[1:]):
                weight = haversine_m(a, b)
                self.total_osm_m += weight
                ia = self._node(a)
                ib = self._node(b)
                self._edge(ia, ib, weight, osm_id, highway)

        self._add_snap_edges(snap_m=14.0)

    def _node(self, coord: Coord) -> int:
        key = (round(coord[0], 7), round(coord[1], 7))
        if key not in self.node_index:
            self.node_index[key] = len(self.nodes)
            self.nodes.append(key)
        return self.node_index[key]

    def _edge(self, a: int, b: int, weight: float, osm_id: int | None, highway: str | None) -> None:
        self.edges.setdefault(a, []).append((b, weight, osm_id, highway))
        self.edges.setdefault(b, []).append((a, weight, osm_id, highway))

    def _add_snap_edges(self, snap_m: float) -> None:
        for a in range(len(self.nodes)):
            for b in range(a + 1, len(self.nodes)):
                distance = haversine_m(self.nodes[a], self.nodes[b])
                if 0 < distance <= snap_m:
                    self._edge(a, b, distance, None, "snap")

    def nearest_node(self, coord: Coord) -> tuple[int, float] | None:
        if not self.nodes:
            return None
        idx = min(range(len(self.nodes)), key=lambda node: haversine_m(coord, self.nodes[node]))
        return idx, haversine_m(coord, self.nodes[idx])

    def route(self, start: Coord, end: Coord, max_snap_m: float = 260.0) -> dict[str, Any] | None:
        start_nearest = self.nearest_node(start)
        end_nearest = self.nearest_node(end)
        if not start_nearest or not end_nearest:
            return None
        start_idx, start_snap_m = start_nearest
        end_idx, end_snap_m = end_nearest
        if start_snap_m > max_snap_m or end_snap_m > max_snap_m:
            return None

        queue: list[tuple[float, int]] = [(0.0, start_idx)]
        distances = {start_idx: 0.0}
        previous: dict[int, tuple[int, float, int | None, str | None]] = {}

        while queue:
            distance, node = heapq.heappop(queue)
            if node == end_idx:
                break
            if distance > distances.get(node, math.inf):
                continue
            for neighbor, weight, osm_id, highway in self.edges.get(node, []):
                next_distance = distance + weight
                if next_distance < distances.get(neighbor, math.inf):
                    distances[neighbor] = next_distance
                    previous[neighbor] = (node, weight, osm_id, highway)
                    heapq.heappush(queue, (next_distance, neighbor))

        if end_idx not in distances:
            return None

        node_path = [end_idx]
        edge_path: list[tuple[int, float, int | None, str | None]] = []
        while node_path[-1] != start_idx:
            prev = previous[node_path[-1]]
            edge_path.append(prev)
            node_path.append(prev[0])
        node_path.reverse()
        edge_path.reverse()

        osm_m = sum(weight for _, weight, osm_id, _ in edge_path if osm_id)
        if osm_m <= 0:
            return None
        way_ids = sorted({osm_id for _, _, osm_id, _ in edge_path if osm_id})
        highways = sorted({highway for _, _, _, highway in edge_path if highway and highway != "snap"})
        return {
            "coordinates": dedupe_path([start, *[self.nodes[idx] for idx in node_path], end]),
            "osm_m": osm_m,
            "way_ids": way_ids,
            "highways": highways,
            "snap_start_m": start_snap_m,
            "snap_end_m": end_snap_m,
        }


def gpx_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def local_iso(value: datetime) -> str:
    return value.astimezone(LOCAL_TZ).replace(microsecond=0).isoformat()


def add_point(track: list[TimedPoint], coord: Coord, when: datetime) -> None:
    track.append((round(coord[0], 7), round(coord[1], 7), when))


def append_travel(
    track: list[TimedPoint],
    route: list[Coord],
    current: datetime,
    rng: random.Random,
    speed_mps: float,
    jitter_m: float = 1.0,
) -> datetime:
    route = dedupe_path(route)
    if not route:
        return current
    if not track:
        add_point(track, route[0], current)
    elif haversine_m((track[-1][0], track[-1][1]), route[0]) > 2:
        route = [(track[-1][0], track[-1][1]), *route]

    for raw_coord in route[1:]:
        last = (track[-1][0], track[-1][1])
        coord = jitter_coord(raw_coord, rng, jitter_m)
        distance = max(0.2, haversine_m(last, coord))
        seconds = max(5.0, distance / max(0.12, speed_mps))
        seconds *= rng.uniform(0.82, 1.22)
        current += timedelta(seconds=seconds)
        add_point(track, coord, current)
    return current


def record_anchor(
    anchor_stats: dict[str, dict[str, Any]],
    anchor_key: str,
    user_id: str,
    dwell_seconds: float = 0.0,
    crawl_seconds: float = 0.0,
) -> None:
    stats = anchor_stats[anchor_key]
    stats["user_ids"].add(user_id)
    stats["visit_count"] += 1
    stats["planned_dwell_seconds"] += dwell_seconds
    stats["planned_crawl_seconds"] += crawl_seconds


def append_dwell(
    track: list[TimedPoint],
    coord: Coord,
    current: datetime,
    rng: random.Random,
    seconds: float,
    jitter_m: float,
) -> datetime:
    if haversine_m((track[-1][0], track[-1][1]), coord) > 4:
        current = append_travel(track, [(track[-1][0], track[-1][1]), coord], current, rng, speed_mps=0.35, jitter_m=0.2)
    remaining = seconds
    while remaining > 0:
        step = min(remaining, rng.uniform(28, 72))
        current += timedelta(seconds=step)
        add_point(track, jitter_coord(coord, rng, jitter_m), current)
        remaining -= step
    return current


def append_crawl(
    track: list[TimedPoint],
    coord: Coord,
    current: datetime,
    rng: random.Random,
    seconds: float,
    intensity: float,
) -> datetime:
    if haversine_m((track[-1][0], track[-1][1]), coord) > 4:
        current = append_travel(track, [(track[-1][0], track[-1][1]), coord], current, rng, speed_mps=0.28, jitter_m=0.4)

    bearing = rng.uniform(0, math.tau)
    lateral = bearing + math.pi / 2
    half_len = rng.uniform(2.5, 6.5) * intensity
    side_len = rng.uniform(0.6, 1.8)
    elapsed = 0.0
    attempt = 0
    while elapsed < seconds:
        attempt += 1
        phase = (attempt % 6) / 5
        along = -half_len + (2 * half_len * phase)
        if attempt % 7 in {0, 1}:
            along *= -0.45
        side = rng.uniform(-side_len, side_len)
        east = math.cos(bearing) * along + math.cos(lateral) * side
        north = math.sin(bearing) * along + math.sin(lateral) * side
        step = min(seconds - elapsed, rng.uniform(18, 54))
        current += timedelta(seconds=step)
        add_point(track, offset_coord(coord, east, north), current)
        elapsed += step

        if elapsed < seconds and rng.random() < 0.34:
            pause = min(seconds - elapsed, rng.uniform(24, 96))
            current += timedelta(seconds=pause)
            add_point(track, jitter_coord(coord, rng, 1.1), current)
            elapsed += pause
    return current


def weighted_choice(rng: random.Random, weights: dict[str, float]) -> str:
    total = sum(weights.values())
    pick = rng.uniform(0, total)
    upto = 0.0
    for key, weight in weights.items():
        upto += weight
        if pick <= upto:
            return key
    return next(reversed(weights))


def write_gpx(tracks: list[dict[str, Any]], output: Path) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gpx version="1.1" creator="AOP synthetic Saturday activity simulator" xmlns="http://www.topografix.com/GPX/1/1">',
        "  <metadata>",
        "    <name>AOP synthetic Saturday afternoon activity</name>",
        "    <desc>Synthetic RC trail and rock-crawl sessions for hotspot pipeline testing. Not field evidence.</desc>",
        f"    <time>{gpx_time(datetime.now(timezone.utc))}</time>",
        "  </metadata>",
    ]
    for track in tracks:
        lines.extend(
            [
                "  <trk>",
                f"    <name>{escape(track['track_name'])}</name>",
                "    <type>synthetic_activity</type>",
                "    <trkseg>",
            ]
        )
        for lon, lat, when in track["points"]:
            lines.append(f'      <trkpt lat="{lat:.7f}" lon="{lon:.7f}"><time>{gpx_time(when)}</time></trkpt>')
        lines.extend(["    </trkseg>", "  </trk>"])
    lines.append("</gpx>")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_tracks_geojson(tracks: list[dict[str, Any]], output: Path, metadata: dict[str, Any]) -> None:
    features = []
    for track in tracks:
        coords = [[lon, lat] for lon, lat, _ in track["points"]]
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coords},
                "properties": {
                    "id": track["user_id"],
                    "track_name": track["track_name"],
                    "persona": track["persona"],
                    "source_type": "synthetic_activity_gpx",
                    "synthetic": True,
                    "start_anchor": "#pavilion",
                    "start_local": local_iso(track["points"][0][2]),
                    "end_local": local_iso(track["points"][-1][2]),
                    "duration_minutes": round((track["points"][-1][2] - track["points"][0][2]).total_seconds() / 60, 1),
                    "distance_m": round(path_distance_m([(lon, lat) for lon, lat, _ in track["points"]]), 1),
                    "osm_track_m": round(track["osm_track_m"], 1),
                    "osm_route_count": track["osm_route_count"],
                    "osm_way_ids": sorted(track["osm_way_ids"]),
                    "point_count": len(track["points"]),
                    "visited_anchors": sorted(track["visited_anchors"]),
                    "review_status": "synthetic Saturday simulation; not field evidence",
                },
            }
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"type": "FeatureCollection", "name": "aop_synthetic_activity_tracks", "metadata": metadata, "features": features}, indent=2)
        + "\n",
        encoding="utf-8",
    )


def build_anchor_report(
    anchor_defs: dict[str, dict[str, Any]],
    anchor_stats: dict[str, dict[str, Any]],
    existing_points: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    report = []
    for key, definition in anchor_defs.items():
        stats = anchor_stats[key]
        nearest = min(existing_points, key=lambda point: haversine_m(definition["coordinates"], point["coordinates"]))
        distance = haversine_m(definition["coordinates"], nearest["coordinates"])
        users = sorted(stats["user_ids"])
        report.append(
            {
                "key": key,
                "label": definition["label"],
                "coordinates": [round(definition["coordinates"][0], 7), round(definition["coordinates"][1], 7)],
                "source": definition["source"],
                "planned_user_count": len(users),
                "planned_visit_count": stats["visit_count"],
                "planned_dwell_minutes": round(stats["planned_dwell_seconds"] / 60, 1),
                "planned_crawl_minutes": round(stats["planned_crawl_seconds"] / 60, 1),
                "nearest_existing_hotspot": {
                    "rank": nearest["rank"],
                    "distance_m": round(distance, 1),
                    "existing_dwell_minutes": nearest["dwell_minutes"],
                    "existing_class": nearest["class"],
                },
            }
        )
    return sorted(report, key=lambda item: item["planned_dwell_minutes"] + item["planned_crawl_minutes"], reverse=True)


def write_report(
    output: Path,
    args: argparse.Namespace,
    tracks: list[dict[str, Any]],
    persona_counts: Counter[str],
    anchor_report: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> None:
    def repo_rel(path: Path) -> str:
        resolved = path if path.is_absolute() else REPO_ROOT / path
        try:
            return str(resolved.resolve().relative_to(REPO_ROOT.resolve()))
        except ValueError:
            return str(path)

    starts_at_pavilion = sum(1 for track in tracks if track["visited_anchors"] and "#pavilion" in track["visited_anchors"])
    total_points = sum(len(track["points"]) for track in tracks)
    total_distance = sum(path_distance_m([(lon, lat) for lon, lat, _ in track["points"]]) for track in tracks)
    total_osm_m = sum(track["osm_track_m"] for track in tracks)
    osm_way_ids = sorted({osm_id for track in tracks for osm_id in track["osm_way_ids"]})
    overlap_50m = [anchor for anchor in anchor_report if anchor["nearest_existing_hotspot"]["distance_m"] <= 50]
    report = {
        "schema": "aop-synthetic-saturday-activity-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "simulation": metadata,
        "inputs": {
            "publish": repo_rel(args.publish),
            "event_schedule": repo_rel(args.event_schedule),
            "existing_hotspots": repo_rel(args.existing_hotspots),
            "osm_tracks": repo_rel(args.osm),
        },
        "summary": {
            "users": len(tracks),
            "tracks_started_at_pavilion": starts_at_pavilion,
            "track_points": total_points,
            "total_distance_km": round(total_distance / 1000, 2),
            "osm_track_km": round(total_osm_m / 1000, 2),
            "tracks_with_osm_route": sum(1 for track in tracks if track["osm_route_count"] > 0),
            "osm_route_count": sum(track["osm_route_count"] for track in tracks),
            "osm_way_ids_used": osm_way_ids,
            "persona_counts": dict(sorted(persona_counts.items())),
            "anchors_with_existing_hotspot_overlap_50m": len(overlap_50m),
        },
        "expected_hotspots": anchor_report,
        "notes": [
            "All tracks are synthetic and start at #pavilion.",
            "Routes reuse the observed Saturday Afternoon Activity trail, event schedule anchors, and OSM highway=track/service geometry.",
            "OSM-following distance is counted only along OSM line vertices, not snap connectors from anchors to the nearest OSM node.",
            "Rock-crawl behavior is modeled as repeated slow attempts, short reverse moves, and dwell near obstacle anchors.",
            "Overlap is measured against the existing first-party GPX hotspot layer to test whether extraction finds familiar hot zones.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--users", type=int, default=72, help="Number of synthetic users/tracks to generate.")
    parser.add_argument("--seed", type=int, default=20260523, help="Deterministic random seed.")
    parser.add_argument("--start-local", default="2026-05-23T13:00:00", help="Local America/Chicago simulation start.")
    parser.add_argument("--publish", type=Path, default=DEFAULT_PUBLISH, help="publish.geojson input.")
    parser.add_argument("--event-schedule", type=Path, default=DEFAULT_EVENTS, help="Event schedule JSON input.")
    parser.add_argument("--existing-hotspots", type=Path, default=DEFAULT_EXISTING_HOTSPOTS, help="Existing GPX hotspot input.")
    parser.add_argument("--osm", type=Path, default=DEFAULT_OSM, help="OSM 9-patch GeoJSON input for route-following.")
    parser.add_argument("--output-gpx", type=Path, default=DEFAULT_GPX_OUTPUT, help="Synthetic GPX output.")
    parser.add_argument("--tracks-output", type=Path, default=DEFAULT_TRACKS_OUTPUT, help="Synthetic track GeoJSON output.")
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT, help="Simulation report JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rng = random.Random(args.seed)
    publish = read_json(args.publish)
    schedule = read_json(args.event_schedule)
    existing_hotspots = hotspot_points(read_json(args.existing_hotspots))
    locations = resolve_locations(schedule)

    pavilion = location_coord(locations, "#pavilion")
    observed_finish = location_coord(locations, "#observed-finish")
    observed_trailhead = location_coord(locations, "#observed-trailhead")
    segment_1 = publish_trail_coords(publish, "Saturday Afternoon Activity (segment 1)")
    segment_2 = publish_trail_coords(publish, "Saturday Afternoon Activity (segment 2)")
    trail_out = dedupe_path([pavilion, observed_finish, *reversed(segment_2)])
    osm_index = OsmRouteIndex(read_json(args.osm), pavilion)

    anchor_defs: dict[str, dict[str, Any]] = {
        "#pavilion": {
            "label": "Pavilion / registration dwell",
            "coordinates": pavilion,
            "source": "event schedule #pavilion and #registration",
        },
        "#photo-waypoint": {
            "label": "Photo waypoint / pavilion approach",
            "coordinates": location_coord(locations, "#photo-waypoint"),
            "source": "event schedule #photo-waypoint and existing hotspots #8/#9",
        },
        "#night-checkpoint": {
            "label": "Night checkpoint crawl shelf",
            "coordinates": location_coord(locations, "#night-checkpoint"),
            "source": "event schedule #night-checkpoint and existing hotspot #6",
        },
        "#north-technical": {
            "label": "North technical crawl",
            "coordinates": location_coord(locations, "#north-technical"),
            "source": "event schedule #north-technical and existing hotspots #3/#5",
        },
        "#upper-ledges": {
            "label": "Upper ledge attempts",
            "coordinates": hotspot_coord(existing_hotspots, 7),
            "source": "existing hotspot #7",
        },
        "#mid-shelf": {
            "label": "Mid-shelf regroup",
            "coordinates": hotspot_coord(existing_hotspots, 13),
            "source": "existing hotspot #13",
        },
        "#observed-trailhead": {
            "label": "Observed trailhead social stop",
            "coordinates": observed_trailhead,
            "source": "event schedule #observed-trailhead",
        },
        "#proving-grounds": {
            "label": "Proving grounds rock-crawl branch",
            "coordinates": location_coord(locations, "#proving-grounds"),
            "source": "event schedule #proving-grounds",
        },
        "#osm-main-spine-west": {
            "label": "OSM main spine west turn",
            "coordinates": (-85.755586, 35.0919237),
            "source": "OSM highway=track way 1215497663",
        },
        "#osm-north-loop": {
            "label": "OSM north loop crawl",
            "coordinates": (-85.7547755, 35.0971084),
            "source": "OSM highway=track cluster around ways 1215497670 / 1215497704",
        },
        "#osm-south-connector": {
            "label": "OSM south connector crawl",
            "coordinates": (-85.750517, 35.0869504),
            "source": "OSM highway=track ways 1215497666 / 1215497667",
        },
    }
    anchor_stats = {
        key: {"user_ids": set(), "visit_count": 0, "planned_dwell_seconds": 0.0, "planned_crawl_seconds": 0.0}
        for key in anchor_defs
    }

    base_local = datetime.fromisoformat(args.start_local)
    if base_local.tzinfo is None:
        base_local = base_local.replace(tzinfo=LOCAL_TZ)
    base_utc = base_local.astimezone(timezone.utc)

    profile_weights = {
        "north_crawl": 0.24,
        "checkpoint_loop": 0.13,
        "photo_short": 0.12,
        "proving_ground": 0.10,
        "trailhead_social": 0.08,
        "osm_spine_runner": 0.20,
        "osm_south_connector": 0.08,
        "mixed_sampler": 0.05,
    }
    persona_counts: Counter[str] = Counter()
    tracks: list[dict[str, Any]] = []

    def travel_to(
        track: list[TimedPoint],
        current: datetime,
        coord: Coord,
        speed: float,
        osm_meta: dict[str, Any],
        prefer_osm: bool = True,
    ) -> datetime:
        start = (track[-1][0], track[-1][1])
        if prefer_osm:
            osm_route = osm_index.route(start, coord)
            if osm_route and len(osm_route["coordinates"]) >= 3:
                osm_meta["osm_track_m"] += osm_route["osm_m"]
                osm_meta["osm_route_count"] += 1
                osm_meta["osm_way_ids"].update(osm_route["way_ids"])
                return append_travel(track, osm_route["coordinates"], current, rng, speed_mps=speed, jitter_m=0.45)
        return append_travel(track, path_between(trail_out, start, coord), current, rng, speed_mps=speed, jitter_m=1.0)

    def visit_dwell(track: list[TimedPoint], current: datetime, user_id: str, anchor_key: str, seconds: float, jitter_m: float = 1.5) -> datetime:
        record_anchor(anchor_stats, anchor_key, user_id, dwell_seconds=seconds)
        return append_dwell(track, anchor_defs[anchor_key]["coordinates"], current, rng, seconds, jitter_m)

    def visit_crawl(track: list[TimedPoint], current: datetime, user_id: str, anchor_key: str, seconds: float, intensity: float = 1.0) -> datetime:
        record_anchor(anchor_stats, anchor_key, user_id, crawl_seconds=seconds)
        return append_crawl(track, anchor_defs[anchor_key]["coordinates"], current, rng, seconds, intensity)

    for idx in range(1, args.users + 1):
        profile = weighted_choice(rng, profile_weights)
        persona_counts[profile] += 1
        user_id = f"synthetic_user_{idx:03d}"
        start_offset_min = rng.triangular(-12, 178, 58) + (idx % 9) * 2.5
        current = base_utc + timedelta(minutes=start_offset_min)
        track: list[TimedPoint] = []
        visited: set[str] = set()
        osm_meta: dict[str, Any] = {"osm_track_m": 0.0, "osm_route_count": 0, "osm_way_ids": set()}

        add_point(track, jitter_coord(pavilion, rng, 1.1), current)
        visited.add("#pavilion")
        registration_seconds = rng.uniform(110, 520)
        current = visit_dwell(track, current, user_id, "#pavilion", registration_seconds, jitter_m=2.2)
        transit_speed = rng.uniform(0.58, 1.15)

        if profile == "north_crawl":
            if rng.random() < 0.52:
                current = travel_to(track, current, anchor_defs["#night-checkpoint"]["coordinates"], transit_speed, osm_meta)
                visited.add("#night-checkpoint")
                current = visit_crawl(track, current, user_id, "#night-checkpoint", rng.uniform(190, 590), intensity=0.9)
            current = travel_to(track, current, anchor_defs["#north-technical"]["coordinates"], transit_speed * rng.uniform(0.78, 0.95), osm_meta)
            visited.add("#north-technical")
            current = visit_crawl(track, current, user_id, "#north-technical", rng.uniform(620, 1450), intensity=1.25)
            if rng.random() < 0.62:
                current = travel_to(track, current, anchor_defs["#upper-ledges"]["coordinates"], transit_speed * 0.72, osm_meta)
                visited.add("#upper-ledges")
                current = visit_crawl(track, current, user_id, "#upper-ledges", rng.uniform(260, 820), intensity=1.1)
            if rng.random() < 0.24:
                current = travel_to(track, current, observed_trailhead, transit_speed, osm_meta)
                visited.add("#observed-trailhead")
                current = visit_dwell(track, current, user_id, "#observed-trailhead", rng.uniform(120, 420), jitter_m=2.5)

        elif profile == "checkpoint_loop":
            current = travel_to(track, current, anchor_defs["#photo-waypoint"]["coordinates"], transit_speed, osm_meta)
            visited.add("#photo-waypoint")
            if rng.random() < 0.46:
                current = visit_dwell(track, current, user_id, "#photo-waypoint", rng.uniform(80, 260), jitter_m=1.6)
            current = travel_to(track, current, anchor_defs["#night-checkpoint"]["coordinates"], transit_speed * 0.85, osm_meta)
            visited.add("#night-checkpoint")
            current = visit_crawl(track, current, user_id, "#night-checkpoint", rng.uniform(420, 1080), intensity=1.0)
            if rng.random() < 0.35:
                current = travel_to(track, current, anchor_defs["#mid-shelf"]["coordinates"], transit_speed * 0.78, osm_meta)
                visited.add("#mid-shelf")
                current = visit_dwell(track, current, user_id, "#mid-shelf", rng.uniform(100, 360), jitter_m=1.7)

        elif profile == "photo_short":
            current = travel_to(track, current, anchor_defs["#photo-waypoint"]["coordinates"], transit_speed, osm_meta)
            visited.add("#photo-waypoint")
            current = visit_crawl(track, current, user_id, "#photo-waypoint", rng.uniform(220, 700), intensity=0.75)
            if rng.random() < 0.58:
                loop = [segment_1[0], *segment_1, *reversed(segment_1)]
                current = append_travel(track, loop, current, rng, speed_mps=transit_speed * 0.75, jitter_m=0.7)
            if rng.random() < 0.42:
                current = visit_dwell(track, current, user_id, "#pavilion", rng.uniform(90, 360), jitter_m=2.8)

        elif profile == "proving_ground":
            proving = anchor_defs["#proving-grounds"]["coordinates"]
            current = travel_to(track, current, proving, transit_speed * 0.9, osm_meta)
            visited.add("#proving-grounds")
            current = visit_crawl(track, current, user_id, "#proving-grounds", rng.uniform(520, 1320), intensity=1.2)
            if rng.random() < 0.34:
                current = travel_to(track, current, anchor_defs["#photo-waypoint"]["coordinates"], 0.65, osm_meta)
                visited.add("#photo-waypoint")
                current = visit_dwell(track, current, user_id, "#photo-waypoint", rng.uniform(90, 280), jitter_m=1.7)

        elif profile == "trailhead_social":
            current = travel_to(track, current, observed_trailhead, transit_speed * 0.9, osm_meta)
            visited.add("#observed-trailhead")
            current = visit_dwell(track, current, user_id, "#observed-trailhead", rng.uniform(260, 920), jitter_m=3.0)
            if rng.random() < 0.48:
                current = travel_to(track, current, anchor_defs["#north-technical"]["coordinates"], transit_speed * 0.78, osm_meta)
                visited.add("#north-technical")
                current = visit_crawl(track, current, user_id, "#north-technical", rng.uniform(260, 720), intensity=1.0)

        elif profile == "osm_spine_runner":
            current = travel_to(track, current, anchor_defs["#photo-waypoint"]["coordinates"], transit_speed, osm_meta)
            visited.add("#photo-waypoint")
            if rng.random() < 0.35:
                current = visit_dwell(track, current, user_id, "#photo-waypoint", rng.uniform(70, 220), jitter_m=1.5)
            current = travel_to(track, current, anchor_defs["#osm-main-spine-west"]["coordinates"], transit_speed * 0.92, osm_meta)
            visited.add("#osm-main-spine-west")
            current = visit_crawl(track, current, user_id, "#osm-main-spine-west", rng.uniform(180, 520), intensity=0.85)
            if rng.random() < 0.68:
                current = travel_to(track, current, anchor_defs["#osm-north-loop"]["coordinates"], transit_speed * 0.74, osm_meta)
                visited.add("#osm-north-loop")
                current = visit_crawl(track, current, user_id, "#osm-north-loop", rng.uniform(260, 780), intensity=1.0)
            if rng.random() < 0.34:
                current = travel_to(track, current, observed_trailhead, transit_speed, osm_meta)
                visited.add("#observed-trailhead")
                current = visit_dwell(track, current, user_id, "#observed-trailhead", rng.uniform(90, 260), jitter_m=2.2)

        elif profile == "osm_south_connector":
            current = travel_to(track, current, anchor_defs["#osm-south-connector"]["coordinates"], transit_speed * 0.82, osm_meta)
            visited.add("#osm-south-connector")
            current = visit_crawl(track, current, user_id, "#osm-south-connector", rng.uniform(360, 980), intensity=1.15)
            if rng.random() < 0.5:
                current = travel_to(track, current, anchor_defs["#proving-grounds"]["coordinates"], transit_speed * 0.8, osm_meta)
                visited.add("#proving-grounds")
                current = visit_crawl(track, current, user_id, "#proving-grounds", rng.uniform(180, 520), intensity=0.8)
            current = travel_to(track, current, anchor_defs["#photo-waypoint"]["coordinates"], transit_speed * 0.86, osm_meta)
            visited.add("#photo-waypoint")

        else:
            proving = anchor_defs["#proving-grounds"]["coordinates"]
            current = travel_to(track, current, proving, transit_speed, osm_meta)
            visited.add("#proving-grounds")
            current = visit_crawl(track, current, user_id, "#proving-grounds", rng.uniform(240, 600), intensity=0.9)
            current = travel_to(track, current, anchor_defs["#night-checkpoint"]["coordinates"], transit_speed * 0.75, osm_meta)
            visited.add("#night-checkpoint")
            current = visit_crawl(track, current, user_id, "#night-checkpoint", rng.uniform(260, 700), intensity=0.95)
            if rng.random() < 0.66:
                current = travel_to(track, current, anchor_defs["#north-technical"]["coordinates"], transit_speed * 0.75, osm_meta)
                visited.add("#north-technical")
                current = visit_crawl(track, current, user_id, "#north-technical", rng.uniform(260, 680), intensity=1.0)

        current = travel_to(track, current, observed_finish, transit_speed * rng.uniform(0.85, 1.18), osm_meta)
        current = append_travel(track, [observed_finish, pavilion], current, rng, speed_mps=transit_speed, jitter_m=0.8)
        visited.add("#pavilion")
        current = visit_dwell(track, current, user_id, "#pavilion", rng.uniform(120, 720), jitter_m=2.6)

        tracks.append(
            {
                "user_id": user_id,
                "track_name": f"Synthetic Saturday {idx:03d} - {profile.replace('_', ' ')}",
                "persona": profile,
                "points": track,
                "visited_anchors": visited,
                "osm_track_m": osm_meta["osm_track_m"],
                "osm_route_count": osm_meta["osm_route_count"],
                "osm_way_ids": osm_meta["osm_way_ids"],
            }
        )

    metadata = {
        "schema": "aop-synthetic-saturday-activity-v1",
        "seed": args.seed,
        "users": args.users,
        "start_local": local_iso(base_utc),
        "local_timezone": "America/Chicago",
        "saturday_date": base_local.date().isoformat(),
        "scenario": "Many RC users start at the pavilion, follow observed trail evidence, crawl technical spots, dwell/socialize, and overlap existing raw GPX hotspots.",
        "osm_route_index": {
            "input": str(args.osm),
            "feature_count": osm_index.feature_count,
            "track_feature_count": osm_index.track_feature_count,
            "service_feature_count": osm_index.service_feature_count,
            "indexed_osm_km": round(osm_index.total_osm_m / 1000, 2),
        },
        "source_type": "synthetic_activity_gpx",
        "permission": "internal",
        "publish_status": "hold",
        "review_status": "synthetic model for hotspot pipeline testing; not field evidence",
    }

    anchor_report = build_anchor_report(anchor_defs, anchor_stats, existing_hotspots)
    write_gpx(tracks, args.output_gpx)
    write_tracks_geojson(tracks, args.tracks_output, metadata)
    write_report(args.report_output, args, tracks, persona_counts, anchor_report, metadata)

    print(
        "synthetic_saturday_activity "
        f"users={len(tracks)} "
        f"points={sum(len(track['points']) for track in tracks)} "
        f"gpx={args.output_gpx} "
        f"tracks={args.tracks_output} "
        f"report={args.report_output}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
