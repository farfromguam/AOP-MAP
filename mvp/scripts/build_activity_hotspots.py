#!/usr/bin/env python3
"""Build time-weighted activity hotspots from timestamped GPX tracks.

The output is a mixed GeoJSON FeatureCollection:
- Polygon features are the audit-friendly hotspot cells.
- Point features are cell centroids used by the MapLibre heatmap/symbol layers.

This is a derived inspection layer. It does not promote GPX tracks into trails.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GPX = REPO_ROOT / "brain" / "import" / "Saturday_Afternoon_Activity.gpx"
DEFAULT_OUTPUT = REPO_ROOT / "website" / "data" / "aop_activity_hotspots.geojson"

EARTH_RADIUS_M = 6_371_000.0
STOP_SPEED_MPS = 0.05
SLOW_SPEED_MPS = 0.30
STATIONARY_DISTANCE_M = 6.0
STATIONARY_SECONDS = 30.0


@dataclass(frozen=True)
class TrackPoint:
    lon: float
    lat: float
    time: datetime
    ele_m: float | None
    source_file: str
    track_name: str
    segment_index: int
    point_index: int


@dataclass
class CellStats:
    dwell_seconds: float = 0.0
    stop_seconds: float = 0.0
    slow_seconds: float = 0.0
    moving_seconds: float = 0.0
    distance_m: float = 0.0
    capped_seconds: float = 0.0
    max_gap_seconds: float = 0.0
    sample_count: int = 0
    visit_count: int = 0
    interval_ids: set[str] = field(default_factory=set)
    segment_ids: set[str] = field(default_factory=set)
    source_files: set[str] = field(default_factory=set)
    track_names: set[str] = field(default_factory=set)
    weighted_x: float = 0.0
    weighted_y: float = 0.0


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def children_named(element: ET.Element, name: str) -> Iterable[ET.Element]:
    for child in element:
        if local_name(child.tag) == name:
            yield child


def first_child_text(element: ET.Element, name: str) -> str | None:
    for child in children_named(element, name):
        return child.text
    return None


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def gpx_segments(path: Path) -> list[list[TrackPoint]]:
    root = ET.parse(path).getroot()
    segments: list[list[TrackPoint]] = []
    global_segment_index = 0

    for trk in (el for el in root.iter() if local_name(el.tag) == "trk"):
        track_name = first_child_text(trk, "name") or path.stem
        for trkseg in children_named(trk, "trkseg"):
            global_segment_index += 1
            points: list[TrackPoint] = []
            for point_index, trkpt in enumerate(children_named(trkseg, "trkpt"), 1):
                time = parse_time(first_child_text(trkpt, "time"))
                if time is None:
                    continue
                lat = parse_float(trkpt.attrib.get("lat"))
                lon = parse_float(trkpt.attrib.get("lon"))
                if lat is None or lon is None:
                    continue
                points.append(
                    TrackPoint(
                        lon=lon,
                        lat=lat,
                        time=time,
                        ele_m=parse_float(first_child_text(trkpt, "ele")),
                        source_file=path.name,
                        track_name=track_name,
                        segment_index=global_segment_index,
                        point_index=point_index,
                    )
                )
            if len(points) >= 2:
                segments.append(points)

    return segments


def haversine_m(a: TrackPoint, b: TrackPoint) -> float:
    lon1, lat1, lon2, lat2 = map(math.radians, [a.lon, a.lat, b.lon, b.lat])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.atan2(math.sqrt(h), math.sqrt(max(0.0, 1 - h)))


def projectors(points: list[TrackPoint]):
    lat0 = sum(p.lat for p in points) / len(points)
    lon0 = sum(p.lon for p in points) / len(points)
    meters_per_deg_lat = 110_540.0
    meters_per_deg_lon = 111_320.0 * math.cos(math.radians(lat0))

    def to_xy(lon: float, lat: float) -> tuple[float, float]:
        return (lon - lon0) * meters_per_deg_lon, (lat - lat0) * meters_per_deg_lat

    def to_lonlat(x: float, y: float) -> tuple[float, float]:
        return lon0 + x / meters_per_deg_lon, lat0 + y / meters_per_deg_lat

    return to_xy, to_lonlat


def classify_interval(seconds: float, distance_m: float) -> str:
    speed = distance_m / seconds if seconds > 0 else 0.0
    if speed < STOP_SPEED_MPS or (seconds >= STATIONARY_SECONDS and distance_m <= STATIONARY_DISTANCE_M):
        return "stop"
    if speed < SLOW_SPEED_MPS:
        return "slow"
    return "moving"


def intensity_class(norm: float) -> str:
    if norm >= 0.70:
        return "peak"
    if norm >= 0.40:
        return "high"
    if norm >= 0.18:
        return "medium"
    return "low"


def cell_polygon(ix: int, iy: int, cell_m: float, to_lonlat) -> list[list[list[float]]]:
    x0 = ix * cell_m
    y0 = iy * cell_m
    corners = [
        to_lonlat(x0, y0),
        to_lonlat(x0 + cell_m, y0),
        to_lonlat(x0 + cell_m, y0 + cell_m),
        to_lonlat(x0, y0 + cell_m),
        to_lonlat(x0, y0),
    ]
    return [[[round(lon, 7), round(lat, 7)] for lon, lat in corners]]


def round_coord(lon: float, lat: float) -> list[float]:
    return [round(lon, 7), round(lat, 7)]


def build_hotspots(
    gpx_paths: list[Path],
    cell_m: float,
    sample_m: float,
    sample_s: float,
    max_gap_s: float,
    min_cell_seconds: float,
    min_stop_slow_seconds: float,
    max_moving_fraction: float | None,
    rank_by: str,
    intensity_cap_seconds: float | None,
    label_rank_limit: int,
    label_min_seconds: float,
    dataset_name: str,
    source_type: str,
    permission: str,
    publish_status: str,
    review_status: str,
    confidence: str | None,
) -> dict:
    segments_by_source: list[list[TrackPoint]] = []
    for path in gpx_paths:
        if not path.exists():
            raise FileNotFoundError(path)
        segments_by_source.extend(gpx_segments(path))

    all_points = [point for segment in segments_by_source for point in segment]
    if len(all_points) < 2:
        raise ValueError("No timestamped GPX segments with at least two points were found.")

    to_xy, to_lonlat = projectors(all_points)
    cells: dict[tuple[int, int], CellStats] = {}
    interval_total = 0
    skipped_intervals = 0
    capped_interval_count = 0

    for segment in segments_by_source:
        previous_cell: tuple[int, int] | None = None
        previous_visit_key = ""
        for a, b in zip(segment, segment[1:]):
            seconds = (b.time - a.time).total_seconds()
            if seconds <= 0:
                skipped_intervals += 1
                continue

            interval_total += 1
            distance_m = haversine_m(a, b)
            effective_seconds = min(seconds, max_gap_s)
            capped_seconds = max(0.0, seconds - effective_seconds)
            if capped_seconds > 0:
                capped_interval_count += 1

            state = classify_interval(seconds, distance_m)
            samples = max(1, math.ceil(distance_m / sample_m), math.ceil(effective_seconds / sample_s))
            interval_id = f"{a.source_file}:{a.segment_index}:{a.point_index}-{b.point_index}"
            segment_id = f"{a.source_file}:{a.segment_index}"
            visit_key = segment_id

            for i in range(samples):
                frac = (i + 0.5) / samples
                lon = a.lon + (b.lon - a.lon) * frac
                lat = a.lat + (b.lat - a.lat) * frac
                x, y = to_xy(lon, lat)
                cell_key = (math.floor(x / cell_m), math.floor(y / cell_m))
                stats = cells.setdefault(cell_key, CellStats())

                sample_seconds = effective_seconds / samples
                sample_distance = distance_m / samples
                stats.dwell_seconds += sample_seconds
                stats.distance_m += sample_distance
                stats.capped_seconds += capped_seconds / samples
                stats.max_gap_seconds = max(stats.max_gap_seconds, seconds)
                stats.sample_count += 1
                stats.interval_ids.add(interval_id)
                stats.segment_ids.add(segment_id)
                stats.source_files.add(a.source_file)
                stats.track_names.add(a.track_name)
                stats.weighted_x += x * sample_seconds
                stats.weighted_y += y * sample_seconds

                if state == "stop":
                    stats.stop_seconds += sample_seconds
                elif state == "slow":
                    stats.slow_seconds += sample_seconds
                else:
                    stats.moving_seconds += sample_seconds

                if cell_key != previous_cell or visit_key != previous_visit_key:
                    stats.visit_count += 1
                    previous_cell = cell_key
                    previous_visit_key = visit_key

    def interest_seconds(stats: CellStats) -> float:
        if rank_by == "stop_slow":
            return stats.stop_seconds + stats.slow_seconds
        return stats.dwell_seconds

    def moving_fraction(stats: CellStats) -> float:
        return stats.moving_seconds / stats.dwell_seconds if stats.dwell_seconds else 0.0

    kept = [
        (cell, stats)
        for cell, stats in cells.items()
        if stats.dwell_seconds >= min_cell_seconds
        and (stats.stop_seconds + stats.slow_seconds) >= min_stop_slow_seconds
        and (max_moving_fraction is None or moving_fraction(stats) <= max_moving_fraction)
    ]
    kept.sort(key=lambda item: interest_seconds(item[1]), reverse=True)
    max_interest = interest_seconds(kept[0][1]) if kept else 0.0
    norm_denominator = min(max_interest, intensity_cap_seconds) if intensity_cap_seconds else max_interest

    features: list[dict] = []
    for rank, ((ix, iy), stats) in enumerate(kept, 1):
        interest = interest_seconds(stats)
        intensity_seconds = min(interest, intensity_cap_seconds) if intensity_cap_seconds else interest
        norm = intensity_seconds / norm_denominator if norm_denominator else 0.0
        center_x = stats.weighted_x / stats.dwell_seconds if stats.dwell_seconds else (ix + 0.5) * cell_m
        center_y = stats.weighted_y / stats.dwell_seconds if stats.dwell_seconds else (iy + 0.5) * cell_m
        center_lon, center_lat = to_lonlat(center_x, center_y)
        dwell_minutes = stats.dwell_seconds / 60.0
        interest_minutes = interest / 60.0
        avg_speed = stats.distance_m / stats.dwell_seconds if stats.dwell_seconds else 0.0
        hot_class = intensity_class(norm)
        label = f"{interest_minutes:.1f} min" if rank <= label_rank_limit or interest >= label_min_seconds else ""
        common_props = {
            "id": f"activity_hotspot_{rank}",
            "layer": "activity_hotspots",
            "source_type": source_type,
            "source_files": sorted(stats.source_files),
            "track_names": sorted(stats.track_names),
            "confidence": confidence or ("single_track" if len(stats.source_files) == 1 else "multi_track"),
            "permission": permission,
            "publish_status": publish_status,
            "review_status": review_status,
            "cell_m": cell_m,
            "rank": rank,
            "intensity_norm": round(norm, 4),
            "intensity_class": hot_class,
            "dwell_seconds": round(stats.dwell_seconds, 1),
            "dwell_minutes": round(dwell_minutes, 2),
            "interest_seconds": round(interest, 1),
            "interest_minutes": round(interest_minutes, 2),
            "interest_mode": rank_by,
            "intensity_seconds": round(intensity_seconds, 1),
            "stop_seconds": round(stats.stop_seconds, 1),
            "slow_seconds": round(stats.slow_seconds, 1),
            "moving_seconds": round(stats.moving_seconds, 1),
            "moving_fraction": round(moving_fraction(stats), 4),
            "distance_m": round(stats.distance_m, 1),
            "avg_speed_mps": round(avg_speed, 3),
            "max_gap_seconds": round(stats.max_gap_seconds, 1),
            "capped_seconds": round(stats.capped_seconds, 1),
            "visit_count": stats.visit_count,
            "segment_count": len(stats.segment_ids),
            "interval_count": len(stats.interval_ids),
            "sample_count": stats.sample_count,
            "label": label,
        }

        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": cell_polygon(ix, iy, cell_m, to_lonlat),
                },
                "properties": {**common_props, "geom_role": "cell"},
            }
        )
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": round_coord(center_lon, center_lat)},
                "properties": {**common_props, "geom_role": "centroid"},
            }
        )

    return {
        "type": "FeatureCollection",
        "name": dataset_name,
        "metadata": {
            "schema": "aop-activity-hotspots-v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_type": source_type,
            "permission": permission,
            "publish_status": publish_status,
            "review_status": review_status,
            "confidence": confidence or ("single_track" if len(gpx_paths) == 1 else "multi_track"),
            "source_files": [path.name for path in gpx_paths],
            "cell_m": cell_m,
            "sample_m": sample_m,
            "sample_s": sample_s,
            "max_gap_s": max_gap_s,
            "min_cell_seconds": min_cell_seconds,
            "min_stop_slow_seconds": min_stop_slow_seconds,
            "max_moving_fraction": max_moving_fraction,
            "rank_by": rank_by,
            "intensity_cap_seconds": intensity_cap_seconds,
            "label_rank_limit": label_rank_limit,
            "label_min_seconds": label_min_seconds,
            "point_count": len(all_points),
            "segment_count": len(segments_by_source),
            "interval_count": interval_total,
            "skipped_interval_count": skipped_intervals,
            "capped_interval_count": capped_interval_count,
            "cell_feature_count": len(kept),
        },
        "features": features,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gpx", nargs="*", type=Path, default=[DEFAULT_GPX], help="GPX files to process.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output GeoJSON path.")
    parser.add_argument("--cell-m", type=float, default=15.0, help="Hotspot cell size in meters.")
    parser.add_argument("--sample-m", type=float, default=5.0, help="Max interpolation distance in meters.")
    parser.add_argument("--sample-s", type=float, default=20.0, help="Max interpolation time in seconds.")
    parser.add_argument("--max-gap-s", type=float, default=600.0, help="Cap a single interval's contributed time.")
    parser.add_argument("--min-cell-seconds", type=float, default=30.0, help="Drop cells below this dwell time.")
    parser.add_argument(
        "--min-stop-slow-seconds",
        type=float,
        default=0.0,
        help="Drop cells below this combined stopped+slow time.",
    )
    parser.add_argument(
        "--max-moving-fraction",
        type=float,
        default=None,
        help="Drop cells where moving_seconds / dwell_seconds exceeds this fraction.",
    )
    parser.add_argument(
        "--rank-by",
        choices=["total", "stop_slow"],
        default="total",
        help="Rank/intensity by total dwell time or by stopped+slow time.",
    )
    parser.add_argument(
        "--intensity-cap-seconds",
        type=float,
        default=None,
        help="Cap the value used for relative intensity so one extreme cell does not flatten the rest.",
    )
    parser.add_argument("--label-rank-limit", type=int, default=10, help="Always label cells up through this rank.")
    parser.add_argument("--label-min-seconds", type=float, default=120.0, help="Also label cells above this rank metric.")
    parser.add_argument("--name", default="aop_activity_hotspots", help="GeoJSON collection name.")
    parser.add_argument("--source-type", default="field_track_gpx", help="Source type written to metadata and features.")
    parser.add_argument("--permission", default="internal", help="Permission value written to hotspot features.")
    parser.add_argument("--publish-status", default="hold", help="Publish status written to hotspot features.")
    parser.add_argument(
        "--review-status",
        default="raw activity evidence; not a validated trail or facility",
        help="Review status written to hotspot features.",
    )
    parser.add_argument("--confidence", default=None, help="Override hotspot confidence value.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output if args.output.is_absolute() else REPO_ROOT / args.output
    gpx_paths = [path if path.is_absolute() else REPO_ROOT / path for path in args.gpx]

    data = build_hotspots(
        gpx_paths=gpx_paths,
        cell_m=args.cell_m,
        sample_m=args.sample_m,
        sample_s=args.sample_s,
        max_gap_s=args.max_gap_s,
        min_cell_seconds=args.min_cell_seconds,
        min_stop_slow_seconds=args.min_stop_slow_seconds,
        max_moving_fraction=args.max_moving_fraction,
        rank_by=args.rank_by,
        intensity_cap_seconds=args.intensity_cap_seconds,
        label_rank_limit=args.label_rank_limit,
        label_min_seconds=args.label_min_seconds,
        dataset_name=args.name,
        source_type=args.source_type,
        permission=args.permission,
        publish_status=args.publish_status,
        review_status=args.review_status,
        confidence=args.confidence,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    meta = data["metadata"]
    print(
        "activity_hotspots "
        f"cells={meta['cell_feature_count']} "
        f"features={len(data['features'])} "
        f"points={meta['point_count']} "
        f"segments={meta['segment_count']} "
        f"output={output}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
