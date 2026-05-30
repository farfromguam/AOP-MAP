#!/usr/bin/env python3
"""Stage A+B of the paper-map trail extraction pipeline.

Card: brain/tasks/04_event_app/paper_map_trail_extraction.md

This first slice does the two things that have to work before any tracing:
  A. Detect the difficulty markers on the SFWDA 2015 raster:
       green circle = Easy, blue square = Moderate, black triangle = Difficult.
     Each marker -> {type, difficulty, centroid_px, area, bbox}.
  B. Isolate the trail-line network: take the dark ink, then subtract the
     markers, the title/legend chrome, the text labels, and the park boundary,
     leaving (approximately) just the trail lines.

It writes debug overlays + a markers.json so we can verify by observation
(brain/ai_rules/verify_by_observation) before adding skeletonize/vectorize/warp.

No georeferencing yet -- that reuses sfwda_raster_alignment.json downstream.

Run:  python3 mvp/scripts/extract_paper_trails.py
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "brain/import/community_trails/sfwda_aop_trail_map_2015-03-11.png"
OUT = REPO / "brain/output/paper_trace"

# Title block (top-left logo + address) and legend (bottom-right) are chrome,
# not trail data. Fractions of width/height; refined by looking at the overlay.
CHROME_BOXES_FRAC = [
    (0.00, 0.00, 0.36, 0.10),   # top-left: logo + address banner
    (0.78, 0.40, 1.00, 1.00),   # bottom-right: legend column
    (0.93, 0.00, 1.00, 1.00),   # far-right vertical "Stay on designated Trails"
    (0.00, 0.00, 0.06, 1.00),   # far-left vertical "www.adventure..." text
]


def chrome_mask(shape):
    h, w = shape[:2]
    m = np.zeros((h, w), np.uint8)
    for x0, y0, x1, y1 in CHROME_BOXES_FRAC:
        cv2.rectangle(m, (int(x0 * w), int(y0 * h)), (int(x1 * w), int(y1 * h)), 255, -1)
    return m


def detect_color_markers(hsv, chrome, kind):
    """Green circles (Easy) or blue squares (Moderate) by hue."""
    if kind == "green":
        lo, hi, difficulty, want = (35, 60, 40), (90, 255, 255), "easy", "circle"
    else:  # blue
        lo, hi, difficulty, want = (95, 60, 40), (135, 255, 255), "moderate", "square"
    mask = cv2.inRange(hsv, np.array(lo), np.array(hi))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    mask[chrome > 0] = 0
    out, found = np.zeros(mask.shape, np.uint8), []
    n, lab, stats, cent = cv2.connectedComponentsWithStats(mask, 8)
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        w_, h_ = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
        if not (120 <= area <= 6000):
            continue
        if max(w_, h_) / max(1, min(w_, h_)) > 1.8:  # roughly square bbox
            continue
        extent = area / float(w_ * h_)  # filled circle ~0.79, square ~0.95
        shape = "circle" if extent < 0.86 else "square"
        out[lab == i] = 255
        found.append({
            "type": want, "difficulty": difficulty,
            "centroid_px": [round(float(cent[i][0]), 1), round(float(cent[i][1]), 1)],
            "area": int(area), "bbox": [int(stats[i, j]) for j in range(4)],
            "extent": round(float(extent), 2), "shape_guess": shape,
        })
    return out, found


def detect_triangles(gray, chrome, exclude):
    """Black triangles (Difficult): solid-black bodies with a white number.

    They share ink color and weight with the trail lines and usually touch a
    line, so contour-shape on the raw dark mask fails. Instead: fill the white
    number-hole (close), then morphological OPEN to erase the thin trail lines
    while the solid triangle body survives -- connectivity-independent. A
    triangle reads as a 3-vertex blob with low bbox-fill (~0.5); the few solid
    facility icons (picnic/camp/bathroom) read as ~rectangular (fill ~0.9) and
    fall out on that test.
    """
    dark = cv2.threshold(gray, 95, 255, cv2.THRESH_BINARY_INV)[1]
    dark[chrome > 0] = 0
    dark[exclude > 0] = 0
    filled = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    solids = cv2.morphologyEx(
        filled, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))

    out, found = np.zeros(dark.shape, np.uint8), []
    n, lab, stats, cent = cv2.connectedComponentsWithStats(solids, 8)
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        x, y, w_, h_ = (int(stats[i, j]) for j in range(4))
        if not (150 <= area <= 9000):
            continue
        if max(w_, h_) / max(1, min(w_, h_)) > 2.2:
            continue
        extent = area / float(w_ * h_)            # triangle ~0.5, rect icon ~0.9
        comp = (lab == i).astype(np.uint8) * 255
        cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        c = max(cnts, key=cv2.contourArea)
        approx = cv2.approxPolyDP(c, 0.07 * cv2.arcLength(c, True), True)
        is_triangle = (len(approx) == 3) or (0.35 <= extent <= 0.68)
        if not is_triangle:
            continue
        out[lab == i] = 255
        found.append({
            "type": "triangle", "difficulty": "difficult",
            "centroid_px": [round(float(cent[i][0]), 1), round(float(cent[i][1]), 1)],
            "area": int(area), "bbox": [x, y, w_, h_],
            "extent": round(float(extent), 2), "verts": int(len(approx)),
        })
    return out, found


def isolate_trails(gray, chrome, marker_mask):
    """Dark ink minus markers minus chrome minus boundary minus text blobs."""
    dark = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY_INV)[1]
    dark[chrome > 0] = 0
    dark[cv2.dilate(marker_mask, np.ones((9, 9), np.uint8)) > 0] = 0

    # Park boundary = the single longest contour; set it aside (it is useful,
    # but it is not a trail). Keep it as its own output.
    cnts, _ = cv2.findContours(dark, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    boundary = np.zeros(dark.shape, np.uint8)
    if cnts:
        longest = max(cnts, key=lambda c: cv2.arcLength(c, False))
        cv2.drawContours(boundary, [longest], -1, 255, 3)

    trails = dark.copy()
    trails[cv2.dilate(boundary, np.ones((3, 3), np.uint8)) > 0] = 0

    # Drop small text blobs: components with tiny area AND compact bbox.
    n, lab, stats, _ = cv2.connectedComponentsWithStats(trails, 8)
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        w_, h_ = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
        if area < 60 and max(w_, h_) < 30:
            trails[lab == i] = 0
    return trails, boundary, dark


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bgr = cv2.imread(str(SRC))
    if bgr is None:
        raise SystemExit(f"could not read {SRC}")
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    chrome = chrome_mask(bgr.shape)

    green_mask, greens = detect_color_markers(hsv, chrome, "green")
    blue_mask, blues = detect_color_markers(hsv, chrome, "blue")
    color_mask = cv2.bitwise_or(green_mask, blue_mask)
    tri_mask, tris = detect_triangles(gray, chrome, color_mask)
    marker_mask = cv2.bitwise_or(color_mask, tri_mask)

    trails, boundary, dark = isolate_trails(gray, chrome, marker_mask)
    markers = greens + blues + tris

    # --- debug overlays ---
    overlay = bgr.copy()
    palette = {"easy": (0, 180, 0), "moderate": (220, 60, 0), "difficult": (0, 0, 220)}
    for m in markers:
        cx, cy = map(int, m["centroid_px"])
        cv2.circle(overlay, (cx, cy), 18, palette[m["difficulty"]], 3)
    cv2.imwrite(str(OUT / "markers_overlay.png"), overlay)
    cv2.imwrite(str(OUT / "dark_mask.png"), dark)
    cv2.imwrite(str(OUT / "trails_isolated.png"), trails)
    cv2.imwrite(str(OUT / "boundary.png"), boundary)

    # trails over the original, in magenta, for the eyeball check
    tr_overlay = bgr.copy()
    tr_overlay[trails > 0] = (255, 0, 255)
    cv2.imwrite(str(OUT / "trails_overlay.png"), tr_overlay)

    summary = {
        "source": str(SRC.relative_to(REPO)), "image_px": [w, h],
        "counts": {"easy_green_circle": len(greens),
                   "moderate_blue_square": len(blues),
                   "difficult_black_triangle": len(tris),
                   "total": len(markers)},
        "markers": markers,
    }
    (OUT / "markers.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary["counts"], indent=2))
    print(f"debug images + markers.json -> {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
