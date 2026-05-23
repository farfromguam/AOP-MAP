#!/usr/bin/env python3
"""Import FEMA USA Structures building footprints for the AOP 9-patch.

Pulls FEMA/ORNL USA Structures footprints that intersect the AOP 9-patch
envelope, normalizes the ArcGIS fields into compact map properties, tags whether
each footprint's representative point falls inside the current AOP working
boundary, and writes website/data/aop_buildings.geojson.

Stdlib only. Re-runnable; atomic write.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import sys
import tempfile
import urllib.parse
import urllib.request


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
OUT_FILE = os.path.join(REPO_DIR, "website", "data", "aop_buildings.geojson")
PUBLISH_FILE = os.path.join(REPO_DIR, "website", "data", "publish.geojson")

SERVICE_URL = (
    "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/"
    "USA_Structures_View/FeatureServer/0"
)
ITEM_URL = "https://www.arcgis.com/home/item.html?id=e9fc147eaeae4dcaa4e9ad9802c7b9c6"
SOURCE_NAME = "FEMA USA Structures / ORNL"

# AOP 9-patch acquisition envelope (WGS84 west, south, east, north).
BBOX = (-85.782935283, 35.067164188, -85.717154097, 35.117928496)

OUT_FIELDS = [
    "OBJECTID",
    "BUILD_ID",
    "OCC_CLS",
    "PRIM_OCC",
    "SEC_OCC",
    "PROP_ADDR",
    "PROP_CITY",
    "PROP_ST",
    "PROP_ZIP",
    "OUTBLDG",
    "HEIGHT",
    "SQMETERS",
    "SQFEET",
    "PROD_DATE",
    "SOURCE",
    "IMAGE_NAME",
    "IMAGE_DATE",
    "VAL_METHOD",
    "UUID",
    "PROP_CNTY",
]


def arcgis_get(path: str, params: dict[str, str]) -> dict:
    url = f"{SERVICE_URL}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "AOP-map-building-import/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.load(resp)
    if "error" in payload:
        raise RuntimeError(f"ArcGIS error from {path}: {payload['error']}")
    return payload


def fetch_object_ids() -> list[int]:
    params = {
        "f": "json",
        "where": "1=1",
        "geometry": ",".join(str(c) for c in BBOX),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "returnIdsOnly": "true",
    }
    payload = arcgis_get("query", params)
    ids = payload.get("objectIds") or []
    return sorted(int(i) for i in ids)


def fetch_features(object_ids: list[int]) -> list[dict]:
    features: list[dict] = []
    for start in range(0, len(object_ids), 100):
        chunk = object_ids[start:start + 100]
        params = {
            "f": "geojson",
            "objectIds": ",".join(str(i) for i in chunk),
            "outFields": ",".join(OUT_FIELDS),
            "returnGeometry": "true",
            "outSR": "4326",
        }
        payload = arcgis_get("query", params)
        features.extend(payload.get("features", []))
        print(f"  fetched {len(features)} / {len(object_ids)} footprints")
    return features


def iso_date(value: object) -> str:
    if value in (None, ""):
        return ""
    try:
        return dt.datetime.utcfromtimestamp(float(value) / 1000).date().isoformat()
    except (TypeError, ValueError, OSError):
        return ""


def first_ring(geometry: dict) -> list[list[float]]:
    if geometry["type"] == "Polygon":
        return geometry["coordinates"][0]
    if geometry["type"] == "MultiPolygon":
        return geometry["coordinates"][0][0]
    raise ValueError(f"Unexpected building geometry: {geometry['type']}")


def ring_centroid(ring: list[list[float]]) -> list[float]:
    pts = ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring
    return [
        sum(p[0] for p in pts) / len(pts),
        sum(p[1] for p in pts) / len(pts),
    ]


def signed_ring_area(ring: list[list[float]]) -> float:
    if len(ring) < 4:
        return 0.0
    lat0 = sum(p[1] for p in ring) / len(ring)
    coords = [
        (p[0] * 111320.0 * math.cos(math.radians(lat0)), p[1] * 110574.0)
        for p in ring
    ]
    return sum(
        coords[i][0] * coords[i + 1][1] - coords[i + 1][0] * coords[i][1]
        for i in range(len(coords) - 1)
    ) / 2.0


def point_in_ring(point: list[float], ring: list[list[float]]) -> bool:
    x, y = point
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if ((yi > y) != (yj > y)):
            x_intersect = (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
            if x < x_intersect:
                inside = not inside
        j = i
    return inside


def point_in_polygon(point: list[float], polygon: list[list[list[float]]]) -> bool:
    if not polygon or not point_in_ring(point, polygon[0]):
        return False
    return not any(point_in_ring(point, hole) for hole in polygon[1:])


def point_in_geometry(point: list[float], geometry: dict) -> bool:
    if geometry["type"] == "Polygon":
        return point_in_polygon(point, geometry["coordinates"])
    if geometry["type"] == "MultiPolygon":
        return any(point_in_polygon(point, polygon) for polygon in geometry["coordinates"])
    return False


def load_aop_boundary() -> dict | None:
    try:
        with open(PUBLISH_FILE, "r") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return None
    for feature in data.get("features", []):
        props = feature.get("properties") or {}
        if props.get("layer") == "park_boundaries" and feature.get("geometry"):
            return feature["geometry"]
    return None


def building_label(props: dict) -> str:
    address = (props.get("PROP_ADDR") or "").strip()
    if address:
        return address.title()
    occupancy = (props.get("PRIM_OCC") or props.get("OCC_CLS") or "Structure").strip()
    return f"{occupancy.title()} structure"


def normalize_feature(feature: dict, aop_boundary: dict | None) -> dict:
    props = feature.get("properties") or {}
    geometry = feature.get("geometry")
    if not geometry:
        raise ValueError("Feature missing geometry")
    centroid = ring_centroid(first_ring(geometry))
    inside_aop = bool(aop_boundary and point_in_geometry(centroid, aop_boundary))

    address = (props.get("PROP_ADDR") or "").strip()
    label = building_label(props)
    area_sqft = props.get("SQFEET")
    area_sqm = props.get("SQMETERS")
    height_m = props.get("HEIGHT")

    normalized_props = {
        "kind": "building_footprint",
        "name": address.title() if address else "",
        "building_label": label,
        "source_object_id": props.get("OBJECTID"),
        "build_id": props.get("BUILD_ID"),
        "uuid": props.get("UUID"),
        "occupancy_class": props.get("OCC_CLS") or "Unclassified",
        "primary_occupancy": props.get("PRIM_OCC") or "",
        "secondary_occupancy": props.get("SEC_OCC") or "",
        "address": address.title() if address else "",
        "city": (props.get("PROP_CITY") or "").title(),
        "state": props.get("PROP_ST") or "",
        "zip": props.get("PROP_ZIP") or "",
        "county": props.get("PROP_CNTY") or "",
        "outbuilding": props.get("OUTBLDG") or "",
        "height_m": round(float(height_m), 2) if height_m not in (None, "") else None,
        "area_sqm": round(float(area_sqm), 2) if area_sqm not in (None, "") else None,
        "area_sqft": round(float(area_sqft), 1) if area_sqft not in (None, "") else None,
        "centroid_lng": round(centroid[0], 8),
        "centroid_lat": round(centroid[1], 8),
        "inside_aop_boundary": inside_aop,
        "production_date": iso_date(props.get("PROD_DATE")),
        "image_date": iso_date(props.get("IMAGE_DATE")),
        "image_name": props.get("IMAGE_NAME") or "",
        "source_name": props.get("SOURCE") or "ORNL",
        "validation_method": props.get("VAL_METHOD") or "",
        "footprint_source": SOURCE_NAME,
        "source_item_url": ITEM_URL,
        "source_service_url": SERVICE_URL,
        "license_or_permission": "FEMA public data layer; no warranty; raw reference context",
        "publish_status": "raw_context",
        "confidence": "medium",
    }
    return {"type": "Feature", "properties": normalized_props, "geometry": geometry}


def main() -> int:
    print(f"Fetching FEMA USA Structures object ids from {SERVICE_URL}")
    object_ids = fetch_object_ids()
    if not object_ids:
        sys.exit("No FEMA USA Structures footprints returned for the AOP 9-patch.")
    print(f"  {len(object_ids)} footprint ids returned")

    raw_features = fetch_features(object_ids)
    aop_boundary = load_aop_boundary()
    features = [normalize_feature(feature, aop_boundary) for feature in raw_features]
    features.sort(key=lambda f: (
        f["properties"]["building_label"],
        f["properties"]["source_object_id"] or 0,
    ))

    collection = {
        "type": "FeatureCollection",
        "_source": SOURCE_NAME,
        "_source_item": ITEM_URL,
        "_source_service": SERVICE_URL,
        "_generated_by": "mvp/scripts/import_fema_buildings.py",
        "_retrieved_on": dt.date.today().isoformat(),
        "_aop_9_patch_bbox": list(BBOX),
        "_sources_checked": [
            {
                "name": "FEMA USA Structures",
                "result": f"{len(features)} polygon footprints imported",
                "selected": True,
            },
            {
                "name": "OpenStreetMap building=* via Overpass",
                "result": "11 building ways found; not imported to avoid duplicate ODbL context",
                "selected": False,
            },
            {
                "name": "TNMap FEMA BLE Building Footprints",
                "result": "0 features in the 9-patch",
                "selected": False,
            },
        ],
        "features": features,
    }

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(OUT_FILE), suffix=".geojson")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(collection, fh, indent=1)
            fh.write("\n")
        os.replace(tmp, OUT_FILE)
        os.chmod(OUT_FILE, 0o644)
    except (OSError, IOError):
        if os.path.exists(tmp):
            os.remove(tmp)
        raise

    inside = sum(1 for f in features if f["properties"]["inside_aop_boundary"])
    print(f"Wrote {len(features)} building footprints to {OUT_FILE}")
    print(f"  {inside} footprint(s) have centroids inside the current AOP boundary")
    print("  by occupancy class:")
    counts: dict[str, int] = {}
    for feature in features:
        cls = feature["properties"]["occupancy_class"]
        counts[cls] = counts.get(cls, 0) + 1
    for cls, count in sorted(counts.items()):
        print(f"    {count}\t{cls}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
