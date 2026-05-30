#!/usr/bin/env bash
# Paper-map trail extraction — full pipeline, one command.
# Card: brain/tasks/04_event_app/paper_map_trail_extraction.md
#
# Chains every stage in order and ends with the number-attach step so the
# viewer layers always carry trail_number (the trace stages leave it null).
#
#   1. extract   — detect difficulty markers + isolate trail-line ink (OpenCV)
#   2. warp      — georeference the markers via the 6x6 mesh (sfwda_markers.geojson)
#   3. vectorize — skeletonize + trace the trail lines (+ dump trail_graph.json)
#   4. publish   — copy the georeferenced layers into website/data/ for the viewer
#   5. numbers   — attach the hand-read trail numbers to the markers (idempotent)
#   6. trails    — stitch CONTIGUOUS numbered trails under the markers
#                  (sfwda_numbered_trails.geojson) + stamp numbers onto edges
#
# Run from anywhere:  mvp/scripts/run_paper_trace_pipeline.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PT="$REPO/brain/output/paper_trace"
DATA="$REPO/website/data"

echo "[1/6] extract markers + isolate trail lines"
python3 "$HERE/extract_paper_trails.py"

echo "[2/6] georeference markers (6x6 mesh warp)"
python3 "$HERE/paper_trace_warp.py"

echo "[3/6] skeletonize + vectorize trail lines"
python3 "$HERE/vectorize_paper_trails.py"

echo "[4/6] publish georeferenced layers to the viewer"
cp "$PT/sfwda_markers.geojson" "$DATA/sfwda_traced_markers.geojson"
cp "$PT/sfwda_trails.geojson"  "$DATA/sfwda_traced_trails.geojson"
echo "  -> website/data/sfwda_traced_markers.geojson, sfwda_traced_trails.geojson"

echo "[5/6] attach hand-read trail numbers to markers"
python3 "$HERE/attach_trail_numbers.py"

echo "[6/6] stitch contiguous numbered trails under the markers"
python3 "$HERE/build_numbered_trails.py"

echo "done. website/data/: sfwda_traced_markers (numbered), sfwda_traced_trails"
echo "      (edges stamped), and sfwda_numbered_trails (one contiguous trail/number)."
