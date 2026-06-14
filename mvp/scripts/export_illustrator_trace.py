#!/usr/bin/env python3
"""Export the satellite 9-patch + gold trails / waypoints / buildings as a single
layered SVG for hand-tracing in Adobe Illustrator (or Inkscape / Affinity).

Card: brain/tasks/14_illustrator_trace/satellite_illustrator_export.md

The user traces and refines on the satellite, renaming objects as they go, then we
re-import (import_illustrator_trace.py) reading the OBJECT NAMES back as the truth.
So every feature is ONE named geometry OBJECT (a <path> or <circle> — NOT a group,
and NO drawn text), carrying the name in every channel an editor surfaces as the
object name:
  - id="<_xHH_ escaped name>"   Illustrator's Layers-panel object name + SVG round-trip
  - inkscape:label="<name>"     Inkscape's Objects panel
  - serif:id="<name>"           Affinity Designer's name channel
  - <title>name</title>         tooltip + generic fallback
i.e. "Front Office" is the polygon object itself, named — not a text item on the
artboard. The three category layers (Buildings / Waypoints / Gold Trails) are the
only <g> groups.

Coordinate frame: the satellite raster's OWN projected CRS (NAD83 / UTM zone 16N,
EPSG:26916, metres), read straight from the GeoTIFF georeference. SVG user units =
UTM metres, origin at the raster's NW corner, +x east, +y south. Because the frame
IS the raster's grid, vectors land 1:1 on the imagery with NO resampling and the
raster keeps full pixel fidelity. The vector layers are reprojected lng/lat ->
UTM 16N with a self-contained transverse-Mercator series (no GDAL/pyproj needed);
import inverts it. The exact projection params live in the SVG <metadata> so the
importer stays in lock-step.

Layers (top -> bottom):
  Satellite      the NAIP 2023 9-patch ortho (locked reference) [lock]
  Buildings      FEMA/ORNL in-park footprints (polygons)        [reference/edit]
  Waypoints      named point POIs (pavilion, camp POIs)         [reference/edit]
  Gold Trails    the merged gold trail network, colour=difficulty [EDIT]

Output: brain/output/illustrator_trace/aop_satellite_trace.svg
        brain/output/illustrator_trace/satellite_9patch.png  (standalone backdrop)
Run:    python3 mvp/scripts/export_illustrator_trace.py
"""
from __future__ import annotations
import base64, json, math
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "website/data"
OUT_DIR = REPO / "brain/output/illustrator_trace"
TIF = REPO / "mvp/cache/imagery/naip_2023_9patch.tif"

# --- gold trail difficulty palette (mirrors export_trace_svg / import_trace_svg) ---
DIFF_COLOR = {"easy": "#1f9d3a", "moderate": "#2438c8", "difficult": "#111111",
              "extreme": "#f25e0d", "road": "#f25e0d"}

# ===================================================================== UTM 16N
# NAD83 / UTM zone 16N (EPSG:26916). GRS80 ellipsoid. Self-contained transverse-
# Mercator (Snyder series); accurate to ~mm across a UTM zone, far below the
# 1.5 m/px raster. Vectorised over numpy arrays.
_A = 6378137.0                       # GRS80 semi-major
_F = 1.0 / 298.257222101
_E2 = 2 * _F - _F * _F               # e^2
_EP2 = _E2 / (1 - _E2)               # e'^2
_K0 = 0.9996
_LON0 = math.radians(-87.0)          # zone 16 central meridian
_FE, _FN = 500000.0, 0.0


def _meridian_arc(phi):
    e2, e4, e6 = _E2, _E2**2, _E2**3
    return _A * ((1 - e2/4 - 3*e4/64 - 5*e6/256) * phi
                 - (3*e2/8 + 3*e4/32 + 45*e6/1024) * np.sin(2*phi)
                 + (15*e4/256 + 45*e6/1024) * np.sin(4*phi)
                 - (35*e6/3072) * np.sin(6*phi))


def geodetic_to_utm(lon_deg, lat_deg):
    """lng/lat (degrees, arrays ok) -> UTM 16N easting/northing (metres)."""
    lon = np.radians(np.asarray(lon_deg, float))
    lat = np.radians(np.asarray(lat_deg, float))
    N = _A / np.sqrt(1 - _E2 * np.sin(lat)**2)
    T = np.tan(lat)**2
    C = _EP2 * np.cos(lat)**2
    A = (lon - _LON0) * np.cos(lat)
    M = _meridian_arc(lat)
    x = _FE + _K0 * N * (A + (1 - T + C) * A**3 / 6
                         + (5 - 18*T + T**2 + 72*C - 58*_EP2) * A**5 / 120)
    y = _FN + _K0 * (M + N * np.tan(lat) * (A**2/2
                     + (5 - T + 9*C + 4*C**2) * A**4 / 24
                     + (61 - 58*T + T**2 + 600*C - 330*_EP2) * A**6 / 720))
    return x, y


