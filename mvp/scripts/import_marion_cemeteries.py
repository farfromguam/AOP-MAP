#!/usr/bin/env python3
"""Import Marion County cemetery parcels into website/data/aop_cemeteries.geojson.

Pulls cemetery-class parcels from the Tennessee Comptroller Marion County
parcel layer (TN_County_Parcel_Map FeatureServer layer 35) that intersect the
AOP 9-patch envelope, normalizes each into a readable cemetery feature, and
joins a hand-curated burial roster where one is known.

One cemetery — Ellis Cemetery, parcel 110 008.04 — is the interior parcel
excluded from the AOP boundary: the literal hole in the AOP working-envelope
polygon (parent parcel 110 008.00). Its geometry is bit-identical to the
interior ring of `AOP working parcel envelope` in website/data/publish.geojson.

Burial roster source: USGenWeb Archives, Marion County TN cemetery
transcription contributed by Leslie Paul Ellis. USGenWeb terms: free for
non-commercial use as long as the contributor notice travels with the data;
not to be reproduced for profit. The full notice lives in
brain/research/aop_ellis_cemetery.md.

Output: website/data/aop_cemeteries.geojson — per cemetery, one Polygon
feature (the parcel) and one Point feature (a centroid marker). Both carry the
same properties, so a click on either opens the same popup and the viewer
search indexes them as one result.

Stdlib only (urllib); no curl/jq dependency. Re-runnable; atomic write.
"""

from __future__ import annotations

import json
import math
import os
import sys
import tempfile
import urllib.parse
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
OUT_FILE = os.path.join(REPO_DIR, "website", "data", "aop_cemeteries.geojson")

PARCEL_SERVICE_URL = (
    "https://services.arcgis.com/rD2ylXRs80UroD90/arcgis/rest/services/"
    "TN_County_Parcel_Map/FeatureServer/35"
)

# AOP 9-patch acquisition envelope (WGS84 west, south, east, north).
BBOX = (-85.782935283, 35.067164188, -85.717154097, 35.117928496)

PARCEL_SOURCE = (
    "Tennessee Comptroller of the Treasury — Marion County parcels "
    "(TN_County_Parcel_Map FeatureServer layer 35)"
)
BURIAL_SOURCE = (
    "USGenWeb Archives, Marion County TN cemeteries — transcription "
    "contributed by Leslie Paul Ellis"
)
BURIAL_TERMS = (
    "USGenWeb Archives: free for non-commercial use; not to be reproduced "
    "for profit. See brain/research/aop_ellis_cemetery.md for the full notice."
)

# Per-parcel enrichment, keyed by the county assessment ID. Anything not listed
# here still imports — it just carries the county-derived name and no roster.
# `aop_inholding` marks a cemetery confirmed to be the interior parcel carved
# out of the AOP boundary polygon.
CEMETERY_OVERRIDES = {
    "110 008.04": {
        "name": "Ellis Cemetery",
        "aka": "Bryson & Ellis Cemetery",
        "cemetery_type": "family cemetery",
        "aop_inholding": True,
        "note": (
            "Interior parcel excluded from the AOP boundary — the hole in "
            "AOP working-envelope parcel 110 008.00. Reached from Ellis Cove "
            "Road, just past the Battle Creek bridge."
        ),
        "burial_source": BURIAL_SOURCE,
        "burial_terms": BURIAL_TERMS,
        # Recorded markers, in transcription order. 9 named, 3 unnamed infants.
        "burials": [
            {"name": "Ross H. Ellis", "dates": "1890-1981"},
            {"name": "Nathaniel Ellis", "dates": "1850-1920"},
            {"name": "Martha Ellis", "dates": "1853-1935"},
            {"name": "John Paul Ellis", "dates": "Feb 27, 1933 - July 17, 1941"},
            {"name": "David C. Ellis", "dates": "1886-1950"},
            {"name": "Mary Ellen Ellis", "dates": "1881-1951"},
            {"name": "Charles H. Ellis", "dates": "Mar 11, 1884 - Sept 14, 1965"},
            {"name": "Charles Ellis", "dates": "1933-1935"},
            {"name": "Esther Ellis", "dates": "1893-1935"},
            {"name": "Baby (unnamed infant)", "dates": ""},
            {"name": "Baby (unnamed infant)", "dates": ""},
            {"name": "Baby (unnamed infant)", "dates": ""},
        ],
    },
}


def fetch_cemetery_parcels() -> list[dict]:
    """Query the Comptroller parcel layer for cemetery-owned parcels in-AOI."""
    params = {
        "geometry": ",".join(str(c) for c in BBOX),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "outSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "where": (
            "UPPER(Assessment_Data_58_OWNER) LIKE '%CEMETERY%' "
            "OR UPPER(Assessment_Data_58_OWNER2) LIKE '%CEMETERY%'"
        ),
        "outFields": ",".join([
            "OBJECTID",
            "Parcels_GISLINK",
            "Assessment_Data_58_ID",
            "Assessment_Data_58_PARCELID",
            "Assessment_Data_58_OWNER",
            "Assessment_Data_58_OWNER2",
            "Assessment_Data_58_CLASS",
            "Assessment_Data_58_ADDRESS",
        ]),
        "returnGeometry": "true",
        "f": "geojson",
    }
    url = f"{PARCEL_SERVICE_URL}/query?" + urllib.parse.urlencode(params)
    print(f"Fetching cemetery parcels from {PARCEL_SERVICE_URL}/35")
    with urllib.request.urlopen(url, timeout=60) as resp:
        payload = json.load(resp)
    feats = payload.get("features", [])
    if not feats:
        sys.exit("No cemetery parcels returned — refusing to write an empty file.")
    print(f"  {len(feats)} cemetery parcel(s) returned")
    return feats


