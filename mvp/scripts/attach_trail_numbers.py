#!/usr/bin/env python3
"""Attach hand-read trail NUMBERS to the detected SFWDA markers.

Card: brain/tasks/04_event_app/paper_map_trail_extraction.md

The OpenCV pipeline (extract_paper_trails.py) detects + georeferences markers but
leaves `trail_number: null` (OCR of the ~15 px numerals is unreliable). This
script supplies the missing numbers: they were read BY EYE off 3x contact sheets
of the same 2500x1817 raster (tesseract.js did worse). It matches each read to
the detector's marker by pixel-centroid proximity and writes the numbered layer.

Reliability: difficulty + position come from the detector (reliable); the number
is provisional -- 2-digit reads are crisp (confidence 'high'), single-digit
greens are low-res (confidence 'low'). A trail's number is labelled at several
points along its route, so numbers repeat across markers (expected).

Run this AFTER the trace pipeline (it fills the `trail_number` field the trace
step leaves null). Idempotent.

Inputs : brain/output/paper_trace/trail_number_reads.json  (hand-read numbers + centroids)
Targets (numbered in place, by centroid_px match):
         website/data/sfwda_traced_markers.geojson         (canonical viewer layer)
         brain/output/paper_trace/sfwda_markers.geojson    (detector source)
Also writes: brain/output/paper_trace/sfwda_markers_numbered.geojson (record copy)
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
READS_FILE = REPO / "brain/output/paper_trace/trail_number_reads.json"
TARGETS = [REPO / "website/data/sfwda_traced_markers.geojson",
           REPO / "brain/output/paper_trace/sfwda_markers.geojson"]
NUMBERED_COPY = REPO / "brain/output/paper_trace/sfwda_markers_numbered.geojson"

def number_one(det, reads):
    matched = mism = 0
    for f in det["features"]:
        cx, cy = f["properties"]["centroid_px"]
        best, bd = None, 1e9
        for rx, ry, num in reads:
            d = (rx-cx)**2 + (ry-cy)**2
            if d < bd: bd, best = d, num
        if best is not None and bd <= 30**2:        # within 30 px
            num = best
            conf = "high" if num >= 10 else "low"
            f["properties"]["trail_number"] = num
            f["properties"]["number_confidence"] = conf
            f["properties"]["confidence"] = f"position high; number {conf} (hand-read)"
            f["properties"]["review_status"] = "raster marker; number hand-read, needs verify before core/publish"
            matched += 1
            diff = f["properties"].get("difficulty")   # band sanity check
            band_ok = ((diff=="easy" and num<=20) or
                       (diff=="moderate" and (21<=num<=39 or 80<=num<=99)) or
                       (diff=="difficult" and 40<=num<=79))
            if not band_ok:
                f["properties"]["band_flag"] = f"number {num} unusual for {diff}"
                mism += 1
    det["_meta_numbers"] = {
        "added": "2026-05-29 attach_trail_numbers.py (run after the trace pipeline)",
        "method": "hand-read off 3x contact sheets, matched to markers by centroid_px (<30px)",
        "matched": matched, "of": len(det["features"]),
        "difficulty_bands": {"easy":"1-20","moderate":"21-39 & 80-99","difficult":"40-79"},
        "caveat": "number provisional (2-digit high / single-digit low); trail numbers repeat along a route"
    }
    return matched, mism

def main():
    reads = [(r["centroid_px"][0], r["centroid_px"][1], r["number"])
             for r in json.load(open(READS_FILE))["reads"]]
    last = None
    for tgt in TARGETS:
        if not tgt.exists():
            print(f"skip (missing): {tgt.relative_to(REPO)}"); continue
        det = json.load(open(tgt)); last = det
        matched, mism = number_one(det, reads)
        tgt.write_text(json.dumps(det, indent=1))
        print(f"{tgt.relative_to(REPO)}: matched {matched}/{len(det['features'])}, band-flags {mism}")
    if last is not None:
        NUMBERED_COPY.write_text(json.dumps(last, indent=1))
        nums = sorted({f['properties']['trail_number'] for f in last['features']
                       if f['properties'].get('trail_number') is not None})
        print("distinct numbers attached:", nums)

if __name__ == "__main__":
    main()