def utm_to_geodetic(x, y):
    """UTM 16N easting/northing (metres) -> lng/lat (degrees)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    M = (y - _FN) / _K0
    mu = M / (_A * (1 - _E2/4 - 3*_E2**2/64 - 5*_E2**3/256))
    e1 = (1 - math.sqrt(1 - _E2)) / (1 + math.sqrt(1 - _E2))
    phi1 = (mu + (3*e1/2 - 27*e1**3/32) * np.sin(2*mu)
            + (21*e1**2/16 - 55*e1**4/32) * np.sin(4*mu)
            + (151*e1**3/96) * np.sin(6*mu)
            + (1097*e1**4/512) * np.sin(8*mu))
    C1 = _EP2 * np.cos(phi1)**2
    T1 = np.tan(phi1)**2
    N1 = _A / np.sqrt(1 - _E2 * np.sin(phi1)**2)
    R1 = _A * (1 - _E2) / (1 - _E2 * np.sin(phi1)**2)**1.5
    D = (x - _FE) / (N1 * _K0)
    lat = phi1 - (N1 * np.tan(phi1) / R1) * (D**2/2
            - (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*_EP2) * D**4 / 24
            + (61 + 90*T1 + 298*C1 + 45*T1**2 - 252*_EP2 - 3*C1**2) * D**6 / 720)
    lon = _LON0 + (D - (1 + 2*T1 + C1) * D**3 / 6
            + (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*_EP2 + 24*T1**2) * D**5 / 120) / np.cos(phi1)
    return np.degrees(lon), np.degrees(lat)


# ============================================================ name <-> id helpers
def ai_escape(name):
    """Encode a feature name into Illustrator's `_xHH_` id convention so the
    Layers panel shows the clean name and it round-trips on SVG save. Mirrored by
    import_illustrator_trace.ai_unescape."""
    s = str(name)
    out = []
    for i, ch in enumerate(s):
        if ch.isalnum() and ord(ch) < 128:
            out.append(ch)
        elif ch == " ":
            out.append("_x20_")
        else:
            out.append(f"_x{ord(ch):X}_")
    eid = "".join(out)
    if not eid or eid[0].isdigit():     # XML ids may not start with a digit
        eid = "_" + eid
    return eid


def _xml(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ============================================================== raster frame
class RasterFrame:
    """A satellite GeoTIFF's own UTM-16N grid, used as the SVG coordinate frame,
    plus the embedded JPEG backdrop and the round-trip projection metadata.

    SVG user units = UTM 16N metres, origin at the raster NW corner, +x east,
    +y south — so vectors land 1:1 on the imagery (no resampling) and the
    importer inverts it with no warp. Shared by every Illustrator exporter so the
    frame + projection params are defined once, not re-derived per script.
    """

    def __init__(self, tif_path, jpg_path, jpg_quality=90):
        tif = tifffile.TiffFile(str(tif_path))
        page = tif.pages[0]
        tags = {t.name: t.value for t in page.tags.values()}
        pxX, pxY = tags["ModelPixelScaleTag"][0], tags["ModelPixelScaleTag"][1]
        tp = tags["ModelTiepointTag"]          # (i,j,k, X,Y,Z) maps pixel (i,j)->(X,Y)
        self.minE = tp[3] - tp[0] * pxX
        self.maxN = tp[4] + tp[1] * pxY        # +Y up; row increases southward
        self.img_w, self.img_h = page.imagewidth, page.imagelength
        self.px = (pxX, pxY)
        self.width_u = self.img_w * pxX        # SVG user units (UTM metres)
        self.height_u = self.img_h * pxY
        self.raster_name = Path(tif_path).name
        # backdrop: RGB only (drop NIR 4th band). JPEG — NAIP is photographic, so
        # JPEG cuts the embed ~6x vs PNG and keeps the SVG light enough to open
        # snappily in Illustrator; plenty of fidelity at 0.6–1.5 m/px.
        arr = page.asarray()
        rgb = arr[:, :, :3] if arr.ndim == 3 else np.stack([arr] * 3, -1)
        Image.fromarray(rgb.astype(np.uint8)).save(jpg_path, quality=jpg_quality)
        self.raster_b64 = base64.b64encode(Path(jpg_path).read_bytes()).decode()

    def to_frame(self, lon, lat):              # lng/lat -> SVG frame (metres, y south)
        E, N = geodetic_to_utm(lon, lat)
        return (E - self.minE), (self.maxN - N)

    def meta(self, note, extra=None):
        """The projection metadata block the importer reads to invert the frame.
        `note` is exporter-specific prose; `extra` appends after it."""
        nw = utm_to_geodetic(self.minE, self.maxN)
        se = utm_to_geodetic(self.minE + self.width_u, self.maxN - self.height_u)
        m = {
            "projection": "utm", "epsg": 26916, "datum": "NAD83 (GRS80)",
            "lon0_deg": -87.0, "k0": _K0, "false_easting": _FE, "false_northing": _FN,
            "frame_origin_easting": self.minE, "frame_origin_northing": self.maxN,
            "width_m": self.width_u, "height_m": self.height_u,
            "raster": self.raster_name, "raster_px": [self.img_w, self.img_h],
            "px_size_m": [self.px[0], self.px[1]],
            "bbox_lnglat_nw": [float(nw[0]), float(nw[1])],
            "bbox_lnglat_se": [float(se[0]), float(se[1])],
            "note": note,
        }
        if extra:
            m.update(extra)
        return m


# ===================================================================== data load
def load(fn):
    p = DATA / fn
    return json.loads(p.read_text()) if p.exists() else {"features": []}


def norm_diff(d):
    return d[0] if isinstance(d, list) else d


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # raster grid + backdrop + projection frame (shared with export_landcover_svg)
    jpg_path = OUT_DIR / "satellite_9patch.jpg"
    F = RasterFrame(TIF, jpg_path)
    pxX, pxY = F.px
    minE, maxN = F.minE, F.maxN
    img_w, img_h = F.img_w, F.img_h
    width_u, height_u = F.width_u, F.height_u
    to_frame = F.to_frame
    raster_b64 = F.raster_b64

    # ---------------------------------------------------------------- vectors
    def path_d(coords, close=False):
        lon = np.array([c[0] for c in coords]); lat = np.array([c[1] for c in coords])
        xs, ys = to_frame(lon, lat)
        d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in zip(xs, ys))
        return d + (" Z" if close else "")

    def name_attrs(name, fallback):
        """The feature NAME as the OBJECT name, in every editor's name channel —
        on the geometry element itself (no wrapper group, no drawn text). `id` is
        Illustrator's Layers-panel name + SVG round-trip; inkscape:label / serif:id
        for Inkscape / Affinity; a <title> child is returned to nest inside."""
        nm = name if name not in (None, "") else fallback
        eid = ai_escape(nm); lab = _xml(nm)
        return f'id="{eid}" inkscape:label="{lab}" serif:id="{lab}"', f'<title>{lab}</title>'

    # Gold trails -- each trail is ONE named <path> (Multi parts = subpaths) ----
    trails = load("gold_aop_trail_network.geojson")
    trail_els = []
    for f in trails["features"]:
        g = f["geometry"]; p = f["properties"]
        if g["type"] == "LineString":
            parts = [g["coordinates"]]
        elif g["type"] == "MultiLineString":
            parts = g["coordinates"]
        else:
            continue
        col = p.get("color") or DIFF_COLOR.get(norm_diff(p.get("difficulty")), "#888888")
        tn = p.get("trail_number")
        name = p.get("name") or (str(tn) if tn is not None else None)
        fid = p.get("id") or f"trail_{tn if tn is not None else 'x'}"
        d = " ".join(path_d(c) for c in parts if len(c) > 1)
        attrs, title = name_attrs(name, fid)
        # data-fid carries the stable original id so re-import can re-merge the full
        # gold props (color/maturity/permission/…) even if the user renames the
        # object. (Falls back to name-match if an editor strips data-*.)
        trail_els.append(
            f'<path {attrs} class="trail" stroke="{col}" '
            f'data-fid="{_xml(p.get("id") or "")}" '
            f'data-trail-number="{tn if tn is not None else ""}" '
            f'data-difficulty="{_xml(norm_diff(p.get("difficulty")) or "")}" '
            f'd="{d}">{title}</path>')

    # Buildings -- each footprint is ONE named compound <path> -----------------
    buildings = load("gold_aop_buildings.geojson")
    bldg_els = []
    for f in buildings["features"]:
        g = f["geometry"]; p = f["properties"]
        rings = []
        if g["type"] == "Polygon":
            rings = g["coordinates"]
        elif g["type"] == "MultiPolygon":
            rings = [r for poly in g["coordinates"] for r in poly]
        else:
            continue
        name = p.get("name") or p.get("address") or p.get("building_label")
        fid = f"building_{p.get('id') or p.get('build_id') or 'x'}"
        d = " ".join(path_d(r, close=True) for r in rings if len(r) > 2)
        attrs, title = name_attrs(name, fid)
        bldg_els.append(f'<path {attrs} class="building" d="{d}">{title}</path>')

    # Waypoints -- each POI is ONE named <circle> (deduped by name) ------------
    # Cemeteries are NOT a waypoint source: they live in their own (bronze)
    # cemeteries dataset, not the camp-infrastructure trace. Ellis still appears
    # here because it is a publish POI (gold_publish.geojson, kind="poi"); the
    # off-park three (Tate/Bible/Gilliam) were cemetery-only, so dropping the
    # cemeteries source removes them from the template. (User, 2026-06-14: "remove
    # it from the export and the import ... I dont want it.")
    wp_sources = [(load("gold_publish.geojson"), lambda pr: pr.get("kind") == "poi"),
                  (load("bronze_aop_editor_seed_pois.geojson"), lambda pr: True)]
    seen = set(); wp_els = []
    for fc, keep in wp_sources:
        for f in fc["features"]:
            if f["geometry"]["type"] != "Point":
                continue
            p = f["properties"]
            if not keep(p):
                continue
            name = p.get("name")
            key = (name or "").strip().lower()
            if not name or key in seen:
                continue
            seen.add(key)
            lon, lat = f["geometry"]["coordinates"][:2]
            x, y = to_frame(np.array([lon]), np.array([lat]))
            attrs, title = name_attrs(name, f"waypoint_{len(wp_els)}")
            wp_els.append(f'<circle {attrs} class="waypoint" data-kind="{_xml(p.get("kind") or "")}" '
                          f'cx="{x[0]:.1f}" cy="{y[0]:.1f}" r="9">{title}</circle>')

    # ---------------------------------------------------------------- assemble
    meta = F.meta(note=(
        "SVG user units = UTM 16N metres; x=E-origin_E, y=origin_N-N. "
        "import_illustrator_trace.py inverts this (no warp). Feature name = "
        "layer name, read from inkscape:label / serif:id / title / id."))
    nw, se = meta["bbox_lnglat_nw"], meta["bbox_lnglat_se"]
    INK = ('xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           'xmlns:serif="http://www.serif.com/"')
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" {INK}
     width="{width_u:.1f}" height="{height_u:.1f}" viewBox="0 0 {width_u:.2f} {height_u:.2f}">
<metadata id="aop_proj">{json.dumps(meta)}</metadata>
<style>
 .trail {{ fill:none; stroke-width:3; }}
 .building {{ fill:#ffffff22; stroke:#ff3b30; stroke-width:2; }}
 .waypoint {{ fill:#1e90ff; stroke:#ffffff; stroke-width:2; }}
</style>
<g inkscape:groupmode="layer" inkscape:label="Satellite" id="Satellite"
   sodipodi:insensitive="true"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.0.dtd">
  <image x="0" y="0" width="{width_u:.2f}" height="{height_u:.2f}" preserveAspectRatio="none"
         xlink:href="data:image/jpeg;base64,{raster_b64}" />
</g>
<g inkscape:groupmode="layer" inkscape:label="Buildings" id="Buildings">
  {"".join(bldg_els)}
</g>
<g inkscape:groupmode="layer" inkscape:label="Waypoints" id="Waypoints">
  {"".join(wp_els)}
</g>
<g inkscape:groupmode="layer" inkscape:label="Gold Trails" id="Gold_x20_Trails">
  {"".join(trail_els)}
</g>
</svg>'''
    out_svg = OUT_DIR / "aop_satellite_trace.svg"
    out_svg.write_text(svg)

    print(f"wrote {out_svg.relative_to(REPO)}  ({out_svg.stat().st_size/1e6:.1f} MB)")
    print(f"  backdrop {jpg_path.relative_to(REPO)}  ({img_w}x{img_h}px, {pxX:.3f} m/px)")
    print(f"  frame {width_u:.0f} x {height_u:.0f} m  UTM16N origin E{minE:.1f} N{maxN:.1f}")
    print(f"  layers: Gold Trails {len(trail_els)} | Waypoints {len(wp_els)} "
          f"| Buildings {len(bldg_els)}  (named objects, no text)")
    print(f"  raster NW lng/lat {nw[0]:.6f},{nw[1]:.6f}  SE {se[0]:.6f},{se[1]:.6f}")


if __name__ == "__main__":
    main()