def display_name(owner: str) -> str:
    """Turn a county owner string into a readable cemetery name.

    The county records family cemeteries as e.g. 'CEMETERY GILLIAM'; move a
    leading 'CEMETERY' token to the end so it reads 'Gilliam Cemetery'.
    """
    tokens = owner.split()
    if tokens and tokens[0].upper() == "CEMETERY":
        tokens = tokens[1:] + ["CEMETERY"]
    name = " ".join(tokens).title()
    if "CEMETERY" not in name.upper():
        name = f"{name} Cemetery"
    return name


def ring_centroid(ring: list[list[float]]) -> list[float]:
    """Average of a ring's distinct vertices — fine for tiny parcels."""
    pts = ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring
    return [
        sum(p[0] for p in pts) / len(pts),
        sum(p[1] for p in pts) / len(pts),
    ]


def ring_acres(ring: list[list[float]]) -> float:
    """Shoelace area of a lon/lat ring, returned in acres."""
    lat0 = sum(p[1] for p in ring) / len(ring)
    mx = [p[0] * 111320.0 * math.cos(math.radians(lat0)) for p in ring]
    my = [p[1] * 110574.0 for p in ring]
    area = abs(sum(
        mx[i] * my[i + 1] - mx[i + 1] * my[i]
        for i in range(len(ring) - 1)
    ) / 2.0)
    return area / 4046.8564224


def exterior_ring(geom: dict) -> list[list[float]]:
    """Exterior ring of a Polygon or the first ring of a MultiPolygon."""
    if geom["type"] == "Polygon":
        return geom["coordinates"][0]
    if geom["type"] == "MultiPolygon":
        return geom["coordinates"][0][0]
    raise ValueError(f"Unexpected cemetery geometry: {geom['type']}")


def build_features(parcels: list[dict]) -> list[dict]:
    out: list[dict] = []
    for parcel in parcels:
        props = parcel.get("properties", {})
        geom = parcel.get("geometry")
        if not geom:
            continue
        parcel_id = (props.get("Assessment_Data_58_ID") or "").strip()
        owner = (props.get("Assessment_Data_58_OWNER") or "").strip()
        override = CEMETERY_OVERRIDES.get(parcel_id, {})

        ring = exterior_ring(geom)
        burials = override.get("burials", [])
        cemetery = {
            "kind": "cemetery",
            "name": override.get("name") or display_name(owner),
            "cemetery_type": override.get("cemetery_type", "cemetery"),
            "parcel_id": parcel_id,
            "parcel_gislink": (props.get("Parcels_GISLINK") or "").strip(),
            "parcel_class": (props.get("Assessment_Data_58_CLASS") or "").strip(),
            "parcel_owner": owner,
            "address": (props.get("Assessment_Data_58_ADDRESS") or "").strip(),
            "acres": round(ring_acres(ring), 3),
            "aop_inholding": bool(override.get("aop_inholding", False)),
            "note": override.get("note", ""),
            "parcel_source": PARCEL_SOURCE,
            "burial_count": len(burials),
            "named_burial_count": sum(
                1 for b in burials if not b["name"].startswith("Baby")
            ),
            "burials": burials,
            "burial_source": override.get("burial_source", ""),
            "burial_terms": override.get("burial_terms", ""),
        }
        if override.get("aka"):
            cemetery["aka"] = override["aka"]

        # One Polygon (the parcel) and one Point (a centroid marker). Same
        # properties on both so either is clickable and search collapses them.
        out.append({"type": "Feature", "properties": dict(cemetery), "geometry": geom})
        out.append({
            "type": "Feature",
            "properties": dict(cemetery),
            "geometry": {"type": "Point", "coordinates": ring_centroid(ring)},
        })
    return out


def main() -> None:
    parcels = fetch_cemetery_parcels()
    features = build_features(parcels)
    collection = {
        "type": "FeatureCollection",
        "_source": PARCEL_SOURCE,
        "_generated_by": "mvp/scripts/import_marion_cemeteries.py",
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
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise

    cemeteries = [f for f in features if f["geometry"]["type"] == "Polygon"]
    print(f"Wrote {len(cemeteries)} cemeteries "
          f"({len(features)} features) to {OUT_FILE}")
    for f in cemeteries:
        p = f["properties"]
        flags = []
        if p["aop_inholding"]:
            flags.append("AOP inholding")
        if p["burial_count"]:
            flags.append(f"{p['burial_count']} recorded burials")
        suffix = f"  [{'; '.join(flags)}]" if flags else ""
        print(f"  - {p['name']}  parcel {p['parcel_id']}  "
              f"{p['acres']} ac{suffix}")
    print(f"Source: {PARCEL_SOURCE}")


if __name__ == "__main__":
    main()
